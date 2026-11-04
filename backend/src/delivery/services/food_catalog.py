"""Catálogo de comida de ejemplo y descubrimiento por distancia, sin precios ficticios."""

import json
from dataclasses import replace
from pathlib import Path

from delivery.models.catalogs import CatalogNotFound
from delivery.models.entities import Order
from delivery.models.estimation import haversine_km
from delivery.models.order_lifecycle import DuplicateOrder, OrderConflict


class FoodCatalogService:
    def __init__(self, businesses):
        self.businesses = businesses
        self.catalog = json.loads(
            (Path(__file__).parents[1] / "resources" / "food_menu.json").read_text()
        )

    def nearby(self, destination, limit):
        # Catálogo pequeño: recorrer todos evita ordenar sólo una página arbitraria.
        published = {product["business_id"] for product in self.catalog["products"]}
        ranked = sorted(
            (
                (haversine_km(destination, business.location), business)
                for business in self.businesses.all()
                if business.id in published
            ),
            key=lambda pair: (pair[0], pair[1].id),
        )
        return {
            "businesses": [
                {"business": business, "distance_km": distance}
                for distance, business in ranked[:limit]
            ],
            "distance_method": "straight_line",
            "coverage_validated": False,
        }

    def menu(self, business_id):
        business = self.businesses.get(business_id)
        if business is None:
            raise CatalogNotFound(business_id)
        return {
            "business": business,
            "products": [
                product
                for product in self.catalog["products"]
                if product["business_id"] == business_id
            ],
            "simulated": True,
            "catalog_version": self.catalog["version"],
            "prices_configured": False,
        }

    def register(
        self, orders, identifier, business_id, destination, address, items, notes
    ):
        """Validar contra el menú del servidor y registrar una sola solicitud por ID."""
        menu = self.menu(business_id)
        products = {product["id"]: product for product in menu["products"]}
        if not address.strip() or not items:
            raise ValueError("Faltan dirección o productos")
        seen, lines = set(), []
        for product_id, quantity in items:
            if (
                product_id in seen
                or product_id not in products
                or type(quantity) is not int
                or quantity <= 0
            ):
                raise ValueError("Producto o cantidad inválidos")
            seen.add(product_id)
            lines.append(f"{quantity} × {products[product_id]['name']}")
        lines.append(f"Dirección: {address.strip()}")
        if notes.strip():
            lines.append(f"Indicaciones: {notes.strip()}")
        order = Order(
            identifier,
            business_id,
            menu["business"].location,
            destination,
            "\n".join(lines),
        )
        try:
            return orders.register(order)
        except DuplicateOrder:
            existing = orders.get(identifier)
            if replace(existing.order, status=order.status) != order:
                raise OrderConflict(
                    "La referencia ya corresponde a otro pedido"
                ) from None
            return existing
