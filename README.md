# Asistente de Delivery Económico

Proyecto integrador de Python, Ciencia de Datos y Machine Learning. Equipo de dos integrantes. El repositorio comienza con **documentación operativa**, no con una aplicación previamente implementada: los agentes crearán el código al ejecutar cada tarea.

## Modelos actuales: duración y riesgo de retraso

La revisión `meituan-eta-risk-v2` ejecuta **dos modelos entrenados**:

- ETA: usa distancia origen–destino y hora/día UTC para estimar minutos creación–entrega.
- Riesgo: añade el plazo prometido para estimar la probabilidad de entregarlo tarde.

Selección mediante tres folds temporales. En los 136,799 pedidos de test, la ETA
obtuvo **MAE 7.37 min y R² 0.358**, frente a MAE 9.13 de la versión solo temporal.
Riesgo: ROC AUC **0.648**; mejora sobre la referencia, con discriminación modesta.
La revisión reutiliza un test ya observado y sigue sin validación para El Salvador.
No aprende tráfico o diferencias por vehículo. Distancias aproximadas basadas en
la aclaración oficial de Meituan; la codificación 1e6 se documenta como inferencia.

Consultar `POST /predict/delivery` en `/docs`, con fecha, origen, destino y
`promised_minutes`. `/predict` conserva el experimento temporal v1 por compatibilidad.
La demo completa usa **v2** y devuelve también el riesgo en `delivery_prediction`.
La API carga `DELIVERY_MODEL_V2_DIR` al iniciar; Compose monta el bundle local.
V2 aún no se publica en S3; los objetos anteriores son de v1.

Entrenamiento reproducible (la salida debe ser nueva):

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 uv run --locked python ml/experiments/train_delivery_v2.py \
  --data-root data --output models/delivery-duration/meituan-eta-risk-v2
```

Resultados/alcance en `docs/DATA_ML.md`; notebook explicativo:
`notebooks/03_eta_y_riesgo.ipynb`. Los bundles incluyen hashes, entorno y métricas
reales. No se reentrena al atender peticiones.

## Demostración completa para la exposición

El flujo puede ejecutarse por HTTP con el modelo entrenado y MongoDB local:

```bash
DELIVERY_DEMO_ENABLED=1 docker compose up --build -d --wait
python scripts/demo_delivery.py
```

Abrir http://127.0.0.1:8000/docs. El endpoint optativo
`POST /demo/deliveries` ejecuta solicitud, cotización, confirmación, asignación,
recogida, entrega, cobro y entrega de efectivo, y libera al repartidor.
El modelo T19 debe estar disponible en `models/`, como indica T34.

El comando guarda los parámetros y resultados de esa ejecución en
`data/reports/presentation/demo_result.json`: versión/duración del modelo,
distancia, desglose de importes, historial, recorrido, conversación y efectivo.
Negocio/repartidor/pedido/asignación/efectivo quedan en el volumen MongoDB local;
la cotización completa y su configuración se conservan en el recibo JSON.
Cada ejecución genera IDs nuevos `demo-`; no sobrescribe anteriores.

`examples/demo_delivery.json` contiene únicamente valores de ejemplo, incluidos
ubicaciones, tarifas, límites y carga: son datos simulados para exponer, no tarifas
o cobertura de El Salvador. La duración procede del modelo real y conserva sus
limitaciones. Ningún dato demo se añade al entrenamiento. El endpoint acepta
explícitamente estos parámetros, no establece tarifas predeterminadas.

La aceptación se limita a ese recorrido simulado y no cambia los requisitos de
los endpoints generales. Los pasos son consecutivos: si falla uno, consultar el
pedido y sus eventos; no se promete rollback global ni reanudación del recorrido.
La demo está deshabilitada por defecto y se habilita explícitamente en el Compose
local de loopback. `docker compose down` detiene la demo conservando sus datos.

## Qué se construirá

Un MVP para pequeños comedores, pupuserías y negocios de almuerzos/cenas sin repartidor propio. Simula solicitudes por WhatsApp, cotiza envíos locales, gestiona entregas individuales/agrupadas, asigna repartidores simulados en bicicleta o motocicleta, registra efectivo ficticio y muestra resultados en Next.js. La predicción de duración usará **datos reales verificables** y modelos ML/DL evaluados; los costos comerciales se calculan por reglas explícitas, no por resultados fabricados.

## Documentación y configuración base

| Archivo | Para qué sirve |
|---|---|
| `README.md` | Introducción y comienzo rápido para ambos |
| `AGENTS.md` | Reglas compartidas para Codex o Claude Code |
| `docs/SPEC.md` | Requisitos y flujo de negocio del MVP |
| `docs/ARCHITECTURE.md` | Componentes, interfaces, datos, S3 y despliegue |
| `docs/DATA_ML.md` | Guía de obtención, procesamiento y ML/DL |
| `docs/TASKS.md` | 54 tareas, responsables y pasos de inicio verificables |
| `.env.example` | Variables de entorno no secretas |
| `.gitignore` | Exclusiones de Git |

Este paquete conserva los nombres y asignaciones reflejados en la última copia disponible del backlog de 54 tareas. **La hoja Excel compartida sigue siendo la fuente de verdad** para nuevos cambios de responsables, estados y prioridades.

## Configuración de AWS ya decidida

- S3 bucket **existente**: `ml-kodigo-resources`
- Región: `us-east-1`
- Prefijos: `datasets/`, `models/`, `docs/`
- No crear ni borrar el bucket. No subir objetos ni cambiar IAM sin aprobación.
- MongoDB se utilizará para entidades y estados del negocio; S3 para archivos/datasets/modelos.

## Inicio de ambos integrantes

1. Descomprimir en una carpeta `whatsapp-delivery/`.
2. Integrante que crea el repositorio: `git init` (o crear directamente el repositorio remoto y clonarlo); revisar `.gitignore`.
3. Ambos deben trabajar sobre **el mismo repositorio remoto** y consultar `AGENTS.md` y `docs/TASKS.md`.
4. Crear ramas por bloque pequeño desde `origin/main` actualizado, por ejemplo `data/T05-T07-datos`; trabajar una tarea a la vez y usar un PR para integrar el bloque. Ver el flujo vigente y la checklist en `docs/TASKS.md`.
5. Revisar cambios y pruebas antes de integrarlos a la rama compartida. No ejecutar despliegues AWS para probar tareas iniciales.

### Primer prompt del integrante Ruben (T01)

> Lee `AGENTS.md`, `README.md`, `docs/SPEC.md`, `docs/ARCHITECTURE.md` y `docs/TASKS.md`. Implementa exclusivamente T01, respetando los criterios de aceptación. No hagas commits automáticos, no implementes otras tareas y al final muestra archivos cambiados y verificaciones realizadas.

### Primer prompt del integrante Guillermo (T05)

> Lee `AGENTS.md`, `docs/SPEC.md`, `docs/DATA_ML.md` y `docs/TASKS.md`. Trabaja exclusivamente en T05: investiga y verifica fuentes reales de entregas adecuadas para el objetivo candidato. Documenta las fuentes, licencia, accesibilidad, variables y evidencia; no inventes etiquetas ni entrenes modelos todavía. No cambies archivos de arquitectura ajenos ni subas nada a S3 sin permiso.

**Importante para trabajo paralelo:** Guillermo puede investigar T05 de inmediato, pero debe esperar a que el repositorio/base esté compartido para incorporar su documentación. Ruben puede seguir con T02–T04 mientras se validan fuentes de datos.

## Orden de lectura para cualquier agente

1. `AGENTS.md`
2. `docs/TASKS.md` (tarea exacta y responsable)
3. `docs/SPEC.md` (reglas del negocio)
4. `docs/ARCHITECTURE.md` (contratos e integración)
5. `docs/DATA_ML.md` (para tareas de datos/ML)

Las guías académicas oficiales del curso prevalecen sobre estas notas. El equipo confirmará con el docente el alcance permitido de la asistencia mediante agentes antes de presentar el trabajo.

## Estructura inicial — T01

```text
backend/
  src/delivery/      # Base del código Python de dominio, servicios y API
  tests/             # Pruebas del backend
