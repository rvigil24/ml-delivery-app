"""Fixtures controladas de simulación, no pedidos reales ni observaciones ML."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from threading import Barrier

import pytest

from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.domain import Business, Location, Order, OrderStatus as S
from delivery.domain.order_lifecycle import (
    BusinessNotFound, DuplicateOrder, MissingPrerequisite, OrderConflict, OrderNotFound,
)
from delivery.services.orders import OrderService


NOW = datetime(2022, 1, 1, tzinfo=timezone.utc)
BUSINESS = Business("business-fixture", "Negocio de prueba", Location(0, 0))
ORDER = Order("order-fixture", BUSINESS.id, BUSINESS.location, Location(0, 1), "Pedido de prueba")


class ControlledRequirements:
    """Autoriza solo dentro de estas pruebas de la máquina de estados."""

    def __init__(self):
        self.checked = []

    def validate(self, order, target):
        self.checked.append((order.id, target))


def service(requirements=None, clock=lambda: NOW):
    return OrderService(InMemoryOrderRepository(), InMemoryBusinesses([BUSINESS]), requirements, clock)


def test_register_query_history_is_utc_immutable_and_duplicate_does_not_overwrite():
    app = service(clock=lambda: NOW.astimezone(timezone(timedelta(hours=-6))))
    initial = app.register(ORDER)
    assert app.get(ORDER.id) is initial
    assert initial.order.status is S.REQUESTED
    assert len(initial.events) == 1 and initial.events[0].previous_status is None
    assert initial.events[0].occurred_at == NOW
    assert initial.events[0].occurred_at.tzinfo is timezone.utc
    with pytest.raises(FrozenInstanceError):
        initial.order.status = S.DELIVERED
    with pytest.raises(DuplicateOrder):
        app.register(replace(ORDER, details="Otro contenido"))
    assert app.get(ORDER.id) is initial
    with pytest.raises(OrderNotFound):
        app.get("inexistente")


def test_invalid_registration_never_creates_a_record():
    app = service()
    with pytest.raises(BusinessNotFound):
        app.register(replace(ORDER, business_id="inexistente"))
    with pytest.raises(ValueError, match="origen"):
        app.register(replace(ORDER, origin=Location(1, 1)))
    with pytest.raises(OrderConflict):
        app.register(replace(ORDER, status=S.DELIVERED))
    with pytest.raises(OrderNotFound):
        app.get(ORDER.id)
    naive = service(clock=lambda: datetime(2022, 1, 1))
    with pytest.raises(ValueError, match="zona horaria"):
        naive.register(ORDER)
    with pytest.raises(OrderNotFound):
        naive.get(ORDER.id)


def test_approved_linear_flow_requires_checks_and_rejects_skips_reversals_and_terminal_changes():
    requirements = ControlledRequirements()
    app = service(requirements)
    first = app.register(ORDER)
    with pytest.raises(OrderConflict):
        app.transition(ORDER.id, S.REQUESTED, S.ASSIGNED)
    states = [S.REQUESTED, S.QUOTED, S.CONFIRMED, S.ASSIGNED, S.PICKED_UP, S.DELIVERED]
    for current, target in zip(states, states[1:]):
        updated = app.transition(ORDER.id, current, target)
        count = len(updated.events)
        with pytest.raises(OrderConflict):
            app.transition(ORDER.id, target, target)
        with pytest.raises(OrderConflict):
            app.transition(ORDER.id, target, current)
        assert len(app.get(ORDER.id).events) == count
        if target in (S.ASSIGNED, S.PICKED_UP, S.DELIVERED):
            with pytest.raises(OrderConflict):
                app.transition(ORDER.id, target, S.CANCELLED)
    assert len(updated.events) == 6 and len(first.events) == 1
    assert [target for _, target in requirements.checked] == states[1:]


def test_cancellation_only_before_assignment_and_missing_or_failed_requirements_do_not_advance():
    for cancel_from in (S.REQUESTED, S.QUOTED, S.CONFIRMED):
        app = service(ControlledRequirements())
        app.register(ORDER)
        state = S.REQUESTED
        for target in [S.QUOTED, S.CONFIRMED][:list((S.REQUESTED, S.QUOTED, S.CONFIRMED)).index(cancel_from)]:
            app.transition(ORDER.id, state, target)
            state = target
        cancelled = app.transition(ORDER.id, cancel_from, S.CANCELLED)
        with pytest.raises(OrderConflict):
            app.transition(ORDER.id, S.CANCELLED, S.REQUESTED)
        assert app.get(ORDER.id) is cancelled
    app = service()
    before = app.register(ORDER)
    with pytest.raises(MissingPrerequisite):
        app.transition(ORDER.id, S.REQUESTED, S.QUOTED)
    assert app.get(ORDER.id) is before
    assert app.transition(ORDER.id, S.REQUESTED, S.CANCELLED).order.status is S.CANCELLED

    class RejectRequirements:
        def validate(self, order, target):
            raise MissingPrerequisite("No hay cotización válida")

    rejected = service(RejectRequirements())
    initial = rejected.register(ORDER)
    with pytest.raises(MissingPrerequisite):
        rejected.transition(ORDER.id, S.REQUESTED, S.QUOTED)
    assert rejected.get(ORDER.id) is initial


def test_competing_updates_compare_expected_state_and_append_only_one_event():
    repository = InMemoryOrderRepository()
    businesses = InMemoryBusinesses([BUSINESS])
    OrderService(repository, businesses, clock=lambda: NOW).register(ORDER)
    barrier = Barrier(2)

    def synchronized_clock():
        barrier.wait(timeout=5)
        return NOW

    app = OrderService(repository, businesses, clock=synchronized_clock)

    def cancel():
        try:
            app.transition(ORDER.id, S.REQUESTED, S.CANCELLED)
            return "updated"
        except OrderConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: cancel(), range(2)))
    assert sorted(results) == ["conflict", "updated"]
    assert repository.get(ORDER.id).order.status is S.CANCELLED
    assert len(repository.get(ORDER.id).events) == 2
