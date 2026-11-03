"""Auditoría de calidad y validación de la variable objetivo (T07)."""

from dataclasses import dataclass
from typing import Dict, List, Any
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TargetValidationReport:
    """Resultado de la auditoría de la variable objetivo."""

    target_name: str
    total_records: int
    null_count: int
    min_value: float
    max_value: float
    mean_value: float
    median_value: float
    is_valid: bool
    rejection_reasons: List[str]


@dataclass(frozen=True)
class DataQualityAuditReport:
    """Informe de calidad de datos y prevención de fuga (data leakage)."""

    total_rows: int
    zero_coordinate_rows: int
    null_counts: Dict[str, int]
    pre_quote_features: List[str]
    post_order_leakage_features: List[str]
    target_report: TargetValidationReport
    decision: str
    recommendations: List[str]


PRE_QUOTE_FEATURES = [
    "Restaurant_latitude",
    "Restaurant_longitude",
    "Delivery_location_latitude",
    "Delivery_location_longitude",
    "Weather_conditions",
    "Road_traffic_density",
    "Type_of_vehicle",
    "City",
    "multiple_deliveries",
]

POST_ORDER_LEAKAGE_FEATURES = [
    "Time_Order_picked",
]


def audit_target_variable(df: pd.DataFrame, target_col: str = "Time_taken (min)") -> TargetValidationReport:
    """Valida la variable objetivo del dataset."""
    reasons = []
    if target_col not in df.columns:
        return TargetValidationReport(
            target_name=target_col,
            total_records=len(df),
            null_count=len(df),
            min_value=0.0,
            max_value=0.0,
            mean_value=0.0,
            median_value=0.0,
            is_valid=False,
            rejection_reasons=[f"Columna {target_col} no encontrada"],
        )

    series = df[target_col]
    if series.dtype == object:
        cleaned_series = series.astype(str).str.extract(r"(\d+)", expand=False)
        numeric_series = pd.to_numeric(cleaned_series, errors="coerce")
    else:
        numeric_series = pd.to_numeric(series, errors="coerce")

    nulls = int(numeric_series.isna().sum())
    valid_values = numeric_series.dropna()

    if len(valid_values) == 0:
        return TargetValidationReport(
            target_name=target_col,
            total_records=len(df),
            null_count=nulls,
            min_value=0.0,
            max_value=0.0,
            mean_value=0.0,
            median_value=0.0,
            is_valid=False,
            rejection_reasons=["No existen valores numéricos válidos en el target"],
        )

    min_val = float(valid_values.min())
    max_val = float(valid_values.max())
    mean_val = float(valid_values.mean())
    median_val = float(valid_values.median())

    if min_val <= 0:
        reasons.append(f"Existen duraciones <= 0 minutos (min: {min_val})")
    if max_val > 300:
        reasons.append(f"Existen duraciones inverosímiles > 300 minutos (max: {max_val})")

    is_valid = len(reasons) == 0 and nulls < (len(df) * 0.05)

    return TargetValidationReport(
        target_name=target_col,
        total_records=len(df),
        null_count=nulls,
        min_value=round(min_val, 2),
        max_value=round(max_val, 2),
        mean_value=round(mean_val, 2),
        median_value=round(median_val, 2),
        is_valid=is_valid,
        rejection_reasons=reasons,
    )


def audit_zomato_quality(df: pd.DataFrame) -> DataQualityAuditReport:
    """Realiza la auditoría integral de calidad del dataset Zomato."""
    total_rows = len(df)
    null_counts = {col: int(df[col].isna().sum()) for col in df.columns}

    zero_mask = (
        (df["Restaurant_latitude"].abs() < 1e-4)
        | (df["Restaurant_longitude"].abs() < 1e-4)
        | (df["Delivery_location_latitude"].abs() < 1e-4)
        | (df["Delivery_location_longitude"].abs() < 1e-4)
    )
    zero_rows = int(zero_mask.sum())

    target_rep = audit_target_variable(df)
    decision = "APROBADO_CON_FILTROS" if target_rep.is_valid else "RECHAZADO"

    recommendations = [
        "Filtrar filas con coordenadas en 0.0 (afecta cálculo de distancia)",
        "Excluir 'Time_Order_picked' de features de cotización para evitar data leakage",
        "Calcular distancia ortodrómica Haversine (km) como predictor pre-entrega",
        "Imputar o descartar registros con nulos en Weather_conditions y Road_traffic_density",
    ]

    return DataQualityAuditReport(
        total_rows=total_rows,
        zero_coordinate_rows=zero_rows,
        null_counts=null_counts,
        pre_quote_features=PRE_QUOTE_FEATURES,
        post_order_leakage_features=POST_ORDER_LEAKAGE_FEATURES,
        target_report=target_rep,
        decision=decision,
        recommendations=recommendations,
    )

