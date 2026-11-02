# DATA_ML — Datos reales, procesamiento y modelos predictivos

**Responsabilidad inicial:** T05–T12 asignadas a Guillermo Minero; T13–T19 asignadas a Ruben Vigil. Ambos revisan el trabajo del otro. **Estado:** el dataset y la variable objetivo definitiva aún no están seleccionados ni validados.

**Objetivo académico:** demostrar un flujo reproducible desde registros de entregas hasta predicciones evaluadas, diferenciando evidencia experimental de reglas comerciales e información simulada.

## Pregunta candidata

Estimar **duración observada de una entrega en minutos** a partir de atributos conocidos antes de realizarla. Solo procede si existe una fuente con etiquetas observadas y variables válidas. Una duración derivada de dos timestamps reales observados puede ser válida si se explica claramente su definición; una duración generada con distancia/velocidad supuesta **no es una etiqueta real**.

## Fuentes candidatas que deben evaluarse (no seleccionadas)

Estas fuentes ayudan a iniciar T05, pero **no equivalen a datos aprobados**. La información descriptiva proviene de páginas públicas y repositorios secundarios; antes de decidir es obligatorio descargar los archivos originales y comprobar su licencia, su esquema y la procedencia de sus etiquetas.

| Candidato | Acceso inicial | Campos/objetivo descritos públicamente | Riesgos que hay que comprobar |
|---|---|---|---|
| **Zomato Delivery Operations Analytics** | https://www.kaggle.com/datasets/saurabhbadole/zomato-delivery-operations-analytics-dataset | Se reportan aproximadamente 45,584 filas y 20 columnas, coordenadas de origen/destino, tipo de vehículo y `Time_taken (min)`. | Procedencia real de los tiempos, licencia de redistribución, significado exacto del intervalo temporal, valores GPS anómalos y variables que solo se conocen después del pedido. |
| **DoorDash Delivery Duration** | https://github.com/dklim-git/DoorDash-Project (copia publicada); descripción del problema: https://github.com/Sean329/DoorDash-Delivery-Duration/blob/main/%23%23%23%23%20Data%20description%20%23%23%23%23 | Registros históricos de 2015; `created_at` y `actual_delivery_time` permiten calcular la duración total desde la solicitud hasta la entrega. | La descripción indica que los datos fueron **alterados con ruido para ocultar información comercial**. No contienen necesariamente la ubicación ni el tipo de vehículo del MVP; verificar derechos sobre el conjunto original, no solo sobre el repositorio que lo comparte. |

La cifra de filas y las columnas anteriores son **referencias preliminares de terceros**, no conteos comprobados por este equipo. Tampoco se ha demostrado que Zomato contenga observaciones sin alterar. Si no se obtiene evidencia razonable de mediciones, no presentar sus etiquetas como tiempos reales verificados.

**Criterio de selección:** preferir un dataset con etiqueta documentada y observada, derechos de uso claros y atributos útiles **antes de emitir una cotización**. La semejanza con una aplicación comercial no compensa una variable objetivo inválida.

**Diferencia crítica entre targets:** Zomato usa una etiqueta denominada `Time_taken (min)` cuyo inicio y final deben verificarse en la fuente; DoorDash documenta la duración desde creación del pedido hasta entrega final. No asumir que ambas representan el mismo intervalo ni combinarlas como una sola etiqueta sin justificarlo.

**Representatividad:** incluso si los datos provienen de operaciones reales en India o EE. UU., su modelo no queda validado para El Salvador ni para bicicleta/motocicleta local. El producto deberá comunicar esta limitación y usar reglas de negocio explícitas cuando los datos no sostengan una distinción.

## Datos necesarios para cada parte del producto

| Necesidad | Fuente adecuada | Método previsto |
|---|---|---|
| Tiempo de entrega (objetivo ML) | Registros históricos con duración observada o marcas temporales reales | Regresión ML/DL, validación y MAE/RMSE. |
| Coordenadas / distancia | Campos del dataset o puntos de origen/destino de la demo | Cálculo geográfico; distancia en línea recta no equivale necesariamente a ruta vial. |
| Bicicleta y motocicleta | Si la fuente registra el vehículo, se estudia su validez; de lo contrario, parámetros explícitos | Reglas configurables y limitaciones documentadas. |
| Tarifa, pago del repartidor, combustible y margen | Parámetros comerciales documentados por el equipo | Cálculos deterministas; no son etiquetas del modelo de duración. |
| Pedidos y conversación WhatsApp simulada | Datos ficticios exclusivamente para la demostración | MongoDB y Next.js, sin mezclar con entrenamiento/evaluación. |

## Protocolo de obtención de datos — T05/T06/T07

Para cada fuente candidata comprobar y documentar:

