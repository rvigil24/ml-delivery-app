"use client";

import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";
import { businesses, businessName, coordinates, orders } from "@/lib/demo-data";
import { createLocalRequest, readDestination, type LocalRequest, type RequestFields } from "@/lib/request-draft";
import { Icon } from "./icon";

type Step = "business" | "details" | "destination" | "review" | "complete";
const steps: Step[] = ["business", "details", "destination", "review", "complete"];
const labels: Record<Step, string> = { business: "Elegir negocio", details: "Detalle del pedido", destination: "Destino del envío", review: "Revisar solicitud", complete: "Solicitud simulada" };
const emptyFields: RequestFields = { businessId: "", details: "", latitude: "", longitude: "" };

function Message({ outgoing = false, children }: { outgoing?: boolean; children: ReactNode }) {
  return <div className={`message ${outgoing ? "outgoing" : "incoming"}`}><div>{children}</div><span className="message-sender">{outgoing ? "Vos" : "Asistente"}{outgoing && <Icon name="check"/>}</span></div>;
}

export function GuidedChat() {
  const [step, setStep] = useState<Step>("business");
  const [fields, setFields] = useState<RequestFields>(emptyFields);
  const [error, setError] = useState("");
  const [request, setRequest] = useState<LocalRequest | null>(null);
  const stepHeading = useRef<HTMLHeadingElement>(null);
  const previousStep = useRef(step);
  const confirmed = useRef(false);
  const position = steps.indexOf(step);
  const destination = readDestination(fields.latitude, fields.longitude);
  const selected = businesses.find((business) => business.id === fields.businessId);

  useEffect(() => {
    if (previousStep.current !== step) stepHeading.current?.focus();
    previousStep.current = step;
  }, [step]);

  function go(next: Step) { setError(""); setStep(next); }
  function update(name: keyof RequestFields, value: string) { setError(""); setFields((previous) => ({ ...previous, [name]: value })); }
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (step === "details") {
      if (!fields.details.trim()) { setError("Indicá qué querés pedir y las cantidades antes de continuar."); return; }
      go("destination");
    } else if (step === "destination") {
      if (!destination) { setError("Indicá una latitud entre −90 y 90 y una longitud entre −180 y 180, con punto decimal."); return; }
      go("review");
    } else if (step === "review" && !confirmed.current) {
      try {
        const local = createLocalRequest(fields, businesses, `demo-chat-${crypto.randomUUID()}`);
        confirmed.current = true;
        setRequest(local);
        go("complete");
      } catch { setError("No pudimos preparar la solicitud. Revisá sus datos e intentá de nuevo."); }
    }
  }
  function restart() { confirmed.current = false; setRequest(null); setFields(emptyFields); go("business"); }

  return <section className="chat-window" aria-label="Solicitud guiada, simulación de WhatsApp">
    <header className="chat-header"><span className="contact-avatar"><Icon name="package"/></span><div><h2>Asistente de Delivery</h2><p>Simulación de WhatsApp</p></div><span className="preview-label">Prueba local</span></header>
    <div className="guided-messages">
      <p className="chat-notice">Esta pantalla representa WhatsApp. No envía mensajes reales.</p>
      <div className="conversation" role="log" aria-label="Conversación de la solicitud" aria-live="polite" aria-relevant="additions">
        <Message><p>¡Hola! ¿De qué negocio querés pedir comida hoy?</p></Message>
        {position >= 1 && selected && <><Message outgoing><p>Quiero pedir de {businessName(selected.id)}.</p></Message><Message><p>¿Qué querés pedir de {businessName(selected.id)}? Indicá los productos, las cantidades y cualquier indicación para el negocio.</p></Message></>}
        {position >= 2 && <><Message outgoing><p>{fields.details.trim()}</p></Message><Message><p>¿Dónde querés recibir tu pedido? Indicá las coordenadas o usá el destino de ejemplo.</p></Message></>}
        {position >= 3 && destination && <><Message outgoing><p>Destino: {coordinates(destination)}.</p></Message><Message><p>Revisá los datos antes de confirmar la simulación. El costo y la duración todavía no se han calculado.</p></Message></>}
        {step === "complete" && <Message><p>¡Listo! Preparaste una solicitud simulada. Existe solo en esta pestaña; todavía no se envió al negocio ni se guardó en el sistema.</p></Message>}
      </div>
    </div>
    <div className="chat-action-area">
      <h3 ref={stepHeading} tabIndex={-1} className="step-heading">{labels[step]}</h3>
      {step === "business" ? <div className="business-options">{businesses.map((business) => <button key={business.id} type="button" className="business-choice" onClick={() => { update("businessId", business.id); go("details"); }}><Icon name="store"/><span>{businessName(business.id)}</span><Icon name="arrow"/></button>)}</div>
      : step === "complete" && request ? <><dl className="request-summary"><div><dt>Referencia local</dt><dd className="local-reference">{request.id}</dd></div><div><dt>Negocio</dt><dd>{businessName(request.business_id)}</dd></div><div><dt>Pedido</dt><dd>{request.details}</dd></div><div><dt>Destino</dt><dd>{coordinates(request.destination)}</dd></div></dl><p className="form-help">Al recargar se borra la prueba. No hay una entrega, cotización ni cobro en curso.</p><button type="button" className="button button-primary" onClick={restart}>Preparar otra solicitud</button></>
      : <form onSubmit={submit} noValidate>
        {step === "details" && <div className="form-field"><label htmlFor="order-details">Detalle del pedido</label><textarea id="order-details" rows={3} value={fields.details} onChange={(event) => update("details", event.target.value)} placeholder="Escribí los platos o productos, las cantidades y tus indicaciones" required aria-invalid={!!error} aria-describedby={error ? "chat-error" : undefined}/></div>}
        {step === "destination" && <><p id="coordinates-help" className="form-help">Usá coordenadas en grados con punto decimal. Esto ubica el destino; no comprueba la cobertura de entrega.</p><div className="coordinate-fields"><div className="form-field"><label htmlFor="destination-latitude">Latitud</label><input id="destination-latitude" type="text" inputMode="text" value={fields.latitude} onChange={(event) => update("latitude", event.target.value)} required aria-invalid={!!error} aria-describedby={`coordinates-help${error ? " chat-error" : ""}`}/></div><div className="form-field"><label htmlFor="destination-longitude">Longitud</label><input id="destination-longitude" type="text" inputMode="text" value={fields.longitude} onChange={(event) => update("longitude", event.target.value)} required aria-invalid={!!error} aria-describedby={`coordinates-help${error ? " chat-error" : ""}`}/></div></div><button type="button" className="text-button" onClick={() => { setFields((previous) => ({ ...previous, latitude: String(orders[0].destination.latitude), longitude: String(orders[0].destination.longitude) })); setError(""); }}>Usar destino de ejemplo</button></>}
        {step === "review" && selected && destination && <><dl className="request-summary"><div><dt>Negocio</dt><dd>{businessName(selected.id)}</dd></div><div><dt>Pedido</dt><dd>{fields.details.trim()}</dd></div><div><dt>Origen del negocio</dt><dd>{coordinates(selected.location)}</dd></div><div><dt>Destino</dt><dd>{coordinates(destination)}</dd></div></dl><p className="form-help">Confirmar prepara una solicitud de prueba solo en esta pestaña. No envía el pedido ni calcula una cotización.</p></>}
        {error && <p id="chat-error" role="alert" className="form-error">{error}</p>}
        <div className="form-actions"><button type="button" className="button button-secondary" onClick={() => go(steps[position - 1])}>Volver</button><button type="submit" className="button button-primary">{step === "review" ? "Confirmar simulación" : "Continuar"}<Icon name={step === "review" ? "check" : "arrow"}/></button></div>
      </form>}
    </div>
  </section>;
}
