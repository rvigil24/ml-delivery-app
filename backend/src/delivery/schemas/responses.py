"""Datos y descripciones de las respuestas HTTP."""

from decimal import Decimal
from typing import Literal, Tuple

from pydantic import AwareDatetime, BaseModel, Field

from delivery.models.entities import VehicleType
from delivery.models.vehicle_rules import VehicleRejection


class PredictResponse(BaseModel):
    requested_at_utc: AwareDatetime
    duration_minutes: float = Field(ge=0, allow_inf_nan=False)
    duration_source: Literal["prediccion"]
    interval_definition: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    experimental: Literal[True] = True
    coverage_validated: Literal[False] = False
    limitations: Tuple[str, ...] = (
        "Estimación experimental; validación local pendiente.",
        "Duración creación–entrega; no es tiempo de conducción ni incluye intervalo predictivo",
        "Sin validación para El Salvador, distancias o diferencias entre vehículos",
        "Sin tarifa, cobertura comercial o cambios de estado",
    )


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    model_available: bool = Field(
        description="Indica si los modelos de duración y retraso están cargados."
    )


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    detail: ErrorDetail


class QuoteAmountsResponse(BaseModel):
    currency: str
    delivery_fee: Decimal
    courier_payment: Decimal
    variable_cost: Decimal
    attributable_cost: Decimal
    margin: Decimal


class VehicleDecisionResponse(BaseModel):
    vehicle: VehicleType
    reasons: Tuple[VehicleRejection, ...]


class QuotePreviewResponse(BaseModel):
    quote_id: str
    order_id: str
    distance_km: Decimal
    distance_method: str
    duration: PredictResponse
    amounts: QuoteAmountsResponse
    pricing_policy_version: str
    vehicle_policy_version: str
    service_area_id: str
    load_kg: Decimal
    within_configured_area: bool
    eligible_vehicles: Tuple[VehicleType, ...]
    vehicle_decisions: Tuple[VehicleDecisionResponse, ...]
    experimental: Literal[True] = True
    coverage_validated: Literal[False] = False
    commercial_quote_validated: Literal[False] = False
    limitations: Tuple[str, ...]
