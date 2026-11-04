"""Conexión MongoDB y preparación/verificación del esquema."""

from pymongo import MongoClient

from delivery.domain.catalogs import StorageUnavailable
from delivery.domain.models import Business, Courier

from .cash import MongoCashRepository
from .catalogs import MongoCatalog
from .documents import COLLECTIONS, collection_validator, mongo_errors
from .orders import MongoDispatchRepository


class MongoStorage:
    @mongo_errors
    def __init__(self, uri, database_name):
        if (
            not uri
            or not database_name
            or database_name in ("admin", "config", "local")
        ):
            raise StorageUnavailable("Se requieren URI y base de aplicación explícitas")
        self.client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            appname="ml-delivery-app",
        )
        try:
            hello = self.client.admin.command("hello")
            if not hello.get("setName") and hello.get("msg") != "isdbgrid":
                raise StorageUnavailable(
                    "MongoDB debe soportar transacciones: usar replica set o Atlas"
                )
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
                self.database.create_collection(
                    name,
                    validator=validator,
                    validationLevel="strict",
                    validationAction="error",
                )
            else:
                info = next(self.database.list_collections(filter={"name": name}))
                if info.get("options", {}).get("validator") != validator:
                    raise StorageUnavailable(
                        "Esquema existente incompatible; requiere migración explícita"
                    )
        self.database.orders.create_index(
            [("data.order.business_id", 1), ("data.order.status", 1)]
        )
        self.database.assignments.create_index(
            "data.courier.id",
            unique=True,
            partialFilterExpression={"data.released_at": None},
            name="one_active_assignment_per_courier",
        )
        self.database.assignments.create_index("data.route.orders.id")

    @mongo_errors
    def verify_schema(self):
        """La API no debe autocrear colecciones sin validadores si se omitió el bootstrap."""
        existing = {info["name"]: info for info in self.database.list_collections()}
        for name, kind in COLLECTIONS:
            options = existing.get(name, {}).get("options", {})
            if (
                options.get("validator") != collection_validator(kind)
                or options.get("validationLevel", "strict") != "strict"
                or options.get("validationAction", "error") != "error"
            ):
                raise StorageUnavailable(
                    "Preparar o migrar el esquema antes de utilizar la API"
                )
        if (
            "data.order.business_id_1_data.order.status_1"
            not in self.database.orders.index_information()
        ):
            raise StorageUnavailable("Falta índice de pedidos")
        indexes = self.database.assignments.index_information()
        active = indexes.get("one_active_assignment_per_courier", {})
        if (
            not active.get("unique")
            or active.get("partialFilterExpression") != {"data.released_at": None}
            or "data.route.orders.id_1" not in indexes
        ):
            raise StorageUnavailable("Faltan índices de asignación")

    def close(self):
        self.client.close()
