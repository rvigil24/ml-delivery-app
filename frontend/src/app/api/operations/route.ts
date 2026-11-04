import { NextRequest, NextResponse } from "next/server";

const base = () => (process.env.DELIVERY_API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
async function forward(path: string, init?: RequestInit) {
  try {
    const response = await fetch(`${base()}${path}`, { ...init, cache: "no-store", signal: AbortSignal.timeout(15000) });
    if (!response.ok) return NextResponse.json({ message: response.status === 503
      ? "El cálculo o la consulta no están disponibles. Verificá la conexión, las tarifas y los límites configurados en la API."
      : "No se pudo completar la consulta. Revisá los datos y el estado del pedido." }, { status: response.status });
    return NextResponse.json(await response.json());
  } catch { return NextResponse.json({ message: "No pudimos conectar con la API. Intentá actualizar de nuevo." }, { status: 503 }); }
}
export async function GET() { return forward("/operations/orders?limit=100"); }
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    if (typeof body.order_id !== "string" || !body.order_id.trim()) return NextResponse.json({ message: "Seleccioná un pedido." }, { status: 422 });
    return forward(`/orders/${encodeURIComponent(body.order_id)}/quotes`, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quote_id: `preview-${crypto.randomUUID()}`, load_kg: body.load_kg, costs: body.costs }) });
  } catch { return NextResponse.json({ message: "Datos inválidos." }, { status: 422 }); }
}
