"""Auditoría T07 de registros originales; produce agregados, no datos de entrenamiento."""

import argparse
from collections import Counter
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from statistics import mean, median
from typing import Iterable, Mapping, Optional


QUOTE_FIELDS = (
    "platform_order_time", "sender_lat", "sender_lng",
    "recipient_lat", "recipient_lng", "is_prebook",
)
TIME_FIELDS = (
    "platform_order_time", "order_push_time", "dispatch_time",
    "grab_time", "fetch_time", "arrive_time",
)
CONTEXT_FIELDS = ("dt", "da_id", "poi_id", "is_weekend")
FLAGS = ("is_prebook", "is_courier_grabbed", "is_weekend")
REQUIRED = tuple(dict.fromkeys(QUOTE_FIELDS + TIME_FIELDS + CONTEXT_FIELDS + FLAGS))
MISSING_TOKENS = {"", "nan", "null", "none", "na"}


@dataclass
class OrderAudit:
    signature: tuple
    context: tuple
    completion: Optional[tuple] = None
    completion_count: int = 0
    conflicting_quote: bool = False
    rows: int = 0


def duration_summary(seconds: list) -> dict:
    """Cuantiles de rango más próximo; ausencia se expresa con None."""
    if not seconds:
        return {"count": 0, "min_minutes": None, "median_minutes": None,
                "mean_minutes": None, "p95_minutes": None,
                "p99_minutes": None, "max_minutes": None}
    values = sorted(seconds)
    return {
        "count": len(values),
        "min_minutes": round(values[0] / 60, 4),
        "median_minutes": round(median(values) / 60, 4),
        "mean_minutes": round(mean(values) / 60, 4),
        "p95_minutes": round(values[math.ceil(0.95 * len(values)) - 1] / 60, 4),
        "p99_minutes": round(values[math.ceil(0.99 * len(values)) - 1] / 60, 4),
        "max_minutes": round(values[-1] / 60, 4),
    }


