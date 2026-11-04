"""Filtro por negocio antes de limitar y transición condicional sobre fixtures."""

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.api.app import create_app
from delivery.domain.models import Business, Location, Order


def test_business_filter_precedes_limit_and_transitions_preserve_other_business(monkeypatch):
    for name in ("DELIVERY_MODEL_DIR", "DELIVERY_MODEL_MANIFEST_KEY", "DELIVERY_MODEL_V2_DIR", "DELIVERY_MODEL_V2_MANIFEST_KEY"):
        monkeypatch.delenv(name, raising=False)
    point = Location(0, 0)
    businesses = InMemoryBusinesses([Business("fixture-a", "Negocio A", point), Business("fixture-b", "Negocio B", point)])
    orders = InMemoryOrderRepository()
    for identifier, business in (("a-order", "fixture-a"), ("b-order", "fixture-b")):
        orders.create(Order(identifier, business, point, point, "Comida de prueba"), datetime.now(timezone.utc))
    storage = SimpleNamespace(businesses=businesses, couriers=businesses, orders=orders)
    with TestClient(create_app(mongo_storage=storage)) as client:
        response = client.get("/orders?business_id=fixture-b&limit=1")
        assert response.status_code == 200 and [row["order"]["id"] for row in response.json()] == ["b-order"]
        assert len(client.get("/orders").json()) == 2
        assert client.get("/orders?business_id=missing").status_code == 404
        response = client.post("/orders/b-order/transitions", json={"expected": "solicitado", "target": "cancelado"})
        assert response.status_code == 200 and len(response.json()["events"]) == 2
        assert client.get("/orders/a-order").json()["order"]["status"] == "solicitado"
        assert client.post("/orders/b-order/transitions", json={"expected": "solicitado", "target": "cancelado"}).status_code == 409
