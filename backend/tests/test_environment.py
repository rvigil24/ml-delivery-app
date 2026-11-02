"""Verificaciones del entorno de T02, sin solicitudes a AWS."""

from contextlib import closing
import importlib
from importlib.metadata import distribution
import socket

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import pytest


def test_delivery_is_installed() -> None:
    """El paquete se importa desde su instalación, sin alterar sys.path."""
    package = importlib.import_module("delivery")

    assert package.__file__ is not None
    assert distribution("ml-delivery-app").metadata["Requires-Python"] == ">=3.9"


def test_boto3_can_prepare_s3_without_credentials_or_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Carga el cliente/modelo local del SDK, sin operar sobre ningún bucket."""
    def reject_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("La prueba de T02 no debe abrir conexiones de red")

    def reject_credentials(*args: object, **kwargs: object) -> None:
        raise AssertionError("La prueba de T02 no debe buscar credenciales")

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    monkeypatch.setattr(socket, "create_connection", reject_network)
    monkeypatch.setattr(
        "botocore.session.Session.get_credentials", reject_credentials
    )
    # UNSIGNED se usa exclusivamente para esta comprobación local del SDK.
    session = boto3.Session(region_name="us-east-1")
    with closing(session.client("s3", config=Config(signature_version=UNSIGNED))) as client:
        assert client.meta.region_name == "us-east-1"
        assert client.meta.service_model.service_name == "s3"
        assert "GetObject" in client.meta.service_model.operation_names
