from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import PowerTransformer

from ppg_stroke.schemas import NOREL_FEATURES, RAW_PPG_FEATURES, RELATIVE_FEATURES, require_columns


def robust_power_transform(values: np.ndarray) -> np.ndarray:
    """Column-wise Yeo-Johnson transform used by the warning ResNet scripts."""
    x = np.asarray(values, dtype=np.float64)
    out = np.zeros_like(x, dtype=np.float64)
    for j in range(x.shape[1]):
        col = x[:, j]
        mask = np.isfinite(col)
        if mask.sum() < 3 or np.nanstd(col[mask]) < 1e-12:
            out[:, j] = 0.0
            continue
        filled = col.copy()
        filled[~mask] = np.nanmedian(col[mask])
        transformer = PowerTransformer(method="yeo-johnson", standardize=True)
        out[:, j] = transformer.fit_transform(filled.reshape(-1, 1)).reshape(-1)
    if not np.isfinite(out).all():
        raise ValueError("Non-finite values after PowerTransformer.")
    return out.astype(np.float32)


def zscore_1d(values: np.ndarray) -> np.ndarray:
    x = np.asarray(values, dtype=np.float64)
    mask = np.isfinite(x)
    if mask.sum() == 0:
        return np.zeros_like(x, dtype=np.float32)
    filled = x.copy()
    filled[~mask] = np.nanmedian(x[mask])
    sd = np.nanstd(filled)
    if sd < 1e-12:
        return np.zeros_like(filled, dtype=np.float32)
    return ((filled - np.nanmean(filled)) / sd).astype(np.float32)


def fit_linear_residual(y: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Residualize one feature against relative time, matching Step45."""
    y = np.asarray(y, dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)
    mask = np.isfinite(y) & np.isfinite(t)
    if mask.sum() < 3:
        return np.zeros_like(y, dtype=np.float32)
    coef = np.polyfit(t[mask], y[mask], deg=1)
    pred = coef[0] * t + coef[1]
    resid = y - pred
    resid[~np.isfinite(resid)] = np.nanmedian(resid[mask])
    return resid.astype(np.float32)


def build_warning_feature_matrix(df: pd.DataFrame, experiment_group: str = "Raw") -> tuple[np.ndarray, list[str]]:
    """Build warning-model feature channels from labeled beat features.

    ``experiment_group`` mirrors the Step45 rebuttal script: ``Raw``,
    ``NoREL``, ``ResidualREL`` or ``TimeOnly``.
    """
    group = experiment_group.strip()
    if group == "Raw":
        require_columns(df, RAW_PPG_FEATURES, context="warning feature table")
        return robust_power_transform(df[RAW_PPG_FEATURES].to_numpy()), list(RAW_PPG_FEATURES)
    if group == "NoREL":
        require_columns(df, NOREL_FEATURES, context="warning feature table")
        return robust_power_transform(df[NOREL_FEATURES].to_numpy()), list(NOREL_FEATURES)
    if group == "ResidualREL":
        require_columns(df, [*RELATIVE_FEATURES, "Time_Rel_Min"], context="warning feature table")
        t = pd.to_numeric(df["Time_Rel_Min"], errors="coerce").to_numpy(dtype=np.float64)
        residuals = [
            fit_linear_residual(pd.to_numeric(df[col], errors="coerce").to_numpy(dtype=np.float64), t).reshape(-1, 1)
            for col in RELATIVE_FEATURES
        ]
        x = np.concatenate(residuals, axis=1)
        return robust_power_transform(x), [f"{col}_resid" for col in RELATIVE_FEATURES]
    if group == "TimeOnly":
        require_columns(df, ["Time_Rel_Min"], context="warning feature table")
        x = zscore_1d(pd.to_numeric(df["Time_Rel_Min"], errors="coerce").to_numpy()).reshape(-1, 1)
        return x.astype(np.float32), ["Time_Rel_Min_z"]
    raise ValueError(f"Unknown experiment_group: {experiment_group}")

