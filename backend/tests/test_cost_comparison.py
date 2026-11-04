"""Costos, políticas y coordenadas ficticios de tests; no evidencian ahorro real."""

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal, localcontext

import pytest

from delivery.adapters.memory import InMemoryBusinesses, InMemoryOrderRepository
from delivery.domain import Business, Location, Order
from delivery.domain.cost_comparison import CostComparisonConfigurationMissing, compare_route_costs
from delivery.domain.pricing import OperatorCosts, PricingPolicy
from delivery.domain.routing import RoutePolicy
from delivery.domain.vehicle_rules import ServiceArea
from delivery.services.cost_comparison import CostComparisonService
from delivery.services.orders import OrderService


D = Decimal
START = Location(0, 0)
A = Order("fixture-a", "fixture-business", START, Location(0, 0.01), "Prueba A")
B = Order("fixture-b", "fixture-business", START, Location(0, 0.02), "Prueba B")
ROUTE = RoutePolicy("fixture-route-v1", 2, ServiceArea("fixture-area", Location(-1, -1), Location(1, 1)))
PRICE = PricingPolicy("fixture-price-v1", "USD", D("0.01"), D("999"), D("999"), D("1"), D("0"))
COSTS = OperatorCosts("USD", D("0.10"), D("0.20"))


def test_same_snapshots_open_routes_and_one_base_per_route_reconcile_totals_and_signed_difference():
    costs = {A.id: COSTS, B.id: COSTS}
    result = compare_route_costs((B, A), START, ROUTE, PRICE, costs, COSTS)
    assert result.individual_totals.courier_payment == D("2.00")
    assert result.individual_totals.total_cost == D("2.60")
    assert result.grouped.amounts.total_cost == D("1.30")
    assert result.individual_minus_group_cost == D("1.30")
    assert result.individual_minus_group_km == result.individual_distance_km - result.grouped.route.total_distance_km
    for individual, grouped_order in zip(result.individual, result.grouped.route.orders):
        assert individual.route.orders[0] is grouped_order
        assert individual.route.start == result.grouped.route.start == START
        assert len(individual.route.stops) == 2
    assert result.academic_only and not result.capacity_validated and not result.road_route_validated


def test_grouping_can_cost_more_and_single_order_equal_costs_have_zero_difference():
    expensive = OperatorCosts("USD", D("10"), D("0.20"))
    result = compare_route_costs((A, B), START, ROUTE, PRICE, {A.id: COSTS, B.id: COSTS}, expensive)
    assert result.individual_minus_group_cost < 0
    single = compare_route_costs((A,), START, ROUTE, PRICE, {A.id: COSTS}, COSTS)
    assert single.individual_minus_group_cost == 0
    assert single.individual_minus_group_km == 0


def test_explicit_costs_must_match_all_orders_and_currency_without_default_filling():
    with pytest.raises(ValueError, match="exactamente"):
        compare_route_costs((A, B), START, ROUTE, PRICE, {A.id: COSTS}, COSTS)
    with pytest.raises(ValueError, match="exactamente"):
        compare_route_costs((A,), START, ROUTE, PRICE, {A.id: COSTS, B.id: COSTS}, COSTS)
    with pytest.raises(ValueError, match="OperatorCosts"):
        compare_route_costs((A,), START, ROUTE, PRICE, {A.id: COSTS}, None)
    with pytest.raises(ValueError, match="moneda"):
        compare_route_costs((A,), START, ROUTE, PRICE, {A.id: COSTS}, OperatorCosts("EUR", D("0"), D("0")))
    with pytest.raises(CostComparisonConfigurationMissing):
        CostComparisonService(InMemoryOrderRepository()).compare([A.id], START, {A.id: COSTS}, COSTS)


def test_payment_uses_route_kilometers_and_half_up_but_customer_rates_do_not_affect_costs():
    price = replace(PRICE, courier_base=D("1.005"), courier_per_km=D("0.1"))
    with localcontext() as context:
        context.prec = 3
        result = compare_route_costs((A, B), START, ROUTE, price, {A.id: COSTS, B.id: COSTS}, COSTS)
    expected = (price.courier_base + price.courier_per_km * result.grouped.route.total_distance_km).quantize(D("0.01"), rounding=price.rounding)
    assert result.grouped.amounts.courier_payment == expected
    changed = compare_route_costs((A, B), START, ROUTE, replace(price, customer_base=D("0"), customer_per_km=D("0")),
                                  {A.id: COSTS, B.id: COSTS}, COSTS)
    assert changed.individual_totals == result.individual_totals
    assert changed.grouped.amounts == result.grouped.amounts


def test_service_reads_once_per_order_and_does_not_mutate_status_or_history():
    class CountingRepository(InMemoryOrderRepository):
        def __init__(self):
            super().__init__()
            self.reads = []

        def get(self, order_id):
            self.reads.append(order_id)
            return super().get(order_id)

    repository = CountingRepository()
    business = Business(A.business_id, "Negocio de prueba", START)
    orders = OrderService(repository, InMemoryBusinesses([business]),
        clock=lambda: datetime(2022, 1, 1, tzinfo=timezone.utc))
    initial = {order.id: orders.register(order) for order in (A, B)}
    result = CostComparisonService(repository, ROUTE, PRICE).compare([B.id, A.id], START, {A.id: COSTS, B.id: COSTS}, COSTS)
    assert repository.reads == [B.id, A.id]
    assert result.pricing_policy is PRICE and result.grouped.supplied_costs is COSTS
    for order_id, record in initial.items():
        assert repository.get(order_id) is record and len(record.events) == 1
