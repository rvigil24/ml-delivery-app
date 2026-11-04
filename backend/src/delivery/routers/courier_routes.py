"""Rutas del repartidor; los cambios se validan y persisten en servicios existentes."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, Tuple

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from delivery.dependencies import service
from delivery.models.entities import Location, OrderStatus
from delivery.models.order_lifecycle import OrderRecord
from delivery.models.routing import RouteStop
from delivery.schemas.requests import Input
from delivery.schemas.responses import ErrorResponse
from delivery.validation import valid


class CourierRouteResponse(BaseModel):
    id: str
    courier_id: str
    active: bool
    start: Location
    stops: Tuple[RouteStop, ...]
    total_distance_km: Decimal
    created_at: datetime
    released_at: Optional[datetime]
    orders: Tuple[OrderRecord, ...]
    simulated: Literal[True]
    road_route_validated: Literal[False]


class ProgressInput(Input):
    order_id: str = Field(min_length=1)
    expected: OrderStatus
    target: OrderStatus


def courier_routes_router():
    router = APIRouter(
        tags=["Repartidores"],
        responses={
            status: {"model": ErrorResponse} for status in (404, 409, 422, 503, 500)
        },
    )

    @router.get(
        "/couriers/{courier_id}/assignments",
        response_model=Tuple[CourierRouteResponse, ...],
        summary="Consultar las rutas de un repartidor",
        description="Devuelve sus asignaciones, paradas y estados actuales de los pedidos.",
    )
    def listing(
        courier_id: str, request: Request, limit: int = Query(100, ge=1, le=100)
    ):
        return service(request, "courier_routes").list(courier_id, limit)

    @router.post(
        "/couriers/{courier_id}/assignments/{assignment_id}/progress",
        response_model=CourierRouteResponse,
        summary="Registrar una recogida o entrega",
        description="Avanza la siguiente parada de la ruta si coincide con el estado esperado del pedido.",
    )
    def progress(
        courier_id: str, assignment_id: str, body: ProgressInput, request: Request
    ):
        return valid(
            lambda: service(request, "courier_routes").progress(
                courier_id, assignment_id, body.order_id, body.expected, body.target
            )
        )

    @router.post(
        "/couriers/{courier_id}/assignments/{assignment_id}/complete",
        response_model=CourierRouteResponse,
        summary="Finalizar una ruta entregada",
        description="Cierra la asignación y libera al repartidor cuando todos los pedidos están entregados.",
    )
    def complete(courier_id: str, assignment_id: str, request: Request):
        return valid(
            lambda: service(request, "courier_routes").complete(
                courier_id, assignment_id
            )
        )

    return router
