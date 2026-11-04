# ARCHITECTURE — Arquitectura del Asistente de Delivery Económico

**Estado:** diseño precisado en T03, no implementación terminada. Los contratos nuevos de este documento son propuestas para coordinación antes de implementarlos; no se consideran aprobados por el otro integrante. T04 implementa únicamente los modelos de dominio. Las decisiones aún abiertas se señalan expresamente.

**Propósito de este documento:** explicar qué responsabilidad tiene cada componente, cómo se comunican los dos integrantes y cómo almacenaremos los datos en AWS sin introducir infraestructura innecesaria.

## Visión de alto nivel

```text
               Next.js (T47–T54)
          chat / negocio / repartidor / operador
                        |
                   HTTP/JSON
                        v
                 FastAPI (T30)
          /health  /predict  + operaciones
                        |
          ┌─────────────┼──────────────────┐
          v             v                  v
     Pedidos/estados  Cotizaciones     Predicción ML
     y asignaciones   costos/rutas      (inferencia)
          |             |                  |
          └─────────────┼──────────────────┘
                        |
             puertos/adaptadores de IO
                   /            \
              MongoDB          Amazon S3
           entidades/eventos   datasets/ models/ docs/

     Procesamiento/entrenamiento (offline Python)
     fuente REAL → Pandas / Dask / PySpark local
                → ML + MLP → métricas y artefacto
                → S3 models/ [solo con autorización]
```

**Separación importante:** `predict()` estima una variable respaldada por datos; el motor comercial aplica reglas de tarifa/vehículo. Los resultados comerciales no se presentan como métricas ML.

## Stack acordado o previsto

| Capa | Tecnología | Función |
|---|---|---|
| Dominio y servicios | Python 3.9+ | Entidades, casos de uso, validación |
| API | FastAPI + Pydantic | `/health`, `/predict`, OpenAPI; otros contratos a acordar |
| BD operacional | MongoDB | Pedidos, negocios, repartidores, estados, eventos, índices/validaciones |
| Objetos | AWS S3 con `boto3` | Datasets, modelos, documentos |
| ETL | Pandas, Dask, PySpark local | Transformaciones comparables y benchmarks |
| ML/DL | scikit-learn + framework MLP a acordar | Baseline, 3 familias ML y MLP pequeña |
| Demo | Next.js | Cuatro vistas y chat simulado |
| Local | Docker / Docker Compose | Demo reproducible |
| Infraestructura | Terraform + AWS | Provisionar recursos nuevos de despliegue con permiso |
| CI/CD | GitHub Actions | Tests/build/deploy, en tareas posteriores |

No incluir Kubernetes, colas, microservicios ni servicios administrados caros sin necesidad demostrable.

## Límites de componentes y dependencias — T03

Se propone un backend modular dentro de un solo paquete Python, `delivery`.
La API y el procesamiento offline comparten únicamente contratos y artefactos
documentados; no hace falta separar el backend en varios servicios desplegables.

| Componente | Responsabilidad | Límite |
|---|---|---|
| `delivery.domain` | Entidades, unidades y reglas puras de negocio | No importa FastAPI, MongoDB, boto3 ni bibliotecas de entrenamiento. No fija parámetros comerciales pendientes. |
| `delivery.services` | Coordinar pedidos, cotizaciones, asignaciones y efectivo simulado | Usa dominio y puertos; no conoce documentos MongoDB ni claves S3 concretas. |
| `delivery.ports` | Describir operaciones de persistencia, archivos e inferencia | Contratos Python simples basados en tipos del dominio; sin clientes de SDK ni tipos HTTP. |
| `delivery.adapters` | Implementar puertos con MongoDB, S3 y el modelo validado | Traduce datos externos al contrato interno; no decide tarifas ni entrena durante una solicitud. |
| `delivery.api` | Validar solicitudes/respuestas, componer dependencias y traducir errores a HTTP | Invoca servicios; no contiene reglas comerciales ni acceso directo desde los handlers a MongoDB/S3. |
| `ml/data` | Adquisición y transformaciones reproducibles | Trabaja con archivos de procedencia verificada; no consume pedidos simulados como etiquetas reales. |
| `ml/experiments` | Entrenar, evaluar y exportar pipeline y manifiesto | Produce artefactos versionados para inferencia; no depende de la API ni de MongoDB. |
| `frontend` | Presentar chat y paneles Next.js | Consume HTTP/JSON; no calcula una tarifa oficial en paralelo al backend ni accede a MongoDB/S3 con credenciales. |
| `infra` | Contenedores y recursos de despliegue cuando corresponda | Sin lógica de negocio; referencia el bucket existente y no se ejecuta en T03. |

Las dependencias de código apuntan hacia el dominio: los servicios usan puertos,
los adaptadores los implementan y la composición de la API los conecta. Los
adaptadores no se invocan entre sí para coordinar el negocio. El motor de
cotización recibe un resultado del puerto de predicción, sin importar código
de entrenamiento. La API carga una versión validada del pipeline al iniciar el
servicio o mediante un mecanismo explícito de carga; no la descarga ni la
reentrena en cada solicitud. La política definitiva de carga se concreta en
T19/T30/T31.

