"""T25: comparación académica de costos, sin ingresos ni ahorro supuesto."""

from dataclasses import dataclass, field
from decimal import Context, Decimal, DecimalException, Inexact, localcontext
from typing import Mapping, Tuple

from delivery.models.entities import Location, Order
from delivery.models.pricing import OperatorCosts, PricingPolicy
from delivery.models.routing import RoutePlan, RoutePolicy, suggest_route


class CostComparisonConfigurationMissing(RuntimeError):
    pass


@dataclass(frozen=True)
class CostTotals:
    currency: str
    courier_payment: Decimal
    variable_cost: Decimal
    attributable_cost: Decimal
    total_cost: Decimal


@dataclass(frozen=True)
class CostedRoute:
    route: RoutePlan
    supplied_costs: OperatorCosts
    amounts: CostTotals


@dataclass(frozen=True)
class CostComparison:
    pricing_policy: PricingPolicy
    individual: Tuple[CostedRoute, ...]
    individual_totals: CostTotals
    individual_distance_km: Decimal
    grouped: CostedRoute
    individual_minus_group_cost: Decimal
    individual_minus_group_km: Decimal
    academic_only: bool = field(default=True, init=False)
    capacity_validated: bool = field(default=False, init=False)
    road_route_validated: bool = field(default=False, init=False)
    assumptions: Tuple[str, ...] = field(
        default=(
            "Mismos pedidos/snapshots, punto inicial, moneda y política para ambos escenarios",
            "Recorridos individuales independientes desde el mismo inicio; el grupo es un solo recorrido",
            "Una base de pago por recorrido; costos individuales y agrupados suministrados explícitamente",
            "Rutas abiertas, sin retorno ni reposicionamiento final; los puntos finales pueden diferir",
            "Solo costos del operador, sin tarifas al cliente, ingresos, ROI o ahorro garantizado",
            "Distancia geográfica aproximada; sin validación de capacidad, tiempos o viabilidad vial",
        ),
        init=False,
    )


def _route_cost(
    route: RoutePlan, policy: PricingPolicy, costs: OperatorCosts
) -> CostedRoute:
    if not isinstance(costs, OperatorCosts) or costs.currency != policy.currency:
        raise ValueError(
            "Cada recorrido requiere OperatorCosts explícitos en la moneda de la política"
        )
    try:
        with localcontext(Context(prec=28, rounding=policy.rounding)) as context:
            context.traps[Inexact] = True
            payment = (
                policy.courier_base + policy.courier_per_km * route.total_distance_km
            )
            context.traps[Inexact] = False
            payment = payment.quantize(policy.monetary_quantum)
            variable = costs.variable_cost.quantize(policy.monetary_quantum)
            attributable = costs.attributable_cost.quantize(policy.monetary_quantum)
            context.traps[Inexact] = True
            total = payment + variable + attributable
            return CostedRoute(
                route,
                costs,
                CostTotals(policy.currency, payment, variable, attributable, total),
            )
    except DecimalException as error:
        raise ValueError("El costo excede la precisión decimal soportada") from error


def compare_route_costs(
    orders: Tuple[Order, ...],
    start: Location,
    route_policy: RoutePolicy,
    pricing_policy: PricingPolicy,
    individual_costs: Mapping[str, OperatorCosts],
    grouped_costs: OperatorCosts,
) -> CostComparison:
    if not isinstance(pricing_policy, PricingPolicy):
        raise ValueError("Se requiere PricingPolicy explícita")
    grouped_plan = suggest_route(orders, start, route_policy)
    identifiers = {order.id for order in grouped_plan.orders}
    if (
        not isinstance(individual_costs, Mapping)
        or set(individual_costs) != identifiers
    ):
        raise ValueError(
            "Los costos individuales deben corresponder exactamente al grupo de pedidos"
        )
    individual = tuple(
        _route_cost(
            suggest_route((order,), start, route_policy),
            pricing_policy,
            individual_costs[order.id],
        )
        for order in grouped_plan.orders
    )
    grouped = _route_cost(grouped_plan, pricing_policy, grouped_costs)
    try:
        with localcontext(
            Context(prec=28, rounding=pricing_policy.rounding)
        ) as context:
            context.traps[Inexact] = True
            payment = sum(
                (item.amounts.courier_payment for item in individual), Decimal(0)
            )
            variable = sum(
                (item.amounts.variable_cost for item in individual), Decimal(0)
            )
            attributable = sum(
                (item.amounts.attributable_cost for item in individual), Decimal(0)
            )
            total = payment + variable + attributable
            distance = sum(
                (item.route.total_distance_km for item in individual), Decimal(0)
            )
            totals = CostTotals(
                pricing_policy.currency, payment, variable, attributable, total
            )
            return CostComparison(
                pricing_policy,
                individual,
                totals,
                distance,
                grouped,
                total - grouped.amounts.total_cost,
                distance - grouped.route.total_distance_km,
            )
    except DecimalException as error:
        raise ValueError("El agregado excede la precisión decimal soportada") from error
