"""Pedidos y asignaciones con transacciones compartidas."""

from dataclasses import replace
from typing import Tuple

from pymongo.errors import DuplicateKeyError

from delivery.database.codec import decode
from delivery.database.documents import cas, document, mongo_errors, transaction
from delivery.models.assignments import (
    AssignmentConflict,
    AssignmentNotFound,
    CourierNotFound,
    SimulatedAssignment,
)
from delivery.models.entities import Business, Courier, OrderStatus
from delivery.models.order_lifecycle import (
    BusinessNotFound,
    DuplicateOrder,
    OrderConflict,
    OrderEvent,
    OrderNotFound,
    OrderRecord,
    validate_transition,
)
from delivery.models.routing import StopType


class MongoDispatchRepository:
    """Una instancia satisface OrderRepository y DispatchRepository."""

    def __init__(self, database):
        self.database = database

    def _order_doc(self, identifier, session=None):
        doc = self.database.orders.find_one({"_id": identifier}, session=session)
        if doc is None:
            raise OrderNotFound(identifier)
        return doc

    def _assignment_doc(self, identifier, session=None):
        doc = self.database.assignments.find_one({"_id": identifier}, session=session)
        if doc is None:
            raise AssignmentNotFound(identifier)
        return doc

    @mongo_errors
    def get(self, order_id):
        return decode(OrderRecord, self._order_doc(order_id)["data"])

    @mongo_errors
    def list(self, limit):
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        ):
            raise ValueError("limit fuera de rango")
        return tuple(
            decode(OrderRecord, doc["data"])
            for doc in self.database.orders.find().sort("_id", 1).limit(limit)
        )

    @mongo_errors
    def list_for_business(self, business_id, limit):
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        ):
            raise ValueError("limit fuera de rango")
        query = {"data.order.business_id": business_id}
        return tuple(
            decode(OrderRecord, doc["data"])
            for doc in self.database.orders.find(query).sort("_id", 1).limit(limit)
        )

    @mongo_errors
    def create(self, order, occurred_at):
        if order.status is not OrderStatus.REQUESTED:
            raise OrderConflict("Un pedido nuevo debe estar solicitado")
        record = OrderRecord(order, (OrderEvent(None, order.status, occurred_at),))

        def perform(session):
            business = self.database.businesses.find_one(
                {"_id": order.business_id}, session=session
            )
            if business is None:
                raise BusinessNotFound(order.business_id)
            if decode(Business, business["data"]).location != order.origin:
                raise ValueError("El origen debe coincidir con el negocio")
            # Escribir el negocio evita carrera entre registrar pedido y borrar/editar su referencia.
            self.database.businesses.update_one(
                {"_id": order.business_id}, {"$inc": {"version": 1}}, session=session
            )
            self.database.orders.insert_one(document(order.id, record), session=session)
            return record

        try:
            return transaction(self.database, perform)
        except DuplicateKeyError:
            raise DuplicateOrder(order.id) from None

    @mongo_errors
    def get_courier(self, courier_id):
        doc = self.database.couriers.find_one({"_id": courier_id})
        if doc is None:
            raise CourierNotFound(courier_id)
        return decode(Courier, doc["data"])

    @mongo_errors
    def get_assignment(self, assignment_id):
        return decode(SimulatedAssignment, self._assignment_doc(assignment_id)["data"])

    @mongo_errors
    def list_assignments(self, courier_id, limit):
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        ):
            raise ValueError("limit fuera de rango")
        query = {"data.courier.id": courier_id}
        return tuple(
            decode(SimulatedAssignment, doc["data"])
            for doc in self.database.assignments.find(query).sort("_id", 1).limit(limit)
        )

    def _progress(self, order_id, target, session):
        doc = self.database.assignments.find_one(
            {"data.route.orders.id": order_id, "data.released_at": None},
            session=session,
        )
        if doc is None:
            raise AssignmentConflict("El pedido no tiene asignación activa")
        assignment = decode(SimulatedAssignment, doc["data"])
        for stop in assignment.route.stops:
            record = decode(
                OrderRecord, self._order_doc(stop.order_id, session)["data"]
            )
            done = record.order.status is OrderStatus.DELIVERED or (
                stop.kind is StopType.PICKUP
                and record.order.status is OrderStatus.PICKED_UP
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
                return doc
        raise AssignmentConflict("La ruta ya fue completada")

    @mongo_errors
    def validate_progress(self, order_id, target):
        transaction(
            self.database, lambda session: self._progress(order_id, target, session)
        )

    @mongo_errors
    def transition(self, order_id, expected, target, occurred_at):
        validate_transition(expected, target)
        if target is OrderStatus.ASSIGNED:
            raise AssignmentConflict("Usar asignación atómica, no transición aislada")
        event = OrderEvent(expected, target, occurred_at)

        def perform(session):
            before = self._order_doc(order_id, session)
            current = decode(OrderRecord, before["data"])
            if current.order.status is not expected:
                raise OrderConflict("El estado cambió")
            if occurred_at < current.events[-1].occurred_at:
                raise ValueError("Un evento no puede preceder al historial")
            if target in (OrderStatus.PICKED_UP, OrderStatus.DELIVERED):
                assignment = self._progress(order_id, target, session)
                # Serializar avances de pedidos distintos que comparten el mismo plan.
                self.database.assignments.update_one(
                    {"_id": assignment["_id"]},
                    {"$inc": {"version": 1}},
                    session=session,
                )
            updated = OrderRecord(
                replace(current.order, status=target), current.events + (event,)
            )
            return cas(self.database.orders, before, updated, OrderConflict, session)

        return transaction(self.database, perform)

    @mongo_errors
    def commit_assignment(self, assignment, expected: Tuple[OrderRecord, ...]):
        def perform(session):
            if not assignment.active or self.database.assignments.find_one(
                {"_id": assignment.id}, session=session
            ):
                raise AssignmentConflict("Asignación duplicada o cerrada")
            courier_doc = self.database.couriers.find_one(
                {"_id": assignment.courier.id}, session=session
            )
            if courier_doc is None:
                raise CourierNotFound(assignment.courier.id)
            courier = decode(Courier, courier_doc["data"])
            if (
                courier != assignment.courier
                or not courier.approved
                or not courier.available
            ):
                raise AssignmentConflict("El repartidor cambió o no está disponible")
            snapshots = {record.order.id: record for record in expected}
            if len(snapshots) != len(expected) or set(snapshots) != {
                order.id for order in assignment.route.orders
            }:
                raise AssignmentConflict("Snapshots incompatibles con el grupo")
            for order in assignment.route.orders:
                before = self._order_doc(order.id, session)
                current = decode(OrderRecord, before["data"])
                if (
                    current != snapshots[order.id]
                    or current.order != order
                    or order.status is not OrderStatus.CONFIRMED
                ):
                    raise AssignmentConflict("Un pedido cambió o ya tiene asignación")
                event = OrderEvent(
                    OrderStatus.CONFIRMED, OrderStatus.ASSIGNED, assignment.created_at
                )
                if event.occurred_at < current.events[-1].occurred_at:
                    raise ValueError("La asignación no puede preceder al historial")
                updated = OrderRecord(
                    replace(order, status=OrderStatus.ASSIGNED),
                    current.events + (event,),
                )
                cas(self.database.orders, before, updated, AssignmentConflict, session)
            cas(
                self.database.couriers,
                courier_doc,
                replace(courier, available=False),
                AssignmentConflict,
                session,
            )
            self.database.assignments.insert_one(
                document(assignment.id, assignment), session=session
            )
            return assignment

        try:
            return transaction(self.database, perform)
        except DuplicateKeyError:
            raise AssignmentConflict("Asignación o repartidor ya reservados") from None

    @mongo_errors
    def release(self, assignment_id, occurred_at):
        def perform(session):
            before = self._assignment_doc(assignment_id, session)
            assignment = decode(SimulatedAssignment, before["data"])
            if not assignment.active:
                raise AssignmentConflict("La asignación ya fue liberada")
            records = [
                decode(OrderRecord, self._order_doc(order.id, session)["data"])
                for order in assignment.route.orders
            ]
            if any(
                record.order.status is not OrderStatus.DELIVERED for record in records
            ):
                raise AssignmentConflict("Faltan entregas")
            OrderEvent(OrderStatus.PICKED_UP, OrderStatus.DELIVERED, occurred_at)
            if occurred_at < max(record.events[-1].occurred_at for record in records):
                raise ValueError("La liberación no puede preceder a las entregas")
            courier_doc = self.database.couriers.find_one(
                {"_id": assignment.courier.id}, session=session
            )
            courier = decode(Courier, courier_doc["data"])
            cas(
                self.database.couriers,
                courier_doc,
                replace(courier, available=True),
                AssignmentConflict,
                session,
            )
            return cas(
                self.database.assignments,
                before,
                replace(assignment, released_at=occurred_at),
                AssignmentConflict,
                session,
            )

        return transaction(self.database, perform)
