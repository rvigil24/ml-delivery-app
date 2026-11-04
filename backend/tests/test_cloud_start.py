"""Arranque cloud sin conectarse a Atlas ni escribir datos."""

from delivery import cloud_start
from delivery.domain.catalogs import StorageUnavailable


def test_wait_then_exec_keeps_process_and_closes_clients(monkeypatch, tmp_path):
    monkeypatch.setenv("MONGODB_URI", "mongodb://example.invalid")
    monkeypatch.setenv("MONGODB_DATABASE", "delivery")
    monkeypatch.setenv("DELIVERY_CLOUD_START_TIMEOUT_SECONDS", "0")
    monkeypatch.setattr(cloud_start, "WAIT_STATE", tmp_path / "wait.json")
    monkeypatch.setattr(cloud_start.sys, "argv", ["cloud_start"])
    monkeypatch.setattr(cloud_start.time, "sleep", lambda seconds: None)
    clients, executions = [], []

    class Storage:
        def __init__(self, uri, database):
            self.closed = False
            clients.append(self)

        def verify_schema(self):
            assert cloud_start.healthcheck()  # Proceso vivo durante la espera.
            if len(clients) == 1:
                raise StorageUnavailable("Aún no se ha permitido la IP")

        def close(self):
            self.closed = True

    def execute(program, args):
        assert not cloud_start.WAIT_STATE.exists()
        assert all(client.closed for client in clients)
        executions.append((program, args))

    monkeypatch.setattr(cloud_start, "MongoStorage", Storage)
    monkeypatch.setattr(cloud_start.os, "execvp", execute)
    assert cloud_start.main() == 0
    assert len(clients) == 2
    assert executions == [("uvicorn", ["uvicorn", "delivery.api.app:app", "--host", "0.0.0.0", "--port", "8000"])]


def test_timeout_does_not_start_api_or_print_uri(monkeypatch, tmp_path, capsys):
    uri = "mongodb://private-user:private-password@example.invalid"
    monkeypatch.setenv("MONGODB_URI", uri)
    monkeypatch.setenv("MONGODB_DATABASE", "delivery")
    monkeypatch.setenv("DELIVERY_CLOUD_START_TIMEOUT_SECONDS", "1")
    monkeypatch.setattr(cloud_start, "WAIT_STATE", tmp_path / "wait.json")
    monkeypatch.setattr(cloud_start.sys, "argv", ["cloud_start"])
    ticks = iter([0, 0, 2, 2])
    monkeypatch.setattr(cloud_start.time, "monotonic", lambda: next(ticks))

    def unavailable(uri, database):
        raise StorageUnavailable(uri)

    def forbidden_exec(*args):
        raise AssertionError("No debe arrancar la API")

    monkeypatch.setattr(cloud_start, "MongoStorage", unavailable)
    monkeypatch.setattr(cloud_start.os, "execvp", forbidden_exec)
    assert cloud_start.main() == 1
    assert not cloud_start.WAIT_STATE.exists()
    assert uri not in capsys.readouterr().out
