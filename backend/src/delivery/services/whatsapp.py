"""T27: canal local de demostración; sin envío de mensajes o acceso a WhatsApp."""

from delivery.models.entities import Order
from delivery.models.messages import SimulatedConversation, conversation_from_record
from delivery.services.orders import OrderService


class WhatsAppSimulationService:
    def __init__(self, orders: OrderService) -> None:
        self._orders = orders

    def request(self, order: Order) -> SimulatedConversation:
        record = self._orders.register(order)
        return conversation_from_record(record)

    def conversation(self, order_id: str) -> SimulatedConversation:
        return conversation_from_record(self._orders.get(order_id))
