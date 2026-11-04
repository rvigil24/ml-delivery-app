"""T18: ajustar configuraciones congeladas y medir errores sin retuning."""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

from delivery_ml.baseline import fit_baseline, validated_xy
from delivery_ml.mlp import SmallMLPRegressor
from delivery_ml.models import build_models, fit_model


def fit_frozen_models(train, parameters: dict, mlp_epochs: int) -> dict:
    """No recibe test; la configuración proviene de la validación interna."""
    fitted = {"baseline": fit_baseline(train)}
    for name, model in build_models().items():
        fitted[name] = fit_model(model.set_params(**parameters[name]), train)
    fitted["mlp"] = SmallMLPRegressor().fit(train, epochs=mlp_epochs)
    return fitted


def regression_metrics(observed, predicted) -> dict:
    y = np.asarray(observed, dtype=float)
    prediction = np.asarray(predicted, dtype=float)
    if y.ndim != 1 or prediction.shape != y.shape or not len(y) or not np.isfinite(y).all() or not np.isfinite(prediction).all():
        raise ValueError("Observaciones/predicciones deben ser vectores finitos del mismo tamaño")
    error = prediction - y
    return {"rows": len(y), "mae_minutes": float(mean_absolute_error(y, prediction)),
            "rmse_minutes": float(root_mean_squared_error(y, prediction)),
            "r2": float(r2_score(y, prediction)) if len(y) > 1 and np.ptp(y) > 0 else None,
            "mean_signed_error_minutes": float(error.mean()),
            "p95_absolute_error_minutes": float(np.quantile(np.abs(error), 0.95))}


def evaluate_models(fitted: dict, partition) -> dict:
    """Mismos pedidos/predictores para todos; predict nunca reajusta modelos."""
    x, y = validated_xy(partition)
    days = pd.to_datetime(partition["platform_order_time"], unit="s", utc=True).dt.strftime("%Y-%m-%d")
    result = {}
    for name, model in fitted.items():
        prediction = np.asarray(model.predict(x))
        overall = regression_metrics(y, prediction)
        overall["by_creation_day_utc"] = {
            day: regression_metrics(y.to_numpy()[mask.to_numpy()], prediction[mask.to_numpy()])
            for day in sorted(days.unique()) for mask in [days.eq(day)]
        }
        result[name] = overall
    return result
