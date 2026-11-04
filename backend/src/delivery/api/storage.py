"""T32: CRUD operativo y transiciones controladas, sin acceso directo a MongoDB."""

from typing import Tuple

from fastapi import APIRouter, HTTPException, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field, StrictBool

from delivery.domain.catalogs import StorageUnavailable
from delivery.domain.models import Business, Courier, Location, Order, OrderStatus, VehicleType
from delivery.domain.order_lifecycle import OrderRecord
from .schemas import ErrorResponse


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LocationInput(Input):
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False, strict=True)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False, strict=True)


class BusinessInput(Input):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    location: LocationInput


class CourierInput(Input):
    id: str = Field(min_length=1)
    vehicle: VehicleType
    approved: StrictBool
    available: StrictBool


class OrderInput(Input):
    id: str = Field(min_length=1)
    business_id: str = Field(min_length=1)
    origin: LocationInput
    destination: LocationInput
    details: str = Field(min_length=1)


class TransitionInput(Input):
    expected: OrderStatus
    target: OrderStatus


def service(request, name):
    value = getattr(request.app.state, name, None)
    if value is None:
        raise StorageUnavailable("No hay persistencia configurada")
    return value


def valid(function):
    try:
        return function()
    except ValueError:
        raise HTTPException(422, detail={"code": "invalid_request", "message": "Datos de dominio inválidos."}) from None


def storage_router():
    router = APIRouter(tags=["Datos operativos simulados"],
        responses={status: {"model": ErrorResponse} for status in (404, 409, 422, 503, 500)})

    # Las mismas cuatro operaciones de catálogo para negocios y repartidores.
    def register_catalog(path, state_name, entity_type, input_type):
        def build(body):
            values = body.model_dump()
            if entity_type is Business:
                values["location"] = Location(**values["location"])
            return entity_type(**values)

        def create(body: input_type, request: Request):
            return valid(lambda: service(request, state_name).create(build(body)))

        def get(identifier: str, request: Request):
            return service(request, state_name).get(identifier)

        def listing(request: Request, limit: int = Query(100, ge=1, le=100)):
            return service(request, state_name).list(limit)

        def update(identifier: str, body: input_type, request: Request):
            return valid(lambda: service(request, state_name).update(identifier, build(body)))

        def delete(identifier: str, request: Request):
            service(request, state_name).delete(identifier)
            return Response(status_code=204)

        for function, suffix, method, model, status in (
            (create, "", "POST", entity_type, 201), (listing, "", "GET", Tuple[entity_type, ...], 200),
            (get, "/{identifier}", "GET", entity_type, 200), (update, "/{identifier}", "PUT", entity_type, 200),
            (delete, "/{identifier}", "DELETE", None, 204)):
            router.add_api_route(path + suffix, function, methods=[method], response_model=model,
                                 status_code=status, name=f"{method.lower()}_{path.strip('/')}_{function.__name__}")

    register_catalog("/businesses", "business_catalog", Business, BusinessInput)
    register_catalog("/couriers", "courier_catalog", Courier, CourierInput)

    @router.post("/orders", response_model=OrderRecord, status_code=201)
    def create_order(body: OrderInput, request: Request):
        return valid(lambda: service(request, "order_service").register(Order(body.id, body.business_id,
            Location(**body.origin.model_dump()), Location(**body.destination.model_dump()), body.details)))

    @router.get("/orders", response_model=Tuple[OrderRecord, ...])
    def list_orders(request: Request, limit: int = Query(100, ge=1, le=100)):
        return service(request, "order_service").list(limit)

    @router.get("/orders/{order_id}", response_model=OrderRecord)
    def get_order(order_id: str, request: Request):
        return service(request, "order_service").get(order_id)

    @router.post("/orders/{order_id}/transitions", response_model=OrderRecord)
    def transition(order_id: str, body: TransitionInput, request: Request):
        return service(request, "order_service").transition(order_id, body.expected, body.target)

    return router
