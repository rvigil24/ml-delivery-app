"""Ejecuta la demo HTTP y guarda datos reales de ejecución, sin credenciales."""

import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parents[1] / "examples/demo_delivery.json")
    parser.add_argument("--output", type=Path, default=Path("data/reports/presentation/demo_result.json"))
    args = parser.parse_args()
    payload = json.loads(args.input.read_text())
    prefix = "demo-" + uuid4().hex
    payload["business"]["id"] = prefix + "-business"
    payload["courier"]["id"] = prefix + "-courier"
    payload["order"]["id"] = prefix + "-order"
    payload["order"]["business_id"] = payload["business"]["id"]
    request = Request(args.url.rstrip("/") + "/demo/deliveries",
                      data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=120) as response:
            receipt = json.load(response)
    except HTTPError as error:
        raise SystemExit(f"Demo HTTP {error.code}: {error.read().decode()}") from None
    except URLError:
        raise SystemExit("No se pudo conectar: iniciar la API con DELIVERY_DEMO_ENABLED=1") from None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"input": payload, "result": receipt}, ensure_ascii=False, indent=2) + "\n")
    print("SIMULACIÓN completada:", receipt["order"]["order"]["id"])
    print("Duración estimada por el modelo:", receipt["quote"]["duration"]["minutes"], "min")
    print("Probabilidad estimada de retraso:", receipt["delivery_prediction"]["late_probability"])
    print("Tarifa de ejemplo:", receipt["quote"]["amounts"]["delivery_fee"], receipt["quote"]["amounts"]["currency"])
    print("Pedido:", receipt["order"]["order"]["status"], "; efectivo:", receipt["cash"]["events"][-1]["status"])
    print("Recibo para estudiar/exponer:", args.output)


if __name__ == "__main__":
    main()
