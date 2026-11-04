"""T26: fixtures sintéticas; no cotizaciones, cargas ni repartidores reales."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from decimal import Decimal as D
from threading import Barrier

import pytest

from delivery.adapters.memory import InMemoryBusinesses
from delivery.adapters.memory_dispatch import InMemoryDispatchRepository
from delivery.domain.assignments import AssignmentConflict, AssignmentNotFound, CourierNotFound, prepare_assignment
from delivery.domain.models import Business, Courier, Location, Order, OrderStatus as S, VehicleType
from delivery.domain.order_lifecycle import MissingPrerequisite
from delivery.domain.routing import RouteConfigurationMissing, RoutePolicy, StopType
from delivery.domain.vehicle_rules import ServiceArea, VehicleLimits, VehiclePolicy
from delivery.services.assignments import AssignmentService, DispatchOrderRequirements
from delivery.services.orders import OrderService


NOW = datetime(2022, 1, 1, tzinfo=timezone.utc)
START = Location(0, 0)
AREA = ServiceArea("fixture-area", Location(-1, -1), Location(1, 1))
ROUTES = RoutePolicy("fixture-route", 2, AREA)
VEHICLES = VehiclePolicy("fixture-vehicle", AREA, VehicleLimits(D(20), D(5)), VehicleLimits(D(30), D(10)))
COURIER = Courier("fixture-courier", VehicleType.BICYCLE, approved=True, available=True)
A = Order("a", "business-a", Location(0, .02), Location(0, -.001), "Fixture A")
B = Order("b", "business-b", Location(0, .01), Location(0, .03), "Fixture B")
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
    businesses = InMemoryBusinesses([Business(order.business_id, "Fixture", order.origin) for order in (A, B)])
    orders = OrderService(repository, businesses, DispatchOrderRequirements(repository, quotes), lambda: NOW)
    for order in (A, B):
        orders.register(order)
        orders.transition(order.id, S.REQUESTED, S.QUOTED)
        orders.transition(order.id, S.QUOTED, S.CONFIRMED)
    assignments = AssignmentService(repository, ROUTES, VEHICLES, quotes, lambda: NOW)
    return repository, orders, assignments


def test_group_reservation_progress_and_release_preserve_history_and_capacity():
    repository, orders, service = setup()
    before = orders.get(A.id)
    with pytest.raises(MissingPrerequisite):
        orders.transition(A.id, S.CONFIRMED, S.ASSIGNED)
    with pytest.raises(AssignmentConflict):
        repository.transition(A.id, S.CONFIRMED, S.ASSIGNED, NOW)
    assignment = service.assign("run", COURIER.id, [B.id, A.id], START, LOADS)
    assert assignment.peak_load_kg == D(5)  # Exact equality with the configured limit is allowed.
    assert assignment.loads_kg == ((A.id, D(2)), (B.id, D(3)))
    assert assignment.active and assignment.simulated and not assignment.road_route_validated
    assert before.order.status is S.CONFIRMED and len(before.events) == 3
    assert not repository.get_courier(COURIER.id).available
    assert all(orders.get(identifier).order.status is S.ASSIGNED for identifier in LOADS)
    with pytest.raises(FrozenInstanceError):
        assignment.peak_load_kg = D(0)
    with pytest.raises(AssignmentConflict):
        service.release("run")
    with pytest.raises(AssignmentConflict):
        orders.transition(A.id, S.ASSIGNED, S.PICKED_UP)  # B must be picked up first.
    for stop in assignment.route.stops:
        expected, target = (S.ASSIGNED, S.PICKED_UP) if stop.kind is StopType.PICKUP else (S.PICKED_UP, S.DELIVERED)
        orders.transition(stop.order_id, expected, target)
    assert not repository.get_courier(COURIER.id).available
    released = service.release("run")
    assert not released.active and released.released_at == NOW
    assert repository.get_courier(COURIER.id).available
    for identifier in LOADS:
        assert [event.status for event in orders.get(identifier).events] == [
            S.REQUESTED, S.QUOTED, S.CONFIRMED, S.ASSIGNED, S.PICKED_UP, S.DELIVERED]
        assert all(event.occurred_at.tzinfo is timezone.utc for event in orders.get(identifier).events)
    with pytest.raises(AssignmentConflict):
        service.release("run")


def test_unapproved_unavailable_and_unknown_couriers_do_not_change_orders():
    for courier in (replace(COURIER, approved=False), replace(COURIER, available=False)):
        repository, orders, service = setup((courier,))
        before = orders.get(A.id)
        with pytest.raises(AssignmentConflict):
            service.assign("run", courier.id, [A.id], START, {A.id: D(1)})
        assert orders.get(A.id) is before and repository.get_courier(courier.id) == courier
        with pytest.raises(AssignmentNotFound):
            service.get("run")
    with pytest.raises(CourierNotFound):
        service.assign("run", "missing", [A.id], START, {A.id: D(1)})


def test_full_route_distance_accumulated_load_and_zone_are_checked_without_writes():
    repository, orders, _ = setup()
    before = tuple(orders.get(identifier) for identifier in LOADS)
    limited = replace(VEHICLES, bicycle=VehicleLimits(D(4), D(5)))
    # Each origin/destination distance fits 4 km; the complete open route does not.
    service = AssignmentService(repository, ROUTES, limited, FixtureQuoteRequirements(), lambda: NOW)
    with pytest.raises(AssignmentConflict, match="ruta completa"):
        service.assign("km", COURIER.id, list(LOADS), START, LOADS)
    service = AssignmentService(repository, ROUTES, VEHICLES, FixtureQuoteRequirements(), lambda: NOW)
    with pytest.raises(AssignmentConflict, match="carga acumulada"):
        service.assign("load", COURIER.id, list(LOADS), START, {A.id: D(3), B.id: D(3)})
    smaller_area = ServiceArea("other-fixture", Location(-.5, -.5), Location(.5, .015))
    outside = AssignmentService(repository, ROUTES, replace(VEHICLES, area=smaller_area),
                                FixtureQuoteRequirements(), lambda: NOW)
    with pytest.raises(AssignmentConflict, match="incompatible"):
        outside.assign("area", COURIER.id, list(LOADS), START, LOADS)
    with pytest.raises(ValueError, match="exactamente"):
        service.assign("missing-load", COURIER.id, list(LOADS), START, {A.id: D(1)})
    assert tuple(orders.get(identifier) for identifier in LOADS) == before
    assert repository.get_courier(COURIER.id).available
    plan = prepare_assignment("boundary", COURIER, tuple(record.order for record in before),
                              START, ROUTES, VEHICLES, LOADS, NOW)
    exact = replace(VEHICLES, bicycle=replace(VEHICLES.bicycle, max_distance_km=plan.route.total_distance_km))
    boundary = AssignmentService(repository, ROUTES, exact, FixtureQuoteRequirements(), lambda: NOW)
    assert boundary.assign("boundary", COURIER.id, list(LOADS), START, LOADS).route.total_distance_km == exact.bicycle.max_distance_km


def test_missing_configuration_quote_evidence_and_confirmation_block_the_entire_group():
    repository, orders, _ = setup()
    before = tuple(orders.get(identifier) for identifier in LOADS)
    with pytest.raises(RouteConfigurationMissing):
        AssignmentService(repository).assign("run", COURIER.id, list(LOADS), START, LOADS)
    with pytest.raises(MissingPrerequisite):
        AssignmentService(repository, ROUTES, VEHICLES).assign("run", COURIER.id, list(LOADS), START, LOADS)
    service = AssignmentService(repository, ROUTES, VEHICLES, FixtureQuoteRequirements(rejected=B.id), lambda: NOW)
    with pytest.raises(MissingPrerequisite, match="rechazada"):
        service.assign("run", COURIER.id, list(LOADS), START, LOADS)
    assert tuple(orders.get(identifier) for identifier in LOADS) == before
    orders.transition(B.id, S.CONFIRMED, S.CANCELLED)
    with pytest.raises(MissingPrerequisite, match="confirmados"):
        service.assign("run", COURIER.id, list(LOADS), START, LOADS)
    assert orders.get(A.id) is before[0] and repository.get_courier(COURIER.id).available


def test_competing_assignments_cannot_share_a_courier_or_an_order():
    other = replace(COURIER, id="second")
    for candidates in (((A, COURIER), (B, COURIER)), ((A, COURIER), (A, other))):
        repository, orders, _ = setup((COURIER, other))
        quotes = FixtureQuoteRequirements(barrier=Barrier(2))
        service = AssignmentService(repository, ROUTES, VEHICLES, quotes, lambda: NOW)

        def assign(candidate):
            order, courier = candidate
            try:
                service.assign("run-" + order.id + courier.id, courier.id, [order.id], START, {order.id: D(1)})
                return "assigned"
            except AssignmentConflict:
                return "conflict"

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(assign, candidates))
        assert sorted(results) == ["assigned", "conflict"]
        assert sorted(len(orders.get(identifier).events) for identifier in LOADS) == [3, 4]
        assert sum(not repository.get_courier(c.id).available for c in (COURIER, other)) == 1


def test_duplicate_assignment_id_does_not_occupy_another_courier_or_order():
    other = replace(COURIER, id="second", vehicle=VehicleType.MOTORCYCLE)
    repository, orders, service = setup((COURIER, other))
    assignment = service.assign("run", COURIER.id, [A.id], START, {A.id: D(1)})
    before = orders.get(B.id)
    with pytest.raises(AssignmentConflict, match="duplicado"):
        service.assign("run", other.id, [B.id], START, {B.id: D(1)})
    assert service.get("run") is assignment and orders.get(B.id) is before
    assert repository.get_courier(other.id).available


def test_stale_group_snapshot_rejects_reservation_without_partial_assignment():
    repository, orders, _ = setup()
    records = tuple(orders.get(identifier) for identifier in LOADS)
    prepared = prepare_assignment("run", COURIER, tuple(record.order for record in records),
                                  START, ROUTES, VEHICLES, LOADS, NOW)
    orders.transition(B.id, S.CONFIRMED, S.CANCELLED)
    with pytest.raises(AssignmentConflict, match="cambió"):
        repository.commit_assignment(prepared, records)
    assert orders.get(A.id) is records[0] and orders.get(B.id).order.status is S.CANCELLED
    assert repository.get_courier(COURIER.id).available
    with pytest.raises(AssignmentNotFound):
        repository.get_assignment("run")
