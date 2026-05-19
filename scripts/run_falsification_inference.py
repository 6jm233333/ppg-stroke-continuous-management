from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ppg_stroke.config import ensure_dir, load_config
from ppg_stroke.falsification.frozen_inference import (
    infer_anchor_manifest,
    permutation_from_pseudo,
    summarize_anchor_predictions,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen-model pseudo/permutation anchor falsification.")
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    cfg = cfg.get("falsification", cfg)
    out_dir = ensure_dir(cfg["output_dir"])
    pred_path = out_dir / "falsification_predictions.csv"

    predictions = infer_anchor_manifest(
        manifest_path=cfg["manifest_csv"],
        output_path=pred_path,
        feature_path_col=str(cfg.get("feature_path_col", "feature_path")),
        checkpoint_col=str(cfg.get("checkpoint_col", "model_checkpoint")),
        transformer_path_col=cfg.get("transformer_path_col", "preprocessing_artifact"),
        device=str(cfg.get("device", "cpu")),
    )
    summarize_anchor_predictions(predictions).to_csv(out_dir / "falsification_summary.csv", index=False)

    if bool(cfg.get("write_permutation_anchor", True)):
        permuted = permutation_from_pseudo(predictions, seed=int(cfg.get("seed", 42)))
        permuted.to_csv(out_dir / "permutation_anchor_predictions.csv", index=False)
        combined = pd.concat([predictions, permuted], ignore_index=True)
        summarize_anchor_predictions(combined).to_csv(out_dir / "falsification_with_permutation_summary.csv", index=False)

    print(f"Saved falsification outputs to {out_dir}")


if __name__ == "__main__":
    main()
