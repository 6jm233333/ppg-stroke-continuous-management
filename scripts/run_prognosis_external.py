from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from ppg_stroke.config import ensure_dir, load_config, save_json
from ppg_stroke.models.aggregation import predict_sequences, sequence_metrics
from ppg_stroke.models.resnet1d import ResNet1D, load_checkpoint


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen prognosis model on external sequence manifests.")
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args()


def get_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(name)


def load_sequence(path: str | Path) -> np.ndarray:
    data = np.load(path, allow_pickle=True)
    for key in ("X", "x", "sequence", "features"):
        if key in data:
            return np.asarray(data[key], dtype=np.float32)
    raise KeyError(f"No sequence array found in {path}")


def manifest_records(
    manifest: pd.DataFrame,
    path_col: str,
    label_col: str | None,
    group_col: str | None,
    mean: np.ndarray | None = None,
    std: np.ndarray | None = None,
):
    for idx, row in manifest.iterrows():
        x = load_sequence(row[path_col])
        if mean is not None and std is not None:
            safe_std = np.where(std == 0, 1.0, std).astype(np.float32)
            x = (x - mean.astype(np.float32)) / safe_std
        record = {"x": x.astype(np.float32), "group_id": row[group_col] if group_col else idx}
        if label_col and label_col in manifest.columns:
            record["y"] = int(row[label_col])
        yield record


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    cfg = cfg.get("prognosis_external", cfg)
    out_dir = ensure_dir(cfg["output_dir"])
    device = get_device(str(cfg.get("device", "auto")))

    manifest = pd.read_csv(cfg["manifest_csv"])
    path_col = str(cfg.get("sequence_path_col", "sequence_path"))
    label_col = cfg.get("label_col", "label")
    group_col = cfg.get("group_col", "group_id")
    if path_col not in manifest.columns:
        raise ValueError(f"Manifest missing sequence path column: {path_col}")

    state = load_checkpoint(cfg["checkpoint_path"], device)
    mean = None
    std = None
    if isinstance(state, dict) and "model_state" in state:
        input_dim = int(state["input_dim"])
        output_dim = int(state.get("output_dim", 2))
        mean = np.asarray(state["mean"], dtype=np.float32) if "mean" in state else None
        std = np.asarray(state["std"], dtype=np.float32) if "std" in state else None
        state_dict = state["model_state"]
    else:
        sample = load_sequence(manifest[path_col].iloc[0])
        input_dim = int(sample.shape[1])
        output_dim = 2
        state_dict = state["state_dict"] if isinstance(state, dict) and "state_dict" in state else state

    model = ResNet1D(input_dim=input_dim, output_dim=output_dim).to(device)
    model.load_state_dict(state_dict)

    predictions = predict_sequences(
        model=model,
        records=manifest_records(
            manifest,
            path_col=path_col,
            label_col=label_col,
            group_col=group_col,
            mean=mean,
            std=std,
        ),
        device=device,
        method=str(cfg.get("aggregation", "max")),
        threshold=float(cfg.get("threshold", 0.5)),
        window_size=int(cfg.get("window_size", 2048)),
        stride=int(cfg.get("stride", 1024)),
        batch_size=int(cfg.get("batch_size", 64)),
    )
    pred_df = pd.DataFrame([p.__dict__ for p in predictions])
    pred_df.to_csv(out_dir / "prognosis_external_predictions.csv", index=False)
    save_json(sequence_metrics(predictions), out_dir / "prognosis_external_metrics.json")
    print(f"Saved prognosis external outputs to {out_dir}")


if __name__ == "__main__":
    main()
