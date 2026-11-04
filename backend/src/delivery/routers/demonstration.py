"""Endpoint optativo de demostración local, sin modificar contratos generales."""

from decimal import Decimal
from typing import Dict, Literal, Tuple

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field

from delivery.models.catalogs import StorageUnavailable
from delivery.models.entities import Business, Courier, Order
from delivery.models.pricing import OperatorCosts, PricingPolicy
from delivery.models.routing import RoutePolicy
from delivery.models.vehicle_rules import VehiclePolicy
from delivery.services.demonstration import run_demonstration, run_group_demonstration
from delivery.validation import valid


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


def public_receipt(value):
    if isinstance(value, dict):
        return {
            ("experimental" if key == "academic_only" else key): public_receipt(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [public_receipt(item) for item in value]
    return value


class GroupDemonstrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    simulated: Literal[True]
    business: Business
    courier: Courier
    orders: Tuple[Order, ...] = Field(min_length=2)
    pricing: PricingPolicy
    vehicle_policy: VehiclePolicy
    route_policy: RoutePolicy
    per_order_costs: Dict[str, OperatorCosts]
    grouped_costs: OperatorCosts
    loads_kg: Dict[str, Decimal]
    promised_minutes: float = Field(gt=0, allow_inf_nan=False, strict=True)


def demonstration_router():
    router = APIRouter(tags=["Demostración"])

    @router.post(
        "/demo/deliveries",
        status_code=201,
        summary="Probar un envío completo",
        description="Ejecuta un recorrido de prueba desde la solicitud hasta el registro del efectivo, usando datos simulados.",
    )
    def demonstrate(body: DemonstrationRequest, request: Request):
        storage = request.app.state.mongo_storage
        if storage is None:
            raise StorageUnavailable("La demostración requiere MongoDB preparado")
        values = {
            name: getattr(body, name)
            for name in DemonstrationRequest.model_fields
            if name != "simulated"
        }
        result = valid(
            lambda: run_demonstration(
                storage, request.app.state.delivery_estimates, **values
            )
        )

        return public_receipt(jsonable_encoder(result, custom_encoder={Decimal: str}))

    @router.post(
        "/demo/group-deliveries",
        status_code=201,
        summary="Probar entregas agrupadas",
        description="Ejecuta varios pedidos en una ruta, registra su efectivo y compara costos individuales y agrupados con parámetros de ejemplo.",
    )
    def demonstrate_group(body: GroupDemonstrationRequest, request: Request):
        storage = request.app.state.mongo_storage
        if storage is None:
            raise StorageUnavailable("La demostración requiere MongoDB preparado")
        values = {
            name: getattr(body, name)
            for name in GroupDemonstrationRequest.model_fields
            if name != "simulated"
        }
        result = valid(
            lambda: run_group_demonstration(
                storage, request.app.state.delivery_estimates, **values
            )
        )
        return public_receipt(jsonable_encoder(result, custom_encoder={Decimal: str}))

    return router
