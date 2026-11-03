# DATA_ML — Datos reales, procesamiento y modelos predictivos

**Responsabilidad actual:** Ruben Vigil asume T05–T19 por instrucción explícita del 2026-11-03. **Estado:** Meituan seleccionado y adquirido; auditoría T07 aprueba con condiciones la preparación académica de una cohorte de pedidos inmediatos. El resultado y las restricciones vigentes están en la sección T07. Las entregas anteriores descartadas de T05–T12 no se utilizan como evidencia. Las secciones previas conservan la historia de investigación y selección.

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

### Resultado inicial de la investigación (ampliado más abajo)

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

## Ampliación de T05 — fuentes con datos previos a la asignación

**Consulta:** 2026-11-03. Ruben autorizó ampliar la búsqueda conservando la
predicción desde solicitud del pedido. Se inspeccionaron dos candidatos nuevos
mediante sus publicaciones oficiales y archivos accesibles; el objetivo del
proyecto no cambia. Esta sección actualiza la recomendación inicial anterior.

| Candidato | Procedencia y acceso comprobados | Objetivo documentado / entradas candidatas | Condiciones y limitaciones |
|---|---|---|---|
| **Meituan / INFORMS TSL Research Challenge** | Repositorio de la organización Meituan, enlazado por INFORMS. ZIP oficial descargado y leído en memoria. Se contaron 654,343 filas y 568,546 `order_id` distintos. | `(arrive_time - platform_order_time) / 60`: creación del pedido→entrega, desde timestamps Unix en segundos según el diccionario oficial. Origen, destino, instante de solicitud y atributos del pedido pueden conocerse antes de asignar repartidor. | Uso académico/no comercial con reconocimiento y prohibición explícita de redistribuir sin permiso. Datos de China, con coordenadas desplazadas e intentos de asignación repetidos; no demuestra desempeño local ni por vehículo. |
| **`modeldata::deliveries` / tidymodels** | Mantenido por Max Kuhn y autores de modeldata. CSV de R-universe consultado: 10,012 filas y 31 columnas; también se accedió al `.rda` original. | `time_to_delivery`, minutos solicitud→recepción según la ficha. `hour`, `day`, `distance` (millas aproximadas) y 27 conteos de artículos del pedido. Son variables conceptualmente disponibles al solicitar comida. | El paquete declara MIT; no se encontró una restricción particular en la ficha del dataset. Un solo restaurante, sin país/periodo publicados en esa ficha, sin coordenadas, vehículo ni timestamps originales para auditar el intervalo. La procedencia del estudio se apoya en el editor, no en registros operativos primarios. |

### Evidencia y condiciones de Meituan

