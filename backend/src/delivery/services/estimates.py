"""T21: preparar una estimación académica sin emitir cotización comercial."""

from dataclasses import replace
from typing import Optional

from delivery.ml.base import DurationPredictor
from delivery.models.entities import OrderStatus, Quote
from delivery.models.estimation import (
    DISTANCE_METHOD,
    AcademicQuoteEstimate,
    PredictionUnavailable,
    haversine_km,
)
from delivery.models.order_lifecycle import OrderConflict, OrderRecord
from delivery.repositories.base import OrderRepository


def estimate_from_record(
    record: OrderRecord, quote_id: str, predictor: Optional[DurationPredictor]
) -> AcademicQuoteEstimate:
    """Estimar sobre un snapshot ya leído; permite componer T31 sin releer pedidos."""
    if record.order.status is not OrderStatus.REQUESTED:
        raise OrderConflict("El borrador inicial requiere un pedido solicitado")
    quote = Quote(
        quote_id,
        record.order.id,
        haversine_km(record.order.origin, record.order.destination),
        DISTANCE_METHOD,
    )
    if predictor is None:
        raise PredictionUnavailable("No hay un predictor validado configurado")
    duration = predictor.predict(record.events[0].occurred_at)
    return AcademicQuoteEstimate(replace(quote, duration=duration))


class AcademicQuoteService:
    def __init__(
        self, orders: OrderRepository, predictor: Optional[DurationPredictor] = None
    ) -> None:
        self._orders = orders
        self._predictor = predictor

    def estimate(self, order_id: str, quote_id: str) -> AcademicQuoteEstimate:
        return estimate_from_record(
            self._orders.get(order_id), quote_id, self._predictor
        )
