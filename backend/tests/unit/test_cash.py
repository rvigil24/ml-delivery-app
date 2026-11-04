"""Ciclo de efectivo simulado con importes de prueba."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

import pytest
from delivery.models.cash import CashStatus as C
from delivery.models.entities import (
    Business,
    Courier,
    Location,
    Order,
    Quote,
    QuoteAmounts,
    VehicleType,
)
from delivery.models.entities import OrderStatus as S
from delivery.models.order_lifecycle import MissingPrerequisite
from delivery.models.routing import RoutePolicy
from delivery.models.vehicle_rules import ServiceArea, VehicleLimits, VehiclePolicy
from delivery.repositories.memory import InMemoryBusinesses
from delivery.repositories.memory_cash import InMemoryCashRepository
from delivery.repositories.memory_dispatch import InMemoryDispatchRepository
from delivery.services.assignments import AssignmentService, DispatchOrderRequirements
from delivery.services.cash import CashService
from delivery.services.orders import OrderService

NOW = datetime(2022, 1, 1, tzinfo=timezone.utc)
START = Location(0, 0)
BUSINESS = Business("fixture-business", "Negocio de prueba", START)
ORDER = Order(
    "fixture-order", BUSINESS.id, START, Location(0, 0.01), "Pedido de prueba"
)
COURIER = Courier("fixture-courier", VehicleType.BICYCLE, True, True)
AREA = ServiceArea("fixture-area", Location(-1, -1), Location(1, 1))
ROUTES = RoutePolicy("fixture-route", 1, AREA)
VEHICLES = VehiclePolicy(
    "fixture-vehicle", AREA, VehicleLimits(D(20), D(5)), VehicleLimits(D(30), D(10))
)
# No son tarifas/costos reales. Solo el delivery_fee se registra como efectivo.
QUOTE = Quote(
    "fixture-quote",
    ORDER.id,
    1,
    "fixture-distance",
    amounts=QuoteAmounts("USD", D("2.50"), D("1.00"), D("0.10"), D("0.20"), D("1.20")),
)


class FixtureQuotes:
    """Doble de evidencia explícito; no usar como validador comercial."""

    def __init__(self, quote=QUOTE):
        self.quote = quote

    def validate(self, order, target):
        assert target in (S.QUOTED, S.CONFIRMED)

    def validate_confirmed(self, order):
        assert order.status is S.CONFIRMED

    def get_validated(self, order):
        return self.quote


def setup():
    repository = InMemoryDispatchRepository([COURIER])
    quotes = FixtureQuotes()
    orders = OrderService(
        repository,
        InMemoryBusinesses([BUSINESS]),
        DispatchOrderRequirements(repository, quotes),
        lambda: NOW,
    )
    orders.register(ORDER)
    orders.transition(ORDER.id, S.REQUESTED, S.QUOTED)
    orders.transition(ORDER.id, S.QUOTED, S.CONFIRMED)
    ledger = InMemoryCashRepository()
    cash = CashService(ledger, repository, quotes, lambda: NOW)
    assignments = AssignmentService(repository, ROUTES, VEHICLES, quotes, lambda: NOW)
    return repository, orders, ledger, quotes, cash, assignments


def deliver(orders, assignments):
    assignments.assign("fixture-run", COURIER.id, [ORDER.id], START, {ORDER.id: D(1)})
    orders.transition(ORDER.id, S.ASSIGNED, S.PICKED_UP)
    orders.transition(ORDER.id, S.PICKED_UP, S.DELIVERED)


def test_cash_lifecycle():
    repository, orders, ledger, quotes, _, assignments = setup()
    cash = CashService(
        ledger,
        repository,
        quotes,
        lambda: NOW.astimezone(timezone(timedelta(hours=-6))),
    )
    initial = cash.open(ORDER.id)
    assert initial.simulated and initial.status is C.PENDING
    assert (initial.quote_id, initial.currency, initial.expected_amount) == (
        QUOTE.id,
        "USD",
        D("2.50"),
    )
    with pytest.raises(MissingPrerequisite):
        cash.collect(ORDER.id, "USD", D("2.50"))
    deliver(orders, assignments)
    before = orders.get(ORDER.id)
    assert cash.get(ORDER.id) is initial  # Delivery does not imply collection.
    collected = cash.collect(ORDER.id, "USD", D("2.50"))
    assert collected.status is C.COLLECTED and initial.status is C.PENDING
    # A later source change cannot silently replace the agreed cash expectation.
    quotes.quote = replace(QUOTE, amounts=replace(QUOTE.amounts, delivery_fee=D(100)))
    remitted = cash.remit(ORDER.id, "USD", D("2.50"))
    assert remitted.status is C.REMITTED and remitted.expected_amount == D("2.50")
    assert [event.status for event in remitted.events] == [
        C.PENDING,
        C.COLLECTED,
        C.REMITTED,
    ]
    assert all(
        event.occurred_at == NOW and event.occurred_at.tzinfo is timezone.utc
        for event in remitted.events
    )
    assert (
        orders.get(ORDER.id) is before
        and not repository.get_courier(COURIER.id).available
    )
    with pytest.raises(FrozenInstanceError):
        remitted.events[-1].status = C.PENDING
