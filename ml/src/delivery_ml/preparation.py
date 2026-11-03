"""Preparación Pandas de la cohorte inmediata delimitada en T07."""

import pandas as pd


QUOTE_FIELDS = [
    "platform_order_time", "sender_lat", "sender_lng",
    "recipient_lat", "recipient_lng", "is_prebook",
]
TIME_FIELDS = [
    "platform_order_time", "order_push_time", "dispatch_time",
    "grab_time", "fetch_time", "arrive_time",
]
NUMERIC_FIELDS = list(dict.fromkeys(QUOTE_FIELDS + TIME_FIELDS + ["is_courier_grabbed"]))
REQUIRED_FIELDS = ["order_id", "waybill_id"] + NUMERIC_FIELDS


def prepare_orders(raw: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una fila por pedido elegible, sin modificar la entrada."""
    missing = set(REQUIRED_FIELDS) - set(raw.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {sorted(missing)}")
    data = raw[REQUIRED_FIELDS].copy()
    for name in ("order_id", "waybill_id"):
        data[name] = data[name].astype("string")
        if data[name].isna().any() or data[name].str.strip().eq("").any():
            raise ValueError(f"Identificador ausente: {name}")
    if data["waybill_id"].duplicated().any():
        raise ValueError("waybill_id duplicado; revisar antes de preparar")
    numeric = data[NUMERIC_FIELDS].apply(pd.to_numeric, errors="raise")
    if (
        numeric.isna().any().any()
        or numeric.isin([float("inf"), float("-inf")]).any().any()
        or numeric.mod(1).ne(0).any().any()
    ):
        raise ValueError("Se requieren enteros finitos; no se truncan timestamps")
    data[NUMERIC_FIELDS] = numeric.astype("int64")
    if not data[["is_prebook", "is_courier_grabbed"]].isin([0, 1]).all().all():
        raise ValueError("Indicador distinto de 0/1")

    # Se detectan cambios sobre todos los intentos, antes de filtrar completados.
    unstable = data.groupby("order_id")[QUOTE_FIELDS].nunique(dropna=False).gt(1).any(axis=1)
    completed = data.loc[data["arrive_time"].gt(0)].copy()
    completion_count = completed.groupby("order_id")["waybill_id"].transform("size")
    chronology = completed[TIME_FIELDS].diff(axis=1).iloc[:, 1:].ge(0).all(axis=1)
    valid = (
        ~completed["order_id"].isin(unstable.index[unstable])
        & completion_count.eq(1)
        & completed["is_prebook"].eq(0)
        & completed["is_courier_grabbed"].eq(1)
        & completed[TIME_FIELDS].gt(0).all(axis=1)
        & chronology
        & completed["arrive_time"].gt(completed["platform_order_time"])
    )
    selected = completed.loc[valid].sort_values("order_id", kind="stable").copy()
    created = pd.to_datetime(selected["platform_order_time"], unit="s", utc=True)
    selected["time_taken_min"] = (selected["arrive_time"] - selected["platform_order_time"]) / 60
    selected["request_hour_utc"] = created.dt.hour
    selected["request_weekday_utc"] = created.dt.dayofweek  # lunes=0, domingo=6
    columns = [
        "order_id", "waybill_id", "platform_order_time", "arrive_time",
        "request_hour_utc", "request_weekday_utc", "time_taken_min",
        "sender_lat", "sender_lng", "recipient_lat", "recipient_lng",
    ]
    result = selected[columns].rename(columns={
        "waybill_id": "source_waybill_id",
        **{name: name + "_raw" for name in ("sender_lat", "sender_lng", "recipient_lat", "recipient_lng")},
    }).reset_index(drop=True)
    if not result["order_id"].is_unique:
        raise ValueError("La salida no contiene pedidos únicos")
    return result
