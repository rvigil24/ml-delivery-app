"""T30: API local de inferencia con carga única del bundle T19 al arrancar."""

from contextlib import asynccontextmanager
from datetime import timezone
import logging
import os
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from delivery.adapters.local_model import LocalDurationPredictor
from delivery.domain.estimation import PredictionUnavailable
from delivery.domain.order_lifecycle import OrderConflict, OrderNotFound
from delivery.domain.pricing import OperatorCosts, PricingPolicy
from delivery.domain.vehicle_rules import VehiclePolicy
from delivery.ports.estimation import DurationPredictor
from delivery.ports.orders import OrderRepository
from delivery.services.predictions import PredictionService
from delivery.services.quote_previews import QuoteConfigurationMissing, QuotePreviewService
from .schemas import (
    ErrorResponse, HealthResponse, PredictRequest, PredictResponse, QuoteAmountsResponse,
    QuotePreviewRequest, QuotePreviewResponse, VehicleDecisionResponse,
)


logger = logging.getLogger(__name__)


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"detail": {"code": code, "message": message}})


def create_app(model_directory: Optional[Path] = None,
               predictor_factory: Callable[[Path], DurationPredictor] = LocalDurationPredictor, *,
               orders: Optional[OrderRepository] = None, pricing_policy: Optional[PricingPolicy] = None,
               vehicle_policy: Optional[VehiclePolicy] = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        configured = model_directory if model_directory is not None else os.environ.get("DELIVERY_MODEL_DIR")
        predictor = None
        if configured:
            try:
                predictor = predictor_factory(Path(configured))
            except Exception:
                # El detalle es diagnóstico local; nunca forma parte de la respuesta HTTP.
                logger.exception("No se pudo cargar el modelo local; inferencia no disponible")
        application.state.predictions = PredictionService(predictor)
        application.state.quote_previews = QuotePreviewService(orders, application.state.predictions,
                                                               pricing_policy, vehicle_policy)
        application.state.model_available = predictor is not None
        yield

    application = FastAPI(title="Asistente de Delivery Económico", version="0.1.0",
        description="Inferencia académica de duración; sin cotización comercial o validación local.", lifespan=lifespan)

    @application.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, error: RequestValidationError):
        return error_response(422, "invalid_request", "Entrada inválida. Consulte el esquema en /docs.")

    @application.exception_handler(PredictionUnavailable)
    async def unavailable(request: Request, error: PredictionUnavailable):
        return error_response(503, "prediction_unavailable", "La predicción no está disponible.")

    @application.exception_handler(QuoteConfigurationMissing)
    async def quote_configuration_missing(request: Request, error: QuoteConfigurationMissing):
        return error_response(503, "quote_configuration_missing", "Falta configuración de cotizaciones académicas.")

    @application.exception_handler(OrderNotFound)
    async def order_not_found(request: Request, error: OrderNotFound):
        return error_response(404, "order_not_found", "Pedido inexistente.")

    @application.exception_handler(OrderConflict)
    async def order_conflict(request: Request, error: OrderConflict):
        return error_response(409, "order_conflict", "El estado del pedido no permite esta operación.")

    @application.exception_handler(Exception)
    async def unexpected(request: Request, error: Exception):
        logger.error("Fallo interno de la API", exc_info=(type(error), error, error.__traceback__))
        return error_response(500, "internal_error", "Error interno del servidor.")

    @application.get("/health", response_model=HealthResponse, tags=["Proceso"],
                     summary="Comprobar proceso y carga inicial del modelo")
    def health(request: Request) -> HealthResponse:
        return HealthResponse(model_available=request.app.state.model_available)

    @application.post("/predict", response_model=PredictResponse, tags=["Inferencia académica"],
        summary="Estimar duración creación–entrega usando calendario UTC",
        responses={422: {"model": ErrorResponse, "description": "Entrada inválida"},
                   503: {"model": ErrorResponse, "description": "Modelo o predicción no disponibles"},
                   500: {"model": ErrorResponse, "description": "Error interno"}})
    def predict(payload: PredictRequest, request: Request) -> PredictResponse:
        stamp = payload.requested_at.astimezone(timezone.utc)
        duration = request.app.state.predictions.predict(stamp)
        return PredictResponse(requested_at_utc=stamp, duration_minutes=duration.minutes,
            duration_source=duration.source.value, interval_definition=duration.interval_definition,
            model_version=duration.model_version)

    @application.post("/orders/{order_id}/quotes", response_model=QuotePreviewResponse,
        tags=["Cotización académica"], summary="Previsualizar duración, importes y vehículos sin emitir cotización",
        responses={status: {"model": ErrorResponse} for status in (404, 409, 422, 503, 500)})
    def quote_preview(order_id: str, payload: QuotePreviewRequest, request: Request):
        try:
            preview = request.app.state.quote_previews.preview(order_id, payload.quote_id, payload.load_kg,
                OperatorCosts(payload.costs.currency, payload.costs.variable_cost, payload.costs.attributable_cost))
        except ValueError:
            return error_response(422, "invalid_request", "Datos incompatibles con la política configurada.")
        quote = preview.quote
        duration = quote.duration
        return QuotePreviewResponse(quote_id=quote.id, order_id=quote.order_id,
            distance_km=preview.pricing.distance_km, distance_method=quote.distance_method,
            duration=PredictResponse(requested_at_utc=preview.record.events[0].occurred_at.astimezone(timezone.utc),
                duration_minutes=duration.minutes, duration_source=duration.source.value,
                interval_definition=duration.interval_definition, model_version=duration.model_version),
            amounts=QuoteAmountsResponse(**vars(preview.pricing.amounts)),
            pricing_policy_version=preview.pricing.policy.version, vehicle_policy_version=preview.vehicles.policy.version,
            service_area_id=preview.vehicles.policy.area.id, load_kg=preview.vehicles.load_kg,
            within_configured_area=preview.vehicles.within_configured_area,
            eligible_vehicles=preview.vehicles.eligible_vehicles,
            vehicle_decisions=tuple(VehicleDecisionResponse(vehicle=decision.vehicle, reasons=decision.reasons)
                                   for decision in preview.vehicles.decisions),
            limitations=preview.pricing.estimate.limitations)

    return application


app = create_app()
