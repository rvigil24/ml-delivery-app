"""T10: agrupa intentos con Dask y reutiliza las reglas aprobadas de T08."""

import dask
import dask.dataframe as dd
import pandas as pd

from delivery_ml.preparation import prepare_orders, REQUIRED_FIELDS


def validate_ids(partition: pd.DataFrame) -> pd.DataFrame:
    """Validar antes del shuffle evita perder identificadores ausentes."""
    partition = partition.copy()
    for name in ("order_id", "waybill_id"):
        ids = partition[name].astype("string")
        if ids.isna().any() or ids.str.strip().eq("").any():
            raise ValueError(f"Identificador ausente: {name}")
        partition[name] = ids
    return partition


def prepare_orders_dask(raw: dd.DataFrame) -> dd.DataFrame:
    """Devuelve un grafo particionado; comprueba unicidad global de waybills.

    La validación global ejecuta una reducción. El resto se ejecuta al llamar
    compute(). No aplicar prepare_orders a fragmentos sin reunir antes pedidos:
    las ambigüedades y los reintentos pueden cruzar particiones.
    """
    missing = set(REQUIRED_FIELDS) - set(raw.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {sorted(missing)}")
    data = raw[REQUIRED_FIELDS]
    data = data.map_partitions(validate_ids, meta=validate_ids(data._meta))
    count, unique = dask.compute(data["waybill_id"].count(), data["waybill_id"].nunique())
    if count != unique:
        raise ValueError("waybill_id duplicado; revisar antes de preparar")
    # Todos los intentos de cada pedido terminan en una misma partición.
    grouped = data.shuffle(on="order_id", shuffle_method="tasks")
    return grouped.map_partitions(prepare_orders, meta=prepare_orders(data._meta))
