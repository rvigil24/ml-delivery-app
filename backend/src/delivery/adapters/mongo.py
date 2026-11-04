"""T32: persistencia operativa con CAS y transacciones reales de MongoDB."""

from dataclasses import replace
from functools import wraps
from typing import Tuple

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from delivery.domain.assignments import AssignmentConflict, AssignmentNotFound, CourierNotFound, SimulatedAssignment
from delivery.domain.cash import CashConflict, CashEvent, CashNotFound, CashRecord, CashStatus, validate_cash_transition, validate_full_payment
from delivery.domain.catalogs import CatalogConflict, StorageUnavailable
from delivery.domain.models import Business, Courier, OrderStatus
from delivery.domain.order_lifecycle import BusinessNotFound, DuplicateOrder, OrderConflict, OrderEvent, OrderNotFound, OrderRecord, validate_transition
from delivery.domain.routing import StopType
from .mongo_codec import decode, encode, schema_for


def mongo_errors(function):
    @wraps(function)
    def call(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except PyMongoError:
            raise StorageUnavailable("MongoDB no disponible o rechaza la operación") from None
    return call


def transaction(database, callback):
    with database.client.start_session() as session:
        return session.with_transaction(callback, read_concern=ReadConcern("snapshot"),
                                        write_concern=WriteConcern("majority"))


def document(identifier, value, version=0):
    return {"_id": identifier, "version": version, "data": encode(value)}


COLLECTIONS = (("businesses", Business), ("couriers", Courier), ("orders", OrderRecord),
               ("assignments", SimulatedAssignment), ("cash", CashRecord))


def collection_validator(kind):
    return {"$jsonSchema": {"bsonType": "object", "required": ["_id", "version", "data"],
        "additionalProperties": False, "properties": {"_id": {"bsonType": "string", "minLength": 1},
            "version": {"bsonType": ["int", "long"], "minimum": 0}, "data": schema_for(kind)}}}


def cas(collection, before, value, conflict, session=None):
    updated = document(before["_id"], value, before["version"] + 1)
    result = collection.replace_one({"_id": before["_id"], "version": before["version"]}, updated, session=session)
    if result.matched_count != 1:
        raise conflict("El registro cambió; consultar antes de reintentar")
    return value


class MongoCatalog:
    def __init__(self, database, kind):
        if kind not in (Business, Courier):
            raise ValueError("Catálogo no soportado")
        self.database, self.kind = database, kind
        self.collection = database.businesses if kind is Business else database.couriers

    @mongo_errors
    def get(self, identifier):
        doc = self.collection.find_one({"_id": identifier})
        return decode(self.kind, doc["data"]) if doc else None

    @mongo_errors
    def list(self, limit):
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit fuera de rango")
        return tuple(decode(self.kind, doc["data"]) for doc in self.collection.find().sort("_id", 1).limit(limit))

    @mongo_errors
    def all(self):
        """Lectura del catálogo pequeño para ordenar cercanía antes de paginar."""
        return tuple(decode(self.kind, doc["data"]) for doc in self.collection.find().sort("_id", 1))

    @mongo_errors
    def create(self, entity):
        if not isinstance(entity, self.kind):
            raise ValueError("Tipo de entidad incompatible")
        try:
            self.collection.insert_one(document(entity.id, entity))
        except DuplicateKeyError:
            raise CatalogConflict("ID de catálogo duplicado") from None
        return entity

    def _change(self, identifier, expected, entity=None):
        def perform(session):
            before = self.collection.find_one({"_id": identifier}, session=session)
            if before is None or decode(self.kind, before["data"]) != expected:
                raise CatalogConflict("El catálogo cambió")
            if self.kind is Courier:
                query = {"data.courier.id": identifier}
                if entity is not None:
                    query["data.released_at"] = None
                if self.database.assignments.find_one(query, session=session):
                    raise CatalogConflict("Repartidor referenciado por una asignación")
            elif entity is None and self.database.orders.find_one({"data.order.business_id": identifier}, session=session):
                raise CatalogConflict("Negocio referenciado por pedidos")
            if entity is None:
                self.collection.delete_one({"_id": identifier, "version": before["version"]}, session=session)
                return None
            return cas(self.collection, before, entity, CatalogConflict, session)
        return transaction(self.database, perform)

    @mongo_errors
    def update(self, entity, expected):
        if not isinstance(entity, self.kind) or entity.id != expected.id:
            raise ValueError("Entidad o ID incompatible")
        return self._change(entity.id, expected, entity)

    @mongo_errors
    def delete(self, identifier, expected):
        return self._change(identifier, expected)


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
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit fuera de rango")
        return tuple(decode(OrderRecord, doc["data"]) for doc in self.database.orders.find().sort("_id", 1).limit(limit))

    @mongo_errors
    def list_for_business(self, business_id, limit):
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit fuera de rango")
        query = {"data.order.business_id": business_id}
        return tuple(decode(OrderRecord, doc["data"]) for doc in
                     self.database.orders.find(query).sort("_id", 1).limit(limit))

    @mongo_errors
    def create(self, order, occurred_at):
        if order.status is not OrderStatus.REQUESTED:
            raise OrderConflict("Un pedido nuevo debe estar solicitado")
        record = OrderRecord(order, (OrderEvent(None, order.status, occurred_at),))
        def perform(session):
            business = self.database.businesses.find_one({"_id": order.business_id}, session=session)
            if business is None:
                raise BusinessNotFound(order.business_id)
            if decode(Business, business["data"]).location != order.origin:
                raise ValueError("El origen debe coincidir con el negocio")
            # Escribir el negocio evita carrera entre registrar pedido y borrar/editar su referencia.
            self.database.businesses.update_one({"_id": order.business_id}, {"$inc": {"version": 1}}, session=session)
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
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit fuera de rango")
        query = {"data.courier.id": courier_id}
        return tuple(decode(SimulatedAssignment, doc["data"]) for doc in
                     self.database.assignments.find(query).sort("_id", 1).limit(limit))

    def _progress(self, order_id, target, session):
        doc = self.database.assignments.find_one({"data.route.orders.id": order_id, "data.released_at": None}, session=session)
        if doc is None:
            raise AssignmentConflict("El pedido no tiene asignación activa")
        assignment = decode(SimulatedAssignment, doc["data"])
        for stop in assignment.route.stops:
            record = decode(OrderRecord, self._order_doc(stop.order_id, session)["data"])
            done = record.order.status is OrderStatus.DELIVERED or (
                stop.kind is StopType.PICKUP and record.order.status is OrderStatus.PICKED_UP)
            if not done:
                next_status = OrderStatus.PICKED_UP if stop.kind is StopType.PICKUP else OrderStatus.DELIVERED
                if stop.order_id != order_id or next_status is not target:
                    raise AssignmentConflict("La transición no corresponde a la siguiente parada")
                return doc
        raise AssignmentConflict("La ruta ya fue completada")

    @mongo_errors
    def validate_progress(self, order_id, target):
        transaction(self.database, lambda session: self._progress(order_id, target, session))

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
                self.database.assignments.update_one({"_id": assignment["_id"]}, {"$inc": {"version": 1}}, session=session)
            updated = OrderRecord(replace(current.order, status=target), current.events + (event,))
            return cas(self.database.orders, before, updated, OrderConflict, session)
        return transaction(self.database, perform)

    @mongo_errors
    def commit_assignment(self, assignment, expected: Tuple[OrderRecord, ...]):
        def perform(session):
            if not assignment.active or self.database.assignments.find_one({"_id": assignment.id}, session=session):
                raise AssignmentConflict("Asignación duplicada o cerrada")
            courier_doc = self.database.couriers.find_one({"_id": assignment.courier.id}, session=session)
            if courier_doc is None:
                raise CourierNotFound(assignment.courier.id)
            courier = decode(Courier, courier_doc["data"])
            if courier != assignment.courier or not courier.approved or not courier.available:
                raise AssignmentConflict("El repartidor cambió o no está disponible")
            snapshots = {record.order.id: record for record in expected}
            if len(snapshots) != len(expected) or set(snapshots) != {order.id for order in assignment.route.orders}:
                raise AssignmentConflict("Snapshots incompatibles con el grupo")
            for order in assignment.route.orders:
                before = self._order_doc(order.id, session)
                current = decode(OrderRecord, before["data"])
                if current != snapshots[order.id] or current.order != order or order.status is not OrderStatus.CONFIRMED:
                    raise AssignmentConflict("Un pedido cambió o ya tiene asignación")
                event = OrderEvent(OrderStatus.CONFIRMED, OrderStatus.ASSIGNED, assignment.created_at)
                if event.occurred_at < current.events[-1].occurred_at:
                    raise ValueError("La asignación no puede preceder al historial")
                updated = OrderRecord(replace(order, status=OrderStatus.ASSIGNED), current.events + (event,))
                cas(self.database.orders, before, updated, AssignmentConflict, session)
            cas(self.database.couriers, courier_doc, replace(courier, available=False), AssignmentConflict, session)
            self.database.assignments.insert_one(document(assignment.id, assignment), session=session)
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
            records = [decode(OrderRecord, self._order_doc(order.id, session)["data"]) for order in assignment.route.orders]
            if any(record.order.status is not OrderStatus.DELIVERED for record in records):
                raise AssignmentConflict("Faltan entregas")
            OrderEvent(OrderStatus.PICKED_UP, OrderStatus.DELIVERED, occurred_at)
            if occurred_at < max(record.events[-1].occurred_at for record in records):
                raise ValueError("La liberación no puede preceder a las entregas")
            courier_doc = self.database.couriers.find_one({"_id": assignment.courier.id}, session=session)
            courier = decode(Courier, courier_doc["data"])
            cas(self.database.couriers, courier_doc, replace(courier, available=True), AssignmentConflict, session)
            return cas(self.database.assignments, before, replace(assignment, released_at=occurred_at), AssignmentConflict, session)
        return transaction(self.database, perform)


class MongoCashRepository:
    def __init__(self, database):
        self.collection = database.cash

    @mongo_errors
    def get(self, order_id):
        doc = self.collection.find_one({"_id": order_id})
        if doc is None:
            raise CashNotFound(order_id)
        return decode(CashRecord, doc["data"])

    @mongo_errors
    def create(self, record):
        if len(record.events) != 1 or record.events[0].previous_status is not None or record.status is not CashStatus.PENDING:
            raise CashConflict("Se requiere un evento inicial pendiente")
        try:
            self.collection.insert_one(document(record.order_id, record))
        except DuplicateKeyError:
            raise CashConflict("Efectivo duplicado para el pedido") from None
        return record

    @mongo_errors
    def transition(self, order_id, expected, target, currency, amount, occurred_at):
        validate_cash_transition(expected, target)
        before = self.collection.find_one({"_id": order_id})
        if before is None:
            raise CashNotFound(order_id)
        current = decode(CashRecord, before["data"])
        if current.status is not expected:
            raise CashConflict("El estado contable cambió")
        validate_full_payment(current, currency, amount)
        event = CashEvent(expected, target, occurred_at)
        if occurred_at < current.events[-1].occurred_at:
            raise ValueError("Un evento no puede preceder al historial")
        return cas(self.collection, before, replace(current, events=current.events + (event,)), CashConflict)


class MongoStorage:
    @mongo_errors
    def __init__(self, uri, database_name):
        if not uri or not database_name or database_name in ("admin", "config", "local"):
            raise StorageUnavailable("Se requieren URI y base de aplicación explícitas")
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000,
                                  appname="ml-delivery-app")
        try:
            hello = self.client.admin.command("hello")
            if not hello.get("setName") and hello.get("msg") != "isdbgrid":
                raise StorageUnavailable("MongoDB debe soportar transacciones: usar replica set o Atlas")
            self.database = self.client[database_name]
            self.database.command("ping")
        except Exception:
            self.client.close()
            raise
        self.businesses = MongoCatalog(self.database, Business)
        self.couriers = MongoCatalog(self.database, Courier)
        self.orders = MongoDispatchRepository(self.database)
        self.cash = MongoCashRepository(self.database)

    @mongo_errors
    def initialize_schema(self):
        """Paso explícito; nunca borrar colecciones ni migrar validadores existentes silenciosamente."""
        existing = self.database.list_collection_names()
        for name, kind in COLLECTIONS:
            validator = collection_validator(kind)
            if name not in existing:
                self.database.create_collection(name, validator=validator, validationLevel="strict", validationAction="error")
            else:
                info = next(self.database.list_collections(filter={"name": name}))
                if info.get("options", {}).get("validator") != validator:
                    raise StorageUnavailable("Esquema existente incompatible; requiere migración explícita")
        self.database.orders.create_index([("data.order.business_id", 1), ("data.order.status", 1)])
        self.database.assignments.create_index("data.courier.id", unique=True,
            partialFilterExpression={"data.released_at": None}, name="one_active_assignment_per_courier")
        self.database.assignments.create_index("data.route.orders.id")

    @mongo_errors
    def verify_schema(self):
        """La API no debe autocrear colecciones sin validadores si se omitió el bootstrap."""
        existing = {info["name"]: info for info in self.database.list_collections()}
        for name, kind in COLLECTIONS:
            options = existing.get(name, {}).get("options", {})
            if (options.get("validator") != collection_validator(kind)
                    or options.get("validationLevel", "strict") != "strict"
                    or options.get("validationAction", "error") != "error"):
                raise StorageUnavailable("Preparar o migrar el esquema antes de utilizar la API")
        if "data.order.business_id_1_data.order.status_1" not in self.database.orders.index_information():
            raise StorageUnavailable("Falta índice de pedidos")
        indexes = self.database.assignments.index_information()
        active = indexes.get("one_active_assignment_per_courier", {})
        if (not active.get("unique") or active.get("partialFilterExpression") != {"data.released_at": None}
                or "data.route.orders.id_1" not in indexes):
            raise StorageUnavailable("Faltan índices de asignación")

    def close(self):
        self.client.close()


if __name__ == "__main__":
    import os
    storage = MongoStorage(os.environ.get("MONGODB_URI"), os.environ.get("MONGODB_DATABASE"))
    try:
        storage.initialize_schema()
        print("Esquemas e índices de la base configurada preparados")
    finally:
        storage.close()
