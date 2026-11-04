"""T27: mensajes/pedidos sintéticos; no comunicaciones o cotizaciones reales."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.domain.messages import MessageSender, conversation_from_record
from delivery.domain.models import Business, Location, Order, OrderStatus as S
from delivery.domain.order_lifecycle import (
    BusinessNotFound, DuplicateOrder, MissingPrerequisite, OrderConflict, OrderEvent, OrderNotFound, OrderRecord,
)
from delivery.services.orders import OrderService
from delivery.services.whatsapp import WhatsAppSimulationService


NOW = datetime(2022, 1, 1, tzinfo=timezone.utc)
BUSINESS = Business("fixture-business", "Negocio de prueba", Location(0, 0))
ORDER = Order("fixture-order", BUSINESS.id, BUSINESS.location, Location(0, .01), "Solicitud de prueba")


def setup(clock=lambda: NOW):
    repository = InMemoryOrderRepository()
    orders = OrderService(repository, InMemoryBusinesses([BUSINESS]), clock=clock)
    return orders, WhatsAppSimulationService(orders)


def test_request_registers_validated_order_and_returns_identified_immutable_messages():
    orders, chat = setup(lambda: NOW.astimezone(timezone(timedelta(hours=-6))))
    result = chat.request(ORDER)
    assert result.record is orders.get(ORDER.id)
    assert result.record.order.status is S.REQUESTED
    assert result.channel == "whatsapp_simulado" and result.simulated and result.reconstructed
    assert len(result.messages) == 2
    assert result.messages[0].sender is MessageSender.CLIENT
    assert result.messages[0].text == ORDER.details
    assert result.messages[1].sender is MessageSender.SYSTEM
    assert "Cotización y cobertura pendientes" in result.messages[1].text
    assert all(message.occurred_at == NOW and message.occurred_at.tzinfo is timezone.utc for message in result.messages)
    with pytest.raises(FrozenInstanceError):
        result.messages[0].text = "Cambio"


def test_rejected_requests_and_duplicate_ids_do_not_create_false_acknowledgements():
    orders, chat = setup()
    for invalid, error in ((replace(ORDER, business_id="missing"), BusinessNotFound),
                           (replace(ORDER, origin=Location(1, 1)), ValueError),
                           (replace(ORDER, status=S.DELIVERED), OrderConflict)):
        with pytest.raises(error):
            chat.request(invalid)
        with pytest.raises(OrderNotFound):
            chat.conversation(ORDER.id)
    original = chat.request(ORDER)
    with pytest.raises(DuplicateOrder):
        chat.request(replace(ORDER, details="Otro mensaje"))
    assert chat.conversation(ORDER.id) == original and orders.get(ORDER.id) is original.record


def test_consultation_reflects_committed_cancellation_without_appending_events_or_messages():
    times = iter((NOW, NOW + timedelta(minutes=1)))
    orders, chat = setup(lambda: next(times))
    original = chat.request(ORDER)
    cancelled = orders.transition(ORDER.id, S.REQUESTED, S.CANCELLED)
    result = chat.conversation(ORDER.id)
    assert result.record is cancelled and len(result.messages) == 3
    assert result.messages[-1].text == "Estado registrado: cancelado."
    assert result.messages[-1].occurred_at == cancelled.events[-1].occurred_at
    assert chat.conversation(ORDER.id) == result
    assert len(original.messages) == 2 and len(orders.get(ORDER.id).events) == 2
    with pytest.raises(OrderNotFound):
        chat.conversation("missing")


def test_chat_does_not_bypass_missing_quotation_requirements_or_report_rejected_changes():
    orders, chat = setup()
    before = chat.request(ORDER)
    with pytest.raises(MissingPrerequisite):
        orders.transition(ORDER.id, S.REQUESTED, S.QUOTED)
    with pytest.raises(OrderConflict):
        orders.transition(ORDER.id, S.REQUESTED, S.DELIVERED)
    assert chat.conversation(ORDER.id) == before and orders.get(ORDER.id) is before.record


def test_projection_uses_each_recorded_event_in_order_without_inventing_extra_client_messages():
    # Historial construido únicamente como fixture para probar la representación.
    states = (S.REQUESTED, S.QUOTED, S.CONFIRMED, S.ASSIGNED, S.PICKED_UP, S.DELIVERED)
    events = tuple(OrderEvent(states[index - 1] if index else None, status,
                             NOW + timedelta(minutes=index)) for index, status in enumerate(states))
    record = OrderRecord(replace(ORDER, status=S.DELIVERED), events)
    result = conversation_from_record(record)
    assert len(result.messages) == len(events) + 1
    assert [message.text for message in result.messages[2:]] == [
        f"Estado registrado: {status.value}." for status in states[1:]]
    assert [message.occurred_at for message in result.messages[1:]] == [event.occurred_at for event in events]
    assert sum(message.sender is MessageSender.CLIENT for message in result.messages) == 1
    assert result.record is record
