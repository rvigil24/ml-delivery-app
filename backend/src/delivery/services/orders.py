"""T20: registro, consulta y transiciones de pedidos con requisitos explícitos."""

from datetime import datetime, timezone
from typing import Callable, Optional

from delivery.models.entities import Order, OrderStatus
from delivery.models.order_lifecycle import (
    BusinessNotFound,
    MissingPrerequisite,
    OrderConflict,
    OrderRecord,
    validate_transition,
)
from delivery.repositories.base import (
    BusinessReader,
    OrderRepository,
    TransitionRequirements,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OrderService:
    def __init__(
        self,
        orders: OrderRepository,
        businesses: BusinessReader,
        requirements: Optional[TransitionRequirements] = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._orders = orders
        self._businesses = businesses
        self._requirements = requirements
        self._clock = clock

    def _timestamp(self) -> datetime:
        value = self._clock()
        if (
            not isinstance(value, datetime)
            or value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError("El reloj debe devolver datetime con zona horaria")
        return value.astimezone(timezone.utc)

    def register(self, order: Order) -> OrderRecord:
        if not isinstance(order, Order):
            raise ValueError("order debe ser Order")
        if order.status is not OrderStatus.REQUESTED:
            raise OrderConflict("Un pedido nuevo debe estar solicitado")
        business = self._businesses.get(order.business_id)
        if business is None:
            raise BusinessNotFound(order.business_id)
        if order.origin != business.location:
            raise ValueError("El origen debe coincidir con la ubicación del negocio")
        return self._orders.create(order, self._timestamp())

    def get(self, order_id: str) -> OrderRecord:
        return self._orders.get(order_id)

    def list(self, limit: int = 100):
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        ):
            raise ValueError("limit debe estar entre 1 y 100")
        return self._orders.list(limit)

    def list_for_business(self, business_id: str, limit: int = 100):
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        ):
            raise ValueError("limit debe estar entre 1 y 100")
        if self._businesses.get(business_id) is None:
            raise BusinessNotFound(business_id)
        return self._orders.list_for_business(business_id, limit)

    def transition(
        self, order_id: str, expected: OrderStatus, target: OrderStatus
    ) -> OrderRecord:
        record = self.get(order_id)
        if record.order.status is not expected:
            raise OrderConflict(
                "El estado cambió; consultar el pedido antes de reintentar"
            )
        validate_transition(expected, target)
        if target is not OrderStatus.CANCELLED:
            if self._requirements is None:
                raise MissingPrerequisite(
                    "Falta un validador de cotización/asignación para avanzar"
                )
            self._requirements.validate(record.order, target)
        return self._orders.transition(order_id, expected, target, self._timestamp())
