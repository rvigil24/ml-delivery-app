"""Pedidos: registro, transiciones y concurrencia."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from threading import Barrier

import pytest
from delivery.models import Business, Location, Order
from delivery.models import OrderStatus as S
from delivery.models.order_lifecycle import DuplicateOrder, OrderConflict, OrderNotFound
from delivery.repositories.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.services.orders import OrderService

NOW = datetime(2022, 1, 1, tzinfo=timezone.utc)
BUSINESS = Business("business-fixture", "Negocio de prueba", Location(0, 0))
ORDER = Order(
    "order-fixture", BUSINESS.id, BUSINESS.location, Location(0, 1), "Pedido de prueba"
)


class ControlledRequirements:
    """Autoriza solo dentro de estas pruebas de la máquina de estados."""

    def __init__(self):
        self.checked = []

    def validate(self, order, target):
        self.checked.append((order.id, target))


def service(requirements=None, clock=lambda: NOW):
    return OrderService(
        InMemoryOrderRepository(), InMemoryBusinesses([BUSINESS]), requirements, clock
    )


def test_register_order_preserves_history():
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


def test_order_transitions_require_valid_steps():
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


def test_concurrent_updates_write_one_event():
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
