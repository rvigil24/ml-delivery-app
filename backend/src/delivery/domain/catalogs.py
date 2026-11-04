"""T32: errores de integridad para catálogos operativos."""


class CatalogConflict(RuntimeError):
    pass


class CatalogNotFound(LookupError):
    pass


class StorageUnavailable(RuntimeError):
    pass
