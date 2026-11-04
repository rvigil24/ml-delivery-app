"""T29: escenarios sintéticos exclusivamente de tests, no tarifas/ROI observados."""

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal as D, localcontext

import pytest

from delivery.domain.finance import FinancialScenario, analyze_finances
from delivery.domain.models import QuoteAmounts
from delivery.domain.pricing import OperatorCosts, PricingPolicy, calculate_amounts


def scenario():
    policy = PricingPolicy("fixture-v1", "USD", D("0.01"), D(10), D(0), D(4), D(0))
    amounts = calculate_amounts(D(1), policy, OperatorCosts("USD", D(1), D(1)))
    return FinancialScenario("fixture-period", 10, amounts, D(12), D(100), policy.monetary_quantum)


def test_projection_reconciles_t22_components_fixed_costs_and_simple_period_roi():
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


def test_loss_and_non_positive_margin_are_visible_without_inventing_break_even():
    source = scenario()
    loss = analyze_finances(replace(source, volume=1))
    assert loss.operating_result == D(-8) and loss.roi_percent == D(-8)
    assert loss.break_even_deliveries == 3  # Threshold differs from supplied demand.
    for fee, margin in ((D(6), D(0)), (D(5), D(-1))):
        amounts = replace(source.unit_amounts, delivery_fee=fee, margin=margin)
        result = analyze_finances(replace(source, unit_amounts=amounts))
        assert result.break_even_deliveries is None
        assert result.operating_result < 0 and result.roi_percent < 0


def test_zero_volume_fixed_costs_and_investment_have_defined_distinct_meanings():
    source = scenario()
    empty = analyze_finances(replace(source, volume=0, investment=D(0)))
    assert empty.revenue == empty.contribution == 0
    assert empty.operating_result == -source.additional_fixed_costs and empty.roi_percent is None
    no_fixed = analyze_finances(replace(source, additional_fixed_costs=D(0)))
    assert no_fixed.break_even_deliveries == 0 and no_fixed.operating_result == D(40)
    negative = replace(source.unit_amounts, delivery_fee=D(5), margin=D(-1))
    no_fixed_loss = analyze_finances(replace(source, unit_amounts=negative, additional_fixed_costs=D(0)))
    assert no_fixed_loss.break_even_deliveries == 0 and no_fixed_loss.operating_result == D(-10)
    all_zero = analyze_finances(FinancialScenario("fixture-zero", 0,
        QuoteAmounts("USD", D(0), D(0), D(0), D(0), D(0)), D(0), D(0), D("0.01")))
    assert all_zero.operating_result == 0 and all_zero.break_even_deliveries == 0 and all_zero.roi_percent is None


def test_break_even_uses_exact_integer_ceiling_and_roi_is_only_an_approximate_ratio():
    source = scenario()
    fractional = replace(source, additional_fixed_costs=D("12.01"), investment=D(3))
    result = analyze_finances(fractional)
    assert result.break_even_deliveries == 4
    assert analyze_finances(replace(fractional, volume=3)).operating_result < 0
    assert analyze_finances(replace(fractional, volume=4)).operating_result >= 0
    assert result.roi_percent == D("933.00")
    repeating = analyze_finances(replace(source, volume=1, additional_fixed_costs=D(3), investment=D(3)))
    assert repeating.roi_percent == D("33.33333333333333333333333333")
    # A rounded 28-digit division would become exactly 1 and miss the second delivery.
    margin = D(10**28 - 2)
    edge = FinancialScenario("fixture-ceiling", 0,
        QuoteAmounts("USD", margin, D(0), D(0), D(0), margin), D(10**28 - 1), D(0), D(1))
    assert analyze_finances(edge).break_even_deliveries == 2


def test_invalid_or_unreconciled_inputs_and_lossy_aggregates_are_rejected():
    source = scenario()
    for changes in ({"period": " "}, {"volume": True}, {"volume": -1}, {"volume": 1.5},
                    {"additional_fixed_costs": 1.0}, {"additional_fixed_costs": D(-1)},
                    {"investment": D("NaN")}, {"monetary_quantum": D("0.05")},
                    {"investment": D("0.001")}, {"unit_amounts": replace(source.unit_amounts, margin=D(99))}):
        with pytest.raises(ValueError):
            replace(source, **changes)
    with pytest.raises(ValueError, match="FinancialScenario"):
        analyze_finances(None)
    huge_volume = replace(source, volume=10**28 + 1)
    with pytest.raises(ValueError, match="precisión"):
        analyze_finances(huge_volume)
