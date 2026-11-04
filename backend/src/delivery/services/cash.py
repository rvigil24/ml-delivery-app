"""T28: cobro y entrega ficticios del importe del envío, sin movimiento de dinero."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable, Optional

from delivery.domain.cash import CashConflict, CashRecord, CashStatus, pending_cash
from delivery.domain.models import OrderStatus, Quote
from delivery.domain.order_lifecycle import MissingPrerequisite, OrderRecord
from delivery.ports.cash import CashQuoteSource, CashRepository
from delivery.ports.orders import OrderRepository
from .orders import utc_now


class CashService:
    def __init__(self, repository: CashRepository, orders: OrderRepository,
                 quotes: Optional[CashQuoteSource] = None, clock: Callable[[], datetime] = utc_now) -> None:
        self._repository = repository
        self._orders = orders
        self._quotes = quotes
        self._clock = clock

    def _timestamp(self, record: OrderRecord) -> datetime:
        value = self._clock()
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("El reloj debe devolver datetime con zona horaria")
        value = value.astimezone(timezone.utc)
        if value < record.events[-1].occurred_at:
            raise ValueError("El evento de efectivo no puede preceder al historial logístico")
        return value

    def open(self, order_id: str) -> CashRecord:
        if self._quotes is None:
            raise MissingPrerequisite("Falta fuente autoritativa de cotización validada")
        record = self._orders.get(order_id)
        if record.order.status is OrderStatus.CANCELLED:
            raise CashConflict("No se abre efectivo para un pedido cancelado")
        quote = self._quotes.get_validated(record.order)
        if not isinstance(quote, Quote) or quote.order_id != order_id:
            raise MissingPrerequisite("La fuente debe devolver una cotización del mismo pedido")
        return self._repository.create(pending_cash(quote, self._timestamp(record)))

    def get(self, order_id: str) -> CashRecord:
        return self._repository.get(order_id)

    def _advance(self, order_id: str, expected: CashStatus, target: CashStatus,
                 currency: str, amount: Decimal) -> CashRecord:
        record = self._orders.get(order_id)
        if record.order.status is not OrderStatus.DELIVERED:
            raise MissingPrerequisite("Solo se registra cobro/entrega de efectivo tras entregar el pedido")
        return self._repository.transition(order_id, expected, target, currency, amount, self._timestamp(record))

    def collect(self, order_id: str, currency: str, amount: Decimal) -> CashRecord:
        return self._advance(order_id, CashStatus.PENDING, CashStatus.COLLECTED, currency, amount)

    def remit(self, order_id: str, currency: str, amount: Decimal) -> CashRecord:
        return self._advance(order_id, CashStatus.COLLECTED, CashStatus.REMITTED, currency, amount)
