"""Fixtures sintéticas de transformación, separadas del experimento real."""

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from delivery_ml.preparation import prepare_orders, REQUIRED_FIELDS


def row(order="order-test", waybill="waybill-test", **changes):
    start = 1665964800
    result = {field: 1 for field in REQUIRED_FIELDS}
    result.update(
        order_id=order, waybill_id=waybill, is_prebook=0, is_courier_grabbed=1,
        platform_order_time=start, order_push_time=start+1, dispatch_time=start+2,
        grab_time=start+3, fetch_time=start+4, arrive_time=start+60,
    )
    result.update(changes)
    return result


def test_consolidates_attempts_derives_utc_context_and_keeps_original():
    raw = pd.DataFrame([
        row(waybill="rejected", arrive_time=0, is_courier_grabbed=0),
        row(waybill="completed"),
    ])
    before = raw.copy(deep=True)
    result = prepare_orders(raw)
    assert_frame_equal(raw, before)
    assert len(result) == 1
    assert result.iloc[0]["time_taken_min"] == 1
    assert result.iloc[0]["request_hour_utc"] == 0
    assert result.iloc[0]["request_weekday_utc"] == 0
    assert "is_courier_grabbed" not in result.columns
    assert "sender_lat_raw" in result.columns


def test_excludes_conflicting_reserved_missing_and_ambiguous_orders():
    raw = pd.DataFrame([
        row("changed", "a", arrive_time=0, recipient_lat=2),
        row("changed", "b"), row("reserved", "c", is_prebook=1),
        row("missing", "d", arrive_time=0),
        row("ambiguous", "e"), row("ambiguous", "f"),
        row("valid", "g"),
    ])
    result = prepare_orders(raw)
    assert result["order_id"].tolist() == ["valid"]


def test_keeps_long_durations_and_rejects_reversed_timeline():
    start = 1665964800
    raw = pd.DataFrame([
        row("long", "a", arrive_time=start+60000),
        row("reversed", "b", fetch_time=start+120),
    ])
    result = prepare_orders(raw)
    assert result["order_id"].tolist() == ["long"]
    assert result.iloc[0]["time_taken_min"] == 1000


def test_rejects_duplicate_waybills_and_fractional_timestamps():
    with pytest.raises(ValueError, match="duplicado"):
        prepare_orders(pd.DataFrame([row("a"), row("b")]))
    with pytest.raises(ValueError, match="enteros"):
        prepare_orders(pd.DataFrame([row(platform_order_time=1665964800.5)]))
