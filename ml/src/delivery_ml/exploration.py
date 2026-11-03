"""Resúmenes agregados de T09; no modifica ni filtra la cohorte."""

import pandas as pd


TARGET = "time_taken_min"
COORDINATES = ["sender_lat_raw", "sender_lng_raw", "recipient_lat_raw", "recipient_lng_raw"]


def grouped_duration(data: pd.DataFrame, key: str) -> list:
    grouped = data.groupby(key, sort=True)[TARGET]
    table = grouped.agg(count="count", mean="mean", median="median")
    table["p10"] = grouped.quantile(0.10)
    table["p90"] = grouped.quantile(0.90)
    return table.reset_index().to_dict(orient="records")


def summarize_orders(orders: pd.DataFrame) -> dict:
    """Perfila la tabla preparada; los extremos son señales, no descartes."""
    if orders.empty:
        raise ValueError("La cohorte está vacía")
    data = orders.copy()
    target = data[TARGET]
    if target.isna().any() or target.isin([float("inf"), float("-inf")]).any() or target.le(0).any():
        raise ValueError("Target ausente, no finito o no positivo; revisar preparación")
    created = pd.to_datetime(data["platform_order_time"], unit="s", utc=True)
    data["request_date_utc"] = created.dt.strftime("%Y-%m-%d")
    q = target.quantile([0.01, 0.10, 0.25, 0.5, 0.75, 0.90, 0.95, 0.99])
    iqr = float(q.loc[0.75] - q.loc[0.25])
    lower, upper = float(q.loc[0.25] - 1.5 * iqr), float(q.loc[0.75] + 1.5 * iqr)
    # Spearman = Pearson de rangos promedios; no requiere instalar SciPy.
    correlations = data[[TARGET] + COORDINATES].rank(method="average").corr()
    return {
        "rows": len(data),
        "columns": list(orders.columns),
        "dtypes": {name: str(dtype) for name, dtype in orders.dtypes.items()},
        "quality": {
            "missing_by_column": {name: int(value) for name, value in orders.isna().sum().items()},
            "duplicate_orders": int(data["order_id"].duplicated().sum()),
            "duplicate_waybills": int(data["source_waybill_id"].duplicated().sum()),
            "target_mismatch": int(((data["arrive_time"] - data["platform_order_time"]) / 60 - target).abs().gt(1e-9).sum()),
            "utc_context_mismatch": int((created.dt.hour.ne(data["request_hour_utc"]) | created.dt.dayofweek.ne(data["request_weekday_utc"])).sum()),
        },
        "duration_minutes": {
            "min": float(target.min()), "max": float(target.max()),
            "mean": float(target.mean()), "std_population": float(target.std(ddof=0)),
            **{f"p{int(probability * 100):02d}": float(value) for probability, value in q.items()},
        },
        "tail_diagnostics": {
            "method": "Tukey: Q1 - 1.5*IQR y Q3 + 1.5*IQR; diagnóstico, sin eliminar filas",
            "lower_fence_minutes": lower, "upper_fence_minutes": upper,
            "below_lower_fence": int(target.lt(lower).sum()),
            "above_upper_fence": int(target.gt(upper).sum()),
            "above_p99": int(target.gt(q.loc[0.99]).sum()),
            "removed_rows": 0,
        },
        "by_hour_utc": grouped_duration(data, "request_hour_utc"),
        "by_weekday_utc": grouped_duration(data, "request_weekday_utc"),
        "by_date_utc": grouped_duration(data, "request_date_utc"),
        "dates_per_weekday_utc": {
            str(day): int(count) for day, count in data[["request_date_utc", "request_weekday_utc"]]
            .drop_duplicates().groupby("request_weekday_utc").size().items()
        },
        "spearman_raw_coordinates": correlations.astype(object).where(correlations.notna(), None).to_dict(),
    }
