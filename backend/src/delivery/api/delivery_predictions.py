"""Entrada geográfica de la revisión ML, sin romper /predict temporal v1."""

from fastapi import APIRouter, Body, Request
from pydantic import Field

from delivery.domain.models import Location
from .schemas import ErrorResponse, PredictRequest
from .storage import LocationInput, valid


class DeliveryPredictionRequest(PredictRequest):
    origin: LocationInput
    destination: LocationInput
    promised_minutes: float = Field(gt=0, allow_inf_nan=False, strict=True)


PRESENTATION_EXAMPLES = {
    "recorrido_corto": {
        "summary": "Recorrido corto · plazo de 30 minutos",
        "description": "Puntos y plazo ilustrativos para exposición; no representan un envío real.",
        "value": {
            "requested_at": "2026-11-04T12:00:00-06:00",
            "origin": {"latitude": 13.6929, "longitude": -89.2182},
            "destination": {"latitude": 13.7000, "longitude": -89.2000},
            "promised_minutes": 30.0,
        },
    },
    "plazo_amplio": {
        "summary": "Mismo recorrido · plazo de 60 minutos",
        "description": "Permite comparar el riesgo aprendido al cambiar solo el plazo ilustrativo.",
        "value": {
            "requested_at": "2026-11-04T12:00:00-06:00",
            "origin": {"latitude": 13.6929, "longitude": -89.2182},
            "destination": {"latitude": 13.7000, "longitude": -89.2000},
            "promised_minutes": 60.0,
        },
    },
    "recorrido_largo": {
        "summary": "Otro recorrido · plazo de 45 minutos",
        "description": "Escenario simulado para comparar distancia y estimación. Sin resultados prefabricados.",
        "value": {
            "requested_at": "2026-11-04T12:00:00-06:00",
            "origin": {"latitude": 13.6929, "longitude": -89.2182},
            "destination": {"latitude": 13.7250, "longitude": -89.2450},
            "promised_minutes": 45.0,
        },
    },
}


def delivery_prediction_router():
    router = APIRouter(tags=["ML: duración del envío y riesgo de retraso"])

    @router.post("/predict/delivery", summary="Estimar duración y probabilidad de superar el plazo indicado",
                 responses={code: {"model": ErrorResponse} for code in (422, 503, 500)})
    def predict_delivery(request: Request,
                         body: DeliveryPredictionRequest = Body(..., openapi_examples=PRESENTATION_EXAMPLES)):
        return valid(lambda: request.app.state.delivery_estimates.predict(body.requested_at,
            Location(**body.origin.model_dump()), Location(**body.destination.model_dump()), body.promised_minutes))

    return router