1. Nombre/editor, URL de origen y fecha de consulta.
2. Descarga o acceso efectivo (no basta encontrar una página que menciona el dataset).
3. Licencia, términos de reutilización, privacidad y si scraping está permitido cuando aplique.
4. Cobertura geográfica/temporal y unidad de observación.
5. Volumen y tipos de columnas; ausencia de identificadores personales no necesarios.
6. Etiqueta objetivo real, fórmula solo si deriva de observaciones y evidencia.
7. Features que existen **antes de la entrega**, disponibles en la futura API.
8. Calidad inicial (nulos, duplicados, outliers, registros inválidos) y límites de representatividad.
9. Pasos reproducibles de adquisición, versión/hash y localización de archivos en el proyecto.

Resultado de T05: **informe de fuentes candidatas con verificación y recomendación argumentada**, no código de entrenamiento. Resultado de T06: dataset accesible/licenciado y preparación reproducible. Resultado de T07: aprobación o rechazo explícito del target/calidad antes de avanzar.

**Si ningún dataset sirve:** informar el bloqueo al equipo y plantear opciones verificables; no inventar registros ni cambiar la pregunta principal sin aprobación.

### Evidencia mínima de T05–T07

- **T05:** tabla comparativa de al menos dos candidatos, origen, URL, permiso/licencia observada o «no confirmado», etiqueta, features, riesgos y recomendación condicional.
- **T06:** receta ejecutable o instrucciones reproducibles de descarga **del candidato aprobado**, inventario real de archivos, número de filas/columnas medidos, hash SHA-256 y diccionario de datos. Si la licencia impide subirlo a S3, documentar cómo obtenerlo sin redistribuirlo.
- **T07:** informe de calidad con filas descartadas, faltantes y anomalías cuantificados; definición inequívoca del objetivo y unidades, listado de features válidas para predicción y decisión «aprobado / rechazado / pendiente» con justificación.

T05 puede realizarse sin cambiar la arquitectura que T01–T04 están creando. T06 no comienza sobre un candidato sin decisión del equipo.

## Organización propuesta del dataset en AWS S3

El bucket `ml-kodigo-resources` (región `us-east-1`) ya existe. Las siguientes claves son una **estructura de trabajo propuesta**, que se creará solo cuando haya archivos verificados y permiso para escribir:

```text
s3://ml-kodigo-resources/
├── datasets/<fuente-aprobada>/<version>/
│   ├── raw/<archivo-original>.csv
│   ├── processed/<archivo-limpio>.parquet
│   ├── splits/train.parquet
│   ├── splits/validation.parquet
│   ├── splits/test.parquet
│   └── manifest.json
├── models/delivery-duration/<version-modelo>/
│   ├── pipeline.joblib
│   ├── metrics.json
│   └── manifest.json
└── docs/<hito-o-evidencia>/
```

La presencia de `splits/validation` es opcional según el diseño de validación cruzada; los formatos `.csv`, `.parquet` y `.joblib` son candidatos, no requisitos cerrados. No es necesario generar tres ficheros de partición si la validación se hace de otra forma reproducible.

### Contenido mínimo de un manifiesto de datos

Documentar en un registro legible (JSON o Markdown): nombre de la fuente, enlace y editor, fecha de descarga, licencia o restricciones, versión de adquisición, SHA-256, columnas y unidades, registros antes/después de la limpieza, transformaciones aplicadas, variable objetivo y restricciones de uso. Los valores se completan **después de realizar y verificar la adquisición**, nunca con cifras de ejemplo presentadas como resultados.

### Procedimiento de almacenamiento

1. Descargar/verificar localmente y comprobar los derechos de almacenamiento y redistribución.
2. Mantener copia inalterada del origen cuando esté autorizado y no escribir encima.
3. Ejecutar limpieza reproducible, registrar código/versión y guardar el resultado en una nueva clave.
4. Proteger la división entrenamiento/prueba de filtraciones de información (no aplicar imputación/normalización ajustada con el conjunto de prueba).
5. Tras entrenar y elegir un modelo, guardar artefacto, métricas reales y manifiesto; la API utilizará esa **versión identificada**.

El código local de Pandas/Dask/PySpark puede descargar primero el objeto desde S3 a una carpeta de trabajo ignorada por Git. Se debe registrar el hash para comprobar que todos procesaron los mismos datos. No pedir a Spark local que lea credenciales AWS desde un archivo versionado.

**Seguridad:** `boto3` usará perfil AWS local o roles IAM en despliegue. No colocar `AWS_ACCESS_KEY_ID` ni secretos en el repositorio ni en el frontend. El bucket es compartido: no modificar políticas, cifrado o versionado por cuenta propia. Para T05, la investigación y evaluación preliminar no necesitan permisos de escritura.


## Procesamiento — T08 a T12

