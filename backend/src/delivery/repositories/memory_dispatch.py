"""T26: coordinador local bajo el mismo lock de pedidos, repartidores y reservas."""

from dataclasses import replace
from datetime import datetime
from typing import Iterable, Tuple

from delivery.models.assignments import (
    AssignmentConflict,
    AssignmentNotFound,
    CourierNotFound,
    SimulatedAssignment,
)
from delivery.models.entities import Courier, OrderStatus
from delivery.models.order_lifecycle import OrderEvent, OrderRecord
from delivery.models.routing import StopType
from delivery.repositories.memory import InMemoryOrderRepository


class InMemoryDispatchRepository(InMemoryOrderRepository):
    """Usar esta misma instancia también al componer OrderService."""

    def __init__(self, couriers: Iterable[Courier]) -> None:
        super().__init__()
        self._couriers = {}
        self._assignments = {}
        self._active_orders = {}
        for courier in couriers:
            if not isinstance(courier, Courier) or courier.id in self._couriers:
                raise ValueError("Se requieren Courier con IDs únicos")
            self._couriers[courier.id] = courier

    def get_courier(self, courier_id: str) -> Courier:
        with self._lock:
            try:
                return self._couriers[courier_id]
            except KeyError:
                raise CourierNotFound(courier_id) from None

    def get_assignment(self, assignment_id: str) -> SimulatedAssignment:
        with self._lock:
            try:
                return self._assignments[assignment_id]
            except KeyError:
                raise AssignmentNotFound(assignment_id) from None

    def list_assignments(self, courier_id: str, limit: int):
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        ):
            raise ValueError("limit fuera de rango")
        with self._lock:
            return tuple(
                self._assignments[key]
                for key in sorted(self._assignments)
                if self._assignments[key].courier.id == courier_id
            )[:limit]

    def commit_assignment(
        self, assignment: SimulatedAssignment, expected: Tuple[OrderRecord, ...]
    ) -> SimulatedAssignment:
        with self._lock:
            if assignment.id in self._assignments or not assignment.active:
                raise AssignmentConflict(
                    "ID de asignación duplicado o asignación ya cerrada"
                )
            courier = self.get_courier(assignment.courier.id)
            if (
                courier != assignment.courier
                or not courier.approved
                or not courier.available
            ):
                raise AssignmentConflict(
                    "El repartidor cambió o dejó de estar disponible"
                )
            before = {record.order.id: record for record in expected}
            if len(before) != len(expected) or set(before) != {
                order.id for order in assignment.route.orders
            }:
                raise AssignmentConflict("Snapshots incompatibles con el grupo")
            updates = {}
            for order in assignment.route.orders:
                current = self._get(order.id)
                if (
                    current != before[order.id]
                    or current.order != order
                    or current.order.status is not OrderStatus.CONFIRMED
                    or order.id in self._active_orders
                ):
                    raise AssignmentConflict("Un pedido cambió o ya tiene asignación")
                event = OrderEvent(
                    OrderStatus.CONFIRMED, OrderStatus.ASSIGNED, assignment.created_at
                )
                if event.occurred_at < current.events[-1].occurred_at:
                    raise ValueError("La asignación no puede preceder al historial")
                updates[order.id] = OrderRecord(
                    replace(order, status=OrderStatus.ASSIGNED),
                    current.events + (event,),
                )
            occupied = replace(courier, available=False)
            # Todas las comprobaciones se completan antes de la primera escritura.
            self._records.update(updates)
            self._couriers[courier.id] = occupied
            self._assignments[assignment.id] = assignment
            self._active_orders.update(
                {order_id: assignment.id for order_id in updates}
            )
            return assignment

    def validate_progress(self, order_id: str, target: OrderStatus) -> None:
        with self._lock:
            assignment_id = self._active_orders.get(order_id)
            if assignment_id is None:
                raise AssignmentConflict("El pedido no tiene asignación activa")
            assignment = self.get_assignment(assignment_id)
            for stop in assignment.route.stops:
                status = self._get(stop.order_id).order.status
                done = status is OrderStatus.DELIVERED or (
                    stop.kind is StopType.PICKUP and status is OrderStatus.PICKED_UP
                )
                if not done:
                    next_status = (
                        OrderStatus.PICKED_UP
                        if stop.kind is StopType.PICKUP
                        else OrderStatus.DELIVERED
                    )
                    if stop.order_id != order_id or next_status is not target:
                        raise AssignmentConflict(
                            "La transición no corresponde a la siguiente parada"
                        )
                    return
            raise AssignmentConflict("La ruta ya fue completada")

    def transition(
        self,
        order_id: str,
        expected: OrderStatus,
        target: OrderStatus,
        occurred_at: datetime,
    ) -> OrderRecord:
        if target is OrderStatus.ASSIGNED:
            raise AssignmentConflict(
                "Usar la asignación atómica del grupo, no una transición aislada"
            )
        with self._lock:
            if target in (OrderStatus.PICKED_UP, OrderStatus.DELIVERED):
                self.validate_progress(order_id, target)
            return super().transition(order_id, expected, target, occurred_at)

    def release(self, assignment_id: str, occurred_at: datetime) -> SimulatedAssignment:
        with self._lock:
            assignment = self.get_assignment(assignment_id)
            if not assignment.active:
                raise AssignmentConflict("La asignación ya fue liberada")
            records = [self._get(order.id) for order in assignment.route.orders]
            if any(
                record.order.status is not OrderStatus.DELIVERED for record in records
            ):
                raise AssignmentConflict(
                    "No se libera antes de entregar todos los pedidos"
                )
            OrderEvent(OrderStatus.PICKED_UP, OrderStatus.DELIVERED, occurred_at)
            if occurred_at < max(record.events[-1].occurred_at for record in records):
                raise ValueError("La liberación no puede preceder a las entregas")
            released = replace(assignment, released_at=occurred_at)
            self._couriers[assignment.courier.id] = replace(
                self.get_courier(assignment.courier.id), available=True
            )
            self._assignments[assignment_id] = released
            for record in records:
                del self._active_orders[record.order.id]
            return released
