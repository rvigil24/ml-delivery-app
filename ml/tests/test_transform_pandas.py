"""Pruebas unitarias para transformaciones con Pandas (T08)."""

import numpy as np
import pandas as pd
import pytest

from delivery_ml.transform_pandas import (
    haversine_distance_km,
    clean_target_column,
    filter_invalid_coordinates,
    clean_string_columns,
    transform_pandas_pipeline,
)


def test_haversine_distance_equator_point() -> None:
    lat1 = pd.Series([0.0])
    lon1 = pd.Series([0.0])
    lat2 = pd.Series([1.0])
    lon2 = pd.Series([0.0])
    dist = haversine_distance_km(lat1, lon1, lat2, lon2)
    assert 110.0 < dist.iloc[0] < 112.5


def test_haversine_distance_same_point_is_zero() -> None:
    lat1 = pd.Series([13.6929])
    lon1 = pd.Series([-89.2182])
    dist = haversine_distance_km(lat1, lon1, lat1, lon1)
    assert dist.iloc[0] == pytest.approx(0.0, abs=1e-5)


def test_clean_target_column_parses_strings() -> None:
    df = pd.DataFrame({"Time_taken (min)": ["(min) 24", "(min) 35", 40]})
    res = clean_target_column(df)
    assert "time_taken_min" in res.columns
    assert list(res["time_taken_min"]) == [24.0, 35.0, 40.0]


def test_filter_invalid_coordinates_removes_zeros() -> None:
    df = pd.DataFrame({
        "Restaurant_latitude": [0.0, 22.5, 23.0],
        "Restaurant_longitude": [0.0, 88.3, 88.4],
        "Delivery_location_latitude": [22.5, 22.6, 0.0],
        "Delivery_location_longitude": [88.3, 88.4, 0.0],
    })
    filtered = filter_invalid_coordinates(df)
    assert len(filtered) == 1
    assert filtered.iloc[0]["Restaurant_latitude"] == 22.5


def test_clean_string_columns_strips_prefixes() -> None:
    df = pd.DataFrame({
        "Weather_conditions": ["conditions Sunny", " conditions Fog "],
        "Road_traffic_density": [" High ", "Low"],
    })
    cleaned = clean_string_columns(df)
    assert cleaned["Weather_conditions"].tolist() == ["Sunny", "Fog"]
    assert cleaned["Road_traffic_density"].tolist() == ["High", "Low"]


def test_transform_pandas_pipeline_end_to_end() -> None:
    sample = pd.DataFrame({
        "ID": ["0x1", "0x2"],
        "Delivery_person_Age": [25, 30],
        "Delivery_person_Ratings": [4.5, 4.8],
        "Restaurant_latitude": [22.5726, 0.0],
        "Restaurant_longitude": [88.3639, 0.0],
        "Delivery_location_latitude": [22.6000, 22.6],
        "Delivery_location_longitude": [88.4000, 88.4],
        "Weather_conditions": ["conditions Sunny", "Stormy"],
        "Road_traffic_density": ["Medium", "High"],
        "Vehicle_condition": [1, 2],
        "Type_of_order": ["Meal", "Buffet"],
        "Type_of_vehicle": ["motorcycle", "scooter"],
        "multiple_deliveries": [0, 1],
        "Festival": ["No", "No"],
        "City": ["Metropolitian", "Urban"],
        "Time_taken (min)": ["(min) 26", "(min) 40"],
    })
    transformed = transform_pandas_pipeline(sample)
    assert len(transformed) == 1
    assert transformed.iloc[0]["ID"] == "0x1"
    assert transformed.iloc[0]["time_taken_min"] == 26.0
    assert transformed.iloc[0]["Weather_conditions"] == "Sunny"
    assert transformed.iloc[0]["distance_km"] > 0

