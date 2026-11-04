"""T26: reserva condicional del grupo y validación autoritativa de cotización."""

from datetime import datetime
from typing import Protocol, Tuple

from delivery.domain.assignments import SimulatedAssignment
from delivery.domain.models import Courier, Order, OrderStatus
from delivery.domain.order_lifecycle import OrderRecord
from .orders import OrderRepository


class ConfirmedQuoteRequirements(Protocol):
    def validate_confirmed(self, order: Order) -> None:
        """Acreditar cotización/confirmación válidas; no fabricar ni modificar datos."""
        ...


class DispatchRepository(OrderRepository, Protocol):
    def get_courier(self, courier_id: str) -> Courier: ...

    def get_assignment(self, assignment_id: str) -> SimulatedAssignment: ...

    def commit_assignment(self, assignment: SimulatedAssignment, expected: Tuple[OrderRecord, ...]) -> SimulatedAssignment:
        """Revalidar snapshots/repartidor y reservar grupo + disponibilidad atómicamente."""
        ...

    def validate_progress(self, order_id: str, target: OrderStatus) -> None: ...

    def release(self, assignment_id: str, occurred_at: datetime) -> SimulatedAssignment:
        """Liberar solo después de todas las entregas, sin completar pedidos implícitamente."""
        ...
