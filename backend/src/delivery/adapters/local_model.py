"""T21: inferencia local con un bundle T19 propio, sin entrenar ni descargar."""

from datetime import datetime, timezone
import json
from pathlib import Path
import pickle

from delivery.domain.estimation import PredictionUnavailable
from delivery.domain.models import DeliveryDuration, DurationSource


INTERVAL_DEFINITION = "creación del pedido (platform_order_time) -> entrega (arrive_time)"


class LocalDurationPredictor:
    def __init__(self, directory: Path) -> None:
        # Imports del runtime ML solo en este adaptador, no en dominio/servicios.
        try:
            from delivery_ml.artifact import load_pipeline

            self._pipeline = load_pipeline(directory)
            metadata = json.loads((directory / "metadata.json").read_text())
            if metadata["target"] != "time_taken_min" or metadata["target_unit"] != "minutes":
                raise ValueError("Target/unidad incompatible con duración de entrega")
            self.model_version = metadata["model_version"]
            if not isinstance(self.model_version, str) or not self.model_version.strip():
                raise ValueError("Versión de modelo ausente")
            if not callable(getattr(self._pipeline, "predict", None)):
                raise ValueError("El artefacto no permite inferencia")
        except (OSError, ValueError, KeyError, pickle.UnpicklingError, ImportError) as error:
            raise PredictionUnavailable(f"Modelo local no disponible: {error}") from error

    def predict(self, requested_at: datetime) -> DeliveryDuration:
        if (not isinstance(requested_at, datetime) or requested_at.tzinfo is None
                or requested_at.utcoffset() is None):
            raise ValueError("La creación del pedido debe tener zona horaria")
        import pandas as pd

        stamp = requested_at.astimezone(timezone.utc)
        context = pd.DataFrame({"request_hour_utc": [stamp.hour], "request_weekday_utc": [stamp.weekday()]})
        try:
            prediction = self._pipeline.predict(context)
            if len(prediction) != 1:
                raise ValueError("Se esperaba una única predicción")
            return DeliveryDuration(float(prediction[0]), DurationSource.PREDICTION,
                                    INTERVAL_DEFINITION, self.model_version)
        except (ValueError, TypeError, IndexError) as error:
            raise PredictionUnavailable(f"Predicción no disponible: {error}") from error
