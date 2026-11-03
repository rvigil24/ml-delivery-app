"""T08: materializa la cohorte Pandas y su manifiesto, sin entrenar ni subir archivos."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile

import pandas as pd

from acquire_meituan import CSV_NAME, DEFAULT_OUTPUT as DEFAULT_DATASET, EXPECTED, REVISION, verify_file
from delivery_ml import preparation


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "data" / "reports" / "meituan" / REVISION / "t07_audit.json"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "meituan" / REVISION / "t08-v1"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare(dataset: Path, audit: Path, output: Path) -> dict:
    source = dataset / CSV_NAME
    integrity = verify_file(source, *EXPECTED[CSV_NAME])
    report = json.loads(audit.read_text(encoding="utf-8"))
    audit_sha256 = file_hash(audit)
    if report["decision"] != "APROBADO_CON_CONDICIONES" or report["source"]["sha256"] != integrity["sha256"]:
        raise ValueError("Se requiere una auditoría aprobada para este original")
    implementation = {
        "preparation.py": file_hash(Path(preparation.__file__)),
        "prepare_meituan.py": file_hash(Path(__file__)),
    }
    if output.exists():
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        if (
            manifest["source_sha256"] != integrity["sha256"]
            or manifest["implementation"] != implementation
            or manifest.get("audit_sha256") != audit_sha256
        ):
            raise ValueError("Cambió la receta o fuente; usar una versión de salida nueva")
        verify_file(output / "orders.csv", manifest["bytes"], manifest["sha256"])
        return manifest

    raw = pd.read_csv(source, dtype={"order_id": "string", "waybill_id": "string"})
    orders = preparation.prepare_orders(raw)
    if len(orders) != report["cohort_proposal"]["eligible_orders"]:
        raise ValueError("El conteo Pandas no coincide con la auditoría T07")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".t08-", dir=output.parent) as temporary:
        staging = Path(temporary) / "dataset"
        staging.mkdir()
        csv_path = staging / "orders.csv"
        orders.to_csv(csv_path, index=False, lineterminator="\n")
        manifest = {
            "source_revision": REVISION, "source_sha256": integrity["sha256"],
            "audit_sha256": audit_sha256,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "pipeline_version": "t08-v1", "pandas_version": pd.__version__,
            "implementation": implementation,
            "rows": len(orders), "columns": list(orders.columns),
            "bytes": csv_path.stat().st_size, "sha256": file_hash(csv_path),
            "target": "time_taken_min = (arrive_time - platform_order_time) / 60",
            "timezone": "UTC; weekday: lunes=0, domingo=6",
            "candidate_features": ["request_hour_utc", "request_weekday_utc"],
            "geography": "Columnas *_raw preservadas; unidades pendientes, sin distancia física",
            "license": "Conservar License.txt del original y las condiciones de Meituan",
            "training": "No realizado; sin imputación, escalado ni partición aprendida",
        }
        (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        staging.rename(output)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--audit", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        manifest = prepare(args.dataset, args.audit, args.output)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Preparación no completada: {error}\n")
    print(f"Cohorte: {args.output / 'orders.csv'}")
    print(f"Filas: {manifest['rows']}; SHA-256: {manifest['sha256']}")


if __name__ == "__main__":
    main()
