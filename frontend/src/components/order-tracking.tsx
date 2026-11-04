"use client";

import { useCallback, useState } from "react";
import { statusLabels, type OrderStatus } from "@/lib/business-orders";
import { useLiveRefresh } from "@/lib/use-live-refresh";

export function OrderTracking({ id, initialStatus }: { id: string; initialStatus: OrderStatus }) {
  const [status, setStatus] = useState(initialStatus);
  const [error, setError] = useState("");
  const refresh = useCallback(async (signal: AbortSignal) => {
    try {
      const response = await fetch(`/api/food?${new URLSearchParams({ operation: "order", order_id: id })}`, { signal: AbortSignal.any([signal, AbortSignal.timeout(20000)]), cache: "no-store" });
      const record = await response.json();
      if (!response.ok || record.order?.id !== id || !Object.hasOwn(statusLabels, record.order?.status)) throw new Error("Estado no disponible");
      if (!signal.aborted) { setStatus(record.order.status); setError(""); }
    } catch { if (!signal.aborted) setError("No pudimos actualizar el estado. Mostramos el último conocido y volveremos a intentar."); }
  }, [id]);
  const terminal = status === "entregado" || status === "cancelado";
  useLiveRefresh(refresh, !terminal, true);
  return <section className="delivery-estimate" aria-labelledby="order-tracking-title"><h4 id="order-tracking-title">Estado de tu pedido</h4><p role="status"><strong>{statusLabels[status]}</strong></p><p className="form-help">{terminal ? "El pedido finalizó." : "Se actualiza automáticamente mientras esta pestaña esté visible."}</p>{error && <p className="form-error" role="alert">{error}</p>}</section>;
}