T02 incorporó el paquete importable y las pruebas de entorno. T04 incorpora
únicamente `delivery.domain` y sus pruebas; las demás capas se crearán a medida
que sus tareas las necesiten.

### Modelos de dominio implementados — T04

Importación pública: `from delivery.domain import Business, Order, Courier, Quote`.
Los tipos auxiliares también se exportan desde `delivery.domain`. Se usan
`dataclasses` inmutables y enumeraciones de la biblioteca estándar, compatibles
con Python 3.9+, sin dependencias de FastAPI/Pydantic, MongoDB, S3 ni ML.
Las validaciones rechazan entradas inválidas con `ValueError`; no convierten
silenciosamente strings, booleanos numéricos o importes `float`.

| Tipo | Campos y unidades | Validación / límite |
|---|---|---|
| `Location` | `latitude`, `longitude`: grados geográficos | Números finitos dentro de los rangos geográficos [-90, 90] y [-180, 180]. No comprueba zona de servicio ni calcula rutas. |
| `Business` | `id`, `name`, `location: Location` | Identificador y nombre no vacíos; ubicación tipada. |
| `Order` | `id`, `business_id`, `origin`, `destination`, `details`, `status` | Referencias y detalles no vacíos; ubicaciones tipadas. Estado inicial `OrderStatus.REQUESTED` (`solicitado`). |
| `Courier` | `id`, `vehicle`, `approved`, `available` | `VehicleType`: `bicicleta` o `motocicleta`; aprobación/disponibilidad booleanas explícitas e independientes. No asigna pedidos. |
| `DeliveryDuration` | `minutes`, `source`, `interval_definition`, `model_version` opcional | Minutos finitos no negativos e intervalo no vacío. `DurationSource.PREDICTION` exige versión; `ILLUSTRATIVE` no admite atribuir el dato a un modelo. |
| `QuoteAmounts` | `currency`, `delivery_fee`, `courier_payment`, `variable_cost`, `attributable_cost`, `margin` | Todos los importes son `Decimal` finitos en la misma moneda; tarifa/pago/costos no negativos, margen puede ser negativo. Moneda explícita con formato de tres letras ASCII mayúsculas, sin catálogo monetario ni conversión. |
| `Quote` | `id`, `order_id`, `distance_km`, `distance_method`, `duration` y `amounts` opcionales | Distancia finita no negativa en km y método identificado. Ausencia de duración/importes se representa con `None`; es un borrador incompleto, no una cotización comercial emitida. |

`OrderStatus` incorpora el vocabulario de SPEC: `solicitado`, `cotizado`,
`confirmado`, `asignado`, `recogido`, `entregado`, `cancelado`. T04 valida el tipo
del estado, no implementa sus transiciones ni permite inferirlas de la posición
en esa lista. Persistencia, eventos/historial del pedido y reglas de cambios
corresponden a T20/T32. Asignaciones/entregas y registros de efectivo se concretan
en T24/T26/T28; no se agregan entidades vacías para anticiparlos.

Los identificadores son strings no vacíos suministrados por quien crea la
entidad, sin generación automática ni dependencia de `ObjectId`. La existencia
de referencias, unicidad y coincidencia entre el origen de un pedido y el negocio
se verificarán en los servicios/repositorios. Cada valor monetario se suministra
explícitamente, sin tarifa, redondeo, comisión ni fórmula de margen predefinidos.
Una versión declarada en `DeliveryDuration` registra procedencia; no certifica
por sí sola que exista un artefacto evaluado. Esa verificación sigue en
T19/T30/T31. No se fija el esquema de features de `/predict`.

Los datos en `backend/tests/test_domain.py` son fixtures sintéticas para probar
validaciones: no representan tarifas acordadas, observaciones ni resultados ML.

Verificación de T04: `uv run --locked pytest -q` ejecutó **16 pruebas aprobadas**
en Python 3.12.14 (14 del dominio y 2 del entorno), sin parametrización. La misma suite pasó en
Python 3.9.25 tras `uv sync --locked --python 3.9` con
`UV_PROJECT_ENVIRONMENT` apuntando a un entorno temporal, eliminado al terminar.
`uv lock --check`, `uv pip check` y `git diff --check` también finalizaron
correctamente. No se instalaron dependencias nuevas ni se accedió a AWS o BD.

## Flujo completo del pedido — propuesta T03

