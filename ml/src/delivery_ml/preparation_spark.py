"""T11: preparación equivalente a T08 mediante Spark SQL local, sin UDFs."""

from functools import reduce
import operator
import os
import shutil
import sys
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession, Window, functions as F

from delivery_ml.preparation import NUMERIC_FIELDS, QUOTE_FIELDS, REQUIRED_FIELDS, TIME_FIELDS


def local_spark() -> SparkSession:
    """Sesión local con UTC e intérprete Python del entorno del proyecto."""
    if not shutil.which("java") and not (Path(os.environ.get("JAVA_HOME", "")) / "bin/java").is_file():
        raise RuntimeError("PySpark requiere Java compatible; usar Java 17 y configurar JAVA_HOME/PATH")
    previous = os.environ.get("PYSPARK_PYTHON")
    os.environ["PYSPARK_PYTHON"] = sys.executable
    try:
        spark = (SparkSession.builder.master("local[2]").appName("delivery-data-local")
                 .config("spark.ui.enabled", "false")
                 .config("spark.ui.showConsoleProgress", "false")
                 .config("spark.driver.host", "127.0.0.1")
                 .config("spark.driver.bindAddress", "127.0.0.1")
                 .config("spark.sql.session.timeZone", "UTC")
                 .config("spark.sql.ansi.enabled", "false")
                 .config("spark.sql.shuffle.partitions", "4")
                 .config("spark.sql.files.maxPartitionBytes", str(16 * 1024 * 1024))
                 .config("spark.sql.execution.arrow.pyspark.enabled", "false")
                 .getOrCreate())
        spark.sparkContext.setLogLevel("ERROR")
        return spark
    finally:
        if previous is None:
            os.environ.pop("PYSPARK_PYTHON", None)
        else:
            os.environ["PYSPARK_PYTHON"] = previous


def prepare_orders_spark(raw: DataFrame) -> DataFrame:
    """Validaciones globales y grafo SQL: conflictos, completados y contexto UTC."""
    missing = set(REQUIRED_FIELDS) - set(raw.columns)
    if missing:
        raise ValueError(f"Faltan columnas: {sorted(missing)}")
    if raw.sparkSession.conf.get("spark.sql.session.timeZone") != "UTC":
        raise ValueError("La sesión Spark debe usar UTC")
    ids = ["order_id", "waybill_id"]
    data = raw.select(*[F.col(name).cast("string").alias(name) for name in ids], *NUMERIC_FIELDS)
    absent_id = reduce(operator.or_, [F.col(name).isNull() | F.col(name).rlike(r"(?U)^\s*$") for name in ids])
    if data.where(absent_id).limit(1).count():
        raise ValueError("Identificador ausente")
    if data.groupBy("waybill_id").count().where(F.col("count") > 1).limit(1).count():
        raise ValueError("waybill_id duplicado; revisar antes de preparar")

    invalid = []
    values = []
    for name in NUMERIC_FIELDS:
        number = F.col(name).cast("double")
        parsed = F.col(name).cast("long")
        integer = F.coalesce(parsed, number.cast("long"))
        overflow = parsed.isNull() & ((number >= F.lit(2.0**63)) | (number < F.lit(-(2.0**63))))
        invalid.append(number.isNull() | F.isnan(number) | (F.abs(number) == float("inf"))
                       | integer.isNull() | overflow | (number != integer.cast("double")))
        values.append(integer.alias(name))
    if data.where(reduce(operator.or_, invalid)).limit(1).count():
        raise ValueError("Se requieren enteros finitos; no se truncan timestamps")
    data = data.select(*ids, *values)
    if data.where(~F.col("is_prebook").isin(0, 1) | ~F.col("is_courier_grabbed").isin(0, 1)).limit(1).count():
        raise ValueError("Indicador distinto de 0/1")

    # La estabilidad se evalúa sobre todos los intentos, no solo completados.
    stability = data.groupBy("order_id").agg(*[F.countDistinct(name).alias(name) for name in QUOTE_FIELDS])
    stable = stability.where(reduce(operator.and_, [F.col(name) == 1 for name in QUOTE_FIELDS])).select("order_id")
    completed = data.where(F.col("arrive_time") > 0).withColumn(
        "completion_count", F.count(F.lit(1)).over(Window.partitionBy("order_id"))
    )
    positive = reduce(operator.and_, [F.col(name) > 0 for name in TIME_FIELDS])
    chronology = reduce(operator.and_, [F.col(right) >= F.col(left) for left, right in zip(TIME_FIELDS, TIME_FIELDS[1:])])
    selected = completed.join(stable, "order_id", "left_semi").where(
        (F.col("completion_count") == 1) & (F.col("is_prebook") == 0)
        & (F.col("is_courier_grabbed") == 1) & positive & chronology
        & (F.col("arrive_time") > F.col("platform_order_time"))
    )
    created = F.timestamp_seconds("platform_order_time")
    return selected.select(
        "order_id", F.col("waybill_id").alias("source_waybill_id"),
        "platform_order_time", "arrive_time",
        F.hour(created).alias("request_hour_utc"),
        ((F.dayofweek(created) + 5) % 7).alias("request_weekday_utc"),
        ((F.col("arrive_time") - F.col("platform_order_time")) / F.lit(60.0)).alias("time_taken_min"),
        *[F.col(name).alias(name + "_raw") for name in ("sender_lat", "sender_lng", "recipient_lat", "recipient_lng")],
    )
