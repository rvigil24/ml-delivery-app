"""T18: comparar cinco modelos en el mismo test, con decisiones previas de CV."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import pandas as pd
from sklearn.exceptions import ConvergenceWarning

from delivery_ml import evaluation
from delivery_ml.model_data import FEATURE_COLUMNS


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml/data"))
from acquire_meituan import REVISION
from prepare_meituan import file_hash
from prepare_model_data import DEFAULT_OUTPUT as DEFAULT_SPLITS, prepare_partitions


REPORT_DIR = ROOT / "data/reports/meituan" / REVISION


def verified_selection(path: Path, task: str, manifest_path: Path) -> dict:
    report = json.loads(path.read_text())
    provenance = report["provenance"]
    if (report["task"] != task or report["features"] != FEATURE_COLUMNS
            or not all(report["checks"].values())
            or provenance["split_manifest_sha256"] != file_hash(manifest_path)
            or provenance["lock_sha256"] != file_hash(ROOT / "uv.lock")
            or provenance["pyproject_sha256"] != file_hash(ROOT / "pyproject.toml")
            or provenance["python"] != platform.python_version()):
        raise ValueError(f"{task}: datos/receta distintos; reproducir su informe antes de evaluar")
    for name, digest in provenance["implementation"].items():
        if file_hash(ROOT / name) != digest:
            raise ValueError(f"{task}: implementación cambió; reproducir validación antes de evaluar")
    for name, version in provenance["versions"].items():
        if importlib.metadata.version(name) != version:
            raise ValueError(f"{task}: versión distinta de {name}")
    return report


def compare_models(splits: Path, cv_path: Path, mlp_path: Path, output: Path) -> dict:
    if output.suffix != ".json" or output == splits or splits in output.parents or output in splits.parents:
        raise ValueError("El informe debe ser .json y estar separado de las particiones")
    protected = {cv_path, mlp_path, cv_path.with_suffix(".md"), mlp_path.with_suffix(".md")}
    if output in protected or output.with_suffix(".md") in protected:
        raise ValueError("El informe no puede sobrescribir la selección previa")
    manifest_path = splits / "manifest.json"
    cutoff = json.loads(manifest_path.read_text())["recipe"]["test_start_utc"]
    manifest = prepare_partitions(splits, cutoff)
    if manifest["feature_columns"] != FEATURE_COLUMNS or not all(manifest["checks"].values()):
        raise ValueError("Se requiere el contrato temporal verificado de T13")
    cv = verified_selection(cv_path, "T16", manifest_path)
    mlp = verified_selection(mlp_path, "T17", manifest_path)
    for result in cv["models"].values():
        best = min(range(len(result["candidates"])), key=lambda i: result["candidates"][i]["mean_mae_minutes"])
        if result["best_index"] != best or result["best_parameters"] != result["candidates"][best]["parameters"]:
            raise ValueError("La selección T16 no coincide con el menor MAE interno")
    curve = mlp["mean_validation_mae_by_epoch"]
    epochs = curve.index(min(curve)) + 1
    if epochs != mlp["selected_epochs"]:
        raise ValueError("La selección T17 no coincide con la época de menor MAE interno")
    parameters = {name: result["best_parameters"] for name, result in cv["models"].items()}

    def load(name):
        info = manifest["partitions"][name]
        frame = pd.read_csv(splits / info["file"], float_precision="round_trip",
                            dtype={"order_id": "string", "source_waybill_id": "string"})
        if len(frame) != info["rows"]:
            raise ValueError(f"Conteo distinto: {name}")
        return frame

    train = load("train")
    boundary = pd.Timestamp(cutoff).value // 1_000_000_000
    if train["arrive_time"].max() >= boundary:
        raise ValueError("Train contiene etiquetas futuras")
    # Se congelan todas las configuraciones y se ajustan antes de cargar test.
    fitted = evaluation.fit_frozen_models(train, parameters, epochs)
    training_metrics = evaluation.evaluate_models(fitted, train)
    test = load("test")
    if (test["platform_order_time"].min() < boundary
            or any(not set(train[name]).isdisjoint(test[name]) for name in ("order_id", "source_waybill_id"))):
        raise ValueError("Test temporal o IDs incompatibles")
    test_metrics = evaluation.evaluate_models(fitted, test)
    for part in manifest["partitions"].values():
        if file_hash(splits / part["file"]) != part["sha256"]:
            raise ValueError("Una partición cambió durante la evaluación")
    report = {
        "task": "T18", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "features": FEATURE_COLUMNS, "feature_version": manifest["feature_version"],
        "configuration": {"parameters_from_T16": parameters, "mlp_epochs_from_T17": epochs},
        "metrics": {"train": training_metrics, "test": test_metrics},
        "checks": {"fit_before_loading_test": True, "no_tuning_with_test": True,
                   "same_test_rows_for_all_models": True, "ids_disjoint": True, "input_hashes_unchanged": True},
        "provenance": {
            "selection_reports": {str(cv_path): file_hash(cv_path), str(mlp_path): file_hash(mlp_path)},
            "split_manifest_sha256": file_hash(manifest_path),
            "partition_sha256": {name: part["sha256"] for name, part in manifest["partitions"].items()},
            "implementation": {str(path.relative_to(ROOT)): file_hash(path) for path in
                               [Path(__file__), Path(evaluation.__file__)]},
            "lock_sha256": file_hash(ROOT / "uv.lock"), "pyproject_sha256": file_hash(ROOT / "pyproject.toml"),
            "versions": {name: importlib.metadata.version(name) for name in ["pandas", "numpy", "scikit-learn", "torch"]},
            "python": platform.python_version(),
        },
        "limitations": [
            "Test observado en T18; no usarlo para cambiar parámetros, features ni épocas y volver a presentarlo como independiente",
            "Reejecutar la misma receta reproduce la evaluación, no crea una nueva prueba independiente",
            "EDA global previo y baseline T14 ya observaron información de test; no es un experimento completamente ciego",
            "Dos fechas de test con cobertura parcial; errores por día describen esta cohorte, no intervalos de confianza",
            "Datos chinos, cohorte completada/inmediata, pocas fechas y variables solo temporales; sin validación local ni por vehículo",
            "MAE/RMSE son minutos; R2 no es porcentaje de exactitud; sesgo firmado usa predicción menos observado",
            "T19 decidirá selección/persistencia; no se guardan pesos ni se integra API/AWS aquí",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# T18 — Comparación sobre el mismo test", "", "Configuraciones congeladas por CV antes de cargar test.", "",
             "| Modelo | Pedidos test | MAE (min) | RMSE (min) | R² | Sesgo (min) | P95 error absoluto (min) |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for name, item in test_metrics.items():
        lines.append(f"| {name} | {item['rows']:,} | {item['mae_minutes']:.6f} | {item['rmse_minutes']:.6f} | "
                     f"{item['r2']} | {item['mean_signed_error_minutes']:.6f} | {item['p95_absolute_error_minutes']:.6f} |")
    lines += ["", *report["limitations"], "", "Reproducir: `uv run --locked python ml/experiments/compare_models.py`."]
    output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--validation-report", type=Path, default=REPORT_DIR / "t16_validation.json")
    parser.add_argument("--mlp-report", type=Path, default=REPORT_DIR / "t17_mlp.json")
    parser.add_argument("--output", type=Path, default=REPORT_DIR / "t18_comparison.json")
    args = parser.parse_args()
    try:
        report = compare_models(args.splits.resolve(), args.validation_report.resolve(), args.mlp_report.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError, ConvergenceWarning) as error:
        parser.exit(1, f"Comparación no completada: {error}\n")
    for name, result in report["metrics"]["test"].items():
        r2 = f"{result['r2']:.6f}" if result["r2"] is not None else "no definido"
        print(f"{name}: test n={result['rows']:,}, MAE={result['mae_minutes']:.6f} min, RMSE={result['rmse_minutes']:.6f} min, R2={r2}")
    print(f"Informe: {args.output}; sin retuning ni persistencia final.")


if __name__ == "__main__":
    main()
