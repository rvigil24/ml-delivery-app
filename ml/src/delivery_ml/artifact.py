"""T19: selección por CV y carga verificada de artefactos locales propios."""

import hashlib
import importlib.metadata
import json
from pathlib import Path
import pickle
import platform

from delivery_ml.model_data import CONTEXT_COLUMNS, FEATURE_COLUMNS


ARTIFACT_SCHEMA = "delivery-duration-v1"


def environment_versions() -> dict:
    return {"python": platform.python_version(), **{
        name: importlib.metadata.version(name) for name in ("scikit-learn", "numpy", "scipy", "pandas")}}


def select_by_cv(cv: dict, mlp: dict) -> tuple:
    """No recibe métricas test; en empate conserva el orden documentado."""
    scores = {name: result["best_mean_mae_minutes"] for name, result in cv["models"].items()}
    scores["mlp"] = mlp["selected_cv_mae_minutes"]
    if not scores or any(not isinstance(v, (int, float)) or not 0 <= v < float("inf") for v in scores.values()):
        raise ValueError("MAE de validación inválido")
    return min(scores, key=scores.get), scores


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pipeline(directory: Path):
    """Solo para bundles propios de confianza: pickle no autentica su origen."""
    metadata = json.loads((directory / "metadata.json").read_text())
    if (metadata["schema"] != ARTIFACT_SCHEMA or metadata["context_columns"] != CONTEXT_COLUMNS
            or metadata["feature_columns"] != FEATURE_COLUMNS or metadata["target_unit"] != "minutes"):
        raise ValueError("Contrato de artefacto incompatible")
    if metadata["environment"] != environment_versions():
        raise ValueError("Entorno incompatible con el artefacto; reproducir en su entorno versionado")
    for name in ("pipeline.pkl", "evidence.json", "model_card.md"):
        if file_hash(directory / name) != metadata["files"][name]:
            raise ValueError(f"Hash de artefacto incompatible: {name}")
    with (directory / "pipeline.pkl").open("rb") as stream:
        return pickle.load(stream)


def write_bundle(directory: Path, pipeline, metadata: dict, evidence: dict, card: str) -> dict:
    """Escribe en un directorio de staging nuevo; el exportador lo publica al verificar."""
    directory.mkdir()
    with (directory / "pipeline.pkl").open("wb") as stream:
        pickle.dump(pipeline, stream, protocol=5)
    (directory / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (directory / "model_card.md").write_text(card, encoding="utf-8")
    metadata = {**metadata, "files": {name: file_hash(directory / name) for name in
                                   ("pipeline.pkl", "evidence.json", "model_card.md")}}
    (directory / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return metadata
