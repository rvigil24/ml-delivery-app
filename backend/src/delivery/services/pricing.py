"""T22: desglose académico que conserva entradas y no emite una cotización."""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from delivery.domain.estimation import AcademicQuoteEstimate
from delivery.domain.models import QuoteAmounts
from delivery.domain.pricing import OperatorCosts, PricingConfigurationMissing, PricingPolicy, calculate_amounts


@dataclass(frozen=True)
class AcademicPriceBreakdown:
    estimate: AcademicQuoteEstimate
    policy: PricingPolicy
    costs: OperatorCosts
    distance_km: Decimal
    amounts: QuoteAmounts
    academic_only: bool = field(default=True, init=False)
    coverage_validated: bool = field(default=False, init=False)


class PricingService:
    def __init__(self, policy: Optional[PricingPolicy] = None) -> None:
        self._policy = policy

    def calculate(self, estimate: AcademicQuoteEstimate, costs: Optional[OperatorCosts] = None) -> AcademicPriceBreakdown:
        if self._policy is None or costs is None:
            raise PricingConfigurationMissing("Faltan política o costos explícitos; no se sustituyen por cero")
        if not isinstance(estimate, AcademicQuoteEstimate):
            raise ValueError("Se requiere un borrador académico T21")
        # Captura la representación decimal del resultado geométrico, no su expansión binaria.
        distance = Decimal(str(estimate.quote.distance_km))
        amounts = calculate_amounts(distance, self._policy, costs)
        return AcademicPriceBreakdown(estimate, self._policy, costs, distance, amounts)
