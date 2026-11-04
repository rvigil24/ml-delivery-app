import test from "node:test";
import assert from "node:assert/strict";
import { businessActions, validBusinessAction } from "../src/lib/business-orders.ts";

test("el negocio confirma sólo cotizados y no modifica pedidos asignados o terminales", () => {
  assert.deepEqual(businessActions("cotizado"), ["confirmado", "cancelado"]);
  assert.deepEqual(businessActions("solicitado"), ["cancelado"]);
  for (const state of ["asignado", "recogido", "entregado", "cancelado"]) assert.deepEqual(businessActions(state), []);
  const body = { order_id: "fixture-order", business_id: "fixture-business", expected: "cotizado", target: "confirmado" };
  assert(validBusinessAction(body));
  assert(!validBusinessAction({ ...body, expected: "solicitado" }));
  assert(!validBusinessAction({ ...body, business_id: "" }));
  assert(!validBusinessAction({ ...body, target: "entregado" }));
  assert(!validBusinessAction({ ...body, expected: "__proto__" }));
});
