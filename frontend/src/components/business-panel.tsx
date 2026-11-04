"use client";

import { useEffect, useRef, useState } from "react";
import { type BusinessChoice } from "@/lib/request-draft";
import { businessActions, statusLabels, type BusinessTarget, type OrderRecord, type OrderStatus } from "@/lib/business-orders";
import { coordinates } from "@/lib/demo-data";

const name = (value: string) => value.replace(" · SIMULADO", "");
const date = (value: string) => new Intl.DateTimeFormat("es-SV", { dateStyle: "medium", timeStyle: "short", timeZone: "America/El_Salvador" }).format(new Date(value));

async function query(params: Record<string, string>, signal: AbortSignal) {
  const response = await fetch(`/api/business?${new URLSearchParams(params)}`, { signal });
  if (!response.ok) throw new Error("No pudimos consultar los pedidos. Intentá actualizar de nuevo.");
  return response.json();
}

export function BusinessPanel() {
  const [businesses, setBusinesses] = useState<BusinessChoice[]>([]);
  const [businessId, setBusinessId] = useState("");
  const [records, setRecords] = useState<OrderRecord[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [filter, setFilter] = useState<OrderStatus | "">("");
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [catalogError, setCatalogError] = useState("");
  const [dataError, setDataError] = useState("");
  const [actionError, setActionError] = useState("");
  const [notice, setNotice] = useState("");
  const [pendingCancel, setPendingCancel] = useState(false);
  const [saving, setSaving] = useState(false);
  const actionLock = useRef(false);
  const detailHeading = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    setCatalogError("");
    query({ operation: "businesses" }, controller.signal).then((rows) => {
      if (controller.signal.aborted) return;
      if (!Array.isArray(rows)) throw new Error("Catálogo inválido.");
      setBusinesses(rows);
      const linkedBusiness = new URLSearchParams(window.location.search).get("business_id");
      setBusinessId((current) => rows.some((row: BusinessChoice) => row.id === current) ? current
        : !current && rows.some((row: BusinessChoice) => row.id === linkedBusiness) ? linkedBusiness! : rows[0]?.id || "");
      if (!rows.length) setLoading(false);
    }).catch(() => { if (!controller.signal.aborted) { setCatalogError("No pudimos cargar los negocios. Pulsá Actualizar para intentarlo de nuevo."); setLoading(false); } });
    return () => controller.abort();
  }, [revision]);

  useEffect(() => {
    if (!businessId) return;
    const controller = new AbortController();
    setLoading(true); setDataError("");
    query({ operation: "orders", business_id: businessId }, controller.signal).then((rows) => {
      if (controller.signal.aborted) return;
      if (!Array.isArray(rows)) throw new Error("Pedidos inválidos.");
      setRecords(rows); setLoading(false);
    }).catch(() => { if (!controller.signal.aborted) { setDataError("No pudimos cargar los pedidos de este negocio. Pulsá Actualizar para reintentar."); setLoading(false); } });
    return () => controller.abort();
  }, [businessId, revision]);

  const visible = records.filter((record) => record.order.business_id === businessId && (!filter || record.order.status === filter));
  const selected = visible.find((record) => record.order.id === selectedId) || visible[0];
  const targets = selected ? businessActions(selected.order.status) : [];
  const disabled = loading || saving || !!catalogError || !!dataError;

  function resetFeedback() { setPendingCancel(false); setActionError(""); setNotice(""); }
  function refresh() { resetFeedback(); setRevision((value) => value + 1); }
  function selectOrder(id: string) { setSelectedId(id); resetFeedback(); requestAnimationFrame(() => detailHeading.current?.focus()); }

  async function changeStatus(target: BusinessTarget) {
    if (actionLock.current || disabled || !selected || !targets.includes(target)) return;
    actionLock.current = true; setSaving(true); setActionError(""); setNotice("");
    const id = selected.order.id;
    try {
      const response = await fetch("/api/business", { method: "POST", headers: { "Content-Type": "application/json" }, signal: AbortSignal.timeout(25000),
        body: JSON.stringify({ order_id: id, business_id: businessId, expected: selected.order.status, target }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "No pudimos guardar el cambio. Actualizá el pedido antes de reintentar.");
      if (result.order?.id !== id || result.order?.business_id !== businessId || result.order?.status !== target) throw new Error("No pudimos verificar el cambio. Actualizá el pedido antes de reintentar.");
      setRecords((current) => current.map((record) => record.order.id === id ? result : record));
      setNotice(target === "cancelado" ? "Pedido cancelado. El cambio quedó guardado." : "Pedido confirmado. El cambio quedó guardado.");
      setPendingCancel(false);
    } catch (problem) {
      setActionError(problem instanceof Error ? problem.message : "No pudimos guardar el cambio. Actualizá antes de reintentar.");
      setPendingCancel(false); setRevision((value) => value + 1);
    } finally { actionLock.current = false; setSaving(false); }
  }

  return <div className="business-panel">
    <section className="business-toolbar" aria-label="Seleccionar negocio y pedidos">
      <div className="form-field"><label htmlFor="business-select">Negocio</label><select id="business-select" value={businessId} disabled={saving || !businesses.length} onChange={(event) => { if (event.target.value === businessId) return; setBusinessId(event.target.value); setRecords([]); setSelectedId(""); setFilter(""); resetFeedback(); }}>{businesses.map((business) => <option key={business.id} value={business.id}>{name(business.name)}</option>)}</select></div>
      <div className="form-field"><label htmlFor="order-filter">Estado</label><select id="order-filter" value={filter} disabled={saving} onChange={(event) => { setFilter(event.target.value as OrderStatus | ""); setSelectedId(""); resetFeedback(); }}><option value="">Todos los estados</option>{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>
      <button type="button" className="button button-secondary" disabled={saving || loading} onClick={refresh}>Actualizar</button>
    </section>
    {loading && <p className="business-status" role="status">Consultando pedidos…</p>}
    {(catalogError || dataError) && <p className="form-error" role="alert">{catalogError || dataError}</p>}
    {actionError && <p className="form-error" role="alert">{actionError}</p>}
    {notice && <p className="saved-notice" role="status">{notice}</p>}
    {!businesses.length && !loading && !catalogError && <p className="business-status">No hay negocios registrados para mostrar.</p>}
    <div className="business-order-grid">
      <section className="panel" aria-labelledby="business-orders-heading"><div className="section-heading"><h2 id="business-orders-heading">Pedidos del negocio</h2><span className="count-label">{visible.length} {visible.length === 1 ? "pedido" : "pedidos"}</span></div>
        {visible.length ? <div className="table-scroll"><table className="business-orders-table"><caption className="sr-only">Pedidos registrados del negocio seleccionado</caption><thead><tr><th scope="col">Pedido</th><th scope="col">Estado</th><th scope="col">Detalle</th></tr></thead><tbody>{visible.map((record) => <tr key={record.order.id} className={record.order.id === selected?.order.id ? "selected-order" : ""}><td><strong className="order-identifier">{record.order.id}</strong></td><td><span className="status-label">{statusLabels[record.order.status]}</span></td><td><button type="button" className="text-button" aria-label={`Ver detalle de ${record.order.id}`} aria-controls="business-order-detail" disabled={saving} onClick={() => selectOrder(record.order.id)}>Ver detalle</button></td></tr>)}</tbody></table></div>
        : !loading && !dataError && <p className="panel-footnote">{filter ? "No hay pedidos con este estado." : "Este negocio todavía no tiene pedidos registrados."}</p>}
        <p className="panel-footnote">Hasta 100 pedidos por consulta. Pulsá Actualizar para ver cambios recientes.</p>
      </section>
      <section className="panel order-detail" id="business-order-detail" aria-labelledby="order-detail-heading"><div className="section-heading"><h2 id="order-detail-heading" ref={detailHeading} tabIndex={-1}>Detalle del pedido</h2></div>
        {selected ? <div className="order-detail-body"><p className="record-id">{selected.order.id}</p><p className="order-current-state"><span className="status-label">{statusLabels[selected.order.status]}</span></p><h3>Comida e indicaciones</h3><p className="order-description">{selected.order.details}</p><h3>Lugar de entrega</h3><p className="coordinates">{coordinates(selected.order.destination)}</p>
          <h3>Historial</h3><ol className="order-history">{selected.events.map((event, index) => <li key={`${index}-${event.occurred_at}`}><strong>{statusLabels[event.status]}</strong><time dateTime={event.occurred_at}>{date(event.occurred_at)}</time></li>)}</ol><p className="form-help">Horas de El Salvador.</p>
          {selected.order.status === "solicitado" && <p className="form-help">Pendiente de cotización. La confirmación se habilita cuando el pedido esté cotizado.</p>}
          {selected.order.status === "confirmado" && <p className="form-help">Pedido confirmado; en espera de asignación.</p>}
          {selected.order.status === "asignado" && <p className="form-help">El repartidor tiene la entrega asignada.</p>}
          {selected.order.status === "recogido" && <p className="form-help">El pedido está en camino.</p>}
          {!!targets.length && !pendingCancel && <div className="form-actions">{targets.includes("confirmado") && <button type="button" className="button button-primary" disabled={disabled} onClick={() => changeStatus("confirmado")}>Confirmar pedido</button>}{targets.includes("cancelado") && <button type="button" className="button button-secondary" disabled={disabled} onClick={() => setPendingCancel(true)}>Cancelar pedido</button>}</div>}
          {pendingCancel && <div className="cancel-check" role="group" aria-label="Confirmar cancelación"><p>¿Querés cancelar este pedido? El cambio se guardará en el sistema.</p><div className="form-actions"><button type="button" className="button button-secondary" disabled={disabled} onClick={() => setPendingCancel(false)}>Volver</button><button type="button" className="button button-danger" disabled={disabled} onClick={() => changeStatus("cancelado")}>Sí, cancelar pedido</button></div></div>}
          {saving && <p className="form-help" role="status">Guardando cambio…</p>}
        </div> : <p className="panel-footnote">Elegí un pedido para consultar su detalle.</p>}
      </section>
    </div>
  </div>;
}
