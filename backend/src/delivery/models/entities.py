"""Entidades y unidades mínimas de T04; sin cálculos comerciales ni IO."""

import math
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


def _text(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} debe ser texto no vacío")


def _number(value: float, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} debe ser un número finito")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{field} debe ser un número finito")


class VehicleType(str, Enum):
    BICYCLE = "bicicleta"
    MOTORCYCLE = "motocicleta"


class OrderStatus(str, Enum):
    """Vocabulario inicial; las transiciones se implementarán en T20."""

    REQUESTED = "solicitado"
    QUOTED = "cotizado"
    CONFIRMED = "confirmado"
    ASSIGNED = "asignado"
    PICKED_UP = "recogido"
    DELIVERED = "entregado"
    CANCELLED = "cancelado"


class DurationSource(str, Enum):
    PREDICTION = "prediccion"
    ILLUSTRATIVE = "ilustrativa"


@dataclass(frozen=True)
class Location:
    """Coordenadas geográficas en grados; no validan la zona de servicio."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        _number(self.latitude, "latitude")
        _number(self.longitude, "longitude")
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude debe estar entre -90 y 90 grados")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude debe estar entre -180 y 180 grados")


@dataclass(frozen=True)
class Business:
    id: str
    name: str
    location: Location

    def __post_init__(self) -> None:
        _text(self.id, "id")
        _text(self.name, "name")
        if not isinstance(self.location, Location):
            raise ValueError("location debe ser Location")


@dataclass(frozen=True)
class Order:
    id: str
    business_id: str
    origin: Location
    destination: Location
    details: str
    status: OrderStatus = OrderStatus.REQUESTED

    def __post_init__(self) -> None:
        _text(self.id, "id")
        _text(self.business_id, "business_id")
        _text(self.details, "details")
        if not isinstance(self.origin, Location) or not isinstance(
            self.destination, Location
        ):
            raise ValueError("origin y destination deben ser Location")
        if not isinstance(self.status, OrderStatus):
            raise ValueError("status debe ser OrderStatus")


@dataclass(frozen=True)
class Courier:
    id: str
    vehicle: VehicleType
    approved: bool
    available: bool

    def __post_init__(self) -> None:
        _text(self.id, "id")
        if not isinstance(self.vehicle, VehicleType):
            raise ValueError("vehicle debe ser VehicleType")
        if not isinstance(self.approved, bool) or not isinstance(self.available, bool):
            raise ValueError("approved y available deben ser booleanos")


@dataclass(frozen=True)
class DeliveryDuration:
    """Duración suministrada, sin generar etiquetas ni ejecutar inferencia."""

    minutes: float
    source: DurationSource
    interval_definition: str
    model_version: Optional[str] = None

    def __post_init__(self) -> None:
        _number(self.minutes, "minutes")
        if self.minutes < 0:
            raise ValueError("minutes no puede ser negativo")
        if not isinstance(self.source, DurationSource):
            raise ValueError("source debe ser DurationSource")
        _text(self.interval_definition, "interval_definition")
        if self.source is DurationSource.PREDICTION:
            _text(self.model_version, "model_version")
        elif self.model_version is not None:
            raise ValueError("Una duración ilustrativa no debe atribuirse a un modelo")


@dataclass(frozen=True)
class QuoteAmounts:
    """Importes suministrados; no calcula ni aprueba una fórmula comercial."""

    currency: str
    delivery_fee: Decimal
    courier_payment: Decimal
    variable_cost: Decimal
    attributable_cost: Decimal
    margin: Decimal

    def __post_init__(self) -> None:
        if (
            not isinstance(self.currency, str)
            or len(self.currency) != 3
            or not self.currency.isascii()
            or not self.currency.isalpha()
            or not self.currency.isupper()
        ):
            raise ValueError("currency debe ser un código de tres letras mayúsculas")
        for field in (
            "delivery_fee",
            "courier_payment",
            "variable_cost",
            "attributable_cost",
            "margin",
        ):
            value = getattr(self, field)
            if not isinstance(value, Decimal) or not value.is_finite():
                raise ValueError(f"{field} debe ser Decimal finito")
            if field != "margin" and value < 0:
                raise ValueError(f"{field} no puede ser negativo")


@dataclass(frozen=True)
class Quote:
    """Borrador de cotización; None significa pendiente, no un valor cero."""

    id: str
    order_id: str
    distance_km: float
    distance_method: str
    duration: Optional[DeliveryDuration] = None
    amounts: Optional[QuoteAmounts] = None

    def __post_init__(self) -> None:
        _text(self.id, "id")
        _text(self.order_id, "order_id")
        _number(self.distance_km, "distance_km")
        if self.distance_km < 0:
            raise ValueError("distance_km no puede ser negativo")
        _text(self.distance_method, "distance_method")
        if self.duration is not None and not isinstance(
            self.duration, DeliveryDuration
        ):
            raise ValueError("duration debe ser DeliveryDuration o None")
        if self.amounts is not None and not isinstance(self.amounts, QuoteAmounts):
            raise ValueError("amounts debe ser QuoteAmounts o None")
