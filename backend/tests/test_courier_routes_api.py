"""Rutas con fixtures T26: pertenencia, orden y liberación, sin escribir Atlas."""

from dataclasses import replace
from types import SimpleNamespace

from fastapi.testclient import TestClient

from delivery.adapters.memory import InMemoryBusinesses
from delivery.api.app import create_app
from delivery.domain.models import Business
from test_assignments import setup, A, B, COURIER, START, LOADS


def fixture_client(monkeypatch):
    for name in ("DELIVERY_MODEL_DIR", "DELIVERY_MODEL_MANIFEST_KEY", "DELIVERY_MODEL_V2_DIR", "DELIVERY_MODEL_V2_MANIFEST_KEY"):
        monkeypatch.delenv(name, raising=False)
    other = replace(COURIER, id="fixture-other")
    repository, _, assignments = setup((COURIER, other))
    assignment = assignments.assign("fixture-route", COURIER.id, [A.id, B.id], START, LOADS)
    businesses = InMemoryBusinesses([Business(order.business_id, "Fixture", order.origin) for order in (A, B)])
    storage = SimpleNamespace(businesses=businesses, couriers=repository, orders=repository)
    return TestClient(create_app(mongo_storage=storage)), repository, assignment


def test_routes_are_scoped_and_wrong_owner_or_premature_completion_do_not_change_orders(monkeypatch):
    client, repo, assignment = fixture_client(monkeypatch)
    before = repo.get(A.id)
    with client:
        assert client.get(f"/couriers/{COURIER.id}/assignments").status_code == 200
        assert client.get("/couriers/fixture-other/assignments").json() == []
        assert client.get("/couriers/missing/assignments").status_code == 404
        path = f"/couriers/fixture-other/assignments/{assignment.id}/progress"
        assert client.post(path, json={"order_id": A.id, "expected": "asignado", "target": "recogido"}).status_code == 409
        assert client.post(f"/couriers/{COURIER.id}/assignments/{assignment.id}/complete").status_code == 409
        assert repo.get(A.id) == before and not repo.get_courier(COURIER.id).available


def test_progress_uses_current_states_and_release_waits_for_all_orders(monkeypatch):
    client, repo, assignment = fixture_client(monkeypatch)
    prefix = f"/couriers/{COURIER.id}/assignments/{assignment.id}"
    with client:
        for stop in assignment.route.stops:
            expected, target = ("asignado", "recogido") if stop.kind.value == "recogida" else ("recogido", "entregado")
            body = {"order_id": stop.order_id, "expected": expected, "target": target}
            result = client.post(prefix + "/progress", json=body)
            assert result.status_code == 200
            assert next(row for row in result.json()["orders"] if row["order"]["id"] == stop.order_id)["order"]["status"] == target
            assert client.post(prefix + "/progress", json=body).status_code == 409
        assert not repo.get_courier(COURIER.id).available
        result = client.post(prefix + "/complete")
        assert result.status_code == 200 and not result.json()["active"]
        assert result.json()["released_at"] and repo.get_courier(COURIER.id).available
        assert client.post(prefix + "/complete").status_code == 409
