# T05 — Informe Comparativo de Fuentes de Datos de Entregas

**Responsable:** Guillermo Minero  
**Fecha:** 2026-11-02  
**Estado:** Completado y verificado en memoria  

## 1. Candidatos Evaluados

| Criterio | Candidato 1: Zomato Delivery Analytics | Candidato 2: DoorDash Delivery Duration |
|---|---|---|
| **URL de Acceso** | https://raw.githubusercontent.com/tushar99deep/Zomato_Order_Delivery-Time_Prediction_End-to-End-ML-Application/main/notebook/data/finalTrain.csv | https://raw.githubusercontent.com/dklim-git/DoorDash-Project/master/historical_data.csv |
| **Licencia / Términos** | Uso educativo y de investigación (Kaggle/Open Source) | Copia con alteración de datos con fines educativos (StrataScratch) |
| **Volumen Verificado** | 45,584 filas, 20 columnas (6.08 MB) | 197,428 filas, 16 columnas (18.68 MB) |
| **Hash SHA-256** | `e33e182ebb9c1d7e0f54c83c0cef6ddc5aa98d203e8888d33ab68cca3a079cba` | `b87ae94bd8bf99accc8fd1873dde1ef5f5e1ce76074f22abdb734c54a1bc8d94` |
| **Variable Objetivo** | `Time_taken (min)` (observada en minutos) | Duración derivada (`actual_delivery_time` - `created_at` en segundos) |
| **Coordenadas GPS** | Sí (Latitud y Longitud de Restaurante y Entrega) | No (solo IDs agregados de tienda y mercado) |
| **Tipo de Vehículo** | Sí (`motorcycle`, `scooter`, `electric_scooter`, `bicycle`) | No (repartidores no diferenciados por vehículo) |
| **Riesgos Identificados** | 3,640 filas con coordenadas en 0.0 (GPS no capturado); muy pocas bicicletas (68) | Datos perturbados artificialmente con ruido comercial; sin geolocalización |

## 2. Decisión y Recomendación

Se selecciona **Zomato Delivery Analytics** como fuente principal del pipeline ML y cotizaciones:
1. Permite calcular la distancia ortodrómica real en kilómetros mediante la fórmula Haversine a partir de coordenadas exactas.
2. Contiene clasificación explícita de vehículo, compatible con el modelo de dominio `VehicleType`.
3. Requiere filtrar los registros con coordenadas GPS en 0.0 mediante el pipeline de limpieza.

