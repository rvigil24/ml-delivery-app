"""T20: almacenamiento efímero local; no sustituye MongoDB en T32."""

from dataclasses import replace
from datetime import datetime
from threading import RLock
from typing import Iterable, Optional

from delivery.domain.models import Business, Order, OrderStatus
from delivery.domain.order_lifecycle import (
    DuplicateOrder, OrderConflict, OrderEvent, OrderNotFound, OrderRecord, validate_transition,
)


class InMemoryBusinesses:
    """Catálogo suministrado por quien compone el servicio; sin datos prefijados."""

    def __init__(self, businesses: Iterable[Business] = ()) -> None:
        self._businesses = {}
        for business in businesses:
            if not isinstance(business, Business) or business.id in self._businesses:
                raise ValueError("Catálogo debe contener Business con IDs únicos")
            self._businesses[business.id] = business

    def get(self, business_id: str) -> Optional[Business]:
        return self._businesses.get(business_id)


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._records = {}
        self._lock = RLock()

    def get(self, order_id: str) -> OrderRecord:
        with self._lock:
            return self._get(order_id)

    def list(self, limit: int):
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit fuera de rango")
        with self._lock:
            return tuple(self._records[key] for key in sorted(self._records)[:limit])

    def _get(self, order_id: str) -> OrderRecord:
        try:
            return self._records[order_id]
        except KeyError:
            raise OrderNotFound(order_id) from None

    def list_for_business(self, business_id: str, limit: int):
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit fuera de rango")
        with self._lock:
            return tuple(self._records[key] for key in sorted(self._records)
                         if self._records[key].order.business_id == business_id)[:limit]

    def create(self, order: Order, occurred_at: datetime) -> OrderRecord:
        if order.status is not OrderStatus.REQUESTED:
            raise OrderConflict("Un pedido nuevo debe estar solicitado")
        record = OrderRecord(order, (OrderEvent(None, order.status, occurred_at),))
        with self._lock:
            if order.id in self._records:
                raise DuplicateOrder(order.id)
            self._records[order.id] = record
        return record

    def transition(self, order_id: str, expected: OrderStatus, target: OrderStatus,
                   occurred_at: datetime) -> OrderRecord:
        validate_transition(expected, target)
        with self._lock:
            record = self._get(order_id)
            if record.order.status is not expected:
                raise OrderConflict("El estado cambió; consultar el pedido antes de reintentar")
            event = OrderEvent(expected, target, occurred_at)
            if event.occurred_at < record.events[-1].occurred_at:
                raise ValueError("Un evento no puede preceder al último evento registrado")
            updated = OrderRecord(replace(record.order, status=target), record.events + (event,))
            self._records[order_id] = updated
            return updated
