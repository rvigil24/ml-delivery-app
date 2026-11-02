# SPEC — Producto y alcance

Estado: alcance MVP acordado; decisiones numéricas/comerciales pendientes. **No describe una aplicación ya implementada**.

## Problema

Muchos comedores, pupuserías y negocios de almuerzos/cenas de El Salvador no cuentan con un repartidor propio. El sistema ayuda a gestionar entregas locales dentro de una misma zona y a estimar costos para cliente, negocio, repartidor y operador. Se busca comprobar viabilidad técnica y de negocio; no se presume ROI positivo.

## Actores y vistas de la demostración

| Actor | Necesidad | Vista planificada |
|---|---|---|
| Cliente | Solicitar comida y recibir una cotización/actualización | Chat estilo WhatsApp en Next.js |
| Negocio | Recibir/confirmar pedido, marcar preparación | Panel de negocio |
| Repartidor aprobado | Ver asignación/ruta y confirmar recogida/entrega | Panel de repartidor |
| Operador | Supervisar cotizaciones, asignaciones, efectivo y márgenes | Panel de operaciones |

Los perfiles, mensajes, rutas y cobros del MVP son **simulados**. No se necesita WhatsApp Business API, pagos con tarjeta, cuenta bancaria, tracking GPS en vivo ni app móvil nativa.

## Recorrido funcional end-to-end

1. El cliente simula una solicitud de envío desde un negocio cercano.
2. Se registran origen, destino, detalles y estado del pedido; se valida que el escenario sea local.
3. El sistema calcula distancia de referencia y evalúa bicicleta/motocicleta usando reglas configurables (pendientes de acordar).
4. La predicción de duración se solicita a un modelo ML **entrenado con datos reales** cuando esté disponible. Si aún no existe un modelo válido, la API debe dejarlo claro; los ejemplos ilustrativos no se disfrazan de predicción real.
5. La cotización separa tarifa, pago del repartidor, costo variable, costos atribuibles/comisión y margen **según fórmulas aprobadas**.
6. El negocio confirma; un repartidor de una red pequeña y aprobada se asigna de forma simulada.
7. El repartidor marca recogida y entrega; se notifica al cliente por el chat de la demo.
8. Se registra el manejo de efectivo como estados contables simulados, sin transferencias ni cobros reales.
9. El operador puede comparar un escenario de una entrega contra un grupo pequeño de entregas próximas.

## Entidades mínimas (T04 define campos finales)

- **Negocio**: identificador, nombre y localización de referencia; no presupone catálogo sofisticado.
- **Pedido**: identificador, negocio, origen/destino, estado, detalles y eventos.
- **Repartidor**: identificador, modalidad (`bicicleta` o `motocicleta`), condición de aprobado y disponibilidad simulada.
- **Cotización**: distancia estimada, duración (predicción o dato ilustrativo identificado), tarifa, costos y margen; monedas/unidades explícitas.
- **Asignación/entrega**: pedido(s), repartidor, secuencia de paradas, estados de recogida y entrega.
- **Registro de efectivo**: monto previsto/estado de cobro/entrega simulada; no operación financiera real.

Para evitar inventar reglas, T04 puede modelar campos esenciales y enumeraciones sin fijar todavía tarifas ni límites logísticos.

## Estados de pedido propuestos para revisión en T03/T04

`solicitado → cotizado → confirmado → asignado → recogido → entregado`; `cancelado` solo desde estados permitidos. Estos nombres y transiciones son **propuesta**, no contrato definitivo. Deben revisarse antes de darles persistencia.

## Prioridad de producto

1. Evidencia académica: datos reales, ETL, tres ML + MLP, evaluación reproducible, FastAPI, MongoDB, S3, Docker, pruebas.
2. Flujo mínimo de negocio: pedido, cotización, asignación, entrega, efectivo simulado, costo/margen.
3. Demo visual Next.js: chat + paneles; la implementación se hará en T47–T54.
4. Despliegue AWS mediante Docker/Terraform: T41–T46 después de validar costos y permisos.

## Excluido del MVP

Marketplace de repartidores, validación automática de identidad, GPS continuo, optimización de flotas a gran escala, pagos con tarjeta, WhatsApp Business real, análisis de tráfico en vivo y modelo de combustible entrenado sin mediciones.

## Decisiones pendientes que requieren acuerdo entre ambos

- Dataset real/variable objetivo final, etiquetas, representatividad para El Salvador y vehículos.
- Región/zona de demostración y cómo obtener distancias sin GPS/tráfico vivo.
- Umbrales bicicleta/motocicleta, capacidad y seguridad.
- Reglas de agrupación, orden de paradas y asignación simulada.
- Fórmulas y parámetros de tarifas, pago al repartidor, costos fijos y margen/ROI.
- Convenciones definitivas de estados, errores y contratos REST adicionales.

No codificar constantes arbitrarias como decisiones comerciales aprobadas.
