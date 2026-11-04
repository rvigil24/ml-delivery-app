import Link from "next/link";
import { Icon } from "./icon";

export function PageHeading({ title, children, clientLink = true }: { title: string; children: React.ReactNode; clientLink?: boolean }) {
  return <header className="page-heading"><div><h1>{title}</h1><p>{children}</p></div>
    {clientLink && <Link href="/cliente" className="button button-primary">Ver como cliente <Icon name="arrow"/></Link>}
  </header>;
}

export function Journey() {
  return <aside className="journey"><h2>De la solicitud a la entrega</h2><p>Cada vista participa en el mismo recorrido.</p>
    <ol>{[
      ["Solicitud", "El cliente indica qué necesita y dónde recibirlo."],
      ["Cotización y confirmación", "Se revisan el costo, la estimación y las condiciones."],
      ["Asignación y recogida", "Un repartidor aprobado recibe la entrega."],
      ["Entrega y efectivo", "Se registra la entrega y el manejo del efectivo."],
    ].map(([title, text]) => <li key={title}><span className="journey-dot"/><div><strong>{title}</strong><p>{text}</p></div></li>)}</ol>
    <Link href="/cliente" className="text-link">Explorar la vista del cliente <Icon name="arrow"/></Link>
  </aside>;
}

export function PreviewNotice() {
  return <div className="preview-notice"><Icon name="package"/><p><strong>Datos de ejemplo.</strong> Los pedidos de esta vista todavía no se pueden consultar ni modificar.</p></div>;
}
