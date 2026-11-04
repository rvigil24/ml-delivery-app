export type OrderStatus = "solicitado" | "cotizado" | "confirmado" | "asignado" | "recogido" | "entregado" | "cancelado";
export type BusinessTarget = "confirmado" | "cancelado";
export type OrderRecord = {
  order: { id: string; business_id: string; details: string; status: OrderStatus;
    origin: { latitude: number; longitude: number }; destination: { latitude: number; longitude: number } };
  events: { previous_status: OrderStatus | null; status: OrderStatus; occurred_at: string }[];
};

export const statusLabels: Record<OrderStatus, string> = {
  solicitado: "Solicitado", cotizado: "Cotizado", confirmado: "Confirmado", asignado: "Asignado",
  recogido: "Recogido", entregado: "Entregado", cancelado: "Cancelado",
};

export function businessActions(status: OrderStatus): BusinessTarget[] {
  if (status === "cotizado") return ["confirmado", "cancelado"];
  if (status === "solicitado" || status === "confirmado") return ["cancelado"];
  return [];
}

export function validBusinessAction(body: unknown): body is { order_id: string; business_id: string; expected: OrderStatus; target: BusinessTarget } {
  if (!body || typeof body !== "object") return false;
  const value = body as Record<string, unknown>;
  if (typeof value.order_id !== "string" || !value.order_id.trim() || typeof value.business_id !== "string" || !value.business_id.trim()) return false;
  if (typeof value.expected !== "string" || !Object.hasOwn(statusLabels, value.expected)) return false;
  return businessActions(value.expected as OrderStatus).includes(value.target as BusinessTarget);
}
