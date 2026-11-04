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

## Cálculo académico de importes — reglas aprobadas T22

Ruben aprobó fórmulas configurables sin importes comerciales predeterminados:

- Tarifa = base cliente + precio por km × distancia.
- Pago repartidor = base repartidor + pago por km × distancia.
- Margen = tarifa − pago repartidor − costo variable − costo atribuible.

Moneda, unidad monetaria y todos los valores son explícitos. Los costos se
suministran por envío y son del operador, sin duplicar lo ya incluido en el pago
al repartidor. No se deducen combustible, comisiones o salarios automáticamente.
Se usa Decimal y ROUND_HALF_UP: cada componente se redondea primero y el margen
se obtiene de esos importes finales para que el desglose concilie. Se permite
margen negativo. Ausencia de configuración/costos falla; cero solo es un valor
válido cuando se proporciona explícitamente.

T22 devuelve un desglose académico separado: no modifica el borrador T21, no
emite cotización, no cobra ni cambia estados. Cobertura y precios concretos
siguen pendientes. La duración experimental no determina ninguna tarifa.

## Vehículos — reglas configurables aprobadas T23

Ruben aprobó máximos explícitos de distancia en km y carga en kg para bicicleta
y motocicleta, una zona rectangular que incluya origen y destino y límites
inclusivos (≤). No se fijan valores reales por defecto. Los máximos/cargas deben
ser Decimal finitos positivos y ambos vehículos deben tener configuración.

La evaluación devuelve todas las opciones permitidas y los motivos de rechazo,
sin preferir bicicleta, suponer moto siempre válida o asignar repartidor.
Se rechaza cada vehículo si un extremo queda fuera de zona o supera su máximo
de distancia/carga. Las esquinas de la zona se suministran en grados; no cruza
el antimeridiano y sus bordes se incluyen. Es una regla de simulación, no una
delimitación administrativa o comprobación de rutas por calles.

No cambia precios, tiempo ML, pedido o historial. Cumplir la zona configurada
no modifica el borrador académico T21 ni acredita cobertura comercial. T26
comprobará estado del pedido, aprobación/disponibilidad del repartidor y
asignación; T23 evalúa tipos de vehículo, sin reservarlos.

## Sugerencia de rutas — base académica aprobada T24

Ruben aprobó planificar pedidos elegidos explícitamente y un punto inicial,
con ruta abierta por vecino más cercano usando Haversine. Cada entrega requiere
haber recogido antes su propio pedido; se desempata por ID en distancias iguales.
No se añade regreso automático al inicio ni se eligen pedidos para agrupar.

Máximo de pedidos y zona rectangular T23 son configuración explícita, sin
valores predeterminados. Inicio, recogidas y entregas deben estar dentro. Se
rechazan grupos vacíos, duplicados, exceso del máximo y pedidos ya asignados,
recogidos, entregados o cancelados. No se omiten pedidos inválidos silenciosamente.

Es una sugerencia académica, sin garantía de óptimo, capacidad, ventanas de
tiempo o recorrido vial. No asigna, reserva, cambia estados, calcula costos ni
altera tiempos ML. La viabilidad logística y asignación siguen en T26.

## Comparación de costos — supuestos académicos aprobados T25

Ruben aprobó comparar solo costos del operador: pago al repartidor + costo
variable + atribuible, con los mismos pedidos/snapshots, inicio, política T22
y moneda. Cada individual es un recorrido independiente desde ese inicio;
el grupo es un solo recorrido T24. Una base de pago se aplica por recorrido,
no por pedido dentro del grupo. Los costos de cada individual y del grupo son
entradas explícitas; no se deducen descuentos, costos cero o economías de escala.

Se usan rutas abiertas sin retorno/reposicionamiento final y con extremos finales
posiblemente distintos. No se simula que un mismo repartidor vuelva gratis al
inicio entre individuales: son recorridos independientes, sin comprobar recursos
disponibles. La distancia para pago incluye todos los tramos planificados desde
el inicio, incluida aproximación a recogidas.

Se muestra individual menos agrupado con signo, sin asumir ahorro ni recomendar
automáticamente agrupar. No se comparan tarifas al cliente, ingresos, margen o
ROI. Capacidad, tiempos y viabilidad vial siguen sin validar; no cambia estados,
reserva o asigna pedidos. Es una comparación de supuestos, no rentabilidad medida.

## Asignación de repartidores — base simulada aprobada T26

Ruben aprobó seleccionar un repartidor por ID y exigir aprobación,
disponibilidad y pedidos confirmados con cotización validada por una fuente
explícita. No se usa el borrador académico como autorización comercial.
Sin validador, la asignación queda bloqueada.

Inicio, grupo, cargas en kg y políticas de zona/distancia/capacidad son entradas
explícitas. Se usa la ruta T24, con límites T23 del vehículo elegido aplicados
a toda su distancia y a la carga máxima acumulada entre paradas; se acepta
igualdad con los límites. Se conserva la secuencia al recoger/entregar para
mantener esa comprobación. No se inventan coordenadas del repartidor, velocidades
ni límites reales; Haversine sigue sin representar calles o tiempos viales.

