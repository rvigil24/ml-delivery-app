"""Proyección financiera con entradas de prueba."""

from dataclasses import FrozenInstanceError
from decimal import Decimal as D
from decimal import localcontext

import pytest
from delivery.domain.finance import FinancialScenario, analyze_finances
from delivery.domain.pricing import OperatorCosts, PricingPolicy, calculate_amounts


def scenario():
    policy = PricingPolicy("fixture-v1", "USD", D("0.01"), D(10), D(0), D(4), D(0))
    amounts = calculate_amounts(D(1), policy, OperatorCosts("USD", D(1), D(1)))
    return FinancialScenario(
        "fixture-period", 10, amounts, D(12), D(100), policy.monetary_quantum
    )


def test_financial_projection():
    source = scenario()
    with localcontext() as context:
        context.prec = 3
        result = analyze_finances(source)
    assert result.scenario is source
    assert result.revenue == D(100) and result.courier_payment == D(40)
    assert result.variable_cost == result.attributable_cost == D(10)
    assert result.contribution == D(40) and result.total_cost == D(72)
    assert result.operating_result == result.revenue - result.total_cost == D(28)
    assert result.break_even_deliveries == 3 and result.roi_percent == D(28)
    assert result.academic_only and not result.demand_validated
    with pytest.raises(FrozenInstanceError):
        result.operating_result = D(999)
