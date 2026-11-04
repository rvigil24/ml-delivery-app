"""T32: coordinar CRUD de datos sin permitir cambios ciegos o borrar referencias."""

from typing import Generic, Tuple, TypeVar

from delivery.domain.catalogs import CatalogNotFound
from delivery.ports.catalogs import CatalogRepository


T = TypeVar("T")


class CatalogService(Generic[T]):
    def __init__(self, repository: CatalogRepository[T]) -> None:
        self._repository = repository

    def get(self, identifier: str) -> T:
        entity = self._repository.get(identifier)
        if entity is None:
            raise CatalogNotFound(identifier)
        return entity

    def list(self, limit: int) -> Tuple[T, ...]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit debe ser un entero entre 1 y 100")
        return self._repository.list(limit)

    def create(self, entity: T) -> T:
        return self._repository.create(entity)

    def update(self, identifier: str, entity: T) -> T:
        if entity.id != identifier:
            raise ValueError("El ID no se puede cambiar")
        return self._repository.update(entity, self.get(identifier))

    def delete(self, identifier: str) -> None:
        self._repository.delete(identifier, self.get(identifier))
