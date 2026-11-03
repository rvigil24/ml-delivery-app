"""Transformaciones equivalentes implementadas con PySpark local (T11)."""

from typing import Optional
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T


def get_or_create_local_spark_session(app_name: str = "DeliveryAppLocalETL") -> SparkSession:
    """Crea u obtiene la SparkSession en modo local sin clúster distribuido."""
    return (
        SparkSession.builder.master("local[2]")
        .appName(app_name)
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )


def haversine_distance_spark(
    lat1_col: str,
    lon1_col: str,
    lat2_col: str,
    lon2_col: str,
):
    """Genera la expresión columnar de Spark SQL para distancia Haversine en km."""
    R = 6371.0

    phi1 = F.radians(F.col(lat1_col))
    phi2 = F.radians(F.col(lat2_col))
    delta_phi = F.radians(F.col(lat2_col) - F.col(lat1_col))
    delta_lambda = F.radians(F.col(lon2_col) - F.col(lon1_col))

    a = (
        F.pow(F.sin(delta_phi / 2.0), 2)
        + F.cos(phi1) * F.cos(phi2) * F.pow(F.sin(delta_lambda / 2.0), 2)
    )
    a_clipped = F.when(a > 1.0, 1.0).when(a < 0.0, 0.0).otherwise(a)
    c = 2.0 * F.atan2(F.sqrt(a_clipped), F.sqrt(1.0 - a_clipped))
    return F.round(R * c, 2)


def transform_spark_pipeline(df_spark):
    """Ejecuta el pipeline de transformación con PySpark local."""
    res = df_spark
    if "Time_taken (min)" in res.columns:
        res = res.withColumn(
            "time_taken_min",
            F.regexp_extract(F.col("Time_taken (min)").cast("string"), r"(\d+)", 1).cast(T.DoubleType())
        )

    res = res.filter(
        (F.abs(F.col("Restaurant_latitude")) > 0.1)
        & (F.abs(F.col("Restaurant_longitude")) > 0.1)
        & (F.abs(F.col("Delivery_location_latitude")) > 0.1)
        & (F.abs(F.col("Delivery_location_longitude")) > 0.1)
        & (F.col("Restaurant_latitude").between(-90.0, 90.0))
        & (F.col("Delivery_location_latitude").between(-90.0, 90.0))
        & (F.col("Restaurant_longitude").between(-180.0, 180.0))
        & (F.col("Delivery_location_longitude").between(-180.0, 180.0))
    )

    str_cols = ["Weather_conditions", "Road_traffic_density", "Type_of_vehicle", "City"]
    for c in str_cols:
        if c in res.columns:
            res = res.withColumn(
                c,
                F.trim(F.regexp_replace(F.col(c).cast("string"), r"^conditions\s+", ""))
            )

    res = res.withColumn(
        "distance_km",
        haversine_distance_spark(
            "Restaurant_latitude",
            "Restaurant_longitude",
            "Delivery_location_latitude",
            "Delivery_location_longitude",
        )
    )

    res = res.filter((F.col("distance_km") >= 0.05) & (F.col("distance_km") <= 50.0))

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
    available_cols = [c for c in cols_to_keep if c in res.columns]
    return res.select(*available_cols)

