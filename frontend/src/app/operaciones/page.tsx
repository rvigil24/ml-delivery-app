import type { Metadata } from "next";
import { Journey, PageHeading, PreviewNotice } from "@/components/workspace";
import { businessName, coordinates, orders } from "@/lib/demo-data";

export const metadata: Metadata = { title: "Operaciones" };

export default function Operations() {
  return <>
    <PageHeading title="Las entregas, en un solo lugar">Revisá los pedidos y cambiá de vista para conocer cada parte del recorrido.</PageHeading>
    <PreviewNotice/>
    <div className="work-grid"><section className="panel orders-panel" aria-labelledby="pedidos-heading">
      <div className="section-heading"><h2 id="pedidos-heading">Pedidos de muestra</h2><span className="count-label">{orders.length} pedidos</span></div>
      <div className="table-scroll"><table><caption className="sr-only">Pedidos ficticios para la exposición. No se ha consultado su estado en la API.</caption>
        <thead><tr><th scope="col">Pedido</th><th scope="col">Negocio</th><th scope="col">Destino</th><th scope="col">Estado</th></tr></thead>
        <tbody>{orders.map((order, index) => <tr key={order.id}><td><strong>Pedido {index + 1}</strong><small className="record-id">{order.id}</small></td><td>{businessName(order.business_id)}</td><td className="coordinates">{coordinates(order.destination)}</td><td><span className="status-label">Sin consultar</span></td></tr>)}</tbody>
      </table></div>
      <p className="panel-footnote">Los estados aparecerán aquí al conectar la consulta de pedidos.</p>
    </section><Journey/></div>
    <section className="section-summary"><h2>Una vista para cada paso</h2><p>El cliente solicita, el negocio confirma, el repartidor entrega y operaciones reúne la información. Usá el menú para explorar cada espacio.</p></section>
  </>;
}
