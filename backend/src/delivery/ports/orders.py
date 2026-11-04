"""T20: repositorio de pedidos, catálogo de negocios y validación de requisitos."""

from datetime import datetime
from typing import Optional, Protocol

from delivery.domain.models import Business, Order, OrderStatus
from delivery.domain.order_lifecycle import OrderRecord


class BusinessReader(Protocol):
    def get(self, business_id: str) -> Optional[Business]: ...


class OrderRepository(Protocol):
    def get(self, order_id: str) -> OrderRecord: ...

    def create(self, order: Order, occurred_at: datetime) -> OrderRecord: ...

    def transition(self, order_id: str, expected: OrderStatus, target: OrderStatus,
                   occurred_at: datetime) -> OrderRecord:
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
