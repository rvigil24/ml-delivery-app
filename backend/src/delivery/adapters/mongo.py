"""Imports compatibles; implementación en adapters.mongodb."""

from .mongodb.connection import MongoStorage
from .mongodb.catalogs import MongoCatalog
from .mongodb.orders import MongoDispatchRepository
from .mongodb.cash import MongoCashRepository
from .mongodb.documents import mongo_errors, transaction, document, collection_validator, cas, COLLECTIONS

if __name__ == "__main__":
    import os
    storage = MongoStorage(os.environ.get("MONGODB_URI"), os.environ.get("MONGODB_DATABASE"))
    try:
        storage.initialize_schema()
        print("Esquemas e índices de la base configurada preparados")
    finally:
        storage.close()
