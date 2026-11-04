import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/components/icon";
import { PageHeading, PreviewNotice } from "@/components/workspace";
import { businesses, coordinates, orders } from "@/lib/demo-data";

export const metadata: Metadata = { title: "Negocio" };

export default function Business() {
  return <><PageHeading title="El espacio de tu negocio">Consultá los pedidos del negocio y los datos necesarios para preparar cada entrega.</PageHeading><PreviewNotice/>
    <section className="panel"><div className="section-heading"><h2>Negocios de ejemplo</h2><span className="count-label">{businesses.length} negocios</span></div>
      <ul className="business-directory">{businesses.map((business) => <li key={business.id}><span className="directory-icon"><Icon name="store"/></span><div><h3>{business.name.replace(" · SIMULADO", "")}</h3><p>Ubicación de referencia: <span className="coordinates">{coordinates(business.location)}</span></p></div><span className="directory-count">{orders.filter((order) => order.business_id === business.id).length} pedido de muestra</span></li>)}</ul>
    </section>
    <section className="empty-state"><Icon name="package"/><h2>El seguimiento de pedidos va aquí</h2><p>Este espacio reunirá el detalle del pedido y las acciones para confirmar y actualizar su estado.</p><Link href="/operaciones" className="button button-secondary">Ver pedidos de muestra <Icon name="arrow"/></Link></section>
  </>;
}
