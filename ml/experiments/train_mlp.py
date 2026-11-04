"""T17: aprende épocas en validación interna y reajusta la MLP solo con train."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from delivery_ml import mlp
from delivery_ml.model_data import FEATURE_COLUMNS
from delivery_ml.validation import expanding_day_folds


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml/data"))
from acquire_meituan import REVISION
from prepare_meituan import file_hash
from prepare_model_data import DEFAULT_OUTPUT as DEFAULT_SPLITS, prepare_partitions


DEFAULT_OUTPUT = ROOT / "data/reports/meituan" / REVISION / "t17_mlp.json"


def train_mlp(splits: Path, output: Path) -> dict:
    if output.suffix != ".json" or output == splits or splits in output.parents or output in splits.parents:
        raise ValueError("El informe debe ser .json y estar separado de las particiones")
    manifest_path = splits / "manifest.json"
    cutoff = json.loads(manifest_path.read_text())["recipe"]["test_start_utc"]
    manifest = prepare_partitions(splits, cutoff)
    if manifest["feature_columns"] != FEATURE_COLUMNS or not all(manifest["checks"].values()):
        raise ValueError("Se requiere el contrato temporal verificado de T13")
    train = pd.read_csv(splits / manifest["partitions"]["train"]["file"], float_precision="round_trip",
                        dtype={"order_id": "string", "source_waybill_id": "string"})
    if len(train) != manifest["partitions"]["train"]["rows"] or train["arrive_time"].max() >= pd.Timestamp(cutoff).value // 1_000_000_000:
        raise ValueError("Train no coincide con el manifiesto o contiene etiquetas futuras")
    folds = []
    for fit, holdout in expanding_day_folds(train):
        model = mlp.SmallMLPRegressor().fit(train.iloc[fit], validation=train.iloc[holdout])
        folds.append({"training_rows": len(fit), "validation_rows": len(holdout),
                      "validation_day_utc": pd.to_datetime(train.iloc[holdout]["platform_order_time"].min(), unit="s", utc=True).date().isoformat(),
                      "history": model.history})
    mean_mae = np.mean([[row["validation_mae_minutes"] for row in fold["history"]] for fold in folds], axis=0)
    best_epoch = int(np.argmin(mean_mae)) + 1
    final = mlp.SmallMLPRegressor().fit(train, epochs=best_epoch)
    prediction = final.predict(train)
    for part in manifest["partitions"].values():
        if file_hash(splits / part["file"]) != part["sha256"]:
            raise ValueError("Una partición cambió durante el entrenamiento")
    report = {
        "task": "T17", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "architecture": "4 -> 16 ReLU -> 8 ReLU -> 1 lineal", "parameters": sum(p.numel() for p in final.network.parameters()),
        "features": FEATURE_COLUMNS, "feature_version": manifest["feature_version"],
        "configuration": {"device": "cpu", "threads": 2, "seed": mlp.SEED,
                          "max_epochs": mlp.MAX_EPOCHS, "batch_size": mlp.BATCH_SIZE,
                          "optimizer": "Adam", "learning_rate": mlp.LEARNING_RATE, "loss": "MSE sobre target estandarizado"},
        "folds": folds, "mean_validation_mae_by_epoch": mean_mae.tolist(),
        "selected_epochs": best_epoch, "selected_cv_mae_minutes": float(mean_mae[best_epoch - 1]),
        "selected_cv_rmse_minutes": float(np.mean([f["history"][best_epoch-1]["validation_rmse_minutes"] for f in folds])),
        "refit_training_rows": len(train), "refit_history": final.history,
        "training_mae_minutes": float(mean_absolute_error(train["time_taken_min"], prediction)),
        "training_rmse_minutes": float(root_mean_squared_error(train["time_taken_min"], prediction)),
        "selection": "Menor MAE medio de tres días; empate: primera época. Reajuste desde cero solo con todo train.",
        "checks": {"test_not_loaded_or_evaluated": True, "scalers_fit_only_training_fold": True,
                   "refit_only_full_train": True, "input_hashes_unchanged": True},
        "provenance": {
            "split_manifest_sha256": file_hash(manifest_path),
            "partition_sha256": {name: part["sha256"] for name, part in manifest["partitions"].items()},
            "implementation": {str(path.relative_to(ROOT)): file_hash(path) for path in
                               [Path(__file__), Path(mlp.__file__), ROOT / "ml/src/delivery_ml/validation.py",
                                ROOT / "ml/src/delivery_ml/baseline.py"]},
            "lock_sha256": file_hash(ROOT / "uv.lock"), "pyproject_sha256": file_hash(ROOT / "pyproject.toml"),
            "versions": {name: importlib.metadata.version(name) for name in ["torch", "pandas", "numpy", "scikit-learn"]},
            "python": platform.python_version(),
        },
        "limitations": ["CV usada para seleccionar épocas, no evaluación independiente; entrenamiento tampoco mide generalización",
                        "Semilla/determinismo CPU no garantizan igualdad entre plataformas o versiones",
                        "Cohorte china, pocos días, contexto solo temporal y EDA global previo; sin validación local",
                        "T18 comparación posterior y T19 selección/persistencia pendientes; sin API ni AWS"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    output.with_suffix(".md").write_text(
        f"# T17 — MLP pequeña\n\n{report['architecture']}; {report['parameters']} parámetros.\n\n"
        f"Épocas elegidas: {best_epoch}; MAE CV: {report['selected_cv_mae_minutes']:.6f} min; "
        f"RMSE CV: {report['selected_cv_rmse_minutes']:.6f} min.\n\n" + "\n".join(report["limitations"]) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        report = train_mlp(args.splits.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"MLP no completada: {error}\n")
    print(f"MLP: {report['parameters']} parámetros, {report['selected_epochs']} épocas; MAE CV={report['selected_cv_mae_minutes']:.6f} min; RMSE CV={report['selected_cv_rmse_minutes']:.6f} min")
    print(f"Informe: {args.output}; sin evaluar test ni persistir modelo final.")


if __name__ == "__main__":
    main()
