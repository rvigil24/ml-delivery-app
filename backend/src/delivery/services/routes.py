"""T24: leer snapshots y sugerir paradas, sin reservar o modificar pedidos."""

from typing import Optional, Sequence

from delivery.domain.models import Location
from delivery.domain.routing import RouteConfigurationMissing, RoutePlan, RoutePolicy, suggest_route, validate_group
from delivery.ports.orders import OrderRepository


class RouteSuggestionService:
    def __init__(self, orders: OrderRepository, policy: Optional[RoutePolicy] = None) -> None:
        self._orders = orders
        self._policy = policy

    def suggest(self, order_ids: Sequence[str], start: Location) -> RoutePlan:
        if self._policy is None:
            raise RouteConfigurationMissing("Falta la política de zona y máximo de pedidos")
        if isinstance(order_ids, (str, bytes)):
            raise ValueError("Se requiere una colección explícita de IDs")
        identifiers = tuple(order_ids)
        validate_group(identifiers, self._policy)
        snapshots = tuple(self._orders.get(identifier).order for identifier in identifiers)
        return suggest_route(snapshots, start, self._policy)