La reserva del grupo y la ocupación del repartidor son atómicas en memoria:
un cambio concurrente o reintento duplicado falla sin asignaciones parciales.
La liberación es explícita y solo se permite tras entregar todos los pedidos,
sin generar entregas ni pagos implícitos. Se conserva registro inmutable con
políticas, ruta, cargas, pico de carga y fechas UTC. La garantía es local a un
proceso; MongoDB y los canales/mensajes continúan en tareas posteriores.

## Solicitudes y mensajes simulados — T27

La solicitud del chat es estructurada: ID, negocio, origen/destino y detalles
del pedido T04; se registra mediante T20, sin interpretar lenguaje natural.
Se devuelve una conversación inmutable con el texto de los detalles como mensaje
del cliente, un acuse de registro y actualizaciones derivadas exclusivamente de
los cambios de estado aceptados. Cada mensaje usa la fecha UTC del evento.
Consultar de nuevo no crea mensajes ni estados adicionales; un rechazo no se
presenta como operación exitosa.

Es una vista reconstruida y marcada como simulación, incluso para pedidos que
se registraron por otros medios: no acredita envío, recepción o canal original.
El acuse inicial indica cotización/cobertura pendientes y no promete tarifa,
duración, asignación o cobro. Se conservan los requisitos T20/T26; el chat no los
autoriza ni los omite. No hay WhatsApp Business, teléfonos, tokens o mensajes
externos. La interfaz visual, HTTP y sincronización siguen en T48/T30/T53.

## Efectivo — base simulada aprobada T28

Ruben aprobó registrar únicamente el importe del envío de una cotización
validada, con moneda explícita: `pendiente → cobrado → entregado_al_operador`.
El registro de cobro se permite después de entregar el pedido y por el importe
completo, igual que la entrega al operador. Se excluyen comida, pagos parciales,
devoluciones, cambio y deducciones automáticas de remuneración del repartidor.
No se vuelve a calcular ni redondear la tarifa; se preservan sus términos.

Una expectativa por pedido e historial UTC inmutable, con actualizaciones
condicionales atómicas en memoria. Duplicados, saltos, retrocesos, moneda/monto
incorrectos o fechas anteriores al historial no escriben. Se conserva separado
del estado logístico: entregar no implica cobrar, y cobrar/remitir no cambia
pedidos ni libera repartidores. Un pedido cancelado no puede abrir efectivo;
si se cancela con una expectativa pendiente, no se puede cobrar ni se fabrica
un reembolso. Sin fuente de cotización validada se bloquea la apertura.
Son registros ficticios para la demo; persistencia y análisis financiero
conservan sus alcances posteriores T32/T29.

## Análisis financiero — escenario académico aprobado T29

Ruben aprobó una proyección homogénea por período con volumen, moneda,
desglose unitario T22, costos fijos adicionales e inversión explícitos.
Resultado = volumen × margen unitario − costos fijos; estos excluyen costos
ya incluidos por envío. Se preservan importes unitarios conciliados, con una
unidad monetaria explícita, sin asignar valores comerciales predeterminados.

El punto de equilibrio es el menor volumen entero no negativo con resultado
≥ 0: techo de costos fijos/margen positivo; no existe con costos fijos positivos
y margen ≤ 0. Si no hay costos fijos, el mínimo es cero, incluso si un margen
negativo hace perder dinero al aumentar volumen. ROI simple del período (%) =
resultado/inversión × 100; inversión cero produce resultado no calculable.
No anualizar ni restar la inversión nuevamente como gasto operativo.

Se muestran ingresos/costos agregados, contribución y resultado, también si son
negativos. Los agregados monetarios no admiten pérdida de precisión; ROI usa
aproximación Decimal de 28 dígitos ROUND_HALF_UP cuando sea necesaria. El escenario
es académico, sin demanda/capacidad validadas, datos comerciales observados o
rentabilidad garantizada. No deriva volumen del dataset ML, mezcla costos de
otros escenarios ni cuenta efectivo T28 como ingreso adicional; no modifica estados.

## API de inferencia — T30

API FastAPI local con health, predict y documentación OpenAPI. La solicitud
contiene únicamente la creación del pedido con zona horaria (`requested_at`),
normalizada a UTC; el predictor T19/T21 usa hora/día UTC. La respuesta informa
minutos, versión/procedencia, definición creación–entrega y límites académicos,
sin tarifa, diferencias entre vehículos o validación local acreditadas.

El modelo se carga una vez al arrancar desde un directorio configurado de un
bundle propio, sin entrenamiento o descarga. Health informa proceso y carga
inicial; no representa estado de MongoDB/S3. Entradas inválidas devuelven 422,
ausencia/incompatibilidad o fallo conocido de predicción 503, y errores
inesperados 500 sin detalles internos. Esquemas/códigos en ARCHITECTURE y OpenAPI.
T30 no conecta cotización comercial, almacenamiento, canales o despliegues.

