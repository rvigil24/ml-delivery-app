"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useLiveRefresh } from "@/lib/use-live-refresh";
import { canFinishRoute, nextCourierStop, stopCompleted, type Courier, type CourierRoute } from "@/lib/courier-routes";
import { coordinates } from "@/lib/demo-data";
import { statusLabels } from "@/lib/business-orders";
import { Icon } from "./icon";

async function query(params: Record<string, string>, signal: AbortSignal) {
  const response = await fetch(`/api/courier?${new URLSearchParams(params)}`, { signal: AbortSignal.any([signal, AbortSignal.timeout(20000)]), cache: "no-store" });
  if (!response.ok) throw new Error("No pudimos consultar las entregas.");
  return response.json();
}

export function CourierPanel() {
  const [couriers, setCouriers] = useState<Courier[]>([]);
  const [courierId, setCourierId] = useState("");
  const [routes, setRoutes] = useState<CourierRoute[]>([]);
  const [routeId, setRouteId] = useState("");
  const [revision, setRevision] = useState(0);
  const [loading, setLoading] = useState(true);
  const [catalogError, setCatalogError] = useState("");
  const [dataError, setDataError] = useState("");
  const [actionError, setActionError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  const actionLock = useRef(false);

  useEffect(() => {
    const controller = new AbortController(); setCatalogError("");
    query({ operation: "couriers" }, controller.signal).then((rows) => {
      if (controller.signal.aborted) return;
      if (!Array.isArray(rows)) throw new Error("Repartidores inválidos.");
      setCouriers(rows); setCourierId((current) => rows.some((row: Courier) => row.id === current) ? current : rows[0]?.id || "");
      if (!rows.length) setLoading(false);
    }).catch(() => { if (!controller.signal.aborted) { setCatalogError("No pudimos cargar los repartidores. Pulsá Actualizar para reintentar."); setLoading(false); } });
    return () => controller.abort();
  }, [revision]);

  useEffect(() => {
    if (!courierId) return;
    const controller = new AbortController(); setLoading(true); setDataError("");
    query({ operation: "assignments", courier_id: courierId }, controller.signal).then((rows) => {
      if (controller.signal.aborted) return;
      if (!Array.isArray(rows)) throw new Error("Asignaciones inválidas.");
      setRoutes(rows); setLoading(false);
    }).catch(() => { if (!controller.signal.aborted) { setDataError("No pudimos cargar las asignaciones. Pulsá Actualizar para reintentar."); setLoading(false); } });
    return () => controller.abort();
  }, [courierId, revision]);

  const sync = useCallback(async (signal: AbortSignal) => {
    try {
      const [assignments, people] = await Promise.all([query({ operation: "assignments", courier_id: courierId }, signal), query({ operation: "couriers" }, signal)]);
      if (!Array.isArray(assignments) || !Array.isArray(people)) throw new Error("Respuesta inválida");
      if (!signal.aborted && !actionLock.current) { setRoutes(assignments); setCouriers(people); setDataError(""); }
    } catch { if (!signal.aborted) setDataError("No pudimos actualizar las entregas. Se conserva el último estado; volveremos a intentar."); }
  }, [courierId]);
  useLiveRefresh(sync, !!courierId && !loading && !saving && !catalogError);

  const courier = couriers.find((row) => row.id === courierId);
  const selected = routes.find((row) => row.id === routeId) || routes.find((row) => row.active) || routes[0];
  const next = selected ? nextCourierStop(selected) : null;
  const finish = selected ? canFinishRoute(selected) : false;
  const disabled = loading || saving || !!catalogError || !!dataError;
  function clearFeedback() { setActionError(""); setNotice(""); }

  async function advance(action: "progress" | "complete") {
    if (actionLock.current || disabled || !selected || (action === "progress" && !next) || (action === "complete" && !finish)) return;
    actionLock.current = true; setSaving(true); clearFeedback();
    try {
      const response = await fetch("/api/courier", { method: "POST", headers: { "Content-Type": "application/json" }, signal: AbortSignal.timeout(15000),
        body: JSON.stringify({ action, courier_id: courierId, assignment_id: selected.id,
          ...(action === "progress" && next ? { order_id: next.stop.order_id, expected: next.expected, target: next.target } : {}) }) });
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || "No pudimos guardar el avance. Actualizá antes de reintentar.");
      if (result.id !== selected.id || result.courier_id !== courierId || !Array.isArray(result.orders)) throw new Error("No pudimos verificar el resultado. Actualizá la ruta antes de reintentar.");
      if (action === "complete" && result.active !== false) throw new Error("No pudimos verificar el cierre. Actualizá la ruta.");
      if (action === "progress" && next && !result.orders.some((record: CourierRoute["orders"][number]) => record.order.id === next.stop.order_id && record.order.status === next.target)) throw new Error("El estado cambió. Actualizá la ruta.");
      setRoutes((current) => current.map((row) => row.id === result.id ? result : row));
      setNotice(action === "complete" ? "Ruta finalizada. El cambio quedó guardado." : next?.target === "recogido" ? "Recogida registrada." : "Entrega registrada.");
      setRevision((value) => value + 1);
    } catch (problem) { setActionError(problem instanceof Error ? problem.message : "No pudimos guardar el avance. Actualizá la ruta."); setRevision((value) => value + 1); }
    finally { actionLock.current = false; setSaving(false); }
  }

  return <div className="courier-panel">
    <section className="business-toolbar" aria-label="Elegir repartidor y ruta">
      <div className="form-field"><label htmlFor="courier-select">Repartidor</label><select id="courier-select" value={courierId} disabled={saving || !couriers.length} onChange={(event) => { if (event.target.value === courierId) return; setCourierId(event.target.value); setRoutes([]); setRouteId(""); clearFeedback(); }}>{couriers.map((row) => <option value={row.id} key={row.id}>{row.id} · {row.vehicle === "bicicleta" ? "Bicicleta" : "Motocicleta"}</option>)}</select></div>
      <div className="form-field"><label htmlFor="assignment-select">Ruta asignada</label><select id="assignment-select" value={selected?.id || ""} disabled={saving || !routes.length} onChange={(event) => { setRouteId(event.target.value); clearFeedback(); }}><option value="" disabled>{loading ? "Consultando rutas…" : "Sin asignaciones"}</option>{routes.map((row) => <option key={row.id} value={row.id}>{row.id} · {row.active ? "En curso" : "Finalizada"}</option>)}</select></div>
      <button type="button" className="button button-secondary" disabled={saving || loading} onClick={() => { clearFeedback(); setRevision((value) => value + 1); }}>Actualizar</button>
    </section>
    <p className="form-help">Estados con actualización automática cada 5 segundos.</p>
    {courier && <p className="courier-profile"><Icon name="bike"/>{courier.vehicle === "bicicleta" ? "Bicicleta" : "Motocicleta"} · {courier.approved ? "Aprobado" : "Aprobación pendiente"} · {courier.available ? "Disponible" : "Ocupado"}</p>}
    {loading && <p className="business-status" role="status">Consultando asignaciones…</p>}
    {(catalogError || dataError) && <p className="form-error" role="alert">{catalogError || dataError}</p>}
    {actionError && <p className="form-error" role="alert">{actionError}</p>}
    {notice && <p className="saved-notice" role="status">{notice}</p>}
    {!loading && !catalogError && !dataError && !selected && <section className="panel courier-empty"><Icon name="location"/><h2>{couriers.length ? "Todavía no tenés rutas asignadas" : "No hay repartidores registrados"}</h2><p>Cuando operaciones asigne una ruta, aparecerán aquí los pedidos y sus paradas.</p></section>}
    {selected && <section className="panel courier-route"><div className="section-heading"><h2>Paradas de tu ruta</h2><span className="status-label">{selected.active ? "En curso" : "Finalizada"}</span></div>
      <div className="courier-route-body"><p className="record-id">{selected.id}</p><p className="route-distance">{Number(selected.total_distance_km).toFixed(2)} km de referencia · Distancia en línea recta, sin navegación por calles.</p><p className="form-help">Punto inicial: {coordinates(selected.start)}. Ruta simulada; sin GPS en vivo.</p>
        <ol className="courier-stops">{selected.stops.map((stop, index) => {
          const record = selected.orders.find((row) => row.order.id === stop.order_id);
          const done = stopCompleted(selected, stop); const current = next?.index === index;
          return <li key={`${stop.order_id}-${stop.kind}`} className={current ? "next-stop" : ""}><span className="stop-position">{index + 1}</span><div className="stop-content"><div className="stop-title"><h3>{stop.kind === "recogida" ? "Recoger comida" : "Entregar pedido"}</h3><span className="status-label">{done ? "Completada" : current ? "Siguiente parada" : "Pendiente"}</span></div><p className="record-id">{stop.order_id}</p><p className="coordinates">{coordinates(stop.location)}</p>{record && <><p className="stop-details">{record.order.details}</p><p className="form-help">Estado del pedido: {statusLabels[record.order.status]}</p></>}</div></li>;
        })}</ol>
        <div className="courier-route-actions">{next && <p className="form-help">Completá la parada {next.index + 1} para continuar con la siguiente.</p>}{selected.active && !next && !finish && <p className="form-help">No hay un avance disponible. Actualizá para consultar el estado actual.</p>}{finish && <p className="form-help">Todos los pedidos están entregados. Finalizá la ruta para liberar al repartidor.</p>}
          <div className="form-actions">{next && <button type="button" className="button button-primary" disabled={disabled} onClick={() => advance("progress")}>{next.target === "recogido" ? "Confirmar recogida" : "Confirmar entrega"}</button>}{finish && <button type="button" className="button button-primary" disabled={disabled} onClick={() => advance("complete")}>Finalizar ruta</button>}</div>{saving && <p role="status" className="form-help">Guardando avance…</p>}
        </div>
      </div>
    </section>}
    <p className="panel-footnote">Hasta 100 asignaciones por consulta. Pulsá Actualizar para ver cambios recientes.</p>
  </div>;
}
