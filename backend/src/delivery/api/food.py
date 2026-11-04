"""Catálogo de comida y registro de solicitudes sin inventar disponibilidad."""

from typing import Literal, Optional, Tuple

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from delivery.domain.models import Business, Location
from delivery.domain.order_lifecycle import OrderRecord

from .dependencies import service
from .request_models import Input, LocationInput
from .response_models import ErrorResponse
from .validation import valid


class FoodItemInput(Input):
    product_id: str = Field(min_length=1)
    quantity: int = Field(gt=0, strict=True)


class FoodOrderInput(Input):
    id: str = Field(pattern=r"^demo-chat-.+", min_length=1)
    business_id: str = Field(min_length=1)
    destination: LocationInput
    delivery_address: str = Field(min_length=1)
    items: Tuple[FoodItemInput, ...] = Field(min_length=1)
    notes: str = ""


class ProductResponse(BaseModel):
    id: str
    business_id: str
    name: str
    description: str
    price: Optional[str] = None
    currency: Optional[str] = None


class NearbyBusinessResponse(BaseModel):
    business: Business
    distance_km: float


class NearbyResponse(BaseModel):
    businesses: Tuple[NearbyBusinessResponse, ...]
    distance_method: Literal["straight_line"]
    coverage_validated: Literal[False]


class MenuResponse(BaseModel):
    business: Business
    products: Tuple[ProductResponse, ...]
    simulated: Literal[True]
    catalog_version: str
    prices_configured: Literal[False]


def food_router():
    router = APIRouter(
        tags=["Negocios"],
        responses={
            status: {"model": ErrorResponse} for status in (404, 409, 422, 503, 500)
        },
    )

    @router.post(
        "/food/orders",
        response_model=OrderRecord,
        tags=["Pedidos"],
        summary="Registrar un pedido del menú",
        description="Valida los productos y guarda la solicitud con dirección y cantidades. Repetir la misma referencia y contenido devuelve el pedido existente.",
    )
    def register(body: FoodOrderInput, request: Request):
        return valid(
            lambda: service(request, "food_catalog").register(
                service(request, "order_service"),
                body.id,
                body.business_id,
                Location(**body.destination.model_dump()),
                body.delivery_address,
                tuple((item.product_id, item.quantity) for item in body.items),
                body.notes,
            )
        )

    @router.get(
        "/businesses/nearby",
        response_model=NearbyResponse,
        summary="Buscar negocios por cercanía",
        description="Ordena los negocios con menú por distancia aproximada al punto de entrega. No confirma cobertura ni disponibilidad.",
    )
    def nearby(
        request: Request,
        latitude: float = Query(ge=-90, le=90, allow_inf_nan=False),
        longitude: float = Query(ge=-180, le=180, allow_inf_nan=False),
        limit: int = Query(20, ge=1, le=100),
    ):
        return valid(
            lambda: service(request, "food_catalog").nearby(
                Location(latitude, longitude), limit
            )
        )

    @router.get(
        "/businesses/{business_id}/menu",
        response_model=MenuResponse,
        summary="Consultar el menú de un negocio",
        description="Muestra los productos de ejemplo del negocio. Los precios y la disponibilidad real siguen pendientes de configurar.",
    )
    def menu(business_id: str, request: Request):
        return service(request, "food_catalog").menu(business_id)

    return router
