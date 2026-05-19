from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader

from ppg_stroke.config import ensure_dir, load_config, save_json
from ppg_stroke.models.datasets import WindowArrayDataset, load_npz_arrays
from ppg_stroke.models.train_eval import (
    build_threshold_candidates,
    choose_best_threshold,
    compute_binary_metrics,
    predict_probabilities,
    seed_everything,
    train_resnet1d,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the internal PPG warning ResNet model.")
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args()


def get_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(name)


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    cfg = cfg.get("warning_training", cfg)

    seed_everything(int(cfg.get("seed", 42)))
    out_dir = ensure_dir(cfg["output_dir"])
    device = get_device(str(cfg.get("device", "auto")))

    x_train, y_train = load_npz_arrays(cfg["train_npz"])
    x_val, y_val = load_npz_arrays(cfg["val_npz"])
    train_loader = DataLoader(
        WindowArrayDataset(x_train, y_train),
        batch_size=int(cfg.get("batch_size", 64)),
        shuffle=True,
        num_workers=int(cfg.get("num_workers", 0)),
    )
    val_loader = DataLoader(
        WindowArrayDataset(x_val, y_val),
        batch_size=int(cfg.get("batch_size", 64)),
        shuffle=False,
        num_workers=int(cfg.get("num_workers", 0)),
    )

    model, metadata = train_resnet1d(
        train_loader=train_loader,
        val_loader=val_loader,
        input_dim=int(x_train.shape[2]),
        device=device,
        epochs=int(cfg.get("epochs", 100)),
        learning_rate=float(cfg.get("learning_rate", 1e-3)),
        weight_decay=float(cfg.get("weight_decay", 1e-4)),
        positive_weight=float(cfg.get("positive_weight", 1.0)),
        patience=int(cfg.get("patience", 20)),
        primary_metric=str(cfg.get("primary_metric", "f2")),
        threshold_start=float(cfg.get("threshold_start", 0.50)),
        threshold_end=float(cfg.get("threshold_end", 1.00)),
        threshold_step=float(cfg.get("threshold_step", 0.01)),
    )

    y_val_eval, p_val = predict_probabilities(model, val_loader, device)
    threshold, _ = choose_best_threshold(
        y_val_eval,
        p_val,
        primary_metric=str(cfg.get("primary_metric", "f2")),
        thresholds=build_threshold_candidates(
            float(cfg.get("threshold_start", 0.50)),
            float(cfg.get("threshold_end", 1.00)),
            float(cfg.get("threshold_step", 0.01)),
        ),
    )
    val_metrics = compute_binary_metrics(y_val_eval, p_val, threshold=threshold).to_dict()
    val_metrics["threshold"] = threshold

    torch.save(model.state_dict(), out_dir / "warning_resnet_state_dict.pt")
    pd.DataFrame(metadata["history"]).to_csv(out_dir / "training_history.csv", index=False)
    pd.DataFrame({"y_true": y_val_eval, "y_prob": p_val, "y_pred": (p_val >= threshold).astype(int)}).to_csv(
        out_dir / "validation_predictions.csv", index=False
    )
    save_json({"training": {k: v for k, v in metadata.items() if k != "history"}, "validation": val_metrics}, out_dir / "metrics.json")

    if "test_npz" in cfg and cfg["test_npz"]:
        x_test, y_test = load_npz_arrays(cfg["test_npz"])
        test_loader = DataLoader(WindowArrayDataset(x_test, y_test), batch_size=int(cfg.get("batch_size", 64)), shuffle=False)
        y_test_eval, p_test = predict_probabilities(model, test_loader, device)
        test_metrics = compute_binary_metrics(y_test_eval, p_test, threshold=threshold).to_dict()
        pd.DataFrame({"y_true": y_test_eval, "y_prob": p_test, "y_pred": (p_test >= threshold).astype(int)}).to_csv(
            out_dir / "test_predictions.csv", index=False
        )
        save_json({"threshold": threshold, "test": test_metrics}, out_dir / "test_metrics.json")

    print(f"Saved warning model outputs to {out_dir}")


if __name__ == "__main__":
    main()
