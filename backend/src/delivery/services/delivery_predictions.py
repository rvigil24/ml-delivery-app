"""Inferencia por recorrido y plazo, independiente del cálculo de tarifas."""

from delivery.domain.estimation import PredictionUnavailable


class DeliveryEstimationService:
    def __init__(self, predictor=None, *, source=None):
        self.predictor = predictor
        self.source = source or ("local" if predictor is not None else "unavailable")

    def predict(self, requested_at, origin, destination, promised_minutes):
        if self.predictor is None:
            raise PredictionUnavailable("Modelo ETA/riesgo no disponible")
        result = dict(self.predictor.predict(requested_at, origin, destination, promised_minutes))
        experimental = result.pop("academic_only", True)
        labels = {
            "Datos chinos: sin validación para El Salvador o por vehículo":
                "Modelo experimental: validación local y por vehículo pendiente."
        }
        return {**result, "model_source": self.source, "experimental": experimental,
                "limitations": [labels.get(text, text) for text in result.get("limitations", [])]}
