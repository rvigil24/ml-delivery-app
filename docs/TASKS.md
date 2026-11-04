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
- **T32–T33:** completadas por cierre autorizado con evidencia local, Atlas y S3 indicada abajo; integración verificable en el PR del bloque y la guía externa. T34 completada por cierre autorizado con evidencia abajo. T35 completada por cierre autorizado con evidencia abajo. T36 y la mejora ML con arranque v2 S3 completadas por cierre autorizado, con evidencia abajo. T37 completada por cierre autorizado, con evidencia abajo. T38 completada por cierre autorizado, con reporte Word/PDF y evidencia abajo. T39 completada por cierre autorizado, con informe y paquete de evidencias. T40 completada por cierre autorizado, con presentación y demo ensayada. T41 completada por cierre autorizado con propuesta ECS/Fargate y presupuesto breve; evidencia abajo. T42 completada por cierre autorizado con Terraform validado y plan sin apply. T43 completada por cierre autorizado con arranque local verificado. T44 integrada en PR #29 con CI aprobada. T45–T46 completadas con activación autorizada y evidencia cloud al final. Siguiente tarea: T47 (Next.js), sin iniciar en este cierre.
- **T40:** completada con material editable, PDF y guía; evidencia abajo.
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

### Cierre autorizado: T36 — flujo integrado simulado

**Responsable:** Ruben Vigil. Rama `test/T36-flujo-simulado`, creada desde
origin/main `2eca136` (T35 integrada). **Dependencias:** servicios de pedidos,
estimación/precios, asignación, WhatsApp simulado y efectivo (T20–T28).

**Criterio:** una prueba integrada de solicitud → cotización → confirmación →
asignación → recogida → entrega → cobro → entrega de efectivo, con historial
conservado y liberación del repartidor. Se prueba la composición de servicios
en memoria, sin API/cloud ni validación comercial real.

**Evidencia — 2026-11-04:**
`uv run --locked pytest backend/tests/test_delivery_flow.py -q`:
**1 passed in 0.04s**. Comprueba también el bloqueo sin cotización fixture y
sin entrega para cobrar. Reutiliza servicios y repositorios existentes;
único archivo de prueba nuevo. Predictor, cotización, tarifas, zona y carga
son fixtures explícitos, exclusivos del test; ningún validador se añade a la
API. Un primer intento detectó que el doble predictivo debía respetar el
contrato PREDICTION; se corrigió el fixture sin modificar código del producto.
No se repitió la suite completa. README/guía/ZIP actualizados; pendiente del
cierre autorizado, sin commits/push ni inicio de T37.

**Ampliación solicitada por Ruben para exponer — 2026-11-04:** se conectó el
flujo completo mediante POST /demo/deliveries, optativo con DELIVERY_DEMO_ENABLED=1.
Usa predictor entrenado y MongoDB reales; políticas, zona, carga y ubicaciones del
archivo examples/demo_delivery.json son explícitamente simuladas. scripts/demo_delivery.py
genera IDs demo- nuevos y guarda entrada/recibo en data/reports/presentation/demo_result.json.
El recibo conserva la cotización completa; MongoDB guarda el recorrido operativo.
Aceptación exclusiva de la simulación, sin cambiar validadores generales ni
pretender reanudación por pasos o una transacción global del recorrido.

**Comprobación real:** Docker build/up --wait y POST completo verificados.
Modelo meituan-temporal-rf-v1 produjo 32.57790982477246 minutos para el calendario
del pedido demo; no es duración observada ni validación local. Tarifa simulada
3.22 USD, pedido entregado, seis eventos logísticos y tres de efectivo hasta
entregado_al_operador; importe conciliado y repartidor liberado. GET del pedido
persistido confirmado. Se corrigió la presentación CLI del estado de efectivo
(derivado del último evento); dos recorridos de demo permanecen en MongoDB local.
Sin suite adicional. Contenedores delivery-local e información conservados para
la presentación; no se modificó Atlas/S3. Contrato, README, guía y ZIP actualizados.


### Cierre autorizado: corrección ML y conexión T36 — 2026-11-04

Responsable Ruben Vigil. Rama activa `ml/eta-riesgo-presentacion`, desde el HEAD
main 2eca136; se conservó el trabajo no publicado de T36. Se revisa T13–T19 por
solicitud expresa: el modelo temporal era insuficiente. Los estados históricos
no se reescriben ni se declara cierre de esta ampliación automáticamente.

Informe oficial Meituan 2024, sección 2.1, y artículo 2025, sección 3.1, resuelven
la duda de preservación de distancias relativas. Divisor 1e6 registrado como
inferencia de codificación, sin atribuir confirmación textual al editor.
Protocolo fijado antes de entrenar: misma cohorte/frontera, tres folds temporales,
ETA seleccionada por MAE CV, riesgo por log-loss CV; test ya observado y revisión
exploratoria. Bundle nuevo v2 con dos predictores, sin sobrescribir v1.

