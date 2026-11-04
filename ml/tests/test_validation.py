"""Casos controlados para aislamiento temporal; no son registros experimentales."""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from delivery_ml import validation
from delivery_ml.model_data import FEATURE_COLUMNS, TARGET, temporal_features


def controlled_train():
    timestamps = pd.date_range("2022-01-01", periods=96, freq="h", tz="UTC")
    train = temporal_features(pd.DataFrame({"request_hour_utc": timestamps.hour,
                                          "request_weekday_utc": timestamps.dayofweek}))
    train[TARGET] = 20 + 5 * train["request_hour_sin"]
    train["platform_order_time"] = timestamps.as_unit("s").astype("int64")
    train["arrive_time"] = train["platform_order_time"] + 60 * train[TARGET]
    # Duraciones enteras y coherentes para estos casos controlados.
    train["arrive_time"] = train["arrive_time"].round().astype("int64")
    train[TARGET] = (train["arrive_time"] - train["platform_order_time"]) / 60
    train["order_id"] = [f"control-{i}" for i in range(len(train))]
    train["source_waybill_id"] = train["order_id"]
    return train


def test_daily_folds_purge_labels_at_boundary_and_reject_duplicates():
    train = controlled_train()
    boundary = int(pd.Timestamp("2022-01-02T00:00:00Z").timestamp())
    train.loc[23, "arrive_time"] = boundary
    train.loc[23, TARGET] = (boundary - train.loc[23, "platform_order_time"]) / 60
    folds = validation.expanding_day_folds(train)
    assert 23 not in folds[0][0]  # Llegar exactamente al corte aún no es pasado.
    assert 23 in folds[1][0]  # Etiqueta disponible en el fold siguiente.
    for fit, holdout in folds:
        cutoff = train.iloc[holdout]["platform_order_time"].min()
        assert train.iloc[fit]["arrive_time"].max() < cutoff
        assert set(fit).isdisjoint(holdout)
    with pytest.raises(ValueError, match="duplicados"):
        validation.expanding_day_folds(pd.concat([train, train.iloc[[0]]]))
    with pytest.raises(ValueError, match="suficientes días"):
        validation.expanding_day_folds(train.iloc[:24])


def test_grid_search_fits_scaler_on_each_fold_then_refits_only_full_train(monkeypatch):
    train = controlled_train()
    fitted_means = []

    class RecordingScaler(StandardScaler):
        def fit(self, x, y=None, sample_weight=None):
            fitted_means.append(np.asarray(x).mean(axis=0))
            return super().fit(x, y, sample_weight=sample_weight)

    monkeypatch.setattr(validation, "build_models", lambda: {
        "linear_regression": make_pipeline(RecordingScaler(), LinearRegression())})
    monkeypatch.setitem(validation.PARAM_GRIDS, "linear_regression",
                        {"linearregression__fit_intercept": [True, False]})
    report = validation.search_models(train, n_splits=2)
    folds = validation.expanding_day_folds(train, n_splits=2)
    features = train[FEATURE_COLUMNS]
    assert len(fitted_means) == 5  # Dos candidatos por dos folds, más refit.
    for mean, (fit, _) in zip(fitted_means, folds * 2):
        np.testing.assert_allclose(mean, features.iloc[fit].mean(), atol=1e-14)
    np.testing.assert_allclose(fitted_means[-1], features.mean(), atol=1e-14)
    result = report["models"]["linear_regression"]
    assert result["best_parameters"] == {"linearregression__fit_intercept": True}
    assert result["best_mean_mae_minutes"] == min(c["mean_mae_minutes"] for c in result["candidates"])
    assert result["best_mean_mae_minutes"] == pytest.approx(np.mean(result["candidates"][result["best_index"]]["fold_mae_minutes"]))
    assert result["refit_training_rows"] == len(train)
    assert all(report["checks"].values())
