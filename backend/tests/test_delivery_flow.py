"""T36: integración de servicios en memoria; todos los datos son fixtures.

No acredita flujo HTTP/cloud, inferencia real ni cotización comercial válida.
"""

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal as D

import pytest

from delivery.adapters.memory import InMemoryBusinesses
from delivery.adapters.memory_cash import InMemoryCashRepository
from delivery.adapters.memory_dispatch import InMemoryDispatchRepository
from delivery.domain.cash import CashStatus as C
from delivery.domain.models import Business, Courier, DeliveryDuration, DurationSource, Location, Order, OrderStatus as S, VehicleType
from delivery.domain.order_lifecycle import MissingPrerequisite
from delivery.domain.pricing import OperatorCosts, PricingPolicy
from delivery.domain.routing import RoutePolicy
from delivery.domain.vehicle_rules import ServiceArea, VehicleLimits, VehiclePolicy
from delivery.services.assignments import AssignmentService, DispatchOrderRequirements
from delivery.services.cash import CashService
from delivery.services.estimates import AcademicQuoteService
from delivery.services.orders import OrderService
from delivery.services.pricing import PricingService
from delivery.services.whatsapp import WhatsAppSimulationService


def test_simulated_request_quote_assignment_delivery_and_cash_flow():
    now = datetime(2022, 1, 1, tzinfo=timezone.utc)
    start = Location(0, 0)
    business = Business("fixture-business", "Negocio de prueba", start)
    order = Order("fixture-order", business.id, start, Location(0, .01), "Solicitud ficticia")
    courier = Courier("fixture-courier", VehicleType.BICYCLE, True, True)
    repository = InMemoryDispatchRepository([courier])

    class FixtureQuotes:
        """Evidencia controlada solo para esta integración; no usar en la API."""
        quote = None

        def get_validated(self, current):
            if self.quote is None or self.quote.order_id != current.id or self.quote.amounts is None:
                raise MissingPrerequisite("Falta cotización fixture")
            return self.quote

        def validate(self, current, target):
            assert target in (S.QUOTED, S.CONFIRMED)
            self.get_validated(current)

        def validate_confirmed(self, current):
            assert current.status is S.CONFIRMED
            self.get_validated(current)

    class FixturePredictor:
        """Doble del puerto predictivo; versión ficticia, sin ejecutar ML."""
        def predict(self, requested_at):
            assert requested_at == now
            return DeliveryDuration(10, DurationSource.PREDICTION, "Duración de fixture", "fixture-model")

    quotes = FixtureQuotes()
    orders = OrderService(repository, InMemoryBusinesses([business]),
                          DispatchOrderRequirements(repository, quotes), lambda: now)
    chat = WhatsAppSimulationService(orders)
    assert chat.request(order).record.order.status is S.REQUESTED
    with pytest.raises(MissingPrerequisite):
        orders.transition(order.id, S.REQUESTED, S.QUOTED)

    estimate = AcademicQuoteService(repository, FixturePredictor()).estimate(order.id, "fixture-quote")
    pricing = PricingPolicy("fixture-pricing", "USD", D(".01"), D(1), D(2), D(".5"), D(".5"))
    breakdown = PricingService(pricing).calculate(estimate, OperatorCosts("USD", D(".1"), D(".2")))
    assert breakdown.academic_only and not breakdown.coverage_validated
    # Inyección explícita de evidencia sintética: el borrador no la autoriza por sí solo.
    quotes.quote = replace(estimate.quote, amounts=breakdown.amounts)
    orders.transition(order.id, S.REQUESTED, S.QUOTED)
    orders.transition(order.id, S.QUOTED, S.CONFIRMED)

    area = ServiceArea("fixture-area", Location(-1, -1), Location(1, 1))
    vehicles = VehiclePolicy("fixture-vehicles", area, VehicleLimits(D(20), D(5)), VehicleLimits(D(30), D(10)))
    assignments = AssignmentService(repository, RoutePolicy("fixture-route", 1, area), vehicles, quotes, lambda: now)
    assignments.assign("fixture-run", courier.id, [order.id], start, {order.id: D(1)})
    assert not repository.get_courier(courier.id).available
    cash = CashService(InMemoryCashRepository(), repository, quotes, lambda: now)
    assert cash.open(order.id).status is C.PENDING
    with pytest.raises(MissingPrerequisite):
        cash.collect(order.id, "USD", breakdown.amounts.delivery_fee)
    orders.transition(order.id, S.ASSIGNED, S.PICKED_UP)
    delivered = orders.transition(order.id, S.PICKED_UP, S.DELIVERED)
    assert cash.collect(order.id, "USD", breakdown.amounts.delivery_fee).status is C.COLLECTED
    remitted = cash.remit(order.id, "USD", breakdown.amounts.delivery_fee)
    assert [event.status for event in remitted.events] == [C.PENDING, C.COLLECTED, C.REMITTED]
    assert remitted.expected_amount == breakdown.amounts.delivery_fee
    assert orders.get(order.id) is delivered  # Contabilidad no modifica logística.
    assert [event.status for event in delivered.events] == [
        S.REQUESTED, S.QUOTED, S.CONFIRMED, S.ASSIGNED, S.PICKED_UP, S.DELIVERED]
    assert all(event.occurred_at == now for event in (*delivered.events, *remitted.events))
    assert chat.conversation(order.id).record is delivered
    assert not assignments.release("fixture-run").active
    assert repository.get_courier(courier.id).available