Evidencia: ETA test MAE 7.369698, RMSE 9.878996, R² 0.358061; error MAE ~19.2%
menor que v1. Riesgo ROC AUC 0.647745, Brier 0.122650 y log-loss 0.403900 frente
a 0.422204 de referencia. Clasificación útil pero modesta; sin validación local.
Endpoint POST /predict/delivery y demo T36 usan el bundle real. Escenarios HTTP
con la misma fecha: 1.11 km/plazo 30 → ETA 23.10, riesgo 17.67%; 5.56 km/plazo 30 →
ETA 45.38, riesgo 70.60%; mismo recorrido/plazo 45 → riesgo 32.89%. Son inferencias
sobre entradas ilustrativas, no viajes observados. Recibo demo v2 confirma pedido
entregado y efectivo entregado_al_operador en MongoDB local.

Una prueba nueva de variables y una existente de OpenAPI aprobadas; sin otras
suites. Notebook 03, informe, guía y ZIP actualizados. API local conservada para
exponer. V2 se publicó después en S3; la adaptación de arranque remoto se
documenta abajo. Sin recursos cloud nuevos o cierre formal de esta ampliación.

### Adaptación T33: arranque v2 desde S3 — autorizada por Ruben

Responsable Ruben Vigil; misma rama de mejora ML. La implementación T33
original cargaba v1; al incorporar dos pesos v2 faltaba adaptar el arranque.
Se implementa descarga de manifiesto v2 fijado por SHA256/tamaño, esquema y
lista exacta, verificación de versión/hashes/entorno y carga única en memoria.
Caché/cliente cerrados, limpieza al apagar o fallar, 503 sin fallback.

Configuración v2 en .env.example y .env privado sin mostrar credenciales;
compose.s3.yaml permite verificarlo con perfil local montado en lectura. Para
AWS, perfil vacío y rol IAM a configurar en T45/T43; no se crean permisos,
recursos o despliegues. Respuesta model_source permite distinguir s3/local.
No se modifica el estado histórico/formal de T33 por esta ampliación.

Evidencia real: API sin directorio v2 descargó siete archivos desde S3 al
iniciar, atendió dos inferencias sin nuevas descargas y eliminó caché al cerrar.
Hash de manifiesto incorrecto produjo 503 y limpieza; cliente S3 cerrado en
ambos casos. La prueba existente de arranque v1 pasó (1 passed). Build/Compose
S3 y recorrido completo en Docker verificados: model_source=s3, pedido entregado
y efectivo entregado_al_operador. Evidencia local v2_s3_api_startup.json y
v2_s3_docker_demo.json; demo/recibos conservados para exponer. Sin suites completas,
reentrenamiento, IAM o despliegue AWS. Guía y ZIP actualizados; sin commit/push.


### Cierre del bloque ML/T36 y adaptación T33 — 2026-11-04

Ruben autorizó el cierre tras completar la demo real y la carga S3. T36 queda
Completada en el backlog local; T13–T19/T33 conservan sus cierres históricos y
esta ampliación se integra con un único PR. El commit publicado 6a5a074 se
conserva y se añade el cambio de arranque S3. Se verifica inclusión de ambos
commits en origin/main y se registra el resultado efectivo en la guía externa.

Se contrastaron recibos de arranque S3 y Docker/demo con estados finales,
24 objetos privados publicados y hashes del bundle v2. Se reutilizan las
pruebas/entrenamiento ya acreditados: flujo unitario, variables v2, OpenAPI,
arranque v1 y comprobaciones reales HTTP/S3. No se repiten suites ni ML sin
cambios de ejecución. Límites conservados: test reutilizado, coordenadas con
codificación inferida, riesgo modesto y falta de validación local; aceptación
y tarifas de demo explícitamente simuladas, sin rollback global del recorrido.
Sin modificar Excel, borrar ramas, desplegar AWS o iniciar T37 en este cierre.

### Cierre autorizado: T37 — README de instalación, ejecución y ejemplos

Responsable: Ruben Vigil. Rama docs/T37-readme desde origin/main 9ac9a65.
Dependencias: API/modelos v2, persistencia T32, S3 T33 y demo Docker T34/T36.
Criterio: instrucciones actuales de instalación/configuración, ejecución demo,
consulta HTTP, parada/persistencia y errores; datos simulados diferenciados de
resultados reales y enlaces a reproducción técnica. Conservar recetas previas.

El README prioriza el arranque S3 con configuración explícita, perfil en lectura,
modelo v2 y recibo de demo; incluye alternativas local/nativa y explicación del
health v1. El historial original se conserva en una sección desplegable. No se
cambian código, interfaces o dependencias. El estado local de T37 se actualiza
como parte del cierre autorizado por Ruben, sin modificar Excel.

