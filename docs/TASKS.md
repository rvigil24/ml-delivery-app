# TASKS — Plan compartido de trabajo

**Backlog de referencia:** 54 tareas (T01–T54). Las asignaciones y estados que figuran aquí provienen de la última copia de trabajo disponible; si el Excel compartido cambia, prevalece el Excel. **No actualizar estados automáticamente.**

## Primer bloque de trabajo de cada integrante

- **Ruben:** T01 → T02 → T03 → T04 (primeras cuatro); T13–T29 después de completar dependencias.
- **Guillermo:** T05 → T06 → T07 → T08 → T09 → T10 → T11 → T12; T30–T40 más adelante.
- **T41–T54:** sin asignación todavía. No asumir quién las hará.

Cada agente trabaja una tarea por iteración, informa resultados y evita hacer commits/push por cuenta propia. La T01 prepara la base compartida; Guillermo puede investigar T05 en paralelo, pero no debe crear una arquitectura distinta.

## Instrucciones concretas y criterios de aceptación: T01–T12

### T01 — Crear repositorio Git y estructura modular del proyecto

**Responsable:** Ruben Vigil  
**Dependencia:** Ninguna  
**Implementar:** Preparar repositorio remoto/estructura modular mínima, README y .gitignore; identificar módulos sin implementar funcionalidades futuras.  
**Terminado cuando:** `git status` correcto; estructura consistente y documentada; ningún secreto versionado; revisión del segundo integrante.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T01 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T02 — Configurar entorno Python y dependencias

**Responsable:** Ruben Vigil  
**Dependencia:** T01  
**Implementar:** Configurar Python 3.9+, entorno aislado, dependencias mínimas y pytest; boto3 preparado sin conectar a AWS. Elegir una forma reproducible de instalar.  
**Terminado cuando:** Instalación reproducible y al menos un test real ejecutado; comandos registrados; sin credenciales ni cambios AWS.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T02 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T03 — Diseñar arquitectura general y flujo de pedidos

**Responsable:** Ruben Vigil  
**Dependencia:** T01  
**Implementar:** Revisar/precisar `docs/ARCHITECTURE.md`: componentes, límites, flujo completo y contratos/puertos propuestos para trabajo paralelo; registrar decisiones pendientes.  
**Terminado cuando:** Arquitectura compartida con API/ML/MongoDB/S3/Next.js/infra y sin contratos basados en features inventadas; revisión cruzada.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T03 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T04 — Definir modelos de datos: negocios, pedidos, repartidores y entregas

**Responsable:** Ruben Vigil  
**Dependencia:** T02–T03  
**Implementar:** Crear modelos tipados de negocio/pedido/repartidor/cotización y estados mínimos; validaciones y pruebas sin integrar aún API ni BD.  
**Terminado cuando:** Entidades importables, campos/unidades explícitas, pruebas unitarias ejecutadas, sin constantes comerciales arbitrarias.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T04 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T05 — Investigar y verificar fuentes de datos reales de entregas

**Responsable:** Guillermo Minero  
**Dependencia:** Ninguna  
**Implementar:** Buscar y verificar fuentes reales para entregas, timestamps y features pre-entrega; registrar URL, licencia, cobertura, columnas y evidencia de acceso.  
**Terminado cuando:** Informe comparativo verificable; al menos una fuente realmente accedida o bloqueo justificado. No datos simulados como etiquetas.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T05 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T06 — Descargar y documentar el dataset seleccionado

**Responsable:** Guillermo Minero  
**Dependencia:** T05  
**Implementar:** Descargar el dataset validado o construir acceso reproducible; versionar receta de obtención, no redistribuir si la licencia lo impide.  
**Terminado cuando:** Script/README de adquisición, origen, fecha, licencia, volumen y hash/versionado comprobables.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T06 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T07 — Validar la variable objetivo y calidad de los datos

**Responsable:** Guillermo Minero  
**Dependencia:** T06  
**Implementar:** Auditar target, faltantes, calidad, leakage, cobertura y representatividad; proponer decisión documentada.  
**Terminado cuando:** Target observado aceptado o bloqueo explícito; evidencia que features se conocen al pedir cotización.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T07 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T08 — Limpiar y transformar los datos con Pandas

**Responsable:** Guillermo Minero  
**Dependencia:** T07  
**Implementar:** Implementar pipeline de limpieza y transformación Pandas reproducible, con funciones modulares.  
**Terminado cuando:** Script reutilizable y pruebas de transformación; dataset de salida derivado del insumo real, sin etiquetas inventadas.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T08 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T09 — Realizar análisis exploratorio (EDA) y visualizaciones

**Responsable:** Guillermo Minero  
**Dependencia:** T07–T08  
**Implementar:** Hacer EDA para target/variables, nulos, anomalías y sesgo; gráficos y hallazgos.  
**Terminado cuando:** Informe o notebook legible, reproducible y con conclusiones vinculadas a datos reales.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T09 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T10 — Implementar transformaciones equivalentes con Dask

