from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ppg_stroke.features.windowing import apply_warning_labels, rebuild_time_axis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild stroke-warning labels relative to recognition anchors.")
    parser.add_argument("--input-csv", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--horizon-min", required=True, type=int, choices=(240, 300, 360))
    parser.add_argument("--time-col", default="Time_Rel_Min")
    parser.add_argument("--rebuild-time-axis", action="store_true")
    parser.add_argument("--group-col", default="Source_File")
    parser.add_argument("--beat-col", default="Beat_Idx")
    parser.add_argument("--wave-start-col", default="Wave_Start")
    parser.add_argument("--wave-end-col", default="Wave_End")
    parser.add_argument("--anchor-col", default="Actual_Stroke_Time")
    parser.add_argument("--stable-lookback-min", type=int, default=480)
    parser.add_argument("--transition-buffer-min", type=int, default=15)
    parser.add_argument("--blind-zone-min", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input_csv)
    if args.rebuild_time_axis:
        df = rebuild_time_axis(
            df,
            group_col=args.group_col,
            beat_col=args.beat_col,
            wave_start_col=args.wave_start_col,
            wave_end_col=args.wave_end_col,
            anchor_col=args.anchor_col,
        )
    if args.time_col not in df.columns:
        raise ValueError(f"Missing relative-time column: {args.time_col}")

    out = apply_warning_labels(
        df,
        horizon_min=args.horizon_min,
        time_col=args.time_col,
        stable_lookback_min=args.stable_lookback_min,
        transition_buffer_min=args.transition_buffer_min,
        blind_zone_min=args.blind_zone_min,
    )
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output_csv, index=False)
    print(out["Label"].value_counts(dropna=False).sort_index().to_string())


if __name__ == "__main__":
    main()
