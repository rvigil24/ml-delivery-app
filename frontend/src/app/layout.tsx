import type { Metadata } from "next";
import Link from "next/link";
import { Navigation } from "@/components/navigation";
import { Icon } from "@/components/icon";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Delivery · Entregas locales", template: "%s · Delivery" },
  description: "Demostración de entregas locales: cliente, negocio, repartidor y operaciones.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="es-SV"><body>
    <a className="skip-link" href="#contenido">Saltar al contenido</a>
    <div className="app-shell">
      <aside className="sidebar">
        <Link href="/operaciones" className="brand" aria-label="Delivery, ir a Operaciones"><span className="brand-mark"><Icon name="package"/></span><span>Delivery<small>Entregas locales</small></span></Link>
        <Navigation/>
        <div className="sidebar-note"><span className="demo-indicator"/>Demostración<p>Un recorrido.<br/>Cuatro puntos de vista.</p></div>
        <p className="sidebar-footer">Asistente de Delivery Económico</p>
      </aside>
      <div className="workspace">
        <div className="workspace-bar"><span>Espacio de entregas</span><span className="sample-label">Datos de ejemplo</span></div>
        <main id="contenido" tabIndex={-1}>{children}</main>
      </div>
    </div>
  </body></html>;
}
