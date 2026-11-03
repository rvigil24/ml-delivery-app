# TASKS — Plan compartido de trabajo

**Backlog de referencia:** 54 tareas (T01–T54). Las asignaciones y estados que figuran aquí provienen de la última copia de trabajo disponible; si el Excel compartido cambia, prevalece el Excel. **No actualizar estados automáticamente.**

**Actualización local autorizada — 2026-11-02:** por solicitud explícita de
Ruben, T01, T02 y T03 se registran como completadas. Evidencia: estructura y Git
en `9b9f696`; entorno reproducible y dos pruebas aprobadas en Python 3.9/3.12 en
`78657e4`; diseño y flujo precisados en `docs/ARCHITECTURE.md`, con comprobación
de enlaces y formato. El cierre se basa en la aceptación de Ruben en esta
sesión; no se ha realizado ni se afirma una revisión independiente de Guillermo.
Los contratos propuestos de T03 siguen pendientes de coordinación antes de
implementarlos. Esta actualización no modifica el Excel compartido: el equipo
debe reflejar allí el cierre. Las demás tareas conservan su estado de referencia.

**Actualización local autorizada — 2026-11-03:** Ruben Vigil asume todas las
tareas T01–T54 por instrucción explícita. T04 se registra como completada: modelos
de dominio y documentación en `787d713`, integrados en `main`, con 16 pruebas
aprobadas en Python 3.9 y 3.12. T01–T03 conservan su cierre anterior; T05–T54
permanecen pendientes. Esta reasignación no modifica la autoría histórica de
commits ni acredita revisión independiente. Debe reflejarse también en el
Excel compartido; las referencias anteriores a responsables en otros documentos
corresponden al reparto previo y deben interpretarse con esta actualización.

## Orden de trabajo de Ruben Vigil

- **T01–T09:** completadas e integradas en `main`; T08–T09 mediante PR #5, commit `f93f833`.
- **T10–T12:** completadas en implementación y comprobaciones; cierre e integración autorizados por Ruben.
- **Siguiente tarea:** T13, preparar variables y conjuntos de entrenamiento/prueba; aún sin iniciar.
- **T13–T40:** continuar según dependencias y criterios de aceptación.
- **T41–T54:** asignadas a Ruben Vigil; despliegue y gastos siguen requiriendo autorización explícita.

Cada agente trabaja una tarea por iteración, informa resultados y evita hacer
commits/push por cuenta propia. Las nuevas ramas parten de `origin/main`
actualizado y agrupan un bloque pequeño, conforme al flujo siguiente.

## Flujo de entrega por bloques — acordado el 2026-11-03

Ruben trabaja ahora solo y solicita reducir las operaciones manuales de GitHub.
Se conserva la trazabilidad por tarea y se agrupa la integración:

1. Definir un bloque de **2–3 tareas relacionadas**, con IDs explícitos, y crear su rama desde `origin/main` actualizado.
2. Trabajar una tarea a la vez. Registrar evidencia y pendientes aquí; mantener la guía externa. «Continuemos» avanza a la siguiente tarea documentada del bloque, respetando dependencias.
3. Cuando Ruben indique **«cerrá el bloque»**, el agente verifica cada ID, las dependencias y los criterios de aceptación. Si falta trabajo o hay un bloqueo, lo resuelve dentro del alcance o informa el impedimento antes de publicar un cierre.
4. Esa orden autoriza actualizar el backlog local con evidencia, crear commit(s) identificados con las tareas, hacer push y crear o actualizar **un PR** con el resumen del bloque, comprobaciones y limitaciones.
5. Fusionar el PR cuando los controles y permisos del remoto lo permitan. Verificar que los commits estén incluidos en `origin/main`, sincronizar `main` local y registrar PR/commit de integración en la guía externa. GitHub conserva el estado efectivo del PR. Si falla una operación, informar qué quedó hecho y qué sigue pendiente.

El estado oficial de las tareas del bloque se actualiza como parte de ese cierre;
la preparación local no se confunde con integración confirmada. Antes de iniciar
otro bloque se revisa que sus dependencias estén satisfechas y que ningún ID del
bloque anterior haya quedado sin resultado. No se borran ramas automáticamente,
no se fuerza el historial y no se modifica el Excel sin una instrucción específica.
La fusión no autoriza despliegues ni gastos AWS.

### Bloque T05–T07 — fuentes, adquisición y validación

