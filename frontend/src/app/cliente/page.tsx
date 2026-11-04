import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/components/icon";
import { PageHeading } from "@/components/workspace";
import { businesses } from "@/lib/demo-data";

export const metadata: Metadata = { title: "Cliente" };

export default function Client() {
  return <>
    <PageHeading title="Tu entrega comienza con un mensaje" clientLink={false}>Una conversación guiada para solicitar y seguir un envío.</PageHeading>
    <div className="chat-grid"><section className="chat-window" aria-label="Vista previa de una conversación de WhatsApp">
      <header className="chat-header"><span className="contact-avatar"><Icon name="package"/></span><div><h2>Asistente de Delivery</h2><p>Simulación de WhatsApp</p></div><span className="preview-label">Vista previa</span></header>
      <div className="chat-messages"><p className="chat-notice">Esta pantalla representa WhatsApp. No envía mensajes reales.</p>
        <p className="chat-date">Conversación de ejemplo</p>
        <div className="message incoming"><p>¡Hola! Te ayudo a solicitar una entrega. Primero elegí el negocio desde el que querés enviar tu pedido.</p><span className="message-sender">Asistente</span></div>
        <div className="message outgoing"><p>Quiero solicitar un envío.</p><span className="message-sender">Cliente <Icon name="check"/></span></div>
        <div className="message incoming"><p>Después indicaremos el detalle del pedido y el destino. Antes de confirmar podrás revisar la estimación y el costo.</p><span className="message-sender">Asistente</span></div>
      </div>
      <div className="chat-compose"><label className="sr-only" htmlFor="message-preview">Mensaje, disponible al habilitar las solicitudes</label><input id="message-preview" disabled placeholder="Vista previa del chat" aria-describedby="chat-disabled-help"/><button className="send-button" type="button" disabled aria-label="Enviar mensaje, no disponible en la vista previa"><Icon name="send"/></button></div>
      <p id="chat-disabled-help" className="compose-help">La solicitud guiada todavía no está habilitada.</p>
    </section>
    <aside className="chat-context"><h2>Así funciona</h2><p>Vos indicás qué necesitás. El asistente te guía paso a paso.</p><ol className="simple-steps"><li>Elegí el negocio.</li><li>Indicá el pedido y su destino.</li><li>Revisá y confirmá.</li><li>Consultá cómo va la entrega.</li></ol>
      <div className="context-section"><h3>Negocios de ejemplo</h3><ul className="business-list">{businesses.map((business) => <li key={business.id}><Icon name="store"/><span>{business.name.replace(" · SIMULADO", "")}</span></li>)}</ul></div>
      <Link href="/negocio" className="text-link">Ver el lado del negocio <Icon name="arrow"/></Link>
    </aside></div>
  </>;
}
