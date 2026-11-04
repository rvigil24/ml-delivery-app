import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/components/icon";
import { PageHeading } from "@/components/workspace";
import { businesses } from "@/lib/demo-data";
import { GuidedChat } from "@/components/guided-chat";

export const metadata: Metadata = { title: "Cliente" };

export default function Client() {
  return <>
    <PageHeading title="Pedí tu comida" clientLink={false}>Elegí el negocio, contanos qué querés comer y dónde querés recibirlo.</PageHeading>
    <div className="chat-grid"><GuidedChat/>
    <aside className="chat-context"><h2>Así funciona</h2><p>Pedí comida y recibila donde la necesitás.</p><ol className="simple-steps"><li>Elegí dónde querés pedir.</li><li>Indicá los platos y las cantidades.</li><li>Elegí el lugar de entrega.</li><li>Revisá y confirmá la simulación.</li></ol><p>Por ahora la solicitud queda solo en esta pestaña. El seguimiento estará disponible al conectar el sistema.</p>
      <div className="context-section"><h3>Negocios de ejemplo</h3><ul className="business-list">{businesses.map((business) => <li key={business.id}><Icon name="store"/><span>{business.name.replace(" · SIMULADO", "")}</span></li>)}</ul></div>
      <Link href="/negocio" className="text-link">Ver el lado del negocio <Icon name="arrow"/></Link>
    </aside></div>
  </>;
}
