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
    parser.add_argument("--input", type=Path)
    parser.add_argument(
        "--grouped", action="store_true", help="Ejecutar dos pedidos en una sola ruta"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
    )
    args = parser.parse_args()
    args.output = args.output or Path(
        "data/reports/presentation/demo_grouped_result.json"
        if args.grouped
        else "data/reports/presentation/demo_result.json"
    )
    source = args.input or Path(__file__).resolve().parents[1] / (
        "examples/demo_grouped_delivery.json"
        if args.grouped
        else "examples/demo_delivery.json"
    )
    payload = json.loads(source.read_text())
    prefix = "demo-" + uuid4().hex
    payload["business"]["id"] = prefix + "-business"
    payload["courier"]["id"] = prefix + "-courier"
    if args.grouped:
        costs, loads = {}, {}
        for index, order in enumerate(payload["orders"], 1):
            previous = order["id"]
            order["id"] = prefix + f"-order-{index}"
            order["business_id"] = payload["business"]["id"]
            costs[order["id"]] = payload["per_order_costs"][previous]
            loads[order["id"]] = payload["loads_kg"][previous]
        payload["per_order_costs"], payload["loads_kg"] = costs, loads
    else:
        payload["order"]["id"] = prefix + "-order"
        payload["order"]["business_id"] = payload["business"]["id"]
    request = Request(
        args.url.rstrip("/")
        + ("/demo/group-deliveries" if args.grouped else "/demo/deliveries"),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=120) as response:
            receipt = json.load(response)
    except HTTPError as error:
        raise SystemExit(f"Demo HTTP {error.code}: {error.read().decode()}") from None
    except URLError:
        raise SystemExit(
            "No se pudo conectar: iniciar la API con DELIVERY_DEMO_ENABLED=1"
        ) from None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"input": payload, "result": receipt}, ensure_ascii=False, indent=2)
        + "\n"
    )
    records = receipt.get("orders") or [receipt["order"]]
    cash_records = (
        receipt["cash"] if isinstance(receipt["cash"], list) else [receipt["cash"]]
    )
    if (
        not all(record["order"]["status"] == "entregado" for record in records)
        or not all(
            row["events"][-1]["status"] == "entregado_al_operador"
            for row in cash_records
        )
        or not receipt["courier"]["available"]
        or receipt["assignment"]["released_at"] is None
    ):
        raise SystemExit(
            "La demo no confirmó todas las entregas y el efectivo: revisar recibo"
        )
    print(
        "SIMULACIÓN completada:",
        len(records),
        "pedido(s), efectivo al operador, repartidor disponible",
    )
    predictions = receipt.get("delivery_predictions") or {
        records[0]["order"]["id"]: receipt["delivery_prediction"]
    }
    for identifier, prediction in predictions.items():
        print(
            identifier,
            "— ETA:",
            round(prediction["estimated_minutes"], 1),
            "min; distancia:",
            round(prediction["distance_km"], 2),
            "km; riesgo:",
            round(prediction["late_probability"] * 100, 1),
            "%",
        )
    if "comparison" in receipt:
        comparison = receipt["comparison"]
        print(
            "Costo individual / agrupado:",
            comparison["individual_totals"]["total_cost"],
            "/",
            comparison["grouped"]["amounts"]["total_cost"],
            comparison["individual_totals"]["currency"],
        )
    print("Recibo para estudiar/exponer:", args.output)


if __name__ == "__main__":
    main()
