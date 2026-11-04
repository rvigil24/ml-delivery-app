"""Errores calculables y aislamiento; casos controlados, no datos experimentales."""

import numpy as np
import pandas as pd
import pytest

from delivery_ml.evaluation import evaluate_models, fit_frozen_models, regression_metrics
from delivery_ml.model_data import FEATURE_COLUMNS, TARGET, temporal_features


def controlled_frame():
    frame = temporal_features(pd.DataFrame({"request_hour_utc": [0, 1, 0], "request_weekday_utc": [6, 6, 0]}))
    frame[TARGET] = [10, 20, 30]
    frame["platform_order_time"] = [1666483200, 1666486800, 1666569600]
    frame["arrive_time"] = 999
    return frame


def test_metrics_and_daily_groups_use_identical_rows_without_refitting():
    class FrozenModel:
        def fit(self, *args):
            raise AssertionError("La evaluación no debe ajustar")

        def predict(self, x):
            assert list(x.columns) == FEATURE_COLUMNS
            return np.array([12, 18, 33])

    result = evaluate_models({"frozen": FrozenModel()}, controlled_frame())["frozen"]
    assert result["rows"] == 3
    assert result["mae_minutes"] == pytest.approx(7 / 3)
    assert result["rmse_minutes"] == pytest.approx(np.sqrt(17 / 3))
    assert result["r2"] == pytest.approx(1 - 17 / 200)
    assert result["mean_signed_error_minutes"] == 1
    assert result["p95_absolute_error_minutes"] == pytest.approx(2.9)
    assert [v["rows"] for v in result["by_creation_day_utc"].values()] == [2, 1]
    assert regression_metrics([10], [12])["r2"] is None
    with pytest.raises(ValueError, match="vectores finitos"):
        regression_metrics([10], [float("inf")])


def test_frozen_configurations_and_predictions_stay_unchanged_when_test_labels_change():
    train = controlled_frame()
    parameters = {"linear_regression": {}, "random_forest": {"randomforestregressor__max_depth": 6},
                  "linear_svr": {"linearsvr__C": 0.1}}
    fitted = fit_frozen_models(train, parameters, mlp_epochs=1)
    assert len(fitted) == 5
    assert fitted["random_forest"].get_params()["randomforestregressor__max_depth"] == 6
    assert fitted["linear_svr"].get_params()["linearsvr__C"] == 0.1
    assert len(fitted["mlp"].history) == 1
    before = {name: model.predict(train[FEATURE_COLUMNS]) for name, model in fitted.items()}
    test = train.copy()
    test[TARGET] = 9999
    evaluate_models(fitted, test)
    for name, model in fitted.items():
        np.testing.assert_array_equal(before[name], model.predict(train[FEATURE_COLUMNS]))
