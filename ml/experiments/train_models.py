"""T15: entrena tres familias con todo train; no evalúa ni selecciona con test."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
from time import perf_counter

import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from delivery_ml import models
from delivery_ml.baseline import validated_xy
from delivery_ml.model_data import FEATURE_COLUMNS


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml/data"))
from acquire_meituan import REVISION
from prepare_meituan import file_hash
from prepare_model_data import DEFAULT_OUTPUT as DEFAULT_SPLITS, prepare_partitions


DEFAULT_OUTPUT = ROOT / "data/reports/meituan" / REVISION / "t15_models.json"


def train_models(splits: Path, output: Path) -> dict:
    if output.suffix != ".json" or output == splits or splits in output.parents or output in splits.parents:
        raise ValueError("El informe debe ser .json y estar separado de las particiones")
    manifest_path = splits / "manifest.json"
    cutoff = json.loads(manifest_path.read_text())["recipe"]["test_start_utc"]
    manifest = prepare_partitions(splits, cutoff)
    if manifest["feature_columns"] != FEATURE_COLUMNS or not all(manifest["checks"].values()):
        raise ValueError("Se requiere el contrato temporal verificado de T13")
    info = manifest["partitions"]["train"]
    # Los otros CSV se verifican por hash, pero no se cargan para entrenar/evaluar.
    train = pd.read_csv(splits / info["file"], float_precision="round_trip",
                        dtype={"order_id": "string", "source_waybill_id": "string"})
    if len(train) != info["rows"] or train["arrive_time"].max() >= pd.Timestamp(cutoff).value // 1_000_000_000:
        raise ValueError("Train no coincide con el manifiesto o contiene etiquetas futuras")
    x, y = validated_xy(train)
    results = {}
    for name, model in models.build_models().items():
        started = perf_counter()
        models.fit_model(model, train)
        fit_seconds = perf_counter() - started
        prediction = model.predict(x)
        results[name] = {
            "family": models.FAMILIES[name], "training_rows": len(train),
            "steps": [{"class": type(step).__name__, "parameters": step.get_params(deep=False)}
                      for _, step in model.steps],
            "training_mae_minutes": float(mean_absolute_error(y, prediction)),
            "training_rmse_minutes": float(root_mean_squared_error(y, prediction)),
            "fit_seconds": fit_seconds,
        }
    for part in manifest["partitions"].values():
        if file_hash(splits / part["file"]) != part["sha256"]:
            raise ValueError("Una partición cambió durante el entrenamiento")
    report = {
        "task": "T15", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_version": manifest["feature_version"], "features": FEATURE_COLUMNS,
        "test_start_utc": cutoff, "models": results,
        "checks": {"fit_only_train": True, "test_not_loaded_or_evaluated": True,
                   "all_training_rows_used": True, "input_hashes_unchanged": True},
        "provenance": {
            "split_manifest_sha256": file_hash(manifest_path),
            "partition_sha256": {name: part["sha256"] for name, part in manifest["partitions"].items()},
            "implementation": {str(path.relative_to(ROOT)): file_hash(path) for path in
                               [Path(__file__), Path(models.__file__), ROOT / "ml/src/delivery_ml/baseline.py"]},
            "lock_sha256": file_hash(ROOT / "uv.lock"), "pyproject_sha256": file_hash(ROOT / "pyproject.toml"),
            "versions": {name: importlib.metadata.version(name) for name in ["pandas", "numpy", "scipy", "scikit-learn"]},
            "python": platform.python_version(), "platform": platform.platform(),
        },
        "limitations": [
            "Errores de entrenamiento: no estiman generalización ni eligen un ganador",
            "Configuraciones iniciales fijas; CV/tuning T16 y evaluación posterior T18 pendientes",
            "LinearSVR usa kernel lineal; no equivale a SVR con kernel RBF",
            "Solo contexto temporal: no distingue rutas, distancias ni vehículos",
            "Datos chinos de un periodo corto; sin validación para El Salvador; EDA previo global",
            "Sin persistir modelo final (T19), API ni modificaciones AWS",
            "Tiempos de una ejecución local: incluyen validación de entradas y fit, sin comparación estadística",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# T15 — Tres familias ML", "", "Resultados sobre entrenamiento, no sobre test.", "",
             "| Modelo | Pedidos | MAE train (min) | RMSE train (min) | Ajuste (s) |",
             "|---|---:|---:|---:|---:|"]
    for name, result in results.items():
        lines.append(f"| {name} | {result['training_rows']:,} | {result['training_mae_minutes']:.6f} | "
                     f"{result['training_rmse_minutes']:.6f} | {result['fit_seconds']:.3f} |")
    lines += ["", *report["limitations"], "", "Reproducir: `uv run --locked python ml/experiments/train_models.py`."]
    output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = train_models(args.splits.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError, ConvergenceWarning) as error:
        parser.exit(1, f"Entrenamiento no completado: {error}\n")
    for name, result in report["models"].items():
        print(f"{name}: n={result['training_rows']:,}, MAE train={result['training_mae_minutes']:.6f} min, "
              f"RMSE train={result['training_rmse_minutes']:.6f} min; fit={result['fit_seconds']:.3f} s")
    print(f"Informe: {args.output}; test sin evaluar, sin seleccionar modelo final.")


if __name__ == "__main__":
    main()
