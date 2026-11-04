"""Catálogo de comida de ejemplo y descubrimiento por distancia, sin precios ficticios."""

import json
from pathlib import Path

from delivery.domain.catalogs import CatalogNotFound
from delivery.domain.estimation import haversine_km


class FoodCatalogService:
    def __init__(self, businesses):
        self.businesses = businesses
        self.catalog = json.loads((Path(__file__).parents[1] / "resources" / "food_menu.json").read_text())

    def nearby(self, destination, limit):
        # Catálogo pequeño: recorrer todos evita ordenar sólo una página arbitraria.
        published = {product["business_id"] for product in self.catalog["products"]}
        ranked = sorted(((haversine_km(destination, business.location), business)
                         for business in self.businesses.all() if business.id in published),
                        key=lambda pair: (pair[0], pair[1].id))
        return {"businesses": [{"business": business, "distance_km": distance}
                               for distance, business in ranked[:limit]],
                "distance_method": "straight_line", "coverage_validated": False}

    def menu(self, business_id):
        business = self.businesses.get(business_id)
        if business is None:
            raise CatalogNotFound(business_id)
        return {"business": business, "products": [product for product in self.catalog["products"]
                                                   if product["business_id"] == business_id],
                "simulated": True, "catalog_version": self.catalog["version"], "prices_configured": False}
