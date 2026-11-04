"use client";

import { useRef, useState } from "react";

type Case = "individual" | "grouped";
type OrderResult = { order: { id: string; business_id: string; status: string } };
type Receipt = { scenario: Case; input: unknown; result: {
  order?: OrderResult; orders?: OrderResult[];
  delivery_prediction?: { estimated_minutes: number; distance_km: number; late_probability: number; promised_minutes: number };
  delivery_predictions?: Record<string, { estimated_minutes: number; distance_km: number; late_probability: number; promised_minutes: number }>;
  cash: { currency: string; expected_amount: string; events: { status: string }[] } | { currency: string; expected_amount: string; events: { status: string }[] }[];
  assignment: { id: string; released_at: string | null; route: { stops: { kind: string; order_id: string }[]; total_distance_km: string } };
  courier: { id: string; available: boolean };
  quote?: { amounts: { currency: string; delivery_fee: string; margin: string } };
  comparison?: { individual_totals: { currency: string; total_cost: string }; grouped: { amounts: { total_cost: string } }; individual_minus_group_cost: string };
} };
const number = (value: number) => new Intl.NumberFormat("es-SV", { maximumFractionDigits: 1 }).format(value);

export function DemoPanel() {
  const [busy, setBusy] = useState<Case | null>(null);
  const [error, setError] = useState("");
  const [receipts, setReceipts] = useState<Partial<Record<Case, Receipt>>>({});
  const lock = useRef(false);
  async function run(scenario: Case) {
    if (lock.current) return;
    lock.current = true; setBusy(scenario); setError(""); setReceipts((current) => { const next = { ...current }; delete next[scenario]; return next; });
    try {
      const response = await fetch("/api/demo", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ scenario }), signal: AbortSignal.timeout(130000) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.message);
      const orders = body.result?.orders || (body.result?.order ? [body.result.order] : []);
      const cash = Array.isArray(body.result?.cash) ? body.result.cash : [body.result?.cash];
      if (orders.length !== (scenario === "individual" ? 1 : 2) || cash.length !== orders.length || !orders.every((row: OrderResult) => row.order.status === "entregado") || !cash.every((row: { events?: { status: string }[] }) => row?.events?.at(-1)?.status === "entregado_al_operador") || !body.result?.courier?.available || !body.result?.assignment?.released_at) throw new Error("La ejecución no confirmó todas las entregas, efectivo y liberación. Revisá los registros antes de repetir.");
      setReceipts((current) => ({ ...current, [scenario]: body }));
    } catch (cause) { setError(cause instanceof Error ? cause.message : "No pudimos confirmar la demo."); }
    finally { lock.current = false; setBusy(null); }
  }
  function download(receipt: Receipt) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(receipt, null, 2)], { type: "application/json" }));
    const link = document.createElement("a"); link.href = url; link.download = `demo-${receipt.scenario}.json`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return <details className="panel demo-panel"><summary>Demostración completa: entregas y efectivo</summary><div className="order-detail-body">
    <p className="form-help">Crea pedidos de comida de prueba y ejecuta solicitud, cotización, confirmación, ruta, entrega y registro del efectivo. Usa importes y coordenadas de ejemplo; no prepara comida ni mueve dinero real.</p>
    <div className="form-actions"><button className="button button-primary" disabled={!!busy} onClick={() => run("individual")}>{busy === "individual" ? "Ejecutando…" : "Probar entrega individual"}</button><button className="button button-secondary" disabled={!!busy} onClick={() => run("grouped")}>{busy === "grouped" ? "Ejecutando…" : "Probar dos entregas agrupadas"}</button></div>
    {busy && <p className="form-help" role="status">Guardando el recorrido simulado. No cierres esta pestaña.</p>}
    {error && <p className="form-error" role="alert">{error}</p>}
    {(Object.entries(receipts) as [Case, Receipt][]).map(([scenario, receipt]) => {
      const result = receipt.result; const rows = result.orders || [result.order!];
      const cashRecords = Array.isArray(result.cash) ? result.cash : [result.cash];
      const predictions = result.delivery_predictions || { [rows[0].order.id]: result.delivery_prediction! };
      return <section key={scenario} className="context-section"><h3>{scenario === "individual" ? "Entrega individual completada" : "Dos entregas agrupadas completadas"}</h3><p className="form-help">Pedidos entregados, efectivo registrado al operador y repartidor disponible.</p>
        <dl className="request-summary">{rows.map((row, index) => <div key={row.order.id}><dt>Pedido {index + 1}</dt><dd>{Math.ceil(predictions[row.order.id].estimated_minutes)} min estimados · {number(predictions[row.order.id].distance_km)} km aprox. · {number(predictions[row.order.id].late_probability * 100)} % de superar {predictions[row.order.id].promised_minutes} min (plazo de ejemplo)</dd></div>)}</dl>
        <dl className="request-summary">{cashRecords.map((cash, index) => <div key={index}><dt>Efectivo del envío {index + 1}</dt><dd>{cash.currency} {cash.expected_amount} · registrado al operador (simulado)</dd></div>)}</dl>
        {result.quote && <p className="form-help">Tarifa de ejemplo: {result.quote.amounts.currency} {result.quote.amounts.delivery_fee} · Margen estimado: {result.quote.amounts.currency} {result.quote.amounts.margin}</p>}
        {result.comparison && <dl className="request-summary"><div><dt>Costo por separado</dt><dd>{result.comparison.individual_totals.currency} {result.comparison.individual_totals.total_cost}</dd></div><div><dt>Costo agrupado</dt><dd>{result.comparison.individual_totals.currency} {result.comparison.grouped.amounts.total_cost}</dd></div><div><dt>Diferencia (individual − grupo)</dt><dd>{result.comparison.individual_totals.currency} {result.comparison.individual_minus_group_cost}</dd></div></dl>}
        <p className="form-help">Distancia en línea recta. ETA por pedido; no incluye demoras por agrupar ni garantiza entrega. Los costos del grupo consideran una base por recorrido.</p>
        <ol className="simple-steps">{result.assignment.route.stops.map((stop, index) => <li key={index}>{stop.kind === "recogida" ? "Recogida" : "Entrega"}: Pedido {rows.findIndex((row) => row.order.id === stop.order_id) + 1}</li>)}</ol>
        <div className="form-actions"><a className="text-button" href={`/negocio?business_id=${encodeURIComponent(rows[0].order.business_id)}`}>Ver pedidos del negocio</a><button className="text-button" onClick={() => download(receipt)}>Descargar recibo JSON</button></div>
      </section>;
    })}
  </div></details>;
}
