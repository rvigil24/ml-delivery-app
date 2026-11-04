"""Acceso a los servicios configurados durante el arranque."""

from delivery.models.catalogs import StorageUnavailable


def service(request, name):
    value = getattr(request.app.state, name, None)
    if value is None:
        raise StorageUnavailable("No hay persistencia configurada")
    return value
