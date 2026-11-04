"use client";

import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import { coordinates, orders } from "@/lib/demo-data";
import { createLocalRequest, readDestination, selectedItems, type BusinessChoice, type FoodProduct, type LocalRequest, type RequestFields, type SelectedItem } from "@/lib/request-draft";
import { Icon } from "./icon";

type Step = "location" | "business" | "menu" | "review" | "complete";
type Nearby = { business: BusinessChoice; distance_km: number };
type FoodRequest = LocalRequest & { delivery_address: string; items: SelectedItem[] };
const steps: Step[] = ["location", "business", "menu", "review", "complete"];
const labels: Record<Step, string> = { location: "¿Dónde querés recibir tu comida?", business: "Negocios cerca de vos", menu: "Elegí tu comida", review: "Revisar pedido", complete: "Pedido simulado" };
const emptyFields: RequestFields = { businessId: "", details: "", latitude: "", longitude: "" };
const displayName = (name: string) => name.replace(" · SIMULADO", "");

function Message({ outgoing = false, children }: { outgoing?: boolean; children: ReactNode }) {
  return <div className={`message ${outgoing ? "outgoing" : "incoming"}`}><div>{children}</div><span className="message-sender">{outgoing ? "Vos" : "Asistente"}{outgoing && <Icon name="check"/>}</span></div>;
}

async function foodQuery(params: Record<string, string>) {
  const response = await fetch(`/api/food?${new URLSearchParams(params)}`, { signal: AbortSignal.timeout(15000) });
  if (!response.ok) throw new Error("No pudimos cargar los negocios o el menú. Intentá de nuevo.");
  return response.json();
}

