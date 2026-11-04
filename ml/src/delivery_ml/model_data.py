"""T13: contexto temporal conocido, variables cíclicas y partición sin futuro."""

import math
import pandas as pd


CONTEXT_COLUMNS = ["request_hour_utc", "request_weekday_utc"]
FEATURE_COLUMNS = ["request_hour_sin", "request_hour_cos", "request_weekday_sin", "request_weekday_cos"]
TARGET = "time_taken_min"
TRACE_COLUMNS = ["order_id", "source_waybill_id", "platform_order_time", "arrive_time"] + CONTEXT_COLUMNS
DEFAULT_TEST_START = "2022-10-23T00:00:00Z"


def temporal_features(context: pd.DataFrame) -> pd.DataFrame:
    """Transformación fija del calendario; no aprende estadísticas del dataset."""
    result = pd.DataFrame(index=context.index)
    for name, period, prefix in [(CONTEXT_COLUMNS[0], 24, "request_hour"),
                                 (CONTEXT_COLUMNS[1], 7, "request_weekday")]:
        values = pd.to_numeric(context[name], errors="raise")
        if (values.isna().any() or values.isin([float("inf"), float("-inf")]).any()
                or values.mod(1).ne(0).any() or values.lt(0).any() or values.ge(period).any()):
            raise ValueError(f"Contexto UTC fuera de dominio: {name}")
        angles = values * (2 * math.pi / period)
        result[prefix + "_sin"] = angles.map(math.sin)
        result[prefix + "_cos"] = angles.map(math.cos)
    return result[FEATURE_COLUMNS]


def model_xy(partition: pd.DataFrame):
    """Whitelist explícita: evita incluir IDs, llegada o target en predictores."""
    return partition[FEATURE_COLUMNS].copy(), partition[TARGET].copy()


def temporal_split(orders: pd.DataFrame, test_start: str = DEFAULT_TEST_START) -> dict:
    """Entrena solo con etiquetas observadas antes del inicio del test.

    Pedidos creados antes del corte pero aún abiertos se registran como purged;
    no se trasladan al test ni se eliminan mediante un máximo de duración.
    """
    cutoff = pd.Timestamp(test_start)
    if cutoff.tzinfo is None or pd.isna(cutoff) or cutoff.value % 1_000_000_000:
        raise ValueError("El corte debe tener zona horaria y segundos enteros")
    cutoff = cutoff.tz_convert("UTC")
    cutoff_seconds = cutoff.value // 1_000_000_000
    if orders.empty:
        raise ValueError("La cohorte está vacía")
    data = orders[TRACE_COLUMNS + [TARGET]].copy()
    for name in ("order_id", "source_waybill_id"):
        data[name] = data[name].astype("string")
        if data[name].isna().any() or data[name].str.strip().eq("").any() or data[name].duplicated().any():
            raise ValueError(f"Identificador ausente o duplicado: {name}")
    for name in ("platform_order_time", "arrive_time"):
        values = pd.to_numeric(data[name], errors="raise")
        if (values.isna().any() or values.isin([float("inf"), float("-inf")]).any()
                or values.mod(1).ne(0).any()):
            raise ValueError(f"Timestamp no entero finito: {name}")
        data[name] = values.astype("int64")
    target = pd.to_numeric(data[TARGET], errors="raise")
    if (target.isna().any() or target.isin([float("inf"), float("-inf")]).any()
            or target.le(0).any()
            or ((data["arrive_time"] - data["platform_order_time"]) / 60 - target).abs().gt(1e-9).any()):
        raise ValueError("Target incompatible con los eventos observados")
    data[TARGET] = target
    created = pd.to_datetime(data["platform_order_time"], unit="s", utc=True)
    if (created.dt.hour.ne(data[CONTEXT_COLUMNS[0]]) | created.dt.dayofweek.ne(data[CONTEXT_COLUMNS[1]])).any():
        raise ValueError("Contexto UTC no coincide con el timestamp de solicitud")
    features = temporal_features(data)
    data = pd.concat([data[TRACE_COLUMNS], features, data[[TARGET]]], axis=1)
    before = data["platform_order_time"].lt(cutoff_seconds)
    observed = data["arrive_time"].lt(cutoff_seconds)
    masks = {"train": before & observed, "test": ~before, "purged": before & ~observed}
    parts = {
        name: data.loc[mask].sort_values(["platform_order_time", "order_id"], kind="stable").reset_index(drop=True)
        for name, mask in masks.items()
    }
    if parts["train"].empty or parts["test"].empty:
        raise ValueError("El corte debe dejar entrenamiento y prueba no vacíos")
    assert sum(len(part) for part in parts.values()) == len(data)
    assert parts["train"]["arrive_time"].max() < cutoff_seconds <= parts["test"]["platform_order_time"].min()
    return parts
