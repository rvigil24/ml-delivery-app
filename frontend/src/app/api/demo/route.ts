import { NextRequest, NextResponse } from "next/server";
import individual from "../../../../../examples/demo_delivery.json";
import grouped from "../../../../../examples/demo_grouped_delivery.json";

export async function POST(request: NextRequest) {
  try {
    const { scenario } = await request.json();
    if (scenario !== "individual" && scenario !== "grouped") return NextResponse.json({ message: "Escenario inválido." }, { status: 422 });
    const prefix = `demo-expo-${crypto.randomUUID()}`;
    const payload = structuredClone(scenario === "individual" ? individual : grouped) as Record<string, any>;
    payload.business.id = `${prefix}-business`;
    payload.business.name = scenario === "individual" ? "Comedor SIMULADO · entrega individual" : "Comedor SIMULADO · entrega agrupada";
    payload.courier.id = `${prefix}-courier`;
    if (scenario === "individual") {
      payload.order.id = `${prefix}-order`;
      payload.order.business_id = payload.business.id;
      payload.order.details = "1 × Almuerzo de pollo · SIMULADO, no preparar comida real";
    } else {
      const costs: Record<string, unknown> = {}, loads: Record<string, unknown> = {};
      payload.orders.forEach((order: { id: string; business_id: string }, index: number) => {
        const old = order.id; order.id = `${prefix}-order-${index + 1}`; order.business_id = payload.business.id;
        costs[order.id] = payload.per_order_costs[old]; loads[order.id] = payload.loads_kg[old];
      });
      payload.per_order_costs = costs; payload.loads_kg = loads;
    }
    const base = (process.env.DELIVERY_API_URL || "http://127.0.0.1:8001").replace(/\/$/, "");
    const response = await fetch(`${base}/demo/${scenario === "individual" ? "deliveries" : "group-deliveries"}`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), cache: "no-store", signal: AbortSignal.timeout(120000),
    });
    if (!response.ok) return NextResponse.json({ message: response.status === 404 ? "La demo está deshabilitada. Iniciá la API con DELIVERY_DEMO_ENABLED=1."
      : "No se pudo completar la demo. Puede haber pasos guardados; revisá Operaciones antes de iniciar otra ejecución." }, { status: response.status });
    return NextResponse.json({ scenario, input: payload, result: await response.json() });
  } catch { return NextResponse.json({ message: "No pudimos confirmar el resultado. Puede haber pasos guardados; revisá Operaciones antes de iniciar otra ejecución." }, { status: 503 }); }
}
