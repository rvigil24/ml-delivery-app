"""Endpoint optativo de demostración local, sin modificar contratos generales."""

from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field

from delivery.domain.catalogs import StorageUnavailable
from delivery.domain.models import Business, Courier, Order
from delivery.domain.pricing import OperatorCosts, PricingPolicy
from delivery.domain.routing import RoutePolicy
from delivery.domain.vehicle_rules import VehiclePolicy
from delivery.services.demonstration import run_demonstration
from .storage import valid


class DemonstrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    simulated: Literal[True]
    business: Business
    courier: Courier
    order: Order
    pricing: PricingPolicy
    vehicle_policy: VehiclePolicy
    route_policy: RoutePolicy
    costs: OperatorCosts
    load_kg: Decimal = Field(gt=0, allow_inf_nan=False)
    promised_minutes: float = Field(gt=0, allow_inf_nan=False, strict=True)


def demonstration_router():
    router = APIRouter(tags=["Demostración completa simulada"])

    @router.post("/demo/deliveries", status_code=201,
                 summary="Ejecutar un envío completo simulado y devolver su recibo")
    def demonstrate(body: DemonstrationRequest, request: Request):
        storage = request.app.state.mongo_storage
        if storage is None:
            raise StorageUnavailable("La demostración requiere MongoDB preparado")
        values = {name: getattr(body, name) for name in DemonstrationRequest.model_fields if name != "simulated"}
        result = valid(lambda: run_demonstration(storage, request.app.state.delivery_estimates, **values))
        return jsonable_encoder(result, custom_encoder={Decimal: str})

    return router
