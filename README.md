# Asistente de Delivery Económico

Proyecto académico de entregas simuladas con FastAPI, MongoDB y modelos de
Machine Learning entrenados con datos reales de Meituan. La demo actual permite
recorrer un pedido hasta la entrega del efectivo y consultar **duración estimada
y riesgo de retraso**. Next.js y el despliegue AWS están pendientes.

**Reporte para lectura y entrega:** [PDF](reports/Reporte_Tecnico_Asistente_Delivery.pdf) · [Word editable](reports/Reporte_Tecnico_Asistente_Delivery.docx).

**Evidencias para la entrega:** [Anexo PDF](reports/Anexo_Evidencias_Asistente_Delivery.pdf) · [Word editable](reports/Anexo_Evidencias_Asistente_Delivery.docx) · [Paquete completo ZIP](reports/Entrega_Asistente_Delivery.zip).

**Presentación para la defensa:** [PowerPoint editable con notas](reports/Presentacion_Defensa.pptx) · [PDF](reports/Presentacion_Defensa.pdf).

**Guion y demostración:** [Guía PDF](reports/Guia_Exposicion_y_Demo.pdf) · [Word editable](reports/Guia_Exposicion_y_Demo.docx).

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
| Proceso y disponibilidad del predictor antiguo v1 | `GET /health` |
| Experimento temporal v1, conservado por compatibilidad | `POST /predict` |

`model_available` de `/health` describe v1: puede ser falso en un clon sin ese
bundle local aunque v2 funcione desde S3. Comprobá v2 con `/predict/delivery`.
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
uv run --locked --env-file .env python -m delivery.adapters.mongo
DELIVERY_DEMO_ENABLED=1 uv run --locked --env-file .env uvicorn delivery.api.app:app --host 127.0.0.1 --port 8000
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

Verificación unitaria mínima existente, si instalaste el entorno Python:

```bash
uv run --locked pytest backend/tests/test_domain.py -q
```

Datos, pesos, recibos de demo y ZIP de fuentes se guardan en directorios ignorados
`data/` y `models/`; credenciales en `.env`/perfiles fuera de Git. S3 conserva
bundles y snapshots privados bajo `models/`, `docs/` y metadatos bajo `datasets/`;
los CSV Meituan permanecen locales conforme a las condiciones documentadas.
El modelo no entrena durante el arranque o la inferencia.
