"""Análisis Exploratorio de Datos (EDA) en memoria (T09)."""

from typing import Dict, Any
import numpy as np
import pandas as pd


def generate_eda_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula estadísticas descriptivas y correlaciones en memoria."""
    summary: Dict[str, Any] = {}

    target = df["time_taken_min"].dropna()
    summary["target_stats"] = {
        "count": int(len(target)),
        "mean": float(round(target.mean(), 2)),
        "std": float(round(target.std(), 2)),
        "min": float(round(target.min(), 2)),
        "q25": float(round(target.quantile(0.25), 2)),
        "median": float(round(target.median(), 2)),
        "q75": float(round(target.quantile(0.75), 2)),
        "max": float(round(target.max(), 2)),
        "skewness": float(round(target.skew(), 2)),
    }

    dist = df["distance_km"].dropna()
    summary["distance_stats"] = {
        "count": int(len(dist)),
        "mean": float(round(dist.mean(), 2)),
        "std": float(round(dist.std(), 2)),
        "min": float(round(dist.min(), 2)),
        "median": float(round(dist.median(), 2)),
        "max": float(round(dist.max(), 2)),
    }

    corr = float(round(df[["distance_km", "time_taken_min"]].corr().iloc[0, 1], 4))
    summary["distance_target_correlation"] = corr

    vehicle_grp = (
        df.groupby("Type_of_vehicle")["time_taken_min"]
        .agg(["count", "mean", "median", "std"])
        .round(2)
        .to_dict(orient="index")
    )
    summary["by_vehicle"] = vehicle_grp

    traffic_grp = (
        df.groupby("Road_traffic_density")["time_taken_min"]
        .agg(["count", "mean", "median", "std"])
        .round(2)
        .to_dict(orient="index")
    )
    summary["by_traffic"] = traffic_grp

    weather_grp = (
        df.groupby("Weather_conditions")["time_taken_min"]
        .agg(["count", "mean", "median", "std"])
        .round(2)
        .to_dict(orient="index")
    )
    summary["by_weather"] = weather_grp

    return summary

