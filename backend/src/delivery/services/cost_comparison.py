"""T25: leer cada pedido una vez y comparar ambos escenarios con el mismo snapshot."""

from typing import Mapping, Optional, Sequence

from delivery.domain.cost_comparison import CostComparison, CostComparisonConfigurationMissing, compare_route_costs
from delivery.domain.models import Location
from delivery.domain.pricing import OperatorCosts, PricingPolicy
from delivery.domain.routing import RoutePolicy, validate_group
from delivery.ports.orders import OrderRepository


class CostComparisonService:
    def __init__(self, orders: OrderRepository, route_policy: Optional[RoutePolicy] = None,
                 pricing_policy: Optional[PricingPolicy] = None) -> None:
        self._orders = orders
        self._route_policy = route_policy
        self._pricing_policy = pricing_policy

    def compare(self, order_ids: Sequence[str], start: Location, individual_costs: Mapping[str, OperatorCosts],
                grouped_costs: OperatorCosts) -> CostComparison:
        if self._route_policy is None or self._pricing_policy is None:
            raise CostComparisonConfigurationMissing("Faltan políticas explícitas de ruta/precios")
        if isinstance(order_ids, (str, bytes)):
            raise ValueError("Se requiere una colección explícita de IDs")
        identifiers = tuple(order_ids)
        validate_group(identifiers, self._route_policy)
        snapshots = tuple(self._orders.get(identifier).order for identifier in identifiers)
        return compare_route_costs(snapshots, start, self._route_policy, self._pricing_policy,
                                   individual_costs, grouped_costs)
