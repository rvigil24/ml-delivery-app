"""Pruebas unitarias para equivalencia de transformaciones con PySpark (T11)."""

import pandas as pd
import pytest

from delivery_ml.transform_pandas import transform_pandas_pipeline
from delivery_ml.transform_spark import (
    get_or_create_local_spark_session,
    transform_spark_pipeline,
)


def test_spark_pipeline_matches_pandas() -> None:
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

    spark = get_or_create_local_spark_session()
    spark_df = spark.createDataFrame(sample)
    spark_res_df = transform_spark_pipeline(spark_df).toPandas()

    assert len(pandas_res) == len(spark_res_df)
    assert set(pandas_res.columns) == set(spark_res_df.columns)
    assert (pandas_res["distance_km"] == spark_res_df["distance_km"]).all()
    assert (pandas_res["time_taken_min"] == spark_res_df["time_taken_min"]).all()

