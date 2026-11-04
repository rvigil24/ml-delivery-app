"""T19: seleccionar por CV, guardar pipeline académico y verificar su recarga."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from delivery_ml import artifact
from delivery_ml.baseline import validated_xy
from delivery_ml.evaluation import regression_metrics
from delivery_ml.model_data import CONTEXT_COLUMNS, FEATURE_COLUMNS, temporal_features
from delivery_ml.models import build_models


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml/data"))
from acquire_meituan import REVISION
from prepare_model_data import DEFAULT_OUTPUT as DEFAULT_SPLITS, prepare_partitions
from compare_models import REPORT_DIR, verified_selection


DEFAULT_OUTPUT = ROOT / "models/delivery-duration/meituan-temporal-rf-v1"


def export_model(splits: Path, reports: Path, output: Path) -> dict:
    if any(output == parent or output in parent.parents or parent in output.parents for parent in (splits, reports)):
        raise ValueError("El artefacto debe estar separado de datos e informes")
    manifest_path = splits / "manifest.json"
    cutoff = json.loads(manifest_path.read_text())["recipe"]["test_start_utc"]
    manifest = prepare_partitions(splits, cutoff)
    if manifest["feature_columns"] != FEATURE_COLUMNS or not all(manifest["checks"].values()):
        raise ValueError("Se requiere el contrato temporal verificado de T13")
    paths = {task: reports / name for task, name in
             [("T16", "t16_validation.json"), ("T17", "t17_mlp.json"), ("T18", "t18_comparison.json")]}
    evidence = {task: verified_selection(path, task, manifest_path) for task, path in paths.items()}
    for name, digest in evidence["T18"]["provenance"]["selection_reports"].items():
        if artifact.file_hash(Path(name)) != digest:
            raise ValueError("La comparación T18 no corresponde a los informes de selección actuales")
    selected, scores = artifact.select_by_cv(evidence["T16"], evidence["T17"])
    if selected != "random_forest":
        raise ValueError("Esta versión exporta el bosque elegido; un ganador distinto requiere otra receta/versionado")
    result = evidence["T16"]["models"][selected]
    best = min(range(len(result["candidates"])), key=lambda i: result["candidates"][i]["mean_mae_minutes"])
    if (result["best_index"] != best or result["best_parameters"] != result["candidates"][best]["parameters"]
            or scores[selected] != result["candidates"][best]["mean_mae_minutes"]):
        raise ValueError("Configuración elegida incompatible con CV")
    if evidence["T18"]["configuration"]["parameters_from_T16"][selected] != result["best_parameters"]:
        raise ValueError("La configuración evaluada en T18 no coincide")
    recipe = {
        "train_sha256": manifest["partitions"]["train"]["sha256"],
        "split_manifest_sha256": artifact.file_hash(manifest_path),
        "selected_model": selected, "parameters": result["best_parameters"], "cv_scores": scores,
        "implementation": {name: digest for report in evidence.values()
                           for name, digest in report["provenance"]["implementation"].items()},
        "export_implementation": {str(path.relative_to(ROOT)): artifact.file_hash(path) for path in
                                  [Path(__file__), Path(artifact.__file__)]},
        "lock_sha256": artifact.file_hash(ROOT / "uv.lock"),
        "pyproject_sha256": artifact.file_hash(ROOT / "pyproject.toml"),
        "environment": artifact.environment_versions(),
    }
    if output.exists():
        metadata = json.loads((output / "metadata.json").read_text())
        if metadata["recipe"] != recipe:
            raise ValueError("Cambió la receta; usar una nueva versión mediante --output")
        artifact.load_pipeline(output)
        return metadata
    train = pd.read_csv(splits / manifest["partitions"]["train"]["file"], float_precision="round_trip",
                        dtype={"order_id": "string", "source_waybill_id": "string"})
    if len(train) != manifest["partitions"]["train"]["rows"] or train["arrive_time"].max() >= pd.Timestamp(cutoff).value // 1_000_000_000:
        raise ValueError("Train incompatible con el manifiesto/corte")
    _, target = validated_xy(train)
    model = build_models()[selected].set_params(**result["best_parameters"])
    pipeline = Pipeline([("temporal_features", FunctionTransformer(temporal_features, validate=False)),
                         ("estimator", model)])
    pipeline.fit(train[CONTEXT_COLUMNS], target)
    prediction = pipeline.predict(train[CONTEXT_COLUMNS])
    training = regression_metrics(target, prediction)
    for metric in ("mae_minutes", "rmse_minutes"):
        if abs(training[metric] - evidence["T18"]["metrics"]["train"][selected][metric]) > 1e-9:
            raise ValueError("El reajuste no reproduce el modelo evaluado en T18")
    test_metrics = evidence["T18"]["metrics"]["test"][selected]
    metadata = {
        "schema": artifact.ARTIFACT_SCHEMA, "model_version": output.name, "task": "T19",
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "selected_model": selected,
        "selection": "Menor MAE de CV interna entre baseline, tres ML y MLP; test no decide el ganador",
        "context_columns": CONTEXT_COLUMNS, "feature_columns": FEATURE_COLUMNS,
        "context_contract": {"request_hour_utc": "entero 0–23", "request_weekday_utc": "entero 0–6, lunes=0"},
        "feature_version": manifest["feature_version"], "target": "time_taken_min", "target_unit": "minutes",
        "dataset_revision": REVISION, "training_rows": len(train), "test_metrics_from_T18": test_metrics,
        "training_metrics": training, "environment": artifact.environment_versions(), "recipe": recipe,
        "checks": {"selected_by_cv_only": True, "fit_only_train": True, "test_not_loaded": True,
                   "round_trip_predictions_atol_1e_12": True, "training_metrics_match_T18": True},
        "use": "Modelo académico local; no validación operativa en El Salvador ni por vehículo",
        "publication": "Sin publicación externa/S3; revisión de términos y autorización pendientes antes de subir",
    }
    card = (f"# {output.name}\n\nRandom Forest de profundidad 6, elegido por MAE CV ({scores[selected]:.6f} min).\n\n"
            f"Train: {len(train):,} pedidos. Test T18: MAE {test_metrics['mae_minutes']:.6f} min, "
            f"RMSE {test_metrics['rmse_minutes']:.6f} min, R² {test_metrics['r2']:.6f}.\n\n"
            "La MLP tuvo MAE de test apenas menor; no se usó test para cambiar la selección por CV.\n\n"
            "El pipeline recibe hora UTC (0–23) y día UTC (lunes=0, domingo=6), transforma con seno/coseno "
            "y devuelve minutos. No recibe IDs, llegada, distancias o vehículo.\n\n"
            "Solo uso académico local: datos chinos, período corto, cohorte completada/inmediata, EDA previo global, "
            "R² bajo y errores relevantes. Sin intervalos predictivos ni garantía de entrega.\n\n"
            "Datos Meituan, revisión " + REVISION + ". Términos/atribución en docs/DATA_ML.md; "
            "no se acredita autorización de publicación del modelo ni se sube a AWS.\n\n"
            "Cargar únicamente bundles propios de confianza: pickle puede ejecutar código. "
            "Usar las mismas versiones; hashes comprueban integridad, no autentican al autor.\n")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".t19-", dir=output.parent) as temporary:
        staging = Path(temporary) / "bundle"
        metadata = artifact.write_bundle(staging, pipeline, metadata, evidence, card)
        restored = artifact.load_pipeline(staging)
        np.testing.assert_allclose(restored.predict(train[CONTEXT_COLUMNS]), prediction, rtol=0, atol=1e-12)
        for info in manifest["partitions"].values():
            if artifact.file_hash(splits / info["file"]) != info["sha256"]:
                raise ValueError("Una partición cambió durante la exportación")
        staging.rename(output)
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--reports", type=Path, default=REPORT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        metadata = export_model(args.splits.resolve(), args.reports.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError, AssertionError) as error:
        parser.exit(1, f"Exportación no completada: {error}\n")
    print(f"Modelo: {metadata['selected_model']}; versión: {metadata['model_version']}; train={metadata['training_rows']:,}")
    print(f"Bundle verificado: {args.output}; sin cargar test ni publicar en AWS.")


if __name__ == "__main__":
    main()
