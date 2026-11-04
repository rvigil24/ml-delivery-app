"""T28: estados de efectivo ficticio, independientes del estado logístico."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, Tuple

from delivery.models.entities import Quote
from delivery.models.order_lifecycle import MissingPrerequisite


class CashConflict(RuntimeError):
    pass


class CashNotFound(LookupError):
    pass


class CashStatus(str, Enum):
    PENDING = "pendiente"
    COLLECTED = "cobrado"
    REMITTED = "entregado_al_operador"


def validate_cash_transition(current: CashStatus, target: CashStatus) -> None:
    if not isinstance(current, CashStatus) or not isinstance(target, CashStatus):
        raise ValueError("Los estados deben ser CashStatus")
    if (current, target) not in (
        (CashStatus.PENDING, CashStatus.COLLECTED),
        (CashStatus.COLLECTED, CashStatus.REMITTED),
    ):
        raise CashConflict("Transición contable no permitida")


@dataclass(frozen=True)
class CashEvent:
    previous_status: Optional[CashStatus]
    status: CashStatus
    occurred_at: datetime

    def __post_init__(self) -> None:
        if (
            not isinstance(self.occurred_at, datetime)
            or self.occurred_at.tzinfo is None
            or self.occurred_at.utcoffset() != timedelta(0)
        ):
            raise ValueError("occurred_at debe ser datetime con zona UTC")
        if self.previous_status is None:
            if self.status is not CashStatus.PENDING:
                raise CashConflict("El primer evento debe ser pendiente")
        else:
            validate_cash_transition(self.previous_status, self.status)


@dataclass(frozen=True)
class CashRecord:
    order_id: str
    quote_id: str
    currency: str
    expected_amount: Decimal
    events: Tuple[CashEvent, ...]
    simulated: bool = field(default=True, init=False)

    @property
    def status(self) -> CashStatus:
        return self.events[-1].status


def pending_cash(quote: Quote, occurred_at: datetime) -> CashRecord:
    if not isinstance(quote, Quote) or quote.amounts is None:
        raise MissingPrerequisite("Falta cotización validada con importes")
    return CashRecord(
        quote.order_id,
        quote.id,
        quote.amounts.currency,
        quote.amounts.delivery_fee,
        (CashEvent(None, CashStatus.PENDING, occurred_at),),
    )


def validate_full_payment(record: CashRecord, currency: str, amount: Decimal) -> None:
    if not isinstance(amount, Decimal) or not amount.is_finite() or amount < 0:
        raise ValueError("amount debe ser Decimal finito no negativo")
    if currency != record.currency or amount != record.expected_amount:
        raise ValueError(
            "Se requiere la moneda y el importe completo de la cotización guardada"
        )