Evidencia T37: Compose S3 valida con config --quiet; script de demo acepta los
argumentos documentados (--help); enlaces locales existentes e historial README
anterior íntegro comprobados. El ejemplo curl equivale a una petición real que
respondió 200 con meituan-eta-risk-v2 y model_source=s3. Diff sin errores. No se
clonó/instaló un entorno nuevo, recrearon contenedores o añadieron datos demo;
no se ejecutaron suites ni entrenamientos. Cierre autorizado: T37 completada,
commit/push y PR único con integración normal verificada en origin/main. La guía
externa registra el resultado efectivo; ZIP actualizado, sin iniciar T38.


### Cierre autorizado: T38 — reporte y documentación técnica

Responsable Ruben Vigil. Rama docs/T38-documentacion desde origin/main 4d4c268.
Dependencias: datos/experimentos, inferencia v2, S3, persistencia, demo y README.
Criterio: arquitectura y contratos actuales, metodología y resultados reales,
límites de interpretación y reproducción claramente documentados. Por solicitud
explícita de Ruben, incluye reporte humano en Word y PDF. No se inician otras
tareas de presentación/despliegue ni se repiten entrenamientos.

Se actualizan ARCHITECTURE y DATA_ML con síntesis actual y comparación basada en
evidence.json; se retiran instrucciones de coordinación y asignaciones antiguas
de esos apartados técnicos. Se conservan contratos y recetas experimentales.
No se modifican código, pesos, métricas o dependencias. T38 se registra como
Completada por cierre autorizado; T39 conserva su estado pendiente.

Evidencia: tablas completas cotejadas con evidence.json y hashes del bundle;
546,281 pedidos conciliados entre particiones; enlaces locales válidos y rutas
actuales presentes en OpenAPI. Diff sin errores. Se aclara que el campo pr_auc
es average precision (AP), no un área trapezoidal o porcentaje de exactitud.
Sin suites, inferencias nuevas, entrenamiento o escrituras cloud/demo. Por
corrección explícita de Ruben, el entregable humano es ahora un reporte de ocho
páginas en reports/Reporte_Tecnico_Asistente_Delivery.docx y .pdf, con portada,
diagrama, tablas, gráficas, metodología, evidencia y referencias. Markdown queda
como apoyo técnico. PDF renderizado y páginas de arquitectura/resultados revisadas
visualmente; XML e imágenes Word, paginación y cifras cotejados. README enlaza
ambos documentos. Cierre autorizado por Ruben: commit/push y un PR con integración
normal, verificando el commit en origin/main. La guía externa registra el resultado
efectivo y el ZIP se actualiza. Sin modificar Excel o iniciar/cerrar T39.


### Cierre autorizado: T39 — informe y evidencias de los hitos

Responsable Ruben Vigil. Rama docs/T39-evidencias desde origin/main 3f6f705.
Dependencias: informe/documentación T38 y registros reales de procesamiento,
ML/MLP, pruebas e integración. Se reutiliza el reporte técnico de ocho páginas.
Criterio: entregar informe y evidencias legibles, trazables y agrupadas para
revisión académica, sin inventar resultados o exponer datos/secretos.

Anexo de cuatro páginas Word/PDF: calidad/equivalencia, tiempos locales,
comparación temporal y curva MLP, integración/registro unitario previo. Paquete
reports/Entrega_Asistente_Delivery.zip con reporte/anexo editables, gráficas,
notebooks fuente sin outputs, evidencia agregada, licencia y manifiesto SHA-256.
No incluye CSV, pesos, credenciales o registros reales. README enlaza entregables.

Evidencia: cifras contra JSON conservados, Word/XML y cuatro páginas PDF,
render visual de procesamiento/MLP sin recortes; ZIP con 17 archivos y hashes
verificados. Las 14 pruebas unitarias se citan mediante PR #19; no se simula
un log nuevo o se afirma haberlas reejecutado. Sin suites, entrenamiento,
mediciones nuevas, dependencias, cloud o cambios de código del producto.
Cierre autorizado por Ruben: T39 Completada en backlog local, commit/push y
un PR con merge normal y verificación del commit en origin/main. Guía y ZIP
de fuentes actualizados. Sin modificar Excel, borrar ramas o iniciar T40.

### Cierre autorizado: T40 — presentación y demostración de defensa

Responsable Ruben Vigil. Rama docs/T40-presentacion desde origin/main 17ad73d.
Dependencias: reporte y evidencias, modelos y demo integrada. Criterio: material
proyectable/editable, guion y secuencia reproducible de demostración con límites
claros y sin resultados inventados.

Presentacion_Defensa.pptx: 12 diapositivas editables con 12 notas; PDF exportado
desde el PPTX real para comprobar compatibilidad. Guia_Exposicion_y_Demo.docx/pdf:
cuatro páginas de guion, comandos, preguntas y respaldo ante fallos. ZIP de
entrega actualizado a 23 archivos con presentación/guía y registro real del ensayo.

