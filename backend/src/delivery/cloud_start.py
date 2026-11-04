"""Arranque cloud: esperar el esquema Mongo existente antes de iniciar la API."""

import json
import os
from pathlib import Path
import sys
import time
from typing import Optional
import urllib.request

from delivery.adapters.mongo import MongoStorage
from delivery.domain.catalogs import StorageUnavailable


WAIT_STATE = Path("/tmp/delivery-cloud-start.json")


def healthcheck() -> bool:
    """Vitalidad durante espera; después, salud del proceso HTTP, no readiness."""
    try:
        if WAIT_STATE.exists():
            state = json.loads(WAIT_STATE.read_text())
            os.kill(int(state["pid"]), 0)
            return state["deadline"] is None or time.monotonic() < state["deadline"]
        with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=2) as response:
            return response.status == 200
    except (OSError, ValueError, KeyError, TypeError):
        return False


def wait_for_mongo(uri: str, database: str, deadline: Optional[float]) -> None:
    """Solo lecturas: no crear colecciones, índices ni datos de demostración."""
    while deadline is None or time.monotonic() < deadline:
        storage = None
        try:
            storage = MongoStorage(uri, database)
            storage.verify_schema()
            return
        except StorageUnavailable:
            # No imprimir excepciones: podrían contener URI, hosts o credenciales.
            print("Esperando acceso y esquema MongoDB; revisar IP permitida/configuración.", flush=True)
        finally:
            if storage is not None:
                storage.close()
        remaining = 5 if deadline is None else deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(5, remaining))
    raise TimeoutError("MongoDB no estuvo disponible dentro del plazo de arranque")


def main() -> int:
    if sys.argv[1:] == ["--healthcheck"]:
        return 0 if healthcheck() else 1
    try:
        uri = os.environ["MONGODB_URI"]
        database = os.environ["MONGODB_DATABASE"]
        timeout = int(os.environ.get("DELIVERY_CLOUD_START_TIMEOUT_SECONDS", "900"))
        if not uri or not database or not 0 <= timeout <= 3600:
            raise ValueError
    except (KeyError, ValueError):
        print("Configurar URI/base MongoDB y plazo 0 (sin límite) o entre 1 y 3600 segundos.", flush=True)
        return 2

    deadline = time.monotonic() + timeout if timeout else None
    WAIT_STATE.write_text(json.dumps({"pid": os.getpid(), "deadline": deadline}))
    WAIT_STATE.chmod(0o600)
    try:
        wait_for_mongo(uri, database, deadline)
    except (TimeoutError, ValueError):
        print("Arranque cancelado: revisar acceso, credenciales y esquema MongoDB.", flush=True)
        return 1
    finally:
        WAIT_STATE.unlink(missing_ok=True)
    print("Esquema MongoDB verificado; iniciando API.", flush=True)
    # Reemplazar proceso conserva señales de parada y la red/IP de la tarea.
    os.execvp("uvicorn", ["uvicorn", "delivery.api.app:app", "--host", "0.0.0.0", "--port", "8000"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
