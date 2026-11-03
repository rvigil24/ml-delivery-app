"""Pruebas unitarias para equivalencia de transformaciones con Dask (T10)."""

import pandas as pd
import pytest

from delivery_ml.transform_pandas import transform_pandas_pipeline
from delivery_ml.transform_dask import transform_dask_pipeline


def test_dask_pipeline_matches_pandas() -> None:
    sample = pd.DataFrame({
        "ID": ["0x1", "0x2", "0x3"],
        "Delivery_person_Age": [25, 30, 22],
        "Delivery_person_Ratings": [4.5, 4.8, 4.2],
        "Restaurant_latitude": [22.5726, 0.0, 19.0760],
        "Restaurant_longitude": [88.3639, 0.0, 72.8777],
        "Delivery_location_latitude": [22.6000, 22.6, 19.1000],
        "Delivery_location_longitude": [88.4000, 88.4, 72.9000],
        "Weather_conditions": ["conditions Sunny", "Stormy", "conditions Windy"],
        "Road_traffic_density": ["Medium", "High", "Low"],
        "Vehicle_condition": [1, 2, 1],
        "Type_of_order": ["Meal", "Buffet", "Snack"],
        "Type_of_vehicle": ["motorcycle", "scooter", "bicycle"],
        "multiple_deliveries": [0, 1, 0],
        "Festival": ["No", "No", "No"],
        "City": ["Metropolitian", "Urban", "Urban"],
        "Time_taken (min)": ["(min) 26", "(min) 40", "(min) 18"],
    })

    pandas_res = transform_pandas_pipeline(sample)
    ddf = transform_dask_pipeline(sample, npartitions=2)
    dask_res = ddf.compute().reset_index(drop=True)

    assert len(pandas_res) == len(dask_res)
    assert set(pandas_res.columns) == set(dask_res.columns)
    assert (pandas_res["distance_km"] == dask_res["distance_km"]).all()
    assert (pandas_res["time_taken_min"] == dask_res["time_taken_min"]).all()

