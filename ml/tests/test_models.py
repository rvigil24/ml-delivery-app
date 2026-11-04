"""Casos controlados para comprobar aislamiento; no son datos del experimento."""

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import LinearSVR

from delivery_ml.model_data import FEATURE_COLUMNS, TARGET, model_xy, temporal_features
from delivery_ml.models import build_models, fit_model


def training_frame():
    context = pd.DataFrame({"request_hour_utc": list(range(24)) * 2,
                            "request_weekday_utc": [0] * 24 + [1] * 24})
    train = temporal_features(context)
    train[TARGET] = 20 + 5 * train["request_hour_sin"]
    train["arrive_time"] = 999
    train["order_id"] = [f"control-{i}" for i in range(len(train))]
    return train


def test_three_families_fit_only_allowed_features_and_keep_scaler_frozen():
    train = training_frame()
    x, _ = model_xy(train)
    models = build_models()
    assert [type(model.steps[-1][1]) for model in models.values()] == [LinearRegression, RandomForestRegressor, LinearSVR]
    for name, model in models.items():
        fit_model(model, train)
        assert list(model.feature_names_in_) == FEATURE_COLUMNS
        before = model.predict(x)
        holdout = train.copy()
        holdout[FEATURE_COLUMNS] = 50
        holdout[TARGET] = 9999
        model.predict(model_xy(holdout)[0])
        np.testing.assert_allclose(model.predict(x), before)
        if name != "random_forest":
            np.testing.assert_allclose(model.steps[0][1].mean_, x.mean())
        if name == "linear_regression":
            np.testing.assert_allclose(before, train[TARGET], atol=1e-10)


def test_training_rejects_invalid_targets_before_fitting():
    train = training_frame()
    train.loc[0, TARGET] = float("inf")
    for model in build_models().values():
        with pytest.raises(ValueError, match="finitas"):
            fit_model(model, train)
