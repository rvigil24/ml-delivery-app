"""T14: ajusta una referencia con train y registra errores observados en test."""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import pandas as pd
import sklearn

from delivery_ml import baseline
from delivery_ml.model_data import DEFAULT_TEST_START, FEATURE_COLUMNS


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml/data"))
from acquire_meituan import REVISION
from prepare_model_data import DEFAULT_OUTPUT as DEFAULT_SPLITS, prepare_partitions


DEFAULT_OUTPUT = ROOT / "data/reports/meituan" / REVISION / "t14_baseline.json"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(splits: Path, output: Path) -> dict:
    if output.suffix != ".json":
        raise ValueError("--output debe ser un archivo .json; el informe Markdown usa el mismo nombre")
    if output == splits or splits in output.parents or output in splits.parents:
        raise ValueError("El informe debe estar separado de las particiones")
    manifest_path = splits / "manifest.json"
    cutoff = (json.loads(manifest_path.read_text())["recipe"]["test_start_utc"]
              if manifest_path.is_file() else DEFAULT_TEST_START)
    manifest = prepare_partitions(splits, cutoff)
    if manifest["feature_columns"] != FEATURE_COLUMNS or not all(manifest["checks"].values()):
        raise ValueError("Se requiere el contrato temporal y aislamiento de T13")

    def load(name):
        info = manifest["partitions"][name]
        frame = pd.read_csv(splits / info["file"], float_precision="round_trip",
                            dtype={"order_id": "string", "source_waybill_id": "string"})
        if len(frame) != info["rows"]:
            raise ValueError(f"Conteo distinto del manifiesto: {name}")
        return frame

    train = load("train")
    model = baseline.fit_baseline(train)
    constant = float(model.constant_.ravel()[0])
    training_metrics = baseline.evaluate_baseline(model, train)
    # El test se carga para evaluar el único baseline ya ajustado.
    test = load("test")
    cutoff_seconds = pd.Timestamp(cutoff).value // 1_000_000_000
    if (train["arrive_time"].max() >= cutoff_seconds or test["platform_order_time"].min() < cutoff_seconds
            or not set(train["order_id"]).isdisjoint(test["order_id"])
            or not set(train["source_waybill_id"]).isdisjoint(test["source_waybill_id"])):
        raise ValueError("Particiones mezcladas o etiquetas de entrenamiento posteriores al corte")
    test_metrics = baseline.evaluate_baseline(model, test)
    if float(model.constant_.ravel()[0]) != constant:
        raise ValueError("El baseline cambió durante la evaluación")
    report = {
        "task": "T14", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "estimator": "sklearn.dummy.DummyRegressor", "strategy": "median",
        "primary_metric": "MAE", "strategy_selection": "Fijada antes de evaluar test, sin búsqueda de alternativas",
        "constant_minutes": constant, "constant_source": "Mediana exclusivamente de y_train",
        "features": FEATURE_COLUMNS, "feature_version": manifest["feature_version"],
        "uses_feature_values": False,
        "metrics": {"train": training_metrics, "test": test_metrics},
        "split": {"test_start_utc": cutoff, "partition_version": manifest["partition_version"],
                  "purged_rows_not_used": manifest["partitions"]["purged"]["rows"]},
        "provenance": {
            "lock_sha256": file_hash(ROOT / "uv.lock"), "pyproject_sha256": file_hash(ROOT / "pyproject.toml"),
            "split_manifest_sha256": file_hash(manifest_path),
            "train_sha256": manifest["partitions"]["train"]["sha256"],
            "test_sha256": manifest["partitions"]["test"]["sha256"],
            "implementation": {"baseline.py": file_hash(Path(baseline.__file__)),
                               "evaluate_baseline.py": file_hash(Path(__file__))},
            "versions": {"python": platform.python_version(), "pandas": pd.__version__, "scikit_learn": sklearn.__version__,
                         "numpy": importlib.metadata.version("numpy"), "scipy": importlib.metadata.version("scipy")},
        },
        "checks": {"fit_only_train": True, "constant_unchanged_during_evaluation": True,
                   "ids_disjoint": True, "training_labels_before_test_start": True},
        "limitations": [
            "Referencia que ignora valores de features; no es un modelo operativo ni diferencia rutas/vehículos",
            "MAE/RMSE son errores en minutos, no porcentajes de exactitud ni garantías de entrega",
            "Test observado aquí solo para la referencia fija; no ajustar modelos futuros ni elegir hiperparámetros con sus resultados",
            "EDA anterior exploró la cohorte completa; test no ciego a aquella exploración",
            "Periodo corto, cohorte completada y datos chinos; no valida generalización en El Salvador",
            "Sin persistir un modelo final, servir API, entrenar familias T15 o modificar AWS",
        ],
    }
    # Confirmar también que la evaluación no modificó archivos de entrada.
    for name in ("train", "test", "purged"):
        info = manifest["partitions"][name]
        if file_hash(splits / info["file"]) != info["sha256"]:
            raise ValueError("Una partición cambió durante la evaluación")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = ["# T14 — Baseline constante", "", f"Predice {constant:.6f} minutos, mediana calculada solo con entrenamiento.", "",
             "| Conjunto | Pedidos | MAE (min) | RMSE (min) |", "|---|---:|---:|---:|"]
    for name, info in report["metrics"].items():
        lines.append(f"| {name} | {info['rows']:,} | {info['mae_minutes']:.6f} | {info['rmse_minutes']:.6f} |")
    lines += ["", "## Alcance", "", *report["limitations"], "",
              "Se compara contra esta referencia fija en tareas posteriores; no se eligió entre estrategias por el test.", "",
              "Reproducir: `uv run --locked python ml/experiments/evaluate_baseline.py`.", "",
              "[DummyRegressor: documentación oficial](https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyRegressor.html)."]
    output.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = evaluate(args.splits.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Baseline no completado: {error}\n")
    print(f"Baseline mediana de train: {report['constant_minutes']:.6f} min")
    for name, info in report["metrics"].items():
        print(f"{name}: n={info['rows']:,}, MAE={info['mae_minutes']:.6f} min, RMSE={info['rmse_minutes']:.6f} min")
    print(f"Informe: {args.output}")


if __name__ == "__main__":
    main()
