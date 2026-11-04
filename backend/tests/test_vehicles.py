"""Zonas, cargas y límites ficticios solo de tests, sin recomendaciones comerciales."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.domain import Business, Location, Order, VehicleType
from delivery.domain.estimation import haversine_km
from delivery.domain.order_lifecycle import OrderNotFound
from delivery.domain.vehicle_rules import (
    ServiceArea, VehicleConfigurationMissing, VehicleLimits, VehiclePolicy,
    VehicleRejection as R, evaluate_vehicle_rules,
)
from delivery.services.orders import OrderService
from delivery.services.vehicles import VehicleRulesService


D = Decimal
ORDER = Order("fixture-order", "fixture-business", Location(0, 0), Location(1, 1), "Prueba")
DISTANCE = D(str(haversine_km(ORDER.origin, ORDER.destination)))


def fixture_policy():
    area = ServiceArea("fixture-area", Location(0, 0), Location(1, 1))
    return VehiclePolicy("fixture-v1", area, VehicleLimits(DISTANCE, D("5")), VehicleLimits(DISTANCE, D("5")))


def test_area_edges_and_exact_distance_load_limits_allow_both_without_selecting_one():
    policy = fixture_policy()
    result = evaluate_vehicle_rules(ORDER, D("5"), policy)
    assert policy.area.contains(ORDER.origin) and policy.area.contains(ORDER.destination)
    assert result.within_configured_area and result.distance_km == DISTANCE
    assert result.eligible_vehicles == (VehicleType.BICYCLE, VehicleType.MOTORCYCLE)
    assert all(decision.eligible and not decision.reasons for decision in result.decisions)
    assert result.academic_only and result.policy.version == "fixture-v1"


def test_independent_limits_explain_rejections_and_do_not_assume_motorcycle_always_allowed():
    policy = replace(fixture_policy(), bicycle=VehicleLimits(DISTANCE / 2, D("2")),
                     motorcycle=VehicleLimits(DISTANCE * 2, D("4")))
    result = evaluate_vehicle_rules(ORDER, D("3"), policy)
    assert result.eligible_vehicles == (VehicleType.MOTORCYCLE,)
    assert result.decisions[0].reasons == (R.DISTANCE, R.LOAD)
    overloaded = evaluate_vehicle_rules(ORDER, D("5"), policy)
    assert overloaded.eligible_vehicles == ()
    assert overloaded.decisions[1].reasons == (R.LOAD,)


def test_either_endpoint_outside_the_configured_area_rejects_every_vehicle():
    policy = replace(fixture_policy(), bicycle=VehicleLimits(D("1000"), D("100")),
                     motorcycle=VehicleLimits(D("1000"), D("100")))
    for order in (replace(ORDER, origin=Location(-0.1, 0)), replace(ORDER, destination=Location(1.1, 1))):
        result = evaluate_vehicle_rules(order, D("1"), policy)
        assert not result.within_configured_area and not result.eligible_vehicles
        assert all(decision.reasons == (R.OUTSIDE_AREA,) for decision in result.decisions)


def test_missing_or_invalid_configuration_and_load_are_not_replaced_by_defaults():
    policy = fixture_policy()
    with pytest.raises(VehicleConfigurationMissing):
        VehicleRulesService(InMemoryOrderRepository()).evaluate(ORDER.id, D("1"))
    with pytest.raises(ValueError, match="ambos vehículos"):
        replace(policy, motorcycle=None)
    with pytest.raises(ValueError, match="sur < norte"):
        ServiceArea("fixture-area", Location(1, 0), Location(0, 1))
    with pytest.raises(ValueError, match="positivo"):
        VehicleLimits(D("0"), D("1"))
    with pytest.raises(ValueError, match="Decimal"):
        VehicleLimits(1.0, D("1"))
    with pytest.raises(ValueError, match="load_kg"):
        evaluate_vehicle_rules(ORDER, D("NaN"), policy)
    with pytest.raises(ValueError, match="load_kg"):
        evaluate_vehicle_rules(ORDER, D("0"), policy)
    with pytest.raises(OrderNotFound):
        VehicleRulesService(InMemoryOrderRepository(), policy).evaluate("missing", D("1"))


def test_service_preserves_the_order_and_history_and_returns_immutable_policy_snapshot():
    repository = InMemoryOrderRepository()
    business = Business(ORDER.business_id, "Negocio de prueba", ORDER.origin)
    original = OrderService(repository, InMemoryBusinesses([business]),
        clock=lambda: datetime(2022, 1, 1, tzinfo=timezone.utc)).register(ORDER)
    policy = fixture_policy()
    result = VehicleRulesService(repository, policy).evaluate(ORDER.id, D("1"))
    assert result.order is original.order and result.policy is policy
    assert repository.get(ORDER.id) is original and len(original.events) == 1
    with pytest.raises(FrozenInstanceError):
        result.load_kg = D("999")
