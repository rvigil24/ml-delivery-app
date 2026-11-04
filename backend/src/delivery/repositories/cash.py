"""Persistencia de registros de efectivo."""

from dataclasses import replace

from pymongo.errors import DuplicateKeyError

from delivery.database.codec import decode
from delivery.database.documents import cas, document, mongo_errors
from delivery.models.cash import (
    CashConflict,
    CashEvent,
    CashNotFound,
    CashRecord,
    CashStatus,
    validate_cash_transition,
    validate_full_payment,
)


class MongoCashRepository:
    def __init__(self, database):
        self.collection = database.cash

    @mongo_errors
    def get(self, order_id):
        doc = self.collection.find_one({"_id": order_id})
        if doc is None:
            raise CashNotFound(order_id)
        return decode(CashRecord, doc["data"])

    @mongo_errors
    def create(self, record):
        if (
            len(record.events) != 1
            or record.events[0].previous_status is not None
            or record.status is not CashStatus.PENDING
        ):
            raise CashConflict("Se requiere un evento inicial pendiente")
        try:
            self.collection.insert_one(document(record.order_id, record))
        except DuplicateKeyError:
            raise CashConflict("Efectivo duplicado para el pedido") from None
        return record

    @mongo_errors
    def transition(self, order_id, expected, target, currency, amount, occurred_at):
        validate_cash_transition(expected, target)
        before = self.collection.find_one({"_id": order_id})
        if before is None:
            raise CashNotFound(order_id)
        current = decode(CashRecord, before["data"])
        if current.status is not expected:
            raise CashConflict("El estado contable cambió")
        validate_full_payment(current, currency, amount)
        event = CashEvent(expected, target, occurred_at)
        if occurred_at < current.events[-1].occurred_at:
            raise ValueError("Un evento no puede preceder al historial")
        return cas(
            self.collection,
            before,
            replace(current, events=current.events + (event,)),
            CashConflict,
        )
