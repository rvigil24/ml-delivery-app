export type Point = { latitude: number; longitude: number };
export type BusinessChoice = { id: string; name: string; location: Point };
export type RequestFields = { businessId: string; details: string; latitude: string; longitude: string };
export type LocalRequest = {
  id: string;
  business_id: string;
  origin: Point;
  destination: Point;
  details: string;
};

export type FoodProduct = { id: string; business_id: string; name: string; description: string; price: string | null; currency: string | null };
export type SelectedItem = { product_id: string; name: string; quantity: number };

export function selectedItems(products: readonly FoodProduct[], quantities: Record<string, number>, businessId: string): SelectedItem[] {
  const items: SelectedItem[] = [];
  for (const [id, quantity] of Object.entries(quantities)) {
    if (!Number.isSafeInteger(quantity) || quantity < 0) throw new Error("Revisá las cantidades del pedido.");
    if (!quantity) continue;
    const product = products.find((item) => item.id === id && item.business_id === businessId);
    if (!product) throw new Error("Un producto no pertenece al menú del negocio.");
    items.push({ product_id: product.id, name: product.name, quantity });
  }
  if (!items.length) throw new Error("Elegí al menos un producto del menú.");
  return items;
}

export function readDestination(latitude: string, longitude: string): Point | null {
  // No convertir una cadena vacía en 0 ni aceptar formatos no decimales.
  const decimal = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/;
  if (!decimal.test(latitude.trim()) || !decimal.test(longitude.trim())) return null;
  const lat = Number(latitude);
  const lon = Number(longitude);
  return Number.isFinite(lat) && Number.isFinite(lon) && Math.abs(lat) <= 90 && Math.abs(lon) <= 180
    ? { latitude: lat, longitude: lon } : null;
}

export function createLocalRequest(fields: RequestFields, businesses: readonly BusinessChoice[], id: string): LocalRequest {
  const business = businesses.find((item) => item.id === fields.businessId);
  const destination = readDestination(fields.latitude, fields.longitude);
  if (!business || !fields.details.trim() || !destination || !id.startsWith("demo-chat-")) {
    throw new Error("Revisá el negocio, el detalle del pedido y las coordenadas del destino.");
  }
  return { id, business_id: business.id, origin: { ...business.location }, destination, details: fields.details.trim() };
}
