"""T16: valida y optimiza dentro de train, sin abrir el test reservado."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import pandas as pd
from sklearn.exceptions import ConvergenceWarning

from delivery_ml import validation, models
from delivery_ml.model_data import FEATURE_COLUMNS


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml/data"))
from acquire_meituan import REVISION
from prepare_meituan import file_hash
from prepare_model_data import DEFAULT_OUTPUT as DEFAULT_SPLITS, prepare_partitions


DEFAULT_OUTPUT = ROOT / "data/reports/meituan" / REVISION / "t16_validation.json"


def tune_models(splits: Path, output: Path) -> dict:
    if output.suffix != ".json" or output == splits or splits in output.parents or output in splits.parents:
        raise ValueError("El informe debe ser .json y estar separado de las particiones")
    manifest_path = splits / "manifest.json"
    cutoff = json.loads(manifest_path.read_text())["recipe"]["test_start_utc"]
    manifest = prepare_partitions(splits, cutoff)
    if manifest["feature_columns"] != FEATURE_COLUMNS or not all(manifest["checks"].values()):
        raise ValueError("Se requiere el contrato temporal verificado de T13")
    info = manifest["partitions"]["train"]
    train = pd.read_csv(splits / info["file"], float_precision="round_trip",
                        dtype={"order_id": "string", "source_waybill_id": "string"})
    if len(train) != info["rows"] or train["arrive_time"].max() >= pd.Timestamp(cutoff).value // 1_000_000_000:
        raise ValueError("Train no coincide con el manifiesto o contiene etiquetas futuras")
    report = validation.search_models(train)
    for part in manifest["partitions"].values():
        if file_hash(splits / part["file"]) != part["sha256"]:
            raise ValueError("Una partición cambió durante la validación")
    report["checks"]["input_hashes_unchanged"] = True
    report.update({
        "task": "T16", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_version": manifest["feature_version"], "features": FEATURE_COLUMNS,
        "outer_test_start_utc": cutoff,
        "provenance": {
            "split_manifest_sha256": file_hash(manifest_path),
            "partition_sha256": {name: part["sha256"] for name, part in manifest["partitions"].items()},
            "implementation": {str(path.relative_to(ROOT)): file_hash(path) for path in
                               [Path(__file__), Path(validation.__file__), Path(models.__file__),
                                ROOT / "ml/src/delivery_ml/baseline.py"]},
            "lock_sha256": file_hash(ROOT / "uv.lock"), "pyproject_sha256": file_hash(ROOT / "pyproject.toml"),
            "versions": {name: importlib.metadata.version(name) for name in ["pandas", "numpy", "scipy", "scikit-learn"]},
            "python": platform.python_version(), "platform": platform.platform(),
        },
        "limitations": [
            "CV interna usada para seleccionar parámetros; no es evaluación independiente del modelo elegido",
            "MAE/RMSE medios dan el mismo peso a cada día; no son errores agrupados por pedido",
            "Búsqueda acotada, sin afirmar óptimo global; LinearRegression y baseline son controles sin tuning",
            "Se reajusta cada configuración elegida solo con todo train, en memoria; sin modelo final persistido",
            "Tres días de validación, datos chinos, contexto solo temporal, EDA global previo; sin validación local",
            "Test reservado sin evaluar; MLP T17, comparación posterior T18 y persistencia T19 pendientes",
        ],
    })
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# T16 — Validación temporal interna", "", report["selection"], "",
             "| Modelo | Parámetros elegidos | MAE CV (min) | RMSE CV (min) |",
             "|---|---|---:|---:|"]
    for name, result in report["models"].items():
        best = result["candidates"][result["best_index"]]
        lines.append(f"| {name} | {json.dumps(result['best_parameters'])} | {best['mean_mae_minutes']:.6f} | {best['mean_rmse_minutes']:.6f} |")
    lines += ["", *report["limitations"], "", "Reproducir: `uv run --locked python ml/experiments/tune_models.py`."]
    output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = tune_models(args.splits.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError, ConvergenceWarning) as error:
        parser.exit(1, f"Validación no completada: {error}\n")
    for name, result in report["models"].items():
        print(f"{name}: MAE CV={result['best_mean_mae_minutes']:.6f} min; parámetros={result['best_parameters']}")
    print(f"Informe: {args.output}; tres folds internos, sin evaluar test.")


if __name__ == "__main__":
    main()
