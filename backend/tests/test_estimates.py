"""Geometría y casos controlados; no son negocios, tiempos reales o datos ML."""

from datetime import datetime, timedelta, timezone
import json
import math

import pytest

from delivery.adapters.local_model import LocalDurationPredictor
from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.domain import Business, DeliveryDuration, DurationSource, Location, Order, OrderStatus
from delivery.domain.estimation import DISTANCE_METHOD, EARTH_RADIUS_KM, PredictionUnavailable, haversine_km
from delivery.domain.order_lifecycle import OrderConflict, OrderNotFound
from delivery.services.estimates import AcademicQuoteService
from delivery.services.orders import OrderService
from delivery_ml import artifact


NOW = datetime(2022, 1, 2, 1, tzinfo=timezone.utc)


def registered_order():
    business = Business("fixture-business", "Negocio de prueba", Location(0, 0))
    order = Order("fixture-order", business.id, business.location, Location(0, 1), "Prueba")
    repository = InMemoryOrderRepository()
    service = OrderService(repository, InMemoryBusinesses([business]), clock=lambda: NOW)
    return repository, service, service.register(order)


def test_haversine_handles_zero_symmetry_antimeridian_and_antipodes_in_kilometers():
    assert haversine_km(Location(0, 0), Location(0, 0)) == 0
    distance = haversine_km(Location(0, 0), Location(0, 1))
    assert distance == pytest.approx(111.195080, abs=1e-6)
    assert distance == haversine_km(Location(0, 1), Location(0, 0))
    assert haversine_km(Location(0, 179), Location(0, -179)) == pytest.approx(2 * distance)
    assert haversine_km(Location(0, 0), Location(0, 180)) == pytest.approx(math.pi * EARTH_RADIUS_KM)


def test_academic_draft_uses_creation_time_has_no_amounts_and_does_not_change_order():
    class ControlledPredictor:
        def predict(self, requested_at):
            assert requested_at == NOW
            return DeliveryDuration(10, DurationSource.PREDICTION, "Intervalo de fixture", "fixture-model")

    repository, _, original = registered_order()
    estimate = AcademicQuoteService(repository, ControlledPredictor()).estimate(original.order.id, "fixture-quote")
    assert estimate.quote.order_id == original.order.id
    assert estimate.quote.distance_method == DISTANCE_METHOD
    assert estimate.quote.distance_km == pytest.approx(111.195080, abs=1e-6)
    assert estimate.quote.duration.model_version == "fixture-model"
    assert estimate.quote.amounts is None
    assert estimate.academic_only and not estimate.coverage_validated and estimate.limitations
    assert repository.get(original.order.id) is original


def test_missing_predictor_unknown_or_terminal_order_do_not_create_a_commercial_quote():
    repository, service, original = registered_order()
    estimator = AcademicQuoteService(repository)
    with pytest.raises(OrderNotFound):
        estimator.estimate("unknown", "fixture-quote")
    with pytest.raises(ValueError, match="id"):
        estimator.estimate(original.order.id, "")
    with pytest.raises(PredictionUnavailable):
        estimator.estimate(original.order.id, "fixture-quote")
    assert repository.get(original.order.id) is original
    service.transition(original.order.id, OrderStatus.REQUESTED, OrderStatus.CANCELLED)
    with pytest.raises(OrderConflict):
        estimator.estimate(original.order.id, "fixture-quote")


def test_local_predictor_loads_once_uses_utc_and_preserves_model_version(tmp_path, monkeypatch):
    calls = []

    class ControlledPipeline:
        def predict(self, frame):
            assert frame.to_dict(orient="list") == {"request_hour_utc": [1], "request_weekday_utc": [6]}
            return [12.5]  # Valor de fixture para validar el adaptador, no resultado ML real.

    def controlled_load(directory):
        calls.append(directory)
        return ControlledPipeline()

    monkeypatch.setattr(artifact, "load_pipeline", controlled_load)
    (tmp_path / "metadata.json").write_text(json.dumps({"target": "time_taken_min", "target_unit": "minutes",
                                                       "model_version": "fixture-model"}))
    predictor = LocalDurationPredictor(tmp_path)
    local_stamp = NOW.astimezone(timezone(timedelta(hours=-6)))
    for _ in range(2):
        duration = predictor.predict(local_stamp)
        assert duration.minutes == 12.5
        assert duration.source is DurationSource.PREDICTION and duration.model_version == "fixture-model"
    assert calls == [tmp_path]


def test_bad_artifact_or_prediction_fails_explicitly_without_fallback(tmp_path, monkeypatch):
    with pytest.raises(PredictionUnavailable):
        LocalDurationPredictor(tmp_path / "missing")

    class BadPipeline:
        def predict(self, frame):
            return [float("nan")]

    monkeypatch.setattr(artifact, "load_pipeline", lambda directory: BadPipeline())
    metadata = {"target": "wrong-target", "target_unit": "minutes", "model_version": "fixture-model"}
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))
    with pytest.raises(PredictionUnavailable, match="Target"):
        LocalDurationPredictor(tmp_path)
    metadata["target"] = "time_taken_min"
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))
    predictor = LocalDurationPredictor(tmp_path)
    with pytest.raises(ValueError, match="zona horaria"):
        predictor.predict(datetime(2022, 1, 2))
    with pytest.raises(PredictionUnavailable):
        predictor.predict(NOW)