- **T08 Pandas:** pipeline reproducible de limpieza, tipado y transformación; no aplicar operaciones manuales que no puedan repetirse.
- **T09 EDA:** perfil de variable objetivo, distribuciones, faltantes, correlaciones/relaciones relevantes, gráficos y sesgos.
- **T10 Dask:** operaciones equivalentes a Pandas, con resultados validados.
- **T11 PySpark local:** operaciones/acciones equivalentes, sin cluster cloud.
- **T12 comparación:** medir tiempos sobre los mismos datos, operaciones equivalentes y entorno/hardware documentado. Repetir mediciones cuando sea razonable; distinguir rendimiento de exactitud de datos. Un CSV pequeño puede ejecutarse más rápido en Pandas que en Dask/PySpark por el coste de inicialización: reportar los resultados observados, no forzar una supuesta mejora.

Para comparar las tres herramientas, fijar una lista breve de operaciones equivalentes (lectura, selección de columnas, eliminación/filtrado de nulos, conversión de tipos, agrupación y agregación), comprobar el resultado y medirlas con el mismo equipo. Persistir versiones de datos solo cuando se haya aprobado su procedencia y uso en S3. No subir información personal cruda innecesaria.

## Entrenamiento y evaluación — T13 a T19

- **T13:** variables predictoras, pipelines de preprocesamiento, división entrenamiento/prueba sin fuga de datos (temporal si corresponde).
- **T14:** baseline ingenuo pero válido (p. ej., predictor constante usando solo entrenamiento; elegir según el problema).
- **T15:** al menos tres algoritmos de **familias distintas**; candidatos del Hito I: regresión lineal, Random Forest y SVR.
- **T16:** validación cruzada y búsqueda de hiperparámetros sin usar test para tuning; protocolo replicable.
- **T17:** MLP pequeña ajustada a las features, TensorFlow/Keras o PyTorch según entorno y justificación.
- **T18:** métricas adecuadas de regresión (MAE, RMSE) obtenidas de experimentos reales; comparar baseline, 3 ML y MLP; analizar errores.
- **T19:** seleccionar modelo con evidencia, persistir pipeline + artefacto y metadatos; no sustituir predicciones por datos ilustrativos.

Usar semillas donde proceda, versionar dependencias y parámetros, y documentar CPU/RAM/tiempos cuando sean relevantes. El resultado del experimento debe poder reconstruirse desde un dataset realmente accesible.

## Contrato de integración con API

Cuando se valide el dataset, compartir con quien implemente T30/T31:

- Campos de entrada de `/predict`, nombres/tipos/unidades/validaciones y cuáles son realmente conocidos al cotizar.
- Salida (duración en minutos si ese es el target) y significado de la predicción.
- Pipeline/artefacto serializado y versión; ubicación autorizada `s3://ml-kodigo-resources/models/…`.
- Manejo de ausencia de modelo y errores de validación.
- Métricas reales, limitaciones y dominio de uso (país, vehículo, franja horaria, etc.).

No afirmar que el modelo diferencia bicicleta/motocicleta si no está respaldado por features y etiquetas pertinentes. Las reglas de vehículo y combustible pertenecen al módulo de negocio.

## Entregables de Guillermo antes de T13

1. Informe de auditoría de fuente(s) y decisión del dataset.
2. Dataset y diccionario de datos versionados/reproducibles.
3. Scripts ETL y notebook/reportes EDA, con controles de calidad.
4. Equivalencias con Dask/PySpark local.
5. Comparación de tiempos y pruebas verificables de transformaciones.

Evitar notebooks gigantes que mezclen adquisición, lógica comercial, entrenamiento y presentación. Preferir módulos importables y notebooks solo para exploración cuando aporten valor.

## Criterios de aceptación académica y precauciones

El informe debe explicar **de dónde provienen los datos, qué se quiere predecir, por qué las variables están disponibles antes de la entrega, qué experimentos se ejecutaron y cuáles son las limitaciones**. Ningún número de exactitud, velocidad, ahorro, tarifa o rentabilidad debe rellenarse sin evidencia.

La aplicación académica puede simular un recorrido completo con pedidos ficticios y efectivo ficticio; esto no convierte los registros del simulador en datos válidos para ML. Si el modelo se entrena con datos de otra región, señalarlo en README, API y defensa. La demostración comercial no constituye una validación de desempeño para El Salvador.

### Referencias iniciales para investigación (no equivalen a licencias aprobadas)

- Dataset candidato Zomato: https://www.kaggle.com/datasets/saurabhbadole/zomato-delivery-operations-analytics-dataset
- Descripción de campos en un proyecto que reutiliza Zomato: https://github.com/Parth-Malik/Zomato-Delivery-Time-Prediction
- Archivo histórico DoorDash disponible en un repositorio educativo: https://github.com/dklim-git/DoorDash-Project
- Definición original publicada del problema DoorDash y advertencia de ruido: https://github.com/Sean329/DoorDash-Delivery-Duration/blob/main/%23%23%23%23%20Data%20description%20%23%23%23%23

Antes de usar un candidato, Guillermo debe confirmar directamente los derechos de acceso, uso y almacenamiento, además de verificar que el archivo descargado corresponde a la descripción pública.
