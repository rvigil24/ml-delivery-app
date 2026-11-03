"""T11: compara la preparación Spark SQL local con todos los valores Pandas T08."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import tempfile

import pandas as pd
from pandas.testing import assert_frame_equal
import pyspark

from acquire_meituan import CSV_NAME, DEFAULT_OUTPUT as DEFAULT_DATASET, EXPECTED, REVISION, verify_file
from prepare_meituan import DEFAULT_OUTPUT as DEFAULT_REFERENCE, DEFAULT_REPORT, file_hash, prepare
from delivery_ml import preparation_spark


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data/reports/meituan" / REVISION / "t11_spark.json"


def compare(dataset: Path, reference: Path, audit: Path, output: Path) -> dict:
    source = dataset / CSV_NAME
    if output in (source, reference / "orders.csv", reference / "manifest.json", audit):
        raise ValueError("El informe no puede sobrescribir entradas ni manifiestos")
    integrity = verify_file(source, *EXPECTED[CSV_NAME])
    manifest = prepare(dataset, audit, reference)
    expected = pd.read_csv(reference / "orders.csv", float_precision="round_trip",
                           dtype={"order_id": "string", "source_waybill_id": "string"})
    spark = preparation_spark.local_spark()
    try:
        raw = spark.read.options(header=True, inferSchema=False, mode="FAILFAST").csv(str(source))
        partitions = raw.rdd.getNumPartitions()
        master = spark.sparkContext.master
        java_version = spark.sparkContext._jvm.java.lang.System.getProperty("java.version")
        # collect ejecuta el grafo SQL; Pandas solo recibe la salida terminada.
        # Evita toPandas de Spark 3.5, que requiere distutils en Python 3.12.
        prepared = preparation_spark.prepare_orders_spark(raw)
        result = pd.DataFrame.from_records(prepared.collect(), columns=prepared.columns)
    finally:
        spark.stop()
    result = result.sort_values("order_id", kind="stable").reset_index(drop=True)
    for name in ("order_id", "source_waybill_id"):
        result[name] = result[name].astype("string")
    assert_frame_equal(result, expected, check_dtype=False, check_exact=True)
    with tempfile.TemporaryDirectory(prefix="delivery-t11-csv-") as temporary:
        derived = Path(temporary) / "orders.csv"
        result.to_csv(derived, index=False, lineterminator="\n")
        derived_hash = file_hash(derived)
    if derived_hash != manifest["sha256"]:
        raise ValueError("La serialización normalizada Spark difiere del CSV Pandas")
    report = {
        "task": "T11", "equivalent": True, "rows": len(result), "columns": list(result.columns),
        "comparison": "Todos los valores exactos; CSV normalizado con Pandas tras collect, no escritor CSV de Spark",
        "source_revision": REVISION, "source_sha256": integrity["sha256"],
        "pandas_csv_sha256": manifest["sha256"], "spark_normalized_csv_sha256": derived_hash,
        "reference_manifest_sha256": file_hash(reference / "manifest.json"), "audit_sha256": file_hash(audit),
        "master": master, "input_partitions": partitions, "shuffle_partitions": 4,
        "max_partition_bytes": 16 * 1024 * 1024, "timezone": "UTC", "arrow_enabled": False,
        "operations": [
            "Lectura CSV nativa, selección y validación de IDs/enteros/indicadores",
            "groupBy global para waybills duplicados y estabilidad de cotización",
            "Ventana por pedido para contar completados; join left_semi con pedidos estables",
            "Filtros de reservas, aceptación y cronología; contexto UTC y duración en minutos",
            "collect, ordenación y comparación completa; CSV normalizado temporal para hash",
        ],
        "implementation": {
            "preparation_spark.py": file_hash(Path(preparation_spark.__file__)),
            "compare_spark_meituan.py": file_hash(Path(__file__)),
        },
        "versions": {"python": platform.python_version(), "pandas": pd.__version__, "pyspark": pyspark.__version__, "java": java_version},
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "Salida reunida en memoria para comparar; no acredita escalabilidad ilimitada",
            "No se mide rendimiento ni se usa clúster; comparación de tiempos en T12",
            "Se mantienen los límites de fuente, unidades geográficas y vehículos de T08/T09",
        ],
    }
    verify_file(source, *EXPECTED[CSV_NAME])
    verify_file(reference / "orders.csv", manifest["bytes"], manifest["sha256"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--audit", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = compare(args.dataset.resolve(), args.reference.resolve(), args.audit.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError, AssertionError, RuntimeError) as error:
        parser.exit(1, f"Comparación Spark no completada: {error}\n")
    print(f"Spark equivale a Pandas: {report['rows']:,} pedidos; {report['input_partitions']} particiones; {report['master']}")
    print(f"CSV normalizado SHA-256 idéntico: {report['spark_normalized_csv_sha256']}")
    print(f"Informe: {args.output}")


if __name__ == "__main__":
    main()
