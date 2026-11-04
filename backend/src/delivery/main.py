"""Composición de FastAPI: configuración, arranque, errores y rutas."""

import os
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI

from delivery.errors import register_error_handlers
from delivery.ml.base import DurationPredictor
from delivery.ml.duration_model import LocalDurationPredictor
from delivery.models.pricing import PricingPolicy
from delivery.models.vehicle_rules import VehiclePolicy
from delivery.repositories.base import OrderRepository
from delivery.routers.businesses import businesses_router
from delivery.routers.courier_routes import courier_routes_router
from delivery.routers.couriers import couriers_router
from delivery.routers.delivery_predictions import delivery_prediction_router
from delivery.routers.food import food_router
from delivery.routers.health import health_router
from delivery.routers.operations import operations_router
from delivery.routers.orders import orders_router
from delivery.routers.quotes import quotes_router
from delivery.startup import application_lifespan


def create_app(
    model_directory: Optional[Path] = None,
    predictor_factory: Callable[[Path], DurationPredictor] = LocalDurationPredictor,
    *,
    orders: Optional[OrderRepository] = None,
    pricing_policy: Optional[PricingPolicy] = None,
    vehicle_policy: Optional[VehiclePolicy] = None,
    mongo_storage=None,
) -> FastAPI:
    application = FastAPI(
        title="Asistente de Delivery Económico",
        version="0.1.0",
        description="Gestiona negocios, repartidores y pedidos. Estima la duración de las entregas y su riesgo de retraso.",
        openapi_tags=[
            {
                "name": "Estado",
                "description": "Disponibilidad de la API y sus modelos.",
            },
            {
                "name": "Predicciones",
                "description": "Duración estimada y riesgo de retraso.",
            },
            {"name": "Negocios", "description": "Registro y consulta de negocios."},
            {
                "name": "Repartidores",
                "description": "Vehículos, aprobación y disponibilidad.",
            },
            {"name": "Pedidos", "description": "Registro y seguimiento de entregas."},
            {
                "name": "Cotizaciones",
                "description": "Costos estimados y opciones de vehículo.",
            },
        ],
        lifespan=application_lifespan(
            model_directory,
            predictor_factory,
            orders,
            pricing_policy,
            vehicle_policy,
            mongo_storage,
        ),
    )

    register_error_handlers(application)
    for factory in (
        health_router,
        quotes_router,
        food_router,
        businesses_router,
        couriers_router,
        orders_router,
        courier_routes_router,
        operations_router,
        delivery_prediction_router,
    ):
        application.include_router(factory())
    if os.environ.get("DELIVERY_DEMO_ENABLED") == "1":
        from delivery.routers.demonstration import demonstration_router

        application.include_router(demonstration_router())
    return application


app = create_app()
