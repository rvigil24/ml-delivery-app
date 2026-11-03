# DATA_ML — Datos reales, procesamiento y modelos predictivos

**Responsabilidad actual:** Ruben Vigil asume T05–T19 por instrucción explícita del 2026-11-03. **Estado:** investigación T05 realizada; dataset y variable objetivo definitiva pendientes de selección y validación. Las entregas anteriores de T05–T12 quedan descartadas como base de esta investigación.

**Objetivo académico:** demostrar un flujo reproducible desde registros de entregas hasta predicciones evaluadas, diferenciando evidencia experimental de reglas comerciales e información simulada.

## Pregunta candidata

Estimar **duración observada de una entrega en minutos** a partir de atributos conocidos antes de realizarla. Solo procede si existe una fuente con etiquetas observadas y variables válidas. Una duración derivada de dos timestamps reales observados puede ser válida si se explica claramente su definición; una duración generada con distancia/velocidad supuesta **no es una etiqueta real**.

## Fuentes candidatas que deben evaluarse (no seleccionadas)

Estas fuentes ayudan a iniciar T05, pero **no equivalen a datos aprobados**. La información descriptiva proviene de páginas públicas y repositorios secundarios; antes de decidir es obligatorio descargar los archivos originales y comprobar su licencia, su esquema y la procedencia de sus etiquetas.

| Candidato | Acceso inicial | Campos/objetivo descritos públicamente | Riesgos que hay que comprobar |
|---|---|---|---|
| **Zomato Delivery Operations Analytics** | https://www.kaggle.com/datasets/saurabhbadole/zomato-delivery-operations-analytics-dataset | Se reportan aproximadamente 45,584 filas y 20 columnas, coordenadas de origen/destino, tipo de vehículo y `Time_taken (min)`. | Procedencia real de los tiempos, licencia de redistribución, significado exacto del intervalo temporal, valores GPS anómalos y variables que solo se conocen después del pedido. |
| **DoorDash Delivery Duration** | https://github.com/dklim-git/DoorDash-Project (copia publicada); descripción del problema: https://github.com/Sean329/DoorDash-Delivery-Duration/blob/main/%23%23%23%23%20Data%20description%20%23%23%23%23 | Registros históricos de 2015; `created_at` y `actual_delivery_time` permiten calcular la duración total desde la solicitud hasta la entrega. | La descripción indica que los datos fueron **alterados con ruido para ocultar información comercial**. No contienen necesariamente la ubicación ni el tipo de vehículo del MVP; verificar derechos sobre el conjunto original, no solo sobre el repositorio que lo comparte. |

La tabla anterior conserva las referencias iniciales. Los conteos y accesos comprobados independientemente en T05 se registran a continuación. No se ha demostrado que Zomato contenga observaciones sin alterar. Si no se obtiene evidencia razonable de mediciones, no presentar sus etiquetas como tiempos reales verificados.

**Criterio de selección:** preferir un dataset con etiqueta documentada y observada, derechos de uso claros y atributos útiles **antes de emitir una cotización**. La semejanza con una aplicación comercial no compensa una variable objetivo inválida.

**Diferencia crítica entre targets:** Zomato usa una etiqueta denominada `Time_taken (min)` cuyo inicio y final deben verificarse en la fuente; DoorDash documenta la duración desde creación del pedido hasta entrega final. No asumir que ambas representan el mismo intervalo ni combinarlas como una sola etiqueta sin justificarlo.

**Representatividad:** incluso si los datos provienen de operaciones reales en India o EE. UU., su modelo no queda validado para El Salvador ni para bicicleta/motocicleta local. El producto deberá comunicar esta limitación y usar reglas de negocio explícitas cuando los datos no sostengan una distinción.

## Investigación independiente de fuentes — T05, 2026-11-03

**Alcance:** verificar candidatos y recomendar próximos pasos. No se incorporan
los informes, pipelines ni resultados de las ramas anteriores T05–T12. Se
consultaron fuentes directamente y se descargaron los dos CSV en memoria con
Python estándar (`urllib.request`, `csv`, `hashlib` y `datetime`), sin persistir
datos, instalar dependencias, limpiar, entrenar ni escribir en S3.

### Comparación y decisión provisional

