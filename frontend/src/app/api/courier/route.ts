import { NextRequest, NextResponse } from "next/server";
import { validCourierAction } from "@/lib/courier-routes";

const base = () => (process.env.DELIVERY_API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
function error(status: number) {
  const message = status === 409 ? "La ruta cambió o el avance no corresponde a la siguiente parada. Actualizá antes de intentar de nuevo."
    : status === 404 ? "No encontramos al repartidor o su asignación. Actualizá la lista."
    : status === 400 || status === 422 ? "Los datos del avance no son válidos. Actualizá la ruta."
    : "No pudimos conectar con el servicio de entregas. Intentá de nuevo.";
  return NextResponse.json({ message }, { status });
}

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  let path: string;
  if (params.get("operation") === "couriers") path = "/couriers?limit=100";
  else if (params.get("operation") === "assignments" && params.get("courier_id")) path = `/couriers/${encodeURIComponent(params.get("courier_id")!)}/assignments?limit=100`;
  else return error(400);
  try {
    const response = await fetch(base() + path, { cache: "no-store", signal: AbortSignal.timeout(10000) });
    return response.ok ? NextResponse.json(await response.json()) : error(response.status);
  } catch { return error(503); }
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try { body = await request.json(); } catch { return error(400); }
  if (!validCourierAction(body)) return error(400);
  const path = `/couriers/${encodeURIComponent(body.courier_id)}/assignments/${encodeURIComponent(body.assignment_id)}/${body.action}`;
  try {
    const response = await fetch(base() + path, { method: "POST", headers: { "Content-Type": "application/json" }, signal: AbortSignal.timeout(10000),
      body: body.action === "progress" ? JSON.stringify({ order_id: body.order_id, expected: body.expected, target: body.target }) : undefined });
    return response.ok ? NextResponse.json(await response.json()) : error(response.status);
  } catch { return error(503); }
}