- [Publicación oficial de INFORMS](https://connect.informs.org/tsl/tslresources/datachallenge): identifica datos operativos reales de Meituan, permite investigación académica y exige no compartirlos por otros canales. La [licencia publicada por Meituan](https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/blob/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/License.txt) declara CC BY-NC 4.0 y añade condiciones explícitas de no distribución y reconocimiento. La adquisición actual es local y académica. No se publican registros en Git ni frontend. No se deduce de estos términos una prohibición absoluta de AWS: el diseño contempla almacenamiento privado sujeto a revisión de las condiciones del editor antes de la primera subida. No asumir uso comercial permitido por el carácter económico de la demo.
- [Diccionario oficial, tablas 1–2](https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/blob/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/TSL-Meituan%20challenge_background%20and%20data_20240321.pdf): define creación, asignación, recogida y entrega. [Aclaraciones oficiales de octubre de 2024](https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/blob/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/tsl_meituan_2024_data_report_20241015.pdf): coordenadas desplazadas, timestamps cero en intentos rechazados y otros problemas conocidos. Ambos PDF se descargaron temporalmente y se leyeron con `pdftotext`; los temporales se eliminaron.
- Revisión inspeccionada: `1f9b4288cee5a78d1e5da007fc306bbaa662fc6d`. [ZIP verificado](https://raw.githubusercontent.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/all_waybill_info_meituan_0322.csv.zip): **38,763,754 bytes**, SHA-256 `38b51431a12dd7e73deb4fc750b1275067fbc29cfce2c4b4492339738c988ce2`. CSV interno `all_waybill_info_meituan_0322.csv`: **121,698,401 bytes**, SHA-256 `1d31aac21e17c11aec6ab0033d4040c03aea5bab1dfd60aa11e74d766bbd2c04`.
- El CSV tiene **24 columnas**, incluida una primera columna sin nombre que debe tratarse como índice de exportación, no como predictor. Las fechas `dt` observadas abarcan **20221017–20221024**. Se contaron **568,545 filas con `arrive_time > 0`**; esto no equivale a 568,545 pedidos válidos ni a un dataset ya depurado.
- **Exclusiones antes de cotizar:** `courier_id`, coordenadas `grab_*`, `dispatch_time`, `grab_time`, `fetch_time`, aceptación y demás resultados de asignación. `arrive_time` es exclusivo del target. No usar la promesa `estimate_arrived_time` como sustituto de la duración observada. El instante al que se generó `estimate_meal_prepare_time` debe aclararse antes de usar esa estimación como feature.
- **Pendiente de T07:** resolver una observación por pedido sin duplicar intentos; tratar ceros, reservas previas y diferencias temporales inválidas; verificar unidades de coordenadas y zona horaria. Los límites comerciales, filtros de distancia y comparación entre vehículos no se deducen del dataset. Por ahora, no se declara el target aprobado ni se computan métricas ML.

### Evidencia y límites de `modeldata::deliveries`

- [Ficha del mantenedor](https://modeldata.tidymodels.org/reference/deliveries.html) y [documentación versionada](https://github.com/tidymodels/modeldata/blob/00f1e0a7d1a08d38da02c09133f7f90b2efae318/R/deliveries.R): describen un estudio de entregas de un restaurante y las unidades. El [caso de estudio de los autores](https://aml4td.org/chapters/whole-game.html) explica que la duración completa es conocida. Esto es evidencia editorial de observaciones, no verificación independiente del proceso original de medición.
- [DESCRIPTION](https://github.com/tidymodels/modeldata/blob/00f1e0a7d1a08d38da02c09133f7f90b2efae318/DESCRIPTION), [LICENSE](https://github.com/tidymodels/modeldata/blob/00f1e0a7d1a08d38da02c09133f7f90b2efae318/LICENSE) y [texto MIT](https://github.com/tidymodels/modeldata/blob/00f1e0a7d1a08d38da02c09133f7f90b2efae318/LICENSE.md) se consultaron como condiciones publicadas del paquete. Una eventual redistribución debe conservar los avisos correspondientes; no se atribuye una licencia inventada a un espejo de terceros.
- [CSV consultado](https://tidymodels.r-universe.dev/modeldata/data/deliveries/csv): **777,729 bytes**, SHA-256 `8c51f20650e825a293b69d499f3203a5fddda6be39f92dbb7622226d54217812`; se contaron 10,012 filas, 31 columnas, siete etiquetas de día y cero celdas vacías del target. No se concluye todavía que todos los valores sean válidos.
- La [API de compilación del editor](https://tidymodels.r-universe.dev/api/packages/modeldata) identificó la versión `1.6.0.9000` y el commit `00f1e0a7d1a08d38da02c09133f7f90b2efae318`. El [`.rda` de ese commit](https://raw.githubusercontent.com/tidymodels/modeldata/00f1e0a7d1a08d38da02c09133f7f90b2efae318/data/deliveries.rda) se descargó: 101,444 bytes, SHA-256 `08b431cdcff9e8a9a2804e29c8374e76ca87da0544064dd93ad6acf4c952c827`. No se convirtió ni se comprobó igualdad fila a fila con el CSV. La URL CSV es mutable; T06 debe fijar la versión y verificar el hash o convertir el original versionado.
- La distancia aproximada en millas no debe confundirse con una ruta vial ni con Haversine del simulador. No hay correspondencia publicada entre `item_01`–`item_27` y comidas locales; no inventar esa equivalencia. T07/T13 pueden evaluar hora, día y distancia sin asumir que el catálogo anónimo es transferible.

### Repetición del acceso a los nuevos candidatos

Se verificaron HTTP, hashes y estructura con Python estándar. Esta receta
repite el acceso para T05, conserva los datos en memoria y selecciona únicamente
el CSV principal del ZIP, excluyendo posibles archivos auxiliares de macOS:

```bash
python3 - <<'PY'
import csv
import hashlib
import io
import zipfile
from urllib.request import Request, urlopen

base = "https://raw.githubusercontent.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/"
revision = "1f9b4288cee5a78d1e5da007fc306bbaa662fc6d"
member = "all_waybill_info_meituan_0322.csv"
sources = [
    ("Meituan ZIP", f"{base}{revision}/{member}.zip"),
    ("modeldata CSV", "https://tidymodels.r-universe.dev/modeldata/data/deliveries/csv"),
]
for name, url in sources:
    with urlopen(Request(url, headers={"User-Agent": "ml-delivery-T05-research"}), timeout=45) as response:
        payload = response.read()
    print(name, "bytes:", len(payload), "SHA-256:", hashlib.sha256(payload).hexdigest())
    if name == "Meituan ZIP":
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            payload = archive.read(member)
        print("CSV interno SHA-256:", hashlib.sha256(payload).hexdigest())
    reader = csv.reader(io.StringIO(payload.decode("utf-8-sig")))
    header = next(reader)
    print("Filas:", sum(1 for _ in reader), "Columnas:", len(header))
PY
```

**Recomendación actual:** priorizar **Meituan** para la adquisición local de T06,
porque tiene procedencia operativa publicada por la plataforma y timestamps
definidos para solicitud→entrega. Las restricciones de distribución son
explícitas; no se publicarían registros. El uso privado de S3 se revisará antes de subir artefactos. `modeldata::deliveries`
es una alternativa más pequeña si se acepta depender de la descripción del
estudio del mantenedor y sus límites de cobertura. Ninguna opción necesita
atribuir capacidad predictiva por vehículo ni cambiar el instante de cotización.

La ampliación resuelve la búsqueda de candidatos técnicamente compatibles.
**Decisión posterior de Ruben, 2026-11-03:** utilizar Meituan con las restricciones
locales y académicas descritas. La validación del target/calidad queda pendiente
de T07; esta selección no equivale a aprobación para entrenar.

**Comprobaciones realizadas:** receta anterior ejecutada correctamente: Meituan,
654,343 filas/24 columnas; modeldata, 10,012 filas/31 columnas; hashes coincidentes
con los registrados. `git diff --check` sin errores. Solo cambió este documento;
sin dependencias nuevas ni experimentos ML. No se ejecutó pytest porque el
cambio es documental y la verificación pertinente fue el acceso a las fuentes.

## Selección y adquisición de Meituan — T06

**Decisión de Ruben, 2026-11-03:** utilizar Meituan para el experimento académico.
El origen es el [repositorio oficial de Meituan](https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge),
referido por [INFORMS TSL](https://connect.informs.org/tsl/tslresources/datachallenge).
Se conserva el objetivo candidato solicitud→entrega; seleccionar la fuente no
aprueba todavía su calidad ni autoriza entrenamiento. Los resultados futuros
serán experimentales y no se presentarán como validación para El Salvador.

### Receta, versión y archivos locales

Desde la raíz de esta copia de trabajo:

```bash
uv run --locked python ml/data/acquire_meituan.py
uv run --locked pytest -q
```

La receta fija el commit de la fuente
`1f9b4288cee5a78d1e5da007fc306bbaa662fc6d`. Descarga ZIP y licencia desde URLs
que incluyen esa revisión, valida tamaño y SHA-256, extrae únicamente el CSV
conocido y registra un manifiesto. Usa Python estándar, sin dependencias nuevas.
Los datos se publican en la carpeta final solo después de completar la descarga
y verificación. Si una copia ya existe, comprueba integridad y manifiesto sin
volver a descargar ni sobrescribir archivos. Una copia alterada produce error.

Ubicación predeterminada, ignorada por Git:
`data/raw/meituan/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/`.
`--output <directorio>` permite elegir otra ubicación local; esa carpeta también
debe mantenerse fuera del control de versiones y de canales compartidos.

| Archivo verificado | Bytes originales | SHA-256 |
|---|---:|---|
| `all_waybill_info_meituan_0322.csv.zip` | 38,763,754 | `38b51431a12dd7e73deb4fc750b1275067fbc29cfce2c4b4492339738c988ce2` |
| `all_waybill_info_meituan_0322.csv` | 121,698,401 | `1d31aac21e17c11aec6ab0033d4040c03aea5bab1dfd60aa11e74d766bbd2c04` |
| `License.txt` | 1,961 | `469f53d91ee9d0dbdf7b60146bfdbcee57732db4f2b6bb13c41bfdf28c30daab` |

Se registró la descarga en `2026-11-03T20:50:19.293896+00:00` (UTC). El CSV
contiene **654,343 filas y 24 columnas**, incluida la primera sin nombre.
`manifest.json` conserva fecha real de descarga, URLs, revisión, inventario,
hashes, condiciones de uso y la indicación de que no se aplicaron transformaciones.
Una fila corresponde a un registro de despacho/waybill; no se afirma que cada
fila sea un pedido único ni una entrega válida.

### Licencia y alcance permitido

Se conserva la [licencia de la revisión elegida](https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/blob/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/License.txt):
el editor declara CC BY-NC 4.0 y condiciones adicionales de uso académico/no
comercial, no distribución sin permiso y reconocimiento de Meituan. Los registros
están actualmente en almacenamiento local ignorado y no se publican en Git ni
frontend. El reconocimiento solicitado se conserva en `License.txt`. El uso
privado de S3 y el alcance permitido para modelos derivados se revisarán antes
de su publicación; no se consideran prohibidos ni autorizados de forma automática.

### Papel de AWS y corrección de la restricción anterior

El diseño mantiene `datasets/` para versiones autorizadas de originales,
procesados y particiones; `models/` para pipeline/modelo validado, métricas y
manifiesto; y `docs/` para evidencia académica. El destino previsto es el bucket
existente `ml-kodigo-resources`, con acceso restringido para el proyecto.
No se ha comprobado todavía el acceso o configuración efectiva del bucket.

La afirmación anterior «Meituan no puede subirse a S3» fue demasiado amplia.
El [texto CC BY-NC 4.0, secciones 1 y 2](https://creativecommons.org/licenses/by-nc/4.0/legalcode.en)
permite reproducción y adaptación no comercial y distingue compartir con el
público. Meituan añade una restricción de distribución a terceros. Ninguno de
esos textos menciona expresamente AWS. Esto justifica separar copia privada
académica de publicación, pero no acredita una autorización específica del
editor para el caso concreto de alojamiento externo o distribución de modelos.

**Condición pendiente para T33/T19:** comprobar compatibilidad de ese uso con
los términos, definir qué artefactos pueden alojarse de forma privada y conservar
licencia/atribución. Si no se puede justificar, resolver permiso o fuente antes
de publicar esos artefactos. La auditoría T07 aprueba calidad para preparación
académica; no certifica derechos de publicación ni da permiso de despliegue.
Se corrige la documentación sin subir archivos, cambiar el bucket o iniciar
servicios AWS. El desarrollo de la preparación local puede continuar.

### Diccionario del CSV original

El archivo es CSV: la receta conserva sus textos originales y no realiza
conversión, imputación, filtrado ni renombrado. Los tipos/unidades siguientes
describen la semántica del editor; T07 verificará que los valores la respeten.
Fuentes: [tablas 1–2 del diccionario](https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/blob/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/TSL-Meituan%20challenge_background%20and%20data_20240321.pdf)
y [aclaraciones de octubre de 2024](https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/blob/1f9b4288cee5a78d1e5da007fc306bbaa662fc6d/tsl_meituan_2024_data_report_20241015.pdf).

| Columna(s) | Significado / unidad | Disponibilidad para cotizar |
|---|---|---|
| Primera columna sin nombre | Índice aparente de exportación; sin semántica de negocio documentada | Excluir como predictor. |
| `dt` | Fecha de creación del pedido, formato `YYYYMMDD` | Candidata, verificar coherencia con el timestamp. |
| `order_id` | Identificador anonimizado de pedido | Agrupación y trazabilidad; no predictor numérico. |
| `waybill_id` | Identificador anonimizado del registro de despacho; un pedido puede tener varios | Trazabilidad de intentos; no predictor. |
| `courier_id` | Repartidor al que se asignó el registro | Posterior a la solicitud; excluir antes de asignar. |
| `da_id` | Área operativa anonimizada; áreas pueden solaparse | Solo si su correspondencia está disponible al solicitar; no equivale a una zona de El Salvador. |
| `is_courier_grabbed` | Indicador de aceptación del repartidor | Resultado posterior; excluir como entrada. |
| `is_weekend` | Indicador de fin de semana de la fecha del pedido | Candidato, verificar calendario. |
| `estimate_arrived_time` | Timestamp Unix en segundos de la entrega prometida | Estimación del sistema original, no duración observada; no se supone disponible en nuestra API. |
| `is_prebook` | Indicador de pedido reservado previamente | Candidato a contexto; T07 debe decidir tratamiento de reservas. |
| `poi_id` | Identificador anonimizado del negocio | No tiene correspondencia con negocios locales; evitar asumir transferencia de IDs. |
| `sender_lng`, `sender_lat` | Coordenadas desplazadas del origen, almacenadas como enteros | Origen conocido conceptualmente; escala/unidades a comprobar antes de calcular distancia. |
| `recipient_lng`, `recipient_lat` | Coordenadas desplazadas del destino, almacenadas como enteros | Destino conocido conceptualmente; no son ubicaciones reales publicadas sin anonimización. |
| `grab_lng`, `grab_lat` | Posición desplazada del repartidor al asignar; puede ser cero | Posterior a cotización; excluir como entrada. |
| `dispatch_time` | Timestamp Unix en segundos de asignación del waybill | Posterior a solicitud; excluir como entrada. |
| `grab_time` | Timestamp Unix en segundos de aceptación | Posterior; no usar para predecir desde solicitud. |
| `fetch_time` | Timestamp Unix en segundos de recogida | Posterior; excluir como entrada. |
| `arrive_time` | Timestamp Unix en segundos de entrega; cero puede indicar evento ausente | Solo para construir el target observado, nunca como predictor. |
| `estimate_meal_prepare_time` | Timestamp Unix en segundos de la hora estimada de comida lista | Instante de generación no confirmado para nuestra cotización; no aprobar como feature todavía. |
| `order_push_time` | Timestamp Unix en segundos de entrada al sistema de asignación | Posterior a creación; no sustituye automáticamente el instante de solicitud. |
| `platform_order_time` | Timestamp Unix en segundos de creación del pedido | Base del intervalo objetivo y posible contexto temporal. |

El objetivo candidato sigue siendo `(arrive_time - platform_order_time) / 60`
en minutos, pendiente de T07. No se crean etiquetas ni se calculan métricas en
T06. Quedan por auditar: ceros, intervalos inválidos, intentos repetidos,
reservas, zona horaria, escala geográfica y variables disponibles al solicitar.

### Comprobaciones de T06

La adquisición real completó hashes, tamaños y estructura. Una segunda ejecución
con la red bloqueada verificó la copia existente y conservó el manifiesto.
Las tres pruebas nuevas son offline: rechazan bytes alterados, extraen solo el
miembro esperado y comprueban que una descarga fallida no publica una copia
parcial. `pytest` descubre ahora `backend/tests` y `ml/tests`.

Resultado final: **19 pruebas aprobadas en Python 3.12.14 y 3.9.25** (16 previas
y 3 de adquisición). `uv lock --check`, `uv pip check` y `git diff --check`
correctos. ZIP, CSV, licencia y manifiesto están ignorados por Git. La
adquisición no requirió credenciales, conexiones AWS ni entrenamiento.

## Auditoría de calidad y objetivo — T07, 2026-11-03

**Decisión:** `APROBADO_CON_CONDICIONES` para preparar en T08 una cohorte de
pedidos inmediatos completados. La etiqueta representa minutos desde creación
del pedido hasta entrega observada: `(arrive_time - platform_order_time) / 60`.
Su significado procede del diccionario oficial de Meituan; se comprobaron los
valores del archivo adquirido. No se derivan tiempos mediante distancia o
velocidades supuestas, no se entrena un modelo y no se certifica desempeño local.

### Reproducción

```bash
uv run --locked python ml/data/audit_meituan.py
uv run --locked pytest -q
```

El script comprueba primero el SHA-256 del CSV de T06 y escribe únicamente
agregados en `data/reports/meituan/<revision>/t07_audit.json`, ignorado por Git.
No modifica el original ni genera un dataset limpio. Un campo obligatorio
ausente, un decimal donde se espera un timestamp entero o un indicador distinto
de 0/1 produce error, en lugar de reparar silenciosamente una etiqueta. Una
decisión `BLOQUEADO` se informa con código de salida 2; el JSON conserva motivos.

### Hallazgos medidos sobre el original

| Comprobación | Resultado |
|---|---:|
| Filas / waybills distintos | 654,343 / 654,343 |
| Pedidos distintos | 568,546 |
| Pedidos con varios intentos | 57,770 |
| `waybill_id` repetidos | 0 |
| Celdas vacías o marcadores textuales de ausencia | 0 en las 24 columnas |
| Filas con `arrive_time = 0` | 85,798 |
| Filas con `grab_time = 0` / `fetch_time = 0` | 85,797 / 85,797 |
| Filas con `dispatch_time = 0` | 1 |
| Filas con `platform_order_time = 0` | 0 |
| Filas con entrega positiva | 568,545 |
| Pedidos sin entrega positiva / con varias entregas positivas | 1 / 0 |
| Intervalos no positivos entre creación positiva y entrega positiva | 0 |
| Pedidos con cambios en datos de cotización entre intentos | 88 |

No confundir ausencia de celdas vacías con ausencia de datos faltantes: el editor
utiliza **cero como evento ausente**. Los rangos de origen/destino observados son
enteros, no coordenadas ya aprobadas para `Location`: latitud de origen
45,755,268–46,067,416 y longitud 174,481,806–174,988,918; latitud de destino
45,729,124–46,072,996 y longitud 174,387,310–174,994,756. Ninguna de esas cuatro
columnas tiene ceros. No se aplicó Haversine a esos valores ni se inventó una escala.

Cambian el timestamp de creación en **24 pedidos** y las coordenadas de destino
en **66**; hay solapamiento entre ambos grupos y el total ambiguo es **88**, no
la suma de los conteos por columna. También cambian `dt` en 37 pedidos y `da_id`
en 1,963; esos contextos no se usan como sustitutos del instante de solicitud.

### Cohorte propuesta y descarte documentado

Se cuenta un pedido elegible solo si conserva creación, origen, destino y
condición de reserva entre todos sus intentos; tiene una única entrega positiva;
es inmediato (`is_prebook = 0`); y el intento completado está aceptado con eventos
positivos en orden creación→entrada a asignación→asignación→aceptación→recogida→entrega.
La entrega debe ser estrictamente posterior a creación. No se elige simplemente
la última fila ni se conserva un intento rechazado como otra entrega.

| Resultado por pedido, con motivos excluyentes en ese orden | Cantidad |
|---|---:|
| Excluir por cambios en datos de cotización | 88 |
| Excluir por no tener entrega positiva | 1 |
| Excluir por varias entregas positivas | 0 |
| Separar reservas del alcance de pedidos inmediatos | 22,176 |
| Excluir por cronología inválida dentro del resto | 0 |
| **Pedidos elegibles para preparar** | **546,281** |

El total suma los **568,546 pedidos** originales. Son **108,062 filas menos**
que las del archivo crudo porque se consolidan intentos y se delimitan pedidos;
no son 108,062 duraciones falsas o valores atípicos eliminados. Los criterios
están implementados para contar y auditar, pero la cohorte **no está materializada**.
T08 deberá producirla con transformaciones Pandas y verificar estos conteos.

La separación de reservas es semántica, no un umbral de duración: el editor
distingue pedidos inmediatos de entregas programadas. Las reservas completadas
del original tienen mediana de 79.9 minutos y máximo de 10,336.4833 minutos;
mezclarlas como si todas fueran solicitudes inmediatas confundiría espera
programada con desempeño de una entrega. Los motivos de descarte anteriores
usan precedencia: cinco reservas ya están incluidas en el grupo ambiguo, por
eso el conteo separado no es el de todas las reservas completadas (22,181).

Para los 546,281 pedidos elegibles, la duración observada es: mínimo **1.9667**,
mediana **27.9**, media **29.6445**, percentil 95 **51.4333**, percentil 99
**63.2833** y máximo **645.4167 minutos**. Los percentiles usan rango más próximo.
Son estadísticos descriptivos, no métricas de predicción. Las duraciones largas
se conservan: T09 estudiará su distribución; no se impone un máximo arbitrario
ni se convierte este rango en una promesa de tiempo del negocio.

### Disponibilidad de variables y prevención de leakage

| Campo / grupo | Decisión antes de cotizar |
|---|---|
| `platform_order_time` | Disponible al crear el pedido. Permite derivar hora/día en UTC con convención explícita. Es el contexto temporal confirmado para una primera preparación; el esquema final se decide en T13. |
| `is_prebook` | Información de la solicitud usada para delimitar la cohorte inmediata; será constante 0 dentro de ella, no un predictor informativo. |
| `sender_*`, `recipient_*` | Origen/destino son conocidos conceptualmente, pero la representación desplazada y escala requieren confirmación antes de convertir a grados o calcular km. No aprobar todavía una feature física de distancia ni congelar el contrato geográfico de `/predict`. |
| `dt`, `is_weekend` | No asumir que equivalen a la fecha de creación UTC; preferir calendario derivado del timestamp de solicitud. |
| `courier_id`, `grab_*`, `is_courier_grabbed`, `dispatch_time`, `grab_time`, `fetch_time` | Posteriores a cotización; excluidos como features. Usarlos para auditar completitud no significa suministrarlos al predecir. |
| `arrive_time` | Exclusivo de construcción de etiqueta y auditoría; nunca entrada de inferencia. |
| `estimate_arrived_time`, `estimate_meal_prepare_time` | Salidas de sistemas originales cuyo instante/disponibilidad en nuestro flujo no están acreditados; excluidas por ahora. No sustituyen eventos observados. |
| `order_push_time` | Evento posterior a creación; se audita cronología pero no se presupone como entrada de cotización. |
| Índice sin nombre, `order_id`, `waybill_id`, `poi_id`, `da_id` | Trazabilidad/agrupación, no features aprobadas. Los IDs anonimizados no tienen correspondencia con negocios o zonas locales; `da_id` además cambia entre intentos. |

De las 568,545 filas con entrega positiva, `dt` coincide con la fecha de creación
en UTC en **543,390**, y con UTC+8 en **566,787**. La segunda comparación es
diagnóstica: no acredita por sí sola zona horaria o significado de `dt`. Las
diferencias de timestamps Unix no requieren suponer una zona para medir segundos.
Para fechas/hora se usará una convención explícita, sin trasladar silenciosamente
patrones horarios a El Salvador. La cohorte propuesta tiene fechas de creación
UTC del **2022-10-16 al 2022-10-24**; esa cobertura corta limita la evaluación.

### Condiciones para continuar

La aprobación permite preparar y explorar la cohorte inmediata descrita,
inicialmente con contexto temporal conocido. **Las features de distancia quedan
pendientes de confirmar unidades y anonimización**; no bloquean el objetivo
temporal ni autorizan construir una conversión geográfica sin evidencia.
Solo se avanzará al entrenamiento después de cumplir las dependencias T08–T13.

La etiqueta queda condicionada a pedidos completados; no estima probabilidad de
cancelación ni cubre pedidos sin entrega observada. No se afirma generalización
a otros países, temporadas o modalidades de vehículo. Las futuras particiones
deben evitar que un pedido o sus intentos aparezcan en conjuntos distintos y
evaluar separación temporal; no se adopta una partición de forma anticipada.

**Comprobaciones:** auditoría ejecutada sobre el CSV con hash de T06;
**25 pruebas aprobadas en Python 3.12.14 y 3.9.25**, incluidas seis nuevas de
auditoría. Cubren intentos rechazados, destino cambiante, reservas/eventos
ausentes/cronología inversa, parseo estricto, entregas ambiguas y datos vacíos o
IDs de waybill repetidos. `uv lock --check` y `uv pip check` correctos; sin
dependencias nuevas, entrenamiento, escritura AWS ni publicación de registros.

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