**Responsable:** Guillermo Minero  
**Dependencia:** T08  
**Implementar:** Repetir transformaciones clave de T08 con Dask usando mismo input y criterios.  
**Terminado cuando:** Resultados comparables a Pandas y evidencia automática o documentada de equivalencia.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T10 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T11 — Implementar transformaciones equivalentes con PySpark local

**Responsable:** Guillermo Minero  
**Dependencia:** T08  
**Implementar:** Repetir transformaciones clave con PySpark en modo local, sin clúster.  
**Terminado cuando:** Resultados comparables a Pandas y documentación de operaciones/acciones Spark.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T11 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T12 — Comparar tiempos y resultados de Pandas, Dask y PySpark

**Responsable:** Guillermo Minero  
**Dependencia:** T08, T10, T11  
**Implementar:** Comparar rendimientos Pandas/Dask/PySpark sobre las mismas transformaciones y volumen.  
**Terminado cuando:** Tabla con tiempos medidos realmente, contexto de hardware y explicación de compromisos.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T12 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

## Backlog completo y asignaciones

| ID | Área | Tarea | Responsable | Estado al generar este paquete |
|---|---|---|---|---|
| T01 | Preparación y arquitectura | Crear repositorio Git y estructura modular del proyecto | Ruben Vigil | En progreso |
| T02 | Preparación y arquitectura | Configurar entorno Python y dependencias | Ruben Vigil | En progreso |
| T03 | Preparación y arquitectura | Diseñar arquitectura general y flujo de pedidos | Ruben Vigil | En progreso |
| T04 | Preparación y arquitectura | Definir modelos de datos: negocios, pedidos, repartidores y entregas | Ruben Vigil | En progreso |
| T05 | Dataset y procesamiento de datos | Investigar y verificar fuentes de datos reales de entregas | Guillermo Minero | Pendiente |
| T06 | Dataset y procesamiento de datos | Descargar y documentar el dataset seleccionado | Guillermo Minero | Pendiente |
| T07 | Dataset y procesamiento de datos | Validar la variable objetivo y calidad de los datos | Guillermo Minero | Pendiente |
| T08 | Dataset y procesamiento de datos | Limpiar y transformar los datos con Pandas | Guillermo Minero | Pendiente |
| T09 | Dataset y procesamiento de datos | Realizar análisis exploratorio (EDA) y visualizaciones | Guillermo Minero | Pendiente |
| T10 | Dataset y procesamiento de datos | Implementar transformaciones equivalentes con Dask | Guillermo Minero | Pendiente |
| T11 | Dataset y procesamiento de datos | Implementar transformaciones equivalentes con PySpark local | Guillermo Minero | Pendiente |
| T12 | Dataset y procesamiento de datos | Comparar tiempos y resultados de Pandas, Dask y PySpark | Guillermo Minero | Pendiente |
| T13 | Machine Learning y Deep Learning | Preparar variables predictoras y conjuntos de entrenamiento/prueba | Ruben Vigil | Pendiente |
| T14 | Machine Learning y Deep Learning | Implementar un modelo baseline | Ruben Vigil | Pendiente |
| T15 | Machine Learning y Deep Learning | Entrenar tres algoritmos ML de distintas familias | Ruben Vigil | Pendiente |
| T16 | Machine Learning y Deep Learning | Aplicar validación cruzada y optimización de hiperparámetros | Ruben Vigil | Pendiente |
| T17 | Machine Learning y Deep Learning | Implementar y entrenar una red neuronal MLP | Ruben Vigil | Pendiente |
| T18 | Machine Learning y Deep Learning | Evaluar y comparar modelos mediante MAE, RMSE y otras métricas pertinentes | Ruben Vigil | Pendiente |
| T19 | Machine Learning y Deep Learning | Seleccionar, guardar y documentar el modelo final | Ruben Vigil | Pendiente |
| T20 | Lógica del negocio y simulación | Implementar registro y gestión de pedidos y sus estados | Ruben Vigil | Pendiente |
| T21 | Lógica del negocio y simulación | Implementar estimación de distancia y tiempo para cotizaciones | Ruben Vigil | Pendiente |
| T22 | Lógica del negocio y simulación | Desarrollar cálculo de tarifas, costos operativos y remuneración del repartidor | Ruben Vigil | Pendiente |
| T23 | Lógica del negocio y simulación | Implementar reglas para entregas en bicicleta y motocicleta | Ruben Vigil | Pendiente |
| T24 | Lógica del negocio y simulación | Implementar sugerencia sencilla de rutas y orden de entregas | Ruben Vigil | Pendiente |
| T25 | Lógica del negocio y simulación | Comparar costos de entregas individuales y agrupadas | Ruben Vigil | Pendiente |
| T26 | Lógica del negocio y simulación | Desarrollar simulador de asignación de repartidores aprobados | Ruben Vigil | Pendiente |
| T27 | Lógica del negocio y simulación | Implementar simulación de mensajes y solicitudes por WhatsApp | Ruben Vigil | Pendiente |
| T28 | Lógica del negocio y simulación | Simular pagos en efectivo y estados contables | Ruben Vigil | Pendiente |
| T29 | Lógica del negocio y simulación | Elaborar análisis financiero: márgenes, costos fijos, punto de equilibrio y ROI estimado | Ruben Vigil | Pendiente |
| T30 | API, almacenamiento e infraestructura | Implementar API FastAPI con /health, /predict y documentación OpenAPI | Guillermo Minero | Pendiente |
| T31 | API, almacenamiento e infraestructura | Integrar el modelo predictivo con el motor de cotizaciones | Guillermo Minero | Pendiente |
| T32 | API, almacenamiento e infraestructura | Configurar MongoDB con CRUD, índices y validaciones | Guillermo Minero | Pendiente |
| T33 | API, almacenamiento e infraestructura | Integrar almacenamiento de objetos con S3 o MinIO | Guillermo Minero | Pendiente |
| T34 | API, almacenamiento e infraestructura | Contenerizar los servicios mediante Docker y Docker Compose | Guillermo Minero | Pendiente |
| T35 | Pruebas, documentación y entrega | Implementar al menos 10 pruebas unitarias con pytest | Guillermo Minero | Pendiente |
| T36 | Pruebas, documentación y entrega | Probar el flujo completo: solicitud → cotización → asignación → entrega → efectivo | Guillermo Minero | Pendiente |
| T37 | Pruebas, documentación y entrega | Preparar README con instalación, ejecución y ejemplos | Guillermo Minero | Pendiente |
| T38 | Pruebas, documentación y entrega | Documentar arquitectura, resultados, experimentos y limitaciones | Guillermo Minero | Pendiente |
| T39 | Pruebas, documentación y entrega | Preparar informe técnico y evidencias de los hitos | Guillermo Minero | Pendiente |
| T40 | Pruebas, documentación y entrega | Preparar presentación y demostración para la defensa | Guillermo Minero | Pendiente |
| T41 | Despliegue y CI/CD | Definir arquitectura de despliegue en AWS y revisar presupuesto estimado | Sin asignar | Pendiente |
| T42 | Despliegue y CI/CD | Implementar infraestructura como código con Terraform (EC2, red, IAM y S3) | Sin asignar | Pendiente |
| T43 | Despliegue y CI/CD | Configurar Docker Compose y variables para el entorno de despliegue | Sin asignar | Pendiente |
| T44 | Despliegue y CI/CD | Crear pipeline CI/CD en GitHub Actions para pruebas, build y despliegue | Sin asignar | Pendiente |
| T45 | Despliegue y CI/CD | Configurar secretos, permisos mínimos y acceso seguro a la infraestructura | Sin asignar | Pendiente |
| T46 | Despliegue y CI/CD | Validar despliegue, logs, persistencia y consumo de recursos | Sin asignar | Pendiente |
| T47 | Frontend y simulación visual | Crear aplicación Next.js con navegación entre las vistas de la demo | Sin asignar | Pendiente |
| T48 | Frontend y simulación visual | Implementar chat estilo WhatsApp para que el cliente simule un pedido | Sin asignar | Pendiente |
| T49 | Frontend y simulación visual | Implementar panel del negocio para ver pedidos y cambiar su estado | Sin asignar | Pendiente |
| T50 | Frontend y simulación visual | Implementar panel del repartidor para consultar rutas y confirmar entregas | Sin asignar | Pendiente |
| T51 | Frontend y simulación visual | Implementar panel de operaciones con tarifas, costos, efectivo y márgenes | Sin asignar | Pendiente |
| T52 | Frontend y simulación visual | Conectar las vistas de Next.js con los endpoints reales de FastAPI | Sin asignar | Pendiente |
| T53 | Frontend y simulación visual | Sincronizar actualizaciones de estados entre las vistas sin WhatsApp real | Sin asignar | Pendiente |
| T54 | Frontend y simulación visual | Preparar demo end-to-end de entrega individual, agrupada y pago en efectivo | Sin asignar | Pendiente |

## Orden sugerido para integración

1. Ruben entrega la estructura (T01), dependencias (T02), arquitectura revisada (T03) y dominio (T04).
2. Guillermo investiga T05 y valida T06–T07 antes de construir ETL T08–T12.
3. Ruben y Guillermo acuerdan una interfaz compartida de predicción **después de validar la fuente real**, evitando suponer features.
4. Se hacen ramas pequeñas y revisiones cruzadas; no se cierran tareas sin pruebas/evidencias.
5. T41–T54 se distribuyen explícitamente en el Excel antes de implementarse.

## Definition of Done (mínimo)

- Criterio de aceptación cubierto y verificable.
- Código modular y cambios delimitados a la tarea.
- Tests reales o evidencia de verificación disponible; si no se ejecutó, decirlo.
- No secretos ni datos personales innecesarios en Git.
- No métricas, etiquetas ni ROI falsos.
- Documentación actualizada donde cambian contratos.
- Revisión del otro integrante y actualización manual del backlog compartido.
