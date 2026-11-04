"""Importes inventados únicamente como fixtures; no son tarifas o costos aprobados."""

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext

import pytest

from delivery.domain import DeliveryDuration, DurationSource, Quote
from delivery.domain.estimation import AcademicQuoteEstimate
from delivery.domain.pricing import OperatorCosts, PricingConfigurationMissing, PricingPolicy, calculate_amounts
from delivery.services.pricing import PricingService


D = Decimal


def fixture_policy():
    return PricingPolicy("fixture-v1", "USD", D("0.01"), D("1.005"), D("2"), D("0.505"), D("0.5"))


def test_formula_rounds_components_half_up_and_margin_reconciles_to_the_breakdown():
    policy = fixture_policy()
    costs = OperatorCosts("USD", D("0.105"), D("0.205"))
    with localcontext() as context:
        context.prec = 3  # El cálculo no debe heredar una precisión accidental del llamador.
        amounts = calculate_amounts(D("1"), policy, costs)
    assert amounts.delivery_fee == D("3.01")
    assert amounts.courier_payment == D("1.01")
    assert amounts.variable_cost == D("0.11") and amounts.attributable_cost == D("0.21")
    assert amounts.margin == D("1.68")
    assert amounts.margin == amounts.delivery_fee - amounts.courier_payment - amounts.variable_cost - amounts.attributable_cost


def test_explicit_zero_inputs_are_valid_and_negative_margin_is_not_hidden():
    policy = replace(fixture_policy(), customer_base=D("0"), customer_per_km=D("0"),
                     courier_base=D("1"), courier_per_km=D("0"))
    result = calculate_amounts(D("0"), policy, OperatorCosts("USD", D("0"), D("0")))
    assert result.delivery_fee == D("0.00")
    assert result.courier_payment == D("1.00") and result.margin == D("-1.00")


def test_invalid_configuration_currency_distance_and_precision_fail_explicitly():
    policy = fixture_policy()
    with pytest.raises(ValueError, match="Decimal"):
        replace(policy, customer_base=1.1)
    with pytest.raises(ValueError, match="Decimal"):
        OperatorCosts("USD", D("NaN"), D("0"))
    with pytest.raises(ValueError, match="Decimal"):
        replace(policy, courier_per_km=D("-1"))
    with pytest.raises(ValueError, match="potencia de diez"):
        replace(policy, monetary_quantum=D("0.05"))
    with pytest.raises(ValueError, match="currency"):
        replace(policy, currency="usd")
    with pytest.raises(ValueError, match="misma moneda"):
        calculate_amounts(D("1"), policy, OperatorCosts("EUR", D("0"), D("0")))
    with pytest.raises(ValueError, match="distance_km"):
        calculate_amounts(D("Infinity"), policy, OperatorCosts("USD", D("0"), D("0")))
    with pytest.raises(ValueError, match="precisión decimal"):
        calculate_amounts(D("123456789012345678901234567890"), policy, OperatorCosts("USD", D("0"), D("0")))


def test_monetary_quantum_is_explicit_and_normalized_without_changing_its_value():
    policy = replace(fixture_policy(), monetary_quantum=D("0.0100"))
    assert policy.monetary_quantum.as_tuple().exponent == -2
    hundreds = replace(policy, monetary_quantum=D("100"), customer_base=D("150"),
                       customer_per_km=D("0"), courier_base=D("0"), courier_per_km=D("0"))
    amounts = calculate_amounts(D("0"), hundreds, OperatorCosts("USD", D("0"), D("0")))
    assert hundreds.monetary_quantum.as_tuple().exponent == 2
    assert amounts.delivery_fee == D("200")


def test_academic_pricing_keeps_the_original_estimate_immutable_and_requires_all_configuration():
    estimate = AcademicQuoteEstimate(Quote("fixture-quote", "fixture-order", 1.1, "fixture-distance",
        DeliveryDuration(10, DurationSource.PREDICTION, "Intervalo de fixture", "fixture-model")))
    costs = OperatorCosts("USD", D("0"), D("0"))
    with pytest.raises(PricingConfigurationMissing):
        PricingService().calculate(estimate, costs)
    service = PricingService(fixture_policy())
    with pytest.raises(PricingConfigurationMissing):
        service.calculate(estimate)
    result = service.calculate(estimate, costs)
    assert result.distance_km == D("1.1") and result.estimate is estimate
    assert result.policy.version == "fixture-v1" and result.costs is costs
    assert result.academic_only and not result.coverage_validated
    assert estimate.quote.amounts is None
    with pytest.raises(FrozenInstanceError):
        result.amounts.margin = D("999")
