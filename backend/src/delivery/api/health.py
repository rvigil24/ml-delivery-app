"""Rutas de estado del servicio."""

from fastapi import APIRouter, Request

from .response_models import HealthResponse


def health_router():
    router = APIRouter()

    @router.get(
        "/health",
        response_model=HealthResponse,
        tags=["Estado"],
        summary="Consultar el estado del servicio",
        description="Comprueba que la API responde e indica si los modelos de predicción están cargados.",
    )
    def health(request: Request) -> HealthResponse:
        return HealthResponse(model_available=request.app.state.model_available)

    return router
