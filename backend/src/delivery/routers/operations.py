"""Consulta operativa sin modificar pedidos ni inventar importes."""

from typing import Optional, Tuple

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from delivery.dependencies import service
from delivery.models.cash import CashNotFound, CashRecord
from delivery.models.order_lifecycle import OrderRecord


class OperationRow(BaseModel):
    record: OrderRecord
    cash: Optional[CashRecord]


def operations_router():
    router = APIRouter(tags=["Operaciones"])

    @router.get(
        "/operations/orders",
        response_model=Tuple[OperationRow, ...],
        summary="Consultar pedidos y efectivo",
        description="Reúne cada pedido y su registro de efectivo, si existe. No duplica cobros como ingresos.",
    )
    def listing(request: Request, limit: int = Query(100, ge=1, le=100)):
        storage = service(request, "mongo_storage")
        rows = []
        for record in storage.orders.list(limit):
            try:
                cash = storage.cash.get(record.order.id)
            except CashNotFound:
                cash = None
            rows.append(OperationRow(record=record, cash=cash))
        return tuple(rows)

    return router
