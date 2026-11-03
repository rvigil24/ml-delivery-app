"""Casos controlados de resumen; nunca se incorporan al experimento real."""

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from delivery_ml.exploration import COORDINATES, summarize_orders


def sample():
    start = 1665964800  # lunes, 00:00 UTC
    return pd.DataFrame([
        {"order_id": str(i), "source_waybill_id": str(i),
         "platform_order_time": start, "arrive_time": start + duration * 60,
         "request_hour_utc": 0, "request_weekday_utc": 0,
         "time_taken_min": duration, **{name: i for name in COORDINATES}}
        for i, duration in enumerate([10, 20, 30, 40, 1000])
    ])


def test_summary_retains_tail_uses_utc_groups_and_does_not_modify_input():
    data = sample()
    before = data.copy(deep=True)
    report = summarize_orders(data)
    assert_frame_equal(data, before)
    assert report["rows"] == 5
    assert report["duration_minutes"]["p50"] == 30
    assert report["duration_minutes"]["max"] == 1000
    assert report["tail_diagnostics"]["upper_fence_minutes"] == 70
    assert report["tail_diagnostics"]["above_upper_fence"] == 1
    assert report["tail_diagnostics"]["removed_rows"] == 0
    assert report["by_date_utc"][0]["request_date_utc"] == "2022-10-17"
    assert sum(group["count"] for group in report["by_hour_utc"]) == 5
    assert report["spearman_raw_coordinates"]["time_taken_min"]["sender_lat_raw"] == pytest.approx(1)


def test_quality_reports_missing_context_and_duplicates_and_rejects_invalid_target():
    data = sample()
    data.loc[1, "order_id"] = data.loc[0, "order_id"]
    data.loc[1, "sender_lat_raw"] = None
    data.loc[0, "request_hour_utc"] = 1
    data.loc[0, "arrive_time"] += 60
    report = summarize_orders(data)
    assert report["quality"]["duplicate_orders"] == 1
    assert report["quality"]["missing_by_column"]["sender_lat_raw"] == 1
    assert report["quality"]["utc_context_mismatch"] == 1
    assert report["quality"]["target_mismatch"] == 1
    data["time_taken_min"] = data["time_taken_min"].astype(float)
    data.loc[0, "time_taken_min"] = float("inf")
    with pytest.raises(ValueError, match="Target"):
        summarize_orders(data)
