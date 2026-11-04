"""T33: referencias verificables a objetos, sin credenciales o URLs firmadas."""

import re
from dataclasses import dataclass
from typing import Optional


class ObjectConflict(RuntimeError):
    pass


class ObjectIntegrityError(RuntimeError):
    pass


def validate_key(key: str) -> None:
    if (
        not isinstance(key, str)
        or not key.startswith(("datasets/", "models/", "docs/"))
        or key.endswith("/")
        or any(part in ("", ".", "..") for part in key.split("/"))
    ):
        raise ValueError(
            "La clave debe identificar un archivo bajo datasets/, models/ o docs/"
        )


@dataclass(frozen=True)
class ObjectReference:
    bucket: str
    key: str
    size: int
    sha256: str
    version_id: Optional[str] = None

    def __post_init__(self):
        validate_key(self.key)
        if not isinstance(self.bucket, str) or not self.bucket.strip():
            raise ValueError("Bucket explícito requerido")
        if (
            isinstance(self.size, bool)
            or not isinstance(self.size, int)
            or self.size < 0
        ):
            raise ValueError("Tamaño de objeto inválido")
        if not isinstance(self.sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", self.sha256
        ):
            raise ValueError("Se requiere SHA-256 hexadecimal")
