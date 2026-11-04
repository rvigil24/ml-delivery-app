"""Casos controlados del entrenamiento, separados del experimento real."""

import numpy as np
import pandas as pd
import pytest

from delivery_ml.mlp import SmallMLPRegressor
from delivery_ml.model_data import FEATURE_COLUMNS, TARGET, temporal_features


def controlled_frame():
    x = temporal_features(pd.DataFrame({"request_hour_utc": list(range(24)), "request_weekday_utc": 0}))
    x[TARGET] = 20 + 5 * x["request_hour_sin"]
    x["arrive_time"] = 999
    return x


def test_mlp_training_is_reproducible_and_validation_does_not_change_weights_or_scalers():
    train = controlled_frame()
    holdout = train.copy()
    holdout[FEATURE_COLUMNS] = 50
    holdout[TARGET] = 9999
    first = SmallMLPRegressor().fit(train, epochs=2, validation=holdout)
    second = SmallMLPRegressor().fit(train, epochs=2)
    np.testing.assert_array_equal(first.predict(train[FEATURE_COLUMNS]), second.predict(train[FEATURE_COLUMNS]))
    np.testing.assert_allclose(first.feature_scaler.mean_, train[FEATURE_COLUMNS].mean(), atol=1e-14)
    assert first.target_scaler.mean_[0] == pytest.approx(train[TARGET].mean())
    assert sum(p.numel() for p in first.network.parameters()) == 225
    assert len(first.history) == 2
    assert np.isfinite(first.predict(holdout[FEATURE_COLUMNS])).all()


def test_mlp_rejects_invalid_targets_and_epoch_count():
    train = controlled_frame()
    with pytest.raises(ValueError, match="positivo"):
        SmallMLPRegressor().fit(train, epochs=0)
    train.loc[0, TARGET] = float("inf")
    with pytest.raises(ValueError, match="finitas"):
        SmallMLPRegressor().fit(train)