Verificaciones: XML PPTX/Word, páginas, cifras y render visual. Se corrigió una
conversión de colores en las formas nativas y se revisó de nuevo el PPTX/PDF.
Un ensayo del simulador completó entrega/efectivo y liberó repartidor con
model_source=s3; no se reentrenó ni se repitieron suites. Los escenarios guardados
se identifican como ilustrativos y los resultados previos no se simulan en vivo.
Hash/tamaños/CRC del ZIP comprobados, sin CSV, pesos o credenciales. README enlaza
material. Cierre autorizado por Ruben: T40 Completada en backlog local,
commit/push y PR con merge normal verificado en origin/main. Guía y ZIP de
fuentes actualizados. Sin modificar Excel, borrar ramas o iniciar despliegue.

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
| T36 | Pruebas, documentación y entrega | Probar el flujo completo: solicitud → cotización → asignación → entrega → efectivo | Ruben Vigil | Completada |
| T37 | Pruebas, documentación y entrega | Preparar README con instalación, ejecución y ejemplos | Ruben Vigil | Completada |
| T38 | Pruebas, documentación y entrega | Documentar arquitectura, resultados, experimentos y limitaciones | Ruben Vigil | Completada |
| T39 | Pruebas, documentación y entrega | Preparar informe técnico y evidencias de los hitos | Ruben Vigil | Completada |
| T40 | Pruebas, documentación y entrega | Preparar presentación y demostración para la defensa | Ruben Vigil | Completada |
| T41 | Despliegue y CI/CD | Definir arquitectura de despliegue en AWS y revisar presupuesto estimado | Ruben Vigil | Completada |
| T42 | Despliegue y CI/CD | Implementar infraestructura como código con Terraform (ECS/Fargate, ECR, red, IAM y S3 existente) | Ruben Vigil | Completada |
| T43 | Despliegue y CI/CD | Configurar servicio ECS/Fargate y variables para despliegue; conservar Compose local | Ruben Vigil | Completada |
| T44 | Despliegue y CI/CD | Crear pipeline CI/CD en GitHub Actions para pruebas, build y despliegue | Ruben Vigil | Completada |
| T45 | Despliegue y CI/CD | Configurar secretos, permisos mínimos y acceso seguro a la infraestructura | Ruben Vigil | Completada |
| T46 | Despliegue y CI/CD | Validar despliegue, logs, persistencia y consumo de recursos | Ruben Vigil | Completada |
| T47 | Frontend y simulación visual | Crear aplicación Next.js con navegación entre las vistas de la demo | Ruben Vigil | Completada |
| T48 | Frontend y simulación visual | Implementar chat estilo WhatsApp para que el cliente simule un pedido | Ruben Vigil | Completada |
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

## T41 — arquitectura AWS y presupuesto breve

Responsable: Ruben Vigil. Rama `docs/T41-arquitectura-aws`, desde `origin/main`
`95c9f74`. Dependencias: API, persistencia Atlas, bundle S3 y contenedor ya
implementados (T19, T30–T34 y mejora v2). Criterio: documentar topología,
servicios, límites y una estimación breve antes de implementar infraestructura.

Decisión explícita de Ruben: descartar EC2 y elegir ECS con Fargate. Se ajusta
el alcance futuro de T42–T43 a esta decisión sin cambiar responsables o estados.
Propuesta Word/PDF de dos páginas con diagrama, ECR, tarea de inferencia, Atlas,
S3 y roles. Demo inicial con IP pública variable y acceso restringido; actualizar
lista Atlas /32 al reemplazar tarea. Sin ALB/NAT, TLS o endpoint estable en esta
base; no se afirma alta disponibilidad. Presupuesto orientativo con referencias
oficiales, sin extender el análisis de precios por solicitud del usuario.

Comprobaciones: generación Word/PDF, estructura OOXML, dos páginas y revisión
del texto/diagrama. Sin nuevos tests de producto, entrenamiento o recursos cloud.
T41 completada por autorización explícita de cierre el 2026-11-04. Word/PDF de dos páginas, XML y contenido verificados; git diff --check sin errores. Publicación e integración verificables en el PR y guía externa. Sin apply o recursos cloud.

## T42 — Terraform ECS/Fargate

Responsable: Ruben Vigil. Inicio autorizado tras cerrar T41 en PR #26.
Rama `infra/T42-ecs-fargate` desde `origin/main` `68605c0` actualizado.
Dependencias satisfechas: diseño T41 y contenedor/API/Atlas/S3 existentes.
Criterio: infraestructura declarada, formateada, validada y plan revisable, sin
apply, secretos en estado o cambios al bucket existente.

