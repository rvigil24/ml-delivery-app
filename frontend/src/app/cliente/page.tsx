import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/components/icon";
import { PageHeading } from "@/components/workspace";
import { GuidedChat } from "@/components/guided-chat";

export const metadata: Metadata = { title: "Cliente" };

export default function Client() {
  return <>
    <PageHeading title="Pedí tu comida" clientLink={false}>Indicá tu dirección, elegí un negocio y armá tu pedido.</PageHeading>
    <div className="chat-grid"><GuidedChat/>
    <aside className="chat-context"><h2>Así funciona</h2><p>Primero tu dirección, después la comida.</p><ol className="simple-steps"><li>Indicá dónde querés recibirla.</li><li>Elegí un negocio por cercanía.</li><li>Agregá productos del menú y sus cantidades.</li><li>Revisá y confirmá la simulación.</li></ol><p>Los negocios y los menús se consultan en el sistema. La confirmación todavía queda solo en esta pestaña.</p>
      <Link href="/negocio" className="text-link">Ver el lado del negocio <Icon name="arrow"/></Link>
    </aside></div>
  </>;
}
