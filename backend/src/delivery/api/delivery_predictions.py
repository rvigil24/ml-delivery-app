"""Entrada geográfica de la revisión ML, sin romper /predict temporal v1."""

from fastapi import APIRouter, Request
from pydantic import Field

from delivery.domain.models import Location
from .schemas import ErrorResponse, PredictRequest
from .storage import LocationInput, valid


class DeliveryPredictionRequest(PredictRequest):
    origin: LocationInput
    destination: LocationInput
    promised_minutes: float = Field(gt=0, allow_inf_nan=False, strict=True)


def delivery_prediction_router():
    router = APIRouter(tags=["ML: duración del envío y riesgo de retraso"])

    @router.post("/predict/delivery", summary="Estimar duración y probabilidad de superar el plazo indicado",
                 responses={code: {"model": ErrorResponse} for code in (422, 503, 500)})
    def predict_delivery(body: DeliveryPredictionRequest, request: Request):
        return valid(lambda: request.app.state.delivery_estimates.predict(body.requested_at,
            Location(**body.origin.model_dump()), Location(**body.destination.model_dump()), body.promised_minutes))

    return router