export function GuidedChat() {
  const [step, setStep] = useState<Step>("location");
  const [fields, setFields] = useState<RequestFields>(emptyFields);
  const [address, setAddress] = useState("");
  const [notes, setNotes] = useState("");
  const [nearby, setNearby] = useState<Nearby[]>([]);
  const [selected, setSelected] = useState<BusinessChoice | null>(null);
  const [products, setProducts] = useState<FoodProduct[]>([]);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [items, setItems] = useState<SelectedItem[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [request, setRequest] = useState<FoodRequest | null>(null);
  const stepHeading = useRef<HTMLHeadingElement>(null);
  const previousStep = useRef(step);
  const confirmed = useRef(false);
  const position = steps.indexOf(step);
  const destination = readDestination(fields.latitude, fields.longitude);

  useEffect(() => { if (previousStep.current !== step) stepHeading.current?.focus(); previousStep.current = step; }, [step]);
  function go(next: Step) { setError(""); setStep(next); }
  function update(name: keyof RequestFields, value: string) { setError(""); setFields((previous) => ({ ...previous, [name]: value })); }
  function useExample() {
    setAddress("Dirección de ejemplo para la exposición");
    setFields((previous) => ({ ...previous, latitude: String(orders[0].destination.latitude), longitude: String(orders[0].destination.longitude) }));
    setError("");
  }
  function useCurrentLocation() {
    if (!navigator.geolocation) { setError("Tu navegador no permite obtener la ubicación. Usá el ejemplo o ingresá las coordenadas."); return; }
    setError(""); setBusy(true);
    navigator.geolocation.getCurrentPosition((result) => {
      setFields((previous) => ({ ...previous, latitude: String(result.coords.latitude), longitude: String(result.coords.longitude) })); setBusy(false);
    }, () => { setError("No pudimos obtener tu ubicación. Permití el acceso o usá el destino de ejemplo."); setBusy(false); }, { timeout: 10000 });
  }
  async function chooseBusiness(business: BusinessChoice) {
    if (busy) return;
    setError(""); setBusy(true);
    try {
      const menu = await foodQuery({ operation: "menu", business_id: business.id });
      if (!Array.isArray(menu.products)) throw new Error("Menú inválido.");
      if (selected?.id !== business.id) { setQuantities({}); setNotes(""); setItems([]); }
      setProducts(menu.products); setSelected(business); update("businessId", business.id); go("menu");
    } catch { setError("No pudimos cargar el menú de ese negocio. Intentá de nuevo."); }
    finally { setBusy(false); }
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (busy) return;
    if (step === "location") {
      if (!address.trim() || !destination) { setError("Escribí la dirección y elegí una ubicación válida antes de buscar negocios."); return; }
      setBusy(true); setError("");
      try {
        const result = await foodQuery({ operation: "nearby", latitude: String(destination.latitude), longitude: String(destination.longitude) });
        if (!Array.isArray(result.businesses)) throw new Error("Respuesta inválida.");
        setNearby(result.businesses); go("business");
      } catch { setError("No pudimos buscar los negocios. Verificá la conexión con el servicio e intentá de nuevo."); }
      finally { setBusy(false); }
    } else if (step === "menu" && selected) {
      try { setItems(selectedItems(products, quantities, selected.id)); go("review"); }
      catch (problem) { setError(problem instanceof Error ? problem.message : "Revisá los productos seleccionados."); }
    } else if (step === "review" && selected && !confirmed.current) {
      try {
        const chosen = selectedItems(products, quantities, selected.id);
        const details = [chosen.map((item) => `${item.quantity} × ${item.name}`).join("\n"), `Dirección: ${address.trim()}`, notes.trim() ? `Indicaciones: ${notes.trim()}` : ""].filter(Boolean).join("\n");
        const local = createLocalRequest({ ...fields, details }, nearby.map((item) => item.business), `demo-chat-${crypto.randomUUID()}`);
        confirmed.current = true; setRequest({ ...local, delivery_address: address.trim(), items: chosen }); go("complete");
      } catch { setError("No pudimos preparar el pedido. Volvé al menú y revisá los productos."); }
    }
  }
  function changeQuantity(product: FoodProduct, amount: number) {
    setError(""); setQuantities((previous) => { const value = (previous[product.id] || 0) + amount; return Number.isSafeInteger(value) && value >= 0 ? { ...previous, [product.id]: value } : previous; });
  }
  function restart() {
    confirmed.current = false; setRequest(null); setFields(emptyFields); setAddress(""); setNotes(""); setNearby([]); setSelected(null); setProducts([]); setQuantities({}); setItems([]); go("location");
  }
  const summary = <dl className="request-summary"><div><dt>Negocio</dt><dd>{selected && displayName(selected.name)}</dd></div><div><dt>Tu comida</dt><dd><ul className="order-items">{items.map((item) => <li key={item.product_id}>{item.quantity} × {item.name}</li>)}</ul></dd></div><div><dt>Dirección</dt><dd>{address.trim()}</dd></div>{destination && <div><dt>Punto de entrega</dt><dd>{coordinates(destination)}</dd></div>}{notes.trim() && <div><dt>Indicaciones</dt><dd>{notes.trim()}</dd></div>}</dl>;

  return <section className="chat-window" aria-label="Pedido guiado, simulación de WhatsApp">
    <header className="chat-header"><span className="contact-avatar"><Icon name="store"/></span><div><h2>Asistente de Delivery</h2><p>Simulación de WhatsApp</p></div><span className="preview-label">Prueba local</span></header>
    <div className="guided-messages"><p className="chat-notice">Esta pantalla representa WhatsApp. No envía mensajes reales.</p>
      <div className="conversation" role="log" aria-label="Conversación del pedido" aria-live="polite" aria-relevant="additions">
        <Message><p>¡Hola! Primero decime dónde querés recibir tu comida para mostrarte los negocios por cercanía.</p></Message>
        {position >= 1 && <><Message outgoing><p>{address.trim()}</p></Message><Message><p>Estos negocios están ordenados según la distancia aproximada a tu punto de entrega. Elegí uno para ver su menú.</p></Message></>}
        {position >= 2 && selected && <><Message outgoing><p>Quiero pedir de {displayName(selected.name)}.</p></Message><Message><p>Este es el menú de {displayName(selected.name)}. Elegí los productos y sus cantidades.</p></Message></>}
        {position >= 3 && <><Message outgoing><ul className="order-items">{items.map((item) => <li key={item.product_id}>{item.quantity} × {item.name}</li>)}</ul></Message><Message><p>Revisá tu comida y la dirección antes de confirmar la simulación.</p></Message></>}
        {step === "complete" && <Message><p>¡Listo! Preparaste un pedido simulado. Existe solo en esta pestaña; todavía no se envió al negocio ni se guardó en el sistema.</p></Message>}
      </div>
    </div>
    <div className="chat-action-area" aria-busy={busy}>
      <h3 ref={stepHeading} tabIndex={-1} className="step-heading">{labels[step]}</h3>
      {step === "business" ? <><p className="form-help">Distancias aproximadas en línea recta. La cobertura se confirma por separado.</p><div className="business-options">{nearby.map(({ business, distance_km }) => <button key={business.id} type="button" className="business-choice" disabled={busy} onClick={() => chooseBusiness(business)}><Icon name="store"/><span>{displayName(business.name)}<small className="business-distance">Aprox. {distance_km.toFixed(1)} km · Ver menú</small></span><Icon name="arrow"/></button>)}</div>{!nearby.length && <p className="form-help">No hay negocios registrados para mostrar.</p>}<button type="button" className="text-button" disabled={busy} onClick={() => go("location")}>Cambiar dirección</button></>
      : step === "complete" && request ? <>{summary}<p className="form-help local-reference">Referencia local: {request.id}</p><p className="form-help">Al recargar se borra la prueba. No hay un pedido enviado, cotización ni cobro en curso.</p><button type="button" className="button button-primary" onClick={restart}>Preparar otro pedido</button></>
      : <form onSubmit={submit} noValidate>
        {step === "location" && <><div className="form-field"><label htmlFor="delivery-address">Dirección de entrega</label><textarea id="delivery-address" rows={2} value={address} onChange={(event) => { setAddress(event.target.value); setError(""); }} disabled={busy} placeholder="Colonia, calle, casa y punto de referencia" required aria-describedby="location-help"/></div><p id="location-help" className="form-help location-help">Escribí la dirección y elegí cómo ubicarla. Buscaremos los negocios desde el punto seleccionado.</p><div className="location-actions"><button type="button" className="button button-secondary" disabled={busy} onClick={useCurrentLocation}><Icon name="location"/>Usar mi ubicación</button><button type="button" className="text-button" disabled={busy} onClick={useExample}>Usar destino de ejemplo</button></div>{destination && <p className="chosen-location">Punto seleccionado: {coordinates(destination)}. Verificá que corresponda a tu dirección.</p>}<details className="manual-location"><summary>Ingresar coordenadas manualmente</summary><div className="coordinate-fields"><div className="form-field"><label htmlFor="destination-latitude">Latitud</label><input id="destination-latitude" value={fields.latitude} disabled={busy} onChange={(event) => update("latitude", event.target.value)}/></div><div className="form-field"><label htmlFor="destination-longitude">Longitud</label><input id="destination-longitude" value={fields.longitude} disabled={busy} onChange={(event) => update("longitude", event.target.value)}/></div></div></details></>}
        {step === "menu" && <><p className="form-help">Menú de ejemplo. Los precios y la disponibilidad real todavía no están configurados.</p><div className="food-products">{products.map((product) => <article className="food-product" key={product.id}><div><h4>{product.name}</h4><p>{product.description}</p><span className="product-price">Precio por confirmar</span></div><div className="quantity-control"><button type="button" aria-label={`Quitar ${product.name}`} disabled={!quantities[product.id]} onClick={() => changeQuantity(product, -1)}>−</button><output aria-label={`Cantidad de ${product.name}`} aria-live="polite">{quantities[product.id] || 0}</output><button type="button" aria-label={`Agregar ${product.name}`} onClick={() => changeQuantity(product, 1)}>+</button></div></article>)}</div>{!products.length && <p className="form-help">Este negocio todavía no tiene productos publicados. Volvé y elegí otro.</p>}<div className="form-field"><label htmlFor="food-notes">Indicaciones para el negocio (opcional)</label><textarea id="food-notes" rows={2} value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Preferencias o indicaciones sobre la preparación"/></div></>}
        {step === "review" && <>{summary}<p className="form-help">Productos sin precios configurados. Todavía no hay un total de comida ni una tarifa de entrega calculados. Confirmar solo prepara la simulación en esta pestaña.</p></>}
        {step !== "location" && <div className="form-actions"><button type="button" className="button button-secondary" disabled={busy} onClick={() => go(steps[position - 1])}>Volver</button><button type="submit" className="button button-primary" disabled={busy || (step === "menu" && !products.length)}>{step === "review" ? "Confirmar simulación" : "Revisar pedido"}<Icon name={step === "review" ? "check" : "arrow"}/></button></div>}
        {step === "location" && <div className="form-actions"><button type="submit" className="button button-primary" disabled={busy}>Buscar negocios cercanos <Icon name="arrow"/></button></div>}
      </form>}
      {busy && <p className="form-help" role="status">Consultando…</p>}
      {error && <p id="chat-error" role="alert" className="form-error">{error}</p>}
    </div>
  </section>;
}
