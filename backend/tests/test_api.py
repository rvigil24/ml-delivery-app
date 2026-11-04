"""Contrato HTTP activo con predictor controlado, sin pesos ni conexión cloud."""

from datetime import datetime, timezone
import json

from fastapi.testclient import TestClient
import pytest

from delivery.api.app import create_app
from delivery.domain.estimation import PredictionUnavailable


PAYLOAD = {
    "requested_at": "2022-10-22T12:00:00-06:00",
    "origin": {"latitude": 13.69, "longitude": -89.21},
    "destination": {"latitude": 13.70, "longitude": -89.20},
    "promised_minutes": 30.0,
}


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for key in ("DELIVERY_MODEL_DIR", "DELIVERY_MODEL_MANIFEST_KEY", "DELIVERY_MODEL_V2_DIR",
                "DELIVERY_MODEL_V2_MANIFEST_KEY", "MONGODB_URI", "MONGODB_DATABASE", "DELIVERY_DEMO_ENABLED"):
        monkeypatch.delenv(key, raising=False)


class FixturePredictor:
    def predict(self, stamp, origin, destination, promised):
        assert stamp.astimezone(timezone.utc) == datetime(2022, 10, 22, 18, tzinfo=timezone.utc)
        return {"model_version": "fixture-model", "estimated_minutes": 12.5, "late_probability": 0.2,
                "academic_only": True, "local_validation": False, "limitations": ["Fixture de prueba"]}


def test_delivery_accepts_no_deadline_for_eta_only(monkeypatch, tmp_path):
    class ETAOnly:
        def predict(self, stamp, origin, destination, promised):
            assert promised is None
            return {"model_version": "fixture", "estimated_minutes": 12.5, "distance_km": 0,
                    "late_probability": None, "promised_minutes": None}
    configure_model(monkeypatch, tmp_path, lambda path: ETAOnly())
    payload = {key: value for key, value in PAYLOAD.items() if key != "promised_minutes"}
    with TestClient(create_app()) as client:
        result = client.post("/predict/delivery", json=payload)
        assert result.status_code == 200
        assert result.json()["late_probability"] is None and result.json()["estimated_minutes"] == 12.5


def configure_model(monkeypatch, tmp_path, factory):
    monkeypatch.setenv("DELIVERY_MODEL_V2_DIR", str(tmp_path))
    monkeypatch.setattr("delivery.adapters.delivery_model_v2.LocalDeliveryModelV2", factory)


def test_model_loads_once_and_health_reports_the_active_models(monkeypatch, tmp_path):
    loaded = []

    def factory(path):
        loaded.append(path)
        return FixturePredictor()

    configure_model(monkeypatch, tmp_path, factory)
    app = create_app()
    assert loaded == []
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok", "model_available": True}
        for _ in range(2):
            response = client.post("/predict/delivery", json=PAYLOAD)
            assert response.status_code == 200
            body = response.json()
            assert body["estimated_minutes"] == 12.5 and body["late_probability"] == 0.2
            assert body["model_version"] == "fixture-model" and body["model_source"] == "local"
            assert body["experimental"] and not body["local_validation"] and "academic_only" not in body
        assert loaded == [tmp_path]


def test_missing_or_failed_model_load_returns_safe_503(monkeypatch, tmp_path):
    def broken(path):
        raise PredictionUnavailable("Ruta privada /secret/model.pkl")

    with TestClient(create_app()) as client:
        assert not client.get("/health").json()["model_available"]
        assert client.post("/predict/delivery", json=PAYLOAD).status_code == 503
    configure_model(monkeypatch, tmp_path, broken)
    with TestClient(create_app()) as client:
        assert not client.get("/health").json()["model_available"]
        response = client.post("/predict/delivery", json=PAYLOAD)
        assert response.status_code == 503 and "secret" not in response.text


def test_invalid_payloads_return_422_without_prediction(monkeypatch, tmp_path):
    class Unexpected:
        def predict(self, *args):
            raise AssertionError("No debe predecir para entradas inválidas")

    configure_model(monkeypatch, tmp_path, lambda path: Unexpected())
    invalid = [{}, {**PAYLOAD, "requested_at": "2022-10-22T12:00:00"},
               {**PAYLOAD, "requested_at": "invalid-secret"}, {**PAYLOAD, "requested_at": 1666440000},
               {**PAYLOAD, "vehicle": "bicicleta"}, {**PAYLOAD, "promised_minutes": 0}]
    with TestClient(create_app()) as client:
        for payload in invalid:
            response = client.post("/predict/delivery", json=payload)
            assert response.status_code == 422 and response.json()["detail"]["code"] == "invalid_request"
            assert "invalid-secret" not in response.text
        assert client.post("/predict/delivery", content="{", headers={"Content-Type": "application/json"}).status_code == 422


def test_predictor_errors_do_not_expose_details(monkeypatch, tmp_path):
    class Broken:
        def __init__(self, error):
            self.error = error

        def predict(self, *args):
            raise self.error

    for error, status in ((PredictionUnavailable("private error"), 503), (RuntimeError("private error"), 500)):
        configure_model(monkeypatch, tmp_path, lambda path: Broken(error))
        with TestClient(create_app(), raise_server_exceptions=False) as client:
            response = client.post("/predict/delivery", json=PAYLOAD)
            assert response.status_code == status and "private error" not in response.text


def test_openapi_has_clear_descriptions_and_legacy_route_is_removed():
    app = create_app()
    schema = app.openapi()
    assert "/predict" not in schema["paths"] and "/predict/delivery" in schema["paths"]
    assert "acad" not in json.dumps(schema, ensure_ascii=False).lower()
    for methods in schema["paths"].values():
        for operation in methods.values():
            assert operation["summary"] and operation["description"] and operation["tags"]
            assert not operation["summary"].startswith(("Post ", "Get ", "Put ", "Delete "))
    assert len(schema["paths"]["/predict/delivery"]["post"]["requestBody"]["content"]["application/json"]["examples"]) == 3
    with TestClient(app) as client:
        assert client.post("/predict", json=PAYLOAD).status_code == 404
