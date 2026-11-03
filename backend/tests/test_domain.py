"""Fixtures sintéticas de pruebas; no son tarifas ni observaciones para ML."""

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from delivery.domain import (
    Business, Courier, DeliveryDuration, DurationSource, Location,
    Order, OrderStatus, Quote, QuoteAmounts, VehicleType,
)


@pytest.fixture
def location() -> Location:
    return Location(latitude=0, longitude=0)


@pytest.fixture
def amounts() -> QuoteAmounts:
    # Importes arbitrarios para probar validaciones, sin fórmula comercial.
    return QuoteAmounts(
        currency="USD",
        delivery_fee=Decimal("1.01"),
        courier_payment=Decimal("1.02"),
        variable_cost=Decimal("0.01"),
        attributable_cost=Decimal("0.02"),
        margin=Decimal("-0.04"),
    )


def test_business_requires_name_and_preserves_location(location: Location) -> None:
    business = Business("business-test", "Negocio de prueba", location)
    assert business.location is location
    with pytest.raises(ValueError, match="name"):
        replace(business, name=" ")


def test_coordinate_boundaries() -> None:
    assert Location(-90, -180).latitude == -90
    assert Location(90, 180).longitude == 180
    with pytest.raises(ValueError, match="latitude"):
        Location(91, 0)
    with pytest.raises(ValueError, match="longitude"):
        Location(0, 181)


def test_coordinates_reject_nonfinite_and_boolean_values() -> None:
    with pytest.raises(ValueError):
        Location(float("nan"), 0)
    with pytest.raises(ValueError):
        Location(0, True)


def test_order_initial_state_and_immutability(location: Location) -> None:
    order = Order("order-test", "business-test", location, location, "Prueba")
    assert order.status is OrderStatus.REQUESTED
    with pytest.raises(FrozenInstanceError):
        order.status = OrderStatus.DELIVERED


def test_order_requires_business_and_typed_state(location: Location) -> None:
    order = Order("order-test", "business-test", location, location, "Prueba")
    with pytest.raises(ValueError, match="business_id"):
        replace(order, business_id="")
    with pytest.raises(ValueError, match="status"):
        replace(order, status="entregado")


def test_courier_vehicle_and_explicit_flags() -> None:
    courier = Courier("courier-test", VehicleType.BICYCLE, False, True)
    assert not courier.approved and courier.available
    assert replace(courier, vehicle=VehicleType.MOTORCYCLE).vehicle is VehicleType.MOTORCYCLE
    with pytest.raises(ValueError, match="vehicle"):
        replace(courier, vehicle="carro")
    with pytest.raises(ValueError, match="booleanos"):
        replace(courier, approved=1)


def test_duration_preserves_explicit_provenance() -> None:
    illustrative = DeliveryDuration(1, DurationSource.ILLUSTRATIVE, "Intervalo de prueba")
    assert illustrative.model_version is None
    # Versión ficticia de fixture; no se afirma que exista un modelo entrenado.
    prediction = DeliveryDuration(1, DurationSource.PREDICTION, "Prueba", "fixture-model")
    assert prediction.model_version == "fixture-model"


def test_duration_cannot_misrepresent_its_source() -> None:
    with pytest.raises(ValueError, match="model_version"):
        DeliveryDuration(1, DurationSource.PREDICTION, "Prueba")
    with pytest.raises(ValueError, match="ilustrativa"):
        DeliveryDuration(1, DurationSource.ILLUSTRATIVE, "Prueba", "fixture-model")


def test_duration_requires_valid_minutes_and_interval() -> None:
    with pytest.raises(ValueError, match="minutes"):
        DeliveryDuration(-1, DurationSource.ILLUSTRATIVE, "Prueba")
    with pytest.raises(ValueError, match="interval_definition"):
        DeliveryDuration(1, DurationSource.ILLUSTRATIVE, "")


def test_amounts_preserve_precision_and_allow_negative_margin(amounts: QuoteAmounts) -> None:
    assert amounts.delivery_fee == Decimal("1.01")
    assert amounts.margin == Decimal("-0.04")


def test_amounts_require_finite_decimals(amounts: QuoteAmounts) -> None:
    with pytest.raises(ValueError, match="delivery_fee"):
        replace(amounts, delivery_fee=1.01)
    with pytest.raises(ValueError, match="margin"):
        replace(amounts, margin=Decimal("Infinity"))


def test_amounts_require_currency_and_nonnegative_costs(amounts: QuoteAmounts) -> None:
    with pytest.raises(ValueError, match="currency"):
        replace(amounts, currency="usd")
    with pytest.raises(ValueError, match="variable_cost"):
        replace(amounts, variable_cost=Decimal("-0.01"))


def test_quote_preserves_supplied_values_and_explicit_absence(amounts: QuoteAmounts) -> None:
    quote = Quote("quote-test", "order-test", 0, "Método de prueba")
    assert quote.duration is None and quote.amounts is None
    duration = DeliveryDuration(1, DurationSource.ILLUSTRATIVE, "Prueba")
    complete = replace(quote, duration=duration, amounts=amounts)
    assert complete.duration is duration
    assert complete.amounts is amounts


def test_quote_rejects_invalid_distance_and_nested_types() -> None:
    quote = Quote("quote-test", "order-test", 1, "Método de prueba")
    with pytest.raises(ValueError, match="distance_km"):
        replace(quote, distance_km=-1)
    with pytest.raises(ValueError, match="duration"):
        replace(quote, duration=1)
