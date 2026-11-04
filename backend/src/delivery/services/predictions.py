"""T30: inferencia académica por fecha de creación, sin precios o entrenamiento."""

from datetime import datetime, timezone
from typing import Optional

from delivery.domain.estimation import PredictionUnavailable
from delivery.domain.models import DeliveryDuration, DurationSource
from delivery.ports.estimation import DurationPredictor


class PredictionService:
    def __init__(self, predictor: Optional[DurationPredictor]) -> None:
        self._predictor = predictor

    def predict(self, requested_at: datetime) -> DeliveryDuration:
        if not isinstance(requested_at, datetime) or requested_at.tzinfo is None or requested_at.utcoffset() is None:
            raise ValueError("La fecha de creación debe tener zona horaria")
        if self._predictor is None:
            raise PredictionUnavailable("No hay modelo disponible")
        duration = self._predictor.predict(requested_at.astimezone(timezone.utc))
        if not isinstance(duration, DeliveryDuration) or duration.source is not DurationSource.PREDICTION:
            raise PredictionUnavailable("El predictor no devolvió una predicción de duración válida")
        return duration
