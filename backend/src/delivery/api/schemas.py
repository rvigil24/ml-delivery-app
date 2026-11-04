"""T30–T31: contratos JSON separados de las entidades de dominio."""

from typing import Literal, Tuple
from decimal import Decimal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

from delivery.domain.models import VehicleType
from delivery.domain.vehicle_rules import VehicleRejection


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requested_at: AwareDatetime = Field(description="Creación del pedido en ISO 8601 con zona horaria")

    @field_validator("requested_at", mode="before")
    @classmethod
    def require_iso_string(cls, value):
        if not isinstance(value, str) or "T" not in value:
            raise ValueError("Se requiere una fecha ISO 8601 con zona horaria")
        return value


class PredictResponse(BaseModel):
    requested_at_utc: AwareDatetime
    duration_minutes: float = Field(ge=0, allow_inf_nan=False)
    duration_source: Literal["prediccion"]
    interval_definition: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    academic_only: Literal[True] = True
    coverage_validated: Literal[False] = False
    limitations: Tuple[str, ...] = (
        "Modelo experimental entrenado con datos chinos y solo hora/día UTC",
        "Duración creación–entrega; no es tiempo de conducción ni incluye intervalo predictivo",
        "Sin validación para El Salvador, distancias o diferencias entre vehículos",
        "Sin tarifa, cobertura comercial o cambios de estado",
    )


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    model_available: bool


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    detail: ErrorDetail


class OperatorCostsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    variable_cost: Decimal = Field(ge=0, allow_inf_nan=False)
    attributable_cost: Decimal = Field(ge=0, allow_inf_nan=False)


class QuotePreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quote_id: str = Field(min_length=1)
    load_kg: Decimal = Field(gt=0, allow_inf_nan=False)
    costs: OperatorCostsRequest


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
    academic_only: Literal[True] = True
    coverage_validated: Literal[False] = False
    commercial_quote_validated: Literal[False] = False
    limitations: Tuple[str, ...]
