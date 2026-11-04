"""Comparación temporal reproducible de ETA y riesgo, con evidencia real."""

import argparse
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, log_loss,
                             mean_absolute_error, r2_score, roc_auc_score, root_mean_squared_error)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from delivery_ml.artifact import environment_versions
from delivery_ml.delivery_v2 import CONTEXT, RISK_CONTEXT, SCHEMA, eta_features, risk_features, sha256, spherical_distance
from delivery_ml.model_data import temporal_split
from delivery_ml.validation import expanding_day_folds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Nueva versión requerida; no se sobrescriben bundles")
    processed = next(args.data_root.glob("processed/meituan/*/t08-v1/orders.csv"))
    raw = next(args.data_root.glob("raw/meituan/*/*.csv"))
    data = pd.read_csv(processed, dtype={"order_id": "string", "source_waybill_id": "string"})
    promises = pd.read_csv(raw, usecols=["order_id", "waybill_id", "estimate_arrived_time"],
                          dtype={"order_id": "string", "waybill_id": "string"})
    if promises.groupby("order_id").estimate_arrived_time.nunique().gt(1).any():
        raise ValueError("Plazo inestable entre intentos")
    promised = promises.set_index("waybill_id").estimate_arrived_time.reindex(data.source_waybill_id).to_numpy()
    data["promised_minutes"] = (promised - data.platform_order_time.to_numpy())/60
    if not np.isfinite(data.promised_minutes).all() or data.promised_minutes.le(0).any():
        raise ValueError("Plazo prometido no válido")
    coords = [data[name].to_numpy()/1e6 for name in
              ("sender_lat_raw", "sender_lng_raw", "recipient_lat_raw", "recipient_lng_raw")]
    data["distance_km"] = spherical_distance(*coords)
    data["late"] = (data.arrive_time.to_numpy() > promised).astype(int)
    parts = temporal_split(data)
    for name, part in parts.items():
        parts[name] = part.merge(data[["order_id", "distance_km", "promised_minutes", "late"]],
                                 on="order_id", validate="one_to_one")
    train, test = parts["train"], parts["test"]
    folds = expanding_day_folds(train)
    estimators = {
        "eta": {
            "median": DummyRegressor(strategy="median"),
            "linear": LinearRegression(),
            "random_forest": RandomForestRegressor(n_estimators=50, max_depth=12,
                min_samples_leaf=20, n_jobs=2, random_state=42),
            "hist_gradient_boosting": HistGradientBoostingRegressor(loss="absolute_error",
                max_iter=100, max_leaf_nodes=15, min_samples_leaf=30, l2_regularization=1,
                early_stopping=False, random_state=42),
        },
        "risk": {
            "prevalence": DummyClassifier(strategy="prior"),
            "logistic": make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)),
            "hist_gradient_boosting": HistGradientBoostingClassifier(max_iter=100,
                max_leaf_nodes=15, min_samples_leaf=30, l2_regularization=1,
                early_stopping=False, random_state=42),
        },
    }
    evidence = {"created_at_utc": datetime.now(timezone.utc).isoformat(),
        "processed_sha256": sha256(processed), "raw_sha256": sha256(raw),
        "rows": {key: len(value) for key, value in parts.items()},
        "test_previously_observed": True, "coordinate_divisor": 1000000,
        "coordinate_divisor_is_encoding_inference": True, "experiments": {}}
    selected = {}
    for task, candidates in estimators.items():
        columns, target = (CONTEXT, "time_taken_min") if task == "eta" else (RISK_CONTEXT, "late")
        features = eta_features if task == "eta" else risk_features
        results = {}
        for name, estimator in candidates.items():
            pipeline = make_pipeline(FunctionTransformer(features, validate=False), estimator)
            scores = []
            for fit, validation in folds:
                model = clone(pipeline).fit(train.iloc[fit][columns], train.iloc[fit][target])
                if task == "eta":
                    score = mean_absolute_error(train.iloc[validation][target], model.predict(train.iloc[validation][columns]))
                else:
                    score = log_loss(train.iloc[validation][target], model.predict_proba(train.iloc[validation][columns]))
                scores.append(float(score))
            results[name] = {"fold_scores": scores, "mean_score": float(np.mean(scores))}
            print(task, name, "CV", results[name]["mean_score"], flush=True)
        winner = min(results, key=lambda key: results[key]["mean_score"])
        # Selección congelada antes de evaluar test; se informan todos los candidatos.
        for name, estimator in candidates.items():
            model = make_pipeline(FunctionTransformer(features, validate=False), clone(estimator))
            model.fit(train[columns], train[target])
            if task == "eta":
                prediction = model.predict(test[columns])
                metrics = {"mae_minutes": float(mean_absolute_error(test[target], prediction)),
                           "rmse_minutes": float(root_mean_squared_error(test[target], prediction)),
                           "r2": float(r2_score(test[target], prediction))}
            else:
                prediction = model.predict_proba(test[columns])[:, 1]
                metrics = {"log_loss": float(log_loss(test[target], prediction)),
                           "brier": float(brier_score_loss(test[target], prediction)),
                           "roc_auc": float(roc_auc_score(test[target], prediction)),
                           "pr_auc": float(average_precision_score(test[target], prediction)),
                           "late_prevalence": float(test[target].mean())}
            results[name]["test"] = metrics
            if name == winner:
                selected[task] = model
        evidence["experiments"][task] = {"selected_by_cv": winner, "candidates": results}
    args.output.mkdir(parents=True)
    for task, model in selected.items():
        with (args.output / (task + ".pkl")).open("wb") as stream:
            pickle.dump(model, stream)
    (args.output / "evidence.json").write_text(json.dumps(evidence, indent=2)+"\n")
    limitations = ["Datos chinos: sin validación para El Salvador o por vehículo",
        "Distancia esférica aproximada; coordenadas desplazadas y codificación 1e6 inferida",
        "Riesgo aprendido contra plazos prometidos por Meituan; traslado local no calibrado",
        "Test reutilizado y revisión exploratoria, no validación externa ciega",
        "Duración creación–entrega; no es tiempo de conducción ni garantía"]
    card = "# meituan-eta-risk-v2\n\n" + json.dumps(evidence["experiments"], indent=2) + "\n\n" + "\n".join(limitations)
    (args.output / "model_card.md").write_text(card+"\n")
    metadata = {"schema": SCHEMA, "model_version": "meituan-eta-risk-v2",
        "environment": environment_versions(), "eta_inputs": CONTEXT, "risk_inputs": RISK_CONTEXT,
        "eta_algorithm": evidence["experiments"]["eta"]["selected_by_cv"],
        "risk_algorithm": evidence["experiments"]["risk"]["selected_by_cv"],
        "training_input_ranges": {name: [float(train[name].min()),float(train[name].max())] for name in RISK_CONTEXT},
        "limitations": limitations, "files": {name: sha256(args.output / name)
            for name in ("eta.pkl", "risk.pkl", "evidence.json", "model_card.md")}}
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print("Bundle:", args.output, flush=True)


if __name__ == "__main__":
    main()
