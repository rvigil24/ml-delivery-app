"""Pruebas unitarias para validación de calidad y target (T07)."""

import pandas as pd
import pytest

from delivery_ml.validation import (
    audit_target_variable,
    audit_zomato_quality,
    PRE_QUOTE_FEATURES,
    POST_ORDER_LEAKAGE_FEATURES,
)


def test_target_validation_with_clean_data() -> None:
    df = pd.DataFrame({"Time_taken (min)": [15, 20, 25, 30, 45]})
    report = audit_target_variable(df)
    assert report.is_valid is True
    assert report.null_count == 0
    assert report.min_value == 15.0
    assert report.max_value == 45.0
    assert report.mean_value == 27.0


def test_target_validation_with_string_and_invalid_values() -> None:
    df = pd.DataFrame({"Time_taken (min)": ["(min) 10", "-5", "350", "20"]})
    report = audit_target_variable(df)
    assert report.is_valid is False
    assert len(report.rejection_reasons) > 0


def test_target_validation_missing_column() -> None:
    df = pd.DataFrame({"other_col": [1, 2, 3]})
    report = audit_target_variable(df)
    assert report.is_valid is False
    assert "no encontrada" in report.rejection_reasons[0]


def test_audit_zomato_quality_identifies_zero_coordinates() -> None:
    df = pd.DataFrame({
        "Restaurant_latitude": [0.0, 13.69, 13.70],
        "Restaurant_longitude": [0.0, -89.21, -89.22],
        "Delivery_location_latitude": [13.70, 0.0, 13.71],
        "Delivery_location_longitude": [-89.22, -89.21, 0.0],
        "Time_taken (min)": [20, 25, 30],
        "Weather_conditions": ["Sunny", None, "Windy"],
        "Road_traffic_density": ["Low", "High", "Medium"],
        "Type_of_vehicle": ["motorcycle", "scooter", "bicycle"],
        "multiple_deliveries": [0, 1, 0],
        "City": ["Urban", "Metropolitian", "Urban"],
    })
    audit = audit_zomato_quality(df)
    assert audit.zero_coordinate_rows == 3
    assert audit.total_rows == 3
    assert "Time_Order_picked" in POST_ORDER_LEAKAGE_FEATURES

