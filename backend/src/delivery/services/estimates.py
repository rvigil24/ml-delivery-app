"""T21: preparar una estimación académica sin emitir cotización comercial."""

from dataclasses import replace
from typing import Optional

from delivery.domain.estimation import AcademicQuoteEstimate, DISTANCE_METHOD, PredictionUnavailable, haversine_km
from delivery.domain.models import OrderStatus, Quote
from delivery.domain.order_lifecycle import OrderConflict
from delivery.ports.estimation import DurationPredictor
from delivery.ports.orders import OrderRepository


class AcademicQuoteService:
    def __init__(self, orders: OrderRepository, predictor: Optional[DurationPredictor] = None) -> None:
        self._orders = orders
        self._predictor = predictor

    def estimate(self, order_id: str, quote_id: str) -> AcademicQuoteEstimate:
        record = self._orders.get(order_id)
        if record.order.status is not OrderStatus.REQUESTED:
            raise OrderConflict("El borrador inicial requiere un pedido solicitado")
        quote = Quote(quote_id, record.order.id, haversine_km(record.order.origin, record.order.destination),
                      DISTANCE_METHOD)
        if self._predictor is None:
            raise PredictionUnavailable("No hay un predictor validado configurado")
        # El target T13 empieza en creación: no usar la hora de una consulta posterior.
        duration = self._predictor.predict(record.events[0].occurred_at)
        return AcademicQuoteEstimate(replace(quote, duration=duration))