def audit_rows(rows: Iterable[Mapping[str, str]]) -> dict:
    """Audita sin corregir timestamps ni escoger un intento por su posición."""
    counts = Counter()
    missing = Counter()
    zeros = Counter()
    flags = {field: Counter() for field in FLAGS}
    changes = {field: set() for field in QUOTE_FIELDS + CONTEXT_FIELDS}
    orders = {}
    waybills = set()
    dates = Counter()
    raw_durations = {"0": [], "1": []}
    source_weekday_matches = Counter()
    coordinate_ranges = {}
    column_names = ()
    for row in rows:
        column_names = tuple(row)
        counts["rows"] += 1
        for field, value in row.items():
            if value is None or value.strip().lower() in MISSING_TOKENS:
                missing[field] += 1
        order_id, waybill_id = row.get("order_id"), row.get("waybill_id")
        if not order_id or not waybill_id:
            raise ValueError("Falta identificador de pedido o waybill")
        try:
            values = {field: int(row[field]) for field in REQUIRED}
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Campo obligatorio ausente o distinto de entero; no se corrige") from error
        if any(values[field] not in (0, 1) for field in FLAGS):
            raise ValueError("Indicador distinto de 0/1")
        if waybill_id in waybills:
            counts["duplicate_waybill_ids"] += 1
        waybills.add(waybill_id)
        for field in TIME_FIELDS:
            zeros[field] += values[field] == 0
        for field in ("sender_lat", "sender_lng", "recipient_lat", "recipient_lng"):
            value = values[field]
            if field not in coordinate_ranges:
                coordinate_ranges[field] = {"min": value, "max": value, "zero_count": 0}
            limits = coordinate_ranges[field]
            limits["min"] = min(limits["min"], value)
            limits["max"] = max(limits["max"], value)
            limits["zero_count"] += value == 0
        for field in FLAGS:
            flags[field][str(values[field])] += 1
        dates[str(values["dt"])] += 1
        signature = tuple(values[field] for field in QUOTE_FIELDS)
        context = tuple(values[field] for field in CONTEXT_FIELDS)
        if order_id not in orders:
            orders[order_id] = OrderAudit(signature, context)
        order = orders[order_id]
        order.rows += 1
        for index, field in enumerate(QUOTE_FIELDS):
            if order.signature[index] != signature[index]:
                changes[field].add(order_id)
                order.conflicting_quote = True
        for index, field in enumerate(CONTEXT_FIELDS):
            if order.context[index] != context[index]:
                changes[field].add(order_id)
        times = tuple(values[field] for field in TIME_FIELDS)
        if times[-1] > 0:
            counts["rows_with_arrival"] += 1
            order.completion_count += 1
            order.completion = times + (values["is_courier_grabbed"],)
            elapsed = times[-1] - times[0]
            if times[0] > 0 and elapsed > 0:
                raw_durations[str(values["is_prebook"])].append(elapsed)
            else:
                counts["invalid_completed_target"] += 1
            if times[0] > 0:
                for hours in (0, 8):
                    day = datetime.fromtimestamp(times[0], timezone(timedelta(hours=hours)))
                    source_weekday_matches[f"date_matches_utc_plus_{hours}"] += (
                        day.strftime("%Y%m%d") == str(values["dt"])
                    )

    excluded = Counter()
    selected_durations = []
    selected_dates = Counter()
    for order in orders.values():
        if order.conflicting_quote:
            excluded["conflicting_quote_fields"] += 1
        elif order.completion_count == 0:
            excluded["missing_completion"] += 1
        elif order.completion_count > 1:
            excluded["multiple_completions"] += 1
        elif order.signature[-1] == 1:
            excluded["prebook_separate_scope"] += 1
        else:
            times, grabbed = order.completion[:-1], order.completion[-1]
            if grabbed != 1 or any(value <= 0 for value in times):
                excluded["invalid_completed_timeline"] += 1
            elif any(left > right for left, right in zip(times, times[1:])) or times[-1] <= times[0]:
                excluded["invalid_completed_timeline"] += 1
            else:
                selected_durations.append(times[-1] - times[0])
                date = datetime.fromtimestamp(times[0], timezone.utc).strftime("%Y-%m-%d")
                selected_dates[date] += 1

    selected = len(selected_durations)
    assert selected + sum(excluded.values()) == len(orders)
    blockers = []
    if not selected:
        blockers.append("No hay pedidos elegibles con duración observada válida")
    if counts["duplicate_waybill_ids"]:
        blockers.append("Hay waybill_id repetidos que requieren revisión")
    return {
        "decision": "BLOQUEADO" if blockers else "APROBADO_CON_CONDICIONES",
        "blockers": blockers,
        "target": {
            "definition": "(arrive_time - platform_order_time) / 60",
            "unit": "minutes", "prediction_time": "order_creation",
            "scope": "Pedidos inmediatos, una entrega inequívoca y campos de cotización estables",
        },
        "raw": {
            "rows": counts["rows"], "distinct_orders": len(orders),
            "distinct_waybills": len(waybills),
            "duplicate_waybill_ids": counts["duplicate_waybill_ids"],
            "missing_counts": {field: missing[field] for field in column_names},
            "coordinate_ranges_raw_units": coordinate_ranges,
            "zero_timestamps": dict(zeros), "flags": {key: dict(value) for key, value in flags.items()},
            "dates_dt": dict(sorted(dates.items())),
            "rows_with_arrival": counts["rows_with_arrival"],
            "invalid_completed_target": counts["invalid_completed_target"],
            "orders_with_repeated_attempts": sum(order.rows > 1 for order in orders.values()),
            "orders_without_positive_completion": sum(order.completion_count == 0 for order in orders.values()),
            "orders_with_multiple_completions": sum(order.completion_count > 1 for order in orders.values()),
            "orders_with_conflicting_quote_fields": sum(order.conflicting_quote for order in orders.values()),
            "orders_changed_by_field": {key: len(value) for key, value in changes.items()},
            "completed_dates_comparison": dict(source_weekday_matches),
            "duration_by_prebook": {key: duration_summary(value) for key, value in raw_durations.items()},
        },
        "cohort_proposal": {
            "eligible_orders": selected,
            "excluded_orders_by_first_reason": dict(excluded),
            "rows_not_represented_in_cohort": counts["rows"] - selected,
            "creation_dates_utc": dict(sorted(selected_dates.items())),
            "duration": duration_summary(selected_durations),
            "materialized": False,
        },
        "conditions": [
            "T08 deberá implementar los criterios auditados sin modificar el original",
            "Mantener reservas y pedidos ambiguos fuera de la cohorte inmediata propuesta",
            "No recortar duraciones mediante límites comerciales o estadísticos inventados",
            "Usar solo información disponible al crear el pedido; no resultados de asignación",
            "Confirmar unidades/anonimización antes de usar coordenadas como grados o distancias",
            "Derivar contexto de solicitud desde su timestamp UTC; dt no equivale siempre a ese día",
            "Separar grupos/tiempos al evaluar; ocho días no validan generalización local",
        ],
    }


def main() -> None:
    from acquire_meituan import CSV_NAME, DEFAULT_OUTPUT, EXPECTED, REVISION, verify_file

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output", type=Path, default=root / "data" / "reports" / "meituan" / REVISION / "t07_audit.json")
    args = parser.parse_args()
    source = args.dataset / CSV_NAME
    try:
        integrity = verify_file(source, *EXPECTED[CSV_NAME])
        with source.open(encoding="utf-8-sig", newline="") as stream:
            report = audit_rows(csv.DictReader(stream))
    except (OSError, ValueError) as error:
        parser.exit(1, f"Auditoría no completada: {error}\n")
    report["source"] = {"revision": REVISION, "file": CSV_NAME, **integrity}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Informe agregado: {args.output}")
    print(f"Decisión: {report['decision']}; pedidos elegibles: {report['cohort_proposal']['eligible_orders']}")
    print("No se creó un dataset limpio ni se entrenó un modelo.")
    if report["decision"] == "BLOQUEADO":
        parser.exit(2, "No avanzar a tareas dependientes hasta resolver los bloqueos.\n")


if __name__ == "__main__":
    main()
