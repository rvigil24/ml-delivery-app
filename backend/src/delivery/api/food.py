"""Consultas de comida sin modificar pedidos ni inventar disponibilidad."""

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from typing import Literal, Optional, Tuple

from delivery.domain.models import Business, Location
from .schemas import ErrorResponse
from .storage import service, valid


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
    router = APIRouter(tags=["Negocios"],
        responses={status: {"model": ErrorResponse} for status in (404, 422, 503, 500)})

    @router.get("/businesses/nearby", response_model=NearbyResponse, summary="Buscar negocios por cercanía",
                description="Ordena los negocios con menú por distancia aproximada al punto de entrega. No confirma cobertura ni disponibilidad.")
    def nearby(request: Request,
               latitude: float = Query(ge=-90, le=90, allow_inf_nan=False),
               longitude: float = Query(ge=-180, le=180, allow_inf_nan=False),
               limit: int = Query(20, ge=1, le=100)):
        return valid(lambda: service(request, "food_catalog").nearby(Location(latitude, longitude), limit))

    @router.get("/businesses/{business_id}/menu", response_model=MenuResponse, summary="Consultar el menú de un negocio",
                description="Muestra los productos de ejemplo del negocio. Los precios y la disponibilidad real siguen pendientes de configurar.")
    def menu(business_id: str, request: Request):
        return service(request, "food_catalog").menu(business_id)

    return router
