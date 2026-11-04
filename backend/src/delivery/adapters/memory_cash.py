"""T28: libro de efectivo efímero, con un registro inmutable por pedido."""

from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from threading import Lock

from delivery.domain.cash import (
    CashConflict, CashEvent, CashNotFound, CashRecord, CashStatus,
    validate_cash_transition, validate_full_payment,
)


class InMemoryCashRepository:
    def __init__(self) -> None:
        self._records = {}
        self._lock = Lock()

    def _get(self, order_id: str) -> CashRecord:
        try:
            return self._records[order_id]
        except KeyError:
            raise CashNotFound(order_id) from None

    def get(self, order_id: str) -> CashRecord:
        with self._lock:
            return self._get(order_id)

    def create(self, record: CashRecord) -> CashRecord:
        if len(record.events) != 1 or record.events[0].previous_status is not None or record.status is not CashStatus.PENDING:
            raise CashConflict("Un registro nuevo debe tener solo el evento inicial pendiente")
        with self._lock:
            if record.order_id in self._records:
                raise CashConflict("Ya existe un registro de efectivo para el pedido")
            self._records[record.order_id] = record
            return record

    def transition(self, order_id: str, expected: CashStatus, target: CashStatus,
                   currency: str, amount: Decimal, occurred_at: datetime) -> CashRecord:
        validate_cash_transition(expected, target)
        with self._lock:
            current = self._get(order_id)
            if current.status is not expected:
                raise CashConflict("El estado contable cambió; consultar antes de reintentar")
            validate_full_payment(current, currency, amount)
            event = CashEvent(expected, target, occurred_at)
            if event.occurred_at < current.events[-1].occurred_at:
                raise ValueError("Un evento no puede preceder al último evento de efectivo")
            updated = replace(current, events=current.events + (event,))
            self._records[order_id] = updated
            return updated
