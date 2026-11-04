import type { Metadata } from "next";
import { PageHeading } from "@/components/workspace";
import { OperationsPanel } from "@/components/operations-panel";

export const metadata: Metadata = { title: "Operaciones" };
export default function Operations() {
  return <><PageHeading title="Las entregas, en un solo lugar">Consultá los pedidos, el efectivo y el desglose de cada entrega.</PageHeading><OperationsPanel/></>;
}
