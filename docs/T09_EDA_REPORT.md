# T09 — Informe de Análisis Exploratorio de Datos (EDA)

**Responsable:** Guillermo Minero  
**Fecha:** 2026-11-02  

## 1. Perfil de la Variable Objetivo (`time_taken_min`)

- **Registros procesados válidos:** 41,368 registros (tras filtrar coordenadas 0.0)
- **Media:** 26.29 minutos
- **Mediana:** 26.00 minutos
- **Desviación Estándar:** 9.38 minutos
- **Mínimo:** 10.00 minutos
- **Máximo:** 54.00 minutos
- **Rango Intercuartil (P25 - P75):** 19.00 - 32.00 minutos
- **Distribución:** Simétrica y acotada, centrada en 26 minutos con leve bimodalidad producida por franjas horarias de congestión vehicular.

## 2. Distancia Ortodrómica (`distance_km`)

- **Fórmula:** Haversine ortodrómica sobre radio terrestre de 6,371 km
- **Media:** 9.78 km
- **Mediana:** 9.25 km
- **Mínimo:** 0.05 km
- **Máximo:** 49.80 km
- **Correlación con Tiempo de Entrega:** **+0.298** (correlación positiva moderada; el tiempo se ve fuertemente influido por tráfico y clima).

## 3. Comportamiento por Tipo de Vehículo

| Tipo de Vehículo | Conteo | Media (min) | Mediana (min) | Desviación Estándar |
|---|---|---|---|---|
| `motorcycle` | 23,982 | 27.60 | 27.00 | 9.15 |
| `scooter` | 13,870 | 24.50 | 24.00 | 9.42 |
| `electric_scooter` | 3,454 | 24.40 | 24.00 | 9.38 |
| `bicycle` | 62 | 26.20 | 26.00 | 8.85 |

> [!WARNING]
> La muestra de bicicletas en el dataset real es de únicamente 62 observaciones tras la limpieza de GPS, lo cual es estadísticamente insuficiente para entrenar un modelo que diferencie rendimientos de bicicleta vs motocicleta. Por tanto, conforme a las reglas del proyecto (`AGENTS.md`), las limitaciones de bicicleta y motocicleta se manejarán mediante **reglas de negocio explícitas y configurables**, no por inferencia predictiva del modelo.

## 4. Comportamiento por Densidad de Tráfico

| Densidad de Tráfico | Conteo | Media (min) | Mediana (min) |
|---|---|---|---|
| `Low` | 14,021 | 21.20 | 21.00 |
| `Medium` | 9,985 | 26.70 | 26.00 |
| `High` | 4,025 | 27.20 | 27.00 |
| `Jam` | 13,337 | 31.10 | 31.00 |

La congestión vehicular (`Jam`) eleva el tiempo medio de entrega en aproximadamente 10 minutos (+47%) respecto a tráfico despejado (`Low`).
