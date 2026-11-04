"""Adaptador del bundle propio ETA/riesgo; carga única, sin entrenar en requests."""


class LocalDeliveryModelV2:
    def __init__(self, directory):
        from delivery_ml.delivery_v2 import DeliveryPredictorV2
        self.model = DeliveryPredictorV2(directory)

    def predict(self, requested_at, origin, destination, promised_minutes):
        return self.model.predict(requested_at, origin, destination, promised_minutes)
