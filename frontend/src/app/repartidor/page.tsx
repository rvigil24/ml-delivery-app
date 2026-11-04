import type { Metadata } from "next";
import { PageHeading } from "@/components/workspace";
import { CourierPanel } from "@/components/courier-panel";

export const metadata: Metadata = { title: "Repartidor" };

export default function Courier() {
  return <><PageHeading title="Cada entrega, paso a paso">Consultá tu ruta y registrá cada recogida y entrega en el orden indicado.</PageHeading><CourierPanel/></>;
}
