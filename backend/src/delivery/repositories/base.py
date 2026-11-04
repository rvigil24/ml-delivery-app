"""Tipos compartidos que deben cumplir los repositorios y validadores."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Protocol, Tuple, TypeVar

from delivery.models.assignments import SimulatedAssignment
from delivery.models.cash import CashRecord, CashStatus
from delivery.models.entities import Business, Courier, Order, OrderStatus, Quote
from delivery.models.order_lifecycle import OrderRecord

T = TypeVar("T")


class CatalogRepository(Protocol[T]):
    def get(self, identifier: str) -> Optional[T]: ...
    def list(self, limit: int) -> Tuple[T, ...]: ...
    def all(self) -> Tuple[T, ...]: ...
    def create(self, entity: T) -> T: ...
    def update(self, entity: T, expected: T) -> T: ...
    def delete(self, identifier: str, expected: T) -> None: ...


class BusinessReader(Protocol):
    def get(self, business_id: str) -> Optional[Business]: ...


class OrderRepository(Protocol):
    def get(self, order_id: str) -> OrderRecord: ...

    def list(self, limit: int) -> Tuple[OrderRecord, ...]: ...

    def list_for_business(
        self, business_id: str, limit: int
    ) -> Tuple[OrderRecord, ...]: ...

    def create(self, order: Order, occurred_at: datetime) -> OrderRecord: ...

    def transition(
        self,
        order_id: str,
        expected: OrderStatus,
        target: OrderStatus,
        occurred_at: datetime,
    ) -> OrderRecord:
        """Comparar estado, cambiar pedido y añadir evento como una sola operación.

        Si el estado actual no coincide con expected, fallar sin escribir.
        """
        ...


class TransitionRequirements(Protocol):
    def validate(self, order: Order, target: OrderStatus) -> None:
        """Exigir cotización/asignación válida y contexto según la transición.

        Consulta fuentes autoritativas; falla si falta una dependencia o requisito.
        No calcula tarifas ni crea una asignación para permitir avanzar.
        """
        ...


class ConfirmedQuoteRequirements(Protocol):
    def validate_confirmed(self, order: Order) -> None:
        """Acreditar cotización/confirmación válidas; no fabricar ni modificar datos."""
        ...


class DispatchRepository(OrderRepository, Protocol):
    def get_courier(self, courier_id: str) -> Courier: ...

    def get_assignment(self, assignment_id: str) -> SimulatedAssignment: ...

    def list_assignments(
        self, courier_id: str, limit: int
    ) -> Tuple[SimulatedAssignment, ...]: ...

    def commit_assignment(
        self, assignment: SimulatedAssignment, expected: Tuple[OrderRecord, ...]
    ) -> SimulatedAssignment:
        """Revalidar snapshots/repartidor y reservar grupo + disponibilidad atómicamente."""
        ...

    def validate_progress(self, order_id: str, target: OrderStatus) -> None: ...

    def release(self, assignment_id: str, occurred_at: datetime) -> SimulatedAssignment:
        """Liberar solo después de todas las entregas, sin completar pedidos implícitamente."""
        ...


class CashQuoteSource(Protocol):
    def get_validated(self, order: Order) -> Quote:
        """Consultar fuente autoritativa; rechazar cotizaciones no validadas o ausentes."""
        ...


class CashRepository(Protocol):
    def get(self, order_id: str) -> CashRecord: ...

    def create(self, record: CashRecord) -> CashRecord:
        """Crear expectativa pendiente una sola vez, sin sobrescribir por pedido."""
        ...

    def transition(
        self,
        order_id: str,
        expected: CashStatus,
        target: CashStatus,
        currency: str,
        amount: Decimal,
        occurred_at: datetime,
    ) -> CashRecord:
        """Comparar estado, validar pago/fecha y añadir evento atómicamente."""
        ...
