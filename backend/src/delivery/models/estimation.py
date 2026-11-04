"""T21: distancia esférica de referencia y borrador académico explícito."""

import math
from dataclasses import dataclass, field
from typing import Tuple

from delivery.models.entities import DurationSource, Location, Quote

# Radio medio IUGG para WGS-84: (2a+b)/3; no es un límite de servicio.
# https://geopy.readthedocs.io/en/stable/#calculating-distance
EARTH_RADIUS_KM = 6371.0087714150598
DISTANCE_METHOD = "haversine_great_circle_iugg_mean_radius"


class PredictionUnavailable(RuntimeError):
    pass


def haversine_km(origin: Location, destination: Location) -> float:
    if not isinstance(origin, Location) or not isinstance(destination, Location):
        raise ValueError("Origen y destino deben ser Location en grados geográficos")
    lat1, lat2 = math.radians(origin.latitude), math.radians(destination.latitude)
    delta_lat = lat2 - lat1
    delta_lon = math.radians(destination.longitude - origin.longitude)
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    value = min(1.0, max(0.0, value))  # Redondeo numérico cerca de puntos antípodas.
    return EARTH_RADIUS_KM * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


@dataclass(frozen=True)
class AcademicQuoteEstimate:
    quote: Quote
    academic_only: bool = field(default=True, init=False)
    coverage_validated: bool = field(default=False, init=False)
    limitations: Tuple[str, ...] = field(
        default=(
            "Distancia aproximada por círculo máximo; no representa una ruta por calles",
            "Modelo experimental entrenado con datos chinos y solo hora/día UTC",
            "Duración desde creación del pedido hasta entrega; no es tiempo de conducción",
            "Sin validación para El Salvador, distancias o diferencias entre vehículos",
            "Cobertura local y tarifas pendientes; no es una cotización comercial",
        ),
        init=False,
    )

    def __post_init__(self) -> None:
        if (
            not isinstance(self.quote, Quote)
            or self.quote.amounts is not None
            or self.quote.duration is None
            or self.quote.duration.source is not DurationSource.PREDICTION
        ):
            raise ValueError(
                "El borrador académico requiere predicción y no incluye importes"
            )
