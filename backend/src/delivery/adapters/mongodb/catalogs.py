"""Repositorios de negocios y repartidores."""

from pymongo.errors import DuplicateKeyError

from delivery.domain.catalogs import CatalogConflict
from delivery.domain.models import Business, Courier

from ..mongo_codec import decode
from .documents import cas, document, mongo_errors, transaction


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
        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or not 1 <= limit <= 100
        ):
            raise ValueError("limit fuera de rango")
        return tuple(
            decode(self.kind, doc["data"])
            for doc in self.collection.find().sort("_id", 1).limit(limit)
        )

    @mongo_errors
    def all(self):
        """Lectura del catálogo pequeño para ordenar cercanía antes de paginar."""
        return tuple(
            decode(self.kind, doc["data"])
            for doc in self.collection.find().sort("_id", 1)
        )

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
            elif entity is None and self.database.orders.find_one(
                {"data.order.business_id": identifier}, session=session
            ):
                raise CatalogConflict("Negocio referenciado por pedidos")
            if entity is None:
                self.collection.delete_one(
                    {"_id": identifier, "version": before["version"]}, session=session
                )
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
