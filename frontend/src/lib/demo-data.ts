import fixtures from "../../../examples/exposicion.json";

// Solo fixtures de exposición; nunca representan una lectura de Atlas.
export const businesses = fixtures.businesses;
export const orders = fixtures.orders;
export const couriers = fixtures.couriers;

export function businessName(id: string) {
  return businesses.find((business) => business.id === id)?.name.replace(" · SIMULADO", "") ?? id;
}

export function coordinates(point: { latitude: number; longitude: number }) {
  return `${point.latitude.toFixed(4)}, ${point.longitude.toFixed(4)}`;
}