## Integración del motor de cotizaciones — T31

La previsualización académica combina duración T19/T21, importes T22 y reglas
de vehículos T23 sobre un snapshot de pedido solicitado. Requiere políticas y
costos explícitos, conserva versiones/contexto y usa la fecha de creación
guardada. Se reutiliza el modelo de la API, sin recargar, entrenar o convertir
distancia en duración. No predice diferencias entre vehículos.

Se expone mediante POST /orders/{order_id}/quotes con quote_id, carga y costos;
el cliente no provee fecha o tarifas para sustituir las configuradas. Sin
repositorio/políticas se bloquea con 503; un pedido ausente produce 404 y un
estado incompatible 409. MongoDB/CRUD permanecen en T32; no se cargan pedidos
o reglas ilustrativas automáticamente en la aplicación.

El resultado siempre es académico, con cobertura y cotización comercial sin
validar. Incluye decisiones para ambos vehículos, incluso ninguno admisible;
no elige, asigna, reserva, persiste cotizaciones o cambia el pedido/historial.
Los valores de demostración se identifican como fixtures. Una previsualización
con importes no sustituye la fuente autoritativa requerida por T20/T26/T28.

## Persistencia operativa — T32

MongoDB Atlas Free sobre AWS us-east-1 es el servicio elegido. Tras desarrollar
y probar localmente, Ruben creó el clúster; conexión, esquema, transacción y
lecturas de la API en Atlas se verificaron. Persisten negocios, pedidos/historial, repartidores,
asignaciones y efectivo simulado; el entrenamiento y los archivos siguen fuera
de la base operacional. URI/base explícitas y privadas, sin datos prefijados.

CRUD de catálogos y creación/consulta/listado/transiciones de pedidos por API.
No se cambia un estado mediante edición genérica ni se borra su historial;
se conservan las restricciones de referencias y repartidores ocupados.
Validadores e índices se preparan de forma explícita; la API comprueba su
existencia antes de usar la persistencia. Actualizaciones condicionales y
transacciones preservan atomicidad y rechazos sin cambios parciales.
La indisponibilidad produce 503, sin sustituir MongoDB por memoria.

Guardar datos no valida cotizaciones, cobertura o importes comerciales:
T20/T26/T28 mantienen sus requisitos y T31 su alcance académico. No se crean
recursos cloud, pagos reales o permisos de producción como parte de la prueba local.

## Almacenamiento de objetos — T33

S3 ml-kodigo-resources en us-east-1 almacena copias privadas autorizadas de
artefactos académicos, sin recrear bucket o modificar IAM/políticas. Modelo,
documentación y metadatos se versionan y verifican por SHA-256/tamaño. Una
clave existente con bytes distintos no se sobrescribe. Los CSV Meituan siguen
locales; datasets declara disponibilidad exclusiva de metadatos/licencia.
La API recupera opcionalmente un bundle propio al inicio con manifiesto fijado
por hash/tamaño, conserva los controles T19 y limpia su caché al terminar.
Fallos mantienen inferencia 503, sin entrenamiento o descarga por petición.
Credenciales fuera de Git/frontend; sin despliegue o uso comercial habilitado.

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
- Valores reales de límites/capacidades y seguridad; los criterios configurables T23 ya fueron aprobados.
- Viabilidad operativa y persistencia de agrupaciones; T24 y la reserva/carga simuladas T26 ya fueron aprobadas.
- Valores reales de tarifas, costos, demanda e inversión y reglas adicionales de combustible/comisiones; las fórmulas configurables T22 y el escenario financiero T29 ya fueron aprobados.
- Integración de requisitos, recotización, errores y contratos REST adicionales; la matriz básica T20 ya fue aprobada.

No codificar constantes arbitrarias como decisiones comerciales aprobadas.


## Demostración ejecutable de extremo a extremo — ampliación T36

El entorno local puede habilitar POST /demo/deliveries con DELIVERY_DEMO_ENABLED=1.
Ejecuta un envío simulado completo, incluida aceptación explícita para ese
recorrido, asignación, entrega y entrega del efectivo al operador. La duración
proviene del modelo entrenado; tarifas, cobertura, cargas y ubicaciones son
parámetros de ejemplo identificados. No se añaden registros demo al entrenamiento.
El comando scripts/demo_delivery.py conserva parámetros/cotización/resultados en
un recibo JSON y MongoDB persiste los historiales operativos. El recorrido es
consecutivo y conserva pasos completados si se interrumpe. No se afirma que este
endpoint sustituya las operaciones individuales o valide condiciones comerciales
reales; está destinado a la exposición local del proyecto académico.


### Revisión predictiva solicitada para la exposición

La demostración usa v2: duración condicionada por distancia/calendario y riesgo
de superar un plazo prometido explícito. El riesgo es una salida aprendida de
entregas/plazos reales, sin umbral comercial inventado. El modelo no calcula
precio, elige vehículo o garantiza cumplimiento. La mejora en test se documenta
junto a la ausencia de validación local y la reutilización exploratoria del test.
