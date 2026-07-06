#!/usr/bin/env python3
"""
TCC Manuscript Visualizations

Generates 4 figures specifically requested by the TCC manuscript revision pass:

  A) slope_chart_by_mode.png     -- Slope chart Quality->Balanced->Performance->Ultra
                                     (substitui mean_metrics_by_mode no manuscrito)
  B) forest_plot_delta_quality.png -- Forest plot DeltaSSIM Quality vs DLAA por jogo
  C) winners_by_metric.png       -- Bar chart 100% empilhado: % winners por modo,
                                     evidenciando o achado central (LPIPS chi^2)
  D) lpips_ecdf_by_mode.png      -- ECDF de LPIPS por modo, mostrando overlap

All figures use ordinal color ramps for DLSS modes (Quality < Balanced < Performance
< UltraPerformance), respecting the perceptual order.

Usage:
    python src/insights/tcc_visualizations.py \\
        --aggregated-dir results/aggregated \\
        --output results/aggregated/tcc

Output:
    - tcc/slope_chart_by_mode.png
    - tcc/forest_plot_delta_quality.png
    - tcc/winners_by_metric.png
    - tcc/lpips_ecdf_by_mode.png
"""

import argparse
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

# Permite importar labels_pt mesmo executando o script diretamente
sys.path.insert(0, str(Path(__file__).resolve().parent))
from labels_pt import display_name


# DLSS modes in their canonical (ordinal) order, from least aggressive to most.
MODE_ORDER = ["Quality", "Balanced", "Performance", "Ultra_Performance"]
MODE_LABEL = {
    "Quality": "Quality",
    "Balanced": "Balanced",
    "Performance": "Performance",
    "Ultra_Performance": "Ultra Perf.",
}
RES_ORDER = ["1080p", "1440p", "4K"]

