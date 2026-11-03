"""Carga de datasets en memoria desde URL sin persistir archivos CSV en disco."""

from dataclasses import dataclass
import hashlib
import io
from typing import Optional, Tuple
import urllib.request
import pandas as pd

ZOMATO_RAW_URL = (
    "https://raw.githubusercontent.com/tushar99deep/"
    "Zomato_Order_Delivery-Time_Prediction_End-to-End-ML-Application/"
    "main/notebook/data/finalTrain.csv"
)

DOORDASH_RAW_URL = (
    "https://raw.githubusercontent.com/dklim-git/DoorDash-Project/"
    "master/historical_data.csv"
)

EXPECTED_ZOMATO_COLUMNS = [
    "ID",
    "Delivery_person_ID",
    "Delivery_person_Age",
    "Delivery_person_Ratings",
    "Restaurant_latitude",
    "Restaurant_longitude",
    "Delivery_location_latitude",
    "Delivery_location_longitude",
    "Order_Date",
    "Time_Orderd",
    "Time_Order_picked",
    "Weather_conditions",
    "Road_traffic_density",
    "Vehicle_condition",
    "Type_of_order",
    "Type_of_vehicle",
    "multiple_deliveries",
    "Festival",
    "City",
    "Time_taken (min)",
]


@dataclass(frozen=True)
class DatasetMetadata:
    """Metadatos de la carga en memoria."""

    source_url: str
    num_rows: int
    num_cols: int
    sha256_hash: str
    byte_size: int
    memory_usage_mb: float


def load_csv_from_url_in_memory(
    url: str,
    nrows: Optional[int] = None,
    timeout: int = 60,
) -> Tuple[pd.DataFrame, DatasetMetadata]:
    """Descarga el contenido CSV directamente a un buffer en memoria y lo carga en pandas.

    No escribe archivos en disco.
    """
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ml-delivery-app-loader/0.1"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        content_bytes = response.read()

    sha256_hash = hashlib.sha256(content_bytes).hexdigest()
    byte_size = len(content_bytes)

    buffer = io.BytesIO(content_bytes)
    df = pd.read_csv(buffer, nrows=nrows)
    memory_mb = float(df.memory_usage(deep=True).sum() / (1024 * 1024))

    metadata = DatasetMetadata(
        source_url=url,
        num_rows=len(df),
        num_cols=len(df.columns),
        sha256_hash=sha256_hash,
        byte_size=byte_size,
        memory_usage_mb=round(memory_mb, 2),
    )
    return df, metadata


def load_zomato_dataset_in_memory(
    nrows: Optional[int] = None,
) -> Tuple[pd.DataFrame, DatasetMetadata]:
    """Carga en memoria el dataset Zomato verificado."""
    df, metadata = load_csv_from_url_in_memory(ZOMATO_RAW_URL, nrows=nrows)
    missing_cols = set(EXPECTED_ZOMATO_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Faltan columnas esperadas en Zomato: {missing_cols}")
    return df, metadata

