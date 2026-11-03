"""T10: compara todos los pedidos/valores Dask contra la salida Pandas T08."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import tempfile

import dask
import dask.dataframe as dd
import pandas as pd
from pandas.testing import assert_frame_equal

from acquire_meituan import CSV_NAME, DEFAULT_OUTPUT as DEFAULT_DATASET, EXPECTED, REVISION, verify_file
from prepare_meituan import DEFAULT_OUTPUT as DEFAULT_REFERENCE, DEFAULT_REPORT, file_hash, prepare
from delivery_ml import preparation, preparation_dask


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data/reports/meituan" / REVISION / "t10_dask.json"


def compare(dataset: Path, reference: Path, audit: Path, output: Path) -> dict:
    source = dataset / CSV_NAME
    if output in (source, reference / "orders.csv", reference / "manifest.json", audit):
        raise ValueError("El informe no puede sobrescribir entradas ni manifiestos")
    integrity = verify_file(source, *EXPECTED[CSV_NAME])
    # Verifica también la receta y auditoría de la referencia; no cambia T08.
    manifest = prepare(dataset, audit, reference)
    expected = pd.read_csv(
        reference / "orders.csv", float_precision="round_trip",
        dtype={"order_id": "string", "source_waybill_id": "string"},
    )
    with dask.config.set({"scheduler": "threads", "num_workers": 2, "dataframe.convert-string": False}):
        raw = dd.read_csv(
            str(source), blocksize=16 * 1024 * 1024,
            dtype={"order_id": "string", "waybill_id": "string"},
        )
        partitions = raw.npartitions
        result = preparation_dask.prepare_orders_dask(raw).compute()
    # El orden de particiones no equivale a orden de pedidos.
    result = result.sort_values("order_id", kind="stable").reset_index(drop=True)
    # CSV no conserva anchos int32/int64 ni backend de strings; se comparan
    # columnas y valores exactos, con floats de referencia leídos en round-trip.
    assert_frame_equal(result, expected, check_dtype=False, check_exact=True)
    with tempfile.TemporaryDirectory(prefix="delivery-t10-csv-") as temporary:
        derived = Path(temporary) / "orders.csv"
        result.to_csv(derived, index=False, lineterminator="\n")
        derived_hash = file_hash(derived)
    if derived_hash != manifest["sha256"]:
        raise ValueError("La serialización Dask difiere del CSV Pandas")
    report = {
        "task": "T10", "equivalent": True,
        "rows": len(result), "columns": list(result.columns),
        "comparison": "Todas las filas y columnas, valores exactos; dtype de almacenamiento no exigido",
        "source_revision": REVISION, "source_sha256": integrity["sha256"],
        "pandas_csv_sha256": manifest["sha256"], "dask_csv_sha256": derived_hash,
        "reference_manifest_sha256": file_hash(reference / "manifest.json"),
        "audit_sha256": file_hash(audit),
        "input_partitions": partitions, "blocksize_bytes": 16 * 1024 * 1024,
        "scheduler": "threads", "workers": 2,
        "operations": [
            "Lectura CSV particionada y selección de campos T08",
            "Validación de IDs y unicidad global de waybill_id",
            "Shuffle por order_id para reunir intentos",
            "Reglas T08 por partición: tipado, conflictos, completados, reservas y cronología",
            "Derivación de duración y contexto UTC; preservación de coordenadas raw",
            "Compute local, ordenación y comparación completa con Pandas",
        ],
        "implementation": {
            "preparation.py": file_hash(Path(preparation.__file__)),
            "preparation_dask.py": file_hash(Path(preparation_dask.__file__)),
            "compare_dask_meituan.py": file_hash(Path(__file__)),
        },
        "versions": {"python": platform.python_version(), "pandas": pd.__version__, "dask": dask.__version__},
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "Compute reúne la cohorte final en memoria para compararla; no demuestra escalabilidad ilimitada",
            "No se midió rendimiento: comparación de tiempos pendiente de T12",
            "Mismos límites de fuente, coordenadas y vehículos que T08/T09",
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
    except (OSError, ValueError, KeyError, AssertionError) as error:
        parser.exit(1, f"Comparación Dask no completada: {error}\n")
    print(f"Dask equivale a Pandas: {report['rows']:,} pedidos; {report['input_partitions']} particiones de entrada")
    print(f"CSV SHA-256 idéntico: {report['dask_csv_sha256']}")
    print(f"Informe: {args.output}")


if __name__ == "__main__":
    main()
