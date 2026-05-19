from __future__ import annotations

import numpy as np
import pandas as pd


def assign_warning_label(
    time_rel_min: float,
    horizon_min: int,
    stable_lookback_min: int = 480,
    transition_buffer_min: int = 15,
    blind_zone_min: int = 0,
) -> int:
    """Assign warning labels relative to clinical recognition time.

    Label definitions:
    - 1: warning window, from ``-horizon + transition_buffer`` to the
      clinical recognition anchor. This matches the executable Step6 logic;
      the earlier ``BUFFER_0`` constant was defined but not applied there.
    - 0: earlier stable window, from ``-stable_lookback`` to
      ``-horizon - transition_buffer``.
    - -1: excluded transition, post-anchor, blind-zone, or out-of-range sample.

    This mirrors the manuscript logic: ambiguous transition regions and
    near-anchor physiology are excluded rather than forced into a class.
    """
    if pd.isna(time_rel_min):
        return -1
    t = float(time_rel_min)
    if t < -float(stable_lookback_min):
        return -1
    upper_exclusion = -float(blind_zone_min) if blind_zone_min > 0 else 0.0
    if t >= upper_exclusion:
        return -1
    if (-horizon_min - transition_buffer_min) < t < (-horizon_min + transition_buffer_min):
        return -1
    if (-horizon_min + transition_buffer_min) <= t < upper_exclusion:
        return 1
    if -stable_lookback_min <= t <= (-horizon_min - transition_buffer_min):
        return 0
    return -1


def rebuild_time_axis(
    df: pd.DataFrame,
    group_col: str = "Source_File",
    beat_col: str = "Beat_Idx",
    wave_start_col: str = "Wave_Start",
    wave_end_col: str = "Wave_End",
    anchor_col: str = "Actual_Stroke_Time",
) -> pd.DataFrame:
    """Reconstruct per-waveform absolute and relative beat times.

    Each waveform file is handled independently so merged feature tables do
    not borrow timing anchors across files.
    """
    required = [group_col, wave_start_col, wave_end_col, anchor_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required timing columns: {missing}")

    parts: list[pd.DataFrame] = []
    for _, group in df.groupby(group_col, sort=False):
        g = group.copy()
        start = pd.to_datetime(g[wave_start_col].iloc[0], errors="coerce")
        end = pd.to_datetime(g[wave_end_col].iloc[0], errors="coerce")
        anchor = pd.to_datetime(g[anchor_col].iloc[0], errors="coerce")
        if pd.isna(start) or pd.isna(end) or pd.isna(anchor):
            continue

        if beat_col in g.columns:
            g[beat_col] = pd.to_numeric(g[beat_col], errors="coerce")
            g = g.sort_values(beat_col, kind="mergesort")
        else:
            g = g.reset_index(drop=True)

        n = len(g)
        if n == 0:
            continue
        if n == 1 or end <= start:
            abs_times = start + pd.to_timedelta(np.arange(n), unit="s")
        else:
            abs_times = pd.date_range(start=start, end=end, periods=n)

        g["Absolute_Time"] = pd.to_datetime(abs_times)
        g["Time_Rel_Min"] = (g["Absolute_Time"] - anchor).dt.total_seconds() / 60.0
        parts.append(g)

    if not parts:
        return pd.DataFrame(columns=list(df.columns) + ["Absolute_Time", "Time_Rel_Min"])
    return pd.concat(parts, ignore_index=True)


def apply_warning_labels(
    df: pd.DataFrame,
    horizon_min: int,
    time_col: str = "Time_Rel_Min",
    **label_kwargs,
) -> pd.DataFrame:
    out = df.copy()
    out["Label"] = out[time_col].map(
        lambda x: assign_warning_label(float(x), horizon_min=horizon_min, **label_kwargs)
    )
    return out
