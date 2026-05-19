from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from ppg_stroke.models.datasets import WindowArrayDataset, fixed_windows
from ppg_stroke.models.resnet1d import ResNet1D, load_checkpoint
from ppg_stroke.schemas import RAW_PPG_FEATURES, numeric_feature_frame, require_columns


def load_frozen_model(checkpoint_path: str | Path, input_dim: int, device: torch.device) -> ResNet1D:
    model = ResNet1D(input_dim=input_dim, output_dim=2).to(device)
    state = load_checkpoint(str(checkpoint_path), device)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    if isinstance(state, dict) and "model_state" in state:
        state = state["model_state"]
    model.load_state_dict(state)
    model.eval()
    return model


def load_power_transformer(path: str | Path | None) -> Any | None:
    if not path:
        return None
    with Path(path).open("rb") as handle:
        payload = pickle.load(handle)
    return payload["transformer"] if isinstance(payload, dict) and "transformer" in payload else payload


def prepare_manifest_window(
    feature_path: str | Path,
    feature_cols: list[str],
    row_start: int | None = None,
    row_end_excl: int | None = None,
    transformer: Any | None = None,
) -> np.ndarray:
    raw = pd.read_csv(feature_path)
    require_columns(raw, feature_cols, context=str(feature_path))
    if row_start is not None and row_end_excl is not None:
        raw = raw.iloc[int(row_start) : int(row_end_excl)].copy()
    for col in feature_cols:
        raw[col] = pd.to_numeric(raw[col], errors="coerce")
    raw = raw.dropna(subset=feature_cols)
    x = raw[feature_cols].to_numpy(dtype=np.float64)
    if transformer is not None:
        x = transformer.transform(x)
    return x.astype(np.float32)


def predict_feature_csv(
    feature_path: str | Path,
    checkpoint_path: str | Path,
    feature_cols: list[str] | None = None,
    window_size: int = 500,
    stride: int = 500,
    batch_size: int = 128,
    device: str = "cpu",
    row_start: int | None = None,
    row_end_excl: int | None = None,
    transformer_path: str | Path | None = None,
) -> float:
    feature_cols = feature_cols or RAW_PPG_FEATURES
    transformer = load_power_transformer(transformer_path)
    x2d = prepare_manifest_window(
        feature_path,
        feature_cols=feature_cols,
        row_start=row_start,
        row_end_excl=row_end_excl,
        transformer=transformer,
    )
    if row_start is not None and row_end_excl is not None:
        if len(x2d) != window_size:
            raise ValueError(f"Manifest window length {len(x2d)} does not equal expected {window_size}.")
        windows = [x2d]
    else:
        windows = fixed_windows(x2d, window_size=window_size, stride=stride)
    if not windows:
        return float("nan")

    x = np.stack(windows)
    y = np.zeros(len(x), dtype=np.int64)
    dev = torch.device(device if device == "cpu" or torch.cuda.is_available() else "cpu")
    model = load_frozen_model(checkpoint_path, input_dim=len(feature_cols), device=dev)
    loader = DataLoader(WindowArrayDataset(x, y), batch_size=batch_size, shuffle=False)
    probs: list[np.ndarray] = []
    with torch.no_grad():
        for bx, _ in loader:
            logits = model(bx.to(dev))
            probs.append(torch.softmax(logits, dim=1)[:, 1].detach().cpu().numpy())
    return float(np.mean(np.concatenate(probs)))


def infer_anchor_manifest(
    manifest_path: str | Path,
    output_path: str | Path,
    feature_path_col: str = "feature_path",
    checkpoint_col: str = "model_checkpoint",
    transformer_path_col: str | None = "preprocessing_artifact",
    device: str = "cpu",
) -> pd.DataFrame:
    manifest = pd.read_csv(manifest_path)
    require_columns(manifest, [feature_path_col, checkpoint_col], context=str(manifest_path))
    rows = []
    for _, row in manifest.iterrows():
        status = "ok"
        try:
            transformer_path = None
            if transformer_path_col and transformer_path_col in manifest.columns and pd.notna(row[transformer_path_col]):
                transformer_path = row[transformer_path_col]
            row_start = int(row["row_start"]) if "row_start" in manifest.columns and pd.notna(row["row_start"]) else None
            row_end = (
                int(row["row_end_excl"])
                if "row_end_excl" in manifest.columns and pd.notna(row["row_end_excl"])
                else None
            )
            prob = predict_feature_csv(
                row[feature_path_col],
                row[checkpoint_col],
                device=device,
                row_start=row_start,
                row_end_excl=row_end,
                transformer_path=transformer_path,
            )
        except Exception as exc:
            prob = np.nan
            status = f"failed: {exc}"
        threshold = float(row["threshold"]) if "threshold" in manifest.columns and pd.notna(row["threshold"]) else np.nan
        false_warning = int(prob >= threshold) if pd.notna(prob) and pd.notna(threshold) else np.nan
        rows.append({**row.to_dict(), "y_prob": prob, "threshold": threshold, "false_warning": false_warning, "inference_status": status})

    out = pd.DataFrame(rows)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    return out


def permutation_from_pseudo(pseudo_predictions: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Create a diagnostic patient-owner permutation from pseudo-anchor predictions."""
    out = pseudo_predictions.copy()
    if "patient_uid" in out.columns:
        rng = np.random.default_rng(seed)
        owners = out["patient_uid"].astype(str).to_numpy()
        out["permuted_patient_uid"] = rng.permutation(owners)
    out["analysis_type"] = "permutation_anchor"
    out["permutation_definition"] = (
        "patient-level permutation of pseudo-anchor ownership; probabilities unchanged; "
        "diagnostic falsification only"
    )
    return out


def summarize_anchor_predictions(df: pd.DataFrame, group_cols: list[str] | None = None) -> pd.DataFrame:
    group_cols = group_cols or ["analysis_type", "horizon"]
    use = df.dropna(subset=["y_prob"]).copy()
    if use.empty:
        return pd.DataFrame()
    return (
        use.groupby(group_cols, dropna=False)
        .agg(
            n_windows=("y_prob", "size"),
            mean_warning_probability=("y_prob", "mean"),
            median_warning_probability=("y_prob", "median"),
            proportion_ge_0_5=("y_prob", lambda x: float(np.mean(np.asarray(x) >= 0.5))),
        )
        .reset_index()
    )
