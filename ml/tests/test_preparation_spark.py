"""Casos controlados de reglas Spark SQL; separados de los datos reales."""

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from delivery_ml.preparation import REQUIRED_FIELDS, prepare_orders
from delivery_ml.preparation_spark import local_spark, prepare_orders_spark


@pytest.fixture(scope="module")
def spark():
    session = local_spark()
    yield session
    session.stop()


def row(order, waybill, **changes):
    start = 1665964800
    result = {name: 1 for name in REQUIRED_FIELDS}
    result.update(order_id=order, waybill_id=waybill, is_prebook=0, is_courier_grabbed=1,
                  platform_order_time=start, order_push_time=start+1, dispatch_time=start+2,
                  grab_time=start+3, fetch_time=start+4, arrive_time=start+60)
    result.update(changes)
    return result


def frame(spark, rows):
    # Entrada textual, como la lectura CSV sin inferencia; conserva ausencias.
    values = [tuple(None if row[name] is None else str(row[name]) for name in REQUIRED_FIELDS) for row in rows]
    return spark.createDataFrame(values, ",".join(f"{name} string" for name in REQUIRED_FIELDS)).repartition(3)


def test_native_sql_matches_pandas_for_attempts_scope_chronology_and_long_tail(spark):
    rows = [
        row("changed", "a", arrive_time=0, recipient_lat=2), row("ambiguous", "b"),
        row("valid", "c", arrive_time=0, is_courier_grabbed=0),
        row("long", "d", arrive_time=1665964800+60000),
        row("changed", "e"), row("ambiguous", "f"), row("valid", "g"),
        row("reserved", "h", is_prebook=1), row("reversed", "i", fetch_time=1665964800+120),
        row("numeric-format", "j", platform_order_time="1.6659648e9"),
    ]
    prepared = prepare_orders_spark(frame(spark, rows))
    actual = pd.DataFrame.from_records(prepared.collect(), columns=prepared.columns).sort_values("order_id").reset_index(drop=True)
    expected = prepare_orders(pd.DataFrame(rows))
    assert_frame_equal(actual, expected, check_dtype=False, check_exact=True)
    assert actual["order_id"].tolist() == ["long", "numeric-format", "valid"]
    assert actual.loc[0, "time_taken_min"] == 1000


def test_rejects_global_duplicates_missing_ids_fractional_times_and_invalid_flags(spark):
    for rows, message in [
        ([row("a", "same"), row("b", "same")], "duplicado"),
        ([row(None, "a"), row("b", "b")], "Identificador"),
        ([row("a", "a", platform_order_time=1665964800.5)], "enteros"),
        ([row("a", "a", platform_order_time="9223372036854775808")], "enteros"),
        ([row("a", "a", platform_order_time="NaN")], "enteros"),
        ([row("a", "a", is_prebook=2)], "Indicador"),
    ]:
        with pytest.raises(ValueError, match=message):
            prepare_orders_spark(frame(spark, rows)).collect()
