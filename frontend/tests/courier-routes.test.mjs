import test from "node:test";
import assert from "node:assert/strict";
import { nextCourierStop, canFinishRoute, validCourierAction } from "../src/lib/courier-routes.ts";

test("sólo se avanza la siguiente parada y se finaliza tras todas las entregas", () => {
  const record = { order: { id: "fixture-order", status: "asignado" }, events: [] };
  const route = { active: true, orders: [record], stops: [{ order_id: "fixture-order", kind: "recogida" }, { order_id: "fixture-order", kind: "entrega" }] };
  assert.equal(nextCourierStop(route).target, "recogido");
  assert(!canFinishRoute(route));
  record.order.status = "recogido";
  assert.equal(nextCourierStop(route).target, "entregado");
  record.order.status = "entregado";
  assert.equal(nextCourierStop(route), null);
  assert(canFinishRoute(route));
  assert(!canFinishRoute({ ...route, orders: [] }));
  assert(!canFinishRoute({ ...route, active: false }));
  const body = { courier_id: "fixture-courier", assignment_id: "fixture-route", action: "progress", order_id: "fixture-order", expected: "asignado", target: "recogido" };
  assert(validCourierAction(body));
  assert(!validCourierAction({ ...body, target: "entregado" }));
  assert(!validCourierAction({ ...body, courier_id: "" }));
});
