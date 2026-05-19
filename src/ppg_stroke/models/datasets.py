from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

from ppg_stroke.schemas import numeric_feature_frame, require_columns


def fixed_windows(
    values: np.ndarray,
    window_size: int,
    stride: int,
    drop_last: bool = False,
) -> list[np.ndarray]:
    if values.ndim != 2:
        raise ValueError(f"Expected [time,features], got {values.shape}")
    n = values.shape[0]
    if n == 0:
        return []
    if n < window_size:
        if drop_last:
            return []
        out = np.zeros((window_size, values.shape[1]), dtype=np.float32)
        out[:n] = values.astype(np.float32)
        return [out]

    starts = list(range(0, n - window_size + 1, stride))
    if starts[-1] != n - window_size:
        starts.append(n - window_size)
    return [values[s : s + window_size].astype(np.float32) for s in starts]


class WindowArrayDataset(Dataset):
    def __init__(self, x: np.ndarray, y: np.ndarray):
        if x.ndim != 3:
            raise ValueError(f"x must be [N,T,F], got {x.shape}")
        self.x = x.astype(np.float32)
        self.y = y.astype(np.int64)

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        return torch.from_numpy(self.x[idx]), torch.tensor(self.y[idx], dtype=torch.long)


def load_warning_csv_windows(
    paths: Iterable[str | Path],
    feature_cols: list[str],
    window_size: int,
    stride: int,
    label_col: str = "Label",
    group_col: str = "Group_ID",
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    x_parts: list[np.ndarray] = []
    y_parts: list[int] = []
    meta_rows: list[dict] = []

    for path in paths:
        path = Path(path)
        df = pd.read_csv(path)
        require_columns(df, [label_col, group_col], context=str(path))
        use = df[df[label_col].isin([0, 1])].copy()
        if use.empty:
            continue
        for group_id, part in use.groupby(group_col, sort=False):
            labels = part[label_col].astype(int).unique()
            if len(labels) != 1:
                raise ValueError(f"{path} group {group_id!r} contains multiple labels: {labels}")
            label = int(labels[0])
            features = numeric_feature_frame(part, feature_cols).fillna(0.0).to_numpy(dtype=np.float32)
            for w_i, window in enumerate(fixed_windows(features, window_size, stride)):
                x_parts.append(window)
                y_parts.append(label)
                meta_rows.append(
                    {
                        "source_file": str(path),
                        "group_id": str(group_id),
                        "window_index": w_i,
                        "label": label,
                    }
                )

    if not x_parts:
        raise ValueError("No windows were generated.")
    return np.stack(x_parts), np.asarray(y_parts, dtype=np.int64), pd.DataFrame(meta_rows)


def load_npz_arrays(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.load(path)
    for x_key in ("X", "x", "features"):
        if x_key in data:
            x = data[x_key]
            break
    else:
        raise KeyError("NPZ missing X/x/features array")
    for y_key in ("y", "labels", "Label"):
        if y_key in data:
            y = data[y_key]
            break
    else:
        raise KeyError("NPZ missing y/labels/Label array")
    return np.asarray(x, dtype=np.float32), np.asarray(y, dtype=np.int64)
