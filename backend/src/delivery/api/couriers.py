"""Registro, consulta y mantenimiento de repartidores."""

from typing import Tuple

from fastapi import APIRouter, Query, Request, Response

from delivery.domain.models import Courier

from .dependencies import service
from .request_models import CourierInput
from .response_models import ErrorResponse
from .validation import valid


def couriers_router():
    router = APIRouter(
        responses={
            status: {"model": ErrorResponse} for status in (404, 409, 422, 503, 500)
        }
    )

    def build(body: CourierInput):
        values = body.model_dump()
        return Courier(**values)

    @router.post(
        "/couriers",
        response_model=Courier,
        status_code=201,
        tags=["Repartidores"],
        name="post_couriers_create",
        summary="Registrar un repartidor",
        description="Registra el vehículo, la aprobación y la disponibilidad del repartidor.",
    )
    def create(body: CourierInput, request: Request):
        return valid(lambda: service(request, "courier_catalog").create(build(body)))

    @router.get(
        "/couriers",
        response_model=Tuple[Courier, ...],
        status_code=200,
        tags=["Repartidores"],
        name="get_couriers_listing",
        summary="Listar repartidores",
        description="Devuelve los repartidores registrados, con un límite de resultados.",
    )
    def listing(request: Request, limit: int = Query(100, ge=1, le=100)):
        return service(request, "courier_catalog").list(limit)

    @router.get(
        "/couriers/{identifier}",
        response_model=Courier,
        status_code=200,
        tags=["Repartidores"],
        name="get_couriers_get",
        summary="Consultar un repartidor",
        description="Devuelve los datos del repartidor indicado.",
    )
    def get(identifier: str, request: Request):
        return service(request, "courier_catalog").get(identifier)

    @router.put(
        "/couriers/{identifier}",
        response_model=Courier,
        status_code=200,
        tags=["Repartidores"],
        name="put_couriers_update",
        summary="Actualizar un repartidor",
        description="Guarda los datos actualizados del repartidor.",
    )
    def update(identifier: str, body: CourierInput, request: Request):
        return valid(
            lambda: service(request, "courier_catalog").update(identifier, build(body))
        )

    @router.delete(
        "/couriers/{identifier}",
        response_model=None,
        status_code=204,
        tags=["Repartidores"],
        name="delete_couriers_delete",
        summary="Eliminar un repartidor",
        description="Elimina un repartidor sin asignaciones registradas.",
    )
    def delete(identifier: str, request: Request):
        service(request, "courier_catalog").delete(identifier)
        return Response(status_code=204)

    return router
