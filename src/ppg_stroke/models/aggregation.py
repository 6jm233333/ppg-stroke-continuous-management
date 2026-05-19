from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


def parse_aggregation_method(method: str) -> tuple[str, int | None]:
    """Parse aggregation names used in the prognosis experiments.

    Supported values are ``max``, ``mean`` and ``consecutive_k`` where
    ``k`` is the minimum number of consecutive positive windows required
    to call a patient positive.
    """
    method = method.lower().strip()
    if method in {"max", "mean"}:
        return method, None
    if method.startswith("consecutive_k"):
        try:
            k = int(method.replace("consecutive_k", ""))
        except ValueError as exc:
            raise ValueError(f"Invalid consecutive aggregation method: {method}") from exc
        if k <= 0:
            raise ValueError("consecutive_k requires k > 0")
        return "consecutive", k
    if method.startswith("consecutive_"):
        try:
            k = int(method.rsplit("_", 1)[1])
        except ValueError as exc:
            raise ValueError(f"Invalid consecutive aggregation method: {method}") from exc
        if k <= 0:
            raise ValueError("consecutive_k requires k > 0")
        return "consecutive", k
    raise ValueError(f"Unsupported aggregation method: {method}")


def max_consecutive_true(mask: Iterable[bool]) -> int:
    best = 0
    current = 0
    for value in mask:
        if bool(value):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def aggregate_window_probabilities(
    probabilities: np.ndarray,
    method: str = "max",
    threshold: float = 0.5,
) -> tuple[float, int]:
    """Aggregate window-level probabilities into one sequence score.

    Returns ``(score, predicted_label)``. For ``consecutive_k``, the score is
    the longest run of windows with probability at least 0.5 divided by k,
    matching the executable external-test script. The predicted label uses
    the supplied threshold.
    """
    probabilities = np.asarray(probabilities, dtype=float)
    probabilities = probabilities[np.isfinite(probabilities)]
    if probabilities.size == 0:
        return float("nan"), 0

    mode, k = parse_aggregation_method(method)
    if mode == "max":
        score = float(np.max(probabilities))
        return score, int(score >= threshold)
    if mode == "mean":
        score = float(np.mean(probabilities))
        return score, int(score >= threshold)

    assert k is not None
    score_run = max_consecutive_true(probabilities >= 0.5)
    pred_run = max_consecutive_true(probabilities >= threshold)
    return float(score_run / float(k)), int(pred_run >= k)


@dataclass(frozen=True)
class SequencePrediction:
    group_id: str
    y_true: int | None
    y_score: float
    y_pred: int
    n_windows: int


def predict_sequence_windows(
    model: Any,
    sequence: np.ndarray,
    device: Any,
    window_size: int = 2048,
    stride: int = 1024,
    batch_size: int = 64,
) -> np.ndarray:
    """Run a sequence through a frozen model using fixed sliding windows."""
    import torch

    from ppg_stroke.models.datasets import fixed_windows

    windows = fixed_windows(np.asarray(sequence, dtype=np.float32), window_size=window_size, stride=stride)
    if not windows:
        return np.asarray([], dtype=float)

    model.eval()
    probs: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(windows), batch_size):
            batch = torch.from_numpy(np.stack(windows[start : start + batch_size])).to(device)
            logits = model(batch)
            probs.append(torch.softmax(logits, dim=1)[:, 1].detach().cpu().numpy())
    return np.concatenate(probs)


def predict_sequences(
    model: Any,
    records: Iterable[dict],
    device: Any,
    method: str = "max",
    threshold: float = 0.5,
    window_size: int = 2048,
    stride: int = 1024,
    batch_size: int = 64,
) -> list[SequencePrediction]:
    """Predict patient- or stay-level outcomes from iterable sequence records.

    Each record must contain ``x`` as a [time, feature] array. Optional keys:
    ``group_id`` and ``y``.
    """
    out: list[SequencePrediction] = []
    for i, record in enumerate(records):
        probs = predict_sequence_windows(
            model=model,
            sequence=np.asarray(record["x"], dtype=np.float32),
            device=device,
            window_size=window_size,
            stride=stride,
            batch_size=batch_size,
        )
        score, pred = aggregate_window_probabilities(probs, method=method, threshold=threshold)
        y = record.get("y")
        out.append(
            SequencePrediction(
                group_id=str(record.get("group_id", i)),
                y_true=None if y is None else int(y),
                y_score=score,
                y_pred=pred,
                n_windows=int(len(probs)),
            )
        )
    return out


def sequence_metrics(predictions: Iterable[SequencePrediction]) -> dict:
    rows = [p for p in predictions if p.y_true is not None and np.isfinite(p.y_score)]
    if not rows:
        return {}
    y_true = np.asarray([p.y_true for p in rows], dtype=int)
    y_pred = np.asarray([p.y_pred for p in rows], dtype=int)
    y_score = np.asarray([p.y_score for p in rows], dtype=float)
    metrics = {
        "n_sequences": int(len(rows)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    metrics["auc"] = float(roc_auc_score(y_true, y_score)) if len(np.unique(y_true)) == 2 else np.nan
    return metrics
