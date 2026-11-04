"""Carga de modelos, conexión de base de datos y cierre de recursos."""

import asyncio
import logging
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from delivery.models.catalogs import StorageUnavailable
from delivery.services.assignments import DispatchOrderRequirements
from delivery.services.catalogs import CatalogService
from delivery.services.orders import OrderService
from delivery.services.predictions import PredictionService
from delivery.services.quote_previews import QuotePreviewService

logger = logging.getLogger("delivery.main")


def application_lifespan(
    model_directory,
    predictor_factory,
    orders,
    pricing_policy,
    vehicle_policy,
    mongo_storage,
):
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        model_cache = None
        delivery_cache = None
        from delivery.services.delivery_predictions import DeliveryEstimationService

        delivery_model = None
        delivery_directory = os.environ.get("DELIVERY_MODEL_V2_DIR")
        delivery_source = "local" if delivery_directory else "unavailable"
        if delivery_directory or os.environ.get("DELIVERY_MODEL_V2_MANIFEST_KEY"):
            try:
                if not delivery_directory:
                    from delivery.models.objects import ObjectReference
                    from delivery.services.model_files import download_model_bundle
                    from delivery.storage.s3 import create_s3_store

                    reference = ObjectReference(
                        os.environ.get("S3_BUCKET", "ml-kodigo-resources"),
                        os.environ["DELIVERY_MODEL_V2_MANIFEST_KEY"],
                        int(os.environ["DELIVERY_MODEL_V2_MANIFEST_SIZE"]),
                        os.environ["DELIVERY_MODEL_V2_MANIFEST_SHA256"],
                    )
                    store = create_s3_store(
                        profile=os.environ.get("DELIVERY_AWS_PROFILE") or None,
                        bucket=reference.bucket,
                        region=os.environ.get("AWS_REGION", "us-east-1"),
                        endpoint=os.environ.get("S3_ENDPOINT_URL") or None,
                    )
                    try:
                        delivery_cache = tempfile.TemporaryDirectory(
                            prefix="delivery-model-v2-"
                        )
                        delivery_directory = download_model_bundle(
                            store,
                            reference,
                            Path(delivery_cache.name),
                            schema="delivery-s3-model-v2",
                        )
                    finally:
                        store.client.close()
                    delivery_source = "s3"
                from delivery.ml.delivery_model import LocalDeliveryModelV2

                delivery_model = LocalDeliveryModelV2(Path(delivery_directory))
            except Exception:
                logger.warning(
                    "Modelo ETA/riesgo no disponible; revisar configuración, hashes y entorno"
                )
                delivery_source = "unavailable"
                if delivery_cache is not None:
                    delivery_cache.cleanup()
                    delivery_cache = None
        application.state.delivery_estimates = DeliveryEstimationService(
            delivery_model, source=delivery_source
        )
        storage, owned_storage = mongo_storage, False
        if storage is None and (
            os.environ.get("MONGODB_URI") or os.environ.get("MONGODB_DATABASE")
        ):
            from delivery.database.connection import MongoStorage

            # Atlas puede necesitar otro intento al abrir conexiones TLS nuevas.
            for attempt in range(3):
                try:
                    storage = MongoStorage(
                        os.environ.get("MONGODB_URI"),
                        os.environ.get("MONGODB_DATABASE"),
                    )
                    storage.verify_schema()
                    owned_storage = True
                    break
                except StorageUnavailable:
                    if storage is not None:
                        storage.close()
                        storage = None
                    if attempt < 2:
                        await asyncio.sleep(1)
            if storage is None:
                logger.warning(
                    "Persistencia MongoDB no disponible; no se usará un reemplazo en memoria"
                )
        effective_orders = (
            orders
            if orders is not None
            else (storage.orders if storage is not None else None)
        )
        application.state.mongo_storage = storage
        application.state.business_catalog = (
            CatalogService(storage.businesses) if storage is not None else None
        )
        from delivery.services.food_catalog import FoodCatalogService

        application.state.food_catalog = (
            FoodCatalogService(storage.businesses) if storage is not None else None
        )
        application.state.courier_catalog = (
            CatalogService(storage.couriers) if storage is not None else None
        )
        application.state.order_service = (
            OrderService(
                effective_orders,
                storage.businesses,
                DispatchOrderRequirements(effective_orders),
            )
            if storage is not None
            else None
        )
        from delivery.services.courier_routes import CourierRouteService

        application.state.courier_routes = (
            CourierRouteService(storage.orders, application.state.order_service)
            if storage is not None
            else None
        )
        configured = (
            model_directory
            if model_directory is not None
            else os.environ.get("DELIVERY_MODEL_DIR")
        )
        if not configured and os.environ.get("DELIVERY_MODEL_MANIFEST_KEY"):
            try:
                from delivery.models.objects import ObjectReference
                from delivery.services.model_files import download_model_bundle
                from delivery.storage.s3 import create_s3_store

                reference = ObjectReference(
                    os.environ.get("S3_BUCKET", "ml-kodigo-resources"),
                    os.environ["DELIVERY_MODEL_MANIFEST_KEY"],
                    int(os.environ["DELIVERY_MODEL_MANIFEST_SIZE"]),
                    os.environ["DELIVERY_MODEL_MANIFEST_SHA256"],
                )
                store = create_s3_store(
                    profile=os.environ.get("DELIVERY_AWS_PROFILE") or None,
                    bucket=reference.bucket,
                    region=os.environ.get("AWS_REGION", "us-east-1"),
                    endpoint=os.environ.get("S3_ENDPOINT_URL") or None,
                )
                model_cache = tempfile.TemporaryDirectory(prefix="delivery-model-")
                try:
                    configured = download_model_bundle(
                        store, reference, Path(model_cache.name)
                    )
                finally:
                    store.client.close()
            except Exception:
                logger.warning(
                    "No se pudo recuperar el bundle S3 verificado; inferencia no disponible"
                )
                if model_cache is not None:
                    model_cache.cleanup()
                    model_cache = None
        predictor = None
        if configured:
            try:
                predictor = predictor_factory(Path(configured))
            except Exception:
                # El detalle es diagnóstico local; nunca forma parte de la respuesta HTTP.
                logger.exception(
                    "No se pudo cargar el modelo local; inferencia no disponible"
                )
        application.state.predictions = PredictionService(predictor)
        application.state.quote_previews = QuotePreviewService(
            effective_orders,
            application.state.predictions,
            pricing_policy,
            vehicle_policy,
        )
        application.state.model_available = delivery_model is not None
        try:
            yield
        finally:
            if owned_storage:
                storage.close()
            if model_cache is not None:
                model_cache.cleanup()
            if delivery_cache is not None:
                delivery_cache.cleanup()

    return lifespan