# Color palette: ordinal sequential per DLSS mode (viridis-like).
MODE_COLORS = {
    "Quality": "#440154",            # dark purple
    "Balanced": "#3b528b",           # blue
    "Performance": "#21918c",        # teal
    "Ultra_Performance": "#fde725",  # yellow
}
RES_COLORS = {
    "1080p": "#1f77b4",
    "1440p": "#ff7f0e",
    "4K": "#2ca02c",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_summary(aggregated_dir: Path) -> pd.DataFrame:
    """Load the aggregated all-games summary (one row per game x res x mode)."""
    csv = aggregated_dir / "all_games_summary.csv"
    df = pd.read_csv(csv)
    return df


def load_metric_data(aggregated_dir: Path) -> pd.DataFrame:
    """Load the per-comparison metric data (used for rankings/ECDF)."""
    csv = aggregated_dir / "metric_agreement" / "metric_data.csv"
    df = pd.read_csv(csv)
    return df


def load_summary_by_mode(aggregated_dir: Path) -> pd.DataFrame:
    """Load the summary aggregated by (resolution, mode)."""
    csv = aggregated_dir / "summary_by_mode.csv"
    df = pd.read_csv(csv)
    return df


# ---------------------------------------------------------------------------
# Figure A: Slope chart
# ---------------------------------------------------------------------------

def plot_slope_chart(summary_by_mode: pd.DataFrame, output_path: Path):
    """
    Three-panel slope chart: SSIM, LPIPS, FLIP across DLSS modes,
    one line per resolution. Replaces the bar chart `mean_metrics_by_mode`.
    """
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    metrics = [
        ("ssim_mean_mean", "SSIM", "higher is better", axes[0]),
        ("lpips_mean_mean", "LPIPS", "lower is better", axes[1]),
        ("flip_mean_mean", "FLIP", "lower is better", axes[2]),
    ]

    x_positions = list(range(len(MODE_ORDER)))
    x_labels = [MODE_LABEL[m] for m in MODE_ORDER]

    for col, label, hint, ax in metrics:
        for res in RES_ORDER:
            sub = summary_by_mode[summary_by_mode["resolution"] == res]
            sub = sub.set_index("mode").reindex(MODE_ORDER)
            ax.plot(
                x_positions,
                sub[col].values,
                marker="o",
                color=RES_COLORS[res],
                linewidth=2.0,
                markersize=7,
                label=res,
            )
        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_labels, rotation=15, ha="right")
        ax.set_title(f"{label}\n({hint})", fontsize=11)
        ax.grid(True, axis="y", alpha=0.3)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[0].set_ylabel("Métrica média (10 jogos)", fontsize=10)
    axes[0].legend(title="Resolução", loc="lower left", frameon=False)

    fig.suptitle(
        "Evolução das métricas ao longo dos modos DLSS\n"
        "(eixo X em ordem ordinal Quality → Ultra Performance)",
        fontsize=12,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  📊 Saved: {output_path}")


# ---------------------------------------------------------------------------
# Figure B: Forest plot of Delta-SSIM (Quality vs DLAA) per game
# ---------------------------------------------------------------------------

def plot_forest_quality(metric_data: pd.DataFrame,
                        all_games_summary: pd.DataFrame,
                        output_path: Path,
                        resolution: str = "1440p"):
    """
    Forest plot: SSIM(Quality) vs SSIM(DLAA-consistency) per game, at a fixed
    resolution. Uses consistency as the per-game DLAA proxy. A grey band marks
    the per-resolution MDD (±2σ noise floor).

    Quality data comes from metric_data.csv (DLSS-mode comparisons), but
    consistency lives in all_games_summary.csv (comparison_type='consistency').
    """
    quality_df = metric_data[
        (metric_data["resolution"] == resolution) &
        (metric_data["mode"] == "Quality") &
        (metric_data["comparison_type"] == "dlss_mode")
    ]
    consistency_df = all_games_summary[
        (all_games_summary["resolution"] == resolution) &
        (all_games_summary["comparison_type"] == "consistency")
    ]

    rows = []
    for _, q in quality_df.iterrows():
        c = consistency_df[consistency_df["game"] == q["game"]]
        if c.empty:
            continue
        c_ssim = c["ssim_mean"].values[0]
        delta = q["ssim"] - c_ssim
        rows.append({
            "game": q["game"],
            "ssim_quality": q["ssim"],
            "ssim_dlaa": c_ssim,
            "delta": delta,
        })

    if not rows:
        print(f"  ⚠️  No data for forest plot at {resolution}, skipping.")
        return

    forest = pd.DataFrame(rows).sort_values("delta")

    # MDD (2σ) for SSIM at this resolution, from the noise_floor.csv
    # Hardcoded reference values — match what TCC text reports
    MDD = {"1080p": 0.160, "1440p": 0.163, "4K": 0.166}
    mdd = MDD.get(resolution, 0.16)

    fig, ax = plt.subplots(figsize=(9, max(4, 0.45 * len(forest))))

    y_positions = np.arange(len(forest))

    # Grey MDD band centered at zero
    ax.axvspan(-mdd, mdd, color="lightgrey", alpha=0.5,
               label=f"Banda MDD (±{mdd:.3f})")
    ax.axvline(0, color="black", linewidth=0.8)

    # Points + horizontal stems
    colors = ["#d62728" if d < -mdd else "#888888" for d in forest["delta"]]
    ax.scatter(forest["delta"], y_positions, s=80, c=colors,
               edgecolor="black", linewidth=0.8, zorder=3)
    for y, d in zip(y_positions, forest["delta"]):
        ax.plot([0, d], [y, y], color="grey", linewidth=1, alpha=0.5)

    ax.set_yticks(y_positions)
    ax.set_yticklabels([display_name(g, short=True) for g in forest["game"].values],
                       fontsize=9)
    ax.set_xlabel("ΔSSIM (Quality − DLAA por jogo)", fontsize=11)
    ax.set_title(
        f"Heterogeneidade DLSS Quality vs DLAA por jogo, {resolution}\n"
        f"Pontos vermelhos: |Δ| > MDD",
        fontsize=12,
        fontweight="bold",
    )
    ax.legend(loc="lower right", frameon=False)
    ax.grid(True, axis="x", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  📊 Saved: {output_path}")


# ---------------------------------------------------------------------------
# Figure C: Winners by metric (chi^2 finding visualised)
# ---------------------------------------------------------------------------

def compute_winners(metric_data: pd.DataFrame) -> pd.DataFrame:
    """
    For each (game, resolution) group, rank the 4 DLSS modes by each metric,
    then count how often each mode is the winner (rank=1).
    Returns a DataFrame: rows=metric, columns=mode, values=fraction of wins.
    Also returns chi-square p-value testing uniformity (H0: 25% per mode).
    """
    # Keep only DLSS modes (drop Consistency)
    df = metric_data[metric_data["comparison_type"] == "dlss_mode"].copy()

    # Metric direction: True if higher is better (winner = max),
    # False if lower is better (winner = min).
    metric_dir = {"ssim": True, "psnr": True, "lpips": False, "flip": False}

    rows = []
    pvals = {}
    for metric, higher_is_better in metric_dir.items():
        win_counts = defaultdict(int)
        total_groups = 0
        for (game, res), grp in df.groupby(["game", "resolution"]):
            grp = grp.set_index("mode").reindex(MODE_ORDER).dropna(subset=[metric])
            if len(grp) < 2:
                continue
            if higher_is_better:
                winner = grp[metric].idxmax()
            else:
                winner = grp[metric].idxmin()
            win_counts[winner] += 1
            total_groups += 1

        # Chi-square test against uniform (1/4 each)
        observed = [win_counts[m] for m in MODE_ORDER]
        expected = [total_groups / len(MODE_ORDER)] * len(MODE_ORDER)
        if total_groups > 0 and all(e > 0 for e in expected):
            chi2, p = stats.chisquare(observed, f_exp=expected)
        else:
            chi2, p = float("nan"), float("nan")

        for m in MODE_ORDER:
            rows.append({
                "metric": metric.upper(),
                "mode": m,
                "wins": win_counts[m],
                "total": total_groups,
                "fraction": win_counts[m] / total_groups if total_groups else 0,
            })
        pvals[metric.upper()] = p

    return pd.DataFrame(rows), pvals


def plot_winners_by_metric(metric_data: pd.DataFrame, output_path: Path):
    """
    Horizontal stacked bar chart: each bar = one metric, segments = % winners
    per DLSS mode. Highlights LPIPS as the only metric where winner distribution
    diverges from uniform (chi^2 p < 0.05).
    """
    winners, pvals = compute_winners(metric_data)

    # Order metrics by chi^2 p-value (most significant first)
    metric_order = sorted(pvals.keys(), key=lambda m: pvals[m])
    fig, ax = plt.subplots(figsize=(10, 4.5))

    y_positions = np.arange(len(metric_order))
    left = np.zeros(len(metric_order))

    for mode in MODE_ORDER:
        fractions = []
        for metric in metric_order:
            row = winners[(winners["metric"] == metric) &
                          (winners["mode"] == mode)]
            fractions.append(row["fraction"].values[0] if not row.empty else 0)
        ax.barh(y_positions, fractions, left=left,
                color=MODE_COLORS[mode],
                label=MODE_LABEL[mode],
                edgecolor="white",
                linewidth=0.8,
                height=0.7)
        left += np.array(fractions)

    # Annotate p-values
    for i, metric in enumerate(metric_order):
        p = pvals[metric]
        marker = " ★" if p < 0.05 else ""
        label = f"{metric}  (χ² p={p:.3f}){marker}"
        ax.text(1.02, y_positions[i], label, va="center", fontsize=10)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(["" for _ in metric_order])
    ax.set_xlim(0, 1)
    ax.set_xlabel("Fração de comparações em que o modo é 'winner' (rank 1)",
                  fontsize=11)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.axvline(0.25, color="grey", linewidth=0.8, linestyle="--",
               label="Esperado por aleatório (25%)")

    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.35),
              ncol=5, frameon=False, fontsize=9)
    ax.set_title(
        "Sensibilidade das métricas a modos DLSS: contagem de winners\n"
        "★ indica métrica que distingue modos significativamente (χ² p < 0.05)",
        fontsize=12, fontweight="bold")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  📊 Saved: {output_path}")


