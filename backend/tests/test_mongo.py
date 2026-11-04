"""T32: integración opt-in con MongoDB real, datos sintéticos y base desechable."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D
import os
from threading import Barrier
from uuid import uuid4

from fastapi.testclient import TestClient
from pymongo.errors import InvalidOperation, OperationFailure
import pytest

from delivery.adapters.mongo import MongoStorage
from delivery.api.app import create_app
from delivery.domain.assignments import AssignmentConflict, AssignmentNotFound, prepare_assignment
from delivery.domain.cash import CashConflict, CashStatus
from delivery.domain.catalogs import CatalogConflict
from delivery.domain.models import Business, Courier, Location, Order, OrderStatus as S, Quote, QuoteAmounts, VehicleType
from delivery.domain.order_lifecycle import DuplicateOrder, MissingPrerequisite, OrderConflict
from delivery.domain.routing import RoutePolicy, StopType
from delivery.domain.vehicle_rules import ServiceArea, VehicleLimits, VehiclePolicy
from delivery.services.assignments import AssignmentService, DispatchOrderRequirements
from delivery.services.cash import CashService
from delivery.services.orders import OrderService


NOW = datetime(2022, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
START = Location(0, 0)
BUSINESS = Business("fixture-business", "Negocio de prueba", START)
COURIER = Courier("fixture-courier", VehicleType.BICYCLE, True, True)
AREA = ServiceArea("fixture-area", Location(-1, -1), Location(1, 1))
ROUTES = RoutePolicy("fixture-route", 2, AREA)
VEHICLES = VehiclePolicy("fixture-vehicles", AREA, VehicleLimits(D(20), D(5)), VehicleLimits(D(30), D(10)))
ORDERS = tuple(Order(name, BUSINESS.id, START, Location(0, distance), "Fixture") for name, distance in (("a", .02), ("b", .03)))


@pytest.fixture
def storage():
    uri = os.environ.get("MONGODB_TEST_URI")
    if not uri:
        pytest.skip("Definir MONGODB_TEST_URI para integración real; nunca usa MONGODB_URI")
    store = MongoStorage(uri, "delivery_test_" + uuid4().hex)
    try:
        store.initialize_schema()
        yield store
    finally:
        store.client.drop_database(store.database.name)
        store.close()


class FixtureQuotes:
    """Únicamente pruebas, sin validez comercial o datos observados."""

    def __init__(self, barrier=None):
        self.barrier = barrier

    def validate(self, order, target):
        assert target in (S.QUOTED, S.CONFIRMED)

    def validate_confirmed(self, order):
        if self.barrier is not None:
            self.barrier.wait(timeout=10)

    def get_validated(self, order):
        return Quote("fixture-quote-" + order.id, order.id, 1, "fixture", amounts=
            QuoteAmounts("USD", D("2.50"), D(1), D(".10"), D(".20"), D("1.20")))


def confirmed(storage):
    storage.businesses.create(BUSINESS)
    storage.couriers.create(COURIER)
    quotes = FixtureQuotes()
    service = OrderService(storage.orders, storage.businesses, DispatchOrderRequirements(storage.orders, quotes), lambda: NOW)
    for order in ORDERS:
        service.register(order)
        service.transition(order.id, S.REQUESTED, S.QUOTED)
        service.transition(order.id, S.QUOTED, S.CONFIRMED)
    return service, quotes


def test_catalog_crud_validators_uniqueness_microseconds_and_new_connection_persistence(storage):
    storage.initialize_schema()  # No destruye ni cambia datos al repetirse.
    storage.businesses.create(BUSINESS)
    renamed = replace(BUSINESS, name="Otro nombre de prueba")
    storage.businesses.update(renamed, BUSINESS)
    with pytest.raises(CatalogConflict):
        storage.businesses.update(BUSINESS, BUSINESS)
    with pytest.raises(CatalogConflict):
        storage.businesses.create(BUSINESS)
    order = OrderService(storage.orders, storage.businesses, clock=lambda: NOW).register(ORDERS[0])
    with pytest.raises(DuplicateOrder):
        storage.orders.create(ORDERS[0], NOW)
    with pytest.raises(CatalogConflict):
        storage.businesses.delete(BUSINESS.id, renamed)
    with pytest.raises(OperationFailure) as error:
        storage.database.orders.update_one({"_id": "a"}, {"$set": {"data.order.status": "inventado"}})
    assert error.value.code == 121
    with pytest.raises(OperationFailure):
        storage.database.businesses.update_one({"_id": BUSINESS.id}, {"$set": {"data.location.latitude": 1000}})
    other = MongoStorage(os.environ["MONGODB_TEST_URI"], storage.database.name)
    try:
        assert other.orders.get("a") == order and other.orders.get("a").events[0].occurred_at == NOW
        assert other.orders.get("a").events[0].occurred_at.microsecond == 123456
    finally:
        other.close()
    storage.couriers.create(COURIER)
    unavailable = replace(COURIER, available=False)
    storage.couriers.update(unavailable, COURIER)
    storage.couriers.delete(COURIER.id, unavailable)
    assert storage.couriers.get(COURIER.id) is None


def test_competing_order_transitions_across_clients_keep_one_event_and_requirements(storage):
    storage.businesses.create(BUSINESS)
    first = OrderService(storage.orders, storage.businesses, clock=lambda: NOW)
    initial = first.register(ORDERS[0])
    with pytest.raises(MissingPrerequisite):
        first.transition("a", S.REQUESTED, S.QUOTED)
    with pytest.raises(ValueError):
        storage.orders.transition("a", S.REQUESTED, S.CANCELLED, NOW - timedelta(microseconds=1))
    assert first.get("a") == initial
    second = MongoStorage(os.environ["MONGODB_TEST_URI"], storage.database.name)
    barrier = Barrier(2)
    def clock():
        barrier.wait(timeout=10)
        return NOW
    services = (OrderService(storage.orders, storage.businesses, clock=clock),
                OrderService(second.orders, second.businesses, clock=clock))
    def attempt(service):
        try:
            service.transition("a", S.REQUESTED, S.CANCELLED)
            return "updated"
        except OrderConflict:
            return "conflict"
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            assert sorted(pool.map(attempt, services)) == ["conflict", "updated"]
        assert len(first.get("a").events) == 2
    finally:
        second.close()


def test_group_assignment_rolls_back_all_writes_when_last_snapshot_is_stale(storage):
    orders, _ = confirmed(storage)
    records = tuple(orders.get(order.id) for order in ORDERS)
    assignment = prepare_assignment("run", COURIER, tuple(record.order for record in records), START,
                                     ROUTES, VEHICLES, {"a": D(1), "b": D(1)}, NOW)
    orders.transition("b", S.CONFIRMED, S.CANCELLED)
    with pytest.raises(AssignmentConflict):
        storage.orders.commit_assignment(assignment, records)
    assert orders.get("a") == records[0] and storage.orders.get_courier(COURIER.id).available
    with pytest.raises(AssignmentNotFound):
        storage.orders.get_assignment("run")


def test_assignment_progress_release_and_cash_decimal_round_trip_are_transactional(storage):
    orders, quotes = confirmed(storage)
    assignments = AssignmentService(storage.orders, ROUTES, VEHICLES, quotes, lambda: NOW)
    assignment = assignments.assign("run", COURIER.id, ["a", "b"], START, {"a": D(1), "b": D(1)})
    assert assignments.get("run") == assignment
    with pytest.raises(AssignmentConflict):
        assignments.release("run")
    with pytest.raises(CatalogConflict):
        storage.couriers.update(replace(COURIER, available=True), storage.orders.get_courier(COURIER.id))
    for stop in assignment.route.stops:
        expected, target = (S.ASSIGNED, S.PICKED_UP) if stop.kind is StopType.PICKUP else (S.PICKED_UP, S.DELIVERED)
        orders.transition(stop.order_id, expected, target)
    before = orders.get("a")
    cash = CashService(storage.cash, storage.orders, quotes, lambda: NOW)
    cash.open("a")
    barrier = Barrier(2)
    def clock():
        barrier.wait(timeout=10)
        return NOW
    racing = CashService(storage.cash, storage.orders, quotes, clock)
    def collect(_):
        try:
            racing.collect("a", "USD", D("2.50"))
            return "updated"
        except CashConflict:
            return "conflict"
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(collect, range(2))) == ["conflict", "updated"]
    result = cash.remit("a", "USD", D("2.50"))
    assert result.status is CashStatus.REMITTED and result.expected_amount == D("2.50")
    assert storage.database.cash.find_one({"_id": "a"})["data"]["expected_amount"].to_decimal() == D("2.50")
    assert orders.get("a") == before and not storage.orders.get_courier(COURIER.id).available
    assert not assignments.release("run").active and storage.orders.get_courier(COURIER.id).available


def test_competing_assignments_do_not_reserve_two_orders_for_one_courier(storage):
    orders, _ = confirmed(storage)
    service = AssignmentService(storage.orders, ROUTES, VEHICLES, FixtureQuotes(Barrier(2)), lambda: NOW)
    def assign(identifier):
        try:
            service.assign("run-" + identifier, COURIER.id, [identifier], START, {identifier: D(1)})
            return "updated"
        except AssignmentConflict:
            return "conflict"
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(assign, ("a", "b"))) == ["conflict", "updated"]
    assert sorted(orders.get(identifier).order.status.value for identifier in ("a", "b")) == ["asignado", "confirmado"]
    assert storage.database.assignments.count_documents({}) == 1


def test_http_catalog_crud_order_registration_and_controlled_states_use_real_storage(storage, monkeypatch):
    monkeypatch.delenv("DELIVERY_MODEL_DIR", raising=False)
    app = create_app(mongo_storage=storage)
    business = {"id": BUSINESS.id, "name": BUSINESS.name, "location": {"latitude": 0, "longitude": 0}}
    with TestClient(app) as client:
        assert client.post("/businesses", json=business).status_code == 201
        assert client.post("/businesses", json=business).status_code == 409
        assert client.get("/businesses").json()[0]["id"] == BUSINESS.id
        changed = {**business, "name": "Actualizado"}
        assert client.put(f"/businesses/{BUSINESS.id}", json=changed).status_code == 200
        body = {"id": "a", "business_id": BUSINESS.id, "origin": business["location"],
                "destination": {"latitude": 0, "longitude": .02}, "details": "Fixture"}
        response = client.post("/orders", json=body)
        assert response.status_code == 201
        assert client.get("/orders/a").json() == response.json()
        assert client.get("/orders").json()[0]["order"]["id"] == "a"
        assert client.delete(f"/businesses/{BUSINESS.id}").status_code == 409
        assert client.post("/orders/a/transitions", json={"expected": "solicitado", "target": "cotizado"}).status_code == 409
        assert client.post("/orders/a/transitions", json={"expected": "solicitado", "target": "cancelado"}).status_code == 200
        assert client.get("/orders/missing").status_code == 404 and client.get("/orders?limit=0").status_code == 422
        assert client.delete("/orders/a").status_code == 405  # Historial no se borra por CRUD genérico.
        courier = {"id": "temporary", "vehicle": "bicicleta", "approved": True, "available": True}
        assert client.post("/couriers", json=courier).status_code == 201
        assert client.delete("/couriers/temporary").status_code == 204
    assert storage.orders.get("a").order.status is S.CANCELLED  # El cliente prestado sigue disponible.


def test_lifespan_owns_exported_connection_and_unconfigured_storage_never_falls_back(storage, monkeypatch):
    monkeypatch.delenv("DELIVERY_MODEL_DIR", raising=False)
    monkeypatch.setenv("MONGODB_URI", os.environ["MONGODB_TEST_URI"])
    monkeypatch.setenv("MONGODB_DATABASE", storage.database.name)
    app = create_app()
    with TestClient(app) as client:
        assert client.get("/businesses").status_code == 200
        owned_client = app.state.business_catalog._repository.database.client
    with pytest.raises(InvalidOperation):
        owned_client.admin.command("ping")
    monkeypatch.setenv("MONGODB_DATABASE", "delivery_uninitialized_" + uuid4().hex)
    with TestClient(create_app()) as client:
        assert client.get("/businesses").status_code == 503  # Nunca crear colecciones sin validar al recibir un POST.
    monkeypatch.delenv("MONGODB_URI")
    monkeypatch.delenv("MONGODB_DATABASE")
    with TestClient(create_app()) as client:
        response = client.get("/orders")
        assert response.status_code == 503 and response.json()["detail"]["code"] == "storage_unavailable"
        assert client.get("/health").status_code == 200
