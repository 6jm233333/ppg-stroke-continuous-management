from __future__ import annotations

import argparse
from pathlib import Path

from ppg_stroke.reporting.extended_data_fig import write_nature_extended_data_figure


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the diagnostic falsification Extended Data figure.")
    parser.add_argument("--plot-data-csv", required=True, type=Path)
    parser.add_argument("--out-base", required=True, type=Path, help="Output path without extension.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    write_nature_extended_data_figure(args.plot_data_csv, args.out_base)
    print(f"Saved figure files next to {args.out_base}")


if __name__ == "__main__":
    main()

