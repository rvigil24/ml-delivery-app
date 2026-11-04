"""Contrato de variables v2; una prueba sin entrenar ni acceder a servicios."""

import numpy as np
import pandas as pd
import pytest

from delivery_ml.delivery_v2 import eta_features, risk_features, spherical_distance


def test_eta_without_deadline_does_not_run_risk_model():
    from datetime import datetime, timezone
    from types import SimpleNamespace
    from delivery_ml.delivery_v2 import DeliveryPredictorV2
    class ETA:
        def predict(self, context):
            assert "promised_minutes" not in context
            return [12.5]
    class Risk:
        def predict_proba(self, context):
            assert context.promised_minutes.iloc[0] == 30
            return np.array([[.8, .2]])
    model = DeliveryPredictorV2.__new__(DeliveryPredictorV2)
    model.eta, model.risk = ETA(), Risk()
    model.metadata = {"model_version": "fixture", "eta_algorithm": "fixture", "risk_algorithm": "fixture",
                      "training_input_ranges": {"distance_km": [0, 10], "promised_minutes": [30, 60]}, "limitations": []}
    point = SimpleNamespace(latitude=13.7, longitude=-89.2)
    stamp = datetime(2026, 11, 4, tzinfo=timezone.utc)
    result = model.predict(stamp, point, point, None)
    assert result["estimated_minutes"] == 12.5 and result["distance_km"] == 0
    assert result["late_probability"] is None and result["promised_minutes"] is None
    assert not result["outside_training_range"]
    assert model.predict(stamp, point, point, 30)["late_probability"] == .2


def test_features_use_distance_and_promise_without_future_events():
    context = pd.DataFrame({"request_hour_utc": [12, 12], "request_weekday_utc": [1, 1],
        "distance_km": [1., 5.], "promised_minutes": [30., 45.], "arrive_time": [1, 999999]})
    eta = eta_features(context)
    risk = risk_features(context)
    assert list(eta.columns) == ["request_hour_sin", "request_hour_cos", "request_weekday_sin", "request_weekday_cos", "distance_km"]
    assert eta.distance_km.tolist() == [1., 5.]
    assert risk.promised_minutes.tolist() == [30., 45.]
    assert "arrive_time" not in risk
    assert spherical_distance(0, 0, 0, 1) == pytest.approx(111.19508, abs=1e-5)
    with pytest.raises(ValueError):
        risk_features(context.assign(promised_minutes=-1))
