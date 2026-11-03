"""Adquisición local reproducible de Meituan (T06), sin limpieza ni AWS."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from urllib.request import Request, urlopen
import zipfile


REVISION = "1f9b4288cee5a78d1e5da007fc306bbaa662fc6d"
BASE_URL = (
    "https://raw.githubusercontent.com/meituan/"
    f"Meituan-INFORMS-TSL-Research-Challenge/{REVISION}"
)
CSV_NAME = "all_waybill_info_meituan_0322.csv"
ZIP_NAME = CSV_NAME + ".zip"
EXPECTED = {
    ZIP_NAME: (38763754, "38b51431a12dd7e73deb4fc750b1275067fbc29cfce2c4b4492339738c988ce2"),
    CSV_NAME: (121698401, "1d31aac21e17c11aec6ab0033d4040c03aea5bab1dfd60aa11e74d766bbd2c04"),
    "License.txt": (1961, "469f53d91ee9d0dbdf7b60146bfdbcee57732db4f2b6bb13c41bfdf28c30daab"),
}
COLUMNS = [
    "", "dt", "order_id", "waybill_id", "courier_id", "da_id",
    "is_courier_grabbed", "is_weekend", "estimate_arrived_time", "is_prebook",
    "poi_id", "sender_lng", "sender_lat", "recipient_lng", "recipient_lat",
    "grab_lng", "grab_lat", "dispatch_time", "grab_time", "fetch_time",
    "arrive_time", "estimate_meal_prepare_time", "order_push_time",
    "platform_order_time",
]
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "data" / "raw" / "meituan" / REVISION


def verify_file(path: Path, expected_size: int, expected_sha256: str) -> dict:
    """Rechaza archivos truncados o distintos de la versión inspeccionada."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    size = path.stat().st_size
    if size != expected_size or digest.hexdigest() != expected_sha256:
        raise ValueError(f"Integridad inválida: {path.name}; no usar ni sobrescribir")
    return {"bytes": size, "sha256": digest.hexdigest()}


def download_file(name: str, directory: Path) -> None:
    request = Request(f"{BASE_URL}/{name}", headers={"User-Agent": "ml-delivery-T06/0.1"})
    with urlopen(request, timeout=45) as source, (directory / name).open("xb") as target:
        shutil.copyfileobj(source, target)
    verify_file(directory / name, *EXPECTED[name])


def extract_csv(archive_path: Path, directory: Path) -> None:
    """Extrae solo el miembro conocido; ignora auxiliares y rutas del ZIP."""
    with zipfile.ZipFile(archive_path) as archive:
        with archive.open(CSV_NAME) as source, (directory / CSV_NAME).open("xb") as target:
            shutil.copyfileobj(source, target)


def inspect_directory(directory: Path) -> dict:
    files = {
        name: verify_file(directory / name, *expected)
        for name, expected in EXPECTED.items()
    }
    with (directory / CSV_NAME).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        columns = next(reader)
        rows = sum(1 for _ in reader)
    if columns != COLUMNS or rows != 654343:
        raise ValueError("Inventario CSV distinto del investigado; requiere revisión")
    return {"files": files, "rows": rows, "columns": columns}


def acquire(output: Path) -> dict:
    """Publica una adquisición completa o comprueba la copia ya existente."""
    if output.exists():
        inventory = inspect_directory(output)
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("revision") != REVISION or manifest.get("inventory") != inventory:
            raise ValueError("Manifiesto incompatible con los archivos locales")
        return manifest

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".meituan-download-", dir=output.parent) as temporary:
        staging = Path(temporary) / "dataset"
        staging.mkdir()
        download_file(ZIP_NAME, staging)
        download_file("License.txt", staging)
        extract_csv(staging / ZIP_NAME, staging)
        inventory = inspect_directory(staging)
        manifest = {
            "dataset": "Meituan INFORMS TSL Research Challenge / waybills",
            "revision": REVISION,
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_urls": {
                name: f"{BASE_URL}/{name}" for name in (ZIP_NAME, "License.txt")
            },
            "license": "CC BY-NC 4.0 y condiciones adicionales del editor en License.txt",
            "usage": "Adquisición académica local; sin redistribución. Uso privado de S3 y modelos sujeto a revisión de términos antes de publicar",
            "inventory": inventory,
            "transformations": [],
            "target_validation": "Pendiente de T07; adquisición no autoriza entrenamiento",
        }
        (staging / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(output)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        manifest = acquire(args.output.resolve())
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(1, f"Adquisición no completada: {error}\n")
    print(f"Copia local verificada: {args.output.resolve()}")
    print(f"Filas originales: {manifest['inventory']['rows']}; columnas: {len(COLUMNS)}")
    print("Manifiesto y licencia disponibles. Consultar la auditoría T07 para validar el target.")


if __name__ == "__main__":
    main()