Archivos: `infra/terraform/` con red pública, ECR, ECS/Fargate, roles separados,
logs y contenedor de secreto sin valor; data S3 existente. Servicio con cero
tareas obligatorio durante esta preparación. No EC2, bucket administrado,
ALB, NAT o publicación de imagen. Variables de ejemplo explícitamente ficticias.

Comprobación real: Terraform 1.13.5 temporal con checksum oficial y proveedor
AWS 6.71.0 firmado, lock versionado. Init, fmt, validate y plan real con perfil
remote-admin, quitando endpoints/credenciales de emulador del entorno del proceso.
Plan con ejemplo TEST-NET /32 y etiqueta aún no publicada: 16 creaciones,
0 cambios, 0 destrucciones. Es un plan orientativo, no uno listo para aplicar.
No se leyó el valor de la URI Atlas ni se ejecutó apply. Plan/texto/evidencia
quedan ignorados en data/reports/presentation/terraform/.

Pendiente de T43: publicar imagen, cargar secreto y resolver espera de Atlas
antes de iniciar Uvicorn dentro de la misma tarea. La API valida Mongo una sola
vez al iniciar; permitir el /32 después no la recupera, y reemplazar una tarea
cambia su IP. No habilitar tareas hasta resolverlo. T42 completada por cierre explícitamente autorizado. Integración verificable
en el PR y guía externa. No se ejecutó apply.

## T43 — arranque y configuración Fargate

Responsable: Ruben Vigil. Inicio explícitamente autorizado tras cerrar T42.
Rama `infra/T43-arranque-fargate` desde `origin/main` `1a522be` actualizado.
Dependencias: T41–T42 y contenedor existente. Criterio: definición de tarea y
variables cloud coherentes, espera de Atlas antes de Uvicorn y procedimiento
reproducible, sin secretos versionados o despliegue implícito.

Se implementa `delivery.cloud_start`: espera esquema/conectividad con clientes
cerrados por intento y plazo configurable; luego exec de Uvicorn sin reemplazar
la tarea. Healthcheck de vitalidad PID/plazo durante espera, HTTP después:
HEALTHY no acredita disponibilidad funcional. Terraform usa el comando, permite
cero/una tarea y conserva cero por defecto. Compose/Dockerfile no cambian.

T43 no crea ECR/IAM/secretos ni publica imagen; esos pasos requieren autorización
de infraestructura/despliegue. Se documentan consulta de IPv4 y alta /32 Atlas,
sin acceso global ni permisos administrativos Atlas dentro de la aplicación.
Completada por cierre autorizado; evidencia final abajo.

Comprobaciones T43: `uv run --locked pytest backend/tests/test_cloud_start.py -q`:
2 aprobadas (0.12 s), reintento/exec/cierre de clientes y timeout sin fuga de URI.
Docker build de `ml-delivery-api:t43-check` aprobado. Un contenedor temporal
sin Mongo permaneció vivo; al conectar la red del Mongo local verificó esquema
y arrancó HTTP sin cambiar contenedor ni PID. Red/contenedor de comprobación
eliminados; API local existente conservada. Solo lecturas Mongo, sin Atlas real,
modelos, puertos publicados o nuevas escrituras de datos.

Terraform fmt/validate aprobados y plan real actualizado con entradas de ejemplo:
16 creaciones, cero cambios/destrucciones, `desired_count = 0`; sin apply.
Evidencia ignorada: `cloud_start_local.json`, `t43_plan.txt`, `t43.tfplan` y
`t43_verification.json` en data/reports/presentation/terraform/. Propuesta Word/PDF,
README, arquitectura, guía externa y ZIP actualizados. No se repiten suites,
entrenamientos o publicación S3. Sin commit/push de T43.

**Autorización persistente de Ruben — 2026-11-04:** integrar cada tarea siguiente
con commit, push y merge normal, y continuar sin repetir confirmación. Se mantienen
ramas desde origin/main actualizado, comprobaciones y evidencia por tarea. No
incluye crear recursos, configurar IAM real, desplegar o generar gastos AWS.

## T44 — GitHub Actions

Responsable: Ruben Vigil. Continuidad e integración autorizadas expresamente.
Rama `ci/T44-pipeline` desde origin/main `e3eb65c` actualizado tras PR #28.
Dependencias: T34 y T41–T43 satisfechas para definir/build/verificar pipeline.
OIDC/IAM real, infraestructura y secreto siguen pendientes antes de ejecutar CD.
Criterio: CI reproducible para PR/main y workflow de entrega manual documentado,
sin despliegue implícito. No convertir la ausencia de prueba cloud en evidencia.

