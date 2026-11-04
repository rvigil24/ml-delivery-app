"""Registro, consulta y mantenimiento de negocios."""

from typing import Tuple

from fastapi import APIRouter, Query, Request, Response

from delivery.dependencies import service
from delivery.models.entities import Business, Location
from delivery.schemas.requests import BusinessInput
from delivery.schemas.responses import ErrorResponse
from delivery.validation import valid


def businesses_router():
    router = APIRouter(
        responses={
            status: {"model": ErrorResponse} for status in (404, 409, 422, 503, 500)
        }
    )

    def build(body: BusinessInput):
        values = body.model_dump()
        values["location"] = Location(**values["location"])
        return Business(**values)

    @router.post(
        "/businesses",
        response_model=Business,
        status_code=201,
        tags=["Negocios"],
        name="post_businesses_create",
        summary="Registrar un negocio",
        description="Guarda el nombre y la ubicación del negocio.",
    )
    def create(body: BusinessInput, request: Request):
        return valid(lambda: service(request, "business_catalog").create(build(body)))

    @router.get(
        "/businesses",
        response_model=Tuple[Business, ...],
        status_code=200,
        tags=["Negocios"],
        name="get_businesses_listing",
        summary="Listar negocios",
        description="Devuelve los negocios registrados, con un límite de resultados.",
    )
    def listing(request: Request, limit: int = Query(100, ge=1, le=100)):
        return service(request, "business_catalog").list(limit)

    @router.get(
        "/businesses/{identifier}",
        response_model=Business,
        status_code=200,
        tags=["Negocios"],
        name="get_businesses_get",
        summary="Consultar un negocio",
        description="Devuelve los datos del negocio indicado.",
    )
    def get(identifier: str, request: Request):
        return service(request, "business_catalog").get(identifier)

    @router.put(
        "/businesses/{identifier}",
        response_model=Business,
        status_code=200,
        tags=["Negocios"],
        name="put_businesses_update",
        summary="Actualizar un negocio",
        description="Guarda los datos actualizados del negocio.",
    )
    def update(identifier: str, body: BusinessInput, request: Request):
        return valid(
            lambda: service(request, "business_catalog").update(identifier, build(body))
        )

    @router.delete(
        "/businesses/{identifier}",
        response_model=None,
        status_code=204,
        tags=["Negocios"],
        name="delete_businesses_delete",
        summary="Eliminar un negocio",
        description="Elimina un negocio sin pedidos asociados.",
    )
    def delete(identifier: str, request: Request):
        service(request, "business_catalog").delete(identifier)
        return Response(status_code=204)

    return router
