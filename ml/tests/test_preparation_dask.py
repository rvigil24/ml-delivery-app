"""Casos controlados entre particiones; no forman parte de datos reales."""

import dask
import dask.dataframe as dd
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from delivery_ml.preparation import prepare_orders, REQUIRED_FIELDS
from delivery_ml.preparation_dask import prepare_orders_dask


def row(order, waybill, **changes):
    start = 1665964800
    result = {name: 1 for name in REQUIRED_FIELDS}
    result.update(
        order_id=order, waybill_id=waybill, is_prebook=0, is_courier_grabbed=1,
        platform_order_time=start, order_push_time=start+1, dispatch_time=start+2,
        grab_time=start+3, fetch_time=start+4, arrive_time=start+60,
    )
    result.update(changes)
    return result


def test_matches_pandas_when_conflicts_and_completions_cross_partitions():
    raw = pd.DataFrame([
        row("changed", "a", arrive_time=0, recipient_lat=2),
        row("ambiguous", "b"), row("valid", "c", arrive_time=0, is_courier_grabbed=0),
        row("long", "d", arrive_time=1665964800+60000),
        row("changed", "e"), row("ambiguous", "f"), row("valid", "g"),
        row("reserved", "h", is_prebook=1), row("reversed", "i", fetch_time=1665964800+120),
    ])
    expected = prepare_orders(raw)
    with dask.config.set({"dataframe.convert-string": False, "scheduler": "synchronous"}):
        actual = prepare_orders_dask(dd.from_pandas(raw, npartitions=3, sort=False)).compute()
    actual = actual.sort_values("order_id").reset_index(drop=True)
    assert_frame_equal(actual, expected, check_dtype=False, check_exact=True)
    assert actual["order_id"].tolist() == ["long", "valid"]
    assert actual.loc[0, "time_taken_min"] == 1000


def test_rejects_global_duplicate_waybill_missing_id_and_fractional_timestamp():
    with dask.config.set({"dataframe.convert-string": False, "scheduler": "synchronous"}):
        for rows, message in [
            ([row("a", "same"), row("b", "same")], "duplicado"),
            ([row("a", 1), row("b", "1")], "duplicado"),
            ([row(None, "a"), row("b", "b")], "Identificador"),
            ([row("a", "a", platform_order_time=1665964800.5), row("b", "b")], "enteros"),
        ]:
            with pytest.raises(ValueError, match=message):
                prepare_orders_dask(dd.from_pandas(pd.DataFrame(rows), npartitions=2, sort=False)).compute()
