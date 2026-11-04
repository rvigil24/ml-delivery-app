# Asistente de Delivery Económico

Proyecto académico de entregas simuladas con FastAPI, MongoDB y modelos de
Machine Learning entrenados con datos reales de Meituan. La demo actual permite
recorrer un pedido hasta la entrega del efectivo y consultar **duración estimada
y riesgo de retraso**. Next.js ofrece el chat de comida y los paneles locales de
Cliente, Negocio, Repartidor y Operaciones conectados a la API. El pedido del
cliente ya se guarda en Atlas y los estados se consultan automáticamente. La infraestructura AWS ya está
creada; la API cloud ya fue verificada con modelos desde S3 y persistencia Atlas.

**Reporte para lectura y entrega:** [PDF](reports/Reporte_Tecnico_Asistente_Delivery.pdf) · [Word editable](reports/Reporte_Tecnico_Asistente_Delivery.docx).

**Evidencias para la entrega:** [Anexo PDF](reports/Anexo_Evidencias_Asistente_Delivery.pdf) · [Word editable](reports/Anexo_Evidencias_Asistente_Delivery.docx) · [Paquete completo ZIP](reports/Entrega_Asistente_Delivery.zip).

**Presentación para la defensa:** [PowerPoint editable con notas](reports/Presentacion_Defensa.pptx) · [PDF](reports/Presentacion_Defensa.pdf).

**Guion y demostración:** [Guía PDF](reports/Guia_Exposicion_y_Demo.pdf) · [Word editable](reports/Guia_Exposicion_y_Demo.docx).

**Despliegue AWS verificado (ECS con Fargate):** [PDF](reports/Propuesta_Despliegue_AWS.pdf) · [Word editable](reports/Propuesta_Despliegue_AWS.docx).

**Arquitectura para exposición:** [PNG 4K](reports/Arquitectura_Despliegue_AWS.png) · [SVG editable](reports/Arquitectura_Despliegue_AWS.svg).

