"use client";

import { useEffect, useState } from "react";
import type { Point } from "@/lib/request-draft";

type Estimate = { estimated_minutes: number; distance_km: number; late_probability: number | null;
  promised_minutes: number | null; outside_training_range: boolean; model_version: string };
const decimal = new Intl.NumberFormat("es-SV", { maximumFractionDigits: 1 });

export function DeliveryEstimate({ origin, destination }: { origin: Point; destination: Point }) {
  const [estimate, setEstimate] = useState<Estimate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deadline, setDeadline] = useState("");
  const [comparison, setComparison] = useState<number | null>(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setLoading(true); setError(""); setEstimate(null);
    fetch("/api/food/estimate", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origin, destination, promised_minutes: comparison }), signal: controller.signal })
      .then(async (response) => {
        const result = await response.json();
        if (!response.ok) throw new Error(result.message);
        if (!Number.isFinite(result.estimated_minutes) || result.estimated_minutes < 0 || !Number.isFinite(result.distance_km) || result.distance_km < 0
          || (result.late_probability !== null && (!Number.isFinite(result.late_probability) || result.late_probability < 0 || result.late_probability > 1))) throw new Error("El modelo devolvió una estimación inválida.");
        if (!controller.signal.aborted) { setEstimate(result); setLoading(false); }
      }).catch((cause) => { if (!controller.signal.aborted) { setError(cause.message || "No pudimos estimar esta entrega."); setLoading(false); } });
    return () => controller.abort();
  }, [origin.latitude, origin.longitude, destination.latitude, destination.longitude, comparison, revision]); // coordenadas, no identidad de los objetos

  function compare() {
    const minutes = Number(deadline);
    if (deadline.trim() && (!Number.isFinite(minutes) || minutes <= 0)) { setError("Ingresá un plazo mayor que cero para comparar."); return; }
    setComparison(deadline.trim() ? minutes : null); setRevision((value) => value + 1);
  }
  return <section className="delivery-estimate" aria-labelledby="delivery-estimate-title" aria-busy={loading}>
    <h4 id="delivery-estimate-title">Estimación de tu entrega</h4>
    {loading && <p role="status" className="form-help">Calculando con el modelo de entregas…</p>}
    {error && <p className="form-error" role="alert">{error} <button type="button" className="text-button" disabled={loading} onClick={() => setRevision((value) => value + 1)}>Reintentar estimación</button></p>}
    {estimate && <><dl className="request-summary" aria-live="polite"><div><dt>Tiempo estimado</dt><dd><strong>{Math.ceil(estimate.estimated_minutes)} min</strong> desde la solicitud hasta la entrega</dd></div><div><dt>Distancia aproximada</dt><dd>{decimal.format(estimate.distance_km)} km en línea recta</dd></div>{estimate.late_probability !== null && <div><dt>Riesgo de superar {estimate.promised_minutes} min</dt><dd>{decimal.format(estimate.late_probability * 100)} %</dd></div>}</dl>
      <p className="form-help">Estimación del modelo, sin garantía de entrega. Validación local pendiente; no es una ruta por calles.</p>
      {estimate.outside_training_range && <p className="form-help">Este recorrido o plazo está fuera del rango usado para entrenar el modelo.</p>}
      <details className="manual-location"><summary>Ver modelo y comparación de plazo</summary><p className="form-help">Modelo: {estimate.model_version}. El riesgo compara la entrega con el plazo que ingresés; no fija una promesa del negocio.</p><div className="form-field"><label htmlFor="delivery-deadline">Plazo para comparar (minutos, opcional)</label><input id="delivery-deadline" type="number" min="0" step="any" value={deadline} disabled={loading} onChange={(event) => setDeadline(event.target.value)}/></div><button type="button" className="text-button" disabled={loading} onClick={compare}>Comparar plazo</button></details>
    </>}
  </section>;
}
