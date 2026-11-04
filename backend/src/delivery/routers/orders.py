"""Creación, consulta y transiciones de pedidos."""

from typing import Optional, Tuple

from fastapi import APIRouter, Query, Request

from delivery.dependencies import service
from delivery.models.entities import Location, Order
from delivery.models.order_lifecycle import OrderRecord
from delivery.schemas.requests import OrderInput, TransitionInput
from delivery.schemas.responses import ErrorResponse
from delivery.validation import valid


def orders_router():
    router = APIRouter(
        responses={
            status: {"model": ErrorResponse} for status in (404, 409, 422, 503, 500)
        }
    )

    @router.post(
        "/orders",
        response_model=OrderRecord,
        status_code=201,
        tags=["Pedidos"],
        summary="Crear un pedido",
        description="Registra un pedido con negocio, origen, destino y detalle de la entrega.",
    )
    def create_order(body: OrderInput, request: Request):
        return valid(
            lambda: service(request, "order_service").register(
                Order(
                    body.id,
                    body.business_id,
                    Location(**body.origin.model_dump()),
                    Location(**body.destination.model_dump()),
                    body.details,
                )
            )
        )

    @router.get(
        "/orders",
        response_model=Tuple[OrderRecord, ...],
        tags=["Pedidos"],
        summary="Listar pedidos",
        description="Devuelve los pedidos registrados y su estado actual.",
    )
    def list_orders(
        request: Request,
        limit: int = Query(100, ge=1, le=100),
        business_id: Optional[str] = Query(
            None, min_length=1, description="Filtrar los pedidos de un negocio."
        ),
    ):
        orders = service(request, "order_service")
        return (
            orders.list_for_business(business_id, limit)
            if business_id is not None
            else orders.list(limit)
        )

    @router.get(
        "/orders/{order_id}",
        response_model=OrderRecord,
        tags=["Pedidos"],
        summary="Consultar un pedido",
        description="Devuelve los datos del pedido y el historial de sus estados.",
    )
    def get_order(order_id: str, request: Request):
        return service(request, "order_service").get(order_id)

    @router.post(
        "/orders/{order_id}/transitions",
        response_model=OrderRecord,
        tags=["Pedidos"],
        summary="Cambiar el estado de un pedido",
        description="Actualiza el estado cuando se cumplen los requisitos del paso solicitado.",
    )
    def transition(order_id: str, body: TransitionInput, request: Request):
        return service(request, "order_service").transition(
            order_id, body.expected, body.target
        )

    return router
