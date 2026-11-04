"""T33: recuperar únicamente un bundle propio desde un manifiesto SHA-256 fijado."""

import json
from pathlib import Path

from delivery.domain.objects import ObjectReference
from delivery.ports.objects import ObjectStore


MODEL_FILES = {"pipeline.pkl", "metadata.json", "evidence.json", "model_card.md", "License.txt"}


def download_model_bundle(store: ObjectStore, manifest: ObjectReference, directory: Path) -> Path:
    if not manifest.key.startswith("models/") or not manifest.key.endswith("/manifest.json"):
        raise ValueError("Se requiere manifiesto versionado de modelo")
    directory = Path(directory)
    manifest_path = store.download(manifest, directory / "manifest.json")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("schema") != "delivery-s3-model-v1" or set(data.get("files", {})) != MODEL_FILES:
        raise ValueError("Manifiesto de bundle incompatible")
    prefix = manifest.key.rsplit("/", 1)[0]
    for name, info in data["files"].items():
        reference = ObjectReference(manifest.bucket, prefix + "/" + name, info["size"], info["sha256"])
        store.download(reference, directory / name)
    return directory
