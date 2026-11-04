"""T27: vista inmutable de mensajes simulados derivados del historial del pedido."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Tuple

from delivery.models.order_lifecycle import OrderRecord


class MessageSender(str, Enum):
    CLIENT = "cliente"
    SYSTEM = "sistema"


@dataclass(frozen=True)
class SimulatedMessage:
    sender: MessageSender
    text: str
    occurred_at: datetime


@dataclass(frozen=True)
class SimulatedConversation:
    record: OrderRecord
    messages: Tuple[SimulatedMessage, ...]
    channel: str = field(default="whatsapp_simulado", init=False)
    simulated: bool = field(default=True, init=False)
    reconstructed: bool = field(default=True, init=False)


def conversation_from_record(record: OrderRecord) -> SimulatedConversation:
    created_at = record.events[0].occurred_at
    messages = (
        SimulatedMessage(MessageSender.CLIENT, record.order.details, created_at),
        SimulatedMessage(
            MessageSender.SYSTEM,
            "Solicitud registrada. Estado: solicitado. Cotización y cobertura pendientes de validación.",
            created_at,
        ),
    ) + tuple(
        SimulatedMessage(
            MessageSender.SYSTEM,
            f"Estado registrado: {event.status.value}.",
            event.occurred_at,
        )
        for event in record.events[1:]
    )
    return SimulatedConversation(record, messages)
