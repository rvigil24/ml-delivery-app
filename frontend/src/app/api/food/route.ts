import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const base = (process.env.DELIVERY_API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
    const response = await fetch(`${base}/food/orders`, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body), cache: "no-store", signal: AbortSignal.timeout(15000) });
    if (!response.ok) return NextResponse.json({ message: response.status === 409
      ? "La referencia ya tiene otro contenido. Revisá el pedido antes de continuar."
      : response.status === 422 ? "Revisá los productos, las cantidades y la dirección."
      : "No pudimos confirmar el registro. Intentá de nuevo; conservaremos la misma referencia." }, { status: response.status });
    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json({ message: "No pudimos confirmar el registro. Intentá de nuevo; conservaremos la misma referencia." }, { status: 503 });
  }
}

export async function GET(request: NextRequest) {
  const query = request.nextUrl.searchParams;
  const base = (process.env.DELIVERY_API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
  let path: string;
  if (query.get("operation") === "order" && query.get("order_id")) {
    path = `/orders/${encodeURIComponent(query.get("order_id")!)}`;
  } else if (query.get("operation") === "nearby") {
    const params = new URLSearchParams({ latitude: query.get("latitude") || "", longitude: query.get("longitude") || "" });
    path = `/businesses/nearby?${params}`;
  } else if (query.get("operation") === "menu" && query.get("business_id")) {
    path = `/businesses/${encodeURIComponent(query.get("business_id")!)}/menu`;
  } else return NextResponse.json({ message: "Consulta de comida inválida." }, { status: 400 });
  try {
    const response = await fetch(base + path, { cache: "no-store", signal: AbortSignal.timeout(10000) });
    if (!response.ok) return NextResponse.json({ message: "No pudimos consultar los negocios o su menú. Intentá de nuevo." }, { status: response.status });
    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json({ message: "No pudimos conectar con el servicio de pedidos. Intentá de nuevo." }, { status: 503 });
  }
}