Configuración de infraestructura y arranque cloud: [Terraform](infra/terraform/README.md).
API actual: [Swagger en AWS](http://3.239.189.63:8000/docs). Acceso restringido a
la IP configurada del presentador; la IPv4 cambia si se reemplaza la tarea.

CI verifica tipos/build del frontend, pruebas básicas, Terraform y build Docker
en cada PR. El [despliegue AWS](infra/terraform/README.md) es manual y requiere
infraestructura y permisos previamente autorizados.

## Interfaz local (Next.js)

Con Node.js 22 o superior (CI usa Node 24), iniciar primero la API local
con el `.env` privado ya configurado para MongoDB:

```bash
uv run --locked --env-file .env uvicorn delivery.main:app --host 127.0.0.1 --port 8001
```

En otra terminal, desde la raíz:

```bash
cd frontend
npm ci
npm run dev -- --port 3001
```

Abrir [la interfaz local](http://127.0.0.1:3001). Operaciones es el inicio; el
menú permite pasar a Cliente, Negocio y Repartidor. Cliente representa una
**simulación de WhatsApp**, sin canal real ni LLM, con este recorrido:

1. Dirección de entrega y ubicación (GPS, coordenadas manuales o destino de ejemplo).
2. Negocios ordenados por distancia aproximada desde la API.
3. Menú del negocio consultado en la API, productos y cantidades.
4. Revisión con tiempo estimado y distancia del modelo; registro del pedido en la API y MongoDB.

Al revisar el pedido se consulta `/predict/delivery`: muestra minutos estimados
de solicitud a entrega y distancia aproximada en línea recta. La estimación se
conserva en la pantalla al confirmar; no es una promesa de entrega ni una ruta
por calles. «Ver modelo y comparación de plazo» permite ingresar minutos y ver
el riesgo de superarlos. Sin plazo no se inventa riesgo ni compromiso. Si falla
el modelo, aparece el error con reintento; no hay resultados de respaldo ficticios.

El texto de la dirección no se geocodifica automáticamente: la cercanía usa
el punto seleccionado, que debe corresponder a la dirección. La API devuelve
los negocios registrados con menú de ejemplo publicado; no garantiza cobertura.
Hay nueve productos ficticios en tres menús, identificados como ejemplos, sin
precios o disponibilidad real configurados. No se inventan importes ni totales.

Next.js consulta FastAPI mediante `/api/food`, sin exponer credenciales ni
necesitar CORS. `DELIVERY_API_URL` es configuración exclusiva del servidor y
por defecto apunta a `http://127.0.0.1:8001`; puede cambiarse con
`frontend/.env.local` usando `frontend/.env.example` como referencia.

La confirmación guarda la solicitud y devuelve su referencia. FastAPI valida
productos y cantidades contra su menú y obtiene el origen del negocio. El pedido
aparece en Negocio y Operaciones al actualizarse las consultas. Un reintento con la
misma referencia y contenido devuelve el registro existente; contenido distinto
se rechaza. La conversación se reinicia al recargar, pero el pedido permanece
guardado. No envía WhatsApp, calcula un total ni inicia un cobro. Los estados se consultan cada cinco segundos mientras la pestaña está visible
y al volver a ella, sin repetir los modelos ni las escrituras. Cliente muestra
el estado del pedido guardado durante esa conversación.
Negocio consulta pedidos e historial de la API, permite filtrar por estado y
actualizar la consulta. Confirma pedidos cotizados o cancela antes de asignación,
siempre sujeto a las validaciones del backend. Cancelar pide confirmación; los
estados y el historial se actualizan solo después de guardar correctamente.
El panel consulta hasta 100 pedidos del negocio elegido; conserva selección y
filtros durante las actualizaciones. Repartidor consulta sus asignaciones, paradas y estados actuales,
registra recogidas/entregas en orden y finaliza la ruta cuando todos los pedidos
están entregados. No crea asignaciones ni simula GPS en vivo. Sin asignaciones
existentes muestra el estado vacío, sin fabricar rutas. Operaciones consulta pedidos y efectivo guardados y permite previsualizar tarifa,
pago al repartidor, costos y margen mediante la política del backend. El cálculo
requiere política de precios y vehículos, predictor disponible y costos/carga
explícitos. No guarda cotizaciones ni mueve efectivo; sin configuración muestra
el bloqueo. Los registros ausentes no se representan como importes cero.

Comprobación de tipos y compilación de producción:

```bash
npm run typecheck
npm test
npm run build
npm run start -- --port 3001
```

Desarrollo usa `.next/`; la compilación y el servidor de producción usan
`.next-production/`, para que un build no rompa las rutas del servidor dev activo.
`next-env.d.ts` se genera automáticamente y no se versiona.

Detener con `Ctrl+C`. La interfaz local aún no se ha desplegado en AWS.

## Datos simulados para exposición

Swagger ofrece tres ejemplos en `POST /predict/delivery`: recorrido corto,
mismo recorrido con plazo más amplio y otro recorrido. Los plazos 30/45/60
minutos son entradas ilustrativas, no compromisos de entrega; las predicciones
las calculan los modelos reales. Un plazo de 1 minuto está fuera del rango de
entrenamiento registrado (mínimo 30 minutos), por eso no conviene como ejemplo
principal de exposición. La API mantiene el indicador de rango y validación.

[exposicion.json](examples/exposicion.json) contiene 3 negocios, 2 repartidores
y 3 pedidos ficticios, todos identificados con `demo-expo-`. Ya están cargados
en Atlas para consultar `/businesses`, `/couriers` y `/orders`. Los pedidos
permanecen solicitados; no se ejecutaron cotizaciones, asignaciones o cobros.
No se usan estos registros para entrenar o evaluar ML.

Para revisar o repetir la carga en la API que elijas:

```bash
uv run --locked python scripts/seed_presentation.py
uv run --locked python scripts/seed_presentation.py --url http://<IP-de-la-API>:8000 --apply
```

El primer comando solo muestra cantidades. El segundo crea faltantes; verifica
los existentes y falla si difieren, sin sobrescribir su historial. Los ejemplos
no contienen respuestas o tiempos reales prefabricados.

## Inicio rápido: demo con modelos desde S3

Requisitos: Git, Docker con Compose, Python 3.9+ para el comando de demo y un
perfil AWS local configurado con lectura de los objetos del bundle v2 en el
bucket privado existente `ml-kodigo-resources` (`us-east-1`). Docker incluye el
entorno Python 3.12.14 necesario para esos pesos; no hace falta instalar las
dependencias de entrenamiento para ejecutar la demo.

### 1. Preparar el repositorio y la configuración

```bash
git clone https://github.com/rvigil24/ml-delivery-app.git
cd ml-delivery-app
if [ ! -e .env ]; then
  cp .env.example .env
fi
mkdir -p models
```

Si ya tenés el repositorio, comenzá desde su carpeta. Conservá tu `.env` existente.
Agregá o actualizá estas variables no secretas en ese archivo:

```dotenv
DELIVERY_AWS_PROFILE=tu-perfil-aws
AWS_REGION=us-east-1
S3_BUCKET=ml-kodigo-resources
DELIVERY_MODEL_V2_DIR=
DELIVERY_MODEL_V2_MANIFEST_KEY=models/delivery-duration/meituan-eta-risk-v2/manifest.json
DELIVERY_MODEL_V2_MANIFEST_SHA256=0381a68fb7a7634823217d85718ce0efa5dad04fe3bf4f4b36358fa189d5e102
DELIVERY_MODEL_V2_MANIFEST_SIZE=1216
```

Sustituí `tu-perfil-aws` por el nombre de tu perfil autorizado. Sus credenciales
permanecen fuera del repositorio, en la configuración de AWS. No recrear el
bucket ni cambiar sus políticas. Esta variante usa MongoDB **local en Docker**;
conserva cualquier URI Atlas en `.env`, pero no la utiliza para la demo local.

### 2. Iniciar la API y MongoDB

Desde la raíz, en la misma terminal:

```bash
export DELIVERY_RUN_UID="$(id -u)"
export DELIVERY_RUN_GID="$(id -g)"
export DELIVERY_AWS_CONFIG_DIR="$HOME/.aws"
DELIVERY_DEMO_ENABLED=1 docker compose -f compose.yaml -f compose.s3.yaml up --build -d --wait
```

Abrí [Swagger /docs](http://127.0.0.1:8000/docs). MongoDB prepara su réplica,
esquema e índices; la API descarga y verifica v2 desde S3 una vez al arrancar.
Los pesos quedan en memoria, sin reentrenamiento por solicitud. El perfil AWS
se monta en lectura; no se copia a la imagen. HTTP solo se publica en loopback.

### 3. Ejecutar el recorrido completo

```bash
python3 scripts/demo_delivery.py
```

El comando ejecuta solicitud → cotización/aceptación simulada → confirmación →
asignación → recogida → entrega → cobro → entrega de efectivo al operador.
Libera al repartidor y guarda entrada y resultado en
`data/reports/presentation/demo_result.json`.

Comprobá en el recibo `delivery_prediction.model_source: "s3"`, la versión
`meituan-eta-risk-v2`, el pedido `entregado` y el último evento de efectivo
`entregado_al_operador`. Cada ejecución genera IDs `demo-` nuevos. El ejemplo
`examples/demo_delivery.json` contiene ubicaciones, tarifas, carga y límites
**simulados**; las estimaciones sí proceden de los modelos entrenados. Esos
registros no se añaden al entrenamiento.

Los datos operativos quedan en el volumen MongoDB; el recibo conserva la
cotización y su configuración. Los pasos son consecutivos: si se interrumpe la
demo, consultar el pedido y sus eventos; no hay rollback global o reanudación
por pasos. `/demo/deliveries` solo se habilita con `DELIVERY_DEMO_ENABLED=1`.

## Consultar los modelos sin crear un pedido

```bash
curl -sS -X POST http://127.0.0.1:8000/predict/delivery \
  -H 'Content-Type: application/json' \
  -d '{"requested_at":"2022-10-22T18:00:00Z","origin":{"latitude":0.0,"longitude":0.0},"destination":{"latitude":0.0,"longitude":0.01},"promised_minutes":30.0}'
```

La entrada anterior es ilustrativa. La respuesta incluye `estimated_minutes`,
`late_probability` (0–1), `distance_km`, `model_version`, `model_source` y
limitaciones. Cambiar el recorrido modifica la entrada de ETA; cambiar el plazo
modifica la entrada del clasificador de retraso. Las tarifas se calculan con
reglas configurables, no mediante estos modelos.

| Operación | Ruta |
|---|---|
| Inferencia actual v2 | `POST /predict/delivery` |
| Recorrido completo simulado | `POST /demo/deliveries` |
| Consultar pedidos e historial | `GET /orders`, `GET /orders/{order_id}` |
| Documentación HTTP | `GET /docs` |
| Estado del servicio y disponibilidad de los modelos | `GET /health` |

`model_available` de `/health` indica si están cargados los modelos de duración
y riesgo. La única ruta de predicción es `/predict/delivery`; `/predict` se retiró.
Las respuestas HTTP usan `experimental=true` para identificar estimaciones
pendientes de validación local.
Los endpoints generales conservan sus requisitos de cotización; la aceptación
de `/demo/deliveries` corresponde únicamente al recorrido simulado.

## Detener, volver a iniciar y revisar errores

Con las variables exportadas del inicio rápido y los mismos archivos Compose:

```bash
docker compose -f compose.yaml -f compose.s3.yaml logs --tail=40 api mongo-init
docker compose -f compose.yaml -f compose.s3.yaml down
```

`down` conserva el volumen. Para volver a iniciar, repetí el paso 2 y luego el
comando de demo. `down --volumes` borra los datos locales del proyecto; no usarlo
si querés conservarlos. Los perfiles y pesos de S3 permanecen fuera del volumen.

| Problema | Comprobar |
|---|---|
| No conecta al puerto 8000 | Que los contenedores estén iniciados. Si está ocupado, usar `DELIVERY_API_PORT=8001` al iniciar y `python3 scripts/demo_delivery.py --url http://127.0.0.1:8001`. |
| Predicción 503 | Perfil, lectura S3, manifiesto/SHA/tamaño y logs de API. No se sustituyen pesos inválidos. |
| Permiso denegado al perfil | Ruta `.aws`, perfil elegido y UID/GID exportados del usuario propietario. |
| `/demo/deliveries` devuelve 404 | Reiniciar con `DELIVERY_DEMO_ENABLED=1`. |
| Entrada 422 | Consultar esquema en `/docs`; fecha ISO con zona, coordenadas válidas y plazo positivo. |
| Sin acceso a S3 | Usar el modo local con un bundle propio verificado descrito abajo; no habrá inferencia sin pesos compatibles. |

## Alternativas de ejecución

**Solo local:** con v2 propio en
`models/delivery-duration/meituan-eta-risk-v2/`, ejecutar
`DELIVERY_DEMO_ENABLED=1 docker compose up --build -d --wait`. Usa MongoDB y
pesos locales; no necesita credenciales AWS. El bundle no está incluido en Git.

**Python sin contenedor:** instalar Python 3.12.14 y uv; desde la raíz:

```bash
uv sync --locked --python 3.12.14
uv run --locked --env-file .env python -m delivery.database.connection
DELIVERY_DEMO_ENABLED=1 uv run --locked --env-file .env uvicorn delivery.main:app --host 127.0.0.1 --port 8000
```

Esta alternativa usa `MONGODB_URI` y `MONGODB_DATABASE` privados configurados en
`.env` (por ejemplo Atlas), con un replica set accesible y permisos de esquema.
El primer comando Mongo prepara explícitamente validadores/índices; no es una
migración automática. La API no carga `.env` por sí sola: lo hace `uv --env-file`.
Detener el contenedor API si ocupa el mismo puerto. No se requiere esta instalación
completa para usar la imagen Docker de inferencia.

**AWS futuro:** la imagen usará el mismo manifiesto S3 con directorio/perfil
vacíos y rol IAM con lectura del prefijo del bundle. No se monta el perfil
personal. Antes de desplegar deben definirse la infraestructura, los permisos
y el presupuesto. Este inicio rápido no crea infraestructura AWS.

## Resultados, notebooks y reproducción

| Modelo v2 seleccionado por validación temporal | Resultado de test |
|---|---|
| ETA: HistGradientBoostingRegressor | MAE **7.37 min**, RMSE **9.88 min**, R² **0.358** |
| Riesgo: HistGradientBoostingClassifier | ROC AUC **0.648**, log-loss **0.404**, Brier **0.123** |

La ETA usa distancia aproximada y calendario; riesgo añade el plazo prometido.
Se entrenó con 409,083 pedidos y evaluó con 136,799 (399 purgados). El test ya se
había observado: esta mejora es exploratoria. Son datos chinos, la escala 1e6
se documenta como inferencia de codificación y falta validación para El Salvador,
tráfico o bicicleta/moto. El clasificador tiene discriminación modesta; no es
una garantía de entrega ni una probabilidad calibrada para el entorno local.

- [Notebook 01](notebooks/01_datos_y_procesamiento.ipynb): adquisición, calidad y procesamiento.
- [Notebook 02](notebooks/02_modelado_y_evaluacion.ipynb): baseline, comparación ML/MLP y experimento temporal v1.
- [Notebook 03](notebooks/03_eta_y_riesgo.ipynb): revisión v2, métricas y consultas por recorrido/plazo.
- [Datos y ML](docs/DATA_ML.md): fuentes/licencia, metodología y entrenamiento reproducible.
- [Arquitectura](docs/ARCHITECTURE.md) y [especificación](docs/SPEC.md).

## Organización del backend

```text
backend/src/delivery/
├── main.py          # Crea FastAPI y registra las rutas
├── routers/         # Endpoints: negocios, pedidos, repartidores, predicciones
├── schemas/         # Datos de las solicitudes y respuestas HTTP
├── models/          # Entidades, estados y validaciones de los datos
├── services/        # Operaciones y reglas del negocio
├── repositories/    # Consultas y escrituras de pedidos, catálogos y efectivo
├── database/        # Conexión, documentos y esquema de MongoDB
├── ml/              # Carga y ejecución de modelos entrenados
└── storage/         # Archivos en S3
```

El recorrido para exponer es: **ruta → servicio → repositorio → MongoDB**.
Por ejemplo: `routers/orders.py` → `services/orders.py` →
`repositories/orders.py`. `models/` representa los datos y `schemas/` define
lo que acepta/devuelve HTTP. `startup.py` prepara modelos/conexiones al arrancar;
`dependencies.py`, `errors.py` y `validation.py` reúnen utilidades de FastAPI.

Entrada principal: `delivery.main:app`. La entrada anterior `delivery.api.app:app`
se conserva como alias para procesos que ya estaban configurados; no hay una
segunda aplicación ni una segunda implementación de las rutas. MongoDB se
prepara explícitamente con `python -m delivery.database.connection`.

La suite principal contiene **exactamente 10 pruebas unitarias**, conservadas
por su cobertura de registro, estados, concurrencia, precios, vehículos, rutas,
asignación, efectivo, proyección y distancia. Está en `backend/tests/unit/`;
se eliminaron las demás pruebas del backend. Las verificaciones de experimentos
ML permanecen separadas en `ml/tests/` y no forman parte de la suite predeterminada.

Ejecutar las diez pruebas:

```bash
uv run --locked pytest backend/tests/unit -q
```

Datos, pesos, recibos de demo y ZIP de fuentes se guardan en directorios ignorados
`data/` y `models/`; credenciales en `.env`/perfiles fuera de Git. S3 conserva
bundles y snapshots privados bajo `models/`, `docs/` y metadatos bajo `datasets/`;
los CSV Meituan permanecen locales conforme a las condiciones documentadas.
El modelo no entrena durante el arranque o la inferencia.
