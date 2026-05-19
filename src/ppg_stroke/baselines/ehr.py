from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler


LEAKAGE_TOKENS = (
    "label",
    "outcome",
    "stroke_time",
    "anchor",
    "future",
    "discharge",
    "death_time",
    "note",
    "text",
    "path",
)


@dataclass(frozen=True)
class EHRExperimentResult:
    fold_metrics: pd.DataFrame
    predictions: pd.DataFrame
    feature_columns: list[str]


def select_ehr_features(df: pd.DataFrame, label_col: str, id_cols: Iterable[str] = ()) -> list[str]:
    exclude = {label_col, *id_cols}
    out: list[str] = []
    for col in df.columns:
        low = col.lower()
        if col in exclude:
            continue
        if any(token in low for token in LEAKAGE_TOKENS):
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            out.append(col)
    if not out:
        raise ValueError("No numeric EHR features selected.")
    return out


def harmonized_feature_columns(
    mimic_df: pd.DataFrame,
    external_df: pd.DataFrame,
    label_col: str,
    id_cols: Iterable[str] = (),
) -> list[str]:
    """Select shared numeric clinical columns, matching the EHR prognosis script."""
    common = set(mimic_df.columns) & set(external_df.columns)
    exclude = {label_col, *id_cols}
    cols: list[str] = []
    for col in mimic_df.columns:
        low = col.lower()
        if col not in common or col in exclude:
            continue
        if any(token in low for token in LEAKAGE_TOKENS):
            continue
        if pd.api.types.is_numeric_dtype(mimic_df[col]) and pd.api.types.is_numeric_dtype(external_df[col]):
            cols.append(col)
    if not cols:
        raise ValueError("No harmonized numeric EHR features selected.")
    return cols


def build_model(model_name: str, random_state: int = 42):
    name = model_name.lower()
    if name == "randomforest":
        clf = RandomForestClassifier(
            n_estimators=500,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )
    elif name == "lightgbm":
        try:
            from lightgbm import LGBMClassifier
        except ImportError as exc:
            raise RuntimeError("Install lightgbm to use the LightGBM baseline.") from exc
        clf = LGBMClassifier(
            n_estimators=500,
            learning_rate=0.03,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
            class_weight="balanced",
            random_state=random_state,
        )
    elif name == "xgboost":
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise RuntimeError("Install xgboost to use the XGBoost baseline.") from exc
        clf = XGBClassifier(
            n_estimators=500,
            learning_rate=0.03,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=random_state,
        )
    else:
        raise ValueError(f"Unsupported model_name: {model_name}")

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),
            ("model", clf),
        ]
    )


def make_model_and_params(model_name: str, y: pd.Series, random_state: int = 42, n_jobs: int = -1):
    """Return the SMOTE pipeline and search grid used in the real EHR script."""
    try:
        from imblearn.over_sampling import SMOTE
        from imblearn.pipeline import Pipeline as ImbPipeline
    except ImportError as exc:
        raise RuntimeError("Install imbalanced-learn to reproduce the EHR baseline pipeline.") from exc

    pos = max(int((y == 1).sum()), 1)
    neg = max(int((y == 0).sum()), 1)
    scale_pos_weight = neg / pos
    name = model_name.lower()

    if name == "lightgbm":
        try:
            from lightgbm import LGBMClassifier
        except ImportError as exc:
            raise RuntimeError("Install lightgbm to use the LightGBM baseline.") from exc
        clf = LGBMClassifier(
            objective="binary",
            metric="auc",
            random_state=random_state,
            class_weight="balanced",
            n_jobs=n_jobs,
            verbosity=-1,
        )
        params = {
            "classifier__n_estimators": [150, 250, 350],
            "classifier__learning_rate": [0.01, 0.03, 0.05, 0.08],
            "classifier__num_leaves": [15, 31, 63],
            "classifier__max_depth": [-1, 3, 5, 7],
            "classifier__subsample": [0.7, 0.85, 1.0],
            "classifier__colsample_bytree": [0.7, 0.85, 1.0],
            "classifier__reg_alpha": [0, 0.1, 1.0],
            "classifier__reg_lambda": [0.1, 1.0, 5.0],
        }
    elif name == "xgboost":
        try:
            from xgboost import XGBClassifier
        except ImportError as exc:
            raise RuntimeError("Install xgboost to use the XGBoost baseline.") from exc
        clf = XGBClassifier(
            objective="binary:logistic",
            eval_metric="auc",
            random_state=random_state,
            tree_method="hist",
            scale_pos_weight=scale_pos_weight,
            n_jobs=n_jobs,
            verbosity=0,
        )
        params = {
            "classifier__n_estimators": [150, 250, 350],
            "classifier__learning_rate": [0.01, 0.03, 0.05, 0.08],
            "classifier__max_depth": [2, 3, 4, 5],
            "classifier__min_child_weight": [1, 3, 5],
            "classifier__subsample": [0.7, 0.85, 1.0],
            "classifier__colsample_bytree": [0.7, 0.85, 1.0],
            "classifier__reg_alpha": [0, 0.1, 1.0],
            "classifier__reg_lambda": [1.0, 5.0, 10.0],
        }
    elif name == "randomforest":
        clf = RandomForestClassifier(random_state=random_state, class_weight="balanced", n_jobs=n_jobs)
        params = {
            "classifier__n_estimators": [300, 500, 700],
            "classifier__max_depth": [None, 4, 6, 8, 10],
            "classifier__min_samples_split": [2, 5, 10],
            "classifier__min_samples_leaf": [1, 2, 4],
            "classifier__max_features": ["sqrt", "log2", 0.5],
        }
    else:
        raise ValueError(f"Unsupported model_name: {model_name}")

    pipeline = ImbPipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),
            ("smote", SMOTE(random_state=random_state, k_neighbors=5)),
            ("classifier", clf),
        ]
    )
    return pipeline, params


