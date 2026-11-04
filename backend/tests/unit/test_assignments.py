"""Asignación y liberación del repartidor."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from decimal import Decimal as D

import pytest
from delivery.adapters.memory import InMemoryBusinesses
from delivery.adapters.memory_dispatch import InMemoryDispatchRepository
from delivery.domain.assignments import AssignmentConflict
from delivery.domain.models import Business, Courier, Location, Order, VehicleType
from delivery.domain.models import OrderStatus as S
from delivery.domain.order_lifecycle import MissingPrerequisite
from delivery.domain.routing import RoutePolicy, StopType
from delivery.domain.vehicle_rules import ServiceArea, VehicleLimits, VehiclePolicy
from delivery.services.assignments import AssignmentService, DispatchOrderRequirements
from delivery.services.orders import OrderService

NOW = datetime(2022, 1, 1, tzinfo=timezone.utc)
START = Location(0, 0)
AREA = ServiceArea("fixture-area", Location(-1, -1), Location(1, 1))
ROUTES = RoutePolicy("fixture-route", 2, AREA)
VEHICLES = VehiclePolicy(
    "fixture-vehicle", AREA, VehicleLimits(D(20), D(5)), VehicleLimits(D(30), D(10))
)
COURIER = Courier("fixture-courier", VehicleType.BICYCLE, approved=True, available=True)
A = Order("a", "business-a", Location(0, 0.02), Location(0, -0.001), "Fixture A")
B = Order("b", "business-b", Location(0, 0.01), Location(0, 0.03), "Fixture B")
LOADS = {A.id: D(2), B.id: D(3)}


class FixtureQuoteRequirements:
    """Evidencia controlada exclusivamente para tests; nunca fuente comercial."""

    def __init__(self, rejected=None, barrier=None):
        self.rejected = rejected
        self.barrier = barrier

    def validate(self, order, target):
        assert target in (S.QUOTED, S.CONFIRMED)

    def validate_confirmed(self, order):
        if order.id == self.rejected:
            raise MissingPrerequisite("Cotización fixture rechazada")
        if self.barrier is not None:
            self.barrier.wait(timeout=5)


def setup(couriers=(COURIER,), quote=None):
    repository = InMemoryDispatchRepository(couriers)
    quotes = quote or FixtureQuoteRequirements()
    businesses = InMemoryBusinesses(
        [Business(order.business_id, "Fixture", order.origin) for order in (A, B)]
    )
    orders = OrderService(
        repository,
        businesses,
        DispatchOrderRequirements(repository, quotes),
        lambda: NOW,
    )
    for order in (A, B):
        orders.register(order)
        orders.transition(order.id, S.REQUESTED, S.QUOTED)
        orders.transition(order.id, S.QUOTED, S.CONFIRMED)
    assignments = AssignmentService(repository, ROUTES, VEHICLES, quotes, lambda: NOW)
    return repository, orders, assignments


def test_assignment_and_release():
    repository, orders, service = setup()
    before = orders.get(A.id)
    with pytest.raises(MissingPrerequisite):
        orders.transition(A.id, S.CONFIRMED, S.ASSIGNED)
    with pytest.raises(AssignmentConflict):
        repository.transition(A.id, S.CONFIRMED, S.ASSIGNED, NOW)
    assignment = service.assign("run", COURIER.id, [B.id, A.id], START, LOADS)
    assert assignment.peak_load_kg == D(
        5
    )  # Exact equality with the configured limit is allowed.
    assert assignment.loads_kg == ((A.id, D(2)), (B.id, D(3)))
    assert (
        assignment.active
        and assignment.simulated
        and not assignment.road_route_validated
    )
    assert before.order.status is S.CONFIRMED and len(before.events) == 3
    assert not repository.get_courier(COURIER.id).available
    assert all(
        orders.get(identifier).order.status is S.ASSIGNED for identifier in LOADS
    )
    with pytest.raises(FrozenInstanceError):
        assignment.peak_load_kg = D(0)
    with pytest.raises(AssignmentConflict):
        service.release("run")
    with pytest.raises(AssignmentConflict):
        orders.transition(A.id, S.ASSIGNED, S.PICKED_UP)  # B must be picked up first.
    for stop in assignment.route.stops:
        expected, target = (
            (S.ASSIGNED, S.PICKED_UP)
            if stop.kind is StopType.PICKUP
            else (S.PICKED_UP, S.DELIVERED)
        )
        orders.transition(stop.order_id, expected, target)
    assert not repository.get_courier(COURIER.id).available
    released = service.release("run")
    assert not released.active and released.released_at == NOW
    assert repository.get_courier(COURIER.id).available
    for identifier in LOADS:
        assert [event.status for event in orders.get(identifier).events] == [
            S.REQUESTED,
            S.QUOTED,
            S.CONFIRMED,
            S.ASSIGNED,
            S.PICKED_UP,
            S.DELIVERED,
        ]
        assert all(
            event.occurred_at.tzinfo is timezone.utc
            for event in orders.get(identifier).events
        )
    with pytest.raises(AssignmentConflict):
        service.release("run")
