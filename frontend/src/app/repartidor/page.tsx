import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/components/icon";
import { PageHeading, PreviewNotice } from "@/components/workspace";
import { couriers } from "@/lib/demo-data";

export const metadata: Metadata = { title: "Repartidor" };

export default function Courier() {
  return <><PageHeading title="Cada entrega, paso a paso">Un espacio para consultar asignaciones y registrar la recogida y la entrega.</PageHeading><PreviewNotice/>
    <section className="panel"><div className="section-heading"><h2>Repartidores de ejemplo</h2><span className="count-label">{couriers.length} perfiles</span></div>
      <div className="table-scroll"><table><caption className="sr-only">Perfiles ficticios de repartidores; disponibilidad de ejemplo, sin consulta en vivo.</caption><thead><tr><th scope="col">Repartidor</th><th scope="col">Vehículo</th><th scope="col">Aprobación de ejemplo</th></tr></thead><tbody>{couriers.map((courier, index) => <tr key={courier.id}><td><strong>Repartidor {index + 1}</strong><small className="record-id">{courier.id}</small></td><td>{courier.vehicle === "bicicleta" ? "Bicicleta" : "Motocicleta"}</td><td>{courier.approved ? "Aprobado" : "Pendiente"}</td></tr>)}</tbody></table></div>
    </section>
    <section className="empty-state"><Icon name="location"/><h2>Las asignaciones aparecerán aquí</h2><p>La ruta y sus paradas se mostrarán cuando esté habilitada la consulta de asignaciones.</p><Link href="/operaciones" className="button button-secondary">Volver a operaciones <Icon name="arrow"/></Link></section>
  </>;
}
