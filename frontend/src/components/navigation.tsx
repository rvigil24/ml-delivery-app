"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon, type IconName } from "./icon";

const views: { href: string; label: string; icon: IconName }[] = [
  { href: "/operaciones", label: "Operaciones", icon: "overview" },
  { href: "/cliente", label: "Cliente", icon: "chat" },
  { href: "/negocio", label: "Negocio", icon: "store" },
  { href: "/repartidor", label: "Repartidor", icon: "bike" },
];

export function Navigation() {
  const pathname = usePathname();
  return <nav aria-label="Vistas de la demostración" className="navigation">
    {views.map(({ href, label, icon }) => <Link key={href} href={href} className={`nav-link ${pathname === href ? "is-active" : ""}`} aria-current={pathname === href ? "page" : undefined}>
      <Icon name={icon}/><span>{label}</span>
    </Link>)}
  </nav>;
}
