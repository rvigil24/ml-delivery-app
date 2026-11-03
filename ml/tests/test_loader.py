"""Pruebas unitarias para el módulo de carga en memoria (T06)."""

import pandas as pd
import pytest

from delivery_ml.loader import (
    DatasetMetadata,
    EXPECTED_ZOMATO_COLUMNS,
    ZOMATO_RAW_URL,
    DOORDASH_RAW_URL,
)


def test_metadata_dataclass_fields() -> None:
    meta = DatasetMetadata(
        source_url=ZOMATO_RAW_URL,
        num_rows=100,
        num_cols=20,
        sha256_hash="abc123",
        byte_size=1024,
        memory_usage_mb=0.1,
    )
    assert meta.num_rows == 100
    assert meta.num_cols == 20
    assert meta.sha256_hash == "abc123"
    assert meta.byte_size == 1024


def test_expected_columns_definition() -> None:
    assert len(EXPECTED_ZOMATO_COLUMNS) == 20
    assert "Time_taken (min)" in EXPECTED_ZOMATO_COLUMNS
    assert "Restaurant_latitude" in EXPECTED_ZOMATO_COLUMNS
    assert "Delivery_location_latitude" in EXPECTED_ZOMATO_COLUMNS

