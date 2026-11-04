"""Elegibilidad de vehículos con límites explícitos."""

from decimal import Decimal

from delivery.domain import Location, Order, VehicleType
from delivery.domain.estimation import haversine_km
from delivery.domain.vehicle_rules import (
    ServiceArea,
    VehicleLimits,
    VehiclePolicy,
    evaluate_vehicle_rules,
)

D = Decimal
ORDER = Order(
    "fixture-order", "fixture-business", Location(0, 0), Location(1, 1), "Prueba"
)
DISTANCE = D(str(haversine_km(ORDER.origin, ORDER.destination)))


def fixture_policy():
    area = ServiceArea("fixture-area", Location(0, 0), Location(1, 1))
    return VehiclePolicy(
        "fixture-v1",
        area,
        VehicleLimits(DISTANCE, D("5")),
        VehicleLimits(DISTANCE, D("5")),
    )


def test_vehicle_limits():
    policy = fixture_policy()
    result = evaluate_vehicle_rules(ORDER, D("5"), policy)
    assert policy.area.contains(ORDER.origin) and policy.area.contains(
        ORDER.destination
    )
    assert result.within_configured_area and result.distance_km == DISTANCE
    assert result.eligible_vehicles == (VehicleType.BICYCLE, VehicleType.MOTORCYCLE)
    assert all(
        decision.eligible and not decision.reasons for decision in result.decisions
    )
    assert result.academic_only and result.policy.version == "fixture-v1"
