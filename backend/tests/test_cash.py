"""T28: efectivo/cotizaciones sintéticos, exclusivamente fixtures de simulación."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
from threading import Barrier

import pytest

from delivery.adapters.memory import InMemoryBusinesses
from delivery.adapters.memory_cash import InMemoryCashRepository
from delivery.adapters.memory_dispatch import InMemoryDispatchRepository
from delivery.domain.cash import CashConflict, CashEvent, CashNotFound, CashStatus as C
from delivery.domain.models import Business, Courier, Location, Order, OrderStatus as S, Quote, QuoteAmounts, VehicleType
from delivery.domain.order_lifecycle import MissingPrerequisite, OrderNotFound
from delivery.domain.routing import RoutePolicy
from delivery.domain.vehicle_rules import ServiceArea, VehicleLimits, VehiclePolicy
from delivery.services.assignments import AssignmentService, DispatchOrderRequirements
from delivery.services.cash import CashService
from delivery.services.orders import OrderService


NOW = datetime(2022, 1, 1, tzinfo=timezone.utc)
START = Location(0, 0)
BUSINESS = Business("fixture-business", "Negocio de prueba", START)
ORDER = Order("fixture-order", BUSINESS.id, START, Location(0, .01), "Pedido de prueba")
COURIER = Courier("fixture-courier", VehicleType.BICYCLE, True, True)
AREA = ServiceArea("fixture-area", Location(-1, -1), Location(1, 1))
ROUTES = RoutePolicy("fixture-route", 1, AREA)
VEHICLES = VehiclePolicy("fixture-vehicle", AREA, VehicleLimits(D(20), D(5)), VehicleLimits(D(30), D(10)))
# No son tarifas/costos reales. Solo el delivery_fee se registra como efectivo.
QUOTE = Quote("fixture-quote", ORDER.id, 1, "fixture-distance", amounts=
              QuoteAmounts("USD", D("2.50"), D("1.00"), D("0.10"), D("0.20"), D("1.20")))


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
    orders = OrderService(repository, InMemoryBusinesses([BUSINESS]),
                          DispatchOrderRequirements(repository, quotes), lambda: NOW)
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


def test_cash_cycle_keeps_fixed_quote_terms_utc_history_and_logistics_unchanged():
    repository, orders, ledger, quotes, _, assignments = setup()
    cash = CashService(ledger, repository, quotes,
                       lambda: NOW.astimezone(timezone(timedelta(hours=-6))))
    initial = cash.open(ORDER.id)
    assert initial.simulated and initial.status is C.PENDING
    assert (initial.quote_id, initial.currency, initial.expected_amount) == (QUOTE.id, "USD", D("2.50"))
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
    assert [event.status for event in remitted.events] == [C.PENDING, C.COLLECTED, C.REMITTED]
    assert all(event.occurred_at == NOW and event.occurred_at.tzinfo is timezone.utc for event in remitted.events)
    assert orders.get(ORDER.id) is before and not repository.get_courier(COURIER.id).available
    with pytest.raises(FrozenInstanceError):
        remitted.events[-1].status = C.PENDING


def test_open_requires_valid_quote_of_same_order_and_never_overwrites_existing_cash():
    repository, orders, ledger, quotes, cash, _ = setup()
    with pytest.raises(MissingPrerequisite):
        CashService(ledger, repository).open(ORDER.id)
    for invalid in (None, replace(QUOTE, order_id="other"), replace(QUOTE, amounts=None)):
        quotes.quote = invalid
        with pytest.raises(MissingPrerequisite):
            cash.open(ORDER.id)
        with pytest.raises(CashNotFound):
            cash.get(ORDER.id)

    class RejectedQuote:
        def get_validated(self, order):
            raise MissingPrerequisite("Cotización no validada")

    with pytest.raises(MissingPrerequisite, match="no validada"):
        CashService(ledger, repository, RejectedQuote()).open(ORDER.id)
    quotes.quote = QUOTE
    initial = cash.open(ORDER.id)
    with pytest.raises(CashConflict):
        cash.open(ORDER.id)
    assert cash.get(ORDER.id) is initial
    with pytest.raises(OrderNotFound):
        cash.open("missing")
    orders.transition(ORDER.id, S.CONFIRMED, S.CANCELLED)
    with pytest.raises(MissingPrerequisite):
        cash.collect(ORDER.id, "USD", D("2.50"))
    with pytest.raises(CashConflict, match="cancelado"):
        cash.open(ORDER.id)
    assert cash.get(ORDER.id) is initial


def test_partial_excess_wrong_currency_and_invalid_amounts_fail_without_writes():
    _, orders, _, _, cash, assignments = setup()
    initial = cash.open(ORDER.id)
    deliver(orders, assignments)
    for amount, currency in ((D(1), "USD"), (D(3), "USD"), (D("2.50"), "EUR"),
                             (D("NaN"), "USD"), (D("Infinity"), "USD"), (D(-1), "USD"),
                             (2.5, "USD"), (True, "USD")):
        with pytest.raises(ValueError):
            cash.collect(ORDER.id, currency, amount)
        assert cash.get(ORDER.id) is initial
    collected = cash.collect(ORDER.id, "USD", D("2.50"))
    with pytest.raises(ValueError):
        cash.remit(ORDER.id, "USD", D("1.50"))  # No automatic courier deduction.
    assert cash.get(ORDER.id) is collected


def test_skips_repeats_reversals_and_retroactive_events_are_rejected():
    repository, orders, ledger, quotes, cash, assignments = setup()
    cash.open(ORDER.id)
    deliver(orders, assignments)
    with pytest.raises(CashConflict):
        cash.remit(ORDER.id, "USD", D("2.50"))
    for value in (NOW.replace(tzinfo=None), NOW - timedelta(seconds=1)):
        with pytest.raises(ValueError):
            CashService(ledger, repository, quotes, lambda: value).collect(ORDER.id, "USD", D("2.50"))
    later = CashService(ledger, repository, quotes, lambda: NOW + timedelta(minutes=1))
    collected = later.collect(ORDER.id, "USD", D("2.50"))
    with pytest.raises(CashConflict):
        cash.collect(ORDER.id, "USD", D("2.50"))
    with pytest.raises(ValueError, match="último evento"):
        cash.remit(ORDER.id, "USD", D("2.50"))
    assert cash.get(ORDER.id) is collected
    remitted = later.remit(ORDER.id, "USD", D("2.50"))
    with pytest.raises(CashConflict):
        later.remit(ORDER.id, "USD", D("2.50"))
    with pytest.raises(CashConflict):
        ledger.transition(ORDER.id, C.REMITTED, C.PENDING, "USD", D("2.50"), NOW)
    with pytest.raises(CashConflict):
        CashEvent(None, C.COLLECTED, NOW)
    assert cash.get(ORDER.id) is remitted


def test_competing_opens_and_collections_add_only_one_event_each():
    repository, orders, ledger, quotes, cash, assignments = setup()
    deliver(orders, assignments)
    for action in ("open", "collect"):
        barrier = Barrier(2)

        def synchronized_clock():
            barrier.wait(timeout=5)
            return NOW

        racing = CashService(ledger, repository, quotes, synchronized_clock)

        def attempt(_):
            try:
                if action == "open":
                    racing.open(ORDER.id)
                else:
                    racing.collect(ORDER.id, "USD", D("2.50"))
                return "updated"
            except CashConflict:
                return "conflict"

        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(attempt, range(2))) == ["conflict", "updated"]
    assert cash.get(ORDER.id).status is C.COLLECTED and len(cash.get(ORDER.id).events) == 2


def test_explicit_zero_fee_is_not_a_missing_value_or_an_invented_default():
    _, orders, _, quotes, cash, assignments = setup()
    quotes.quote = replace(QUOTE, amounts=replace(QUOTE.amounts, delivery_fee=D(0)))
    initial = cash.open(ORDER.id)
    assert initial.expected_amount == 0
    deliver(orders, assignments)
    cash.collect(ORDER.id, "USD", D(0))
    assert cash.remit(ORDER.id, "USD", D(0)).status is C.REMITTED
