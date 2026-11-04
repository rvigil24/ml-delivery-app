"""T23: evaluar opciones sin asignar repartidor, cotizar ni mutar pedidos."""

from decimal import Decimal
from typing import Optional

from delivery.models.vehicle_rules import (
    VehicleConfigurationMissing,
    VehicleEvaluation,
    VehiclePolicy,
    evaluate_vehicle_rules,
)
from delivery.repositories.base import OrderRepository


class VehicleRulesService:
    def __init__(
        self, orders: OrderRepository, policy: Optional[VehiclePolicy] = None
    ) -> None:
        self._orders = orders
        self._policy = policy

    def evaluate(self, order_id: str, load_kg: Decimal) -> VehicleEvaluation:
        if self._policy is None:
            raise VehicleConfigurationMissing(
                "Falta una política completa de zona y límites por vehículo"
            )
        record = self._orders.get(order_id)
        return evaluate_vehicle_rules(record.order, load_kg, self._policy)
