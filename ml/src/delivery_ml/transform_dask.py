"""Transformaciones equivalentes implementadas con Dask DataFrame (T10)."""

import dask.dataframe as dd
import numpy as np
import pandas as pd


def haversine_distance_dask(df: dd.DataFrame) -> dd.Series:
    """Calcula la distancia Haversine usando expresiones vectorizadas de Dask."""
    R = 6371.0

    phi1 = np.radians(df["Restaurant_latitude"])
    phi2 = np.radians(df["Delivery_location_latitude"])
    delta_phi = np.radians(df["Delivery_location_latitude"] - df["Restaurant_latitude"])
    delta_lambda = np.radians(df["Delivery_location_longitude"] - df["Restaurant_longitude"])

    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    a = a.clip(lower=0.0, upper=1.0)
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return (R * c).round(2)


def transform_dask_pipeline(
    df_or_ddf,
    npartitions: int = 4,
) -> dd.DataFrame:
    """Ejecuta el pipeline equivalente de transformación utilizando Dask DataFrame."""
    if isinstance(df_or_ddf, pd.DataFrame):
        ddf = dd.from_pandas(df_or_ddf, npartitions=npartitions)
    else:
        ddf = df_or_ddf

    if "Time_taken (min)" in ddf.columns:
        if ddf["Time_taken (min)"].dtype == object:
            cleaned_target = (
                ddf["Time_taken (min)"]
                .astype(str)
                .str.extract(r"(\d+)", expand=False)
            )
            ddf["time_taken_min"] = dd.to_numeric(cleaned_target, errors="coerce")
        else:
            ddf["time_taken_min"] = dd.to_numeric(ddf["Time_taken (min)"], errors="coerce")

    mask = (
        (ddf["Restaurant_latitude"].abs() > 0.1)
        & (ddf["Restaurant_longitude"].abs() > 0.1)
        & (ddf["Delivery_location_latitude"].abs() > 0.1)
        & (ddf["Delivery_location_longitude"].abs() > 0.1)
        & (ddf["Restaurant_latitude"] >= -90)
        & (ddf["Restaurant_latitude"] <= 90)
        & (ddf["Delivery_location_latitude"] >= -90)
        & (ddf["Delivery_location_latitude"] <= 90)
        & (ddf["Restaurant_longitude"] >= -180)
        & (ddf["Restaurant_longitude"] <= 180)
        & (ddf["Delivery_location_longitude"] >= -180)
        & (ddf["Delivery_location_longitude"] <= 180)
    )
    filtered = ddf[mask]

    for col in ["Weather_conditions", "Road_traffic_density", "Type_of_vehicle", "City"]:
        if col in filtered.columns:
            filtered[col] = (
                filtered[col]
                .astype(str)
                .str.strip()
                .str.replace(r"^conditions\s+", "", regex=True)
            )

    filtered["distance_km"] = haversine_distance_dask(filtered)

    valid_dist = (filtered["distance_km"] >= 0.05) & (filtered["distance_km"] <= 50.0)
    result = filtered[valid_dist]

    cols_to_keep = [
        "ID",
        "Delivery_person_Age",
        "Delivery_person_Ratings",
        "distance_km",
        "Weather_conditions",
        "Road_traffic_density",
        "Vehicle_condition",
        "Type_of_order",
        "Type_of_vehicle",
        "multiple_deliveries",
        "Festival",
        "City",
        "time_taken_min",
    ]
    available_cols = [c for c in cols_to_keep if c in result.columns]
    return result[available_cols]

