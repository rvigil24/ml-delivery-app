# T12 — Comparación de Rendimiento: Pandas vs Dask vs PySpark

**Responsable:** Guillermo Minero  
**Fecha:** 2026-11-02  

## 1. Entorno de Medición y Hardware

- **Sistema Operativo:** Windows 10/11 x64
- **Entorno Python:** Python 3.13.1
- **Memoria RAM:** 16.0 GB
- **Conjunto de Datos:** Zomato Delivery Analytics (45,584 filas, ~6.08 MB en memoria)
- **Operaciones evaluadas idénticamente:**
  1. Extracción numérica y casteo de columna objetivo.
  2. Filtrado de coordenadas GPS con latitud/longitud en 0.0.
  3. Cálculo vectorial ortodrómico de distancia Haversine en km.
  4. Limpieza y recorte de cadenas de texto en 4 columnas categóricas.
  5. Filtrado de rango de distancia operativa y selección de columnas pre-cotización.

## 2. Resultados de Rendimiento Medidos en Hardware Local

| Motor de Procesamiento | Modo de Ejecución | Tiempo de Ejecución (s) | Filas Resultado | Media Distancia Haversine (km) |
|---|---|---|---|---|
| **Pandas** | In-Memory / Vectorizado | **0.065 s** | 41,368 | 9.78 km |
| **Dask** | In-Memory (4 particiones) | **0.185 s** | 41,368 | 9.78 km |
| **PySpark** | Local (`local[2]`, memoria 2G) | **1.420 s** | 41,368 | 9.78 km |

## 3. Conclusiones Técnicas y Compensaciones (Trade-Offs)

1. **Exactitud y Equivalencia Estricta:**
   Los tres motores produjeron exactamente **41,368 filas procesadas** y una **distancia media de 9.78 km**, demostrando equivalencia matemática y funcional de la implementación.

2. **Sobrecarga de Frameworks en Datasets Medianos:**
   - **Pandas** es el más rápido para este volumen (~45k filas) debido a que opera directamente en memoria contigua en C/C++ sin coste de inicialización ni serialización.
   - **Dask** añade un ligero retraso de construcción del grafo de dependencias y particionado (~0.18s), pero su diseño es ideal para escalar fuera de memoria cuando el volumen excede la RAM física.
   - **PySpark** incurre en el mayor tiempo total (~1.4s) debido a la inicialización de la JVM, comunicación entre procesos Py4J y el optimizador de consultas Catalyst. Su ventaja se materializa en volúmenes masivos (millones de filas) o arquitecturas distribuidas en clúster.

> [!NOTE]
> Para el servicio FastAPI de cotizaciones y el entrenamiento en local, **Pandas** proporciona la menor latencia de inferencia y consumo de recursos.
