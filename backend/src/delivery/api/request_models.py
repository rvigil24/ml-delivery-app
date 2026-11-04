"""Datos que acepta la API y sus validaciones de entrada."""

from decimal import Decimal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    field_validator,
)

from delivery.domain.models import OrderStatus, VehicleType


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LocationInput(Input):
    latitude: float = Field(
        ge=-90,
        le=90,
        allow_inf_nan=False,
        strict=True,
        description="Latitud del punto, en grados.",
    )
    longitude: float = Field(
        ge=-180,
        le=180,
        allow_inf_nan=False,
        strict=True,
        description="Longitud del punto, en grados.",
    )


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
    expected: OrderStatus = Field(
        description="Estado actual que esperas encontrar en el pedido."
    )
    target: OrderStatus = Field(description="Nuevo estado solicitado.")


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requested_at: AwareDatetime = Field(
        description="Fecha y hora del pedido, con zona horaria."
    )

    @field_validator("requested_at", mode="before")
    @classmethod
    def require_iso_string(cls, value):
        if not isinstance(value, str) or "T" not in value:
            raise ValueError("Se requiere una fecha ISO 8601 con zona horaria")
        return value


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