ml/
  data/              # Código de adquisición y ETL, no datasets versionados
  experiments/       # Código de entrenamiento y evaluación
frontend/            # Aplicación Next.js futura
infra/
  terraform/         # Infraestructura futura
docs/                # Especificación, arquitectura, datos y tareas compartidas
```

En T01 los directorios se reservaron con `.gitkeep` para conservarlos en Git.
T02 incorpora el paquete Python y las primeras pruebas del entorno.
Las capas internas del backend se describen en `docs/ARCHITECTURE.md` y se
crearán al abordar sus tareas. T30 incorpora FastAPI; MongoDB y S3 se integrarán posteriormente;
Docker/Compose se incorporarán en T34 y Terraform en T42.

T01 no incluye una aplicación ejecutable, dependencias instaladas, endpoints,
datos ni modelos. El entorno Python y pytest corresponden a T02; Next.js comienza
en T47. `.env.example` contiene solo la región y el bucket existente acordados,
sin claves ni conexiones. Los datos locales deben guardarse en las rutas
ignoradas `data/`, `ml/data/raw/`, `ml/data/processed/` o `ml/data/splits/`; los
artefactos, en `models/`, `artifacts/` o `ml/experiments/artifacts/`.

El remoto `origin` está configurado en
`https://github.com/rvigil24/ml-delivery-app.git`. La base de T01 está en el commit
`9b9f696`, publicado por Ruben en `feat/T01-estructura`. El flujo actual agrupa
2–3 tareas relacionadas en una rama y un PR. La orden «cerrá el bloque» autoriza
el cierre completo descrito en `docs/TASKS.md`; los agentes no publican ni integran
cambios sin esa orden o una instrucción explícita equivalente.
Por indicación de Ruben, T01 no requiere aprobación de Guillermo. Esta excepción
aplica únicamente a T01; el backlog no se actualiza automáticamente.

## Entorno Python — T02

