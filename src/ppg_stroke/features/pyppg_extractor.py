from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ExtractionResult:
    feature_table: pd.DataFrame
    summary: dict[str, Any]


def select_ppg_channel(signal: np.ndarray, channel_names: list[str] | None = None) -> np.ndarray:
    """Select the most likely PPG/PLETH channel from a 1D or 2D signal array."""
    arr = np.asarray(signal)
    if arr.ndim == 1:
        return arr.astype(float)
    if arr.ndim != 2:
        raise ValueError(f"Expected 1D or 2D signal, got {arr.shape}")

    if channel_names:
        upper = [str(c).upper() for c in channel_names]
        for exact in ("PLETH", "PPG", "PLE"):
            if exact in upper:
                return arr[:, upper.index(exact)].astype(float)
        for i, name in enumerate(upper):
            if any(token in name for token in ("PLETH", "PPG", "PULSE", "PLE")):
                return arr[:, i].astype(float)

    variances = np.nanvar(arr, axis=0)
    return arr[:, int(np.nanargmax(variances))].astype(float)


def extract_pyppg_features(
    signal: np.ndarray,
    sampling_rate: float,
    metadata: dict[str, Any] | None = None,
) -> ExtractionResult:
    """Extract beat-level PPG morphology with pyPPG.

    The exact pyPPG API has changed across versions; this wrapper keeps all
    package-specific logic in one place and raises a clear error when pyPPG is
    unavailable.
    """
    try:
        from pyPPG import PPG
        from pyPPG.fiducials import FpCollection
        from pyPPG.preproc import Preprocess
    except ImportError as exc:
        raise RuntimeError("Install the optional `ppg` dependencies to use pyPPG extraction.") from exc

    metadata = dict(metadata or {})
    raw = np.asarray(signal, dtype=float).reshape(-1)
    raw = raw[np.isfinite(raw)]
    if raw.size < int(max(10, sampling_rate * 5)):
        return ExtractionResult(pd.DataFrame(), {"status": "too_short", **metadata})

    try:
        ppg = PPG(s=raw, fs=float(sampling_rate), check_ppg_len=False)
        prep = Preprocess(fL=0.5, fH=12, order=4, sm_wins={"ppg": 50, "vpg": 10, "apg": 10, "jpg": 10})
        ppg.ppg, ppg.vpg, ppg.apg, ppg.jpg = prep.get_signals(s=ppg)
        fiducials = FpCollection(s=ppg).get_fiducials(s=ppg)
        fp = fiducials.get_fp()
        df = pd.DataFrame(fp)
        df.insert(0, "sampling_rate", float(sampling_rate))
        for key, value in metadata.items():
            df[key] = value
        return ExtractionResult(df, {"status": "ok", "n_beats": int(len(df)), **metadata})
    except Exception as exc:
        return ExtractionResult(pd.DataFrame(), {"status": "failed", "error": str(exc), **metadata})


def write_extraction_outputs(result: ExtractionResult, feature_path: str | Path, summary_path: str | Path) -> None:
    feature_path = Path(feature_path)
    summary_path = Path(summary_path)
    feature_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    result.feature_table.to_csv(feature_path, index=False)
    pd.DataFrame([result.summary]).to_csv(summary_path, index=False)