Se crean ci.yml (dominio/arranque, Terraform estático y build Docker) y deploy.yml
(manual main + DESPLEGAR + CI aprobada, OIDC, ECR SHA, actualización ECS y salida
IPv4 Atlas). CI no necesita AWS o dataset. CD no crea infraestructura, modifica
IAM, escribe secretos o ejecuta apply. Se documenta vitalidad vs readiness,
preparación de entorno/rol y sincronización de variables Terraform tras CD.
Acciones verificadas en sus repositorios oficiales y fijadas por SHA.

Comprobaciones locales T44: actionlint 1.7.12 temporal con SHA256 verificado,
YAML, bash -n de scripts, eventos/permisos y SHA de acciones correctos. Export
UV bloqueado con poda offline aprobado. Propuesta sigue en dos páginas.
Cierre por autorización persistente; fusionar únicamente con tests/Terraform/
build aprobados en GitHub y registrar evidencia real en PR/guía. El workflow
CD no se ejecuta; su validación AWS depende de infraestructura/autorización.
No se ejecutan pruebas locales duplicadas de producto o entrenamiento.

## Bloque activo — T45: seguridad, OIDC y secreto Atlas

Responsable: Ruben Vigil. Rama infra/T45-seguridad-oidc desde origin/main cb58aea.
Dependencias: T41–T44 integradas; CI PR/main aprobada (16 pruebas, Terraform, Docker).
Criterio: confianza OIDC y permisos mínimos definidos/activados, secreto fuera de
Git/estado, entorno protegido y acceso real comprobado. **Pendiente**: sin permiso
para configurar IAM real, crear infraestructura o cargar el secreto no se cierra
T45 ni se avanza a su dependiente T46.

Preparación: github_oidc.tf + restricciones SourceAccount/Arn de roles ECS y salidas
no secretas. Sub inmutable exacto confirmado por API GitHub, aud sts.amazonaws.com.
Inventario IAM de solo lectura: ningún proveedor OIDC existente. Rol de entrega
limitado a ECR de demo, familia ECS, servicio, tareas/red y PassRole de dos roles;
sin URI Atlas, escritura S3 o administración IAM. GitHub aws-demo configurado y
verificado: solo rama main y revisión de rvigil24, permite aprobación propia.

Terraform fmt/validate y plan reales aprobados: 19 altas, cero cambios/bajas,
cero tareas. Variables reales no secretas en deployment.tfvars privado (/32
observado y tag SHA base); plan y recibos ignorados en data/reports/presentation/
terraform/t45*. No se leyó/escribió la URI ni se ejecutó apply. El valor Atlas no
se declara en Terraform. Código preparado se puede integrar bajo autorización
persistente manteniendo la tarea Pendiente; activación/prueba AWS requieren orden
explícita. No se afirman permisos efectivos o despliegue funcional sin esa prueba.

### Activación T45 autorizada — 2026-11-04

Ruben aprobó explícitamente aplicar el plan, cargar URI desde .env, configurar
variables GitHub y desplegar una tarea. Apply real: 19 altas, cero cambios/bajas,
secreto cargado fuera de Terraform/GitHub, variables no secretas configuradas.
Workflow https://github.com/rvigil24/ml-delivery-app/actions/runs/41888010231:
OIDC/ECR aprobados; primer intento falló por DescribeTaskDefinition Resource '*'.
Corrección de lectura regional aplicada mediante plan de una actualización IAM,
cero altas/bajas. Reintento registró :2 y actualizó servicio a una tarea.

Se define ownership de revisión ECS por pipeline (ignore_changes), sincroniza
cantidad en tfvars privado y verifica plan sin cambios. Contenedor vivo y secreto
inyectado; espera Atlas. Requiere permitir 18.214.26.83/32 en Atlas (paso solicitado
al usuario, sin API administrativa disponible). T45 sigue Pendiente hasta validar
acceso/secretos; T46 no se declara terminada ni se afirma inferencia/persistencia
cloud. Corrección de código/documentos se integra bajo autorización persistente.
Evidencia en data/reports/presentation/terraform/; sin suites locales nuevas.

### Corrección de espera manual Atlas

Ruben permitió la /32 anterior, pero el plazo de 900 s ya había vencido y ECS
reemplazó la tarea (nueva IP 44.203.218.6). Se habilita 0 como espera sin límite
para conservar la tarea durante el paso humano; no implica IP fija si hay otra
caída o despliegue. Dos pruebas puntuales aprobadas (0.11 s), cubriendo espera
sin límite/reintento/exec y cancelación limitada sin imprimir URI. Terraform
prepara la configuración y el pipeline usa última revisión de familia + imagen
nueva. Sin ampliar Atlas a 0.0.0.0/0, agregar NAT/EC2 o crear nuevos servidores.
T45 sigue Pendiente hasta la comprobación real de acceso.

