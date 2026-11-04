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

## Estados de pedido — base aprobada para T20

Ruben aprobó el 2026-11-03 el flujo
`solicitado → cotizado → confirmado → asignado → recogido → entregado`.
Solo se cancela desde `solicitado`, `cotizado` o `confirmado`; `entregado` y
`cancelado` son terminales. Saltos, retrocesos y cambios repetidos se rechazan
sin cambiar el pedido ni añadir eventos. El cliente debe consultar el estado
actual antes de reintentar una operación rechazada.

Los avances exigen validación de cotización/asignación y contexto correspondiente.
En T20, sin ese validador, se rechazan; no se inventan cotizaciones, tarifas ni
asignaciones para habilitarlos. Registro/consulta e historial UTC funcionan con
almacenamiento local en memoria; MongoDB se integra en T32. Registrar una solicitud
no constituye una cotización ni acredita cobertura local: la validación del área
de servicio sigue dependiendo de la configuración por concretar en T21/T23.

## Base académica aprobada para estimaciones T21

Ruben aprobó usar Haversine como distancia aproximada por círculo máximo,
sin rutas por calles, y el modelo T19 como duración experimental. El resultado
es un borrador académico sin importes ni cambio de estado. La distancia no se
convierte a minutos mediante una velocidad inventada: el modelo solo recibe
hora/día UTC de creación y predice creación–entrega, no tiempo de conducción.
No distingue vehículos ni está validado para El Salvador.

La cobertura local queda explícitamente sin validar; no se inventan zonas o
límites máximos. El borrador no habilita una cotización comercial ni sustituye
los requisitos de T20. Tarifas, cobertura y reglas logísticas siguen pendientes.

## Prioridad de producto

1. Evidencia académica: datos reales, ETL, tres ML + MLP, evaluación reproducible, FastAPI, MongoDB, S3, Docker, pruebas.
2. Flujo mínimo de negocio: pedido, cotización, asignación, entrega, efectivo simulado, costo/margen.
3. Demo visual Next.js: chat + paneles; la implementación se hará en T47–T54.
4. Despliegue AWS mediante Docker/Terraform: T41–T46 después de validar costos y permisos.

## Excluido del MVP

Marketplace de repartidores, validación automática de identidad, GPS continuo, optimización de flotas a gran escala, pagos con tarjeta, WhatsApp Business real, análisis de tráfico en vivo y modelo de combustible entrenado sin mediciones.

## Decisiones pendientes que requieren acuerdo entre ambos

- Dataset real/variable objetivo final, etiquetas, representatividad para El Salvador y vehículos.
- Región/zona de demostración y método vial/comercial; Haversine de referencia académica ya fue aprobado en T21.
- Umbrales bicicleta/motocicleta, capacidad y seguridad.
- Reglas de agrupación, orden de paradas y asignación simulada.
- Fórmulas y parámetros de tarifas, pago al repartidor, costos fijos y margen/ROI.
- Integración de requisitos, recotización, errores y contratos REST adicionales; la matriz básica T20 ya fue aprobada.

No codificar constantes arbitrarias como decisiones comerciales aprobadas.
