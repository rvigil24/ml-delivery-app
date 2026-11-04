"""T26: asignación local simulada con evidencia de ruta y carga planificadas."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Context, Decimal, DecimalException, Inexact, localcontext
from typing import Mapping, Optional, Tuple

from delivery.models.entities import Courier, Location, Order, OrderStatus, VehicleType
from delivery.models.order_lifecycle import OrderConflict, OrderEvent
from delivery.models.routing import RoutePlan, RoutePolicy, StopType, suggest_route
from delivery.models.vehicle_rules import VehiclePolicy, evaluate_vehicle_rules


class AssignmentConflict(OrderConflict):
    pass


class AssignmentNotFound(LookupError):
    pass


class CourierNotFound(LookupError):
    pass


@dataclass(frozen=True)
class SimulatedAssignment:
    id: str
    courier: Courier
    route: RoutePlan
    vehicle_policy: VehiclePolicy
    loads_kg: Tuple[Tuple[str, Decimal], ...]
    peak_load_kg: Decimal
    created_at: datetime
    released_at: Optional[datetime] = None
    simulated: bool = field(default=True, init=False)
    road_route_validated: bool = field(default=False, init=False)

    @property
    def active(self) -> bool:
        return self.released_at is None


def prepare_assignment(
    assignment_id: str,
    courier: Courier,
    orders: Tuple[Order, ...],
    start: Location,
    route_policy: RoutePolicy,
    vehicle_policy: VehiclePolicy,
    loads_kg: Mapping[str, Decimal],
    occurred_at: datetime,
) -> SimulatedAssignment:
    if not isinstance(assignment_id, str) or not assignment_id.strip():
        raise ValueError("assignment_id debe ser texto no vacío")
    if (
        not isinstance(courier, Courier)
        or not courier.approved
        or not courier.available
    ):
        raise AssignmentConflict("El repartidor debe estar aprobado y disponible")
    if not isinstance(vehicle_policy, VehiclePolicy):
        raise ValueError("Se requiere VehiclePolicy explícita")
    if any(order.status is not OrderStatus.CONFIRMED for order in orders):
        raise AssignmentConflict("Todos los pedidos deben estar confirmados")
    route = suggest_route(orders, start, route_policy)
    identifiers = {order.id for order in route.orders}
    if not isinstance(loads_kg, Mapping) or set(loads_kg) != identifiers:
        raise ValueError("Las cargas deben corresponder exactamente al grupo")
    if not vehicle_policy.area.contains(start):
        raise AssignmentConflict("El inicio queda fuera de la zona del vehículo")
    for order in route.orders:
        evaluation = evaluate_vehicle_rules(order, loads_kg[order.id], vehicle_policy)
        if courier.vehicle not in evaluation.eligible_vehicles:
            raise AssignmentConflict(
                f"Pedido incompatible con el vehículo elegido: {order.id}"
            )
    limits = (
        vehicle_policy.bicycle
        if courier.vehicle is VehicleType.BICYCLE
        else vehicle_policy.motorcycle
    )
    if route.total_distance_km > limits.max_distance_km:
        raise AssignmentConflict(
            "La ruta completa supera el límite de distancia del vehículo"
        )
    try:
        with localcontext(Context(prec=28)) as context:
            context.traps[Inexact] = True
            load = peak = Decimal(0)
            for stop in route.stops:
                load += (
                    loads_kg[stop.order_id]
                    if stop.kind is StopType.PICKUP
                    else -loads_kg[stop.order_id]
                )
                peak = max(peak, load)
                if load < 0 or load > limits.max_load_kg:
                    raise AssignmentConflict(
                        "La carga acumulada de la ruta supera la capacidad"
                    )
            if load != 0:
                raise AssignmentConflict("La ruta no descarga todos los pedidos")
    except DecimalException as error:
        raise ValueError("La carga excede la precisión decimal soportada") from error
    # Reutiliza la validación UTC del dominio sin crear eventos persistidos.
    OrderEvent(OrderStatus.CONFIRMED, OrderStatus.ASSIGNED, occurred_at)
    loads = tuple((order.id, loads_kg[order.id]) for order in route.orders)
    return SimulatedAssignment(
        assignment_id, courier, route, vehicle_policy, loads, peak, occurred_at
    )
