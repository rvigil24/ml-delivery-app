"""T20: flujo de estados aprobado y snapshots inmutables del pedido simulado."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple

from delivery.models.entities import Order, OrderStatus


class OrderNotFound(LookupError):
    pass


class BusinessNotFound(LookupError):
    pass


class OrderConflict(RuntimeError):
    pass


class DuplicateOrder(OrderConflict):
    pass


class MissingPrerequisite(RuntimeError):
    pass


ALLOWED_TRANSITIONS = {
    OrderStatus.REQUESTED: frozenset((OrderStatus.QUOTED, OrderStatus.CANCELLED)),
    OrderStatus.QUOTED: frozenset((OrderStatus.CONFIRMED, OrderStatus.CANCELLED)),
    OrderStatus.CONFIRMED: frozenset((OrderStatus.ASSIGNED, OrderStatus.CANCELLED)),
    OrderStatus.ASSIGNED: frozenset((OrderStatus.PICKED_UP,)),
    OrderStatus.PICKED_UP: frozenset((OrderStatus.DELIVERED,)),
    OrderStatus.DELIVERED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
}


def validate_transition(current: OrderStatus, target: OrderStatus) -> None:
    if not isinstance(current, OrderStatus) or not isinstance(target, OrderStatus):
        raise ValueError("Los estados deben ser OrderStatus")
    if target not in ALLOWED_TRANSITIONS[current]:
        raise OrderConflict(
            f"Transición no permitida: {current.value} -> {target.value}"
        )


@dataclass(frozen=True)
class OrderEvent:
    previous_status: Optional[OrderStatus]
    status: OrderStatus
    occurred_at: datetime

    def __post_init__(self) -> None:
        if (
            not isinstance(self.occurred_at, datetime)
            or self.occurred_at.tzinfo is None
            or self.occurred_at.utcoffset() != timedelta(0)
        ):
            raise ValueError("occurred_at debe ser datetime con zona UTC")
        if self.previous_status is None:
            if self.status is not OrderStatus.REQUESTED:
                raise OrderConflict("El primer evento debe ser solicitado")
        else:
            validate_transition(self.previous_status, self.status)


@dataclass(frozen=True)
class OrderRecord:
    order: Order
    events: Tuple[OrderEvent, ...]
