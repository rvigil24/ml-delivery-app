"""ETA y riesgo: variables conocidas antes de entregar, sin IDs o eventos futuros."""

import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from delivery_ml.artifact import environment_versions
from delivery_ml.model_data import temporal_features


SCHEMA = "delivery-eta-risk-v2"
CONTEXT = ["request_hour_utc", "request_weekday_utc", "distance_km"]
RISK_CONTEXT = CONTEXT + ["promised_minutes"]


def spherical_distance(latitude1, longitude1, latitude2, longitude2):
    points = np.asarray([latitude1, longitude1, latitude2, longitude2], dtype=float)
    if not np.isfinite(points).all():
        raise ValueError("Coordenadas no finitas")
    if (np.abs(points[[0, 2]]) > 90).any() or (np.abs(points[[1, 3]]) > 180).any():
        raise ValueError("Coordenadas fuera de rango")
    lat1, lng1, lat2, lng2 = np.radians(points)
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lng2-lng1)/2)**2
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def eta_features(context):
    result = temporal_features(context)
    distance = pd.to_numeric(context["distance_km"], errors="raise")
    if not np.isfinite(distance).all() or distance.lt(0).any():
        raise ValueError("Distancia no válida")
    result["distance_km"] = distance
    return result


def risk_features(context):
    result = eta_features(context)
    promise = pd.to_numeric(context["promised_minutes"], errors="raise")
    if not np.isfinite(promise).all() or promise.le(0).any():
        raise ValueError("Plazo prometido no válido")
    result["promised_minutes"] = promise
    return result


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class DeliveryPredictorV2:
    """Cargar solo artefactos propios; pickle no autentica al autor."""

    def __init__(self, directory):
        folder = Path(directory)
        self.metadata = json.loads((folder / "metadata.json").read_text())
        if self.metadata["schema"] != SCHEMA or self.metadata["environment"] != environment_versions():
            raise ValueError("Contrato o entorno de modelo v2 incompatible")
        if self.metadata["eta_inputs"] != CONTEXT or self.metadata["risk_inputs"] != RISK_CONTEXT:
            raise ValueError("Entradas de modelo incompatibles")
        for name in ("eta.pkl", "risk.pkl", "evidence.json", "model_card.md"):
            if sha256(folder / name) != self.metadata["files"][name]:
                raise ValueError("Hash del bundle incompatible")
        with (folder / "eta.pkl").open("rb") as stream:
            self.eta = pickle.load(stream)
        with (folder / "risk.pkl").open("rb") as stream:
            self.risk = pickle.load(stream)

    def predict(self, requested_at, origin, destination, promised_minutes):
        from datetime import timezone
        if requested_at.tzinfo is None:
            raise ValueError("Fecha con zona horaria requerida")
        stamp = requested_at.astimezone(timezone.utc)
        distance = float(spherical_distance(origin.latitude, origin.longitude,
                                             destination.latitude, destination.longitude))
        context = pd.DataFrame({"request_hour_utc": [stamp.hour], "request_weekday_utc": [stamp.weekday()],
                                "distance_km": [distance], "promised_minutes": [promised_minutes]})
        # Mismo contrato de validación independientemente del algoritmo seleccionado.
        risk_features(context)
        minutes = float(self.eta.predict(context[CONTEXT])[0])
        risk = float(self.risk.predict_proba(context[RISK_CONTEXT])[0, 1])
        if not np.isfinite(minutes) or minutes < 0 or not np.isfinite(risk) or not 0 <= risk <= 1:
            raise ValueError("Salida del modelo fuera de dominio")
        outside = any(not bounds[0] <= float(context[name].iloc[0]) <= bounds[1]
                      for name, bounds in self.metadata["training_input_ranges"].items())
        return {"model_version": self.metadata["model_version"], "estimated_minutes": minutes,
                "late_probability": risk, "promised_minutes": float(promised_minutes),
                "distance_km": distance, "eta_algorithm": self.metadata["eta_algorithm"],
                "risk_algorithm": self.metadata["risk_algorithm"], "outside_training_range": outside,
                "academic_only": True, "local_validation": False,
                "limitations": self.metadata["limitations"]}