| Paso | Coordinación prevista | Registro o salida | Tareas |
|---|---|---|---|
| Solicitud simulada | Chat Next.js envía la solicitud a la API; el servicio valida negocio, ubicaciones y alcance local según configuración acordada. | Pedido e identificador consultable en MongoDB; mensaje de la demo. | T04, T20, T27, T47–T48 |
| Cotización | Servicio obtiene distancia de referencia, solicita inferencia si hay modelo válido y aplica reglas comerciales aprobadas. | Cotización vinculada al pedido, procedencia de duración y desglose comercial. | T21–T23, T30–T31 |
| Confirmación | El negocio confirma una cotización asociada al pedido; el servicio valida la transición. | Estado y evento del pedido, con referencia a la cotización utilizada. | T20, T49 |
| Asignación | Servicio selecciona un repartidor simulado aprobado y disponible; evalúa agrupación solo con reglas acordadas. | Asignación, pedidos incluidos y secuencia de paradas. | T24, T26, T50 |
| Recogida y entrega | Panel del repartidor solicita transiciones; el servicio verifica estado y asignación antes de persistirlas. | Estados y eventos simulados consultables por cliente, negocio y operador. | T20, T26, T50, T53 |
| Efectivo simulado | Servicio registra cobro/entrega ficticios según el flujo contable acordado. | Registro de efectivo separado del estado logístico; ninguna operación financiera real. | T28, T51 |
| Comparación | Operador compara escenarios individuales y agrupados usando las mismas reglas y supuestos identificados. | Desglose de costos/margen y supuestos; sin afirmar ahorro o ROI no medido. | T25, T29, T51, T54 |

Un paso rechazado no adelanta el estado del pedido. Para T20, Ruben aprobó el
2026-11-03 la siguiente matriz básica:

| Estado actual | Destinos permitidos |
|---|---|
| `solicitado` | `cotizado`, `cancelado` |
| `cotizado` | `confirmado`, `cancelado` |
| `confirmado` | `asignado`, `cancelado` |
| `asignado` | `recogido` |
| `recogido` | `entregado` |
| `entregado` | Ninguno |
| `cancelado` | Ninguno |

Los avances requieren validar cotización/asignación y contexto según corresponda.
T20 exige un `TransitionRequirements` que consulte fuentes autoritativas; sin
validador, o si este rechaza, el avance falla sin escribir. Cotizar/confirmar
requiere cotización válida del pedido; asignar/recoger/entregar requiere la
asignación válida correspondiente. Implementar esos requisitos comerciales y
su conexión sigue en las tareas de cotización/asignación, sin un validador
permisivo de producción. Cancelar antes de asignar no crea cobros ni asignaciones.

Se rechazan saltos, retrocesos y estados repetidos; no se añaden eventos por
reintentos rechazados. La actualización exige el estado esperado y cambia
pedido/historial de forma atómica. La recotización no se habilita implícitamente
con un regreso de estado; sigue pendiente de un diseño específico. En entregas
agrupadas, el estado de cada pedido no se deduce del de otro.

Si falta un modelo válido, no se devuelve una duración fabricada. Si faltan
fórmulas o parámetros comerciales aprobados, no se emite una cotización
comercial completa. La UI debe comunicar la dependencia pendiente; cualquier
escenario ilustrativo se identifica como tal y permanece fuera del dataset ML.
Los eventos y mensajes del simulador no son observaciones reales de entregas.

## Contratos API y coordinación entre integrantes

- **Obligatorios por guía:** `GET /health`, `POST /predict`, documentación OpenAPI.
- El payload de `/predict` dependerá del **dataset real y sus features disponibles al momento de cotizar**. No congelar un contrato con features inventadas. T03 documenta el borrador; T13/T19 lo hacen viable; T30/T31 lo integran.
- Endpoints de pedidos, cotizaciones, repartidores y simulador son **propuestos** y deben documentarse antes de implementarse. La UI debe consumir la API y no acceder directamente a MongoDB.
- Modelos de dominio y DTOs de API se separan: los datos del negocio no se hacen depender de esquemas específicos de una fuente de ML.
- Evitar que el entrenamiento y la inferencia dependan de MongoDB si no aporta al caso.

### Borrador HTTP para coordinación

Solo `/health`, `/predict` y OpenAPI son requisitos ya documentados. Las demás
rutas, nombres de campos y respuestas siguientes son propuestas de T03, no
endpoints implementados. T04 acuerda los tipos y T30 documenta los esquemas en
OpenAPI antes de conectar el frontend.

| Operación | Ruta propuesta o requerida | Entrada/salida conceptual |
|---|---|---|
| Salud del proceso | `GET /health` (requerida) | Estado del proceso. No equivale a certificar disponibilidad del modelo, MongoDB o S3; los chequeos de dependencias se acordarán en T30. |
| Inferencia | `POST /predict` (requerida) | Entrada pendiente de T07/T13. Si el target candidato se valida, duración en minutos, versión del modelo y definición del intervalo; sin tarifa. |
| Crear y consultar pedido | `POST /orders`, `GET /orders/{order_id}` | Datos de negocio/origen/destino/detalles; identificador y estado del pedido. Campos finales en T04. |
| Solicitar cotización | `POST /orders/{order_id}/quotes` | Referencia al pedido; cotización identificada con distancia/unidad, duración/procedencia y desglose monetario con moneda explícita. Parámetros en T21–T23. |
| Solicitar transición | `POST /orders/{order_id}/transitions` | Estado solicitado y contexto necesario; pedido actualizado o rechazo. Matriz interna T20 aprobada; DTOs y conexión HTTP siguen en T30. |
| Crear asignación | `POST /assignments` | Referencias a pedidos y contexto de selección; asignación a repartidor aprobado y paradas, según T24/T26. |
| Registrar efectivo ficticio | `POST /orders/{order_id}/cash-events` | Evento contable simulado; registro identificado. Campos y validaciones pendientes de T28. |

