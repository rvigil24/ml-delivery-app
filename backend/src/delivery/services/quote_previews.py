"""T31: integrar modelo, importes y vehículos sin emitir una cotización comercial."""

from dataclasses import dataclass, field, replace
from decimal import Decimal
from typing import Optional

from delivery.ml.base import DurationPredictor
from delivery.models.entities import Quote
from delivery.models.order_lifecycle import OrderRecord
from delivery.models.pricing import OperatorCosts, PricingPolicy
from delivery.models.vehicle_rules import (
    VehicleEvaluation,
    VehiclePolicy,
    evaluate_vehicle_rules,
)
from delivery.repositories.base import OrderRepository
from delivery.services.estimates import estimate_from_record
from delivery.services.pricing import AcademicPriceBreakdown, PricingService


class QuoteConfigurationMissing(RuntimeError):
    pass


@dataclass(frozen=True)
class AcademicQuotePreview:
    record: OrderRecord
    pricing: AcademicPriceBreakdown
    vehicles: VehicleEvaluation
    academic_only: bool = field(default=True, init=False)
    coverage_validated: bool = field(default=False, init=False)
    commercial_quote_validated: bool = field(default=False, init=False)

    @property
    def quote(self) -> Quote:
        return replace(self.pricing.estimate.quote, amounts=self.pricing.amounts)


class QuotePreviewService:
    def __init__(
        self,
        orders: Optional[OrderRepository],
        predictor: Optional[DurationPredictor],
        pricing_policy: Optional[PricingPolicy],
        vehicle_policy: Optional[VehiclePolicy],
    ) -> None:
        self._orders = orders
        self._predictor = predictor
        self._pricing_policy = pricing_policy
        self._vehicle_policy = vehicle_policy

    def preview(
        self, order_id: str, quote_id: str, load_kg: Decimal, costs: OperatorCosts
    ) -> AcademicQuotePreview:
        if (
            self._orders is None
            or self._pricing_policy is None
            or self._vehicle_policy is None
        ):
            raise QuoteConfigurationMissing(
                "Falta repositorio o políticas explícitas de precios/vehículos"
            )
        if (
            not isinstance(costs, OperatorCosts)
            or costs.currency != self._pricing_policy.currency
        ):
            raise ValueError(
                "Se requieren costos explícitos en la moneda de la política"
            )
        record = self._orders.get(order_id)
        vehicles = evaluate_vehicle_rules(record.order, load_kg, self._vehicle_policy)
        estimate = estimate_from_record(record, quote_id, self._predictor)
        pricing = PricingService(self._pricing_policy).calculate(estimate, costs)
        return AcademicQuotePreview(record, pricing, vehicles)
