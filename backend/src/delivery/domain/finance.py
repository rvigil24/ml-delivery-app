"""T29: proyección académica homogénea, con fórmulas aprobadas y entradas explícitas."""

from dataclasses import dataclass, field
from decimal import Context, Decimal, DecimalException, Inexact, ROUND_HALF_UP, localcontext
from fractions import Fraction
from typing import Optional

from .models import QuoteAmounts


@dataclass(frozen=True)
class FinancialScenario:
    period: str
    volume: int
    unit_amounts: QuoteAmounts
    additional_fixed_costs: Decimal
    investment: Decimal
    monetary_quantum: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.period, str) or not self.period.strip():
            raise ValueError("period debe identificar explícitamente el período")
        if isinstance(self.volume, bool) or not isinstance(self.volume, int) or self.volume < 0:
            raise ValueError("volume debe ser un entero no negativo")
        if not isinstance(self.unit_amounts, QuoteAmounts):
            raise ValueError("Se requiere QuoteAmounts unitario")
        for name in ("additional_fixed_costs", "investment", "monetary_quantum"):
            value = getattr(self, name)
            if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
                raise ValueError(f"{name} debe ser Decimal finito no negativo")
        quantum = self.monetary_quantum
        digits = quantum.as_tuple().digits
        if quantum == 0 or digits[0] != 1 or any(digit != 0 for digit in digits[1:]):
            raise ValueError("monetary_quantum debe ser una potencia de diez positiva")
        quantum = Decimal((0, (1,), quantum.as_tuple().exponent + len(digits) - 1))
        object.__setattr__(self, "monetary_quantum", quantum)
        try:
            with localcontext(Context(prec=28, rounding=ROUND_HALF_UP)) as context:
                context.traps[Inexact] = True
                amounts = self.unit_amounts
                for value in (amounts.delivery_fee, amounts.courier_payment, amounts.variable_cost,
                              amounts.attributable_cost, amounts.margin, self.additional_fixed_costs, self.investment):
                    value.quantize(quantum)  # Rechazar entradas que necesitarían redondeo.
                if amounts.margin != (amounts.delivery_fee - amounts.courier_payment
                                      - amounts.variable_cost - amounts.attributable_cost):
                    raise ValueError("El margen unitario no concilia con los componentes")
        except DecimalException as error:
            raise ValueError("Importes incompatibles con la unidad o precisión monetaria") from error


@dataclass(frozen=True)
class FinancialReport:
    scenario: FinancialScenario
    revenue: Decimal
    courier_payment: Decimal
    variable_cost: Decimal
    attributable_cost: Decimal
    contribution: Decimal
    total_cost: Decimal
    operating_result: Decimal
    break_even_deliveries: Optional[int]
    roi_percent: Optional[Decimal]
    academic_only: bool = field(default=True, init=False)
    demand_validated: bool = field(default=False, init=False)


def analyze_finances(scenario: FinancialScenario) -> FinancialReport:
    if not isinstance(scenario, FinancialScenario):
        raise ValueError("Se requiere FinancialScenario con entradas explícitas")
    try:
        with localcontext(Context(prec=28, rounding=ROUND_HALF_UP)) as context:
            context.traps[Inexact] = True
            amounts = scenario.unit_amounts
            revenue = amounts.delivery_fee * scenario.volume
            payment = amounts.courier_payment * scenario.volume
            variable = amounts.variable_cost * scenario.volume
            attributable = amounts.attributable_cost * scenario.volume
            contribution = amounts.margin * scenario.volume
            total_cost = payment + variable + attributable + scenario.additional_fixed_costs
            result = contribution - scenario.additional_fixed_costs
            if scenario.additional_fixed_costs == 0:
                break_even = 0
            elif amounts.margin > 0:
                # Evitar que redondear una división oculte una entrega adicional.
                ratio = Fraction(scenario.additional_fixed_costs) / Fraction(amounts.margin)
                break_even = -(-ratio.numerator // ratio.denominator)
            else:
                break_even = None
            roi = None
            if scenario.investment > 0:
                ratio = Fraction(result) * 100 / Fraction(scenario.investment)
                context.traps[Inexact] = False
                roi = Decimal(ratio.numerator) / Decimal(ratio.denominator)
            return FinancialReport(scenario, revenue, payment, variable, attributable,
                                   contribution, total_cost, result, break_even, roi)
    except DecimalException as error:
        raise ValueError("La proyección excede la precisión decimal soportada") from error
