"""Consulta y avance de rutas existentes, sin crear asignaciones ni saltar validaciones."""

from delivery.domain.assignments import AssignmentConflict
from delivery.domain.models import OrderStatus
from .assignments import AssignmentService


class CourierRouteService:
    def __init__(self, repository, orders):
        self.repository, self.orders = repository, orders

    def _owned(self, courier_id, assignment_id):
        self.repository.get_courier(courier_id)
        assignment = self.repository.get_assignment(assignment_id)
        if assignment.courier.id != courier_id:
            raise AssignmentConflict("La ruta no pertenece a este repartidor")
        return assignment

    def _view(self, assignment):
        return {"id": assignment.id, "courier_id": assignment.courier.id,
                "active": assignment.active, "start": assignment.route.start,
                "stops": assignment.route.stops, "total_distance_km": assignment.route.total_distance_km,
                "created_at": assignment.created_at, "released_at": assignment.released_at,
                "orders": tuple(self.repository.get(order.id) for order in assignment.route.orders),
                "simulated": True, "road_route_validated": False}

    def list(self, courier_id, limit):
        self.repository.get_courier(courier_id)
        return tuple(self._view(assignment) for assignment in self.repository.list_assignments(courier_id, limit))

    def progress(self, courier_id, assignment_id, order_id, expected, target):
        assignment = self._owned(courier_id, assignment_id)
        if (not assignment.active or order_id not in {order.id for order in assignment.route.orders}
                or (expected, target) not in ((OrderStatus.ASSIGNED, OrderStatus.PICKED_UP),
                                              (OrderStatus.PICKED_UP, OrderStatus.DELIVERED))):
            raise AssignmentConflict("Avance incompatible con la ruta")
        self.orders.transition(order_id, expected, target)
        return self._view(self._owned(courier_id, assignment_id))

    def complete(self, courier_id, assignment_id):
        self._owned(courier_id, assignment_id)
        return self._view(AssignmentService(self.repository).release(assignment_id))
