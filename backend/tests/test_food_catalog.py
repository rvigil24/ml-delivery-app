"""Catálogo de comida de ejemplo: cercanía, pertenencia y contrato HTTP."""

from types import SimpleNamespace

from fastapi.testclient import TestClient

from delivery.adapters.memory import InMemoryOrderRepository
from delivery.api.app import create_app
from delivery.domain.models import Business, Location
from delivery.services.food_catalog import FoodCatalogService


class FixtureBusinesses:
    def __init__(self):
        self.rows = (Business("demo-expo-business-1", "Comedor fixture", Location(0, 2)),
                     Business("demo-expo-business-2", "Cafetería fixture", Location(0, .1)),
                     Business("without-menu", "Sin menú fixture", Location(0, 0)))

    def get(self, identifier):
        return next((row for row in self.rows if row.id == identifier), None)

    def all(self):
        return self.rows


def test_nearby_orders_published_menus_before_limiting_and_menu_stays_in_its_business():
    service = FoodCatalogService(FixtureBusinesses())
    result = service.nearby(Location(0, 0), 1)
    assert [row["business"].id for row in result["businesses"]] == ["demo-expo-business-2"]
    assert not result["coverage_validated"]
    menu = service.menu("demo-expo-business-1")
    assert len(menu["products"]) == 3 and menu["simulated"] and not menu["prices_configured"]
    assert all(product["business_id"] == "demo-expo-business-1" and product["price"] is None for product in menu["products"])


def test_food_http_routes_are_not_shadowed_and_reject_invalid_locations(monkeypatch):
    for name in ("DELIVERY_MODEL_DIR", "DELIVERY_MODEL_MANIFEST_KEY", "DELIVERY_MODEL_V2_DIR", "DELIVERY_MODEL_V2_MANIFEST_KEY"):
        monkeypatch.delenv(name, raising=False)
    repo = FixtureBusinesses()
    storage = SimpleNamespace(businesses=repo, couriers=repo, orders=InMemoryOrderRepository())
    with TestClient(create_app(mongo_storage=storage)) as client:
        response = client.get("/businesses/nearby?latitude=0&longitude=0")
        assert response.status_code == 200 and len(response.json()["businesses"]) == 2
        assert client.get("/businesses/nearby?latitude=91&longitude=0").status_code == 422
        response = client.get("/businesses/demo-expo-business-2/menu")
        assert response.status_code == 200 and response.json()["products"][0]["name"] == "Sándwich de pollo"
        assert client.get("/businesses/missing/menu").status_code == 404


def test_food_order_is_validated_persisted_and_retried_without_duplicate_events(monkeypatch):
    for name in ("DELIVERY_MODEL_DIR", "DELIVERY_MODEL_MANIFEST_KEY", "DELIVERY_MODEL_V2_DIR", "DELIVERY_MODEL_V2_MANIFEST_KEY"):
        monkeypatch.delenv(name, raising=False)
    businesses = FixtureBusinesses()
    repository = InMemoryOrderRepository()
    storage = SimpleNamespace(businesses=businesses, couriers=businesses, orders=repository)
    payload = {"id": "demo-chat-fixture", "business_id": "demo-expo-business-1",
               "destination": {"latitude": 13.7, "longitude": -89.2},
               "delivery_address": "Dirección ficticia", "notes": "Sin cebolla",
               "items": [{"product_id": "demo-expo-business-1-product-1", "quantity": 2}]}
    with TestClient(create_app(mongo_storage=storage)) as client:
        result = client.post("/food/orders", json=payload)
        assert result.status_code == 200
        saved = result.json()
        assert saved["order"]["status"] == "solicitado"
        assert saved["order"]["origin"] == {"latitude": 0, "longitude": 2}
        assert saved["order"]["details"] == "2 × Almuerzo de pollo\nDirección: Dirección ficticia\nIndicaciones: Sin cebolla"
        assert client.post("/food/orders", json=payload).json() == saved
        assert len(repository.list(100)) == 1 and len(repository.get(payload["id"]).events) == 1
        assert client.get("/orders?business_id=demo-expo-business-1").json() == [saved]
        assert client.post("/food/orders", json={**payload, "notes": "Otro contenido"}).status_code == 409
        cancelled = client.post(f"/orders/{payload['id']}/transitions", json={"expected": "solicitado", "target": "cancelado"}).json()
        assert client.post("/food/orders", json=payload).json() == cancelled


def test_food_order_rejects_foreign_products_duplicates_and_invalid_quantities(monkeypatch):
    for name in ("DELIVERY_MODEL_DIR", "DELIVERY_MODEL_MANIFEST_KEY", "DELIVERY_MODEL_V2_DIR", "DELIVERY_MODEL_V2_MANIFEST_KEY"):
        monkeypatch.delenv(name, raising=False)
    businesses, repository = FixtureBusinesses(), InMemoryOrderRepository()
    storage = SimpleNamespace(businesses=businesses, couriers=businesses, orders=repository)
    payload = {"id": "demo-chat-invalid", "business_id": "demo-expo-business-1",
               "destination": {"latitude": 13.7, "longitude": -89.2}, "delivery_address": "Dirección ficticia"}
    product = {"product_id": "demo-expo-business-1-product-1", "quantity": 1}
    with TestClient(create_app(mongo_storage=storage)) as client:
        for items in ([], [product, product], [{**product, "quantity": 0}], [{**product, "quantity": True}],
                      [{**product, "quantity": 1.5}], [{"product_id": "demo-expo-business-2-product-1", "quantity": 1}]):
            assert client.post("/food/orders", json={**payload, "items": items}).status_code == 422
        assert repository.list(100) == ()
