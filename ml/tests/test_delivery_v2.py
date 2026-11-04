"""Contrato de variables v2; una prueba sin entrenar ni acceder a servicios."""

import pandas as pd
import pytest

from delivery_ml.delivery_v2 import eta_features, risk_features, spherical_distance


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