def best_threshold_youden(y_true, y_prob) -> float:
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    idx = int(np.argmax(tpr - fpr))
    return float(thresholds[idx])


def _binary_metric_row(y_true, y_prob, threshold: float, **extra) -> dict:
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    row = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "specificity": float(tn / (tn + fp)) if (tn + fp) else np.nan,
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "threshold": float(threshold),
        "brier": float(brier_score_loss(y_true, y_prob)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }
    if len(np.unique(y_true)) == 2:
        row["auc"] = float(roc_auc_score(y_true, y_prob))
        row["auprc"] = float(average_precision_score(y_true, y_prob))
    else:
        row["auc"] = np.nan
        row["auprc"] = np.nan
    row.update(extra)
    return row


def train_best_model(
    df: pd.DataFrame,
    label_col: str,
    model_name: str,
    feature_columns: list[str] | None = None,
    id_cols: Iterable[str] = (),
    n_splits: int = 5,
    n_iter: int = 30,
    random_state: int = 42,
):
    features = feature_columns or select_ehr_features(df, label_col=label_col, id_cols=id_cols)
    x = df[features]
    y = df[label_col].astype(int)
    pipeline, params = make_model_and_params(model_name, y, random_state=random_state)
    search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=params,
        n_iter=n_iter,
        scoring="roc_auc",
        cv=StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state),
        random_state=random_state,
        n_jobs=1,
        verbose=0,
    )
    search.fit(x, y)
    return search.best_estimator_, float(search.best_score_), features, search.best_params_


def cross_validate_ehr_baseline(
    df: pd.DataFrame,
    label_col: str,
    model_name: str,
    id_cols: Iterable[str] = (),
    n_splits: int = 5,
    random_state: int = 42,
) -> EHRExperimentResult:
    features = select_ehr_features(df, label_col=label_col, id_cols=id_cols)
    x = df[features]
    y = df[label_col].astype(int).to_numpy()
    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    metrics: list[dict] = []
    pred_rows: list[dict] = []
    for fold, (train_idx, test_idx) in enumerate(splitter.split(x, y), start=1):
        model = build_model(model_name, random_state=random_state + fold)
        model.fit(x.iloc[train_idx], y[train_idx])
        prob = model.predict_proba(x.iloc[test_idx])[:, 1]
        metrics.append(_binary_metric_row(y[test_idx], prob, 0.5, fold=fold, model=model_name))
        for row_idx, yt, yp in zip(test_idx, y[test_idx], prob):
            pred_rows.append({"row_index": int(row_idx), "fold": fold, "y_true": int(yt), "y_prob": float(yp)})

    return EHRExperimentResult(pd.DataFrame(metrics), pd.DataFrame(pred_rows), features)


def frozen_external_evaluate(
    train_df: pd.DataFrame,
    external_df: pd.DataFrame,
    label_col: str,
    model_name: str,
    id_cols: Iterable[str] = (),
    threshold: float | None = 0.5,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    features = harmonized_feature_columns(train_df, external_df, label_col=label_col, id_cols=id_cols)
    model, _, features, _ = train_best_model(
        train_df,
        label_col=label_col,
        model_name=model_name,
        feature_columns=features,
        id_cols=id_cols,
        random_state=random_state,
    )
    train_prob = model.predict_proba(train_df[features])[:, 1]
    threshold = best_threshold_youden(train_df[label_col].astype(int), train_prob) if threshold is None else threshold
    y_ext = external_df[label_col].astype(int).to_numpy()
    prob = model.predict_proba(external_df[features])[:, 1]
    metrics = pd.DataFrame([_binary_metric_row(y_ext, prob, threshold, model=model_name, dataset="external")])
    preds = pd.DataFrame({"y_true": y_ext, "y_prob": prob, "y_pred": (prob >= threshold).astype(int)})
    return metrics, preds, features