Requisitos: Python **3.9+** y [uv](https://docs.astral.sh/uv/getting-started/installation/).
Para el trabajo local se selecciona Python **3.12** en `.python-version`.
Si esa versión no está instalada, uv puede descargarla al sincronizar.
No se requiere pip global ni activar el entorno para usar los comandos siguientes.

Desde la raíz del repositorio:

```bash
uv sync --locked
uv run --locked pytest -v
uv pip check
uv lock --check
```

`uv sync --locked` crea `.venv/`, instala el paquete `delivery` en modo editable
y las dependencias de desarrollo. `pyproject.toml` declara Python y dependencias;
`uv.lock` fija las versiones y hashes para cada versión de Python/plataforma
compatible. Ambos archivos deben compartirse. La opción `--locked` impide
actualizar el archivo de bloqueo automáticamente; ver la
[documentación de sincronización de uv](https://docs.astral.sh/uv/concepts/projects/sync/).
Cuando una tarea requiera cambiar dependencias, se actualizarán deliberadamente
`pyproject.toml` y `uv.lock` juntos.

Dependencias directas actuales: **boto3**, **Pandas**, **Matplotlib**, **Dask DataFrame**,
**PySpark**, **scikit-learn**, **PyTorch**, **FastAPI**, **Pydantic**, **PyMongo** y **Uvicorn**.
El grupo `dev` incluye pytest y el cliente de pruebas HTTP compatible con Python
(HTTPX en 3.9/3.10, HTTPX2 desde 3.11). Hatchling construye/instala el paquete.
Las herramientas de frontend se incorporarán en sus tareas.

Las pruebas de `backend/tests/test_environment.py` comprueban la instalación del
paquete y la preparación local del cliente S3. La segunda prueba bloquea la
búsqueda de credenciales y las conexiones de red; usa firma deshabilitada solo
para inspeccionar el modelo local del SDK y no ejecuta operaciones sobre S3.
No se carga `.env` ni se necesita un perfil AWS para estas comprobaciones.
La integración autenticada con S3 corresponde a tareas posteriores.

Validación realizada en T02:

- `uv lock` y `uv sync --locked`: resolución e instalación completadas.
- `uv run --locked pytest -v`: **2 passed** en Python **3.12.14**.
- Instalación con `uv sync --locked --python 3.9` en un entorno temporal mediante
  `UV_PROJECT_ENVIRONMENT`, seguida de `python -m pytest -v` con su intérprete:
  **2 passed** en Python **3.9.25**. El entorno temporal se eliminó después.
- `uv pip check`: dependencias instaladas compatibles.
- `uv lock --check`: archivo de bloqueo actualizado.
- `git diff --check`: sin errores de espacios en los cambios existentes.

Estas pruebas verifican el entorno, no conectividad ni permisos reales de AWS.

## Adquisición local de datos — T06

Ruben seleccionó Meituan para el experimento académico. Desde la raíz:

```bash
uv run --locked python ml/data/acquire_meituan.py
uv run --locked pytest -q
```

La receta descarga una revisión fija del ZIP y su licencia, comprueba SHA-256 y
conserva el original y un manifiesto en `data/raw/meituan/<revision>/`, ignorado
por Git. Si la copia ya existe, la verifica sin descargar ni sobrescribir.
Requiere conexión a Internet únicamente para la primera adquisición y no utiliza
credenciales. Ver origen, condiciones de uso, inventario y diccionario en
[`docs/DATA_ML.md`](docs/DATA_ML.md).

La adquisición actual es local y académica; no se redistribuyen registros.
El diseño mantiene S3 privado para los artefactos autorizados. La compatibilidad
del uso de Meituan y de modelos derivados con ese alojamiento se verificará antes
de la primera subida; no existe una prohibición automática de AWS por esta receta.
La validación del target/calidad corresponde a T07; aún no hay un modelo ni
desempeño validado para El Salvador.

## Auditoría de datos — T07

```bash
uv run --locked python ml/data/audit_meituan.py
```

El comando comprueba el hash del original y genera un informe agregado en
`data/reports/meituan/<revision>/t07_audit.json`, ignorado por Git. La auditoría
aprobó con condiciones preparar 546,281 pedidos inmediatos; T08 materializa
la cohorte según esos criterios. Ver criterios, exclusiones, estadísticas y riesgos de leakage en
[`docs/DATA_ML.md`](docs/DATA_ML.md). Las unidades geográficas siguen pendientes
antes de construir features de distancia; no hay entrenamiento realizado.

## Preparación con Pandas — T08

```bash
uv sync --locked
uv run --locked python ml/data/prepare_meituan.py
uv run --locked pytest -q
```

La receta requiere el original adquirido y la auditoría T07. Genera
`data/processed/meituan/<revision>/t08-v1/orders.csv` y `manifest.json`, ignorados
por Git. Materializa 546,281 pedidos y 11 columnas, con duración en minutos y
hora/día de solicitud UTC. Las coordenadas se conservan como `*_raw`, sin
convertirlas a grados o kilómetros. Ver transformaciones y evidencia en
[`docs/DATA_ML.md`](docs/DATA_ML.md).

## Análisis exploratorio — T09

```bash
uv run --locked python ml/data/explore_meituan.py
```

Comprueba el CSV T08 y genera `t09_eda.json`, `t09_eda.md` y cuatro PNG en
`data/reports/meituan/<revision>/t09/`, ignorado por Git. Incluye calidad,
distribución completa y detalle hasta P99, contexto horario/semanal UTC,
cobertura por fecha y correlaciones descriptivas. El CSV conserva todas sus filas.
La mediana observada es 27.90 minutos y el P95 51.43; las limitaciones de la
muestra y la exposición temporal desigual están documentadas en el informe.

## Equivalencia con Dask — T10

```bash
uv sync --locked
uv run --locked python ml/data/compare_dask_meituan.py
```

Dask lee el mismo original en siete particiones, valida IDs globales y reúne
los intentos de cada pedido mediante shuffle antes de aplicar las reglas T08.
La comparación verifica todos los valores de las 546,281 filas/11 columnas y
el mismo SHA-256 del CSV Pandas. El informe queda en
`data/reports/meituan/<revision>/t10_dask.json`, fuera de Git. Se ejecuta localmente
con dos hilos; la salida final se reúne en memoria para comprobarla. T10 no mide
velocidad ni demuestra escalabilidad ilimitada; los tiempos corresponden a T12.

## Equivalencia con PySpark local — T11

Requiere **Java 17** disponible mediante `JAVA_HOME`/`PATH` y el entorno Python del proyecto:

```bash
java -version
uv sync --locked
uv run --locked python ml/data/compare_spark_meituan.py
```

Spark SQL ejecuta validaciones, agrupaciones, ventanas, join y transformaciones
UTC en `local[2]`, sin clúster remoto. Sobre el original lee ocho particiones y
obtiene los mismos 546,281 pedidos/11 columnas de Pandas. `collect()` materializa
la salida para comparar valores exactos y generar un CSV normalizado temporal
con el mismo hash T08; no se compara el formato CSV nativo de Spark.
Informe: `data/reports/meituan/<revision>/t11_spark.json`, ignorado por Git.
Se conserva la referencia intacta; rendimiento y tiempos corresponden a T12.

## Comparación de tiempos — T12

```bash
uv run --locked python ml/data/benchmark_meituan.py
```

Ejecuta tres rondas en procesos nuevos, rota el orden y verifica valores/hash
de cada resultado. Genera `t12_benchmark.json`, `t12_muestras.csv`,
`t12_benchmark.md` y `t12_tiempos.png` en
`data/reports/meituan/<revision>/t12/`, ignorado por Git.

Medianas observadas del pipeline: **Pandas 3.708 s**, **Dask 6.250 s** y
**Spark 25.138 s**. Incluyen lectura, validaciones, transformación y salida
materializada/ordenada. El arranque se mide aparte; no se confunde construir
un grafo con ejecutarlo. Nueve resultados coinciden con los 546,281 pedidos T08.
Entorno: Ryzen 5 5600H, Linux, 12 CPU lógicas, Python 3.12.14; hardware,
versiones, muestras y límites completos en el informe. Estas cifras describen
este dataset/equipo/configuración; no prueban superioridad general.

`--reuse` permite mostrar una medición previa solo si coinciden código, datos,
versiones y hardware; conserva y muestra su fecha. El comando sin esa opción
mide nuevamente. En Colab las cifras se calcularán con su propio entorno.

## Variables y partición temporal — T13

```bash
uv run --locked python ml/data/prepare_model_data.py
```

Genera `train.csv`, `test.csv`, `purged.csv` y `manifest.json` en
`data/splits/meituan/<revision>/t13-temporal-v1/`, ignorado por Git.
Entrenamiento: **409,083 pedidos**; prueba: **136,799**; otros **399** se registran
aparte porque todavía no habían terminado al corte `2022-10-23T00:00:00Z`.
Los IDs son disjuntos y todas las etiquetas de entrenamiento son anteriores al corte.

Los cuatro predictores son seno/coseno de hora y día UTC, con períodos fijos de
24 horas y 7 días. `model_xy` selecciona solo esa lista, separando target y
trazabilidad; no incorpora llegada, IDs ni coordenadas sin unidades confirmadas.
Es una versión experimental temporal: no describe rutas o diferencias de vehículo
ni garantiza capacidad predictiva. El EDA previo vio la cohorte completa; el test
no se presenta como ciego a esa exploración. T13 prepara los datos; el ajuste
de la referencia se realiza en T14.

Repetir el comando verifica las copias sin sobrescribir. Cambiar receta,
intérprete o corte requiere una versión nueva mediante `--output`; `--test-start`
permite un corte ISO con zona horaria explícita. Ver protocolo y controles en DATA_ML.

## Modelo de referencia — T14

```bash
uv sync --locked
uv run --locked python ml/experiments/evaluate_baseline.py
```

Ajusta `DummyRegressor(strategy="median")` solo con entrenamiento: predice
**27.75 minutos** para todos los pedidos. La estrategia se fija antes de evaluar
test, con MAE como métrica principal; no se elige entre alternativas por sus errores.

| Conjunto | Pedidos | MAE (min) | RMSE (min) |
|---|---:|---:|---:|
| Entrenamiento | 409,083 | 9.260672 | 12.192908 |
| Prueba | 136,799 | 9.501230 | 12.562496 |

Informes JSON/Markdown en `data/reports/meituan/<revision>/t14_baseline.*`,
ignorados por Git, con hashes y versiones. La referencia ignora las variables;
sirve para comparar modelos futuros, sin prometer desempeño local ni por vehículo.
Los errores son minutos, no porcentajes de exactitud. T19 decidirá persistencia
del modelo final; este paso no integra API ni AWS.

## Tres familias ML — T15

```bash
uv run --locked python ml/experiments/train_models.py
```

Entrena regresión lineal, Random Forest y LinearSVR sobre los **409,083 pedidos
de train**, con las mismas cuatro variables T13. Los pipelines ajustan el
escalado solo con train. LinearSVR permite usar todo train con kernel lineal;
no equivale a SVR con kernel RBF. No se cargan ni evalúan las etiquetas de test.

| Modelo | MAE train (min) | RMSE train (min) |
|---|---:|---:|
| Regresión lineal | 9.326470 | 12.032238 |
| Random Forest | 8.876510 | 11.531344 |
| LinearSVR | 9.327745 | 12.032244 |

Son **errores de entrenamiento**, no evidencia de generalización ni selección
de un ganador. Informes con parámetros, versiones y hashes en
`data/reports/meituan/<revision>/t15_models.{json,md}`, fuera de Git.
T16 aplica validación/tuning dentro de train; T18 comparará generalización
y T19 decidirá la persistencia final. No se añadieron dependencias.

## Validación temporal y tuning — T16

```bash
uv run --locked python ml/experiments/tune_models.py
```

Tres folds diarios (20, 21 y 22 de octubre de 2022, UTC) dentro de train.
Cada ajuste utiliza solo pedidos anteriores cuya entrega ya se conocía al corte;
el escalado se aprende dentro de cada fold. Búsqueda pequeña: profundidad 6/12
del bosque y C=0.1/1 de LinearSVR. Regresión lineal y mediana son controles.

| Modelo | MAE medio CV (min) | RMSE medio CV (min) |
|---|---:|---:|
| Baseline | 9.335848 | 12.350835 |
| Regresión lineal | 9.337751 | 12.115916 |
| Random Forest (profundidad 6) | 8.955647 | 11.658948 |
| LinearSVR (C=0.1) | 9.338523 | 12.115426 |

Se eligen parámetros por MAE medio con igual peso por día. Son resultados de
validación usados para seleccionar, no una evaluación independiente del modelo
elegido. Informes con todos los candidatos/folds y hashes en
`data/reports/meituan/<revision>/t16_validation.{json,md}`. Test no se carga;
la comparación posterior y persistencia final siguen en T18/T19.

## MLP pequeña — T17

```bash
uv sync --locked --extra notebooks
uv run --locked python ml/experiments/train_mlp.py
```

PyTorch **2.8 CPU**, instalado desde su índice oficial, entrena una red
`4 → 16 ReLU → 8 ReLU → 1 lineal` de **225 parámetros**. Escala entradas y
target solo con el entrenamiento de cada fold y devuelve predicciones en minutos.
No requiere GPU ni paquetes CUDA. Se incorpora PyTorch porque T17 requiere una
red implementada con un framework de deep learning.

En los tres folds T16 se prueban hasta 30 épocas con configuración fija.
La menor media de MAE interno eligió **7 épocas**: MAE CV **9.065874 min**,
RMSE CV **11.792678 min**. Se reajusta desde cero con todo train durante esas
7 épocas. Son resultados de selección interna; test sigue reservado.

Informes e historiales en `data/reports/meituan/<revision>/t17_mlp.{json,md}`.
El notebook genera también `t17_learning_curves.png`, fuera de Git. La comparación
posterior y persistencia corresponden a T18/T19.

## Comparación sobre test — T18

```bash
uv run --locked python ml/experiments/compare_models.py
```

Requiere informes T16/T17 con hashes/versiones vigentes. Ajusta los cinco modelos
con todo train, fijando previamente los parámetros/épocas elegidos por CV, y
después carga el mismo test de **136,799 pedidos**. No vuelve a hacer tuning.

| Modelo | MAE test (min) | RMSE test (min) | R² |
|---|---:|---:|---:|
| Baseline | 9.501230 | 12.562496 | -0.038054 |
| Regresión lineal | 9.509476 | 12.290476 | 0.006414 |
| Random Forest | 9.125362 | 11.855652 | 0.075474 |
| LinearSVR | 9.510380 | 12.290099 | 0.006475 |
| MLP | 9.121785 | 11.917718 | 0.065769 |

MLP y bosque tienen MAE casi iguales; el bosque tiene menor RMSE. El R² es bajo
y los errores siguen siendo relevantes. No se demuestra precisión operativa en
El Salvador ni superioridad estadística de una diferencia pequeña.
JSON/Markdown con sesgo, P95 absoluto y errores por día en
`data/reports/meituan/<revision>/t18_comparison.*`; el notebook exporta
`t18_model_comparison.png`. T19 decidirá selección/persistencia sin retocar
hiperparámetros con estas cifras de test.

## Modelo final académico — T19

```bash
uv run --locked python ml/experiments/export_model.py
```

Selecciona **Random Forest de profundidad 6** por menor MAE de validación interna
(8.955647 min). Se conserva esa regla aunque la MLP obtuviera MAE de test apenas
menor. Reajusta solo con train y guarda, fuera de Git:

```text
models/delivery-duration/meituan-temporal-rf-v1/
  pipeline.pkl       # Transformación temporal + bosque
  metadata.json      # Versión, contrato, hashes, entorno y métricas
  evidence.json      # Copias de evidencia T16–T18
  model_card.md      # Selección, procedencia, uso y limitaciones
```

El pipeline recibe `request_hour_utc` y `request_weekday_utc` (lunes=0), transforma
a las cuatro variables cíclicas y devuelve minutos. Se carga con
`delivery_ml.artifact.load_pipeline(Path("models/delivery-duration/meituan-temporal-rf-v1"))`.
No requiere entrenar para predecir. La recarga verifica hashes/entorno y reproduce
las predicciones sobre train con tolerancia absoluta 1e-12 min.

Una repetición verifica la misma receta sin sobrescribir; cambios requieren otra
versión con `--output`. No añade dependencias: usa pickle de Python. Cargar solo
artefactos propios de confianza y con el mismo código/entorno; pickle puede ejecutar
código y los hashes no autentican su origen. El modelo conserva R² bajo y errores
relevantes: uso académico local, sin validación operativa ni publicación en S3.

## Pedidos y estados — T20

`delivery.services.orders.OrderService` registra/consulta pedidos y aplica el
flujo aprobado, con historial UTC y actualizaciones por estado esperado.
Los adaptadores en memoria se componen con un catálogo explícito de negocios;
el servicio valida negocio, origen, unicidad y estado inicial solicitado.

Cancelación permitida solo desde solicitado/cotizado/confirmado. Se rechazan
saltos, retrocesos, repeticiones y estados obsoletos sin escribir. Cada avance
requiere un `TransitionRequirements` que acredite cotización/asignación válida;
sin ese validador queda bloqueado. T20 no fabrica esos requisitos ni configura
tarifas/zonas. Registrar no implica aceptar cobertura o emitir una cotización.

```bash
uv run --locked pytest backend/tests/test_orders.py -q
```

El repositorio actual es efímero y local al proceso; MongoDB sigue en T32 y
HTTP en T30. Contratos/matriz en `docs/ARCHITECTURE.md`. Los fixtures de prueba
y eventos simulados no son pedidos reales ni datos de entrenamiento.
Verificación: **55 pruebas aprobadas en Python 3.12**; las cinco nuevas también
en Python 3.9 con un entorno aislado de pytest y las fuentes del backend.

## Distancia y duración académicas — T21

`AcademicQuoteService` produce un borrador para un pedido solicitado:
distancia Haversine aproximada en km y duración del modelo T19 basada en hora/día
UTC de creación. No calcula rutas, tiempos por vehículo ni minutos desde km.
`LocalDurationPredictor` verifica/carga el bundle una vez y reutiliza el pipeline;
si falta o falla, devuelve un error explícito, sin inventar un tiempo.

```bash
uv run --locked pytest backend/tests/test_estimates.py -q
```

El resultado contiene `quote`, `academic_only=True`, `coverage_validated=False`
y limitaciones. La duración es creación–entrega experimental, sin validación
para El Salvador. El borrador no tiene importes, no se persiste ni cambia el
estado del pedido. Cobertura, tarifas y emisión comercial siguen pendientes;
T20 no permite avanzar por disponer únicamente de este borrador. No añade
dependencias ni usa mapas externos, HTTP o AWS.
Verificación: **60 pruebas aprobadas en Python 3.12**, las cinco nuevas también
en Python 3.9, e integración con el modelo real usando entradas ilustrativas
separadas de los experimentos ML, sin reentrenar ni modificar el pedido.

## Desglose académico de importes — T22

`PricingService` recibe el borrador T21, una `PricingPolicy` versionada y
`OperatorCosts` explícitos. Calcula tarifa/pago como base + importe por km ×
distancia; margen = tarifa − pago − costos variable/atribuible del operador.
No incluye nuevamente costos ya cubiertos por el pago al repartidor.

Todos los importes, moneda y unidad monetaria se suministran como configuración;
no hay tarifas reales predeterminadas. Usa Decimal/ROUND_HALF_UP, redondea
componentes y obtiene el margen de esos importes finales. Permite pérdidas.
Faltan política/costos → error, sin reemplazarlos por cero. La duración ML
no interviene en el cálculo.

```bash
uv run --locked pytest backend/tests/test_pricing.py -q
```

El resultado conserva política, costos, distancia y borrador originales,
`academic_only=True` y `coverage_validated=False`. No emite cotización ni cambia
estados. Los valores de las pruebas son fixtures, no tarifas o costos aprobados.
Verificación T22: **31 pruebas del backend aprobadas en Python 3.12** y las cinco
nuevas también en Python 3.9. Las pruebas ML no se repitieron porque su código
y artefactos no cambiaron.

## Reglas configurables de vehículos — T23

`VehicleRulesService` evalúa un pedido con carga explícita en kg y una
`VehiclePolicy` versionada. Requiere zona rectangular y máximos de km/kg para
bicicleta y moto, sin valores predeterminados. Ambos extremos deben estar dentro;
se incluyen bordes y valores iguales a los máximos. Usa distancia Haversine de
referencia, sin convertirla a tiempos por vehículo.

Devuelve ambos vehículos, uno o ninguno con motivos de rechazo, sin preferencia
ni asignación automática. Conserva pedido, política, carga y distancia usados;
no modifica estado/historial, precios ni el modelo ML. La zona configura una regla
académica para extremos, sin demostrar cobertura comercial o rutas por calles.

```bash
uv run --locked pytest backend/tests/test_vehicles.py -q
```

Verificación T23: **36 pruebas del backend aprobadas en Python 3.12** y las cinco
nuevas también en Python 3.9. Zonas/cargas/límites de tests son fixtures, no valores
recomendados. T26 sigue a cargo de asignar repartidores aprobados/disponibles.

## Sugerencia académica de rutas — T24

`RouteSuggestionService` recibe IDs de pedidos y un inicio explícitos, junto
con `RoutePolicy` versionada (máximo de pedidos y zona T23 obligatorios).
Usa vecino más cercano con Haversine, recogida antes de su entrega y desempate
por ID. Devuelve snapshots, paradas y tramos en km, sin volver automáticamente
al inicio. No fusiona paradas coincidentes ni omite pedidos inválidos.

```bash
uv run --locked pytest backend/tests/test_routes.py -q
```

Es una heurística académica, sin garantía de óptimo ni validación de capacidad,
tiempos o recorrido vial. No agrupa automáticamente, asigna, reserva o cambia
pedidos/precios/ML. Los pedidos ya asignados, recogidos o terminales se rechazan.
Verificación: **41 pruebas del backend aprobadas en Python 3.12** y las cinco
nuevas también en Python 3.9; sin repetir entrenamientos o pruebas ML intactas.

## Comparación académica de costos — T25

`CostComparisonService` usa los mismos snapshots, inicio y políticas T22/T24
para rutas individuales abiertas independientes y una agrupada. Exige costos
explícitos por individual y para el grupo, en la misma moneda. Pago del repartidor
= una base por recorrido + pago/km × longitud completa. Total del operador:
pago + costo variable + atribuible. Conserva desgloses y diferencias individual menos
grupo, también negativas. No compara ingresos, tarifas al cliente, margen o ROI.

```bash
uv run --locked pytest backend/tests/test_cost_comparison.py -q
```

Es un escenario académico sin retorno/reposicionamiento final, con extremos
posiblemente distintos y sin capacidad, recursos o rutas viales validados.
No garantiza ahorro ni asigna, reserva, cobra o cambia pedidos. Valores de
prueba son fixtures; no son costos observados ni recomendaciones comerciales.
Verificación T25: **46 pruebas del backend aprobadas en Python 3.12** y las cinco
nuevas también en Python 3.9; pruebas/entrenamientos ML intactos no se repiten.

## Asignación simulada de repartidores — T26

`AssignmentService.assign(assignment_id, courier_id, order_ids, start, loads_kg)`
reserva un grupo confirmado con un repartidor elegido por ID, aprobado y
disponible. Exige políticas T23/T24, cargas Decimal en kg y un validador explícito
de cotizaciones confirmadas. **Sin ese validador queda bloqueado**; los borradores
académicos no son cotizaciones comerciales válidas.

Comprueba zona, km Haversine de toda la ruta y pico de carga acumulada. Guarda
snapshots, políticas, cargas e historial UTC; no inventa posiciones o límites.
`InMemoryDispatchRepository` debe compartirse entre `OrderService` y
`AssignmentService`: una sola operación reserva todos los pedidos y ocupa al
repartidor, sin cambios parciales o duplicados. Para progresar se compone
`OrderService` con `DispatchOrderRequirements`; las recogidas/entregas siguen
las paradas planificadas. `release(id)` solo libera cuando todos estén entregados.
La atomicidad es local a un proceso; no hay persistencia ni viabilidad vial validada.

```bash
uv run --locked pytest backend/tests/test_assignments.py -q
```

Verificación T26: **53 pruebas del backend aprobadas en Python 3.12**, incluidas
siete nuevas, que también pasaron en Python 3.9. Los tests utilizan evidencia de
cotización y valores sintéticos exclusivamente como fixtures. Sin dependencias
nuevas, API, WhatsApp real, pagos ni AWS; ML y notebooks permanecen intactos.

## Solicitudes y mensajes simulados — T27

`WhatsAppSimulationService(orders)` recibe un `OrderService` ya configurado.
`request(order)` registra una solicitud estructurada con las validaciones T20;
`conversation(order_id)` devuelve el pedido y mensajes inmutables: detalles del
cliente, acuse y una actualización por cambio de estado aceptado. Usa las fechas
UTC del historial; consultar no agrega mensajes ni modifica pedidos.

```python
from delivery.services.whatsapp import WhatsAppSimulationService

chat = WhatsAppSimulationService(orders)  # OrderService con su repositorio y negocios.
conversation = chat.request(order)       # Order inicialmente solicitado, con ID único.
messages = chat.conversation(order.id).messages
```

La conversación se identifica como `whatsapp_simulado`, simulada y reconstruida
del historial; no es una bitácora de mensajes de red ni acredita el canal original.
No interpreta texto libre ni envía mensajes. Un registro inválido/duplicado falla
sin acuse de éxito. El acuse inicial deja cotización/cobertura pendientes y las
actualizaciones solo informan estados registrados, sin fabricar tarifas o tiempos.
La interfaz visual y sincronización se implementan en T48/T53.

```bash
uv run --locked pytest backend/tests/test_whatsapp.py -q
```

Verificación T27: **58 pruebas del backend aprobadas en Python 3.12**, incluidas
cinco nuevas; estas también pasan en Python 3.9. Sin nuevas dependencias,
credenciales, canales reales, API o infraestructura.

## Efectivo y estados contables simulados — T28

`CashService(repository, orders, quotes)` usa un repositorio de efectivo y el
repositorio de pedidos existente. `quotes` implementa `CashQuoteSource`: consulta
una cotización validada del mismo pedido, con importes. Sin esa fuente queda
bloqueado; los borradores académicos no la sustituyen.

`open(order_id)` guarda una expectativa pendiente por pedido, con ID de
cotización, moneda e importe del envío. `collect(order_id, currency, amount)`
registra el cobro completo tras entregar el pedido; `remit(...)` registra la
entrega íntegra al operador. `amount` debe ser Decimal finito no negativo, igual
al importe guardado; no hay redondeos nuevos, parciales, cambio, sobrepagos o
deducciones automáticas del pago al repartidor. Un cero explícito en una
cotización validada es admisible; la ausencia de importe nunca se sustituye por cero.

`InMemoryCashRepository` protege estado/historial UTC como una sola operación
local, sin sobrescribir aperturas ni duplicar eventos por reintentos. `get(id)`
devuelve un snapshot inmutable identificado como simulado. No modifica pedidos,
asignaciones o disponibilidad. Los términos guardados no se recotizan implícitamente.

```bash
uv run --locked pytest backend/tests/test_cash.py -q
```

Verificación T28: **64 pruebas del backend aprobadas en Python 3.12**, incluidas
seis nuevas, también aprobadas en Python 3.9. Cotizaciones/valores de tests son
fixtures. Sin dinero real, contabilidad general, API, MongoDB o dependencias nuevas.

## Escenario financiero académico — T29

`delivery.domain.finance` expone `FinancialScenario` y la función pura
`analyze_finances(scenario)`. Requiere período, volumen entero no negativo,
desglose unitario `QuoteAmounts` de T22, costos fijos adicionales, inversión y
unidad monetaria. Todo usa la moneda del desglose; no hay valores predeterminados.
Los costos fijos excluyen lo ya incluido por envío. Se exige margen conciliado
y entradas alineadas a la unidad monetaria, sin redondearlas silenciosamente.

El informe inmutable conserva el escenario y devuelve ingresos, pago/costos
agregados, contribución, costo total y resultado operativo. Resultado = volumen
× margen unitario − costos fijos adicionales. Equilibrio = menor volumen entero
con resultado ≥ 0; puede no existir con margen no positivo. Si no hay costos
fijos, el mínimo es cero, lo que no garantiza rentabilidad al aumentar volumen.
ROI simple del período (%) = resultado / inversión × 100; inversión cero devuelve
`None`. No se vuelve a restar la inversión como gasto operativo ni se anualiza.

```bash
uv run --locked pytest backend/tests/test_finance.py -q
```

Se conservan pérdidas. El equilibrio usa techo exacto; solo el porcentaje ROI
puede aproximarse a 28 dígitos significativos, ROUND_HALF_UP. Los demás cálculos
rechazan pérdida de precisión. No estima demanda, usa efectivo T28 como ingreso
adicional ni altera pedidos. Todo resultado lleva `academic_only=True` y
`demand_validated=False`: no es rentabilidad observada ni garantía de negocio.
Verificación T29: **69 pruebas del backend aprobadas en Python 3.12**, incluidas
cinco nuevas, también aprobadas en Python 3.9. Sin dependencias nuevas.

## API local de inferencia — T30

Desde la raíz, con el bundle T19 propio disponible en su entorno versionado:

```bash
uv sync --locked
export DELIVERY_MODEL_DIR="$PWD/models/delivery-duration/meituan-temporal-rf-v1"
uv run --locked uvicorn delivery.api.app:app --host 127.0.0.1 --port 8000
```

La API no carga `.env` automáticamente: usa la variable exportada. El bundle
no está versionado en Git; sin él, sin configuración o con entorno incompatible,
la API arranca con `model_available=false` y `/predict` devuelve 503. No descarga
ni entrena modelos. La carga se realiza una vez al arrancar mediante
[lifespan de FastAPI](https://fastapi.tiangolo.com/advanced/events/).

En otra terminal, ejemplo de entrada **ilustrativa**, no una entrega observada:

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' -d '{"requested_at":"2022-10-22T12:00:00-06:00"}'
```

`GET /health` comprueba proceso y carga inicial, sin certificar MongoDB/S3.
`POST /predict` solo acepta fecha de creación ISO 8601 con zona horaria; rechaza
campos adicionales. Devuelve fecha UTC, duración en minutos, fuente, intervalo
creación–entrega, versión y limitaciones académicas. El modelo usa hora/día UTC;
no distancia, vehículo, tarifa o tiempo de conducción. No está validado para
El Salvador y no emite una cotización comercial. T31 integra cotizaciones.

Documentación interactiva: `http://127.0.0.1:8000/docs`; esquema:
`http://127.0.0.1:8000/openapi.json`. Errores JSON con `detail.code/message`:
422 entrada inválida, 503 inferencia no disponible y 500 fallo inesperado,
sin exponer entradas o excepciones internas. Reiniciar tras corregir modelo/
configuración; no hay reintentos de carga por petición. Detener con Ctrl+C.

```bash
uv run --locked --extra notebooks pytest backend/tests -q
```

Verificación T30: **75 pruebas del backend aprobadas**, seis nuevas también
en Python 3.9. HTTP local con Uvicorn y bundle real comprobado; evidencia local
en `data/reports/presentation/t30_api_smoke.json`, sin registros del dataset.
El bundle actual conserva su requisito de entorno Python 3.12; probar el código
HTTP en Python 3.9 no acredita compatibilidad de ese artefacto. Sin MongoDB/S3,
despliegue o endpoints de negocio adicionales.

## Modelo y motor de cotizaciones — T31

`QuotePreviewService.preview(order_id, quote_id, load_kg, costs)` combina T21,
T22 y T23 sobre **un único snapshot** del pedido solicitado: duración desde su
creación guardada, distancia Haversine, desglose monetario y opciones de vehículo.
Conserva políticas/entradas y devuelve un resultado inmutable. No modifica el
pedido, registra cotizaciones, reserva IDs o autoriza cobros/asignaciones.

La API añade `POST /orders/{order_id}/quotes`. Para habilitarlo, componer
`create_app(..., orders=repository, pricing_policy=prices, vehicle_policy=rules)`
con un repositorio que contenga pedidos y políticas completas explícitas.
Se reutiliza el mismo modelo cargado para `/predict`, sin HTTP interno o
reentrenamiento. La aplicación predeterminada no carga datos/tarifas de ejemplo;
sin esas dependencias el endpoint devuelve 503 `quote_configuration_missing`.

Con aplicación compuesta y pedido existente, cuerpo de ejemplo **ilustrativo**:

```json
{"quote_id":"ejemplo","load_kg":"1","costs":{"currency":"USD","variable_cost":"0.10","attributable_cost":"0.20"}}
```

Los costos son ejemplos, no valores predeterminados o comerciales. El cliente
no puede cambiar fecha de creación, tarifas o políticas mediante este cuerpo.
La respuesta ofrece importes Decimal como strings, duración/versiones, zona,
carga y razones de aceptación/rechazo de ambos vehículos, sin elegir uno.
Puede mostrar un escenario con ningún vehículo admisible; no habilita la entrega.
Siempre lleva `academic_only=true`, `coverage_validated=false` y
`commercial_quote_validated=false`. Cumplir una zona configurada no valida
cobertura real. Los requisitos de cotización comercial T20/T26/T28 siguen vigentes.

Errores: 404 pedido inexistente, 409 estado incompatible, 422 entrada/moneda
inválida y 503 configuración/modelo ausentes, con el formato T30. DTOs en
OpenAPI y `/docs`; MongoDB/CRUD y fuentes comerciales siguen pendientes.

```bash
uv run --locked pytest backend/tests/test_quote_previews.py -q
```

Verificación T31: **80 pruebas del backend aprobadas en Python 3.12**; las once
nuevas de T30–T31 también pasan en Python 3.9. Previsualización HTTP con bundle
real y reglas/coordenadas de fixture verificada, sin mutación: evidencia local
en `data/reports/presentation/t31_quote_smoke.json`. Sin nuevas dependencias.

## MongoDB y persistencia — T32

Servicio elegido: **MongoDB Atlas Free en AWS us-east-1**. Ruben creó el clúster
y guardó la URI privada; conexión Atlas, cinco colecciones/validadores/índices,
transacción de lectura y lecturas API se verificaron el 2026-11-04. La API
también recuperó el modelo real de S3. Evidencia sin credenciales:
`data/reports/presentation/t32_atlas_smoke.json`. La aplicación no carga `.env`
sola; usar su configuración explícitamente:

```bash
uv sync --locked
uv run --locked --env-file .env python -m delivery.adapters.mongo
uv run --locked --env-file .env uvicorn delivery.api.app:app --host 127.0.0.1 --port 8000
```

El primer comando de módulo crea validadores/índices sin borrar datos; un
esquema existente incompatible exige migración explícita. La API verifica el
esquema antes de habilitar almacenamiento y comparte un cliente durante su
vida. Sin configuración/conexión/esquema preparados, los endpoints operativos
devuelven 503 `storage_unavailable`; no hay fallback de memoria. `/health`
sigue comprobando proceso/modelo, no garantiza disponibilidad de la base.

En `/docs`: CRUD de `/businesses` y `/couriers`; crear/listar/consultar pedidos
en `/orders` y transiciones en `/orders/{order_id}/transitions` con estado
esperado/destino. Catálogos referenciados no se eliminan y un repartidor con
asignación activa no se edita. Los pedidos se actualizan por flujo de estados,
sin borrado genérico de historial. Listas de hasta 100 registros por consulta.

Persisten también asignaciones/efectivo mediante sus servicios actuales.
Transacciones reservan el grupo y ocupan al repartidor conjuntamente; los
conflictos revierten todos los cambios. Versiones internas evitan escrituras
obsoletas; importes Decimal128 y fechas UTC conservan precisión. Ver detalles
y límites del codec en ARCHITECTURE. Las reglas de cotización autoritativa
siguen vigentes: persistir un borrador académico no permite cobrar/asignar.

Pruebas reales opt-in, con bases desechables `delivery_test_<uuid>` y limpieza
al terminar. Nunca usan MONGODB_URI de la aplicación:

```bash
export MONGODB_TEST_URI='mongodb://127.0.0.1:27018/?replicaSet=delivery-test'
uv run --locked --extra notebooks pytest backend/tests -q
```

Se requiere un MongoDB de pruebas accesible con ese replica set. En esta
iteración se utilizó un contenedor temporal de `mongo:8.0`, sin Dockerfiles o
Compose del producto (T34). Sin MONGODB_TEST_URI, las siete pruebas de integración
se omiten explícitamente; no se presentan como verificadas contra Atlas.
Resultado local: **87 pruebas del backend aprobadas**, las siete nuevas también
en Python 3.9. Persistencia tras reiniciar el servidor comprobada; evidencia
agregada en `data/reports/presentation/t32_mongodb.json`. No se crea Atlas ni
se cambia IAM/AWS; S3 corresponde a T33.

## S3 y publicación de artefactos — T33

Bucket existente `ml-kodigo-resources`, us-east-1. Subida condicional y descarga
verificada por SHA-256, sin crear bucket, cambiar IAM/políticas o sobrescribir
otro contenido. Perfil y endpoint explícitos evitan heredar el emulador local:

```bash
uv run --locked --extra notebooks python ml/data/package_notebook_source.py
uv run --locked python ml/data/publish_s3.py --profile remote-admin
uv run --locked python ml/data/publish_s3.py --profile remote-admin --apply
```

El último comando publica la selección autorizada: bundle académico con
licencia/atribución, manifiestos del dataset, código/documentación, notebooks
fuente sin outputs y reportes agregados. **Los CSV Meituan originales, procesados
y particiones permanecen locales**; datasets declara metadata_only. Se conservan
restricciones no comerciales. No se suben .env, credenciales, guía personal,
archivos de agentes o notebooks ejecutados con registros.

Checksum/tamaño y ACL privadas se verifican. El recibo incremental está en
`data/reports/presentation/t33_s3_publication.json` con claves/hashes/estado;
se puede reanudar sin sobrescribir. El manifiesto de documentación identifica
HEAD y cambios sin commit de ese snapshot, sin atribuirle un cierre Git.

Para servir el modelo desde S3, dejar DELIVERY_MODEL_DIR sin configurar y
exportar DELIVERY_MODEL_MANIFEST_KEY, SHA256 y SIZE según el recibo; usar
DELIVERY_AWS_PROFILE para el perfil local y S3_ENDPOINT_URL para AWS real.
La API descarga una vez al arrancar, valida el bundle T19 en su entorno exacto
y limpia la caché al cerrar; no entrena o descarga por petición.

En este equipo quedó configurado `.env` local, ignorado por Git. Para cargarlo
explícitamente sin agregar python-dotenv:

```bash
uv run --locked --env-file .env uvicorn delivery.api.app:app --host 127.0.0.1 --port 8000
```

Publicación T33 verificada: **47 objetos, 2,183,341 bytes**, privados, bajo
`models/delivery-duration/meituan-temporal-rf-v1/`,
`datasets/meituan/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/` (metadatos) y
`docs/ml-delivery-app/ed6b32c222a2706df91c/`. Documentación remota es un snapshot
inmutable previo a registrar este resultado, no un espejo de cambios posteriores.

```bash
uv run --locked pytest backend/tests/test_s3.py -q
```

Pruebas de contrato SDK con objetos sintéticos; la publicación/descarga real
se acredita por su recibo y evidencia local, separadas de esos tests.
Resultado: 92 pruebas del backend con MongoDB real aprobadas; las cinco nuevas
también pasan en Python 3.9, con aviso de fin de soporte de Boto3 para esa
versión. El entorno de ejecución del bundle continúa en Python 3.12.

## Notebooks para estudiar y exponer

[`notebooks/01_datos_y_procesamiento.ipynb`](notebooks/01_datos_y_procesamiento.ipynb)
explica y ejecuta T05–T12 usando los scripts existentes. Para la sección Spark y sus
pruebas se necesita Java 17 también en el entorno de ejecución del notebook.

[`notebooks/02_modelado_y_evaluacion.ipynb`](notebooks/02_modelado_y_evaluacion.ipynb)
incluye T13 (variables/partición), T14 (baseline y métricas reales) y T15
(tres familias, resultados sobre train), T16 (validación/tuning temporal) y T17
(MLP y curvas de aprendizaje), T18 (comparación/errores) y T19
(selección/persistencia académica local).
Puede adquirir y preparar la fuente por sí mismo. Sus pruebas específicas
usan Pandas/scikit-learn, sin necesitar Java para ejecutarlas.

```bash
uv sync --locked --extra notebooks
uv run --locked --extra notebooks python ml/data/package_notebook_source.py
```

Localmente, abrir el notebook en VS Code con `.venv/bin/python`. Para Colab,
subir el `.ipynb` y, cuando lo solicite la primera celda, seleccionar
`data/reports/presentation/delivery_source.zip`. Regenerar el ZIP al cambiar el
código: incluye fuentes, pruebas y documentación técnica con hashes, sin datasets,
credenciales ni `.env`. El paquete y la ejecución funcionan sin `AGENTS.md`;
las instrucciones temporales para agentes podrán retirarse después. Las decisiones
y la reproducción se conservan en este README, `docs/DATA_ML.md` y el notebook.

Las dependencias opcionales `notebooks` permiten ejecutar y validar el cuaderno;
no se necesitan para usar los scripts de datos. La copia con resultados de la
validación local se guarda fuera de Git en
`data/reports/presentation/01_datos_y_procesamiento_ejecutado.ipynb` y
`data/reports/presentation/02_modelado_y_evaluacion_ejecutado.ipynb`.

Verificación T12: quince celdas del primer notebook sin errores y 35 pruebas
aprobadas al cerrar ese bloque. T13/T14: diez celdas del segundo notebook sin
errores y suite de **40 pruebas aprobadas en Python 3.12/3.9** al cerrar el bloque. Las
particiones tienen los mismos hashes; constante y métricas coinciden en ambos intérpretes.
T15: segundo notebook completo con **13 celdas** ejecutadas sin errores;
**42 pruebas aprobadas en Python 3.12** y las dos nuevas también en Python 3.9.
T16: notebook ampliado a **16 celdas** ejecutadas sin errores y suite de
**44 pruebas aprobadas en Python 3.12**; sus dos pruebas nuevas pasan también en 3.9.
T17: **19 celdas** ejecutadas sin errores, curvas exportadas y **46 pruebas
aprobadas en Python 3.12**; las dos nuevas pasan también en Python 3.9.
T18: **21 celdas** ejecutadas sin errores, comparación exportada y **48 pruebas
aprobadas en Python 3.12**; las dos nuevas pasan también en Python 3.9.
T19: tres celdas nuevas ejecutadas sin errores, conservando las 21 ejecuciones
previas sin cambios de código; **24 celdas verificadas en etapas**, **50 pruebas
aprobadas en Python 3.12** y las dos nuevas también en Python 3.9.
Una ejecución aislada desde el ZIP regeneró 546,281 pedidos con el mismo hash
de T08 antes de incorporar T09. El EDA y las equivalencias Dask/Spark–Pandas se verificaron
en Python 3.12 y 3.9. La ejecución directamente en el servicio de Colab queda por comprobar.


## Docker y Compose local — T34

Requisitos: Docker con Compose. Desde la raíz:

```bash
docker compose build api
docker compose up -d --wait
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/businesses
docker compose logs mongo-init api
docker compose down
```

Compose usa MongoDB local, independientemente de la URI Atlas guardada en
`.env`; no importa ese archivo al contenedor. MongoDB no publica puertos y
comparte una red interna con la API. Su réplica de un nodo permite las
transacciones T32. `mongo-init` prepara réplica/esquema/índices antes de la API;
el volumen `mongo-data` conserva la información después de `down`.
No hay autenticación en esta base aislada de demostración local; este Compose
no es una configuración de despliegue público. `down --volumes` elimina los
datos locales del proyecto y debe usarse únicamente si se desea reiniciar la demo.

El puerto HTTP solo se publica en 127.0.0.1. Si está ocupado:
`DELIVERY_API_PORT=8001 docker compose up -d --wait`. `/docs` muestra OpenAPI.
La imagen ejecuta un usuario sin privilegios; no contiene `.env`, perfiles
AWS, datasets ni modelos. Usa versiones del lock y excluye Spark, PyTorch,
Dask, Matplotlib, notebooks y herramientas de desarrollo. El entorno completo
para experimentos sigue disponible con `uv sync` fuera del contenedor.

El directorio local ignorado `models/` se monta en lectura. Con el bundle T19
en `models/delivery-duration/meituan-temporal-rf-v1/`, `/health` debe informar
`model_available: true` y `/predict` puede estimar una fecha ilustrativa:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"requested_at":"2022-10-22T12:00:00-06:00"}'
```

Sin un bundle propio compatible, la API sigue disponible y `/predict` devuelve
503. No descarga datos ni entrena modelos. Para otra ruta dentro del montaje,
configurar `DELIVERY_LOCAL_MODEL_DIR`; las tarifas comerciales siguen pendientes.

Para ejecutar la misma imagen contra Atlas y recuperar el modelo de S3,
usar explícitamente la configuración privada existente, fuera del Compose local:

```bash
docker run --rm --init --name delivery-atlas \
  --user "$(id -u):$(id -g)" \
  --env-file .env \
  --mount type=bind,src="$HOME/.aws",dst=/home/delivery/.aws,readonly \
  -p 127.0.0.1:8000:8000 ml-delivery-api:local
```

Este comando requiere permisos de lectura del perfil AWS para el usuario del
contenedor y Atlas debe admitir la IP de salida del equipo. Si se usa un rol
en lugar de un perfil, omitir el montaje. El modelo local tiene prioridad si
`DELIVERY_MODEL_DIR` está configurado; para S3 dejarlo vacío. No se copian
credenciales a la imagen ni se cambia IAM o Atlas desde Docker. El esquema
Atlas debe estar preparado como se documentó en T32. Next.js se incorpora en T47;
Terraform y Compose de despliegue corresponden a tareas posteriores.

Referencias de implementación: [uv en Docker](https://docs.astral.sh/uv/guides/integration/docker/)
y [orden de arranque en Compose](https://docs.docker.com/compose/how-tos/startup-order/).


## Verificación mínima de pruebas unitarias — T35

```bash
uv run --locked pytest backend/tests/test_domain.py -q
```

Las 14 pruebas existentes de dominio cubren entidades, coordenadas, estados
iniciales, inmutabilidad, procedencia de duración, precisión monetaria y
validaciones de cotizaciones. Superan el mínimo académico de diez; no requieren
MongoDB, AWS, modelos entrenados ni datasets. Resultado comprobado en T35:
**14 aprobadas**. Los valores de prueba son fixtures sintéticos. Esta selección
no equivale a repetir la suite completa ni al flujo integrado de T36.


## Prueba del flujo simulado — T36

```bash
uv run --locked pytest backend/tests/test_delivery_flow.py -q
```

Una sola prueba integra solicitud WhatsApp simulada, estimación y desglose de
precios, confirmación, asignación, recogida/entrega, cobro y entrega de efectivo
al operador. Comprueba historiales y liberación del repartidor. Resultado T36:
**1 aprobada**. Usa servicios reales del proyecto con repositorios en memoria;
predictor, evidencia de cotización y políticas son fixtures exclusivos del test.
No acredita flujo HTTP/cloud, calidad ML o autorización comercial: la API sigue
bloqueando avances que requieren una fuente de cotización validada.
