import type { OrderRecord } from "./business-orders";

export type Courier = { id: string; vehicle: "bicicleta" | "motocicleta"; approved: boolean; available: boolean };
export type Stop = { order_id: string; kind: "recogida" | "entrega"; location: { latitude: number; longitude: number }; leg_distance_km: string };
export type CourierRoute = { id: string; courier_id: string; active: boolean; start: Stop["location"]; stops: Stop[];
  total_distance_km: string; orders: OrderRecord[]; created_at: string; released_at: string | null; simulated: true; road_route_validated: false };

export function stopCompleted(route: CourierRoute, stop: Stop) {
  const status = route.orders.find((record) => record.order.id === stop.order_id)?.order.status;
  return status === "entregado" || (stop.kind === "recogida" && status === "recogido");
}

export function nextCourierStop(route: CourierRoute) {
  if (!route.active) return null;
  const index = route.stops.findIndex((stop) => !stopCompleted(route, stop));
  if (index < 0) return null;
  const stop = route.stops[index];
  const status = route.orders.find((record) => record.order.id === stop.order_id)?.order.status;
  if (stop.kind === "recogida" && status === "asignado") return { index, stop, expected: "asignado", target: "recogido" } as const;
  if (stop.kind === "entrega" && status === "recogido") return { index, stop, expected: "recogido", target: "entregado" } as const;
  return null;
}

export function canFinishRoute(route: CourierRoute) {
  return route.active && route.stops.length > 0 && route.stops.every((stop) => route.orders.some((record) => record.order.id === stop.order_id && record.order.status === "entregado"));
}

export function validCourierAction(body: unknown): body is { courier_id: string; assignment_id: string; action: "progress" | "complete"; order_id?: string; expected?: string; target?: string } {
  if (!body || typeof body !== "object") return false;
  const value = body as Record<string, unknown>;
  if (typeof value.courier_id !== "string" || !value.courier_id.trim() || typeof value.assignment_id !== "string" || !value.assignment_id.trim()) return false;
  if (value.action === "complete") return true;
  return value.action === "progress" && typeof value.order_id === "string" && !!value.order_id.trim() &&
    ((value.expected === "asignado" && value.target === "recogido") || (value.expected === "recogido" && value.target === "entregado"));
}
