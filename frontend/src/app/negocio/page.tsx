import type { Metadata } from "next";
import { PageHeading } from "@/components/workspace";
import { BusinessPanel } from "@/components/business-panel";

export const metadata: Metadata = { title: "Negocio" };

export default function Business() {
  return <><PageHeading title="Pedidos de tu negocio">Consultá los pedidos registrados, revisá sus indicaciones y actualizá su estado.</PageHeading><BusinessPanel/></>;
}
