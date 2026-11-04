"""Orden de recogidas y entregas."""

from decimal import Decimal

from delivery.domain import Location, Order
from delivery.domain.routing import RoutePolicy, StopType, suggest_route
from delivery.domain.vehicle_rules import ServiceArea

START = Location(0, 0)
POLICY = RoutePolicy(
    "fixture-v1", 2, ServiceArea("fixture-area", Location(-1, -1), Location(1, 1))
)
A = Order("a-fixture", "business-a", Location(0, 0.02), Location(0, -0.001), "Prueba A")
B = Order("b-fixture", "business-b", Location(0, 0.01), Location(0, 0.03), "Prueba B")


def test_pickup_before_delivery():
    result = suggest_route((A, B), START, POLICY)
    assert [(stop.order_id, stop.kind) for stop in result.stops] == [
        (B.id, StopType.PICKUP),
        (A.id, StopType.PICKUP),
        (B.id, StopType.DELIVERY),
        (A.id, StopType.DELIVERY),
    ]
    for order in (A, B):
        positions = [
            index
            for index, stop in enumerate(result.stops)
            if stop.order_id == order.id
        ]
        assert len(positions) == 2
        assert result.stops[positions[0]].kind is StopType.PICKUP
    assert result.total_distance_km == sum(
        (stop.leg_distance_km for stop in result.stops), Decimal(0)
    )
    assert result.stops[-1].location == A.destination != START
    assert (
        result.academic_only
        and not result.capacity_validated
        and not result.road_route_validated
    )
