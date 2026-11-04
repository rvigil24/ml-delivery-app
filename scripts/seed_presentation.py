"""Carga únicamente fixtures SIMULADAS para exposición mediante la API existente."""

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parents[1] / "examples/exposicion.json")
    parser.add_argument("--apply", action="store_true", help="Crear fixtures faltantes; sin esta opción solo muestra resumen.")
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    if data.get("simulated") is not True:
        raise SystemExit("El archivo debe estar marcado como simulado.")
    for collection in ("businesses", "couriers", "orders"):
        for item in data[collection]:
            if not item["id"].startswith("demo-expo-"):
                raise SystemExit("Solo se permiten identificadores demo-expo-.")
    if not args.apply:
        print("SIMULACIÓN:", {k: len(data[k]) for k in ("businesses", "couriers", "orders")})
        print("Agregar --apply para crear los registros faltantes. No contiene tiempos o resultados ML inventados.")
        return

    def request(path, method="GET", body=None):
        req = Request(args.url.rstrip("/") + path,
                      data=json.dumps(body).encode() if body is not None else None,
                      headers={"Content-Type": "application/json"}, method=method)
        with urlopen(req, timeout=30) as response:
            return json.load(response)

    for collection in ("businesses", "couriers", "orders"):
        created = existing = 0
        for item in data[collection]:
            try:
                current = request("/" + collection + "/" + item["id"])
            except HTTPError as error:
                if error.code != 404:
                    raise SystemExit("No se pudo consultar " + collection + "; HTTP " + str(error.code)) from None
                request("/" + collection, "POST", item)
                created += 1
            else:
                current = current.get("order", current)
                if any(current.get(k) != v for k, v in item.items()):
                    raise SystemExit("Fixture existente diferente: " + item["id"] + ". No se sobrescribe.")
                existing += 1
        print(collection + ":", created, "creados,", existing, "existentes; SIMULADOS.")
    print("Pedidos solicitados para exposición. No se cotizó, asignó o cobró nada.")


if __name__ == "__main__":
    main()
