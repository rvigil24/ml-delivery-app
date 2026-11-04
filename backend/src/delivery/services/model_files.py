"""T33: recuperar únicamente un bundle propio desde un manifiesto SHA-256 fijado."""

import json
from pathlib import Path

from delivery.domain.objects import ObjectReference
from delivery.ports.objects import ObjectStore


MODEL_FILES = {"pipeline.pkl", "metadata.json", "evidence.json", "model_card.md", "License.txt"}
MODEL_V2_FILES = {"eta.pkl", "risk.pkl", "metadata.json", "evidence.json", "model_card.md", "License.txt"}


def download_model_bundle(store: ObjectStore, manifest: ObjectReference, directory: Path, *,
                          schema: str = "delivery-s3-model-v1") -> Path:
    if not manifest.key.startswith("models/") or not manifest.key.endswith("/manifest.json"):
        raise ValueError("Se requiere manifiesto versionado de modelo")
    directory = Path(directory)
    manifest_path = store.download(manifest, directory / "manifest.json")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {"delivery-s3-model-v1": MODEL_FILES, "delivery-s3-model-v2": MODEL_V2_FILES}.get(schema)
    if expected is None or data.get("schema") != schema or set(data.get("files", {})) != expected:
        raise ValueError("Manifiesto de bundle incompatible")
    prefix = manifest.key.rsplit("/", 1)[0]
    for name, info in data["files"].items():
        reference = ObjectReference(manifest.bucket, prefix + "/" + name, info["size"], info["sha256"])
        store.download(reference, directory / name)
    if schema == "delivery-s3-model-v2":
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        version = data.get("model_version")
        if not isinstance(version, str) or not version.strip() or metadata.get("model_version") != version:
            raise ValueError("Versión del manifiesto incompatible con el bundle")
    return directory