Para `/predict` se propone distinguir entrada inválida, ausencia de modelo y
fallo de inferencia. Como borrador de traducción HTTP: `422` para validación,
`404` para entidad inexistente, `409` para transición incompatible y `503` para
modelo o dependencia no disponible; un fallo inesperado se trata como `500`
sin exponer secretos ni detalles internos. T30 ratifica el formato de error y
los códigos, incluidos los casos de configuración comercial incompleta.
No devolver `200` con una estimación ficticia para ocultar un fallo.

### Puertos internos propuestos

| Puerto | Operaciones conceptuales | Datos compartidos / condición pendiente |
|---|---|---|
| Repositorios de negocio | Consultar entidades, guardar pedido/cotización/asignación y registrar cambios de estado/efectivo | Tipos de dominio de T04; identificadores internos independientes de `ObjectId`. T20/T32 definen actualizaciones condicionales para evitar transiciones concurrentes incompatibles. |
| Almacenamiento de archivos | Leer un objeto identificado por clave y versión; publicar solo desde procesos autorizados | Contenido y manifiesto con hash; bucket/región desde configuración. T33 concreta operaciones y permisos, sin crear buckets. |
| Predictor de duración | Cargar pipeline validado y predecir con entradas compatibles | Esquema de features de T07/T13, resultado/unidad/intervalo y versión de T19. Ausencia/incompatibilidad del modelo es un error explícito. |

No se fijan todavía DTOs HTTP ni features desconocidas. El adapter
de inferencia valida la compatibilidad entre esquema y artefacto; el cálculo
de tarifas usa sus propias reglas y no extrae conclusiones comerciales de las
métricas del modelo. Las rutas de archivos y el driver de MongoDB quedan fuera
de las entidades de dominio.

### Organización prevista del código

**Comparación académica T25 aprobada:** `CostComparisonService.compare(order_ids,
start, individual_costs, grouped_costs)` requiere políticas T24/T22 explícitas.
Lee cada pedido una vez y usa esos mismos snapshots para todas las rutas.
`individual_costs` debe mapear exactamente los IDs solicitados a OperatorCosts,
sin faltantes/extras; grouped_costs es obligatorio. Moneda igual a la política.

Se planifica un recorrido abierto T24 por individual y uno por el grupo,
desde el mismo inicio y con la misma política/zona. Todos los tramos incluyen
aproximación a recogidas; no se añade regreso/reposicionamiento final. Cada ruta
tiene una base de pago T22 más pago/km × longitud, redondeada con su unidad y
ROUND_HALF_UP. Los costos variable/atribuible suministrados se redondean igual;
total operador = pago + variable + atribuible. No se usan los campos de tarifa
al cliente ni se calcula margen/ingresos: no son cotizaciones T22 por cliente.

`CostComparison` inmutable conserva política completa, `CostedRoute` individuales
y agrupada con sus planes/costos suministrados/desglose, agregados de componentes,
distancias y diferencias `individual_minus_group_cost`/`individual_minus_group_km`.
Positivo significa menor costo/distancia agrupado bajo esos supuestos; negativo
no se oculta ni se convierte en cero. Contextos locales Decimal de 28 dígitos
rechazan pérdida de precisión en operaciones previas al redondeo o agregados.

Permanece académico, sin capacidad/ruta vial validada ni elección automática.
Las rutas individuales son independientes: no se validan recursos ni se modela
un mismo repartidor retornando gratis al inicio. Los extremos finales pueden
diferir. No reserva/asigna, cambia estados, emite cotizaciones o usa tiempos ML.
`CostComparisonConfigurationMissing` indica falta de políticas; datos/costos
incompletos o incompatibles fallan sin valores de reemplazo. No certifica ahorro,
ROI o viabilidad logística; T26/T29 completarán sus respectivos alcances.

**Rutas académicas T24 aprobadas:** `RoutePolicy(version, max_orders, area)`
exige un máximo entero positivo y ServiceArea T23 explícitos. No tiene tamaño
de grupo o zona predeterminados. `RouteSuggestionService.suggest(order_ids,
start)` lee snapshots por IDs elegidos por el llamador; no busca pedidos para
formar grupos ni consulta/asigna repartidores.

Se rechazan grupos vacíos/duplicados/excesivos, IDs inválidos, pedidos inexistentes,
inicio/extremos fuera de zona y pedidos en asignado/recogido/entregado/cancelado.
Se admiten solicitado/cotizado/confirmado. `suggest_route` elige en cada paso la
parada más cercana por Haversine: recogidas aún pendientes o entregas de pedidos
ya recogidos en la sugerencia. Es una precedencia del plan, no un evento real.
Distancias iguales se resuelven por ID; snapshots se ordenan por ID para reproducir
el mismo resultado aunque cambie el orden de entrada del grupo.

