"use client";

import { useCallback, useEffect, useState } from "react";
import { useLiveRefresh } from "@/lib/use-live-refresh";
import { statusLabels, type OrderRecord } from "@/lib/business-orders";

type Row = { record: OrderRecord; cash: null | { currency: string; expected_amount: string; events: { status: string }[] } };
type Preview = { amounts: { currency: string; delivery_fee: string; courier_payment: string; variable_cost: string; attributable_cost: string; margin: string }; distance_km: string };
const cashLabels: Record<string, string> = { pendiente: "Pendiente de cobro", cobrado: "Cobrado por el repartidor", entregado_al_operador: "Entregado al operador" };

function orderReference(id: string) {
  if (id.length <= 36) return id;
  const token = id.match(/[0-9a-f]{8}-[0-9a-f-]{27}/i)?.[0].slice(0, 8);
  const item = id.match(/-order-(\d+)$/)?.[1];
  return token ? `Pedido ${token}${item ? ` · ${item}` : ""}` : `${id.slice(0, 12)}…${id.slice(-8)}`;
}

export function OperationsPanel() {
  const [rows, setRows] = useState<Row[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [syncError, setSyncError] = useState("");
  const [revision, setRevision] = useState(0);
  const [preview, setPreview] = useState<Preview | null>(null);
  const [calculating, setCalculating] = useState(false);
  const [calculationError, setCalculationError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true); setError(""); setPreview(null); setCalculationError("");
    fetch("/api/operations", { signal: controller.signal }).then(async (response) => {
      const body = await response.json();
      if (!response.ok) throw new Error(body.message);
      if (!Array.isArray(body)) throw new Error("Respuesta de pedidos inválida.");
      if (!controller.signal.aborted) { setRows(body); setSelectedId((current) => body.some((row: Row) => row.record.order.id === current) ? current : body[0]?.record.order.id || ""); setLoading(false); }
    }).catch((cause) => { if (!controller.signal.aborted) { setError(cause.message || "No pudimos consultar los pedidos."); setLoading(false); } });
    return () => controller.abort();
  }, [revision]);
  const sync = useCallback(async (signal: AbortSignal) => {
    try {
      const response = await fetch("/api/operations", { signal: AbortSignal.any([signal, AbortSignal.timeout(20000)]), cache: "no-store" });
      const body = await response.json();
      if (!response.ok || !Array.isArray(body)) throw new Error("Consulta no disponible");
      if (!signal.aborted) { setRows(body); setError(""); setSyncError(""); }
    } catch { if (!signal.aborted) setSyncError("No pudimos actualizar los pedidos. Se conserva el último estado; volveremos a intentar."); }
  }, []);
  useLiveRefresh(sync, !loading && !calculating);
  const selected = rows.find((row) => row.record.order.id === selectedId) || rows[0];
  async function calculate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || calculating) return;
    const data = new FormData(event.currentTarget);
    setCalculating(true); setPreview(null); setCalculationError("");
    try {
      const response = await fetch("/api/operations", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ order_id: selected.record.order.id,
        load_kg: data.get("load"), costs: { currency: data.get("currency"), variable_cost: data.get("variable"), attributable_cost: data.get("attributable") } }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.message);
      setPreview(body);
    } catch (cause) { setCalculationError(cause instanceof Error ? cause.message : "No pudimos calcular el desglose."); }
    finally { setCalculating(false); }
  }
  return <div className="business-panel operations-panel">
    <p className="form-help">Estados con actualización automática cada 5 segundos.</p>
    {syncError && <p className="form-error" role="alert">{syncError}</p>}
    <div className="business-toolbar"><p>Hasta 100 pedidos guardados. Los cobros son registros simulados.</p><button className="button button-secondary" disabled={loading || calculating} onClick={() => setRevision((value) => value + 1)}>Actualizar</button></div>
    {loading ? <p role="status">Consultando pedidos y efectivo…</p> : error ? <p className="form-error" role="alert">{error}</p> : !rows.length ? <section className="panel empty-state"><h2>Todavía no hay pedidos</h2><p>Los pedidos registrados en la API aparecerán aquí.</p></section> : <div className="work-grid">
      <section className="panel"><div className="section-heading"><h2>Pedidos y efectivo</h2><span className="count-label">{rows.length} pedidos</span></div>
        <div className="table-scroll"><table className="operations-table"><caption className="sr-only">Seleccioná un pedido para consultar su desglose.</caption><thead><tr><th>Pedido</th><th>Estado</th><th>Efectivo</th></tr></thead><tbody>{rows.map(({ record, cash }) => <tr key={record.order.id} aria-selected={selected?.record.order.id === record.order.id}><td><button className="text-button" title={record.order.id} aria-label={`Ver pedido ${record.order.id}`} disabled={calculating} onClick={() => { setSelectedId(record.order.id); setPreview(null); setCalculationError(""); }}>{orderReference(record.order.id)}</button></td><td>{statusLabels[record.order.status]}</td><td>{cash ? <>{cashLabels[cash.events.at(-1)?.status || ""] || "Estado no reconocido"}<small className="record-id">{cash.currency} {cash.expected_amount}</small></> : "Sin registro"}</td></tr>)}</tbody></table></div>
        <p className="panel-footnote">Sin registro no significa cero. El efectivo no se suma de nuevo como ingreso.</p>
      </section>
      {selected && <section className="panel"><div className="section-heading"><h2>Tarifa, costos y margen</h2></div><div className="order-detail-body">
        <p className="stop-details">{selected.record.order.id} · {selected.record.order.details}</p>
        <p className="panel-footnote">Previsualización sin guardar ni cambiar el estado. La tarifa y el pago al repartidor usan la política configurada en FastAPI.</p>
        <form key={selected.record.order.id} onSubmit={calculate} className="operations-form">
          <div className="form-field"><label htmlFor="ops-currency">Moneda (tres letras)</label><input id="ops-currency" name="currency" required pattern="[A-Z]{3}" maxLength={3} placeholder="USD" disabled={calculating}/></div>
          {[{ key: "load", label: "Carga del pedido (kg)", min: "0" }, { key: "variable", label: "Costo variable del operador", min: "0" }, { key: "attributable", label: "Costo atribuible del operador", min: "0" }].map((field) => <div className="form-field" key={field.key}><label htmlFor={`ops-${field.key}`}>{field.label}</label><input id={`ops-${field.key}`} name={field.key} type="number" min={field.min} step="any" required disabled={calculating}/></div>)}
          <button className="button button-primary" disabled={calculating}>{calculating ? "Calculando…" : "Calcular desglose"}</button>
        </form>
        {calculationError && <p role="alert" className="form-error">{calculationError}</p>}
        {preview && <div role="status"><h3>Desglose estimado · {preview.amounts.currency}</h3><dl className="request-summary">{([ ["Tarifa de entrega", "delivery_fee"], ["Pago al repartidor", "courier_payment"], ["Costo variable", "variable_cost"], ["Costo atribuible", "attributable_cost"], ["Margen", "margin"] ] as const).map(([label, key]) => <div key={key}><dt>{label}</dt><dd>{preview.amounts.currency} {preview.amounts[key]}</dd></div>)}</dl><p className="panel-footnote">Distancia aproximada: {preview.distance_km} km. Este cálculo no es una cotización guardada ni un resultado financiero real.</p></div>}
      </div></section>}
    </div>}
  </div>;
}
