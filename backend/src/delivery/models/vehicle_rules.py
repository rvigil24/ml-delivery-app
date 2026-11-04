"""T23: criterios configurables de simulación, independientes del modelo ML."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Tuple

from delivery.models.entities import Location, Order, VehicleType
from delivery.models.estimation import DISTANCE_METHOD, haversine_km


class VehicleConfigurationMissing(RuntimeError):
    pass


def _positive_decimal(value: Decimal, name: str) -> None:
    if not isinstance(value, Decimal) or not value.is_finite() or value <= 0:
        raise ValueError(f"{name} debe ser Decimal finito positivo")


@dataclass(frozen=True)
class ServiceArea:
    id: str
    southwest: Location
    northeast: Location

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("id de zona debe ser texto no vacío")
        if not isinstance(self.southwest, Location) or not isinstance(
            self.northeast, Location
        ):
            raise ValueError("Las esquinas deben ser Location en grados")
        if (
            self.southwest.latitude >= self.northeast.latitude
            or self.southwest.longitude >= self.northeast.longitude
        ):
            raise ValueError(
                "La zona debe tener sur < norte y oeste < este, sin cruzar el antimeridiano"
            )

    def contains(self, location: Location) -> bool:
        return (
            self.southwest.latitude <= location.latitude <= self.northeast.latitude
            and self.southwest.longitude
            <= location.longitude
            <= self.northeast.longitude
        )


@dataclass(frozen=True)
class VehicleLimits:
    max_distance_km: Decimal
    max_load_kg: Decimal

    def __post_init__(self) -> None:
        _positive_decimal(self.max_distance_km, "max_distance_km")
        _positive_decimal(self.max_load_kg, "max_load_kg")


@dataclass(frozen=True)
class VehiclePolicy:
    version: str
    area: ServiceArea
    bicycle: VehicleLimits
    motorcycle: VehicleLimits

    def __post_init__(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("version debe ser texto no vacío")
        if not isinstance(self.area, ServiceArea):
            raise ValueError("Se requiere ServiceArea explícita")
        if not isinstance(self.bicycle, VehicleLimits) or not isinstance(
            self.motorcycle, VehicleLimits
        ):
            raise ValueError("Se requieren VehicleLimits para ambos vehículos")


class VehicleRejection(str, Enum):
    OUTSIDE_AREA = "outside_service_area"
    DISTANCE = "distance_limit_exceeded"
    LOAD = "load_limit_exceeded"


@dataclass(frozen=True)
class VehicleDecision:
    vehicle: VehicleType
    reasons: Tuple[VehicleRejection, ...]

    @property
    def eligible(self) -> bool:
        return not self.reasons


@dataclass(frozen=True)
class VehicleEvaluation:
    order: Order
    policy: VehiclePolicy
    distance_km: Decimal
    load_kg: Decimal
    within_configured_area: bool
    decisions: Tuple[VehicleDecision, ...]
    distance_method: str = field(default=DISTANCE_METHOD, init=False)
    academic_only: bool = field(default=True, init=False)

    @property
    def eligible_vehicles(self) -> Tuple[VehicleType, ...]:
        return tuple(
            decision.vehicle for decision in self.decisions if decision.eligible
        )


def evaluate_vehicle_rules(
    order: Order, load_kg: Decimal, policy: VehiclePolicy
) -> VehicleEvaluation:
    if not isinstance(order, Order) or not isinstance(policy, VehiclePolicy):
        raise ValueError("Se requieren Order y VehiclePolicy")
    _positive_decimal(load_kg, "load_kg")
    distance = Decimal(str(haversine_km(order.origin, order.destination)))
    within_area = policy.area.contains(order.origin) and policy.area.contains(
        order.destination
    )
    decisions = []
    # Orden de presentación estable, sin preferencia ni elección automática.
    for vehicle, limits in (
        (VehicleType.BICYCLE, policy.bicycle),
        (VehicleType.MOTORCYCLE, policy.motorcycle),
    ):
        reasons = []
        if not within_area:
            reasons.append(VehicleRejection.OUTSIDE_AREA)
        if distance > limits.max_distance_km:
            reasons.append(VehicleRejection.DISTANCE)
        if load_kg > limits.max_load_kg:
            reasons.append(VehicleRejection.LOAD)
        decisions.append(VehicleDecision(vehicle, tuple(reasons)))
    return VehicleEvaluation(
        order, policy, distance, load_kg, within_area, tuple(decisions)
    )