| Candidato / editor consultado | Acceso observado | Licencia y procedencia | Objetivo y adecuación | Decisión T05 |
|---|---|---|---|---|
| Zomato, copia publicada por `tushar99deep` | CSV completo accesible; 45,584 registros y 20 columnas contados. | Permiso de uso/redistribución del dataset **no confirmado**. La API de licencia del repositorio devolvió 404; eso no acredita permiso ni demuestra ausencia de derechos. La página Kaggle enlazada no aportó texto verificable en esta consulta. | Existe `Time_taken (min)`, pero la copia no acredita cómo se midió ni sus extremos temporales. Coordenadas y vehículo no bastan para validar etiquetas. | No seleccionado. Falta evidencia primaria de medición, licencia y cobertura. |
| DoorDash, copia publicada por `dklim-git` | CSV completo accesible; 197,428 registros y 16 columnas contados. | Permiso del dataset **no confirmado**; API de licencia de la copia: 404. La descripción del desafío declara perturbación por ruido. | Describe solicitud→entrega mediante `created_at` y `actual_delivery_time`; no contiene coordenadas ni modalidad del repartidor. No se presenta como duración observada inalterada. | No seleccionado para cumplir el requisito actual de etiquetas reales verificadas sin resolver el efecto de la perturbación. |
| LaDe-D, publicado por `Cainiao-AI` | Ficha y API públicas; muestra de 100 registros con 17 columnas accedida en `delivery_jl`. No se descargó ni contó el conjunto completo. | La ficha declara `apache-2.0`; el artículo de los autores declara CC BY-NC 4.0 para los datos. Hay una discrepancia que debe aclararse para la versión utilizada. | Eventos `accept_time` y `delivery_time` documentados por los autores; paquetería de última milla en China. Aceptación→entrega ocurre después de la cotización del MVP. | Alternativa prioritaria para investigar procedencia, condicionada a resolver licencia y acordar el instante de predicción; no seleccionada ni validada. |

Fuentes de las afirmaciones documentales:

