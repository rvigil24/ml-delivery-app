"""Casos controlados de train/test y métricas; no son resultados del experimento."""

import math
import pandas as pd
import pytest

from delivery_ml.baseline import fit_baseline, evaluate_baseline
from delivery_ml.model_data import TARGET, temporal_features, model_xy


def frame(targets):
    context = pd.DataFrame({"request_hour_utc": list(range(len(targets))), "request_weekday_utc": 0})
    result = temporal_features(context)
    result[TARGET] = targets
    result["order_id"] = [f"test-{i}" for i in range(len(targets))]
    result["arrive_time"] = 999
    return result


def test_fits_training_median_and_test_labels_or_features_cannot_change_it():
    train = frame([10, 10, 100])
    model = fit_baseline(train)
    test = frame([1000, 2000])
    assert float(model.constant_.ravel()[0]) == 10
    x, _ = model_xy(test)
    assert model.predict(x).tolist() == [10, 10]
    evaluate_baseline(model, test)
    test[TARGET] = [1, 2]
    test["request_hour_sin"] = [-1, 1]
    evaluate_baseline(model, test)
    assert float(model.constant_.ravel()[0]) == 10
    x, _ = model_xy(test)
    assert model.predict(x).tolist() == [10, 10]


def test_reports_observed_errors_and_rejects_invalid_or_empty_targets():
    model = fit_baseline(frame([10, 10, 100]))
    result = evaluate_baseline(model, frame([10, 20]))
    assert result["rows"] == 2
    assert result["mae_minutes"] == 5
    assert result["rmse_minutes"] == pytest.approx(math.sqrt(50))
    with pytest.raises(ValueError, match="finita"):
        fit_baseline(frame([10, float("inf")]))
    with pytest.raises(ValueError, match="vacía"):
        fit_baseline(frame([]))