Devuelve `RoutePlan` inmutable con política, inicio, snapshots, dos `RouteStop`
por pedido, tipo recogida/entrega, ubicación y km desde la parada anterior.
No fusiona paradas coincidentes: conserva su trazabilidad con tramos cero.
El total suma esos tramos como Decimal en contexto local de 28 dígitos, sin
redondeo monetario ni retorno automático. Registra el método Haversine T21.

`academic_only=True`, `capacity_validated=False` y `road_route_validated=False`
explicitan el alcance: heurística geográfica abierta, sin garantizar óptimo,
capacidad acumulada, tiempos, seguridad vial o viabilidad de entrega. No modifica
repositorios/historial, reserva capacidad, calcula tarifas o altera el modelo.
T26 debe revalidar snapshots/estado y requisitos al asignar; esta lectura no es
una transacción ni reserva del grupo. T25 comparará costos con supuestos explícitos.

**Reglas de vehículos T23 aprobadas:** `ServiceArea(id, southwest, northeast)`
describe un rectángulo en grados, con sur < norte y oeste < este, sin cruzar el
antimeridiano. `contains` incluye bordes; deben estar dentro origen y destino.
No geocodifica direcciones ni valida un recorrido vial. No hay zona prefijada.

`VehiclePolicy(version, area, bicycle, motorcycle)` exige `VehicleLimits` para
ambos tipos, con `max_distance_km` y `max_load_kg` Decimal finitos positivos.
`VehicleRulesService.evaluate(order_id, load_kg)` lee un snapshot y calcula la
misma distancia Haversine de T21, capturada con Decimal(str(...)). La carga es
un dato explícito positivo en kg: no se infiere de detalles, ML o cantidad de
productos. Se admiten distancia/carga iguales al máximo y no se redondea la
distancia ni se añade un margen de tolerancia comercial.

Devuelve `VehicleEvaluation` inmutable con pedido, política completa, carga,
distancia/método, `within_configured_area` y decisiones de ambos vehículos.
Los motivos son `outside_service_area`, `distance_limit_exceeded` y
`load_limit_exceeded`; se conservan todos los que correspondan. `eligible_vehicles`
puede contener ambos, uno o ninguno. El orden de presentación no expresa prioridad.

Resultado siempre académico, sin elegir/reservar/asignar repartidor, cambiar
estado/historial, calcular precios ni alterar duración ML. La comprobación
rectangular no cambia `coverage_validated=False` del borrador T21 ni habilita
el validador T20. T26 debe validar aprobación/disponibilidad y estado al asignar;
este resultado solo describe criterios de tipo de vehículo para el snapshot.
`VehicleConfigurationMissing` indica ausencia de política; configuración parcial,
carga ausente/inválida o geometría invertida fallan sin valores de reemplazo.

**Cálculo académico T22 aprobado:** `PricingPolicy` exige versión, moneda,
unidad de cuantización y bases/importes por km de cliente y repartidor, sin
valores predeterminados. `OperatorCosts` exige moneda y costos variable/atribuible
por envío; son del operador y excluyen lo incluido en el pago al repartidor.
No se hace conversión monetaria. Ambos modelos son inmutables.

