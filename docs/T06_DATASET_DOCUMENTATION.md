# T06 — Documentación y Adquisición del Dataset en Memoria

**Responsable:** Guillermo Minero  
**Fecha:** 2026-11-02  
**Estrategia de Adquisición:** Carga por flujo HTTP directamente en memoria (RAM), sin almacenar archivos CSV locales en el repositorio ni en disco.

## 1. Identificación y Hash

- **URL de Origen:** `https://raw.githubusercontent.com/tushar99deep/Zomato_Order_Delivery-Time_Prediction_End-to-End-ML-Application/main/notebook/data/finalTrain.csv`
- **Tamaño en Bytes:** 6,371,825 bytes (~6.08 MB)
- **Hash SHA-256:** `e33e182ebb9c1d7e0f54c83c0cef6ddc5aa98d203e8888d33ab68cca3a079cba`
- **Registros Totales:** 45,584 filas
- **Columnas Totales:** 20 columnas

## 2. Diccionario de Datos

| Columna | Tipo Crudo | Descripción | Disponibilidad para Cotización |
|---|---|---|---|
| `ID` | string | Identificador único del pedido | No (post-pedido) |
| `Delivery_person_ID` | string | Identificador del repartidor | Asignación posterior |
| `Delivery_person_Age` | float | Edad del repartidor | Asignación posterior |
| `Delivery_person_Ratings` | float | Calificación histórica del repartidor | Asignación posterior |
| `Restaurant_latitude` | float | Latitud geográfica del comercio | **Sí (pre-cotización)** |
| `Restaurant_longitude` | float | Longitud geográfica del comercio | **Sí (pre-cotización)** |
| `Delivery_location_latitude` | float | Latitud geográfica del cliente | **Sí (pre-cotización)** |
| `Delivery_location_longitude` | float | Longitud geográfica del cliente | **Sí (pre-cotización)** |
| `Order_Date` | string | Fecha del pedido | Contexto temporal |
| `Time_Orderd` | string | Hora en que el cliente realizó el pedido | **Sí (pre-cotización)** |
| `Time_Order_picked` | string | Hora de recolección en restaurante | **Fuga de datos (excluir)** |
| `Weather_conditions` | string | Clima observado (Sunny, Stormy, Fog, etc.) | **Sí (contexto operativo)** |
| `Road_traffic_density` | string | Densidad del tráfico (Low, Medium, High, Jam) | **Sí (contexto operativo)** |
| `Vehicle_condition` | int | Estado del vehículo (0, 1, 2) | Asignación |
| `Type_of_order` | string | Categoría del pedido (Snack, Meal, Drinks) | **Sí** |
| `Type_of_vehicle` | string | Tipo de vehículo (`motorcycle`, `scooter`, `bicycle`) | **Sí (regla de vehículo)** |
| `multiple_deliveries` | float | Cantidad de entregas asignadas simultáneamente | Asignación operativa |
| `Festival` | string | Indicador de festival / alta demanda (Yes/No) | Contexto de fecha |
| `City` | string | Tipo de zona (Urban, Metropolitian, Semi-Urban) | **Sí** |
| `Time_taken (min)` | string/int | Duración de la entrega en minutos | **Variable Objetivo (Target)** |

## 3. Receta de Carga

Módulo: [`ml/src/delivery_ml/loader.py`](file:///d:/Proyecto%20Kodigo/ml-delivery-app/ml/src/delivery_ml/loader.py)
```python
from delivery_ml.loader import load_zomato_dataset_in_memory

df, metadata = load_zomato_dataset_in_memory()
print(f"Filas: {metadata.num_rows}, Hash: {metadata.sha256_hash}")
```

