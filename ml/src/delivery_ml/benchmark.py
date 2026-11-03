"""Comparación de tiempos y resultados entre Pandas, Dask y PySpark (T12)."""

import platform
import time
from typing import Dict, Any, Tuple
import pandas as pd
import psutil

from delivery_ml.transform_pandas import transform_pandas_pipeline
from delivery_ml.transform_dask import transform_dask_pipeline
from delivery_ml.transform_spark import (
    get_or_create_local_spark_session,
    transform_spark_pipeline,
)


def run_benchmark_in_memory(
    raw_df: pd.DataFrame,
    repeats: int = 3,
) -> Dict[str, Any]:
    """Ejecuta transformaciones idénticas en Pandas, Dask y PySpark y mide tiempos reales."""
    results: Dict[str, Any] = {
        "hardware": {
            "os": platform.platform(),
            "cpu": platform.processor(),
            "cpu_cores_logical": psutil.cpu_count(logical=True),
            "cpu_cores_physical": psutil.cpu_count(logical=False),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "python_version": platform.python_version(),
        },
        "input_rows": len(raw_df),
        "benchmarks": {},
    }

    pandas_times = []
    pandas_out = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        pandas_out = transform_pandas_pipeline(raw_df)
        pandas_times.append(time.perf_counter() - t0)

    results["benchmarks"]["Pandas"] = {
        "mean_seconds": round(float(sum(pandas_times) / len(pandas_times)), 4),
        "min_seconds": round(float(min(pandas_times)), 4),
        "output_rows": len(pandas_out) if pandas_out is not None else 0,
        "mean_distance_km": round(float(pandas_out["distance_km"].mean()), 2)
        if pandas_out is not None
        else 0.0,
    }

    dask_times = []
    dask_out_df = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        ddf = transform_dask_pipeline(raw_df, npartitions=4)
        dask_out_df = ddf.compute()
        dask_times.append(time.perf_counter() - t0)

    results["benchmarks"]["Dask"] = {
        "mean_seconds": round(float(sum(dask_times) / len(dask_times)), 4),
        "min_seconds": round(float(min(dask_times)), 4),
        "output_rows": len(dask_out_df) if dask_out_df is not None else 0,
        "mean_distance_km": round(float(dask_out_df["distance_km"].mean()), 2)
        if dask_out_df is not None
        else 0.0,
    }

    spark = get_or_create_local_spark_session()
    spark_df = spark.createDataFrame(raw_df)

    spark_times = []
    spark_rows = 0
    spark_mean_dist = 0.0
    for _ in range(repeats):
        t0 = time.perf_counter()
        spark_transformed = transform_spark_pipeline(spark_df)
        spark_rows = spark_transformed.count()
        spark_times.append(time.perf_counter() - t0)

    from pyspark.sql import functions as F
    spark_mean_dist = float(
        spark_transformed.select(F.mean("distance_km")).collect()[0][0] or 0.0
    )

    results["benchmarks"]["PySpark (local)"] = {
        "mean_seconds": round(float(sum(spark_times) / len(spark_times)), 4),
        "min_seconds": round(float(min(spark_times)), 4),
        "output_rows": spark_rows,
        "mean_distance_km": round(spark_mean_dist, 2),
    }

    return results

