import assert from "node:assert/strict";
import test from "node:test";
import { createLocalRequest, readDestination } from "../src/lib/request-draft.ts";

test("las coordenadas vacías, no decimales o fuera de rango no son un destino válido", () => {
  for (const [latitude, longitude] of [["", ""], [" ", "-89"], ["abc", "0"], ["91", "0"], ["0", "-181"], ["Infinity", "0"], ["0x10", "0"], ["13,7", "-89"]]) {
    assert.equal(readDestination(latitude, longitude), null);
  }
  assert.deepEqual(readDestination("0", "0"), { latitude: 0, longitude: 0 });
  assert.deepEqual(readDestination("-90", "180"), { latitude: -90, longitude: 180 });
});

test("la solicitud conserva negocio, origen y destino explícitos y rechaza datos incompletos", () => {
  const businesses = [{ id: "fixture-business", name: "Fixture", location: { latitude: 13, longitude: -89 } }];
  const fields = { businessId: "fixture-business", details: "  Pedido de prueba  ", latitude: "13.7", longitude: "-89.2" };
  const result = createLocalRequest(fields, businesses, "demo-chat-fixture");
  assert.deepEqual(result, { id: "demo-chat-fixture", business_id: "fixture-business", origin: { latitude: 13, longitude: -89 }, destination: { latitude: 13.7, longitude: -89.2 }, details: "Pedido de prueba" });
  assert.notEqual(result.origin, businesses[0].location);
  for (const invalid of [{ ...fields, details: "  " }, { ...fields, businessId: "missing" }, { ...fields, latitude: "" }]) {
    assert.throws(() => createLocalRequest(invalid, businesses, "demo-chat-fixture"));
  }
});
