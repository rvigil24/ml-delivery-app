"""T14: referencia constante fijada antes de evaluar el conjunto de prueba."""

import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from delivery_ml.model_data import model_xy


def validated_xy(partition: pd.DataFrame):
    x, y = model_xy(partition)
    if x.empty:
        raise ValueError("La partición está vacía")
    x = x.apply(pd.to_numeric, errors="raise")
    y = pd.to_numeric(y, errors="raise")
    if (x.isna().any().any() or x.isin([float("inf"), float("-inf")]).any().any()
            or y.isna().any() or y.isin([float("inf"), float("-inf")]).any() or y.le(0).any()):
        raise ValueError("Se requieren features finitas y duraciones positivas finitas")
    return x, y


def fit_baseline(train: pd.DataFrame) -> DummyRegressor:
    """Mediana de y_train: referencia elegida para MAE, sin tuning con test."""
    x, y = validated_xy(train)
    return DummyRegressor(strategy="median").fit(x, y)


def evaluate_baseline(model: DummyRegressor, partition: pd.DataFrame) -> dict:
    """Evalúa el modelo congelado; no llama fit ni modifica su constante."""
    x, y = validated_xy(partition)
    prediction = model.predict(x)
    return {
        "rows": len(y),
        "mae_minutes": float(mean_absolute_error(y, prediction)),
        "rmse_minutes": float(root_mean_squared_error(y, prediction)),
    }
