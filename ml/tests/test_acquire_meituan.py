"""Comprobaciones offline de integridad; las fixtures no son datos de ML."""

import hashlib
from pathlib import Path
import runpy
import zipfile

import pytest


MODULE = runpy.run_path(str(Path(__file__).parents[1] / "data" / "acquire_meituan.py"))


def test_integrity_rejects_corrupted_bytes(tmp_path: Path) -> None:
    path = tmp_path / "fixture.bin"
    path.write_bytes(b"fixture")
    expected = hashlib.sha256(b"fixture").hexdigest()
    MODULE["verify_file"](path, 7, expected)
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="Integridad"):
        MODULE["verify_file"](path, 7, expected)


def test_extracts_only_expected_member(tmp_path: Path) -> None:
    archive = tmp_path / "fixture.zip"
    with zipfile.ZipFile(archive, "w") as target:
        target.writestr(MODULE["CSV_NAME"], "fixture\n")
        target.writestr("../unexpected.txt", "No extraer")
    directory = tmp_path / "output"
    directory.mkdir()
    MODULE["extract_csv"](archive, directory)
    assert [path.name for path in directory.iterdir()] == [MODULE["CSV_NAME"]]
    assert not (tmp_path / "unexpected.txt").exists()


def test_failed_download_leaves_no_published_dataset(tmp_path: Path, monkeypatch) -> None:
    def reject_connection(*args, **kwargs):
        raise OSError("Sin conexión en la prueba")

    monkeypatch.setitem(MODULE["acquire"].__globals__, "urlopen", reject_connection)
    output = tmp_path / "dataset"
    with pytest.raises(OSError, match="Sin conexión"):
        MODULE["acquire"](output)
    assert not output.exists()
    assert list(tmp_path.iterdir()) == []
