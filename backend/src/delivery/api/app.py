"""T30: API local de inferencia con carga única del bundle T19 al arrancar."""

from contextlib import asynccontextmanager
from datetime import timezone
import logging
import os
from pathlib import Path
import tempfile
from typing import Callable, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from delivery.adapters.local_model import LocalDurationPredictor
from delivery.domain.estimation import PredictionUnavailable
from delivery.domain.catalogs import CatalogConflict, CatalogNotFound, StorageUnavailable
from delivery.domain.assignments import AssignmentConflict, AssignmentNotFound, CourierNotFound
from delivery.domain.cash import CashConflict, CashNotFound
from delivery.domain.order_lifecycle import BusinessNotFound, MissingPrerequisite, OrderConflict, OrderNotFound
from delivery.domain.pricing import OperatorCosts, PricingPolicy
from delivery.domain.vehicle_rules import VehiclePolicy
from delivery.ports.estimation import DurationPredictor
from delivery.ports.orders import OrderRepository
from delivery.services.predictions import PredictionService
from delivery.services.catalogs import CatalogService
from delivery.services.orders import OrderService
from delivery.services.assignments import DispatchOrderRequirements
from delivery.services.quote_previews import QuoteConfigurationMissing, QuotePreviewService
from .schemas import (
    ErrorResponse, HealthResponse, PredictRequest, PredictResponse, QuoteAmountsResponse,
    QuotePreviewRequest, QuotePreviewResponse, VehicleDecisionResponse,
)
from .storage import storage_router


logger = logging.getLogger(__name__)


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"detail": {"code": code, "message": message}})


def create_app(model_directory: Optional[Path] = None,
               predictor_factory: Callable[[Path], DurationPredictor] = LocalDurationPredictor, *,
               orders: Optional[OrderRepository] = None, pricing_policy: Optional[PricingPolicy] = None,
               vehicle_policy: Optional[VehiclePolicy] = None, mongo_storage=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        model_cache = None
        from delivery.services.delivery_predictions import DeliveryEstimationService
        delivery_model = None
        if os.environ.get("DELIVERY_MODEL_V2_DIR"):
            try:
                from delivery.adapters.delivery_model_v2 import LocalDeliveryModelV2
                delivery_model = LocalDeliveryModelV2(Path(os.environ["DELIVERY_MODEL_V2_DIR"]))
            except Exception:
                logger.warning("Modelo ETA/riesgo no disponible; revisar bundle y entorno")
        application.state.delivery_estimates = DeliveryEstimationService(delivery_model)
        storage, owned_storage = mongo_storage, False
        if storage is None and (os.environ.get("MONGODB_URI") or os.environ.get("MONGODB_DATABASE")):
            from delivery.adapters.mongo import MongoStorage
            try:
                storage = MongoStorage(os.environ.get("MONGODB_URI"), os.environ.get("MONGODB_DATABASE"))
                storage.verify_schema()
                owned_storage = True
            except StorageUnavailable:
                if storage is not None:
                    storage.close()
                    storage = None
                logger.warning("Persistencia MongoDB no disponible; no se usará un reemplazo en memoria")
        effective_orders = orders if orders is not None else (storage.orders if storage is not None else None)
        application.state.mongo_storage = storage
        application.state.business_catalog = CatalogService(storage.businesses) if storage is not None else None
        application.state.courier_catalog = CatalogService(storage.couriers) if storage is not None else None
        application.state.order_service = OrderService(effective_orders, storage.businesses,
            DispatchOrderRequirements(effective_orders)) if storage is not None else None
        configured = model_directory if model_directory is not None else os.environ.get("DELIVERY_MODEL_DIR")
        if not configured and os.environ.get("DELIVERY_MODEL_MANIFEST_KEY"):
            try:
                from delivery.adapters.s3 import create_s3_store
                from delivery.domain.objects import ObjectReference
                from delivery.services.model_files import download_model_bundle
                reference = ObjectReference(os.environ.get("S3_BUCKET", "ml-kodigo-resources"),
                    os.environ["DELIVERY_MODEL_MANIFEST_KEY"], int(os.environ["DELIVERY_MODEL_MANIFEST_SIZE"]),
                    os.environ["DELIVERY_MODEL_MANIFEST_SHA256"])
                store = create_s3_store(profile=os.environ.get("DELIVERY_AWS_PROFILE") or None,
                    bucket=reference.bucket, region=os.environ.get("AWS_REGION", "us-east-1"),
                    endpoint=os.environ.get("S3_ENDPOINT_URL") or None)
                model_cache = tempfile.TemporaryDirectory(prefix="delivery-model-")
                try:
                    configured = download_model_bundle(store, reference, Path(model_cache.name))
                finally:
                    store.client.close()
            except Exception:
                logger.warning("No se pudo recuperar el bundle S3 verificado; inferencia no disponible")
                if model_cache is not None:
                    model_cache.cleanup()
                    model_cache = None
        predictor = None
        if configured:
            try:
                predictor = predictor_factory(Path(configured))
            except Exception:
                # El detalle es diagnóstico local; nunca forma parte de la respuesta HTTP.
                logger.exception("No se pudo cargar el modelo local; inferencia no disponible")
        application.state.predictions = PredictionService(predictor)
        application.state.quote_previews = QuotePreviewService(effective_orders, application.state.predictions,
                                                               pricing_policy, vehicle_policy)
        application.state.model_available = predictor is not None
        try:
            yield
        finally:
            if owned_storage:
                storage.close()
            if model_cache is not None:
                model_cache.cleanup()

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

    @application.exception_handler(StorageUnavailable)
    async def storage_unavailable(request: Request, error: StorageUnavailable):
        return error_response(503, "storage_unavailable", "La persistencia no está disponible.")

    @application.exception_handler(CatalogNotFound)
    @application.exception_handler(BusinessNotFound)
    @application.exception_handler(AssignmentNotFound)
    @application.exception_handler(CourierNotFound)
    @application.exception_handler(CashNotFound)
    async def catalog_not_found(request: Request, error: Exception):
        return error_response(404, "entity_not_found", "Entidad inexistente.")

    @application.exception_handler(CatalogConflict)
    @application.exception_handler(MissingPrerequisite)
    @application.exception_handler(AssignmentConflict)
    @application.exception_handler(CashConflict)
    async def operation_conflict(request: Request, error: Exception):
        return error_response(409, "operation_conflict", "Operación incompatible o sin requisitos validados.")

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

    application.include_router(storage_router())
    from .delivery_predictions import delivery_prediction_router
    application.include_router(delivery_prediction_router())
    if os.environ.get("DELIVERY_DEMO_ENABLED") == "1":
        from .demonstration import demonstration_router
        application.include_router(demonstration_router())
    return application


app = create_app()
