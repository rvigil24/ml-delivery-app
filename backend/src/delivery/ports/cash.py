"""T28: evidencia de cotización y actualizaciones condicionales del efectivo."""

from datetime import datetime
from decimal import Decimal
from typing import Protocol

from delivery.domain.cash import CashRecord, CashStatus
from delivery.domain.models import Order, Quote


class CashQuoteSource(Protocol):
    def get_validated(self, order: Order) -> Quote:
        """Consultar fuente autoritativa; rechazar cotizaciones no validadas o ausentes."""
        ...


class CashRepository(Protocol):
    def get(self, order_id: str) -> CashRecord: ...

    def create(self, record: CashRecord) -> CashRecord:
        """Crear expectativa pendiente una sola vez, sin sobrescribir por pedido."""
        ...

    def transition(self, order_id: str, expected: CashStatus, target: CashStatus,
                   currency: str, amount: Decimal, occurred_at: datetime) -> CashRecord:
        """Comparar estado, validar pago/fecha y añadir evento atómicamente."""
        ...
