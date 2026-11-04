"""T13: versiona variables temporales y partición train/test sin entrenar."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import tempfile

import pandas as pd

from acquire_meituan import REVISION, verify_file
from prepare_meituan import DEFAULT_DATASET, DEFAULT_REPORT, DEFAULT_OUTPUT as DEFAULT_PROCESSED, file_hash, prepare
from delivery_ml import model_data


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data/splits/meituan" / REVISION / "t13-temporal-v1"


def prepare_partitions(output: Path, test_start: str) -> dict:
    source = DEFAULT_PROCESSED / "orders.csv"
    if output == DEFAULT_PROCESSED or output in DEFAULT_PROCESSED.parents or DEFAULT_PROCESSED in output.parents:
        raise ValueError("Las particiones deben estar separadas del dataset preparado")
    # Valida fuente, auditoría e implementación T08 antes de consumir su salida.
    prepared = prepare(DEFAULT_DATASET, DEFAULT_REPORT, DEFAULT_PROCESSED)
    cutoff = pd.Timestamp(test_start)
    if cutoff.tzinfo is None or pd.isna(cutoff) or cutoff.value % 1_000_000_000:
        raise ValueError("El corte debe tener zona horaria y segundos enteros")
    cutoff = cutoff.tz_convert("UTC")
    recipe = {
        "source_sha256": prepared["sha256"],
        "source_manifest_sha256": file_hash(DEFAULT_PROCESSED / "manifest.json"),
        "test_start_utc": cutoff.isoformat(),
        "implementation": {"model_data.py": file_hash(Path(model_data.__file__)),
                           "prepare_model_data.py": file_hash(Path(__file__))},
        "pandas_version": pd.__version__, "python_version": platform.python_version(),
    }
    if output.exists():
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        if manifest["recipe"] != recipe:
            raise ValueError("Cambió la receta/corte; usar una versión de salida nueva mediante --output")
        for info in manifest["partitions"].values():
            verify_file(output / info["file"], info["bytes"], info["sha256"])
        return manifest
    orders = pd.read_csv(source, float_precision="round_trip",
                         dtype={"order_id": "string", "source_waybill_id": "string"})
    parts = model_data.temporal_split(orders, test_start)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".t13-", dir=output.parent) as temporary:
        staging = Path(temporary) / "dataset"
        staging.mkdir()
        inventory = {}
        for name, frame in parts.items():
            path = staging / f"{name}.csv"
            frame.to_csv(path, index=False, lineterminator="\n")
            dates = pd.to_datetime(frame["platform_order_time"], unit="s", utc=True)
            inventory[name] = {
                "file": path.name, "rows": len(frame), "bytes": path.stat().st_size,
                "sha256": file_hash(path),
                "creation_min_utc": dates.min().isoformat() if len(frame) else None,
                "creation_max_utc": dates.max().isoformat() if len(frame) else None,
            }
        manifest = {
            "dataset_revision": REVISION, "partition_version": "t13-temporal-v1",
            "feature_version": "temporal-cyclic-v1", "recipe": recipe,
            "created_at_utc": datetime.now(timezone.utc).isoformat(), "python_version": platform.python_version(),
            "source_rows": len(orders), "partitions": inventory,
            "feature_columns": model_data.FEATURE_COLUMNS, "target": model_data.TARGET,
            "trace_columns_not_predictors": model_data.TRACE_COLUMNS,
            "context": {"request_hour_utc": "entero 0–23", "request_weekday_utc": "entero 0–6, lunes=0"},
            "transformation": "sin/cos de 2*pi*hora/24 y 2*pi*día/7; fija, sin fit ni estadísticas aprendidas",
            "split_policy": "train: creación y llegada antes del corte; test: creación desde el corte; purged: creados antes pero aún abiertos",
            "limitations": [
                "Versión experimental solo temporal; no diferencia rutas, países ni vehículos",
                "Coordenadas sin unidades confirmadas excluidas; sin distancia física",
                "El EDA previo estudió la cohorte completa; este test no es un experimento ciego a aquella exploración",
                "A partir de T13 reservar test para evaluación; no ajustar transformaciones, features o hiperparámetros con él",
                "Periodo corto, país extranjero y cohorte de entregas completadas; sin validación local",
            ],
            "training": "No realizado; sin baseline, métricas predictivas ni estimadores ajustados",
        }
        # Verificar también el aislamiento por waybill y la cobertura de filas.
        pairs = [("train", "test"), ("train", "purged"), ("test", "purged")]
        manifest["checks"] = {
            "disjoint_order_ids": all(set(parts[a]["order_id"]).isdisjoint(parts[b]["order_id"]) for a, b in pairs),
            "disjoint_waybills": all(set(parts[a]["source_waybill_id"]).isdisjoint(parts[b]["source_waybill_id"]) for a, b in pairs),
            "all_source_rows_accounted": sum(len(part) for part in parts.values()) == len(orders),
            "training_labels_before_test_start": bool(parts["train"]["arrive_time"].max() < cutoff.value // 1_000_000_000),
        }
        if not all(manifest["checks"].values()):
            raise ValueError("Fallo de aislamiento temporal/grupos")
        (staging / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        verify_file(source, prepared["bytes"], prepared["sha256"])
        staging.rename(output)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--test-start", default=model_data.DEFAULT_TEST_START)
    args = parser.parse_args()
    try:
        manifest = prepare_partitions(args.output.resolve(), args.test_start)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Preparación T13 no completada: {error}\n")
    print(f"T13: {args.output}; corte {manifest['recipe']['test_start_utc']}")
    for name, info in manifest["partitions"].items():
        print(f"{name}: {info['rows']:,} pedidos; SHA-256 {info['sha256']}")
    print("Cuatro features temporales; sin entrenamiento ni métricas predictivas.")


if __name__ == "__main__":
    main()