`calculate_amounts(distance_km: Decimal, policy, costs)` aplica:
tarifa = base cliente + precio/km × distancia;
pago = base repartidor + pago/km × distancia;
margen = tarifa − pago − costo variable − costo atribuible.
Redondea componentes con ROUND_HALF_UP y luego obtiene el margen de los importes
redondeados; admite pérdida. La unidad monetaria debe ser una potencia de diez
positiva explícita. El contexto local tiene 28 dígitos y rechaza pérdida de
precisión antes del redondeo monetario; un error numérico no genera un importe
aproximado como si fuera válido. Referencia: [Decimal](https://docs.python.org/3.12/library/decimal.html).

`PricingService.calculate(estimate, costs)` recibe `AcademicQuoteEstimate`,
captura su distancia mediante `Decimal(str(distance_km))` y devuelve
`AcademicPriceBreakdown` con estimación original, política completa/versionada,
costos, distancia usada e importes. Mantiene `academic_only=True` y
`coverage_validated=False`. El Quote original conserva amounts=None.
`PricingConfigurationMissing` indica falta de política/costos, sin reemplazarlos
por cero. No persiste, cobra, cambia estados ni habilita el validador de T20.
No usa duración ML, vehículo, tarifas ocultas o reglas de combustible inventadas.

**Contratos internos T20 aprobados:** `delivery.ports.orders` define
`BusinessReader.get(business_id)`, `OrderRepository.get/create/transition` y
`TransitionRequirements.validate(order, target)`. Este último falla con una
excepción si no puede acreditar requisitos; devolver un booleano no es su contrato.
El repositorio devuelve `OrderRecord(order, events)` inmutable; `transition`
recibe `expected`, `target` y fecha UTC, y debe comparar estado/cambiar pedido/
añadir evento como una sola operación. T32 debe conservar esa semántica en MongoDB.

`OrderService.register` exige un `Order` inicialmente solicitado, negocio
existente y origen igual a su ubicación. Los IDs se suministran, sin generarlos
ni permitir duplicados. `get` consulta y `transition` verifica flujo/requisitos
antes de actualizar condicionalmente. Cada creación/cambio aceptado añade un
`OrderEvent(previous_status, status, occurred_at)` UTC; los rechazos no escriben.
El reloj es inyectable para pruebas, normaliza a UTC y no admite fechas sin zona.
Se rechazan eventos anteriores al último registrado.

`InMemoryBusinesses` usa un catálogo explícito, sin negocios prefijados;
`InMemoryOrderRepository` protege actualización e historial con un lock local.
No persiste al reiniciar ni coordina procesos distintos: no equivale a MongoDB.
Errores internos: `OrderNotFound`, `BusinessNotFound`, `OrderConflict` (incluye
`DuplicateOrder`) y `MissingPrerequisite`. T30 concretará su traducción HTTP.
El registro captura una solicitud, sin certificar cobertura/tarifa; T21/T23
deben aportar la validación local para cotizar. Los eventos son de simulación,
no observaciones reales para entrenar ML.

**Artefacto académico local T19:** el bundle versionado en
`models/delivery-duration/meituan-temporal-rf-v1/` contiene transformación T13 y
Random Forest, metadatos, evidencia y ficha. Su entrada interna es hora UTC
`request_hour_utc` (0–23) y día UTC `request_weekday_utc` (lunes=0, domingo=6);
su salida es una duración en minutos, sin intervalo predictivo. El cargador
`delivery_ml.artifact.load_pipeline` verifica esquema, hashes y entorno antes de
deserializar un bundle propio de confianza. Incompatibilidad/ausencia falla
explícitamente. No es un DTO HTTP ni cambia los puertos propuestos: T30/T31
concretarán el adapter/API. No se publica en S3 ni se acredita uso operativo;
ver selección y límites en DATA_ML.

**Estimación académica T21 aprobada:** `AcademicQuoteService.estimate(order_id,
quote_id)` consulta un pedido solicitado y devuelve `AcademicQuoteEstimate`.
Contiene un `Quote` sin importes y marcas inmutables `academic_only=True` y
`coverage_validated=False`, con limitaciones explícitas. No persiste el borrador
ni cambia el pedido; recotización y emisión comercial quedan fuera del alcance.
Los identificadores se suministran como en T04.

La distancia usa Haversine con el radio medio IUGG para WGS-84,
6371.0087714150598 km, documentado por [GeoPy](https://geopy.readthedocs.io/en/stable/#calculating-distance).
Se implementa con `math`, sin instalar GeoPy. Es longitud aproximada de círculo
máximo sobre una esfera, no recorrido vial, cobertura ni distancia válida para
facturar. Solo acepta `Location` en grados; no usa coordenadas raw de Meituan.
El radio terrestre es una constante geométrica, no un límite de negocio.

`DurationPredictor.predict(requested_at)` recibe la creación del pedido con zona
horaria. `LocalDurationPredictor` carga una vez un bundle T19 propio de confianza
mediante el cargador verificado, comprueba target/unidad/versión y reutiliza el
pipeline. Deriva hora/día en UTC y devuelve `DeliveryDuration` con fuente
`prediccion`, versión del modelo y definición creación (`platform_order_time`)
hasta entrega (`arrive_time`). No incluye distancia o vehículo entre predictores,
no usa la hora de una consulta posterior y no entrena durante inferencia.

Modelo ausente/incompatible o salida inválida produce `PredictionUnavailable`;
una fecha sin zona se rechaza. No hay fallback de tiempo ficticio. El resultado
continúa siendo experimental/externo al dominio local, con las limitaciones de
T19. No se conectan HTTP, S3, proveedor de mapas ni un validador comercial de T20.

```text
backend/
  src/delivery/
    domain/          # entidades y reglas puras
    services/        # casos de uso
    ports/           # contratos repositorio/storage/predictor
    adapters/        # MongoDB, S3, modelo ML
    api/             # FastAPI + DTOs
  tests/
ml/
  data/              # adquisición/ETL reproducibles
  experiments/       # entrenamiento, evaluación, artefactos
frontend/            # Next.js (futuro)
infra/terraform/      # IaC (futuro)
docs/                # este diseño y acuerdos
```

No crear código vacío de todas estas capas al inicio; T01 crea una base mínima y T03 ratifica el diseño. Usar imports y paths acordados entre agentes.

### Acuerdos necesarios para trabajo paralelo

| Punto de integración | Trabajo que puede avanzar con el backlog actual | Evidencia necesaria antes de integrar |
|---|---|---|
| Dominio y persistencia | Ruben define entidades en T04; Guillermo prepara MongoDB en T32 cuando estén disponibles los contratos. | Campos, unidades, identificadores, estados y validaciones revisados; mapeo MongoDB sin filtrar tipos del driver. |
| Datos e inferencia | Guillermo investiga/valida y transforma en T05–T12; Ruben entrena en T13–T19 sobre la versión validada. | Definición del target, licencia/procedencia, features disponibles al cotizar, versión/hash de datos y artefacto. |
| Cotización y API | Ruben implementa lógica en T20–T29; Guillermo integra API/modelo en T30–T31. | Tipos de entrada/salida y errores acordados; modelo evaluado y reglas comerciales aprobadas. |
| API y demo | T47–T54 conservan sus responsables sin asignar. | OpenAPI de T30 y flujo verificable; no desarrollar un backend paralelo dentro de Next.js. |

Esta tabla no cambia responsables, estados ni prioridades del backlog. Una
modificación de contratos se registra aquí y se coordina antes de que el otro
módulo dependa de ella; las propuestas no deben copiarse a código como acuerdos
definitivos.

## Decisiones abiertas y efecto sobre las tareas

| Decisión pendiente | Dónde se resuelve | Qué impide cerrar |
|---|---|---|
| Fuente real, licencia y duración objetivo observada | T05–T07 y [DATA_ML.md](DATA_ML.md) | Entrenamiento válido y esquema definitivo de `/predict`. |
| Features disponibles al cotizar y representatividad geográfica/vehículo | T07/T13/T19 | Prometer una predicción aplicable al escenario local o diferenciada por vehículo. |
| Valores reales de zona/límites/carga, seguridad y método vial/comercial | [SPEC.md](SPEC.md), T21/T23 | Haversine y criterios configurables T23 aprobados; valores concretos, cobertura comercial y asignación siguen pendientes. |
| Valores de tarifas/costos y reglas adicionales de combustible/comisiones | [SPEC.md](SPEC.md), T22/T25/T29 | Fórmulas T22 y supuestos de comparación T25 aprobados; faltan importes concretos y acuerdos para cotización comercial/análisis financiero. No se sustituyen pendientes por cero. |
| Integración de requisitos, recotización y traducción de errores | T20/T26/T30/T32 y contratos de este documento | Conectar la base T20 aprobada con cotización/asignación, MongoDB y HTTP sin omitir requisitos. |
| Agrupación operativa, capacidad, asignación y efectivo ficticio | T24/T26/T28 | Heurística T24 aprobada; faltan viabilidad, reserva/asignación y contabilidad simulada. |
| Driver MongoDB, esquemas OpenAPI, errores y carga del modelo | T19/T30–T33 | Integración operativa API/storage/inferencia; no requiere resolverlos con código en T03. |
| Topología de despliegue, presupuesto e IAM | T41–T46 | Despliegue AWS. Next.js junto al backend o separado sigue pendiente; S3 ya existe y no se recrea. |

T03 puede precisar límites y propuestas sin resolver estos valores. Las tareas
afectadas deben comunicar un bloqueo cuando necesiten una decisión; no completar
tarifas, targets o permisos con supuestos silenciosos.

## Persistencia y AWS S3

La aplicación utiliza **dos tipos de almacenamiento diferentes**, porque resuelven necesidades distintas:

| Componente | Qué almacena | Por qué se utiliza |
|---|---|---|
| MongoDB | Negocios, pedidos, repartidores, estados y registros de operaciones simuladas | Permite consultar y actualizar entidades del sistema mediante CRUD, índices y validaciones. |
| Amazon S3 | Archivos de datasets, resultados procesados, artefactos de modelos y evidencia académica | Permite guardar objetos con rutas estables y separa los archivos grandes de la base de datos transaccional. |

### Configuración confirmada

- Bucket **ya existente**: `ml-kodigo-resources`.
- Región: `us-east-1`.
- Prefijos principales existentes o acordados: `datasets/`, `models/` y `docs/`.
- **No crear ni eliminar el bucket**. Terraform, cuando se implemente, debe consultarlo como recurso externo, salvo un cambio explícitamente autorizado.
- No se ha verificado en este documento el estado actual de versionado, cifrado, políticas IAM o acceso público del bucket. Inspeccionarlos antes de depender de ellos; no modificarlos sin autorización.

### Organización propuesta de objetos en el bucket

La estructura siguiente es una **convención de nombres para futuros objetos**, no una afirmación de que ya existan. En S3 son prefijos de claves, no carpetas físicas.

```text
s3://ml-kodigo-resources/
├── datasets/
│   └── <fuente-aprobada>/
│       └── <version>/
│           ├── raw/                 # Descarga original inalterada (si la licencia permite subirla)
│           ├── processed/           # Limpieza y transformaciones reproducibles
│           ├── splits/              # Particiones para experimentos, si corresponde
│           └── manifest.json        # Origen, hash, fecha, licencia y transformaciones
├── models/
│   └── delivery-duration/
│       └── <version-modelo>/
│           ├── pipeline.joblib      # Ejemplo de formato, sujeto al framework final
│           ├── metrics.json         # Resultados obtenidos, no valores predefinidos
│           └── manifest.json        # Dataset, features, unidades y dependencias
└── docs/
    └── <hito-o-evidencia>/           # Informes, gráficos y evidencias autorizadas
```

Los identificadores entre `< >` son marcadores de posición y **no** nombres ya aprobados. No crear directorios vacíos para simular que hay datasets o modelos disponibles. Los archivos originales pueden permanecer únicamente en la fuente externa si la licencia no autoriza redistribuirlos a S3.

### Recorrido reproducible de los datos

1. El integrante de datos identifica una fuente real, revisa permisos y verifica que el dataset es descargable (**T05**).
2. Documenta URL de origen, fecha, licencia, número de registros observado y checksum SHA-256; descarga la versión aprobada sin alterarla (**T06**).
3. Comprueba el significado y disponibilidad de la etiqueta objetivo, calidad y sesgos (**T07**).
4. Aplica un pipeline repetible con Pandas, equivalente en Dask y PySpark local. Conserva transformaciones, versiones y métricas obtenidas (**T08–T12**).
5. El entrenamiento y evaluación consumen **exactamente la versión validada** de datos; el resultado seleccionado se publica como artefacto versionado en `models/` solo cuando exista (**T13–T19**).
6. FastAPI carga una versión aprobada del modelo y ejecuta inferencia. No vuelve a entrenar en cada pedido (**T30–T31**).

**Acceso a datos:** localmente se puede descargar un objeto S3 a un directorio temporal o de trabajo ignorado por Git y procesarlo con herramientas Python. Esto simplifica la compatibilidad entre Pandas, Dask y PySpark local. Se registran la clave S3 y el hash para repetir experimentos. No depender de que todo el procesamiento ocurra dentro de AWS.

### Acceso seguro desde Python

- Usar `boto3`, las variables no sensibles `AWS_REGION` y `S3_BUCKET` y **credenciales fuera del repositorio**: perfil de AWS CLI para desarrollo, roles IAM para servicios desplegados.
- El frontend Next.js nunca recibe claves de AWS ni se conecta directamente a S3 con credenciales privilegiadas.
- Diferenciar permisos: lectura de datasets para ETL, escritura limitada al publicar objetos autorizados, lectura de modelos para inferencia y acceso restringido a evidencias.
- Si una persona no tiene permiso sobre una ruta, la tarea debe documentar la limitación; no ampliar IAM por iniciativa del agente.
- No subir datos personales innecesarios, archivos `.env`, credenciales ni muestras con información sensible.
- Verificar existencia, región y permisos **sin escribir** antes de conectar el servicio. No modificar el bucket en T01–T04.

### Política de versiones y reproducibilidad

- No sobreescribir objetos originales: cada versión debe quedar identificada por nombre, versión, hash o identificador de ejecución.
- Guardar un manifiesto por versión de datos y modelo con su procedencia y dependencias.
- No suponer que el *S3 Versioning* nativo está habilitado; puede utilizarse versionado lógico por prefijos.
- Diferenciar tres tipos de archivos: **datos observados**, **resultados transformados**, y **escenarios simulados**. Los escenarios de la UI no se añaden al entrenamiento real.

Para el detalle metodológico, ver [`DATA_ML.md`](DATA_ML.md).

## Despliegue objetivo (no implementarlo ahora)

```text
GitHub → GitHub Actions (test/build) → Docker image
                                        |
                              EC2 + Docker Compose
                              FastAPI + MongoDB
                                        |
                                       S3
                     Terraform: EC2, red, IAM y configuración
```

Next.js puede desplegarse junto al backend o por separado, según costos y facilidad demostrable. La decisión final se toma en T41. **Terraform debe consultar/referenciar el bucket ya existente**, no declararlo como recurso nuevo ni ejecutar cambios sobre él sin autorización. Un recurso de datos (`data`) sería una opción si su compatibilidad y permisos se comprueban cuando llegue T42. Antes de ejecutar `terraform apply`: revisar `plan`, costos, credenciales, permisos y alcance del cambio. Nunca aplicar automáticamente como parte de T01–T12. Docker Compose local debe poder funcionar sin un AWS pagado para las piezas que no requieren S3.

## Integración y orden

1. **T01–T04**: estructura, entorno, arquitectura y tipos de dominio (Ruben).
2. **T05–T12**: obtener/validar/transformar datos y comparar Pandas/Dask/PySpark (Guillermo, en paralelo).
3. **T13–T19**: entrenar/evaluar modelos con dataset validado (Ruben).
4. **T20–T34**: procesos de delivery y API/storage (responsables según backlog). Contratos revisados antes de conectarlos.
5. **T35–T40**: calidad, documentación y defensa.
6. **T41–T54**: despliegue y frontend, pendientes de asignar.

## Criterios transversales de calidad

Pruebas automatizadas, separación configuración/secretos, manejo explícito de errores, reproducibilidad, historial Git y revisión cruzada. No asumir que la API funciona con una predicción real hasta contar con artefacto entrenado y evaluado.
