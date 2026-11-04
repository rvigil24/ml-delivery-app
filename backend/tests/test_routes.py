"""Pedidos/coordenadas/límites ilustrativos de tests, sin entregas o rutas reales."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.domain import Business, Location, Order, OrderStatus
from delivery.domain.estimation import haversine_km
from delivery.domain.order_lifecycle import OrderConflict, OrderNotFound
from delivery.domain.routing import RouteConfigurationMissing, RoutePolicy, StopType, suggest_route
from delivery.domain.vehicle_rules import ServiceArea
from delivery.services.orders import OrderService
from delivery.services.routes import RouteSuggestionService


START = Location(0, 0)
POLICY = RoutePolicy("fixture-v1", 2, ServiceArea("fixture-area", Location(-1, -1), Location(1, 1)))
A = Order("a-fixture", "business-a", Location(0, 0.02), Location(0, -0.001), "Prueba A")
B = Order("b-fixture", "business-b", Location(0, 0.01), Location(0, 0.03), "Prueba B")


def test_nearest_admissible_stops_preserve_pickup_precedence_and_open_route_total():
    result = suggest_route((A, B), START, POLICY)
    assert [(stop.order_id, stop.kind) for stop in result.stops] == [
        (B.id, StopType.PICKUP), (A.id, StopType.PICKUP),
        (B.id, StopType.DELIVERY), (A.id, StopType.DELIVERY)]
    for order in (A, B):
        positions = [index for index, stop in enumerate(result.stops) if stop.order_id == order.id]
        assert len(positions) == 2
        assert result.stops[positions[0]].kind is StopType.PICKUP
    assert result.total_distance_km == sum((stop.leg_distance_km for stop in result.stops), Decimal(0))
    assert result.stops[-1].location == A.destination != START
    assert result.academic_only and not result.capacity_validated and not result.road_route_validated


def test_exact_ties_use_ids_and_keep_distinct_zero_length_stops_reproducibly():
    first = replace(A, origin=START, destination=Location(0, 0.02))
    second = replace(B, origin=START, destination=Location(0, 0.01))
    result = suggest_route((first, second), START, POLICY)
    assert result == suggest_route((second, first), START, POLICY)
    assert result.stops[0].order_id == A.id and result.stops[1].order_id == B.id
    assert result.stops[0].leg_distance_km == result.stops[1].leg_distance_km == 0
    assert len(result.stops) == 4


def test_invalid_groups_configuration_or_outside_area_fail_without_silent_filtering():
    with pytest.raises(ValueError, match="no vacío"):
        suggest_route((), START, POLICY)
    with pytest.raises(ValueError, match="duplicados"):
        suggest_route((A, A), START, POLICY)
    with pytest.raises(ValueError, match="max_orders"):
        suggest_route((A, B), START, replace(POLICY, max_orders=1))
    with pytest.raises(ValueError, match="entero positivo"):
        replace(POLICY, max_orders=True)
    with pytest.raises(ValueError, match="inicial"):
        suggest_route((A,), Location(2, 0), POLICY)
    with pytest.raises(ValueError, match="fuera de la zona"):
        suggest_route((replace(A, destination=Location(2, 0)),), START, POLICY)
    with pytest.raises(RouteConfigurationMissing):
        RouteSuggestionService(InMemoryOrderRepository()).suggest([A.id], START)


def test_assigned_picked_up_and_terminal_orders_cannot_be_planned_again():
    for status in (OrderStatus.ASSIGNED, OrderStatus.PICKED_UP, OrderStatus.DELIVERED, OrderStatus.CANCELLED):
        with pytest.raises(OrderConflict):
            suggest_route((replace(A, status=status),), START, POLICY)
    for status in (OrderStatus.REQUESTED, OrderStatus.QUOTED, OrderStatus.CONFIRMED):
        assert len(suggest_route((replace(A, status=status),), START, POLICY).stops) == 2


def test_service_preserves_order_history_and_single_order_route_without_return():
    repository = InMemoryOrderRepository()
    business = Business(A.business_id, "Negocio de prueba", A.origin)
    original = OrderService(repository, InMemoryBusinesses([business]),
        clock=lambda: datetime(2022, 1, 1, tzinfo=timezone.utc)).register(A)
    service = RouteSuggestionService(repository, POLICY)
    result = service.suggest([A.id], START)
    assert len(result.stops) == 2 and result.orders == (original.order,)
    expected = haversine_km(START, A.origin) + haversine_km(A.origin, A.destination)
    assert float(result.total_distance_km) == pytest.approx(expected)
    assert repository.get(A.id) is original and len(original.events) == 1
    with pytest.raises(FrozenInstanceError):
        result.total_distance_km = Decimal("999")
    with pytest.raises(OrderNotFound):
        service.suggest(["missing"], START)
    with pytest.raises(ValueError, match="colección"):
        service.suggest(A.id, START)