Rama: `data/T05-T07-datos`. Base: `origin/main` en `1a7a925`.
Los cambios activos están reunidos en la carpeta principal del repositorio.
T05, T06 y T07 están completadas en implementación y comprobaciones. Su
integración se realiza en el único PR de esta rama; el resultado efectivo del
merge se consulta en GitHub y se registra en la guía externa.

| ID | Preparación local | Evidencia disponible / pendiente |
|---|---|---|
| T05 | Investigación y selección preparadas | `docs/DATA_ML.md`: fuentes accedidas, hashes y elección explícita de Meituan por Ruben. |
| T06 | Adquisición preparada | `ml/data/acquire_meituan.py`, inventario/licencia/manifiesto local; 19 pruebas aprobadas en Python 3.12 y 3.9 en la preparación T06. |
| T07 | Auditoría preparada; aprobada con condiciones | `ml/data/audit_meituan.py` e informe agregado: 546,281 pedidos inmediatos elegibles; reglas y riesgos en DATA_ML. La distancia queda pendiente de confirmar unidades. Suite del bloque: 25 pruebas aprobadas en Python 3.12 y 3.9. |

Checklist de cierre del bloque:

- [x] Investigación T05 y decisión de fuente registradas.
- [x] Receta e inventario de T06 disponibles.
- [x] T07 satisface su criterio de aceptación: target observado, cohorte y features temporales documentados; condiciones geográficas y de alcance explícitas.
- [x] Comprobaciones finales del bloque ejecutadas: auditoría real con hash verificado, 25 pruebas en Python 3.12/3.9, compatibilidad de dependencias y formato.
- [x] Backlog local y guía actualizados con el resultado de cada ID.
- [x] Publicado e integrado mediante [PR #4](https://github.com/rvigil24/ml-delivery-app/pull/4), commit de integración `27e070e`; verificado en remoto y sincronizado localmente.

La confirmación final del merge y sincronización se registra en GitHub y la
guía externa; no requiere crear otro PR solo para anotar el hash posterior.

Los bloques siguientes se definirán al terminar este, por ejemplo T08–T09 y
T10–T12. No se amplía el bloque actual ni se inician tareas posteriores mientras
esté pendiente la validación requerida para ellas.

**Cierre verificado:** T05–T07 integradas en `main` el 2026-11-03 mediante PR #4.

### Bloque T08–T09 — preparación y EDA

Rama `data/T08-T09-preparacion-eda`, creada desde `origin/main` en `27e070e`
después de verificar la integración de T05–T07.

- T08: completada; preparación ejecutada, 546,281 filas/11 columnas, manifiesto reproducible y pruebas de transformación. 29 pruebas aprobadas en Python 3.12/3.9 al implementar T08.
- T09: completada; EDA en `ml/data/explore_meituan.py` y `delivery_ml/exploration.py`, informe JSON/Markdown y cuatro figuras sobre los 546,281 pedidos. Calidad, cola larga, asociaciones y sesgos documentados; CSV intacto. Suite final de 31 pruebas y EDA aprobados en Python 3.12/3.9.
- Apoyo para la exposición autorizado por Ruben: `notebooks/01_datos_y_procesamiento.ipynb` ejecuta T05–T09; diez celdas y 31 pruebas aprobadas localmente. El ZIP de fuentes permitió regenerar la misma cohorte/hash antes de T09 y se actualizó para incluir el EDA. T10–T12 siguen pendientes; falta comprobar directamente el servicio Colab.
- Cierre autorizado por Ruben: T08/T09 se registran como completadas con esta evidencia, sin modificar el Excel ni atribuir revisión independiente. Publicación mediante un único PR; la integración efectiva y su commit se verifican en GitHub y se registran en la guía externa después del merge.

Checklist de cierre:

- [x] Dependencias T07–T08 y criterios de aceptación de ambos IDs contrastados con código y datos reales.
- [x] Preparación repetida con integridad verificada y EDA reproducible; sin datos ni salidas de pedidos en Git.
- [x] 31 pruebas aprobadas; compatibilidad Python 3.9/3.12 y diez celdas del notebook comprobadas.
- [x] Backlog local actualizado por orden explícita; guía externa con decisiones y comprobaciones.

El cierre incluye commit, push y PR único con merge y sincronización de `main`.
La confirmación posterior se registra en GitHub y la guía externa, evitando otro
PR solo para anotar el hash generado por la integración.

**Cierre verificado:** T08–T09 integradas mediante [PR #5](https://github.com/rvigil24/ml-delivery-app/pull/5), commit `f93f833`; `main` local y remoto sincronizados antes de iniciar el bloque siguiente.

### Bloque T10–T12 — motores de procesamiento

Rama `data/T10-T12-motores`, creada desde `origin/main` actualizado en `f93f833`.
Responsable de los tres IDs: Ruben Vigil. La orden de continuar activa este
bloque; se implementa una tarea por iteración y se integra con un solo PR al cierre.

- T10: completada; Dask y comparación completa con Pandas: 546,281 filas, 11 columnas y SHA-256 idéntico desde siete particiones. 33 pruebas y comparación real aprobadas en Python 3.12/3.9 al implementar T10.
- T11: completada; Spark SQL local con 546,281 filas/11 columnas equivalentes exactamente a Pandas y hash normalizado idéntico. Lectura en ocho particiones, `local[2]`, Java 17 y UTC. 35 pruebas y comparación completa aprobadas en Python 3.12/3.9.
- T12: completada; benchmark con tres rondas rotativas y procesos nuevos en Python 3.12: nueve resultados equivalentes. Medianas de pipeline: Pandas 3.708 s, Dask 6.250 s y Spark 25.138 s en el equipo registrado. JSON, CSV de muestras, Markdown y gráfico reproducibles. Comprobación funcional separada en Python 3.9 con una muestra real por motor; no se mezclan los tiempos.

El notebook incorpora T10–T12 y sus evidencias locales: quince celdas ejecutadas
sin errores. Por orden explícita de Ruben, los tres IDs se registran como
completados con esta evidencia, sin modificar el Excel ni atribuir revisión
independiente. La publicación usa un único PR; su integración efectiva y el
commit se verifican en GitHub y se registran en la guía externa tras el merge.

Comprobaciones de cierre:

- [x] Dependencias y criterios T10/T11/T12 contrastados con código, dataset real y reportes.
- [x] Equivalencia completa Dask/Spark–Pandas en Python 3.9/3.12; fuente y referencia intactas.
- [x] Nueve muestras T12, estadísticas, entorno y hashes verificados; prueba funcional 3.9 separada.
- [x] Suite de 35 pruebas aprobada; notebook válido y sin resultados guardados en Git.
- [x] Backlog local y guía actualizados por orden explícita; instrucciones para agentes temporales sin dependencia de ejecución.

El cierre incluye commit, push, PR único, merge y sincronización de `main`.
El resultado posterior queda en GitHub y la guía externa, evitando un PR adicional
solo para anotar el hash de integración. No se usa un clúster, AWS ni entrenamiento;
las coordenadas siguen en unidades originales sin derivar distancias físicas.

La preparación de datos T08 no incluye automáticamente features geográficas no validadas.
La confirmación de unidades geográficas queda como pendiente explícito para el
próximo bloque antes de calcular distancia física; no debe perderse al integrar.
El uso privado de S3 y los derechos sobre publicación de artefactos Meituan quedan
pendientes de revisión en T33/T19 antes de cualquier subida. La auditoría de calidad
no resuelve esa condición ni excluye AWS del diseño; ver la corrección en DATA_ML.

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

**Responsable:** Ruben Vigil

**Dependencia:** Ninguna  
**Implementar:** Buscar y verificar fuentes reales para entregas, timestamps y features pre-entrega; registrar URL, licencia, cobertura, columnas y evidencia de acceso.  
**Terminado cuando:** Informe comparativo verificable; al menos una fuente realmente accedida o bloqueo justificado. No datos simulados como etiquetas.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T05 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T06 — Descargar y documentar el dataset seleccionado

**Responsable:** Ruben Vigil

**Dependencia:** T05  
**Implementar:** Descargar el dataset validado o construir acceso reproducible; versionar receta de obtención, no redistribuir si la licencia lo impide.  
**Terminado cuando:** Script/README de adquisición, origen, fecha, licencia, volumen y hash/versionado comprobables.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T06 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T07 — Validar la variable objetivo y calidad de los datos

**Responsable:** Ruben Vigil

**Dependencia:** T06  
**Implementar:** Auditar target, faltantes, calidad, leakage, cobertura y representatividad; proponer decisión documentada.  
**Terminado cuando:** Target observado aceptado o bloqueo explícito; evidencia que features se conocen al pedir cotización.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T07 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T08 — Limpiar y transformar los datos con Pandas

**Responsable:** Ruben Vigil

**Dependencia:** T07  
**Implementar:** Implementar pipeline de limpieza y transformación Pandas reproducible, con funciones modulares.  
**Terminado cuando:** Script reutilizable y pruebas de transformación; dataset de salida derivado del insumo real, sin etiquetas inventadas.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T08 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T09 — Realizar análisis exploratorio (EDA) y visualizaciones

**Responsable:** Ruben Vigil

**Dependencia:** T07–T08  
**Implementar:** Hacer EDA para target/variables, nulos, anomalías y sesgo; gráficos y hallazgos.  
**Terminado cuando:** Informe o notebook legible, reproducible y con conclusiones vinculadas a datos reales.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T09 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T10 — Implementar transformaciones equivalentes con Dask

**Responsable:** Ruben Vigil

**Dependencia:** T08  
**Implementar:** Repetir transformaciones clave de T08 con Dask usando mismo input y criterios.  
**Terminado cuando:** Resultados comparables a Pandas y evidencia automática o documentada de equivalencia.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T10 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T11 — Implementar transformaciones equivalentes con PySpark local

**Responsable:** Ruben Vigil

**Dependencia:** T08  
**Implementar:** Repetir transformaciones clave con PySpark en modo local, sin clúster.  
**Terminado cuando:** Resultados comparables a Pandas y documentación de operaciones/acciones Spark.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T11 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

### T12 — Comparar tiempos y resultados de Pandas, Dask y PySpark

**Responsable:** Ruben Vigil

**Dependencia:** T08, T10, T11  
**Implementar:** Comparar rendimientos Pandas/Dask/PySpark sobre las mismas transformaciones y volumen.  
**Terminado cuando:** Tabla con tiempos medidos realmente, contexto de hardware y explicación de compromisos.

**Prompt corto:** «Lee `AGENTS.md`, `docs/TASKS.md` y los documentos pertinentes. Implementa solamente T12 siguiendo su aceptación. No hagas commits ni cambies otras tareas; al terminar muestra cambios y verificaciones reales.»

## Backlog completo y asignaciones

| ID | Área | Tarea | Responsable | Estado de referencia / actualización autorizada |
|---|---|---|---|---|
| T01 | Preparación y arquitectura | Crear repositorio Git y estructura modular del proyecto | Ruben Vigil | Completada |
| T02 | Preparación y arquitectura | Configurar entorno Python y dependencias | Ruben Vigil | Completada |
| T03 | Preparación y arquitectura | Diseñar arquitectura general y flujo de pedidos | Ruben Vigil | Completada |
| T04 | Preparación y arquitectura | Definir modelos de datos: negocios, pedidos, repartidores y entregas | Ruben Vigil | Completada |
| T05 | Dataset y procesamiento de datos | Investigar y verificar fuentes de datos reales de entregas | Ruben Vigil | Completada |
| T06 | Dataset y procesamiento de datos | Descargar y documentar el dataset seleccionado | Ruben Vigil | Completada |
| T07 | Dataset y procesamiento de datos | Validar la variable objetivo y calidad de los datos | Ruben Vigil | Completada |
| T08 | Dataset y procesamiento de datos | Limpiar y transformar los datos con Pandas | Ruben Vigil | Completada |
| T09 | Dataset y procesamiento de datos | Realizar análisis exploratorio (EDA) y visualizaciones | Ruben Vigil | Completada |
| T10 | Dataset y procesamiento de datos | Implementar transformaciones equivalentes con Dask | Ruben Vigil | Completada |
| T11 | Dataset y procesamiento de datos | Implementar transformaciones equivalentes con PySpark local | Ruben Vigil | Completada |
| T12 | Dataset y procesamiento de datos | Comparar tiempos y resultados de Pandas, Dask y PySpark | Ruben Vigil | Completada |
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
| T30 | API, almacenamiento e infraestructura | Implementar API FastAPI con /health, /predict y documentación OpenAPI | Ruben Vigil | Pendiente |
| T31 | API, almacenamiento e infraestructura | Integrar el modelo predictivo con el motor de cotizaciones | Ruben Vigil | Pendiente |
| T32 | API, almacenamiento e infraestructura | Configurar MongoDB con CRUD, índices y validaciones | Ruben Vigil | Pendiente |
| T33 | API, almacenamiento e infraestructura | Integrar almacenamiento de objetos con S3 o MinIO | Ruben Vigil | Pendiente |
| T34 | API, almacenamiento e infraestructura | Contenerizar los servicios mediante Docker y Docker Compose | Ruben Vigil | Pendiente |
| T35 | Pruebas, documentación y entrega | Implementar al menos 10 pruebas unitarias con pytest | Ruben Vigil | Pendiente |
| T36 | Pruebas, documentación y entrega | Probar el flujo completo: solicitud → cotización → asignación → entrega → efectivo | Ruben Vigil | Pendiente |
| T37 | Pruebas, documentación y entrega | Preparar README con instalación, ejecución y ejemplos | Ruben Vigil | Pendiente |
| T38 | Pruebas, documentación y entrega | Documentar arquitectura, resultados, experimentos y limitaciones | Ruben Vigil | Pendiente |
| T39 | Pruebas, documentación y entrega | Preparar informe técnico y evidencias de los hitos | Ruben Vigil | Pendiente |
| T40 | Pruebas, documentación y entrega | Preparar presentación y demostración para la defensa | Ruben Vigil | Pendiente |
| T41 | Despliegue y CI/CD | Definir arquitectura de despliegue en AWS y revisar presupuesto estimado | Ruben Vigil | Pendiente |
| T42 | Despliegue y CI/CD | Implementar infraestructura como código con Terraform (EC2, red, IAM y S3) | Ruben Vigil | Pendiente |
| T43 | Despliegue y CI/CD | Configurar Docker Compose y variables para el entorno de despliegue | Ruben Vigil | Pendiente |
| T44 | Despliegue y CI/CD | Crear pipeline CI/CD en GitHub Actions para pruebas, build y despliegue | Ruben Vigil | Pendiente |
| T45 | Despliegue y CI/CD | Configurar secretos, permisos mínimos y acceso seguro a la infraestructura | Ruben Vigil | Pendiente |
| T46 | Despliegue y CI/CD | Validar despliegue, logs, persistencia y consumo de recursos | Ruben Vigil | Pendiente |
| T47 | Frontend y simulación visual | Crear aplicación Next.js con navegación entre las vistas de la demo | Ruben Vigil | Pendiente |
| T48 | Frontend y simulación visual | Implementar chat estilo WhatsApp para que el cliente simule un pedido | Ruben Vigil | Pendiente |
| T49 | Frontend y simulación visual | Implementar panel del negocio para ver pedidos y cambiar su estado | Ruben Vigil | Pendiente |
| T50 | Frontend y simulación visual | Implementar panel del repartidor para consultar rutas y confirmar entregas | Ruben Vigil | Pendiente |
| T51 | Frontend y simulación visual | Implementar panel de operaciones con tarifas, costos, efectivo y márgenes | Ruben Vigil | Pendiente |
| T52 | Frontend y simulación visual | Conectar las vistas de Next.js con los endpoints reales de FastAPI | Ruben Vigil | Pendiente |
| T53 | Frontend y simulación visual | Sincronizar actualizaciones de estados entre las vistas sin WhatsApp real | Ruben Vigil | Pendiente |
| T54 | Frontend y simulación visual | Preparar demo end-to-end de entrega individual, agrupada y pago en efectivo | Ruben Vigil | Pendiente |

## Orden sugerido para integración

1. Ruben entrega la estructura (T01), dependencias (T02), arquitectura revisada (T03) y dominio (T04).
2. Ruben investiga T05 y valida T06–T07 antes de construir ETL T08–T12.
3. Ruben documenta la interfaz compartida de predicción **después de validar la fuente real**, evitando suponer features.
4. Se usan bloques pequeños con una rama y un PR por bloque; no se cierran tareas sin pruebas/evidencias. Aplicar el flujo y la checklist anteriores.
5. Reflejar en el Excel la asignación de T01–T54 a Ruben Vigil y el cierre de T01–T04; no iniciar tareas posteriores sin sus dependencias.

## Definition of Done (mínimo)

- Criterio de aceptación cubierto y verificable.
- Código modular y cambios delimitados a la tarea.
- Tests reales o evidencia de verificación disponible; si no se ejecutó, decirlo.
- No secretos ni datos personales innecesarios en Git.
- No métricas, etiquetas ni ROI falsos.
- Documentación actualizada donde cambian contratos.
- Revisión del otro integrante y actualización manual del backlog compartido.
