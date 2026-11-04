"""Inicialización idempotente exclusiva del MongoDB local de Compose."""

import time

from pymongo import MongoClient
from pymongo.errors import OperationFailure, PyMongoError

from delivery.database.connection import MongoStorage


def main() -> None:
    # Fijo a la red local: no lee la URI privada de Atlas ni inicia réplicas cloud.
    with MongoClient("mongodb://mongo:27017/?directConnection=true",
                     serverSelectionTimeoutMS=2000) as client:
        try:
            client.admin.command("replSetInitiate", {
                "_id": "delivery-local",
                "members": [{"_id": 0, "host": "mongo:27017"}],
            })
        except OperationFailure as error:
            if error.code != 23:  # AlreadyInitialized; otros errores sí bloquean.
                raise
        for _ in range(60):
            try:
                if client.admin.command("hello").get("isWritablePrimary"):
                    break
            except PyMongoError:
                pass
            time.sleep(1)
        else:
            raise RuntimeError("MongoDB local no eligió un primario")
    storage = MongoStorage("mongodb://mongo:27017/?replicaSet=delivery-local", "delivery")
    try:
        storage.initialize_schema()
        storage.verify_schema()
    finally:
        storage.close()
    print("MongoDB local: réplica, validadores e índices preparados")


if __name__ == "__main__":
    main()
