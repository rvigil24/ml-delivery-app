"""Distancia geométrica de referencia."""

import math

import pytest
from delivery.domain.estimation import EARTH_RADIUS_KM, haversine_km
from delivery.domain.models import Location


def test_distance_calculation():
    assert haversine_km(Location(0, 0), Location(0, 0)) == 0
    distance = haversine_km(Location(0, 0), Location(0, 1))
    assert distance == pytest.approx(111.195080, abs=1e-6)
    assert distance == haversine_km(Location(0, 1), Location(0, 0))
    assert haversine_km(Location(0, 179), Location(0, -179)) == pytest.approx(
        2 * distance
    )
    assert haversine_km(Location(0, 0), Location(0, 180)) == pytest.approx(
        math.pi * EARTH_RADIUS_KM
    )
