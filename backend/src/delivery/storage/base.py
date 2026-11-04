"""T33: archivos verificables sin filtrar tipos del SDK al dominio."""

from pathlib import Path
from typing import Protocol

from delivery.models.objects import ObjectReference


class ObjectStore(Protocol):
    def upload(self, path: Path, key: str) -> ObjectReference: ...
    def download(self, reference: ObjectReference, destination: Path) -> Path: ...
