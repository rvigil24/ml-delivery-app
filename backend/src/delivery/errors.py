"""Respuestas de error uniformes, sin detalles privados del servidor."""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from delivery.models.assignments import (
    AssignmentConflict,
    AssignmentNotFound,
    CourierNotFound,
)
from delivery.models.cash import CashConflict, CashNotFound
from delivery.models.catalogs import (
    CatalogConflict,
    CatalogNotFound,
    StorageUnavailable,
)
from delivery.models.estimation import PredictionUnavailable
from delivery.models.order_lifecycle import (
    BusinessNotFound,
    MissingPrerequisite,
    OrderConflict,
    OrderNotFound,
)
from delivery.services.quote_previews import QuoteConfigurationMissing

logger = logging.getLogger("delivery.main")


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status, content={"detail": {"code": code, "message": message}}
    )


def register_error_handlers(application):
    @application.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, error: RequestValidationError):
        return error_response(
            422, "invalid_request", "Entrada inválida. Consulte el esquema en /docs."
        )

    @application.exception_handler(PredictionUnavailable)
    async def unavailable(request: Request, error: PredictionUnavailable):
        return error_response(
            503, "prediction_unavailable", "La predicción no está disponible."
        )

    @application.exception_handler(QuoteConfigurationMissing)
    async def quote_configuration_missing(
        request: Request, error: QuoteConfigurationMissing
    ):
        return error_response(
            503,
            "quote_configuration_missing",
            "Configura las tarifas y los límites de vehículos para calcular una cotización.",
        )

    @application.exception_handler(OrderNotFound)
    async def order_not_found(request: Request, error: OrderNotFound):
        return error_response(404, "order_not_found", "Pedido inexistente.")

    @application.exception_handler(OrderConflict)
    async def order_conflict(request: Request, error: OrderConflict):
        return error_response(
            409, "order_conflict", "El estado del pedido no permite esta operación."
        )

    @application.exception_handler(StorageUnavailable)
    async def storage_unavailable(request: Request, error: StorageUnavailable):
        return error_response(
            503, "storage_unavailable", "La base de datos no está disponible."
        )

    @application.exception_handler(CatalogNotFound)
    @application.exception_handler(BusinessNotFound)
    @application.exception_handler(AssignmentNotFound)
    @application.exception_handler(CourierNotFound)
    @application.exception_handler(CashNotFound)
    async def catalog_not_found(request: Request, error: Exception):
        return error_response(
            404, "entity_not_found", "No se encontró el registro solicitado."
        )

    @application.exception_handler(CatalogConflict)
    @application.exception_handler(MissingPrerequisite)
    @application.exception_handler(AssignmentConflict)
    @application.exception_handler(CashConflict)
    async def operation_conflict(request: Request, error: Exception):
        return error_response(
            409,
            "operation_conflict",
            "El registro no cumple los requisitos para realizar este cambio.",
        )

    @application.exception_handler(Exception)
    async def unexpected(request: Request, error: Exception):
        logger.error(
            "Fallo interno de la API",
            exc_info=(type(error), error, error.__traceback__),
        )
        return error_response(500, "internal_error", "Error interno del servidor.")
