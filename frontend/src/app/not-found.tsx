import Link from "next/link";

export default function NotFound() {
  return <section className="empty-state"><h1>No encontramos esta página</h1><p>Podés volver al espacio de entregas y elegir una vista desde el menú.</p><Link href="/operaciones" className="button button-primary">Ir a Operaciones</Link></section>;
}
