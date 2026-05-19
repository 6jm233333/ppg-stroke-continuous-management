from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ppg_stroke.features.pyppg_extractor import extract_pyppg_features, select_ppg_channel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract PyPPG morphology features from a signal manifest.")
    parser.add_argument("--manifest-csv", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--signal-path-col", default="signal_path")
    parser.add_argument("--sampling-rate-col", default="sampling_rate")
    parser.add_argument("--value-col", default=None, help="Optional CSV column containing the PPG signal.")
    return parser.parse_args()


def load_signal(path: str | Path, value_col: str | None = None) -> tuple[np.ndarray, list[str] | None]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".npy":
        return np.load(path), None
    if suffix == ".npz":
        data = np.load(path, allow_pickle=True)
        for key in ("ppg", "signal", "x", "X", "values"):
            if key in data:
                return np.asarray(data[key]), None
        raise KeyError(f"No signal array found in {path}")
    if suffix == ".csv":
        df = pd.read_csv(path)
        if value_col:
            if value_col not in df.columns:
                raise ValueError(f"{path} missing value column: {value_col}")
            return df[value_col].to_numpy(), [value_col]
        numeric = df.select_dtypes(include=[np.number])
        if numeric.empty:
            raise ValueError(f"No numeric signal columns found in {path}")
        return numeric.to_numpy(), list(numeric.columns)
    raise ValueError(f"Unsupported signal file type: {path.suffix}")


def main() -> None:
    args = parse_args()
    manifest = pd.read_csv(args.manifest_csv)
    for col in (args.signal_path_col, args.sampling_rate_col):
        if col not in manifest.columns:
            raise ValueError(f"Manifest missing required column: {col}")

    feature_dir = args.output_dir / "features"
    summary_dir = args.output_dir / "summaries"
    feature_dir.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict] = []

    for idx, row in manifest.iterrows():
        signal, channel_names = load_signal(row[args.signal_path_col], value_col=args.value_col)
        ppg = select_ppg_channel(signal, channel_names=channel_names)
        metadata = {k: row[k] for k in manifest.columns if k not in {args.signal_path_col}}
        metadata["row_index"] = int(idx)
        result = extract_pyppg_features(ppg, sampling_rate=float(row[args.sampling_rate_col]), metadata=metadata)
        raw_stem = str(row.get("record_id", idx))
        stem = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in raw_stem)
        feature_path = feature_dir / f"{stem}.csv"
        result.feature_table.to_csv(feature_path, index=False)
        summary = {"feature_path": str(feature_path), **result.summary}
        pd.DataFrame([summary]).to_csv(summary_dir / f"{stem}.summary.csv", index=False)
        summaries.append(summary)

    pd.DataFrame(summaries).to_csv(args.output_dir / "extraction_summary.csv", index=False)
    print(f"Saved PPG feature extraction outputs to {args.output_dir}")


if __name__ == "__main__":
    main()
