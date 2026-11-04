"""T30: HTTP con predictor controlado; valores de fixture, no resultados ML reales."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from delivery.api.app import create_app
from delivery.domain.estimation import PredictionUnavailable
from delivery.domain.models import DeliveryDuration, DurationSource


PAYLOAD = {"requested_at": "2022-10-22T12:00:00-06:00"}


class FixturePredictor:
    def predict(self, stamp):
        assert stamp == datetime(2022, 10, 22, 18, tzinfo=timezone.utc)
        return DeliveryDuration(12.5, DurationSource.PREDICTION, "Intervalo de fixture", "fixture-model")


def test_model_loads_only_at_startup_and_multiple_predictions_use_the_same_instance(tmp_path):
    loaded = []

    def factory(path):
        loaded.append(path)
        return FixturePredictor()

    app = create_app(tmp_path, factory)
    assert loaded == []
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok", "model_available": True}
        for _ in range(2):
            response = client.post("/predict", json=PAYLOAD)
            assert response.status_code == 200
            body = response.json()
            assert body["duration_minutes"] == 12.5 and body["model_version"] == "fixture-model"
            assert body["requested_at_utc"] == "2022-10-22T18:00:00Z"
            assert body["duration_source"] == "prediccion" and body["interval_definition"] == "Intervalo de fixture"
            assert body["academic_only"] and not body["coverage_validated"] and body["limitations"]
        assert loaded == [tmp_path]


def test_missing_configuration_or_failed_loading_keeps_health_alive_and_returns_503(tmp_path, monkeypatch):
    monkeypatch.delenv("DELIVERY_MODEL_DIR", raising=False)
    attempts = []

    def broken_factory(path):
        attempts.append(path)
        raise PredictionUnavailable("Ruta privada /secret/model.pkl")

    for app in (create_app(predictor_factory=broken_factory), create_app(tmp_path, broken_factory)):
        with TestClient(app) as client:
            assert client.get("/health").json() == {"status": "ok", "model_available": False}
            for _ in range(2):
                response = client.post("/predict", json=PAYLOAD)
                assert response.status_code == 503
                assert response.json()["detail"]["code"] == "prediction_unavailable"
                assert "secret" not in response.text
    assert attempts == [tmp_path]


def test_invalid_payloads_return_422_without_prediction_or_echoing_input(tmp_path):
    class UnexpectedPredictor:
        def predict(self, stamp):
            raise AssertionError("No debe predecir para entradas inválidas")

    with TestClient(create_app(tmp_path, lambda path: UnexpectedPredictor())) as client:
        for payload in ({}, {"requested_at": "2022-10-22T12:00:00"}, {"requested_at": "invalid-secret"},
                        {"requested_at": 1666440000}, {"requested_at": "1666440000"},
                        {**PAYLOAD, "vehicle": "bicicleta"}, {**PAYLOAD, "distance_km": 1}):
            response = client.post("/predict", json=payload)
            assert response.status_code == 422 and response.json()["detail"]["code"] == "invalid_request"
            assert "invalid-secret" not in response.text
        assert client.post("/predict", content="{", headers={"content-type": "application/json"}).status_code == 422


def test_failed_or_illustrative_prediction_returns_503_and_unexpected_error_returns_safe_500(tmp_path):
    class BrokenPredictor:
        def __init__(self, result):
            self.result = result

        def predict(self, stamp):
            if isinstance(self.result, Exception):
                raise self.result
            return self.result

    for result, status in ((PredictionUnavailable("private error"), 503),
                           (DeliveryDuration(10, DurationSource.ILLUSTRATIVE, "Fixture"), 503),
                           (None, 503), (RuntimeError("private error"), 500)):
        with TestClient(create_app(tmp_path, lambda path: BrokenPredictor(result)), raise_server_exceptions=False) as client:
            response = client.post("/predict", json=PAYLOAD)
            assert response.status_code == status and "private error" not in response.text
            assert response.json()["detail"]["code"] == ("prediction_unavailable" if status == 503 else "internal_error")


def test_openapi_documents_implemented_endpoints_and_validation_error_schemas(tmp_path):
    with TestClient(create_app(tmp_path, lambda path: FixturePredictor())) as client:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert set(schema["paths"]) == {"/health", "/predict", "/orders/{order_id}/quotes"}
        request_schema = schema["components"]["schemas"]["PredictRequest"]
        assert request_schema["required"] == ["requested_at"] and not request_schema["additionalProperties"]
        assert request_schema["properties"]["requested_at"]["format"] == "date-time"
        assert set(schema["paths"]["/predict"]["post"]["responses"]) == {"200", "422", "503", "500"}
        assert client.get("/docs").status_code == 200


def test_model_directory_can_be_configured_from_exported_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("DELIVERY_MODEL_DIR", str(tmp_path))
    loaded = []

    def factory(path):
        loaded.append(path)
        return FixturePredictor()

    with TestClient(create_app(predictor_factory=factory)) as client:
        assert client.post("/predict", json=PAYLOAD).status_code == 200
    assert loaded == [tmp_path]
