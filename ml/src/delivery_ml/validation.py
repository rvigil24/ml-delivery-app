"""T16: validación temporal con etiquetas disponibles y búsqueda pequeña."""

import warnings

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import GridSearchCV

from delivery_ml.baseline import validated_xy
from delivery_ml.models import build_models


PARAM_GRIDS = {
    "baseline": {},
    "linear_regression": {},  # Control de mínimos cuadrados, sin hiperparámetro de regularización.
    "random_forest": {"randomforestregressor__max_depth": [6, 12]},
    "linear_svr": {"linearsvr__C": [0.1, 1.0]},
}
SCORING = {"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error"}


def expanding_day_folds(train: pd.DataFrame, n_splits: int = 3) -> list:
    """Últimos días de train como validación; purga etiquetas aún desconocidas.

    Devuelve posiciones, no etiquetas del índice, para usar con GridSearchCV.
    La frontera diaria depende solo de creación, nunca de errores predictivos.
    """
    if not isinstance(n_splits, int) or n_splits < 2:
        raise ValueError("Se necesitan al menos dos folds temporales")
    for name in ("order_id", "source_waybill_id"):
        if train[name].isna().any() or train[name].astype(str).str.strip().eq("").any() or train[name].duplicated().any():
            raise ValueError(f"IDs ausentes o duplicados: {name}")
    times = train[["platform_order_time", "arrive_time"]].apply(pd.to_numeric, errors="raise")
    if (times.isna().any().any() or not np.isfinite(times.to_numpy()).all()
            or times.mod(1).ne(0).any().any()
            or times["arrive_time"].le(times["platform_order_time"]).any()):
        raise ValueError("Timestamps enteros y cronología positiva requeridos")
    created = times["platform_order_time"]
    arrived = times["arrive_time"]
    days = pd.to_datetime(created, unit="s", utc=True).dt.floor("D")
    dates = sorted(days.unique())
    if len(dates) <= n_splits:
        raise ValueError("No hay suficientes días para entrenamiento y validación")
    folds = []
    for day in dates[-n_splits:]:
        cutoff = int(day.timestamp())
        fit = np.flatnonzero((created.lt(cutoff) & arrived.lt(cutoff)).to_numpy())
        validation = np.flatnonzero(days.eq(day).to_numpy())
        if not len(fit) or not len(validation):
            raise ValueError("Fold temporal vacío")
        folds.append((fit, validation))
    return folds


def search_models(train: pd.DataFrame, n_splits: int = 3) -> dict:
    x, y = validated_xy(train)
    folds = expanding_day_folds(train, n_splits)
    details = []
    for fit, validation in folds:
        cutoff = pd.to_datetime(train.iloc[validation]["platform_order_time"].min(), unit="s", utc=True).floor("D")
        boundary = int(cutoff.timestamp())
        details.append({
            "validation_start_utc": cutoff.isoformat(),
            "validation_end_exclusive_utc": pd.to_datetime(boundary + 24 * 60 * 60, unit="s", utc=True).isoformat(),
            "training_rows": len(fit), "validation_rows": len(validation),
            "purged_training_rows": int((train["platform_order_time"].lt(boundary) & train["arrive_time"].ge(boundary)).sum()),
            "max_training_arrival_utc": pd.to_datetime(train.iloc[fit]["arrive_time"].max(), unit="s", utc=True).isoformat(),
        })
    results = {}
    estimators = {"baseline": DummyRegressor(strategy="median"), **build_models()}
    for name, model in estimators.items():
        search = GridSearchCV(model, PARAM_GRIDS[name], scoring=SCORING, refit="mae",
                              cv=folds, n_jobs=1, error_score="raise", return_train_score=False)
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            search.fit(x, y)
        candidates = []
        cv = search.cv_results_
        for i, params in enumerate(cv["params"]):
            candidates.append({
                "parameters": params,
                "fold_mae_minutes": [float(-cv[f"split{j}_test_mae"][i]) for j in range(n_splits)],
                "fold_rmse_minutes": [float(-cv[f"split{j}_test_rmse"][i]) for j in range(n_splits)],
                "mean_mae_minutes": float(-cv["mean_test_mae"][i]),
                "std_mae_minutes": float(cv["std_test_mae"][i]),
                "mean_rmse_minutes": float(-cv["mean_test_rmse"][i]),
                "mean_fit_seconds": float(cv["mean_fit_time"][i]),
            })
        results[name] = {
            "candidates": candidates, "best_index": int(search.best_index_),
            "best_parameters": search.best_params_,
            "best_mean_mae_minutes": float(-search.best_score_),
            "refit_training_rows": len(train),
            "refit_steps": [{"class": type(step).__name__, "parameters": step.get_params(deep=False)}
                            for _, step in search.best_estimator_.steps] if hasattr(search.best_estimator_, "steps")
                           else [{"class": type(search.best_estimator_).__name__,
                                  "parameters": search.best_estimator_.get_params(deep=False)}],
        }
    return {"folds": details, "models": results, "parameter_grids": PARAM_GRIDS,
            "selection": "Menor MAE medio, mismo peso por día; empate: primer candidato de la lista fija",
            "checks": {"test_not_loaded_or_evaluated": True, "training_labels_before_each_fold": True,
                       "scaling_inside_cv_pipelines": True, "refit_only_full_train": True}}
