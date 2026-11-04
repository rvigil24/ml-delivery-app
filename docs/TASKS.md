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

- **T01–T12:** completadas e integradas en `main`; T10–T12 mediante PR #6, commit `f504c8f`.
- **T13–T14:** completadas con la evidencia de cierre indicada abajo; integración verificable en el PR del bloque y la guía externa.
- **T15–T16:** completadas con la evidencia de cierre indicada abajo; integración verificable en el PR del bloque y la guía externa.
- **T17–T18:** completadas con la evidencia de cierre indicada abajo; integración verificable en el PR del bloque y la guía externa.
- **T19:** completada con la evidencia de cierre indicada abajo; integración verificable en su PR y la guía externa.
- **T20–T21:** completadas con la evidencia de cierre indicada abajo; integración verificable en su PR y la guía externa.
- **T22–T23:** completadas con la evidencia de cierre indicada abajo; integración verificable en su PR y la guía externa.
- **T24–T25:** completadas con la evidencia de cierre indicada abajo; integración verificable en su PR y la guía externa.
- **T26–T27:** completadas por cierre autorizado, con evidencia abajo; integración verificable en el PR y la guía externa.
- **T28–T29:** completadas por cierre autorizado, con evidencia abajo; integración verificable en el PR y la guía externa.
- **T30–T31:** completadas por cierre autorizado con alcance académico, con evidencia abajo; integración verificable en el PR y la guía externa.
- **T32–T33:** completadas por cierre autorizado con evidencia local, Atlas y S3 indicada abajo; integración verificable en el PR del bloque y la guía externa. T34 completada por cierre autorizado con evidencia abajo. T35 completada por cierre autorizado con evidencia abajo. Sin bloque activo; siguiente tarea: T36 (flujo integrado simulado).
- **T36–T40:** continuar según dependencias y criterios de aceptación.
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

