from __future__ import annotations

import random
from dataclasses import asdict, dataclass

import numpy as np
import torch
import torch.nn as nn
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, fbeta_score, precision_score, recall_score, roc_auc_score
from torch.utils.data import DataLoader

from ppg_stroke.models.resnet1d import ResNet1D


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


@dataclass
class BinaryMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    f2: float
    auc: float | None
    specificity: float
    tn: int
    fp: int
    fn: int
    tp: int

    def to_dict(self) -> dict:
        return asdict(self)


def compute_binary_metrics(y_true, y_prob, threshold: float = 0.5) -> BinaryMetrics:
    y_true = np.asarray(y_true, dtype=int)
    y_prob = np.asarray(y_prob, dtype=float)
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    auc = None
    if len(np.unique(y_true)) == 2:
        auc = float(roc_auc_score(y_true, y_prob))
    return BinaryMetrics(
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision=float(precision_score(y_true, y_pred, zero_division=0)),
        recall=float(recall_score(y_true, y_pred, zero_division=0)),
        f1=float(f1_score(y_true, y_pred, zero_division=0)),
        f2=float(fbeta_score(y_true, y_pred, beta=2, zero_division=0)),
        auc=auc,
        specificity=float(tn / (tn + fp)) if (tn + fp) else 0.0,
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
    )


def predict_probabilities(model: nn.Module, loader: DataLoader, device: torch.device) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    probs: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            logits = model(x)
            p = torch.softmax(logits, dim=1)[:, 1]
            probs.append(p.detach().cpu().numpy())
            labels.append(y.detach().cpu().numpy())
    return np.concatenate(labels), np.concatenate(probs)


def choose_threshold_by_f1(y_true, y_prob, grid: np.ndarray | None = None) -> float:
    if grid is None:
        grid = np.linspace(0.05, 0.95, 181)
    best_thr = 0.5
    best_f1 = -1.0
    for thr in grid:
        score = f1_score(y_true, np.asarray(y_prob) >= thr, zero_division=0)
        if score > best_f1:
            best_f1 = float(score)
            best_thr = float(thr)
    return best_thr


def build_threshold_candidates(start: float = 0.50, end: float = 1.00, step: float = 0.01) -> np.ndarray:
    arr = np.arange(start, end + step / 2.0, step)
    arr = np.round(arr, 4)
    return arr[(arr >= start) & (arr <= end)]


def threshold_sweep(y_true, y_prob, thresholds: np.ndarray) -> pd.DataFrame:
    rows = []
    for thr in thresholds:
        rows.append({"threshold": float(thr), **compute_binary_metrics(y_true, y_prob, float(thr)).to_dict()})
    return pd.DataFrame(rows)


def choose_best_threshold(
    y_true,
    y_prob,
    primary_metric: str = "f2",
    thresholds: np.ndarray | None = None,
) -> tuple[float, dict]:
    thresholds = thresholds if thresholds is not None else build_threshold_candidates()
    sweep = threshold_sweep(y_true, y_prob, thresholds)
    metric_col = primary_metric.lower()
    if metric_col not in sweep.columns:
        metric_col = "f2"
    ranked = sweep.sort_values(
        by=[metric_col, "f1", "recall", "auc", "threshold"],
        ascending=[False, False, False, False, False],
        na_position="last",
    ).reset_index(drop=True)
    best = ranked.iloc[0].to_dict()
    return float(best["threshold"]), best


def train_resnet1d(
    train_loader: DataLoader,
    val_loader: DataLoader,
    input_dim: int,
    device: torch.device,
    epochs: int = 100,
    learning_rate: float = 1e-3,
    weight_decay: float = 1e-4,
    positive_weight: float = 1.0,
    patience: int = 20,
    primary_metric: str = "f2",
    threshold_start: float = 0.50,
    threshold_end: float = 1.00,
    threshold_step: float = 0.01,
) -> tuple[ResNet1D, dict]:
    model = ResNet1D(input_dim=input_dim, output_dim=2).to(device)
    weights = torch.tensor([1.0, float(positive_weight)], dtype=torch.float32, device=device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)

    best_state = None
    thresholds = build_threshold_candidates(threshold_start, threshold_end, threshold_step)
    best_auc = -1.0
    best_primary = -1.0
    best_threshold = 0.5
    best_epoch = -1
    stale = 0
    history: list[dict] = []

    for epoch in range(1, epochs + 1):
        model.train()
        losses = []
        for x, y in train_loader:
            x = x.to(device)
            y = y.to(device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            losses.append(float(loss.item()))

        y_val, p_val = predict_probabilities(model, val_loader, device)
        thr, best_row = choose_best_threshold(y_val, p_val, primary_metric=primary_metric, thresholds=thresholds)
        metrics = compute_binary_metrics(y_val, p_val, threshold=thr)
        row = {"epoch": epoch, "loss": float(np.mean(losses)), "threshold": thr, **metrics.to_dict()}
        history.append(row)

        val_auc = -1.0 if metrics.auc is None or np.isnan(metrics.auc) else float(metrics.auc)
        val_primary = float(best_row.get(primary_metric.lower(), best_row.get("f2", metrics.f2)))
        if val_auc > best_auc or (np.isclose(val_auc, best_auc) and val_primary > best_primary):
            best_auc = val_auc
            best_primary = val_primary
            best_threshold = thr
            best_epoch = epoch
            stale = 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            stale += 1
        if stale >= patience:
            break

    if best_state is None:
        raise RuntimeError("Training produced no best state.")
    model.load_state_dict(best_state)
    metadata = {
        "best_epoch": best_epoch,
        "best_val_auc": best_auc,
        f"best_val_{primary_metric.lower()}": best_primary,
        "selected_threshold": best_threshold,
        "history": history,
    }
    return model, metadata