- [Repositorio de la copia Zomato](https://github.com/tushar99deep/Zomato_Order_Delivery-Time_Prediction_End-to-End-ML-Application) y [ficha Kaggle inicialmente propuesta](https://www.kaggle.com/datasets/saurabhbadole/zomato-delivery-operations-analytics-dataset). No se ha acreditado que la copia y esa ficha correspondan a una misma versión original autorizada.
- [Repositorio de la copia DoorDash](https://github.com/dklim-git/DoorDash-Project) y [descripción del desafío reproducida por Sean329](https://github.com/Sean329/DoorDash-Delivery-Duration/blob/main/%23%23%23%23%20Data%20description%20%23%23%23%23). Esta última sigue siendo una copia de la descripción, no una publicación corporativa primaria con licencia confirmada.
- [Ficha LaDe-D](https://huggingface.co/datasets/Cainiao-AI/LaDe-D/blob/e1f85a3339848b9eb606ce543fcaaba3f4be1893/README.md), [artículo de los autores, sección 3 y apéndice C.6](https://arxiv.org/html/2306.10675v2) y [código de los autores](https://github.com/wenhaomin/LaDe). Se distingue la licencia de los datos de la licencia del artículo o del código.

### Evidencia de acceso y versiones

Los hashes siguientes corresponden a los bytes originales descargados, antes
de parsear el CSV. Los tamaños son bytes del archivo, no memoria de un DataFrame.
Contar filas y verificar hashes no demuestra por sí solo la procedencia real.

| Copia inspeccionada | Revisión del repositorio | Bytes | SHA-256 |
|---|---|---:|---|
| Zomato | `016f391a017f7222d1f6ff3990ea0739a7e6fd78` | 6,371,825 | `e33e182ebb9c1d7e0f54c83c0cef6ddc5aa98d203e8888d33ab68cca3a079cba` |
| DoorDash | `3f20e78a4a3abf5e4cf2eb0c5d9b6f82f9f554ca` | 19,585,886 | `b87ae94bd8bf99accc8fd1873dde1ef5f5e1ce76074f22abdb734c54a1bc8d94` |

URLs de los archivos verificados, fijadas a esas revisiones:

- [Zomato finalTrain.csv](https://raw.githubusercontent.com/tushar99deep/Zomato_Order_Delivery-Time_Prediction_End-to-End-ML-Application/016f391a017f7222d1f6ff3990ea0739a7e6fd78/notebook/data/finalTrain.csv).
- [DoorDash historical_data.csv](https://raw.githubusercontent.com/dklim-git/DoorDash-Project/3f20e78a4a3abf5e4cf2eb0c5d9b6f82f9f554ca/historical_data.csv).

Observaciones propias sobre archivos sin transformar:

- **Zomato:** `Order_Date`, interpretado con `%d-%m-%Y`, abarca 2022-02-11 a 2022-04-06. Esto constata valores de la copia, no una cobertura operacional acreditada. Hay 3,640 registros con al menos una de las cuatro coordenadas igual a cero. Al quitar solo espacios al texto de vehículo se cuentan 26,429 `motorcycle`, 15,273 `scooter`, 3,814 `electric_scooter` y 68 `bicycle`. No se equiparan esas categorías con el dominio ni se valida una comparación de tiempos por vehículo. Su país y proceso de recogida siguen sin acreditarse mediante una fuente original.
- **DoorDash:** `created_at`, interpretado como timestamp ISO, abarca 2014-10-19 05:24:15 a 2015-02-18 06:00:44. No hay celdas vacías en `actual_delivery_time`; esto no comprueba validez de todos los intervalos. La descripción habla de comienzos de 2015 y regiones de EE. UU.; la fecha mínima de 2014 requiere aclaración. Los IDs de mercado no permiten atribuir una ciudad concreta sin diccionario.
- **LaDe-D:** revisión consultada `e1f85a3339848b9eb606ce543fcaaba3f4be1893`; muestra obtenida mediante la [API first-rows](https://datasets-server.huggingface.co/first-rows?dataset=Cainiao-AI%2FLaDe-D&config=default&split=delivery_jl), marcada como truncada. Los timestamps inspeccionados usan mes/día y hora sin año. La API de muestra usa referencias mutables: no se afirma que sea un snapshot completo ni se asigna un hash de dataset. La ficha declara 31,415 registros para `delivery_jl`, cifra **del editor, no un conteo propio**. El código de los autores documenta mayo–octubre de 2022 para el conjunto; T07 deberá verificar coherencia temporal y unidades de coordenadas antes de calcular distancias o duraciones.

### Variables útiles y riesgos antes de cotizar

| Candidato | Campos observados relevantes | Disponibilidad / exclusiones |
|---|---|---|
| Zomato | Cuatro coordenadas, `Order_Date`, `Time_Orderd`, `Type_of_order`, `Time_taken (min)`; contexto como clima y tráfico. | Origen/destino y solicitud son candidatos a entradas; clima/tráfico necesitan un origen disponible en el MVP y evidencia de cuándo fueron medidos. `Time_Order_picked` ocurre después; edad/rating/vehículo del repartidor y `multiple_deliveries` no se suponen conocidos antes de asignarlo. |
| DoorDash | Dos timestamps, características del pedido/negocio y contadores operativos. | `actual_delivery_time` solo sirve para construir el target, nunca como entrada. La descripción sitúa los contadores en la creación del pedido, pero la demo necesitaría poder suministrarlos. Las estimaciones de otros modelos no son mediciones ni están necesariamente disponibles en nuestro sistema. |
| LaDe-D | Destino (`lng`, `lat`), zona, ciudad, aceptación y finalización; coordenadas GPS de eventos. | Los campos de finalización no pueden ser features. La aceptación y su posición del repartidor son posteriores al instante de cotización actual. No se usará `ds` como fecha de solicitud si representa el día de finalización. |

Los esquemas inspeccionados se obtuvieron del encabezado de los CSV y de la
respuesta `features` de la muestra LaDe-D; los tipos de CSV son texto crudo,
no un contrato tipado aprobado. T06 deberá completar el diccionario del
candidato elegido y T07 validar unidades, calidad y disponibilidad de features.
No se extrae una conclusión estadística ni un modelo de estos conteos.

### Repetición mínima de la verificación de acceso

Desde la raíz, con Python estándar, sin instalar dependencias ni guardar CSV:

```bash
python3 - <<'PY'
import csv
import hashlib
import io
from urllib.request import Request, urlopen

sources = [
    ("Zomato", "tushar99deep/Zomato_Order_Delivery-Time_Prediction_End-to-End-ML-Application",
     "016f391a017f7222d1f6ff3990ea0739a7e6fd78", "notebook/data/finalTrain.csv"),
    ("DoorDash", "dklim-git/DoorDash-Project",
     "3f20e78a4a3abf5e4cf2eb0c5d9b6f82f9f554ca", "historical_data.csv"),
]
for name, repo, revision, path in sources:
    url = f"https://raw.githubusercontent.com/{repo}/{revision}/{path}"
    request = Request(url, headers={"User-Agent": "ml-delivery-T05-research"})
    with urlopen(request, timeout=45) as response:
        content = response.read()
    reader = csv.reader(io.StringIO(content.decode("utf-8-sig")))
    header = next(reader)
    count = sum(1 for _ in reader)
    print(name, count, len(header), len(content), hashlib.sha256(content).hexdigest())
    print("Columnas:", header)
PY
```

En esta investigación se ejecutó además un contador con `csv.DictReader` para
coordenadas/vehículos y `datetime.strptime`/`fromisoformat` para los rangos
temporales. No se ejecutó el pipeline descartado. La receta anterior reproduce
el acceso, volumen y hash, no constituye la adquisición aprobada de T06.

### Recomendación y bloqueo para avanzar a T06

**T05 entrega un informe comparativo con acceso efectivo; ningún dataset queda
seleccionado.** Zomato no se aprueba por parecido con la aplicación; DoorDash
no se presenta como registros sin alterar. LaDe-D merece priorizarse por la
documentación de eventos, pero no autoriza cambiar el objetivo de cotización
por uno posterior a la asignación.

Para iniciar T06, Ruben debe decidir entre: conseguir evidencia primaria y
permisos del candidato alimentario; ampliar la búsqueda manteniendo el instante
de cotización; o evaluar LaDe-D resolviendo la discrepancia de licencia y
acordando explícitamente la adaptación del problema. La última opción requiere
actualizar SPEC/arquitectura antes de depender de una duración desde aceptación.
Mientras tanto, la selección está **pendiente**, no rechazada por falta de acceso.
No se necesita tocar AWS ni entrenar para resolver esta decisión.

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

## Entregables de Ruben antes de T13

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

Antes de usar un candidato, Ruben debe confirmar directamente los derechos de acceso, uso y almacenamiento, además de verificar que el archivo descargado corresponde a la descripción pública.