**Cierre verificado:** T10–T12 integradas mediante [PR #6](https://github.com/rvigil24/ml-delivery-app/pull/6), commit `f504c8f`; `main` local y remoto sincronizados antes del bloque siguiente.

### Cierre autorizado: T13–T14 — preparación y baseline

Rama `ml/T13-T14-preparacion-baseline`, creada desde `origin/main` actualizado
en `f504c8f`. Responsable: Ruben Vigil. T13 y T14 se implementaron en iteraciones
separadas; el cierre autorizado publica un solo PR y verifica su integración en remoto.

- T13: completada. Variables temporales cíclicas y selección explícita de predictores; 409,083 pedidos de entrenamiento, 136,799 de prueba y 399 purgados por etiqueta no disponible al corte. Corte `2022-10-23T00:00:00Z`, IDs disjuntos y datos versionados con hashes; 38 pruebas aprobadas en Python 3.12/3.9 al implementar T13. Segundo notebook con T13 ejecutable.
- T14: completada. `DummyRegressor(strategy="median")` ajustado solo con los 409,083 pedidos de entrenamiento; predicción constante 27.75 min. Test (136,799 pedidos): MAE 9.501230 min y RMSE 12.562496 min. Estrategia única fijada antes de evaluar, sin tuning; 40 pruebas aprobadas en Python 3.12/3.9 y resultados reproducidos en ambos intérpretes.

Por orden de Ruben se actualiza el backlog local, sin modificar el Excel ni
atribuir revisión independiente. Las dependencias y criterios de ambos IDs
se contrastaron con código, manifiestos, hashes y resultados reales. El segundo
notebook tiene diez celdas ejecutadas localmente sin errores y cinco pruebas
específicas; la ejecución directamente en Google Colab sigue pendiente.
El commit de integración y la sincronización de `main` se registran en GitHub y
la guía externa después del merge. T15 permanece pendiente y no se inicia aquí.
T13 solo prepara datos; T14 ajusta la referencia fija. No cambia el contrato HTTP. Coordenadas,
rutas y vehículos quedan fuera de la versión temporal experimental; el EDA
previo de la cohorte completa queda documentado como límite del test.

La preparación de datos T08 no incluye automáticamente features geográficas no validadas.
La confirmación de unidades geográficas queda como pendiente explícito para el
próximo bloque antes de calcular distancia física; no debe perderse al integrar.
El uso privado de S3 y los derechos sobre publicación de artefactos Meituan quedan
pendientes de revisión en T33/T19 antes de cualquier subida. La auditoría de calidad
no resuelve esa condición ni excluye AWS del diseño; ver la corrección en DATA_ML.

### Cierre autorizado: T15–T16 — modelos y validación

Rama `ml/T15-T16-modelos-validacion`, creada desde `origin/main` actualizado
en `9954b65` (T13–T14 integradas mediante PR #7). Responsable: Ruben Vigil.

- T15: completada y entrenada con los 409,083 pedidos de train, sin cargar ni evaluar test. Regresión lineal, Random Forest y LinearSVR; configuraciones iniciales fijas y escalado dentro de los pipelines cuando corresponde. Informes JSON/Markdown, notebook completo con 13 celdas ejecutadas sin errores y guía de estudio con evidencia real. 42 pruebas aprobadas en Python 3.12 y las dos nuevas también en 3.9.
- T16: completada y ejecutada; tres folds diarios crecientes dentro de train, con purga de etiquetas desconocidas al corte. GridSearchCV compara profundidades 6/12 del bosque y C=0.1/1 en LinearSVR, con regresión lineal y baseline como controles. Selección por MAE medio, RMSE diagnóstico; reajuste solo con train y test sin evaluar. Evidencia en `t16_validation.json`/Markdown y guía externa; notebook completo con 16 celdas ejecutadas sin errores. 44 pruebas aprobadas en Python 3.12 y las dos nuevas también en 3.9.

Por orden explícita de Ruben se registran T15 y T16 como completadas en el
backlog local, sin modificar el Excel ni atribuir revisión independiente.
Sus dependencias y criterios se contrastaron con implementación, reportes reales,
hashes y las comprobaciones anteriores: suite de 44 pruebas aprobada y 16 celdas
del notebook completo sin errores. Las dos pruebas nuevas de cada tarea también
pasaron en Python 3.9. La ejecución directamente en Google Colab sigue pendiente.
El cierre publica un único PR, verifica su integración en remoto y sincroniza
`main`; el resultado y el commit se registran en GitHub y la guía externa.
Las métricas de T15 son errores de entrenamiento y no seleccionan un modelo.
T17–T19 y las features geográficas no validadas quedan fuera del bloque.

### Cierre autorizado: T17–T18 — MLP y evaluación

Rama `ml/T17-T18-mlp-evaluacion`, creada desde `origin/main` actualizado en
`2a5f3de` (PR #8 integrado). Responsable: Ruben Vigil.

- T17: completada y entrenada. MLP PyTorch CPU `4→16→8→1`, 225 parámetros; tres folds T16, escalado de X/y solo con entrenamiento y elección de épocas por MAE medio interno. Se eligieron 7 de un máximo de 30 épocas; MAE CV 9.065874 min y RMSE CV 11.792678 min. Reajuste desde cero con los 409,083 pedidos train, sin cargar/evaluar test ni persistir modelo final. Evidencia local en `t17_mlp.json`/Markdown, curvas y guía externa. Notebook completo: 19 celdas sin errores; 46 pruebas aprobadas en Python 3.12 y las dos nuevas también en 3.9.
- T18: completada y evaluada; baseline, tres ML y MLP ajustados con configuraciones T16/T17 verificadas antes de cargar los mismos 136,799 pedidos test. MAE/RMSE/R², sesgo, P95 de error absoluto y desglose por día. MLP MAE 9.121785 min; bosque MAE 9.125362 min/RMSE 11.855652 min. Informes locales, gráfico y guía externa; notebook completo con 21 celdas sin errores, 48 pruebas aprobadas en Python 3.12 y las dos nuevas también en 3.9. No se retoca la receta con test ni se persiste el modelo final.

Por orden explícita de Ruben se registran T17 y T18 como completadas en el
backlog local, sin modificar el Excel ni atribuir revisión independiente.
Dependencias y criterios contrastados con implementación, reportes, hashes y
comprobaciones reales: 48 pruebas aprobadas en Python 3.12, las cuatro nuevas
del bloque también en 3.9 y notebook completo con 21 celdas sin errores.
Los datos permanecen intactos; gráficos y reportes siguen fuera de Git.
Google Colab directamente continúa pendiente. El cierre publica un único PR,
verifica su integración en remoto y sincroniza `main`; PR/commit y resultado
se registran en GitHub y la guía externa tras el merge.
T19 y las features geográficas sin validar quedan fuera del alcance.

### Cierre autorizado: T19 — artefacto final académico

Rama `ml/T19-modelo-final`, creada desde `origin/main` actualizado en `eac944a`
(PR #9 integrado). Responsable: Ruben Vigil. Entrega individual para cerrar ML;
T20 inicia lógica de negocio y no se incorpora a esta iteración.

- T19: completada para uso académico local. Random Forest profundidad 6 elegido por menor MAE interno (8.955647 min), sin seleccionar por test. Pipeline con transformación temporal + bosque, metadata, evidencia T16–T18 y ficha en `models/delivery-duration/meituan-temporal-rf-v1/`, ignorado por Git. Recarga comprobada sobre 409,083 pedidos train con tolerancia absoluta 1e-12 min; receta existente verificada sin sobrescribir. 50 pruebas aprobadas en Python 3.12 y las dos nuevas también en 3.9. Tres celdas nuevas T19 ejecutadas sin repetir las 21 anteriores; notebook con 24 celdas verificadas en etapas.

Por orden explícita de Ruben se registra T19 como completada en el backlog local,
sin modificar el Excel ni atribuir revisión independiente. Dependencias y criterios
contrastados con implementación, bundle, hashes, pruebas y evidencia del notebook.
El cierre publica un único PR con código/documentación; el artefacto queda fuera
de Git. Se verifica el merge y se sincroniza `main`; PR/commit y resultado se
registran después en GitHub y la guía externa. Google Colab directamente sigue
pendiente. No se carga test para exportar,
no se publica el modelo ni se acredita uso operativo. La revisión de términos y
autorización antes de subir artefactos a S3 sigue pendiente en T33; el desarrollo
local continúa conforme a DATA_ML. T20 y contratos HTTP quedan fuera del alcance.

### Cierre autorizado: T20–T21 — pedidos y cotizaciones

Rama `backend/T20-T21-pedidos-cotizaciones`, creada desde `origin/main`
actualizado en `a54a84b` (PR #10 integrado). Responsable: Ruben Vigil.

- T20: completada sobre la base aprobada explícitamente por Ruben. Servicio de registro/consulta/transiciones, puertos y adaptador en memoria, con historial UTC inmutable y actualización condicional atómica. Cancelación solo antes de asignar; rechazos sin mutación, incluidos reintentos y estados obsoletos. Avances bloqueados sin validador de cotización/asignación. Suite de 55 pruebas aprobada en Python 3.12 y las cinco nuevas también en Python 3.9, en un entorno aislado sin dependencias ML. Contratos, README, SPEC y guía externa actualizados.
- T21: completada con el alcance académico aprobado explícitamente por Ruben. Distancia Haversine en km, predictor local T19 cargado una vez y duración desde creación–entrega usando solo calendario UTC de creación. Devuelve borrador sin importes ni cambios de estado, marcado académico y cobertura sin validar. No convierte coordenadas raw Meituan ni inventa velocidad, zona o límite; cobertura/cotización comercial siguen pendientes. 60 pruebas aprobadas en Python 3.12, las cinco nuevas también en Python 3.9 e integración ilustrativa con el modelo real verificada sin reentrenar. Documentación, guía y fuentes actualizadas.

Por orden explícita de Ruben se registran T20 y T21 como completadas en el
backlog local, con la base de reglas y el alcance académico aprobados previamente.
No se modifica el Excel ni se atribuye revisión independiente. Criterios y
dependencias contrastados con código, contratos y comprobaciones reales: 60
pruebas aprobadas en Python 3.12, las diez nuevas del bloque también en 3.9 e
integración ilustrativa con el modelo T19 verificada sin reentrenar ni mutar
el pedido. Fuentes/modelo y dependencias comprobados; no se repiten experimentos.

El cierre publica un único PR, verifica su integración en remoto y sincroniza
`main`; PR/commit y resultado se registran después en GitHub y la guía externa.
La cobertura comercial, tarifas y requisitos de cotización/asignación siguen
pendientes; T21 entrega solo un borrador académico. MongoDB sigue en T32 y API
en T30. No se añaden dependencias, endpoints ni cambios AWS. T22 no se inicia aquí.

### Cierre autorizado: T22–T23 — tarifas y vehículos

Rama `backend/T22-T23-tarifas-vehiculos`, creada desde `origin/main`
actualizado en `78650aa` (PR #11 integrado). Responsable: Ruben Vigil.

- T22: completada; reglas configurables aprobadas explícitamente por Ruben e implementadas con Decimal/ROUND_HALF_UP. Política versionada con moneda/unidad/bases/precios por km obligatorios, costos del operador explícitos por envío y margen conciliado (puede ser negativo). Desglose académico inmutable sin modificar T21 ni cambiar estados; sin importes reales predeterminados. 31 pruebas del backend aprobadas en Python 3.12 y las cinco nuevas también en Python 3.9. Documentación y guía actualizadas.
- T23: completada; base configurable aprobada explícitamente por Ruben e implementada. Zona rectangular y máximos de distancia/carga para ambos vehículos, sin valores predeterminados; incluye bordes y límites iguales al máximo. Devuelve todas las opciones y motivos de rechazo, sin elección/asignación ni mutar pedido/historial, precios o modelo ML. 36 pruebas del backend aprobadas en Python 3.12 y las cinco nuevas también en Python 3.9. Documentación, guía y fuentes actualizadas.

Por orden explícita de Ruben se registran T22 y T23 como completadas en el
backlog local, con fórmulas y criterios configurables aprobados previamente.
No se modifica el Excel ni se atribuye revisión independiente. Dependencias y
criterios contrastados con código, contratos y comprobaciones reales: 36 pruebas
del backend aprobadas en Python 3.12 y las diez nuevas del bloque también en 3.9.
Código/artefactos ML sin cambios: sus pruebas, entrenamientos y notebooks no se
repiten. Fuentes y modelo comprobados; dependencias compatibles y sin adiciones.

El cierre publica un único PR, verifica su integración en remoto y sincroniza
`main`; PR/commit y resultado se registran después en GitHub y la guía externa.
No se fijan valores reales de tarifas, costos, zonas o límites. La emisión
comercial y los avances de T20 siguen sujetos a los requisitos pendientes;
no se añaden API, persistencia o infraestructura. T24 no se inicia en este cierre.

### Cierre autorizado: T24–T25 — rutas y escenarios de costos

Rama `backend/T24-T25-rutas-costos`, creada desde `origin/main` actualizado
en `41c0d93` (PR #12 integrado). Responsable: Ruben Vigil.

- T24: completada; base académica aprobada explícitamente por Ruben e implementada. Ruta abierta desde inicio/grupo explícitos, vecino más cercano Haversine, precedencia recogida/entrega y desempate por ID. Máximo y zona T23 obligatorios, sin valores predeterminados; rechaza duplicados, pedidos no planificables y extremos fuera. Snapshots/paradas/tramos/totales inmutables, sin asignación o cambios de estado, capacidad/tiempos viales sin validar. 41 pruebas del backend aprobadas en Python 3.12 y las cinco nuevas también en Python 3.9. Documentación/guía/fuentes actualizadas.
- T25: completada; supuestos académicos aprobados explícitamente por Ruben e implementados. Mismos pedidos/snapshots, inicio, políticas y moneda; rutas abiertas independientes por individual frente a un recorrido agrupado. Una base de pago por recorrido y costos explícitos para cada individual/grupo, sin ingresos/ROI o descuentos al cliente. Desgloses, agregados y diferencias con signo; sin mutar pedidos ni garantizar capacidad/viabilidad o ahorro. 46 pruebas del backend aprobadas en Python 3.12 y las cinco nuevas también en Python 3.9. Documentación/guía/fuentes actualizadas.

Por orden explícita de Ruben se registran T24 y T25 como completadas en el
backlog local, con las bases académicas y supuestos aprobados previamente.
No se modifica el Excel ni se atribuye revisión independiente. Dependencias y
criterios contrastados con implementación, contratos y comprobaciones reales:
46 pruebas del backend aprobadas en Python 3.12 y las diez nuevas del bloque
también en 3.9. Fuentes y modelo T19 comprobados; dependencias compatibles.
No se repiten pruebas/entrenamientos/notebooks ML sin cambios de código.

El cierre publica un único PR, verifica su integración en remoto y sincroniza
`main`; PR/commit y resultado se registran después en GitHub y la guía externa.
No se inventan tamaños/límites reales, distancias viales, velocidades, costos
o tiempos; capacidad/viabilidad siguen sin validar. No se integran API,
persistencia o AWS. T26 no se inicia en este cierre.

### Cierre autorizado: T26–T27 — asignación y solicitudes simuladas

Rama `backend/T26-T27-simulacion`, creada desde `origin/main` actualizado
en `0b04fa0` (PR #13 integrado). Responsable: Ruben Vigil.

- T26: completada sobre base simulada aprobada explícitamente por Ruben. Selección por ID, aprobación/disponibilidad, pedidos confirmados y validador de cotización obligatorio; políticas/cargas explícitas. Comprueba zonas, distancia total T24 y carga acumulada T23; reserva grupo y ocupa repartidor atómicamente en memoria, revalidando snapshots. Progreso según paradas; liberación explícita solo con todos entregados. Siete pruebas nuevas, incluidas concurrencia y rechazo sin escrituras; 53 del backend aprobadas en Python 3.12 y las siete nuevas también en 3.9. Contratos, README, SPEC y guía externa actualizados; fuentes para Colab regeneradas.
- T27: completada. Servicio de solicitudes estructuradas que delega registro/consulta en T20; conversación inmutable reconstruida de detalles/historial, con acuse y actualizaciones UTC marcadas como simulación. Consultas sin escrituras, rechazos sin acuses de éxito y sin omitir requisitos de cotización/asignación. Cinco pruebas nuevas; 58 del backend aprobadas en Python 3.12 y las cinco nuevas también en 3.9. Contratos, README, SPEC, guía externa y fuentes Colab actualizados. Sin canal real, lenguaje natural, teléfonos o credenciales.

Sin validador autoritativo de cotización, el servicio falla sin asignar; no se
fabrica una cotización comercial ni se habilita el flujo completo. Catálogo de
repartidores explícito y efímero. Sin API, MongoDB, pagos, GPS o AWS.

Por orden explícita de Ruben se registran T26 y T27 como completadas en el
backlog local. Dependencias y criterios contrastados con implementación y
contratos; 58 pruebas del backend aprobadas en Python 3.12 y las doce nuevas
del bloque también en Python 3.9. Las fuentes coinciden con el paquete verificado
y los hashes del artefacto T19 permanecen intactos. Pasaron `uv lock --check`,
`uv pip check` y `git diff --check`; no se repiten pruebas o entrenamientos ML
sin cambios. No se modifica el Excel ni se atribuye revisión independiente.

El cierre publica un único PR, verifica la inclusión del commit en `origin/main`
y sincroniza `main` local; resultado/PR/commit se registran en GitHub y la guía
externa. Se regenera el ZIP de fuentes desde `main` limpio. La integración
comercial de cotizaciones sigue pendiente; T28 no se inicia en este cierre.

### Cierre autorizado: T28–T29 — efectivo y análisis financiero

Rama `backend/T28-T29-efectivo-finanzas`, creada desde `origin/main` actualizado
en `80c88c1` (PR #14 integrado). Responsable: Ruben Vigil.

- T28: completada sobre base simulada aprobada explícitamente por Ruben. Efectivo solo del envío, con importe/moneda de cotización validada; estados pendiente, cobrado y entregado al operador. Cobro tras entrega logística y montos completos, sin parciales, devoluciones o deducciones del repartidor. Registro/historial UTC inmutables y transiciones atómicas locales; duplicados/concurrencia sin eventos extra. Seis pruebas nuevas, 64 del backend aprobadas en Python 3.12 y las seis nuevas también en Python 3.9. Contratos, README, SPEC, guía externa y fuentes Colab actualizados.
- T29: completada sobre fórmulas y alcance aprobados explícitamente por Ruben. Escenario homogéneo por período con volumen/desglose T22, costos fijos adicionales, inversión y unidad monetaria explícitos. Agregados conciliados, resultado con pérdidas, equilibrio entero exacto o inexistente y ROI simple del período o no calculable. Costos fijos excluyen lo ya incluido por envío; no predice demanda ni cuenta efectivo como ingreso adicional. Cinco pruebas nuevas; 69 del backend aprobadas en Python 3.12 y las cinco nuevas también en Python 3.9. Contratos, README, SPEC, guía externa y fuentes Colab actualizados.

Sin fuente autoritativa de cotización validada, la apertura se bloquea. Se
conservan términos por pedido, sin modificar logística/disponibilidad. Sin
dinero real, API, persistencia o AWS.

Por orden explícita de Ruben se registran T28 y T29 como completadas en el
backlog local. Dependencias y criterios contrastados con implementación y
contratos; 69 pruebas del backend aprobadas en Python 3.12 y las once nuevas
del bloque también en Python 3.9. Las 93 fuentes coinciden con el paquete
verificado y los hashes del artefacto/evidencia T19 permanecen intactos.
Pasaron `uv lock --check`, `uv pip check` y `git diff --check`; no se repiten
pruebas o entrenamientos ML sin cambios. No se modifica el Excel ni se atribuye
revisión independiente.

El cierre publica un único PR, verifica la inclusión del commit en `origin/main`
y sincroniza `main` local; resultado/PR/commit se registran en GitHub y la guía
externa. Se regenera el ZIP de fuentes desde `main` limpio. La fuente comercial
de cotización y los valores reales del escenario financiero siguen pendientes;
T30 no se inicia en este cierre.

### Cierre autorizado: T30–T31 — API e integración predictiva

Rama `backend/T30-T31-api-prediccion`, creada desde `origin/main` actualizado
en `468a3af` (PR #15 integrado). Responsable: Ruben Vigil.

- T30: completada. FastAPI/Pydantic, Uvicorn y cliente de pruebas compatible por versión de Python; lock actualizado. GET health, POST predict con creación ISO 8601 y zona horaria, normalización UTC, OpenAPI/docs. PredictionService reutiliza puerto/modelo T19/T21 cargado una vez por inicio; 422/503/500 sin detalles privados o fallback ficticio. Seis pruebas nuevas; 75 del backend aprobadas en Python 3.12 sin avisos y las seis nuevas también en Python 3.9. Uvicorn por HTTP local con bundle real comprobado; evidencia ilustrativa en data/reports/presentation/t30_api_smoke.json, servidor detenido. Documentación, guía y fuentes Colab actualizadas.
- T31: completada con alcance académico. QuotePreviewService combina estimación/precios/vehículos T21–T23 sobre un único snapshot solicitado y la fecha de creación guardada, usando el mismo PredictionService/modelo de T30. POST /orders/{order_id}/quotes exige configuración explícita; devuelve duración/importes/políticas/opciones y marcas de cobertura/cotización comercial sin validar, sin reservar/persistir o cambiar estados. Cinco pruebas nuevas; 80 del backend aprobadas en Python 3.12 y las once nuevas del bloque también en Python 3.9. HTTP con bundle real y reglas/ubicaciones de fixture verificado sin mutación; evidencia en data/reports/presentation/t31_quote_smoke.json. Documentación, guía y fuentes Colab actualizadas. Sin dependencias nuevas.

Sin modelo configurado/compatible, health informa model_available=false y
predict falla con 503. El artefacto actual requiere su entorno Python 3.12;
las pruebas HTTP en 3.9 no relajan ese contrato. Sin reentrenamiento, MongoDB,
S3, canales reales o despliegue.

Por orden explícita de Ruben se registran T30 y T31 como completadas en el
backlog local. Dependencias y criterios contrastados con implementación y
contratos; 80 pruebas del backend aprobadas en Python 3.12 sin avisos y las once
nuevas del bloque también en Python 3.9. Las 100 fuentes coinciden con el
paquete verificado, los hashes del artefacto/evidencia T19 permanecen intactos
y las pruebas HTTP locales con modelo real están documentadas. Pasaron
`uv lock --check`, `uv pip check` y `git diff --check`; no se repiten pruebas,
entrenamientos o notebooks ML sin cambios. No se modifica el Excel ni se
atribuye revisión independiente.

El cierre publica un único PR, verifica la inclusión del commit en `origin/main`
y sincroniza `main` local; resultado/PR/commit se registran en GitHub y la guía
externa. Se regenera el ZIP de fuentes desde `main` limpio. La previsualización
no sustituye los requisitos comerciales T20/T26/T28; cobertura/cotización
comercial y sus valores reales siguen pendientes. T32 no se inicia en este cierre.

### Cierre autorizado: T32–T33 — persistencia y objetos

Rama `backend/T32-T33-almacenamiento`, desde `origin/main` actualizado en
`6ebcf66` (PR #16 integrado). Responsable: Ruben Vigil.

- T32: implementada y verificada localmente. Atlas Free sobre AWS us-east-1 elegido por Ruben; aún sin clúster, autorizó código/pruebas locales. PyMongo, adaptadores de negocios/pedidos/repartidores/asignaciones/efectivo, codec preciso, validadores/índices explícitos, CAS y transacciones reales. CRUD de catálogos, registro/consulta/listado/transiciones de pedidos por HTTP; referencias e historial protegidos. Cliente compartido/cerrado por lifespan, 503 sin fallback ni autocreación de colecciones no validadas. 87 pruebas del backend aprobadas con MongoDB 8.0 real y las siete nuevas también en Python 3.9; persistencia tras reinicio de servidor comprobada. Evidencia agregada local, contratos/README/guía/fuentes Colab actualizados. Conexión cloud Atlas pendiente; no se afirma haberla probado.
- T33: implementada y verificada en AWS real por autorización explícita de Ruben. Perfil remote-admin y endpoint S3 real seleccionados por operación, sin cambiar floci/localhost:4566 global. Puerto/adaptador de objetos, SHA-256, PUT condicional, descargas atómicas y modelo recuperable al inicio desde manifiesto fijado. AWS CLI publicó 47 objetos privados (2,183,341 bytes) en models/delivery-duration/meituan-temporal-rf-v1/, datasets/meituan/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/ (solo metadatos/licencia) y docs/ml-delivery-app/ed6b32c222a2706df91c/. Checksums/tamaños/ACL privados verificados; recibo incremental t33_s3_publication.json y descarga/inferencia real t33_s3_model_smoke.json, en data/reports/presentation/. .env no secreto configurado y carga explícita con uv comprobada. CSV/notebooks ejecutados excluidos; condiciones Meituan conservadas. Cinco pruebas nuevas; 92 del backend con MongoDB real aprobadas y las cinco de S3 también en Python 3.9 (avisos de fin de soporte Boto3). Sin cambios de bucket/IAM, recursos nuevos o despliegue; documentación/guía/fuentes actualizadas.

Cierre autorizado por Ruben: T32 y T33 se registran como completadas con esta
evidencia. Se publica un único PR y se verifica la integración del commit en
origin/main; la guía externa registra el resultado efectivo. Sin modificar Excel.
La persistencia no resuelve requisitos de cotización comercial; Docker/Compose
del producto, Terraform y despliegues permanecen en sus tareas.

**Verificación Atlas posterior — 2026-11-04:** Ruben creó el clúster y guardó
la URI en .env. Se completó MONGODB_DATABASE=delivery, que estaba vacío, sin
mostrar credenciales. Conexión real, cinco colecciones con validadores/índices,
transacción snapshot de lectura y GET API de negocios/repartidores/pedidos
verificados. En la misma aplicación se recuperó el modelo de S3 y se comprobó
inferencia real sobre fecha ilustrativa. Sin pedidos/datos ficticios añadidos
a Atlas; clientes cerrados al terminar. Evidencia sin URI ni credenciales:
data/reports/presentation/t32_atlas_smoke.json. La condición previa de conexión
cloud pendiente de T32 queda resuelta; no se afirma una repetición de toda la
suite de integración contra Atlas. El cierre conserva esta distinción entre
las pruebas locales completas y la comprobación cloud.

### Cierre autorizado: T34 — Docker y Docker Compose

Responsable: Ruben Vigil. Rama `infra/T34-docker`, creada desde `origin/main`
actualizado en `aab5d02` (PR #17 integrado). Alcance autorizado al continuar
con la siguiente tarea: únicamente T34; sin publicación Git automática.

**Dependencias:** API T30–T31, adaptadores MongoDB T32 y modelo T19. El
frontend aún no existe (T47); Atlas/S3 continúan como servicios externos.

**Implementar:** imagen Python 3.12.14 con dependencias de inferencia tomadas
del lock, usuario sin privilegios y contexto sin secretos/datasets/modelos;
Compose local con réplica MongoDB de un nodo, preparación idempotente del
esquema, volumen persistente, modelo montado en lectura y healthchecks.

**Terminado cuando:** build real, arranque ordenado, lecturas/escrituras HTTP,
transacciones, persistencia tras recrear contenedores, inferencia con el bundle
local y limpieza comprobados. Documentar comandos, límites y uso opcional de
Atlas/S3 sin modificar esos servicios. No incluye frontend, CI/CD, Terraform
ni despliegue AWS. Ruben autorizó el cierre: se actualiza el backlog local,
se publica un PR y se verifica la integración en origin/main; sin modificar Excel.

**Evidencia T34 — 2026-11-04:** imagen construida realmente con 32 dependencias
externas bloqueadas, Python 3.12.14 y UID 10001; sin Torch/Spark/Dask/Matplotlib/
pytest en runtime. Compose válido y arranque con réplica, inicializador y API
saludables. Fixture técnico creado por HTTP, pedido cancelado con historial UTC
y persistencia conservada tras `down`/`up` que recreó los contenedores. El modelo
T19 local cargó y predijo sobre fecha ilustrativa con su entorno exacto. Se
eliminaron únicamente contenedores/redes/volumen del proyecto temporal
`delivery-t34-check`; imagen conservada. Evidencia agregada ignorada:
`data/reports/presentation/t34_docker.json`. Guía y ZIP actualizados; sin pruebas
cloud ni cambios en dependencias del proyecto. Cierre Git autorizado por Ruben;
el resultado efectivo del PR y merge se registra en la guía externa.


### Cierre autorizado: T35 — pruebas unitarias existentes

**Responsable:** Ruben Vigil. Rama `test/T35-unitarias`, desde origin/main
`3bd57fb` (T34 integrada). **Dependencia:** dominio implementado en T04.

**Criterio de aceptación:** al menos diez pruebas unitarias pytest del producto,
con resultados reales. Se reutilizan las pruebas existentes, sin añadir casos
redundantes ni ejecutar la suite completa, por solicitud de Ruben.

**Evidencia — 2026-11-04:** `uv run --locked pytest backend/tests/test_domain.py -q`
produjo **14 passed in 0.02s**. Comprueba negocios, coordenadas, pedidos,
repartidores, procedencia/duración, precisión monetaria y cotizaciones. Son
fixtures sintéticos explícitos, sin servicios externos, datasets o entrenamiento.
T35 satisface el mínimo; no fue necesario modificar código o añadir pruebas.
README y guía externa actualizados. Cierre autorizado por Ruben: se marca T35
completada y se publica un PR, verificando su integración en origin/main.
Sin modificar Excel ni iniciar T36; no se repiten pruebas sin cambios de código.

## Instrucciones concretas y criterios de aceptación: T01–T33

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

### T13 — Preparar variables predictoras y conjuntos de entrenamiento/prueba

**Responsable:** Ruben Vigil

**Dependencia:** datos/target validados y preparación T07–T12 verificable.

**Implementar:** variables conocidas antes de cotizar, transformación reutilizable y partición reproducible sin mezclar pedidos ni aprender del futuro.

**Terminado cuando:** predictores/target/trazabilidad separados explícitamente, train/test materializados con corte documentado y controles de aislamiento/etiquetas disponibles, pruebas reales, manifiesto y limitaciones. Sin baseline ni modelos de tareas posteriores.

### T14 — Implementar un modelo baseline

**Responsable:** Ruben Vigil

**Dependencia:** T13, variables y particiones verificadas.

**Implementar:** referencia sencilla elegida antes de evaluar test, ajustada solo con entrenamiento y evaluada con errores reales de regresión.

**Terminado cuando:** receta reproducible, constante aprendida de train, MAE/RMSE en minutos con versión/hashes de datos y software, pruebas de aislamiento y explicación de limitaciones. No usar test para elegir estrategia ni implementar familias ML de T15.

### T15 — Entrenar tres algoritmos ML de distintas familias

**Responsable:** Ruben Vigil

**Dependencia:** variables/particiones T13 y baseline T14 verificadas e integradas.

**Implementar:** regresión lineal, ensamble de árboles y regresión por vectores de soporte; ajustar únicamente con train y registrar configuraciones reproducibles.

**Terminado cuando:** tres modelos entrenados con datos reales y predictores permitidos, transformaciones ajustadas solo en train, parámetros/semillas y procedencia verificables, resultados de entrenamiento claramente identificados, pruebas de aislamiento y reproducción en notebook. Sin tuning T16, selección por test, MLP ni persistencia final.

### T16 — Aplicar validación cruzada y optimización de hiperparámetros

**Responsable:** Ruben Vigil

**Dependencia:** modelos T15 entrenados y particiones T13 verificadas.

**Implementar:** validación interna temporal con etiquetas disponibles en cada corte y búsqueda acotada de hiperparámetros, usando los mismos folds por candidato y familia.

**Terminado cuando:** cortes/conteos/purgas verificables, escaladores ajustados dentro de cada fold, candidatos y criterio de selección explícitos, métricas por fold y parámetros elegidos reproducibles, pruebas de aislamiento y notebook. Sin consultar test para tuning, entrenar MLP ni seleccionar/persistir el modelo final.

### T17 — Implementar y entrenar una red neuronal MLP

**Responsable:** Ruben Vigil

**Dependencia:** particiones T13 y protocolo temporal T16 verificados.

**Implementar:** MLP pequeña con PyTorch CPU, transformaciones aprendidas solo con train, selección interna de épocas y reajuste sin usar test.

**Terminado cuando:** entrenamiento real, arquitectura/semillas/configuración reproducibles, curvas y métricas con unidades explícitas, escaladores aislados por fold, épocas elegidas sin test, pruebas y notebook ejecutables. Sin comparación final T18, persistencia T19 ni API.

### T18 — Evaluar y comparar modelos mediante MAE, RMSE y métricas pertinentes

**Responsable:** Ruben Vigil

**Dependencia:** baseline T14, selección interna T16 y MLP T17 verificables.

**Implementar:** comparación de los cinco modelos sobre el mismo test temporal, congelando parámetros/épocas antes de cargarlo; analizar errores con trazabilidad.

**Terminado cuando:** reportes reproducibles con MAE/RMSE/R², errores firmados/absolutos y por día, mismo conjunto para todos, procedencia de las decisiones de CV, pruebas y notebook. Sin tuning a partir del test, selección/persistencia T19 ni cambios HTTP/AWS.

### T19 — Seleccionar, guardar y documentar el modelo final

**Responsable:** Ruben Vigil

**Dependencia:** T13–T18 verificables, selección por CV y comparación test congelada.

**Implementar:** seleccionar por menor MAE interno, reajustar solo con train y persistir pipeline/transformación con versión, metadatos, procedencia y ficha de uso académico.

**Terminado cuando:** artefacto local recargable con predicciones equivalentes, hashes/versiones comprobados, evidencia y limitaciones conservadas, receta reproducible sin sobrescritura, pruebas/notebook. Sin elegir con test, publicar en S3, autorizar uso operativo ni implementar API.

### T20 — Implementar registro y gestión de pedidos y sus estados

**Responsable:** Ruben Vigil

**Dependencia:** modelos T04 y contratos de ciclo de vida aprobados por Ruben.

**Implementar:** servicio de registro/consulta, flujo aprobado con requisitos explícitos, historial UTC y actualizaciones condicionales; repositorio local detrás de puertos, sin adelantar MongoDB/API.

**Terminado cuando:** negocio/origen/ID/estado inicial validados, historial inmutable, matriz y cancelación respetadas, rechazos sin escrituras, avances bloqueados sin requisitos, concurrencia probada y contratos/documentación/guía actualizados. Sin cotizaciones, asignaciones, tarifas o datos ML fabricados.

### T21 — Implementar estimación de distancia y tiempo para cotizaciones

**Responsable:** Ruben Vigil

**Dependencia:** pedido/historial T20, modelo local T19 y base académica aprobada.

**Implementar:** Haversine en km y predictor T19 detrás de un puerto, con procedencia/intervalo/versiones y limitaciones visibles; borrador académico sin importes ni mutación del pedido.

**Terminado cuando:** geometría y unidades comprobadas, calendario de creación en UTC, modelo cargado una vez sin entrenar, fallos explícitos sin tiempos ficticios, cobertura sin validar y uso académico marcados, pruebas/integración real y documentación/guía. Sin emitir cotización comercial, inventar velocidades/zonas, cambiar estados o integrar HTTP/AWS.

### T22 — Desarrollar cálculo de tarifas, costos operativos y remuneración

**Responsable:** Ruben Vigil

**Dependencia:** modelos monetarios T04, borrador T21 y reglas aprobadas por Ruben.

**Implementar:** fórmulas aprobadas con configuración/costos explícitos, Decimal, redondeo y trazabilidad; solo desglose académico.

**Terminado cuando:** componentes/margen conciliados, moneda/unidad/versión preservadas, pérdida visible, entradas inválidas o configuración ausente rechazadas, sin precios predeterminados ni duplicar costos del repartidor; pruebas, contratos y guía. Sin emitir/cobrar cotización ni adelantar T23/HTTP/DB.

### T23 — Implementar reglas para bicicleta y motocicleta

**Responsable:** Ruben Vigil

**Dependencia:** modelos T04, distancia T21 y criterios configurables aprobados por Ruben.

**Implementar:** política versionada de zona/límites explícitos, comprobación inclusiva de extremos/distancia/carga y motivos por vehículo, sin selección automática.

**Terminado cuando:** ambos vehículos configurados, entradas válidas/unidades explícitas, bordes y límites probados, todos/uno/ninguno como opciones, pedido/historial y ML intactos, snapshot reproducible, pruebas/contratos/guía. Sin valores comerciales inventados, tiempos por vehículo ni asignación T26.

### T24 — Implementar sugerencia sencilla de rutas y orden de entregas

**Responsable:** Ruben Vigil

**Dependencia:** pedidos T20, distancia T21, ServiceArea T23 y base de planificación aprobada.

**Implementar:** ruta académica abierta por vecino cercano con recogida previa a entrega, grupo/inicio/configuración explícitos, snapshots y tramos reproducibles.

**Terminado cuando:** precedencia y desempate comprobados, dos paradas por pedido, total de tramos sin retorno automático, rechazos sin filtrar entradas, pedido/historial intactos y restricciones visibles; pruebas, contratos y guía. Sin óptimo garantizado, capacidad/tiempos viales/asignación ni comparación T25.

### T25 — Comparar costos de entregas individuales y agrupadas

**Responsable:** Ruben Vigil

**Dependencia:** política T22, rutas T24 y supuestos de comparación aprobados.

**Implementar:** comparación académica de costos del operador con mismas entradas, costos explícitos, base por recorrido y diferencias con signo.

**Terminado cuando:** snapshots/rutas/políticas/costos trazables, componentes/totales conciliados, redondeo/moneda preservados, caso agrupado más caro y caso individual idéntico probados, entradas incompletas rechazadas y pedido/historial intactos. Sin ingresos/ROI, ahorro garantizado, asignación o capacidad/vialidad implícitas; contratos y guía actualizados.

### T26 — Desarrollar simulador de asignación de repartidores aprobados

**Responsable:** Ruben Vigil

**Dependencias:** pedidos/estados T20, reglas T23, rutas T24 y base simulada aprobada. La ejecución requiere evidencia explícita de cotización confirmada; sin ella queda bloqueada.

**Implementar:** selección por ID, comprobaciones de aprobación/disponibilidad, zona, distancia total y carga acumulada; reserva atómica local con historial, progreso y liberación controlados.

**Terminado cuando:** estados/snapshots se revalidan antes de reservar todo el grupo y ocupar al repartidor; rechazos, duplicados y concurrencia no producen cambios parciales; solo se ejecutan paradas en orden y se libera tras todas las entregas. Configuración/cargas explícitas, límites inclusivos, registro inmutable UTC, contratos/guía/pruebas. Sin cotizaciones, posiciones, tiempos o datos ML fabricados; sin canales reales ni persistencia anticipada.

### T27 — Implementar simulación de mensajes y solicitudes por WhatsApp

**Responsable:** Ruben Vigil

**Dependencia:** registro, consulta e historial de pedidos T20. Sin requerir canal real o API/UI anticipadas.

**Implementar:** solicitud estructurada mediante OrderService y representación inmutable de mensajes simulados del cliente/sistema, reconstruida del historial existente.

**Terminado cuando:** solicitud válida registrada con acuse; errores/duplicados sin éxito ficticio; actualizaciones solo de eventos aceptados con fechas UTC; consultas repetidas sin escrituras. Simulación/reconstrucción explícitas, requisitos T20/T26 intactos, pruebas/contratos/guía. Sin tarifas, tiempos, cotizaciones o mensajes externos fabricados; UI y sincronización mantienen su alcance posterior.

### T28 — Simular pagos en efectivo y estados contables

**Responsable:** Ruben Vigil

**Dependencias:** pedidos/historial T20 y base simulada aprobada. La apertura requiere fuente autoritativa de cotización validada con importe/moneda; los borradores T21/T22 no la sustituyen.

**Implementar:** expectativa única por pedido y flujo pendiente → cobrado → entregado al operador, por el importe completo del envío, con historial UTC independiente de la logística.

**Terminado cuando:** apertura bloqueada sin evidencia; cobro solo tras entrega; importes/moneda exactos y términos conservados, sin deducciones o redondeos implícitos. Rechazos, duplicados, fechas inválidas y concurrencia no escriben eventos extra; snapshots inmutables y pedido/asignación intactos. Pruebas, contratos y guía actualizados. Sin dinero real, parciales/devoluciones, ROI o persistencia anticipada.

### T29 — Elaborar análisis financiero: márgenes, costos fijos, punto de equilibrio y ROI estimado

**Responsable:** Ruben Vigil

**Dependencias:** desglose unitario T22 y fórmulas/alcance académico aprobados. Todos los valores son entradas explícitas; no requiere convertir efectivo T28 en ingresos ni inventar datos comerciales.

**Implementar:** escenario financiero homogéneo por período con agregados de ingresos/costos, contribución, resultado, equilibrio entero y ROI simple, conservando entradas y supuestos.

**Terminado cuando:** moneda/unidad/margen conciliados; costos fijos adicionales sin doble conteo declarado; pérdidas visibles y ceros/margen no positivo/inversión cero resueltos. Equilibrio calculado con techo exacto y aproximación solo en ROI, sin pérdida monetaria silenciosa. Proyección inmutable y académica sin demanda validada, pruebas/contratos/guía; sin valores predeterminados, rentabilidad observada atribuida, cambios de pedidos o infraestructura.

### T30 — Implementar API FastAPI con /health, /predict y documentación OpenAPI

**Responsable:** Ruben Vigil

**Dependencias:** artefacto T19 y puerto/adaptador de inferencia T21; contrato temporal y limitaciones validados en DATA_ML/ARCHITECTURE.

**Implementar:** API local mínima con DTOs HTTP, health, inferencia, OpenAPI y carga única del bundle propio al inicio, sin funciones de T31 o almacenamiento.

**Terminado cuando:** entrada con fecha/zona UTC y sin features extra, salida académica trazable, health distinto de inferencia disponible, errores 422/503/500 sin detalles privados, modelo no cargado por request ni fallback ficticio. Pruebas HTTP/compatibilidad 3.9+, integración local real sin reentrenar, dependencias/lock, ejecución/contratos/guía actualizados. Sin MongoDB/S3, canales, cotización comercial o despliegue anticipados.

### T31 — Integrar el modelo predictivo con el motor de cotizaciones

**Responsable:** Ruben Vigil

**Dependencias:** inferencia/API T19/T21/T30, precios T22 y vehículos T23 con bases académicas aprobadas; políticas, costos y pedido explícitos.

**Implementar:** previsualización académica que combine modelo, distancia, importes y reglas en un único snapshot; exponer por el endpoint de cotizaciones propuesto sin emitir cotización comercial ni anticipar persistencia.

**Terminado cuando:** se reutiliza el modelo de T30 y la creación guardada, una lectura por pedido, importes/opciones trazables e historial intacto. Configuración/entrada/estado/modelo ausentes o inválidos producen errores documentados, sin defaults o tiempos ficticios; ningún vehículo admisible no se presenta como cobertura validada. Pruebas HTTP/3.9+, integración real ilustrativa, contratos y guía actualizados. Los requisitos comerciales T20/T26/T28 siguen bloqueados sin fuente autoritativa; no hay selección automática, almacenamiento o despliegue anticipados.

### T32 — Configurar MongoDB con CRUD, índices y validaciones

**Responsable:** Ruben Vigil

**Dependencias:** entidades, puertos y garantías T04/T20/T26/T28 y API T30–T31. Atlas Free AWS us-east-1 elegido; desarrollo/pruebas locales autorizados mientras no exista clúster.

**Implementar:** adaptadores MongoDB/PyMongo y composición API con cliente compartido, CRUD operativo, persistencia de historiales/asignaciones/efectivo, validadores, índices, CAS y transacciones sin filtrar BSON al dominio.

**Terminado cuando:** persistencia entre conexiones/reinicio, precisión UTC/Decimal, duplicados, esquema, CRUD HTTP, referencias, conflictos y rollback real comprobados. Configuración privada explícita, esquema preparado/verificado antes de usarlo y fallo 503 sin fallback; compatibilidad 3.9+, contratos/guía/pruebas. Conexión Atlas se verifica cuando haya clúster/URI y se distingue de pruebas locales; sin crear cloud, autorizar cotizaciones o anticipar S3/Docker/Terraform.

### T33 — Integrar almacenamiento de objetos con S3 o MinIO

**Responsable:** Ruben Vigil

**Dependencias:** bucket existente/configuración AWS y artefactos reales con términos revisados. Ruben autorizó AWS CLI y subidas a ml-kodigo-resources; CSV Meituan excluidos de esta publicación.

**Implementar:** puerto/adaptador de objetos, claves versionadas, escritura condicional, checksum y descarga atómica; publicación curada con manifiestos/recibos y modelo opcional desde S3 al iniciar API.

**Terminado cuando:** acceso AWS real/región y objetos privados comprobados, hashes/tamaños preservados, conflictos sin sobrescribir, errores sanitizados y recibos reanudables. Integración real de descarga/inferencia más tests SDK/3.9+, configuración/docs/guía. Sin bucket nuevo, cambios IAM/políticas, secretos versionados, frontend privilegiado, reentrenamiento o registros Meituan distribuidos sin resolver sus términos.

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
| T13 | Machine Learning y Deep Learning | Preparar variables predictoras y conjuntos de entrenamiento/prueba | Ruben Vigil | Completada |
| T14 | Machine Learning y Deep Learning | Implementar un modelo baseline | Ruben Vigil | Completada |
| T15 | Machine Learning y Deep Learning | Entrenar tres algoritmos ML de distintas familias | Ruben Vigil | Completada |
| T16 | Machine Learning y Deep Learning | Aplicar validación cruzada y optimización de hiperparámetros | Ruben Vigil | Completada |
| T17 | Machine Learning y Deep Learning | Implementar y entrenar una red neuronal MLP | Ruben Vigil | Completada |
| T18 | Machine Learning y Deep Learning | Evaluar y comparar modelos mediante MAE, RMSE y otras métricas pertinentes | Ruben Vigil | Completada |
| T19 | Machine Learning y Deep Learning | Seleccionar, guardar y documentar el modelo final | Ruben Vigil | Completada |
| T20 | Lógica del negocio y simulación | Implementar registro y gestión de pedidos y sus estados | Ruben Vigil | Completada |
| T21 | Lógica del negocio y simulación | Implementar estimación de distancia y tiempo para cotizaciones | Ruben Vigil | Completada |
| T22 | Lógica del negocio y simulación | Desarrollar cálculo de tarifas, costos operativos y remuneración del repartidor | Ruben Vigil | Completada |
| T23 | Lógica del negocio y simulación | Implementar reglas para entregas en bicicleta y motocicleta | Ruben Vigil | Completada |
| T24 | Lógica del negocio y simulación | Implementar sugerencia sencilla de rutas y orden de entregas | Ruben Vigil | Completada |
| T25 | Lógica del negocio y simulación | Comparar costos de entregas individuales y agrupadas | Ruben Vigil | Completada |
| T26 | Lógica del negocio y simulación | Desarrollar simulador de asignación de repartidores aprobados | Ruben Vigil | Completada |
| T27 | Lógica del negocio y simulación | Implementar simulación de mensajes y solicitudes por WhatsApp | Ruben Vigil | Completada |
| T28 | Lógica del negocio y simulación | Simular pagos en efectivo y estados contables | Ruben Vigil | Completada |
| T29 | Lógica del negocio y simulación | Elaborar análisis financiero: márgenes, costos fijos, punto de equilibrio y ROI estimado | Ruben Vigil | Completada |
| T30 | API, almacenamiento e infraestructura | Implementar API FastAPI con /health, /predict y documentación OpenAPI | Ruben Vigil | Completada |
| T31 | API, almacenamiento e infraestructura | Integrar el modelo predictivo con el motor de cotizaciones | Ruben Vigil | Completada |
| T32 | API, almacenamiento e infraestructura | Configurar MongoDB con CRUD, índices y validaciones | Ruben Vigil | Completada |
| T33 | API, almacenamiento e infraestructura | Integrar almacenamiento de objetos con S3 o MinIO | Ruben Vigil | Completada |
| T34 | API, almacenamiento e infraestructura | Contenerizar los servicios mediante Docker y Docker Compose | Ruben Vigil | Completada |
| T35 | Pruebas, documentación y entrega | Implementar al menos 10 pruebas unitarias con pytest | Ruben Vigil | Completada |
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
