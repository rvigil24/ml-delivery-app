"""Rutas de cotización y desglose de costos."""

from datetime import timezone

from fastapi import APIRouter, Request

from delivery.errors import error_response
from delivery.models.pricing import OperatorCosts
from delivery.schemas.requests import QuotePreviewRequest
from delivery.schemas.responses import (
    ErrorResponse,
    PredictResponse,
    QuoteAmountsResponse,
    QuotePreviewResponse,
    VehicleDecisionResponse,
)


def quotes_router():
    router = APIRouter()

    @router.post(
        "/orders/{order_id}/quotes",
        response_model=QuotePreviewResponse,
        tags=["Cotizaciones"],
        summary="Estimar el costo de un pedido",
        description="Muestra el costo estimado y los tipos de vehículo permitidos para el pedido.",
        responses={
            status: {"model": ErrorResponse} for status in (404, 409, 422, 503, 500)
        },
    )
    def quote_preview(order_id: str, payload: QuotePreviewRequest, request: Request):
        try:
            preview = request.app.state.quote_previews.preview(
                order_id,
                payload.quote_id,
                payload.load_kg,
                OperatorCosts(
                    payload.costs.currency,
                    payload.costs.variable_cost,
                    payload.costs.attributable_cost,
                ),
            )
        except ValueError:
            return error_response(
                422,
                "invalid_request",
                "Datos incompatibles con la política configurada.",
            )
        quote = preview.quote
        duration = quote.duration
        return QuotePreviewResponse(
            quote_id=quote.id,
            order_id=quote.order_id,
            distance_km=preview.pricing.distance_km,
            distance_method=quote.distance_method,
            duration=PredictResponse(
                requested_at_utc=preview.record.events[0].occurred_at.astimezone(
                    timezone.utc
                ),
                duration_minutes=duration.minutes,
                duration_source=duration.source.value,
                interval_definition=duration.interval_definition,
                model_version=duration.model_version,
            ),
            amounts=QuoteAmountsResponse(**vars(preview.pricing.amounts)),
            pricing_policy_version=preview.pricing.policy.version,
            vehicle_policy_version=preview.vehicles.policy.version,
            service_area_id=preview.vehicles.policy.area.id,
            load_kg=preview.vehicles.load_kg,
            within_configured_area=preview.vehicles.within_configured_area,
            eligible_vehicles=preview.vehicles.eligible_vehicles,
            vehicle_decisions=tuple(
                VehicleDecisionResponse(
                    vehicle=decision.vehicle, reasons=decision.reasons
                )
                for decision in preview.vehicles.decisions
            ),
            limitations=preview.pricing.estimate.limitations,
        )

    return router
