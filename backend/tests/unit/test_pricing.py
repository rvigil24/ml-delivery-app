"""Tarifa, costos y redondeo monetario."""

from decimal import Decimal, localcontext

from delivery.domain.pricing import OperatorCosts, PricingPolicy, calculate_amounts

D = Decimal


def fixture_policy():
    return PricingPolicy(
        "fixture-v1", "USD", D("0.01"), D("1.005"), D("2"), D("0.505"), D("0.5")
    )


def test_price_breakdown_rounding():
    policy = fixture_policy()
    costs = OperatorCosts("USD", D("0.105"), D("0.205"))
    with localcontext() as context:
        context.prec = (
            3  # El cálculo no debe heredar una precisión accidental del llamador.
        )
        amounts = calculate_amounts(D("1"), policy, costs)
    assert amounts.delivery_fee == D("3.01")
    assert amounts.courier_payment == D("1.01")
    assert amounts.variable_cost == D("0.11") and amounts.attributable_cost == D("0.21")
    assert amounts.margin == D("1.68")
    assert (
        amounts.margin
        == amounts.delivery_fee
        - amounts.courier_payment
        - amounts.variable_cost
        - amounts.attributable_cost
    )
