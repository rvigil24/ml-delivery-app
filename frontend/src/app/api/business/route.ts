import { NextRequest, NextResponse } from "next/server";
import { validBusinessAction } from "@/lib/business-orders";

const base = () => (process.env.DELIVERY_API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");

function error(status: number) {
  const message = status === 409 ? "El pedido cambió o todavía no cumple los requisitos para avanzar. Actualizá su estado y revisá la cotización."
    : status === 404 ? "No encontramos ese negocio o pedido. Actualizá la lista."
    : status === 422 || status === 400 ? "Los datos del cambio no son válidos. Actualizá el pedido e intentá de nuevo."
    : "No pudimos conectar con el servicio de pedidos. Intentá de nuevo.";
  return NextResponse.json({ message }, { status });
}

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;
  const operation = params.get("operation");
  let path: string;
  if (operation === "businesses") path = "/businesses?limit=100";
  else if (operation === "orders" && params.get("business_id")) path = `/orders?${new URLSearchParams({ business_id: params.get("business_id")!, limit: "100" })}`;
  else return error(400);
  try {
    const response = await fetch(base() + path, { cache: "no-store", signal: AbortSignal.timeout(10000) });
    return response.ok ? NextResponse.json(await response.json()) : error(response.status);
  } catch { return error(503); }
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try { body = await request.json(); } catch { return error(400); }
  if (!validBusinessAction(body)) return error(400);
  try {
    const url = `${base()}/orders/${encodeURIComponent(body.order_id)}`;
    const current = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(10000) });
    if (!current.ok) return error(current.status);
    if ((await current.json()).order.business_id !== body.business_id) return error(409);
    const response = await fetch(url + "/transitions", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expected: body.expected, target: body.target }),
      signal: AbortSignal.timeout(10000),
    });
    return response.ok ? NextResponse.json(await response.json()) : error(response.status);
  } catch { return error(503); }
}
