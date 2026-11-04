"""Puerto de inferencia; no recibe distancia, vehículo ni etiquetas futuras."""

from datetime import datetime
from typing import Protocol

from delivery.domain.models import DeliveryDuration


class DurationPredictor(Protocol):
    def predict(self, requested_at: datetime) -> DeliveryDuration:
        """Usar fecha de creación con zona horaria y devolver minutos/procedencia."""
        ...
