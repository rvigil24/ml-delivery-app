"""Pipeline de limpieza y transformación de datos con Pandas (T08)."""

import math
import numpy as np
import pandas as pd


def haversine_distance_km(
    lat1: pd.Series,
    lon1: pd.Series,
    lat2: pd.Series,
    lon2: pd.Series,
) -> pd.Series:
    """Calcula la distancia Haversine en kilómetros entre dos coordenadas geográficas."""
    R = 6371.0

    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    a = np.clip(a, 0.0, 1.0)
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return pd.Series(R * c, index=lat1.index, name="distance_km")


def clean_target_column(df: pd.DataFrame, target_col: str = "Time_taken (min)") -> pd.DataFrame:
    """Limpia y castea la columna objetivo a float extrayendo dígitos."""
    out = df.copy()
    if target_col in out.columns:
        if out[target_col].dtype == object:
            cleaned = out[target_col].astype(str).str.extract(r"(\d+)", expand=False)
            out["time_taken_min"] = pd.to_numeric(cleaned, errors="coerce")
        else:
            out["time_taken_min"] = pd.to_numeric(out[target_col], errors="coerce")
    return out


def filter_invalid_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra registros con coordenadas GPS nulas o fuera de límites geográficos válidos."""
    mask = (
        (df["Restaurant_latitude"].abs() > 0.1)
        & (df["Restaurant_longitude"].abs() > 0.1)
        & (df["Delivery_location_latitude"].abs() > 0.1)
        & (df["Delivery_location_longitude"].abs() > 0.1)
        & (df["Restaurant_latitude"].between(-90, 90))
        & (df["Delivery_location_latitude"].between(-90, 90))
        & (df["Restaurant_longitude"].between(-180, 180))
        & (df["Delivery_location_longitude"].between(-180, 180))
    )
    return df[mask].copy()


def clean_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia espacios en blanco y estandariza textos en columnas categóricas."""
    out = df.copy()
    str_cols = [
        "Weather_conditions",
        "Road_traffic_density",
        "Type_of_vehicle",
        "Type_of_order",
        "Festival",
        "City",
    ]
    for col in str_cols:
        if col in out.columns:
            out[col] = (
                out[col]
                .astype(str)
                .str.strip()
                .str.replace(r"^conditions\s+", "", regex=True)
                .replace({"nan": None, "NaN": None, "": None})
            )
    return out


def transform_pandas_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta el pipeline completo y reproducible de transformación con Pandas."""
    step1 = clean_target_column(df)
    step2 = filter_invalid_coordinates(step1)
    step3 = clean_string_columns(step2)

    step3["distance_km"] = haversine_distance_km(
        step3["Restaurant_latitude"],
        step3["Restaurant_longitude"],
        step3["Delivery_location_latitude"],
        step3["Delivery_location_longitude"],
    ).round(2)

    valid_dist = step3["distance_km"].between(0.05, 50.0)
    out = step3[valid_dist].copy()

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
    available_cols = [c for c in cols_to_keep if c in out.columns]
    return out[available_cols].reset_index(drop=True)

