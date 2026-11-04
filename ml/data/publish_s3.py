"""T33: plan curado y publicación privada con AWS CLI, sin recrear recursos."""

import argparse
import base64
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from botocore.exceptions import ClientError

from delivery.storage.s3 import create_s3_store, file_sha256
from delivery.models.objects import ObjectReference


ROOT = Path(__file__).resolve().parents[2]
REVISION = "1f9b4288cee5a78d1e5da007fc306bbaa662fc6d"
MODEL = "meituan-temporal-rf-v1"
BUCKET = "ml-kodigo-resources"
ENDPOINT = "https://s3.us-east-1.amazonaws.com"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as temporary:
        temporary.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)
    return path


def file_info(path):
    return {"size": path.stat().st_size, "sha256": file_sha256(path)}


def build_plan():
    stage = ROOT / "data/s3-publication"
    raw = ROOT / "data/raw/meituan" / REVISION
    bundle = ROOT / "models/delivery-duration" / MODEL
    metadata = json.loads((bundle / "metadata.json").read_text())
    for name, digest in metadata["files"].items():
        if file_sha256(bundle / name) != digest:
            raise ValueError("Bundle local incompatible con sus hashes")
    paths = {name: bundle / name for name in ("pipeline.pkl", "metadata.json", "evidence.json", "model_card.md")}
    paths["License.txt"] = raw / "License.txt"
    model_manifest = write_json(stage / "model-manifest.json", {
        "schema": "delivery-s3-model-v1", "model_version": MODEL,
        "purpose": "Copia privada académica no comercial; sin registros del dataset o validación local",
        "attribution": "This research was supported by data provided by Meituan.",
        "original_metadata_publication": "Describe el estado al exportar; esta copia se autoriza posteriormente por el propietario del proyecto",
        "files": {name: file_info(path) for name, path in paths.items()}})
    objects = [(path, f"models/delivery-duration/{MODEL}/{name}") for name, path in paths.items()]
    objects.append((model_manifest, f"models/delivery-duration/{MODEL}/manifest.json"))
    dataset_prefix = f"datasets/meituan/{REVISION}"
    manifests = [(raw / "manifest.json", "raw/manifest.json"),
        (ROOT / f"data/processed/meituan/{REVISION}/t08-v1/manifest.json", "processed/t08-v1/manifest.json"),
        (ROOT / f"data/splits/meituan/{REVISION}/t13-temporal-v1/manifest.json", "splits/t13-temporal-v1/manifest.json")]
    objects += [(path, f"{dataset_prefix}/{name}") for path, name in manifests]
    objects.append((raw / "License.txt", f"{dataset_prefix}/License.txt"))
    dataset_index = write_json(stage / "dataset-manifest.json", {"schema": "delivery-s3-dataset-v1",
        "revision": REVISION, "availability": "metadata_only", "rows_uploaded": False,
        "reason": "Redistribución de registros Meituan pendiente; originales/procesados/particiones permanecen locales",
        "manifests": {name: file_info(path) for path, name in manifests},
        "attribution": "This research was supported by data provided by Meituan."})
    objects.append((dataset_index, f"{dataset_prefix}/manifest.json"))
    docs = [(ROOT / "README.md", "README.md")]
    docs += [(path, str(path.relative_to(ROOT))) for path in sorted((ROOT / "docs").glob("*.md"))]
    for path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        notebook = json.loads(path.read_text())
        if any(cell.get("outputs") for cell in notebook["cells"]):
            raise ValueError("Publicar únicamente notebooks fuente sin outputs de registros")
        docs.append((path, str(path.relative_to(ROOT))))
    docs.append((ROOT / "data/reports/presentation/delivery_source.zip", "delivery_source.zip"))
    reports = ROOT / "data/reports/meituan" / REVISION
    docs += [(p, "reports/" + str(p.relative_to(reports))) for p in sorted(reports.rglob("*"))
             if p.is_file() and p.suffix in (".json", ".md", ".png")]
    docs += [(ROOT / "data/reports/presentation" / name, "evidence/" + name)
             for name in ("t30_api_smoke.json", "t31_quote_smoke.json", "t32_mongodb.json")]
    inventory = {name: file_info(path) for path, name in docs}
    fingerprint = hashlib.sha256(json.dumps(inventory, sort_keys=True).encode()).hexdigest()[:20]
    docs_prefix = f"docs/ml-delivery-app/{fingerprint}"
    objects += [(path, docs_prefix + "/" + name) for path, name in docs]
    docs_manifest = write_json(stage / "docs-manifest.json", {"schema": "delivery-s3-docs-v1",
        "source_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "working_tree_changes": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "files": inventory})
    objects.append((docs_manifest, docs_prefix + "/manifest.json"))
    return objects, docs_prefix, file_info(model_manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--apply", action="store_true", help="Publicar el plan con la autorización del propietario")
    args = parser.parse_args()
    objects, docs_prefix, model_manifest = build_plan()
    report = {"bucket": BUCKET, "region": "us-east-1", "docs_prefix": docs_prefix,
        "model_manifest": {"key": f"models/delivery-duration/{MODEL}/manifest.json", **model_manifest},
        "object_count": len(objects), "total_bytes": sum(path.stat().st_size for path, _ in objects),
        "dataset_rows_uploaded": False, "objects": []}
    print(json.dumps({key: value for key, value in report.items() if key != "objects"}, ensure_ascii=False))
    if not args.apply:
        return
    store = create_s3_store(profile=args.profile)
    receipt = ROOT / "data/reports/presentation/t33_s3_publication.json"
    report["status"] = "in_progress"
    report["planned_objects"] = [{"key": key, **file_info(path)} for path, key in objects]
    try:
        region = store.client.get_bucket_location(Bucket=BUCKET).get("LocationConstraint") or "us-east-1"
        if region != "us-east-1":
            raise ValueError("Región del bucket incompatible")
        try:
            policy = store.client.get_bucket_policy_status(Bucket=BUCKET)
            if policy["PolicyStatus"]["IsPublic"]:
                raise ValueError("El bucket tiene política pública; no se modifica automáticamente")
        except ClientError as error:
            if error.response["Error"]["Code"] != "NoSuchBucketPolicy":
                raise
        ownership = store.client.get_bucket_ownership_controls(Bucket=BUCKET)
        if ownership["OwnershipControls"]["Rules"][0]["ObjectOwnership"] != "BucketOwnerEnforced":
            raise ValueError("Revisar propiedad/ACL antes de publicar; no se modifica el bucket")
        write_json(receipt, report)
        for path, key in objects:
            info = file_info(path)
            reference = ObjectReference(BUCKET, key, info["size"], info["sha256"])
            head = store._head(key)
            if head is None:
                command = ["aws", "s3api", "put-object", "--bucket", BUCKET, "--key", key, "--body", str(path),
                    "--if-none-match", "*", "--checksum-algorithm", "SHA256", "--checksum-sha256",
                    base64.b64encode(bytes.fromhex(info["sha256"])).decode(), "--metadata", "sha256=" + info["sha256"],
                    "--server-side-encryption", "AES256", "--profile", args.profile, "--region", "us-east-1",
                    "--endpoint-url", ENDPOINT, "--output", "json"]
                subprocess.run(command, check=True, capture_output=True, text=True)
                head = store._head(key)
            store._verify(reference, head)
            acl = store.client.get_object_acl(Bucket=BUCKET, Key=key)
            if any(grant["Grantee"]["Type"] != "CanonicalUser" for grant in acl["Grants"]):
                raise ValueError("Objeto con concesiones de acceso no privadas")
            report["objects"].append(asdict(ObjectReference(BUCKET, key, info["size"], info["sha256"], head.get("VersionId"))))
            write_json(receipt, report)
        report["verified_at_utc"] = datetime.now(timezone.utc).isoformat()
        report["status"] = "verified"
        write_json(receipt, report)
        print(f"Objetos verificados en S3: {len(report['objects'])}; sin modificar bucket, IAM o ACL públicas")
    except Exception:
        report["status"] = "incomplete"
        write_json(receipt, report)
        raise
    finally:
        store.client.close()


if __name__ == "__main__":
    main()