Despliegue de espera 0: run 41892559213 publicó imagen main 17d4a75 y actualizó
servicio a revisión :5. La tarea arrancó con IP 3.231.221.94 y timeout 0 comprobado;
el run falló al buscar la IP con margen previo de 60 s. Se amplía a 180 s para
futuras entregas sin redesplegar esta tarea. Nuevo /32 solicitado al usuario.
El fallo del indicador no se oculta como run verde: validación de HTTP/modelos/
persistencia sigue pendiente. No se reintenta el job para evitar otra rotación.

## Cierre autorizado — T45–T46: AWS verificado

Responsable: Ruben Vigil. Rama docs/T45-T46-despliegue-verificado desde origin/main
a88633c actualizado. Autorizaciones persistentes de integración y explícita AWS.
T45 completada: proveedor/roles reales, OIDC efectivo, secreto fuera de Git/estado,
entorno main/aprobación, URI inyectada y acceso Atlas confirmado tras /32 del usuario.
T46 completada: HTTP health y predicción v2 200 con model_source=s3; creación y
consulta de negocio SIMULADO por HTTP, lectura independiente Atlas y borrado de
fixture verificados. Logs de arranque/predicción y series CPU/memoria CloudWatch
reales comprobados; no se afirma capacidad bajo carga. Revisión activa :5, imagen
17d4a75 y tarea 69922685c0654ffc8117f8620856c646 en 3.231.221.94, espera 0.

Recibos ignorados cloud_functional_smoke.json y cloud_runtime_verification.json.
Sin entrenamientos, nuevas métricas ML, pruebas masivas o viajes/cobros reales.
La demo automática de efectivo queda local; no se afirma ese flujo cloud.
El run 41892559213 falló por margen de búsqueda de IP; tarea arrancó después y
se comprobó manualmente. Margen de 180 s preparado para la próxima entrega;
no se cambia ese fallo a verde ni se redespliega para un cambio documental.
Estado completado bajo autorización de cierre con evidencia funcional real.
Next.js T47 sigue pendiente; no se amplía el bloque a frontend por iniciativa propia.

## Ajuste explícito solicitado — presentación y datos simulados

Ruben solicitó cambiar «Datos chinos» en la respuesta y disponer de datos para
exposición. Rama feat/ejemplos-exposicion desde origin/main actualizado. No inicia
T47 ni cambia responsables. Servicio transforma solo ese texto en respuesta;
metadata/pesos/hashes y procedencia documentada permanecen. Tres ejemplos Swagger
válidos con plazos 30/45/60; se evita usar como muestra principal el plazo 1 fuera
del rango real registrado (mínimo 30).

Fixture JSON y script de carga por HTTP: 3 negocios, 2 repartidores y 3 pedidos
SIMULADOS ya creados en AWS/Atlas, confirmada repetición sin duplicados o cambios.
Pedidos solicitados, sin cotizar/asignar/cobrar; datos excluidos de entrenamiento.
Verificados OpenAPI (3 ejemplos), validación de entradas y conservación de valores
numéricos mediante predictor controlado, sin suites adicionales locales. Integración
y despliegue de la nueva imagen bajo autorizaciones persistentes; Atlas requiere
actualizar /32 al reemplazar tarea. El script no sobrescribe datos existentes.

Verificación posterior de la solicitud de exposición: Ruben permitió
100.54.11.78/32; Swagger HTTP con 3 ejemplos y predicción source S3 con frase
nueva comprobados. GET de catálogos/pedidos confirma 3 negocios, 2 repartidores y
3 pedidos SIMULADOS. Recibo privado presentation_verified.json. URL de README
actualizada; cierre por autorización persistente, sin redespliegue documental.
T47 sigue pendiente. No se modificaron datasets, pesos o responsables.

## Actualización explícita de reportes — sin iniciar T47

Ruben solicitó actualizar todo el material necesario tras revisar desajustes.
Rama docs/reportes-actualizados desde origin/main actualizado. Se actualizan
reporte técnico Word/PDF (8 páginas), AWS Word/PDF (2), guía Word/PDF (4),
presentación PPTX/PDF (12 diapositivas + 12 notas) y ZIP (29 archivos).
AWS/IP/imagen actuales, roles IAM presentes, ejemplos Swagger y fixtures 3/2/3;
se separan predicción/CRUD cloud del flujo completo de efectivo local.
Se conserva el anexo científico byte por byte y las métricas existentes.

Comprobaciones: conteo de páginas/diapositivas/notas, XML Office y CRC/hashes ZIP,
referencias obsoletas eliminadas y revisión visual de páginas/diapositivas
modificadas. PPTX mantiene formas/textos editables y colores corregidos.
ZIP incorpora JSON de fixtures, cargador y evidencia de exposición sin secretos
ni registros de entrenamiento. Guía externa actualizada; sin cambios runtime,
redespliegue, AWS o IP. Publicación por autorización persistente, con CI normal.

## Solicitud explícita — arquitectura PNG para exposición

