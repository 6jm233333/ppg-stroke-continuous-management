from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


GROUP_LABELS = {
    "true stroke-warning": "Clinically anchored",
    "pseudo-anchor": "Pseudo-anchor",
    "permutation-anchor": "Permutation-anchor",
}

COLORS = {
    "Clinically anchored": "#d99aa5",
    "Pseudo-anchor": "#91b8c7",
    "Permutation-anchor": "#b8b8b8",
}


def patient_level_probabilities(plot_data: pd.DataFrame) -> pd.DataFrame:
    df = plot_data[plot_data["analysis_group"].isin(GROUP_LABELS)].copy()
    df["group"] = df["analysis_group"].map(GROUP_LABELS)
    df["horizon_h"] = df["horizon"].astype(str).str.extract(r"(\d+)").astype(int)
    return (
        df.groupby(["group", "horizon_h", "patient_uid"], as_index=False)
        .agg(probability=("y_prob", "mean"), windows=("y_prob", "size"))
    )


def bootstrap_ci(values: np.ndarray, seed: int = 11, n_boot: int = 4000) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = rng.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
    return float(values.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def write_nature_extended_data_figure(
    plot_data_csv: str | Path,
    out_base: str | Path,
) -> None:
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    plot_data = pd.read_csv(plot_data_csv)
    patient = patient_level_probabilities(plot_data)
    order = ["Clinically anchored", "Pseudo-anchor", "Permutation-anchor"]
    horizons = [4, 5, 6]

    mpl.rcParams.update(
        {
            "font.family": "Arial",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "axes.linewidth": 0.65,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )
    fig = plt.figure(figsize=(7.2, 5.05), dpi=500)
    gs = GridSpec(2, 2, figure=fig, height_ratios=[1.02, 1.02], width_ratios=[1.22, 1.0], hspace=0.58, wspace=0.42)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    sub = gs[1, :].subgridspec(1, 3, wspace=0.23)
    axs_c = [fig.add_subplot(sub[0, i]) for i in range(3)]

    rng = np.random.default_rng(6)
    ypos = np.arange(len(order))
    viol = ax_a.violinplot(
        [patient[patient.group == g]["probability"].to_numpy() for g in order],
        positions=ypos,
        vert=False,
        widths=0.60,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )
    for body, group in zip(viol["bodies"], order):
        body.set_facecolor(COLORS[group])
        body.set_alpha(0.28)
        body.set_edgecolor("#555555")
        body.set_linewidth(0.65)
    for i, group in enumerate(order):
        vals = patient[patient.group == group]["probability"].to_numpy()
        ax_a.scatter(vals, np.full(len(vals), i) + rng.normal(0, 0.072, len(vals)), s=9.0, color=COLORS[group], edgecolor="#4a4a4a", linewidth=0.25, alpha=0.72)
        q1, med, q3 = np.percentile(vals, [25, 50, 75])
        mean, lo, hi = bootstrap_ci(vals, seed=410 + i)
        ax_a.plot([q1, q3], [i, i], color="#202020", lw=1.25)
        ax_a.plot([med, med], [i - 0.15, i + 0.15], color="#202020", lw=1.0)
        ax_a.errorbar(mean, i, xerr=[[mean - lo], [hi - mean]], fmt="o", color="black", ms=3.1, lw=0.95, capsize=2.0)
    ax_a.axvline(0.5, color="#777777", lw=0.78, ls=(0, (2, 2)))
    ax_a.set_xlim(0, 1.02)
    ax_a.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax_a.set_yticks(ypos)
    ax_a.set_yticklabels(["Clinically\nanchored", "Pseudo-\nanchor", "Permutation-\nanchor"], fontsize=6.9)
    ax_a.invert_yaxis()
    ax_a.set_xlabel("Patient-level warning probability", fontsize=7.2)
    ax_a.set_title("Patient-level distributions", loc="left", fontsize=8.2, fontweight="bold")
    ax_a.grid(axis="x", color="#e6e6e6", lw=0.58)
    ax_a.spines[["top", "right"]].set_visible(False)

    markers = {"Clinically anchored": "o", "Pseudo-anchor": "s", "Permutation-anchor": "^"}
    linestyles = {"Clinically anchored": "-", "Pseudo-anchor": "-", "Permutation-anchor": (0, (3, 2))}
    offsets = {"Clinically anchored": -0.045, "Pseudo-anchor": 0.0, "Permutation-anchor": 0.045}
    for group in order:
        xs, ys, ylo, yhi = [], [], [], []
        for h in horizons:
            vals = patient[(patient.group == group) & (patient.horizon_h == h)]["probability"].to_numpy()
            mean, lo, hi = bootstrap_ci(vals, seed=100 + h * 7 + order.index(group))
            xs.append(h + offsets[group])
            ys.append(mean)
            ylo.append(mean - lo)
            yhi.append(hi - mean)
        ax_b.plot(xs, ys, color=COLORS[group], lw=1.55, linestyle=linestyles[group], marker=markers[group], ms=4.4, markeredgecolor="#4b4b4b", markeredgewidth=0.5, label=group)
        ax_b.errorbar(xs, ys, yerr=[ylo, yhi], fmt="none", ecolor=COLORS[group], elinewidth=1.0, capsize=2.6)
    ax_b.set_xlim(3.72, 6.28)
    ax_b.set_ylim(0.74, 1.005)
    ax_b.set_xticks(horizons)
    ax_b.set_xticklabels(["4 h", "5 h", "6 h"])
    ax_b.set_xlabel("Warning horizon", fontsize=7.2)
    ax_b.set_ylabel("Mean probability", fontsize=7.2)
    ax_b.set_title("Horizon-resolved means", loc="left", fontsize=8.2, fontweight="bold")
    ax_b.grid(axis="y", color="#e6e6e6", lw=0.58)
    ax_b.spines[["top", "right"]].set_visible(False)
    ax_b.legend(frameon=False, loc="lower right", fontsize=6.6)

    for ax, h in zip(axs_c, horizons):
        for group in order:
            vals = np.sort(patient[(patient.group == group) & (patient.horizon_h == h)]["probability"].to_numpy())
            yy = np.arange(1, len(vals) + 1) / len(vals)
            ax.plot(vals, yy, color=COLORS[group], lw=1.45, linestyle=linestyles[group])
        ax.axvline(0.5, color="#777777", lw=0.72, ls=(0, (2, 2)))
        ax.set_xlim(0, 1.02)
        ax.set_ylim(0, 1.02)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_yticks([0, 0.5, 1.0])
        ax.set_title(f"{h} h", fontsize=8.0, fontweight="bold", color="#163f5e")
        ax.grid(color="#e8e8e8", lw=0.55)
        ax.spines[["top", "right"]].set_visible(False)
        if h == 4:
            ax.set_ylabel("Cumulative fraction", fontsize=7.2)
        else:
            ax.set_yticklabels([])
        ax.set_xlabel("Warning probability", fontsize=7.0)

    ax_a.text(-0.14, 1.10, "a", transform=ax_a.transAxes, fontsize=10.2, fontweight="bold")
    ax_b.text(-0.14, 1.10, "b", transform=ax_b.transAxes, fontsize=10.2, fontweight="bold")
    axs_c[0].text(-0.18, 1.17, "c", transform=axs_c[0].transAxes, fontsize=10.2, fontweight="bold")
    axs_c[0].text(0.0, 1.17, "Horizon-specific empirical distributions", transform=axs_c[0].transAxes, fontsize=8.2, fontweight="bold")

    out_base = Path(out_base)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(out_base.with_suffix(f".{ext}"), dpi=600 if ext == "png" else None, bbox_inches="tight", pad_inches=0.045)
    plt.close(fig)
