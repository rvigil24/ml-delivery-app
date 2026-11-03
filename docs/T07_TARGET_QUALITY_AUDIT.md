# T07 — Auditoría de Calidad y Validación de la Variable Objetivo

**Responsable:** Guillermo Minero  
**Fecha:** 2026-11-02  
**Decisión Final:** `APROBADO_CON_FILTROS`

## 1. Validación de la Variable Objetivo (`Time_taken (min)`)

- **Valores Totales:** 45,584 registros
- **Valores Nulos:** 0 nulos (100% de cobertura)
- **Mínimo Observado:** 10 minutos
- **Máximo Observado:** 54 minutos
- **Media:** 26.30 minutos
- **Mediana:** 26.00 minutos
- **Desviación Estándar:** 9.40 minutos
- **Evaluación:** El rango [10, 54] minutos corresponde a duraciones operativas reales de entregas urbanas. No se encontraron valores negativos, ceros ni duraciones absurdas (> 300 min). Target validado.

## 2. Auditoría de Calidad y Detección de Fuga de Datos (Leakage)

| Variable | Tipo / Estado | Hallazgo de Auditoría | Acción en Pipeline |
|---|---|---|---|
| Coordenadas GPS (Lat/Lon) | 3,640 registros en 0.0 | Indica GPS no registrado en el dispositivo del comercio o cliente | **Filtrar obligatoriamente** antes de calcular distancias |
| `Time_Order_picked` | Timestamp de recolección | **Data Leakage**: Esta marca temporal no existe al momento de cotizar el pedido | **Excluir** de las variables predictoras |
| `distance_km` | Métrica calculada | Distancia ortodrómica Haversine calculada directamente de coordenadas reales | **Feature primaria** para cotización |
| `Weather_conditions` | 616 nulos | Cadenas con prefijo 'conditions ' y espacios | Limpiar formato y filtrar nulos |
| `Road_traffic_density` | 601 nulos | Valores: Low, Medium, High, Jam | Limpiar espacios y codificar |
| `Type_of_vehicle` | 0 nulos | motorcycle (26,429), scooter (15,273), electric_scooter (3,814), bicycle (68) | Desbalance severo en bicicletas; documentar regla de negocio |
