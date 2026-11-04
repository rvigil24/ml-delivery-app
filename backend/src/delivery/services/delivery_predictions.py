"""Inferencia por recorrido y plazo, independiente del cálculo de tarifas."""

from delivery.domain.estimation import PredictionUnavailable


class DeliveryEstimationService:
    def __init__(self, predictor=None):
        self.predictor = predictor

    def predict(self, requested_at, origin, destination, promised_minutes):
        if self.predictor is None:
            raise PredictionUnavailable("Modelo ETA/riesgo no disponible")
        return self.predictor.predict(requested_at, origin, destination, promised_minutes)
