import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const base = (process.env.DELIVERY_API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
    const response = await fetch(`${base}/predict/delivery`, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requested_at: new Date().toISOString(), origin: body.origin, destination: body.destination,
        promised_minutes: body.promised_minutes ?? null }), cache: "no-store", signal: AbortSignal.timeout(15000) });
    if (!response.ok) return NextResponse.json({ message: response.status === 422
      ? "Revisá la ubicación y el plazo: debe ser mayor que cero."
      : "No pudimos obtener la estimación del modelo. Intentá de nuevo." }, { status: response.status });
    return NextResponse.json(await response.json());
  } catch { return NextResponse.json({ message: "No pudimos conectar con el modelo. Intentá de nuevo." }, { status: 503 }); }
}
