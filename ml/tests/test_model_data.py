"""Casos controlados de calendario y aislamiento; nunca son datos de ML reales."""

import math
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from delivery_ml.model_data import FEATURE_COLUMNS, TARGET, temporal_features, temporal_split, model_xy


CUT = int(pd.Timestamp("2022-10-23T00:00:00Z").timestamp())


def row(name, start, end):
    stamp = pd.to_datetime(start, unit="s", utc=True)
    return {"order_id": name, "source_waybill_id": name,
            "platform_order_time": start, "arrive_time": end,
            "request_hour_utc": stamp.hour, "request_weekday_utc": stamp.dayofweek,
            TARGET: (end-start)/60}


def test_fixed_cyclic_features_keep_midnight_close_and_ignore_future_columns():
    context = pd.DataFrame({"request_hour_utc": [0, 23, 12], "request_weekday_utc": [0, 6, 3],
                            "arrive_time": [1, 2, 3], TARGET: [10, 20, 30]})
    before = context.copy(deep=True)
    features = temporal_features(context)
    assert_frame_equal(context, before)
    assert list(features) == FEATURE_COLUMNS
    assert features.loc[0, "request_hour_sin"] == 0
    assert features.loc[0, "request_hour_cos"] == 1
    distance = lambda a, b: math.hypot(features.loc[a, "request_hour_sin"]-features.loc[b, "request_hour_sin"], features.loc[a, "request_hour_cos"]-features.loc[b, "request_hour_cos"])
    assert distance(0, 1) < distance(0, 2)
    context[TARGET] = [99, 99, 99]
    context["arrive_time"] = [999, 999, 999]
    assert_frame_equal(features, temporal_features(context))
    with pytest.raises(ValueError, match="dominio"):
        temporal_features(pd.DataFrame({"request_hour_utc": [24], "request_weekday_utc": [0]}))


def test_time_split_purges_labels_not_available_at_cut_and_never_mixes_ids():
    orders = pd.DataFrame([row("train", CUT-120, CUT-60), row("crossing", CUT-30, CUT+60),
                           row("edge", CUT-60, CUT), row("test", CUT, CUT+120)])
    before = orders.copy(deep=True)
    parts = temporal_split(orders)
    assert_frame_equal(orders, before)
    assert parts["train"]["order_id"].tolist() == ["train"]
    assert set(parts["purged"]["order_id"]) == {"crossing", "edge"}
    assert parts["test"]["order_id"].tolist() == ["test"]
    assert sum(map(len, parts.values())) == len(orders)
    assert parts["train"]["arrive_time"].max() < parts["test"]["platform_order_time"].min()
    x, y = model_xy(parts["train"])
    assert list(x) == FEATURE_COLUMNS and y.name == TARGET
    assert "arrive_time" not in x and "order_id" not in x and TARGET not in x


def test_rejects_ambiguous_ids_naive_or_empty_cut_and_changed_utc_context():
    orders = pd.DataFrame([row("train", CUT-120, CUT-60), row("test", CUT, CUT+120)])
    with pytest.raises(ValueError, match="zona horaria"):
        temporal_split(orders, "2022-10-23")
    with pytest.raises(ValueError, match="no vacíos"):
        temporal_split(orders, "2023-01-01T00:00:00Z")
    repeated = pd.concat([orders, orders.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicado"):
        temporal_split(repeated)
    orders.loc[0, "request_hour_utc"] = 0
    with pytest.raises(ValueError, match="Contexto UTC"):
        temporal_split(orders)
