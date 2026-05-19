from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ppg_stroke.baselines.ehr import cross_validate_ehr_baseline, frozen_external_evaluate
from ppg_stroke.config import ensure_dir, load_config, save_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run structured EHR baseline experiments.")
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    cfg = cfg.get("ehr_baseline", cfg)
    out_dir = ensure_dir(cfg["output_dir"])
    id_cols = cfg.get("id_cols", [])

    train_df = pd.read_csv(cfg["train_csv"])
    cv = cross_validate_ehr_baseline(
        train_df,
        label_col=str(cfg["label_col"]),
        model_name=str(cfg.get("model", "lightgbm")),
        id_cols=id_cols,
        n_splits=int(cfg.get("n_splits", 5)),
        random_state=int(cfg.get("seed", 42)),
    )
    cv.fold_metrics.to_csv(out_dir / "ehr_cv_metrics.csv", index=False)
    cv.predictions.to_csv(out_dir / "ehr_cv_predictions.csv", index=False)
    save_json({"feature_columns": cv.feature_columns}, out_dir / "ehr_feature_columns.json")

    if cfg.get("external_csv"):
        external_df = pd.read_csv(cfg["external_csv"])
        ext_metrics, ext_predictions, features = frozen_external_evaluate(
            train_df,
            external_df,
            label_col=str(cfg["label_col"]),
            model_name=str(cfg.get("model", "lightgbm")),
            id_cols=id_cols,
            threshold=None if str(cfg.get("threshold", "youden")).lower() == "youden" else float(cfg.get("threshold", 0.5)),
            random_state=int(cfg.get("seed", 42)),
        )
        ext_metrics.to_csv(out_dir / "ehr_external_metrics.csv", index=False)
        ext_predictions.to_csv(out_dir / "ehr_external_predictions.csv", index=False)
        save_json({"feature_columns": features}, out_dir / "ehr_external_feature_columns.json")

    print(f"Saved EHR baseline outputs to {out_dir}")


if __name__ == "__main__":
    main()
