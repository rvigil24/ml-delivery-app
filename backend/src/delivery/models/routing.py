"""T24: sugerencia académica por vecino cercano y precedencia recogida/entrega."""

from dataclasses import dataclass, field
from decimal import Context, Decimal, localcontext
from enum import Enum
from typing import Tuple

from delivery.models.entities import Location, Order, OrderStatus
from delivery.models.estimation import DISTANCE_METHOD, haversine_km
from delivery.models.order_lifecycle import OrderConflict
from delivery.models.vehicle_rules import ServiceArea


class RouteConfigurationMissing(RuntimeError):
    pass


@dataclass(frozen=True)
class RoutePolicy:
    version: str
    max_orders: int
    area: ServiceArea

    def __post_init__(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("version debe ser texto no vacío")
        if (
            isinstance(self.max_orders, bool)
            or not isinstance(self.max_orders, int)
            or self.max_orders <= 0
        ):
            raise ValueError("max_orders debe ser entero positivo explícito")
        if not isinstance(self.area, ServiceArea):
            raise ValueError("Se requiere ServiceArea explícita")


class StopType(str, Enum):
    PICKUP = "recogida"
    DELIVERY = "entrega"


@dataclass(frozen=True)
class RouteStop:
    order_id: str
    kind: StopType
    location: Location
    leg_distance_km: Decimal


@dataclass(frozen=True)
class RoutePlan:
    policy: RoutePolicy
    start: Location
    orders: Tuple[Order, ...]
    stops: Tuple[RouteStop, ...]
    total_distance_km: Decimal
    distance_method: str = field(default=DISTANCE_METHOD, init=False)
    academic_only: bool = field(default=True, init=False)
    capacity_validated: bool = field(default=False, init=False)
    road_route_validated: bool = field(default=False, init=False)


def validate_group(order_ids: Tuple[str, ...], policy: RoutePolicy) -> None:
    if not isinstance(policy, RoutePolicy):
        raise ValueError("Se requiere RoutePolicy")
    if not order_ids or len(order_ids) > policy.max_orders:
        raise ValueError("El grupo debe ser no vacío y no superar max_orders")
    if any(
        not isinstance(identifier, str) or not identifier.strip()
        for identifier in order_ids
    ):
        raise ValueError("Los IDs deben ser textos no vacíos")
    if len(set(order_ids)) != len(order_ids):
        raise ValueError("El grupo no puede contener pedidos duplicados")


def suggest_route(
    orders: Tuple[Order, ...], start: Location, policy: RoutePolicy
) -> RoutePlan:
    if any(not isinstance(order, Order) for order in orders):
        raise ValueError("El grupo debe contener Order")
    validate_group(tuple(order.id for order in orders), policy)
    if not isinstance(start, Location) or not policy.area.contains(start):
        raise ValueError("El punto inicial debe estar dentro de la zona configurada")
    snapshots = tuple(sorted(orders, key=lambda order: order.id))
    for order in snapshots:
        if order.status not in (
            OrderStatus.REQUESTED,
            OrderStatus.QUOTED,
            OrderStatus.CONFIRMED,
        ):
            raise OrderConflict(
                "No planificar pedidos asignados, recogidos, entregados o cancelados"
            )
        if not policy.area.contains(order.origin) or not policy.area.contains(
            order.destination
        ):
            raise ValueError(f"Pedido fuera de la zona configurada: {order.id}")
    unpicked = {order.id: order for order in snapshots}
    carried = {}
    stops = []
    current = start
    while unpicked or carried:
        candidates = [
            (
                haversine_km(current, order.origin),
                order.id,
                StopType.PICKUP,
                order.origin,
            )
            for order in unpicked.values()
        ]
        candidates += [
            (
                haversine_km(current, order.destination),
                order.id,
                StopType.DELIVERY,
                order.destination,
            )
            for order in carried.values()
        ]
        distance, order_id, kind, location = min(
            candidates, key=lambda item: (item[0], item[1])
        )
        stops.append(RouteStop(order_id, kind, location, Decimal(str(distance))))
        if kind is StopType.PICKUP:
            carried[order_id] = unpicked.pop(order_id)
        else:
            carried.pop(order_id)
        current = location
    with localcontext(Context(prec=28)):
        total = sum((stop.leg_distance_km for stop in stops), Decimal(0))
    return RoutePlan(policy, start, snapshots, tuple(stops), total)
