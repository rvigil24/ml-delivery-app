"""T15: tres familias con configuración inicial fija, sin selección ni tuning."""

import warnings

from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVR

from delivery_ml.baseline import validated_xy


FAMILIES = {
    "linear_regression": "Regresión lineal por mínimos cuadrados",
    "random_forest": "Ensamble de árboles con bagging",
    "linear_svr": "Máquinas de vectores de soporte para regresión",
}


def build_models() -> dict:
    """Parámetros de partida para CPU local; no elegidos con métricas de test."""
    return {
        "linear_regression": make_pipeline(StandardScaler(), LinearRegression()),
        "random_forest": make_pipeline(RandomForestRegressor(
            n_estimators=50, max_depth=12, min_samples_leaf=20,
            n_jobs=2, random_state=42,
        )),
        "linear_svr": make_pipeline(StandardScaler(), LinearSVR(
            C=1.0, epsilon=0.1, loss="squared_epsilon_insensitive",
            dual=False, tol=1e-4, max_iter=10000, random_state=42,
        )),
    }


def fit_model(model, train):
    """Solo recibe train; el escalado se ajusta dentro del pipeline."""
    x, y = validated_xy(train)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        model.fit(x, y)
    return model
