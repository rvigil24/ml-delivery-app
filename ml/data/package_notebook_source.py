"""Empaqueta solo código/documentación para ejecutar el notebook en Colab."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "reports" / "presentation" / "delivery_source.zip"


def main() -> None:
    paths = [ROOT / name for name in ("pyproject.toml", "uv.lock", ".python-version", "README.md", "Dockerfile", ".dockerignore", "compose.yaml")]
    for name in ("backend/src", "backend/tests", "ml/src", "ml/data", "ml/experiments", "ml/tests", "infra/docker"):
        paths.extend((ROOT / name).rglob("*.py"))
    paths.extend((ROOT / "docs").glob("*.md"))
    files = sorted(set(paths))
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_tree_changes": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "files": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
        "content": "Solo código, pruebas y documentación; sin datasets, credenciales o .env",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT))
        archive.writestr("SOURCE_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Fuentes para Colab: {OUTPUT}")
    print(f"Archivos: {len(files)}; no contiene datos ni .env")


if __name__ == "__main__":
    main()
