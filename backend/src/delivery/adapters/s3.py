"""T33: S3 existente, escritura condicional y descarga atómica con SHA-256."""

import base64
from functools import wraps
import hashlib
import mimetypes
import os
from pathlib import Path
import tempfile

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from delivery.domain.catalogs import StorageUnavailable
from delivery.domain.objects import ObjectConflict, ObjectIntegrityError, ObjectReference, validate_key


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def s3_errors(function):
    @wraps(function)
    def call(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (BotoCoreError, ClientError):
            raise StorageUnavailable("S3 no disponible o acceso no autorizado") from None
    return call


def create_s3_store(profile=None, bucket="ml-kodigo-resources", region="us-east-1", endpoint=None):
    # Endpoint explícito evita heredar accidentalmente AWS_ENDPOINT_URL de un emulador.
    client = boto3.Session(profile_name=profile).client("s3", region_name=region,
        endpoint_url=endpoint or f"https://s3.{region}.amazonaws.com")
    return S3ObjectStore(client, bucket)


class S3ObjectStore:
    def __init__(self, client, bucket="ml-kodigo-resources"):
        self.client, self.bucket = client, bucket

    def _head(self, key):
        try:
            return self.client.head_object(Bucket=self.bucket, Key=key, ChecksumMode="ENABLED")
        except ClientError as error:
            if error.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
                return None
            raise

    def _verify(self, reference, head):
        if head["ContentLength"] != reference.size:
            raise ObjectIntegrityError("Tamaño de objeto incompatible")
        checksum = head.get("ChecksumSHA256")
        if checksum:
            if checksum != base64.b64encode(bytes.fromhex(reference.sha256)).decode("ascii"):
                raise ObjectIntegrityError("SHA-256 del objeto incompatible")
        else:
            # Un ETag o metadata declarada por el cliente no sustituyen al hash del contenido.
            response = self.client.get_object(Bucket=self.bucket, Key=reference.key)
            digest = hashlib.sha256()
            try:
                for chunk in iter(lambda: response["Body"].read(1024 * 1024), b""):
                    digest.update(chunk)
            finally:
                response["Body"].close()
            if digest.hexdigest() != reference.sha256:
                raise ObjectIntegrityError("SHA-256 del contenido incompatible")

    @s3_errors
    def upload(self, path: Path, key: str) -> ObjectReference:
        path = Path(path)
        validate_key(key)
        reference = ObjectReference(self.bucket, key, path.stat().st_size, file_sha256(path))
        if reference.size > 5 * 1024**3:
            raise ValueError("Este publicador usa PUT simple, máximo 5 GiB por objeto")
        head = self._head(key)
        if head is not None:
            try:
                self._verify(reference, head)
            except ObjectIntegrityError:
                raise ObjectConflict("La clave existente contiene otro archivo; usar otra versión") from None
        else:
            try:
                with path.open("rb") as source:
                    self.client.put_object(Bucket=self.bucket, Key=key, Body=source,
                        IfNoneMatch="*", ChecksumAlgorithm="SHA256",
                        ChecksumSHA256=base64.b64encode(bytes.fromhex(reference.sha256)).decode("ascii"),
                        Metadata={"sha256": reference.sha256}, ServerSideEncryption="AES256",
                        ContentType=mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            except ClientError as error:
                if error.response["Error"]["Code"] not in ("PreconditionFailed", "412", "ConditionalRequestConflict", "409"):
                    raise
            head = self._head(key)
            if head is None:
                raise ObjectConflict("Escritura concurrente; reintentar explícitamente")
            self._verify(reference, head)
        return ObjectReference(self.bucket, key, reference.size, reference.sha256, head.get("VersionId"))

    @s3_errors
    def download(self, reference: ObjectReference, destination: Path) -> Path:
        if reference.bucket != self.bucket:
            raise ValueError("Referencia a otro bucket")
        destination = Path(destination)
        if destination.exists():
            if destination.stat().st_size == reference.size and file_sha256(destination) == reference.sha256:
                return destination
            raise ObjectConflict("El destino local contiene otro archivo")
        destination.parent.mkdir(parents=True, exist_ok=True)
        params = {"Bucket": self.bucket, "Key": reference.key}
        if reference.version_id is not None:
            params["VersionId"] = reference.version_id
        response = self.client.get_object(**params)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as target:
                temporary = Path(target.name)
                digest, size = hashlib.sha256(), 0
                for chunk in iter(lambda: response["Body"].read(1024 * 1024), b""):
                    target.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
            if size != reference.size or digest.hexdigest() != reference.sha256:
                raise ObjectIntegrityError("Descarga con tamaño o SHA-256 incompatible")
            # No reemplazar un archivo creado por otra descarga mientras se verificaba.
            try:
                os.link(temporary, destination)
            except FileExistsError:
                if destination.stat().st_size != reference.size or file_sha256(destination) != reference.sha256:
                    raise ObjectConflict("El destino local cambió durante la descarga") from None
            return destination
        finally:
            response["Body"].close()
            if temporary is not None:
                temporary.unlink(missing_ok=True)