# ---------------------------------------------------------------------------
# Figure D: ECDF of LPIPS by mode
# ---------------------------------------------------------------------------

def plot_lpips_ecdf(metric_data: pd.DataFrame, output_path: Path):
    """
    Empirical CDF of LPIPS per DLSS mode, aggregated across all
    (game, resolution) DLSS-DLAA comparisons.
    """
    df = metric_data[metric_data["comparison_type"] == "dlss_mode"].copy()

    fig, ax = plt.subplots(figsize=(8, 5))

    for mode in MODE_ORDER:
        sub = df[df["mode"] == mode]["lpips"].dropna().sort_values().values
        if len(sub) == 0:
            continue
        y = np.arange(1, len(sub) + 1) / len(sub)
        ax.plot(sub, y, marker="o", markersize=3, linewidth=1.8,
                color=MODE_COLORS[mode],
                label=f"{MODE_LABEL[mode]} (n={len(sub)})")

    ax.set_xlabel("LPIPS", fontsize=11)
    ax.set_ylabel("P(LPIPS ≤ x)", fontsize=11)
    ax.set_title(
        "ECDF empírica de LPIPS por modo DLSS\n"
        "Curvas deslocadas à direita = pior qualidade perceptual",
        fontsize=12, fontweight="bold")
    ax.legend(title="Modo DLSS", frameon=False, loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  📊 Saved: {output_path}")


# ---------------------------------------------------------------------------
# Figure E: Reproducibility heatmap on LPIPS (DLAA run1 vs run2)
# ---------------------------------------------------------------------------

def plot_reproducibility_lpips(all_games_summary: pd.DataFrame, output_path: Path):
    """
    Heatmap of LPIPS reproducibility (DLAA Consistency, run1 vs run2)
    by game x resolution. Mirrors the existing SSIM heatmap but on the
    perceptual axis. Lower is better, so we use a reversed colormap
    (RdYlGn_r) so that 'green = low LPIPS = good' matches the visual
    convention of the SSIM heatmap.
    """
    import seaborn as sns

    consistency_df = all_games_summary[
        all_games_summary["comparison_type"] == "consistency"
    ].copy()

    if consistency_df.empty:
        print("  ⚠️  No consistency data found, skipping LPIPS reproducibility heatmap")
        return

    # Pivot games × resolutions → LPIPS
    pivot = consistency_df.pivot(index="game", columns="resolution",
                                  values="lpips_mean")
    # Order resolutions canonically
    pivot = pivot.reindex(columns=[r for r in RES_ORDER if r in pivot.columns])
    # Aplica nomes oficiais (curtos) aos jogos
    pivot.index = [display_name(g, short=True) for g in pivot.index]

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        pivot,
        annot=True,
        fmt=".3f",
        cmap="RdYlGn_r",  # reversed: low (good) = green, high (bad) = red
        vmin=0.10,
        vmax=0.50,
        cbar_kws={"label": "LPIPS (DLAA exec1 vs exec2)"},
        ax=ax,
        linewidths=0.5,
        linecolor="gray",
    )

    ax.set_title(
        "Análise de reprodutibilidade: consistência DLAA\n"
        "(LPIPS entre duas capturas DLAA independentes)",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Resolução", fontsize=10)
    ax.set_ylabel("Jogo", fontsize=10)

    obs_min = pivot.min().min()
    obs_max = pivot.max().max()
    ax.text(
        0.5,
        -0.15,
        f"Limiar ideal: LPIPS ≈ 0 | Observado: {obs_min:.3f}–{obs_max:.3f} (alta variância)",
        ha="center",
        transform=ax.transAxes,
        fontsize=9,
        color="red",
        style="italic",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  📊 Saved: {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate TCC manuscript figures (Slope, Forest, Winners, ECDF)"
    )
    parser.add_argument("--aggregated-dir", type=Path,
                        default=Path("results/aggregated"),
                        help="Directory with aggregated CSVs")
    parser.add_argument("--output", type=Path,
                        default=Path("results/aggregated/tcc"),
                        help="Output directory for PNGs")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    print("📂 Loading data...")
    summary_by_mode = load_summary_by_mode(args.aggregated_dir)
    metric_data = load_metric_data(args.aggregated_dir)
    all_games_summary = load_summary(args.aggregated_dir)
    print(f"  - summary_by_mode:    {len(summary_by_mode)} rows")
    print(f"  - metric_data:        {len(metric_data)} rows")
    print(f"  - all_games_summary:  {len(all_games_summary)} rows")

    print("\n🎨 Generating figures...")

    plot_slope_chart(
        summary_by_mode,
        args.output / "slope_chart_by_mode.png",
    )
    plot_forest_quality(
        metric_data,
        all_games_summary,
        args.output / "forest_plot_delta_quality_1440p.png",
        resolution="1440p",
    )
    plot_winners_by_metric(
        metric_data,
        args.output / "winners_by_metric.png",
    )
    plot_lpips_ecdf(
        metric_data,
        args.output / "lpips_ecdf_by_mode.png",
    )
    plot_reproducibility_lpips(
        all_games_summary,
        args.output / "reproducibility_analysis_lpips.png",
    )

    print(f"\n✅ All figures saved to: {args.output}")


if __name__ == "__main__":
    main()
