"""Consulta de efectivo ausente/presente sin escrituras ni importes inferidos."""
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient
from delivery.api.app import create_app
from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.domain.models import Business, Location, Order
from delivery.domain.cash import CashNotFound, CashRecord, CashEvent, CashStatus


def test_operations_preserves_cash_and_missing_records(monkeypatch):
    for key in ("MONGODB_URI", "MONGODB_DATABASE", "DELIVERY_MODEL_DIR", "DELIVERY_MODEL_MANIFEST_KEY", "DELIVERY_MODEL_V2_DIR", "DELIVERY_MODEL_V2_MANIFEST_KEY"):
        monkeypatch.delenv(key, raising=False)
    now = datetime.now(timezone.utc)
    point = Location(13.7, -89.2)
    orders = InMemoryOrderRepository()
    for identifier in ("a", "b"):
        orders.create(Order(identifier, "business", point, point, "Comida de prueba"), now)
    cash_record = CashRecord("b", "quote-b", "USD", Decimal("2.50"), (CashEvent(None, CashStatus.PENDING, now),))
    class Cash:
        def get(self, identifier):
            if identifier == "b": return cash_record
            raise CashNotFound(identifier)
    storage = SimpleNamespace(orders=orders, businesses=InMemoryBusinesses([Business("business", "Prueba", point)]), couriers=None, cash=Cash())
    with TestClient(create_app(mongo_storage=storage)) as client:
        rows = client.get("/operations/orders").json()
        assert rows[0]["cash"] is None
        assert rows[1]["cash"]["expected_amount"] == "2.50"
        assert rows[1]["cash"]["events"][-1]["status"] == "pendiente"
        assert len(client.get("/operations/orders?limit=1").json()) == 1
        assert client.get("/operations/orders?limit=101").status_code == 422
        assert orders.get("a").order.status.value == "solicitado"
