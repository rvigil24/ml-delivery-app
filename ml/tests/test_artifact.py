"""Casos controlados para selección y persistencia, fuera del experimento real."""

import json

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from delivery_ml import artifact
from delivery_ml.model_data import CONTEXT_COLUMNS, FEATURE_COLUMNS, temporal_features


def test_selection_uses_cv_instead_of_test_ranking():
    cv = {"models": {"random_forest": {"best_mean_mae_minutes": 2},
                     "linear_regression": {"best_mean_mae_minutes": 4}},
          "test": {"random_forest": 99, "mlp": 0}}
    selected, scores = artifact.select_by_cv(cv, {"selected_cv_mae_minutes": 3})
    assert selected == "random_forest"
    assert scores == {"random_forest": 2, "linear_regression": 4, "mlp": 3}


def test_bundle_round_trip_rejects_wrong_environment_and_corruption_before_unpickling(tmp_path, monkeypatch):
    context = pd.DataFrame({"request_hour_utc": [0, 6, 12, 18], "request_weekday_utc": [0, 1, 2, 3]})
    pipeline = Pipeline([("features", FunctionTransformer(temporal_features)),
                         ("forest", RandomForestRegressor(n_estimators=2, random_state=42))]).fit(context, [10, 20, 30, 40])
    metadata = {"schema": artifact.ARTIFACT_SCHEMA, "context_columns": CONTEXT_COLUMNS,
                "feature_columns": FEATURE_COLUMNS, "target_unit": "minutes", "environment": artifact.environment_versions()}
    directory = tmp_path / "model"
    written = artifact.write_bundle(directory, pipeline, metadata, {"controlled": True}, "Caso controlado\n")
    np.testing.assert_array_equal(pipeline.predict(context), artifact.load_pipeline(directory).predict(context))
    monkeypatch.setattr(artifact.pickle, "load", lambda *args: pytest.fail("No deserializar un bundle incompatible"))
    written["environment"] = {"python": "incompatible"}
    (directory / "metadata.json").write_text(json.dumps(written))
    with pytest.raises(ValueError, match="Entorno incompatible"):
        artifact.load_pipeline(directory)
    written["environment"] = artifact.environment_versions()
    (directory / "metadata.json").write_text(json.dumps(written))
    (directory / "pipeline.pkl").write_bytes(b"contenido alterado")
    with pytest.raises(ValueError, match="Hash de artefacto incompatible"):
        artifact.load_pipeline(directory)