Rama docs/arquitectura-png desde origin/main actualizado. PNG 3840×2160 (16:9)
y SVG editable en reports/: código/CI/entrega/ECR, Fargate/FastAPI, dos modelos,
S3 al arrancar, Atlas externo, Secrets Manager, CloudWatch, roles/red/Terraform
y preparación offline. Next.js marcado pendiente; sin inventar ALB/NAT/EC2 o
funciones futuras. Diseño vectorial revisado visualmente, dimensiones/XML y
paquete verificados. ZIP suma las dos imágenes; guía personal actualizada.
No se modifica backend, AWS, IP, métricas o responsables. Publicación autorizada.

Ajuste visual solicitado por Ruben: se reemplaza la primera composición por una
vista técnica de infraestructura con iconos oficiales AWS, región/VPC/subred/SG
anidados y conectores ortogonales. Activos embebidos en SVG para uso offline;
atribución AWS incluida. Se corrigen puertos de conexión para no cruzar etiquetas.
No se añaden servicios inexistentes ni se modifica infraestructura. PNG 4K y
SVG sustituidos en el mismo PR/paquete, con nueva revisión visual y hashes.


## Solicitud explícita — lenguaje y rutas de Swagger

Se retira POST /predict; se conserva POST /predict/delivery con los mismos
modelos y resultados numéricos. Swagger agrupa las operaciones por función, con
títulos y descripciones breves en español. Los DTO HTTP usan experimental en
lugar de academic_only; se mantienen las limitaciones y validaciones existentes.
Health informa la carga de los modelos v2. Sin cambios de responsables ni de
alcance de T47. Verificación: contrato OpenAPI, ruta retirada 404 y pruebas
focalizadas de API, arranque S3 y cotizaciones.


## Bloque cerrado — T47: layout Next.js

Responsable: Ruben Vigil. Rama feat/T47-layout-nextjs desde origin/main actualizado.
Alcance confirmado: Operaciones al entrar, menú para Cliente/Negocio/Repartidor,
chat similar a WhatsApp identificado como simulación y futuro flujo guiado sin LLM.
Dependencias: alcance de las cuatro vistas en SPEC y backend T30–T46 disponible;
esta base visual no depende de conectividad cloud. Criterio de aceptación T47:
aplicación Next.js ejecutable y navegación entre las cuatro vistas en móvil y
escritorio. Sin iniciar acciones de T48–T54 por este bloque.

Implementación: App Router, TypeScript, CSS compartido e iconos SVG de trazo
consistente; fixtures de exposición reutilizados sin copiar datasets o secretos.
Estados operativos «Sin consultar», mensajes de muestra y envío deshabilitado.
Comprobaciones locales: tipos y build de producción aprobados; cuatro rutas
navegables a 1440 y 390 px sin desborde del documento ni errores JavaScript;
404 correcto. Detector Impeccable sin hallazgos. Revisión visual independiente: disposition ship, ocho capturas válidas y sin
correcciones materiales para T47. Tokens documentados con Impeccable; publicación
bajo autorización persistente de Ruben, condicionada a CI aprobada.
T48–T54 permanecen pendientes; no se despliega la interfaz en AWS.


## Bloque activo — T48: dirección, cercanía y menú de comida

Responsable: Ruben Vigil. Rama feat/T48-chat-guiado desde origin/main actualizado.
Dependencias: T47 y contratos T20/T27/T32. Ruben corrigió explícitamente el flujo:
primero dirección/ubicación, después negocios por cercanía y un menú de productos
para elegir con cantidades. También solicitó las capacidades faltantes en la API.

Se añaden GET /businesses/nearby y GET /businesses/{id}/menu y el proxy Next.js
para consumirlos. Menús de sólo lectura con nueve productos de ejemplo, ligados
a negocios existentes, sin precios inventados ni disponibilidad real declarada.
No hay LLM, proveedor de geocodificación, radio de servicio o nueva colección
MongoDB. Las distancias usan el punto elegido, no se deducen del texto de dirección.

Aceptación: dirección → negocios ordenados desde API → menú desde API → carrito
con cantidades → revisión/corrección → confirmación local explícitamente simulada.
La confirmación no registra/envía pedidos ni calcula totales. Escrituras y demás
integración quedan en T52 y sincronización en T53; T49–T51 no se adelantan.

Comprobaciones locales: siete pruebas backend focalizadas, tres pruebas de
borrador/carrito y build aprobados. Recorrido real de navegador a 1440/390 px
consultando la API local y MongoDB: dirección primero, tres negocios, tres
productos del comedor, cantidades, revisión, corrección y confirmación local.
Sin errores JS ni desborde. Revisión visual final: ship, seis capturas válidas
sin correcciones materiales. Wheel verificado con el menú JSON incluido.
El PR único incorpora todas las correcciones solicitadas por Ruben; cierre
autorizado persistente condicionado a CI aprobada. Sin despliegue AWS.
