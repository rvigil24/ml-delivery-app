"""Codificación de documentos, validadores y actualizaciones atómicas."""

from functools import wraps

from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from delivery.database.codec import encode, schema_for
from delivery.models.assignments import SimulatedAssignment
from delivery.models.cash import CashRecord
from delivery.models.catalogs import StorageUnavailable
from delivery.models.entities import Business, Courier
from delivery.models.order_lifecycle import OrderRecord

COLLECTIONS = (
    ("businesses", Business),
    ("couriers", Courier),
    ("orders", OrderRecord),
    ("assignments", SimulatedAssignment),
    ("cash", CashRecord),
)


def mongo_errors(function):
    @wraps(function)
    def call(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except PyMongoError:
            raise StorageUnavailable(
                "MongoDB no disponible o rechaza la operación"
            ) from None

    return call


def transaction(database, callback):
    with database.client.start_session() as session:
        return session.with_transaction(
            callback,
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )


def document(identifier, value, version=0):
    return {"_id": identifier, "version": version, "data": encode(value)}


def collection_validator(kind):
    return {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["_id", "version", "data"],
            "additionalProperties": False,
            "properties": {
                "_id": {"bsonType": "string", "minLength": 1},
                "version": {"bsonType": ["int", "long"], "minimum": 0},
                "data": schema_for(kind),
            },
        }
    }


def cas(collection, before, value, conflict, session=None):
    updated = document(before["_id"], value, before["version"] + 1)
    result = collection.replace_one(
        {"_id": before["_id"], "version": before["version"]}, updated, session=session
    )
    if result.matched_count != 1:
        raise conflict("El registro cambió; consultar antes de reintentar")
    return value
