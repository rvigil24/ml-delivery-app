# Asistente de Delivery Económico

Proyecto integrador de Python, Ciencia de Datos y Machine Learning. Equipo de dos integrantes. El repositorio comienza con **documentación operativa**, no con una aplicación previamente implementada: los agentes crearán el código al ejecutar cada tarea.

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
crearán al abordar sus tareas. FastAPI, MongoDB y S3 se integrarán posteriormente;
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

Dependencias directas actuales: **boto3**, **Pandas**, **Matplotlib** y **pytest** (grupo `dev`). Hatchling se
usa únicamente para construir/instalar el paquete. FastAPI, el driver MongoDB,
las demás bibliotecas de datos/ML y las herramientas de frontend se incorporarán cuando
se implementen sus tareas.

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

## Notebook para estudiar y exponer

[`notebooks/01_datos_y_procesamiento.ipynb`](notebooks/01_datos_y_procesamiento.ipynb)
explica y ejecuta T05–T09 usando los scripts existentes. T10–T12 aparecen como
pendientes; se completarán al implementar esas tareas.

```bash
uv sync --locked --extra notebooks
uv run --locked --extra notebooks python ml/data/package_notebook_source.py
```

Localmente, abrir el notebook en VS Code con `.venv/bin/python`. Para Colab,
subir el `.ipynb` y, cuando lo solicite la primera celda, seleccionar
`data/reports/presentation/delivery_source.zip`. Regenerar el ZIP al cambiar el
código: incluye fuentes, pruebas y documentación con hashes, sin datasets,
credenciales ni `.env`. No requiere publicar la rama para probarla.

Las dependencias opcionales `notebooks` permiten ejecutar y validar el cuaderno;
no se necesitan para usar los scripts de datos. La copia con resultados de la
validación local se guarda fuera de Git en
`data/reports/presentation/01_datos_y_procesamiento_ejecutado.ipynb`.

Verificación local: diez celdas de código sin errores y 31 pruebas aprobadas.
Una ejecución aislada desde el ZIP regeneró 546,281 pedidos con el mismo hash
de T08 antes de incorporar T09. El EDA y las 31 pruebas se verificaron en Python
3.12 y 3.9. La ejecución directamente en el servicio de Colab queda por comprobar.
