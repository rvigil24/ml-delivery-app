"""T31: políticas, costos y ubicaciones de fixture; no cotizaciones comerciales."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from decimal import Decimal as D

from fastapi.testclient import TestClient
import pytest

from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.api.app import create_app
from delivery.domain.estimation import PredictionUnavailable
from delivery.domain.models import Business, DeliveryDuration, DurationSource, Location, Order, OrderStatus as S
from delivery.domain.order_lifecycle import MissingPrerequisite
from delivery.domain.pricing import OperatorCosts, PricingPolicy
from delivery.domain.vehicle_rules import ServiceArea, VehicleLimits, VehiclePolicy
from delivery.services.orders import OrderService
from delivery.services.predictions import PredictionService
from delivery.services.quote_previews import QuoteConfigurationMissing, QuotePreviewService


NOW = datetime(2022, 10, 22, 18, tzinfo=timezone.utc)
BUSINESS = Business("fixture-business", "Negocio de prueba", Location(0, 0))
ORDER = Order("fixture-order", BUSINESS.id, BUSINESS.location, Location(0, .01), "Pedido de prueba")
PRICES = PricingPolicy("fixture-prices", "USD", D("0.01"), D(3), D(2), D(1), D("0.5"))
AREA = ServiceArea("fixture-area", Location(-1, -1), Location(1, 1))
VEHICLES = VehiclePolicy("fixture-vehicles", AREA, VehicleLimits(D(20), D(5)), VehicleLimits(D(30), D(10)))
COSTS = OperatorCosts("USD", D("0.10"), D("0.20"))
BODY = {"quote_id": "fixture-quote", "load_kg": "1",
        "costs": {"currency": "USD", "variable_cost": "0.10", "attributable_cost": "0.20"}}


class CountingOrders(InMemoryOrderRepository):
    def __init__(self):
        super().__init__()
        self.reads = 0

    def get(self, order_id):
        self.reads += 1
        return super().get(order_id)


class FixturePredictor:
    def __init__(self):
        self.calls = []

    def predict(self, stamp):
        self.calls.append(stamp)
        assert stamp == NOW
        return DeliveryDuration(12.5, DurationSource.PREDICTION, "Intervalo de fixture", "fixture-model")


def setup(order=ORDER):
    repository = CountingOrders()
    orders = OrderService(repository, InMemoryBusinesses([BUSINESS]), clock=lambda: NOW)
    initial = orders.register(order)
    return repository, orders, initial


def test_service_combines_a_single_snapshot_model_price_and_vehicle_rules_without_mutation():
    repository, orders, initial = setup()
    predictor = FixturePredictor()
    service = QuotePreviewService(repository, PredictionService(predictor), PRICES, VEHICLES)
    preview = service.preview(ORDER.id, BODY["quote_id"], D(1), COSTS)
    assert repository.reads == 1 and preview.record is initial
    assert predictor.calls == [initial.events[0].occurred_at]
    assert preview.vehicles.order is initial.order and preview.pricing.estimate.quote.order_id == ORDER.id
    assert preview.quote.duration.minutes == 12.5 and preview.quote.duration.model_version == "fixture-model"
    assert preview.quote.distance_km == pytest.approx(1.111950802)
    assert preview.quote.amounts.delivery_fee == D("5.22") and preview.quote.amounts.margin == D("3.36")
    assert preview.pricing.policy is PRICES and preview.vehicles.policy is VEHICLES
    assert len(preview.vehicles.eligible_vehicles) == 2
    assert preview.academic_only and not preview.coverage_validated and not preview.commercial_quote_validated
    assert orders.get(ORDER.id) is initial and len(initial.events) == 1
    with pytest.raises(MissingPrerequisite):
        orders.transition(ORDER.id, S.REQUESTED, S.QUOTED)
    with pytest.raises(FrozenInstanceError):
        preview.quote.amounts.margin = D(999)


def test_missing_configuration_model_or_incompatible_inputs_never_modify_the_order():
    repository, orders, initial = setup()
    predictor = FixturePredictor()
    for repo, prices, vehicles in ((None, PRICES, VEHICLES), (repository, None, VEHICLES), (repository, PRICES, None)):
        with pytest.raises(QuoteConfigurationMissing):
            QuotePreviewService(repo, predictor, prices, vehicles).preview(ORDER.id, "q", D(1), COSTS)
    with pytest.raises(PredictionUnavailable):
        QuotePreviewService(repository, PredictionService(None), PRICES, VEHICLES).preview(ORDER.id, "q", D(1), COSTS)
    service = QuotePreviewService(repository, predictor, PRICES, VEHICLES)
    for quote_id, load, costs in ((" ", D(1), COSTS), ("q", D(0), COSTS),
                                  ("q", D(1), OperatorCosts("EUR", D(0), D(0)))):
        with pytest.raises(ValueError):
            service.preview(ORDER.id, quote_id, load, costs)
    assert predictor.calls == [] and orders.get(ORDER.id) is initial


def test_http_quote_and_predict_share_one_loaded_model_and_quote_uses_stored_creation(tmp_path):
    repository, orders, initial = setup()
    loaded = []
    predictor = FixturePredictor()

    def factory(path):
        loaded.append(path)
        return predictor

    with TestClient(create_app(tmp_path, factory, orders=repository, pricing_policy=PRICES, vehicle_policy=VEHICLES)) as client:
        assert client.app.state.predictions.predict(datetime(2022, 10, 22, 18, tzinfo=timezone.utc)).minutes >= 0
        for _ in range(2):
            response = client.post(f"/orders/{ORDER.id}/quotes", json=BODY)
            assert response.status_code == 200
            body = response.json()
            assert body["quote_id"] == BODY["quote_id"] and body["order_id"] == ORDER.id
            assert body["duration"]["requested_at_utc"] == "2022-10-22T18:00:00Z"
            assert body["duration"]["duration_minutes"] == 12.5
            assert body["amounts"]["delivery_fee"] == "5.22" and body["amounts"]["margin"] == "3.36"
            assert body["pricing_policy_version"] == PRICES.version and body["vehicle_policy_version"] == VEHICLES.version
            assert len(body["eligible_vehicles"]) == 2 and body["limitations"]
            assert body["experimental"] and not body["commercial_quote_validated"] and not body["coverage_validated"]
        assert loaded == [tmp_path] and predictor.calls == [NOW, NOW, NOW]
        schema = client.get("/openapi.json").json()
        assert set(schema["paths"]["/orders/{order_id}/quotes"]["post"]["responses"]) == {"200", "404", "409", "422", "503", "500"}
    assert orders.get(ORDER.id) is initial


def test_http_quote_reports_configuration_validation_missing_order_and_state_errors(tmp_path):
    repository, orders, initial = setup()
    factory = lambda path: FixturePredictor()
    with TestClient(create_app(tmp_path, factory)) as client:
        response = client.post(f"/orders/{ORDER.id}/quotes", json=BODY)
        assert response.status_code == 503 and response.json()["detail"]["code"] == "quote_configuration_missing"
    app = create_app(tmp_path, factory, orders=repository, pricing_policy=PRICES, vehicle_policy=VEHICLES)
    with TestClient(app) as client:
        assert client.post("/orders/missing/quotes", json=BODY).status_code == 404
        for changes in ({"requested_at": "2022-10-22T18:00:00Z"}, {"quote_id": " "},
                        {"load_kg": "NaN"}, {"costs": {**BODY["costs"], "currency": "EUR"}}):
            assert client.post(f"/orders/{ORDER.id}/quotes", json={**BODY, **changes}).status_code == 422
        assert orders.get(ORDER.id) is initial
        orders.transition(ORDER.id, S.REQUESTED, S.CANCELLED)
        assert client.post(f"/orders/{ORDER.id}/quotes", json=BODY).status_code == 409
    fresh_repository, _, _ = setup()
    def unavailable(path):
        raise PredictionUnavailable("private model location")
    with TestClient(create_app(tmp_path, unavailable, orders=fresh_repository,
                              pricing_policy=PRICES, vehicle_policy=VEHICLES)) as client:
        response = client.post(f"/orders/{ORDER.id}/quotes", json=BODY)
        assert response.status_code == 503 and "private" not in response.text


def test_no_vehicle_option_keeps_all_reasons_without_claiming_commercial_coverage():
    repository, orders, initial = setup(replace(ORDER, destination=Location(0, 2)))
    preview = QuotePreviewService(repository, FixturePredictor(), PRICES, VEHICLES).preview(ORDER.id, "q", D(1), COSTS)
    assert not preview.vehicles.eligible_vehicles and not preview.vehicles.within_configured_area
    assert all(decision.reasons for decision in preview.vehicles.decisions)
    assert preview.quote.amounts is not None and not preview.commercial_quote_validated
    assert orders.get(ORDER.id) is initial
