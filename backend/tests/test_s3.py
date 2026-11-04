"""T33: contrato SDK sin red; objetos/bytes sintéticos, no datasets o modelos reales."""

import base64
import hashlib
import io
import json
from pathlib import Path

import boto3
from botocore import UNSIGNED
from botocore.config import Config
from botocore.response import StreamingBody
from botocore.stub import ANY, Stubber
from fastapi.testclient import TestClient
import pytest

from delivery.adapters.s3 import S3ObjectStore
from delivery.api.app import create_app
from delivery.domain.catalogs import StorageUnavailable
from delivery.domain.models import DeliveryDuration, DurationSource
from delivery.domain.objects import ObjectConflict, ObjectIntegrityError, ObjectReference
from delivery.services.model_files import MODEL_FILES


BUCKET = "ml-kodigo-resources"
KEY = "docs/fixture/content.txt"
DATA = b"fixture"
SHA = hashlib.sha256(DATA).hexdigest()
CHECKSUM = base64.b64encode(bytes.fromhex(SHA)).decode()
HEAD = {"ContentLength": len(DATA), "ChecksumSHA256": CHECKSUM}


def setup():
    client = boto3.client("s3", region_name="us-east-1", config=Config(signature_version=UNSIGNED))
    return S3ObjectStore(client), Stubber(client)


def test_upload_is_conditional_verified_and_idempotent_without_overwriting_other_bytes(tmp_path):
    path = tmp_path / "content.txt"
    path.write_bytes(DATA)
    store, stub = setup()
    head_params = {"Bucket": BUCKET, "Key": KEY, "ChecksumMode": "ENABLED"}
    stub.add_client_error("head_object", service_error_code="404", http_status_code=404, expected_params=head_params)
    stub.add_response("put_object", {"ChecksumSHA256": CHECKSUM}, {"Bucket": BUCKET, "Key": KEY,
        "Body": ANY, "IfNoneMatch": "*", "ChecksumAlgorithm": "SHA256", "ChecksumSHA256": CHECKSUM,
        "Metadata": {"sha256": SHA}, "ServerSideEncryption": "AES256", "ContentType": "text/plain"})
    stub.add_response("head_object", HEAD, head_params)
    stub.add_response("head_object", HEAD, head_params)
    stub.add_response("head_object", {**HEAD, "ContentLength": 999}, head_params)
    with stub:
        reference = store.upload(path, KEY)
        assert store.upload(path, KEY) == reference
        with pytest.raises(ObjectConflict):
            store.upload(path, KEY)
        assert reference.sha256 == SHA and reference.size == len(DATA)
    stub.assert_no_pending_responses()


def test_conditional_race_is_rechecked_and_access_errors_do_not_leak_sdk_details(tmp_path):
    path = tmp_path / "fixture"
    path.write_bytes(DATA)
    store, stub = setup()
    head_params = {"Bucket": BUCKET, "Key": KEY, "ChecksumMode": "ENABLED"}
    stub.add_client_error("head_object", service_error_code="404", http_status_code=404, expected_params=head_params)
    stub.add_client_error("put_object", service_error_code="PreconditionFailed", http_status_code=412)
    stub.add_response("head_object", HEAD, head_params)
    stub.add_client_error("head_object", service_error_code="AccessDenied", service_message="private details", http_status_code=403)
    with stub:
        assert store.upload(path, KEY).sha256 == SHA
        with pytest.raises(StorageUnavailable, match="S3 no disponible") as error:
            store.upload(path, KEY)
        assert "private details" not in str(error.value)
    with pytest.raises(ValueError):
        ObjectReference(BUCKET, "models/../secret", 1, SHA)
    stub.assert_no_pending_responses()


def test_download_verifies_before_publishing_file_and_rejects_corruption_or_existing_conflicts(tmp_path):
    store, stub = setup()
    reference = ObjectReference(BUCKET, KEY, len(DATA), SHA)
    for content in (b"badbyte", DATA):
        stub.add_response("get_object", {"Body": StreamingBody(io.BytesIO(content), len(content))}, {"Bucket": BUCKET, "Key": KEY})
    destination = tmp_path / "downloaded"
    with stub:
        with pytest.raises(ObjectIntegrityError):
            store.download(reference, destination)
        assert not destination.exists() and not list(tmp_path.iterdir())
        assert store.download(reference, destination).read_bytes() == DATA
        assert store.download(reference, destination) == destination
        destination.write_bytes(b"other")
        with pytest.raises(ObjectConflict):
            store.download(reference, destination)
    stub.assert_no_pending_responses()


def test_legacy_objects_are_verified_from_content_instead_of_trusting_etag_or_metadata(tmp_path):
    path = tmp_path / "fixture"
    path.write_bytes(DATA)
    store, stub = setup()
    stub.add_response("head_object", {"ContentLength": len(DATA), "ETag": '"not-a-sha256"'},
        {"Bucket": BUCKET, "Key": KEY, "ChecksumMode": "ENABLED"})
    stub.add_response("get_object", {"Body": StreamingBody(io.BytesIO(DATA), len(DATA))}, {"Bucket": BUCKET, "Key": KEY})
    with stub:
        assert store.upload(path, KEY).sha256 == SHA
    stub.assert_no_pending_responses()


def test_api_downloads_pinned_bundle_once_and_cleans_private_cache(monkeypatch):
    objects = {name: ("fixture-" + name).encode() for name in MODEL_FILES}
    manifest_bytes = json.dumps({"schema": "delivery-s3-model-v1", "files": {
        name: {"size": len(content), "sha256": hashlib.sha256(content).hexdigest()} for name, content in objects.items()}}).encode()
    objects["manifest.json"] = manifest_bytes
    calls, cache = [], []
    class FixtureClient:
        def close(self):
            calls.append("closed")
    class FixtureStore:
        client = FixtureClient()
        def download(self, reference, destination):
            content = objects[reference.key.rsplit("/", 1)[-1]]
            assert len(content) == reference.size and hashlib.sha256(content).hexdigest() == reference.sha256
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            calls.append(reference.key)
            return destination
    class FixturePredictor:
        def predict(self, requested_at):
            return DeliveryDuration(1, DurationSource.PREDICTION, "Fixture", "fixture-model")
    def factory(directory):
        cache.append(directory)
        assert {p.name for p in directory.iterdir()} == MODEL_FILES | {"manifest.json"}
        return FixturePredictor()
    from delivery.adapters import s3
    monkeypatch.setattr(s3, "create_s3_store", lambda **kwargs: FixtureStore())
    for name in ("DELIVERY_MODEL_DIR", "MONGODB_URI", "MONGODB_DATABASE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("DELIVERY_MODEL_MANIFEST_KEY", "models/fixture/v1/manifest.json")
    monkeypatch.setenv("DELIVERY_MODEL_MANIFEST_SIZE", str(len(manifest_bytes)))
    monkeypatch.setenv("DELIVERY_MODEL_MANIFEST_SHA256", hashlib.sha256(manifest_bytes).hexdigest())
    with TestClient(create_app(predictor_factory=factory)) as client:
        for _ in range(2):
            from datetime import datetime, timezone
            assert client.app.state.predictions.predict(datetime(2022, 1, 1, tzinfo=timezone.utc)).minutes >= 0
        assert len(calls) == 7 and calls.count("closed") == 1 and len(cache) == 1
    assert not cache[0].exists()
