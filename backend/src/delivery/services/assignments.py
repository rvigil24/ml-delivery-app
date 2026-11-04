"""T26: asignación simulada, validación explícita y liberación sin canales reales."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable, Mapping, Optional, Sequence

from delivery.models.assignments import SimulatedAssignment, prepare_assignment
from delivery.models.entities import Location, Order, OrderStatus
from delivery.models.order_lifecycle import MissingPrerequisite
from delivery.models.routing import (
    RouteConfigurationMissing,
    RoutePolicy,
    validate_group,
)
from delivery.models.vehicle_rules import VehiclePolicy
from delivery.repositories.base import (
    ConfirmedQuoteRequirements,
    DispatchRepository,
    TransitionRequirements,
)
from delivery.services.orders import utc_now


class AssignmentService:
    def __init__(
        self,
        repository: DispatchRepository,
        route_policy: Optional[RoutePolicy] = None,
        vehicle_policy: Optional[VehiclePolicy] = None,
        requirements: Optional[ConfirmedQuoteRequirements] = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._route_policy = route_policy
        self._vehicle_policy = vehicle_policy
        self._requirements = requirements
        self._clock = clock

    def _timestamp(self) -> datetime:
        value = self._clock()
        if (
            not isinstance(value, datetime)
            or value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError("El reloj debe devolver datetime con zona horaria")
        return value.astimezone(timezone.utc)

    def assign(
        self,
        assignment_id: str,
        courier_id: str,
        order_ids: Sequence[str],
        start: Location,
        loads_kg: Mapping[str, Decimal],
    ) -> SimulatedAssignment:
        if self._route_policy is None or self._vehicle_policy is None:
            raise RouteConfigurationMissing(
                "Faltan políticas explícitas de ruta/vehículo"
            )
        if self._requirements is None:
            raise MissingPrerequisite(
                "Falta un validador autoritativo de cotización confirmada"
            )
        if isinstance(order_ids, (str, bytes)):
            raise ValueError("Se requiere una colección explícita de IDs")
        identifiers = tuple(order_ids)
        validate_group(identifiers, self._route_policy)
        records = tuple(self._repository.get(identifier) for identifier in identifiers)
        courier = self._repository.get_courier(courier_id)
        for record in records:
            if record.order.status is not OrderStatus.CONFIRMED:
                raise MissingPrerequisite("Todos los pedidos deben estar confirmados")
            self._requirements.validate_confirmed(record.order)
        assignment = prepare_assignment(
            assignment_id,
            courier,
            tuple(record.order for record in records),
            start,
            self._route_policy,
            self._vehicle_policy,
            loads_kg,
            self._timestamp(),
        )
        return self._repository.commit_assignment(assignment, records)

    def get(self, assignment_id: str) -> SimulatedAssignment:
        return self._repository.get_assignment(assignment_id)

    def release(self, assignment_id: str) -> SimulatedAssignment:
        return self._repository.release(assignment_id, self._timestamp())


class DispatchOrderRequirements:
    """Componer con OrderService; cotización no se autoriza por tener un borrador académico."""

    def __init__(
        self,
        repository: DispatchRepository,
        quote_requirements: Optional[TransitionRequirements] = None,
    ) -> None:
        self._repository = repository
        self._quote_requirements = quote_requirements

    def validate(self, order: Order, target: OrderStatus) -> None:
        if target in (OrderStatus.PICKED_UP, OrderStatus.DELIVERED):
            self._repository.validate_progress(order.id, target)
        elif (
            target in (OrderStatus.QUOTED, OrderStatus.CONFIRMED)
            and self._quote_requirements is not None
        ):
            self._quote_requirements.validate(order, target)
        else:
            raise MissingPrerequisite(
                "Usar validación de cotización o asignación atómica según la transición"
            )
