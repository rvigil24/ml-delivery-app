"""Ejecución completa y explícita de un envío simulado para la exposición."""

from dataclasses import replace

from delivery.models.assignments import prepare_assignment
from delivery.models.catalogs import CatalogConflict
from delivery.models.entities import DeliveryDuration, DurationSource
from delivery.models.entities import OrderStatus as S
from delivery.models.order_lifecycle import MissingPrerequisite, OrderEvent, OrderRecord
from delivery.services.assignments import AssignmentService, DispatchOrderRequirements
from delivery.services.cash import CashService
from delivery.services.estimates import estimate_from_record
from delivery.services.orders import OrderService, utc_now
from delivery.services.pricing import PricingService
from delivery.services.whatsapp import WhatsAppSimulationService


class SimulationQuoteSource:
    """Aceptación de una cotización para un único recorrido simulado.

    No se registra como validador de los endpoints generales de pedidos.
    La cotización y su configuración se devuelven en el recibo de la demo.
    """

    def __init__(self, quote):
        self.quote = quote

    def get_validated(self, order):
        if order.id != self.quote.order_id or self.quote.amounts is None:
            raise MissingPrerequisite("Cotización ajena a la simulación")
        return self.quote

    def validate(self, order, target):
        if target not in (S.QUOTED, S.CONFIRMED):
            raise MissingPrerequisite("Transición ajena a la cotización")
        self.get_validated(order)

    def validate_confirmed(self, order):
        if order.status is not S.CONFIRMED:
            raise MissingPrerequisite("Pedido sin confirmar")
        self.get_validated(order)


def run_demonstration(
    storage,
    delivery_estimator,
    *,
    business,
    courier,
    order,
    pricing,
    vehicle_policy,
    route_policy,
    costs,
    load_kg,
    promised_minutes,
):
    identifiers = (business.id, courier.id, order.id)
    if any(not identifier.startswith("demo-") for identifier in identifiers):
        raise ValueError("La demostración requiere IDs demo-")
    if (
        order.business_id != business.id
        or order.origin != business.location
        or order.status is not S.REQUESTED
    ):
        raise ValueError("Pedido de demostración incompatible con el negocio")
    if (
        storage.businesses.get(business.id) is not None
        or storage.couriers.get(courier.id) is not None
    ):
        raise CatalogConflict(
            "IDs demo ya utilizados; usar nuevos IDs, sin sobrescribir"
        )
    now = utc_now()
    prediction = delivery_estimator.predict(
        now, order.origin, order.destination, promised_minutes
    )

    class OrderPredictor:
        def predict(self, requested_at):
            if requested_at != now:
                raise ValueError("Fecha ajena a la estimación de este pedido")
            return DeliveryDuration(
                prediction["estimated_minutes"],
                DurationSource.PREDICTION,
                "creación–entrega",
                prediction["model_version"],
            )

    # Validar modelo, importes y viabilidad antes de crear datos operativos.
    snapshot = OrderRecord(order, (OrderEvent(None, S.REQUESTED, now),))
    estimate = estimate_from_record(snapshot, order.id + "-quote", OrderPredictor())
    breakdown = PricingService(pricing).calculate(estimate, costs)
    prepare_assignment(
        order.id + "-run",
        courier,
        (replace(order, status=S.CONFIRMED),),
        order.origin,
        route_policy,
        vehicle_policy,
        {order.id: load_kg},
        now,
    )
    quote = replace(estimate.quote, amounts=breakdown.amounts)
    quotes = SimulationQuoteSource(quote)
    storage.businesses.create(business)
    storage.couriers.create(courier)
    orders = OrderService(
        storage.orders,
        storage.businesses,
        DispatchOrderRequirements(storage.orders, quotes),
        lambda: now,
    )
    chat = WhatsAppSimulationService(orders)
    chat.request(order)
    orders.transition(order.id, S.REQUESTED, S.QUOTED)
    orders.transition(order.id, S.QUOTED, S.CONFIRMED)
    assignments = AssignmentService(
        storage.orders, route_policy, vehicle_policy, quotes, lambda: now
    )
    assignments.assign(
        order.id + "-run", courier.id, [order.id], order.origin, {order.id: load_kg}
    )
    cash = CashService(storage.cash, storage.orders, quotes, lambda: now)
    cash.open(order.id)
    orders.transition(order.id, S.ASSIGNED, S.PICKED_UP)
    orders.transition(order.id, S.PICKED_UP, S.DELIVERED)
    cash.collect(order.id, quote.amounts.currency, quote.amounts.delivery_fee)
    cash.remit(order.id, quote.amounts.currency, quote.amounts.delivery_fee)
    released = assignments.release(order.id + "-run")
    return {
        "simulated": True,
        "accepted_for_simulation": True,
        "commercial_quote_validated": False,
        "coverage_validated": False,
        "delivery_prediction": prediction,
        "quote": quote,
        "pricing": breakdown,
        "vehicle_policy": vehicle_policy,
        "load_kg": load_kg,
        "order": orders.get(order.id),
        "assignment": released,
        "cash": cash.get(order.id),
        "conversation": chat.conversation(order.id),
        "courier": storage.couriers.get(courier.id),
        "limitations": estimate.limitations
        + (
            "Políticas y ubicaciones de ejemplo; no acreditan tarifas o cobertura reales",
            "Los pasos se ejecutan consecutivamente; una interrupción puede dejar un recorrido incompleto",
            "El recibo conserva la cotización; la demo no implementa reanudación por pasos",
        ),
    }
