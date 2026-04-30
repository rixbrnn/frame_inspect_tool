#!/usr/bin/env python3
"""
Metric Agreement Analysis

Analyzes when SSIM, PSNR, LPIPS, and FLIP agree vs disagree on quality rankings.
Addresses TCC key finding: SSIM-LPIPS contradiction.

Usage:
    python src/insights/metric_agreement.py \
        --results-dir results/cyberpunk/quality_comparison \
        --output results/cyberpunk/metric_agreement

    # Cross-game analysis
    python src/insights/metric_agreement.py \
        --aggregated-data results/aggregated/all_games_summary.csv \
        --output results/aggregated/metric_agreement
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.spatial.distance import pdist, squareform
import argparse
from typing import Dict, List, Tuple


def load_comparison_results(results_dir: Path) -> pd.DataFrame:
    """Load all comparison results from directory"""
    data = []

    json_files = list(results_dir.glob("*_vs_*.json"))

    for json_file in json_files:
        try:
            with open(json_file) as f:
                comparison = json.load(f)

            metrics = comparison.get('metrics', {})
            comparison_name = json_file.stem

            # Parse resolution and mode
            parts = comparison_name.split('_')
            resolution = parts[0]
            mode = '_'.join(parts[3:])  # After "DLAA_vs"

            row = {
                'comparison': comparison_name,
                'resolution': resolution,
                'mode': mode,
                'ssim': metrics.get('ssim', {}).get('mean'),
                'psnr': metrics.get('psnr', {}).get('mean'),
                'lpips': metrics.get('lpips', {}).get('mean'),
                'flip': metrics.get('flip', {}).get('mean'),
            }

            data.append(row)

        except Exception as e:
            print(f"  ⚠️  Error loading {json_file.name}: {e}")
            continue

    return pd.DataFrame(data)


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute correlation matrix between metrics

    Returns:
        DataFrame with Pearson and Spearman correlations
    """
    metrics = ['ssim', 'psnr', 'lpips', 'flip']

    # Remove rows with missing values
    df_clean = df[metrics].dropna()

    # Pearson correlation
    pearson_corr = df_clean.corr(method='pearson')

    # Spearman correlation (rank-based, robust to non-linearity)
    spearman_corr = df_clean.corr(method='spearman')

    return pearson_corr, spearman_corr


def compute_ranking_disagreement(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each resolution, rank modes by each metric and find disagreements

    Returns:
        DataFrame with rankings per resolution/mode
    """
    results = []

    for resolution in df['resolution'].unique():
        res_df = df[df['resolution'] == resolution].copy()

        if len(res_df) < 2:
            continue

        # Rank modes by each metric
        # For SSIM/PSNR: higher is better (rank=1 is best)
        # For LPIPS/FLIP: lower is better (rank=1 is best)

        res_df['ssim_rank'] = res_df['ssim'].rank(ascending=False, method='min')
        res_df['psnr_rank'] = res_df['psnr'].rank(ascending=False, method='min')
        res_df['lpips_rank'] = res_df['lpips'].rank(ascending=True, method='min')  # Lower is better
        res_df['flip_rank'] = res_df['flip'].rank(ascending=True, method='min')    # Lower is better

        for _, row in res_df.iterrows():
            results.append({
                'resolution': resolution,
                'mode': row['mode'],
                'ssim': row['ssim'],
                'ssim_rank': int(row['ssim_rank']),
                'psnr': row['psnr'],
                'psnr_rank': int(row['psnr_rank']),
                'lpips': row['lpips'],
                'lpips_rank': int(row['lpips_rank']),
                'flip': row['flip'],
                'flip_rank': int(row['flip_rank']),
            })

    return pd.DataFrame(results)


def find_contradictions(ranking_df: pd.DataFrame) -> List[Dict]:
    """
    Identify cases where metrics give opposite rankings

    Returns:
        List of contradiction cases
    """
    contradictions = []

    for resolution in ranking_df['resolution'].unique():
        res_df = ranking_df[ranking_df['resolution'] == resolution]

        # Find best mode according to each metric
        best_ssim = res_df[res_df['ssim_rank'] == 1]
        best_lpips = res_df[res_df['lpips_rank'] == 1]
        best_flip = res_df[res_df['flip_rank'] == 1]

        # Check for contradictions
        if not best_ssim.empty and not best_lpips.empty:
            ssim_best_mode = best_ssim.iloc[0]['mode']
            lpips_best_mode = best_lpips.iloc[0]['mode']

            if ssim_best_mode != lpips_best_mode:
                contradictions.append({
                    'resolution': resolution,
                    'metric1': 'SSIM',
                    'metric1_best': ssim_best_mode,
                    'metric1_value': best_ssim.iloc[0]['ssim'],
                    'metric2': 'LPIPS',
                    'metric2_best': lpips_best_mode,
                    'metric2_value': best_lpips.iloc[0]['lpips'],
                    'type': 'SSIM-LPIPS disagreement'
                })

        if not best_ssim.empty and not best_flip.empty:
            ssim_best_mode = best_ssim.iloc[0]['mode']
            flip_best_mode = best_flip.iloc[0]['mode']

            if ssim_best_mode != flip_best_mode:
                contradictions.append({
                    'resolution': resolution,
                    'metric1': 'SSIM',
                    'metric1_best': ssim_best_mode,
                    'metric1_value': best_ssim.iloc[0]['ssim'],
                    'metric2': 'FLIP',
                    'metric2_best': flip_best_mode,
                    'metric2_value': best_flip.iloc[0]['flip'],
                    'type': 'SSIM-FLIP disagreement'
                })

    return contradictions


def plot_correlation_matrix(pearson_corr: pd.DataFrame, spearman_corr: pd.DataFrame,
                            output_path: Path):
    """Plot correlation matrices (Pearson and Spearman)"""

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Pearson correlation
    sns.heatmap(
        pearson_corr,
        annot=True,
        fmt='.3f',
        cmap='RdBu_r',
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        cbar_kws={'label': 'Pearson Correlation'},
        ax=axes[0]
    )
    axes[0].set_title('Pearson Correlation\n(Linear Relationship)', fontweight='bold')

    # Spearman correlation
    sns.heatmap(
        spearman_corr,
        annot=True,
        fmt='.3f',
        cmap='RdBu_r',
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        cbar_kws={'label': 'Spearman Correlation'},
        ax=axes[1]
    )
    axes[1].set_title('Spearman Correlation\n(Rank-Based Relationship)', fontweight='bold')

    plt.suptitle('Metric Correlation Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_scatter_matrix(df: pd.DataFrame, output_path: Path):
    """Scatter plot matrix showing relationships between metrics"""

    metrics = ['ssim', 'psnr', 'lpips', 'flip']
    df_clean = df[metrics].dropna()

    fig, axes = plt.subplots(4, 4, figsize=(16, 16))

    for i, metric1 in enumerate(metrics):
        for j, metric2 in enumerate(metrics):
            ax = axes[i, j]

            if i == j:
                # Diagonal: histogram
                ax.hist(df_clean[metric1], bins=20, alpha=0.7, color='steelblue')
                ax.set_ylabel('Frequency')
            else:
                # Off-diagonal: scatter plot
                ax.scatter(df_clean[metric2], df_clean[metric1], alpha=0.6, s=30)

                # Add regression line
                z = np.polyfit(df_clean[metric2], df_clean[metric1], 1)
                p = np.poly1d(z)
                x_line = np.linspace(df_clean[metric2].min(), df_clean[metric2].max(), 100)
                ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)

                # Compute correlation
                r, p_val = stats.pearsonr(df_clean[metric2], df_clean[metric1])
                ax.text(0.05, 0.95, f'r={r:.3f}',
                       transform=ax.transAxes, fontsize=9,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

            # Labels
            if i == len(metrics) - 1:
                ax.set_xlabel(metric2.upper())
            if j == 0:
                ax.set_ylabel(metric1.upper())

            ax.grid(alpha=0.3)

    plt.suptitle('Metric Scatter Matrix with Correlations', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_ranking_comparison(ranking_df: pd.DataFrame, output_path: Path):
    """Bar chart comparing rankings across metrics"""

    resolutions = sorted(ranking_df['resolution'].unique())

    fig, axes = plt.subplots(1, len(resolutions), figsize=(18, 6))
    if len(resolutions) == 1:
        axes = [axes]

    for idx, resolution in enumerate(resolutions):
        ax = axes[idx]
        res_df = ranking_df[ranking_df['resolution'] == resolution].sort_values('ssim_rank')

        x = np.arange(len(res_df))
        width = 0.2

        ax.bar(x - 1.5*width, res_df['ssim_rank'], width, label='SSIM', alpha=0.8)
        ax.bar(x - 0.5*width, res_df['psnr_rank'], width, label='PSNR', alpha=0.8)
        ax.bar(x + 0.5*width, res_df['lpips_rank'], width, label='LPIPS', alpha=0.8)
        ax.bar(x + 1.5*width, res_df['flip_rank'], width, label='FLIP', alpha=0.8)

        ax.set_xlabel('DLSS Mode', fontsize=10)
        ax.set_ylabel('Rank (1=best)', fontsize=10)
        ax.set_title(f'{resolution} - Ranking by Metric', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(res_df['mode'], rotation=15, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        ax.invert_yaxis()  # Rank 1 at top

    plt.suptitle('Metric Ranking Comparison (Lower Rank = Better)',
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_ssim_vs_lpips(df: pd.DataFrame, output_path: Path):
    """
    Detailed scatter plot: SSIM vs LPIPS with mode annotations
    """
    df_clean = df[['ssim', 'lpips', 'mode', 'resolution']].dropna()

    fig, ax = plt.subplots(figsize=(12, 8))

    # Color by resolution
    resolutions = df_clean['resolution'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(resolutions)))
    resolution_colors = dict(zip(resolutions, colors))

    for resolution in resolutions:
        res_df = df_clean[df_clean['resolution'] == resolution]
        ax.scatter(res_df['lpips'], res_df['ssim'],
                  label=resolution, alpha=0.7, s=100,
                  color=resolution_colors[resolution])

    # Add regression line
    r, p_val = stats.pearsonr(df_clean['lpips'], df_clean['ssim'])
    z = np.polyfit(df_clean['lpips'], df_clean['ssim'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df_clean['lpips'].min(), df_clean['lpips'].max(), 100)
    ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2,
           label=f'Linear fit (r={r:.3f}, p={p_val:.4f})')

    # Annotations
    ax.set_xlabel('LPIPS (Lower = Better)', fontsize=12)
    ax.set_ylabel('SSIM (Higher = Better)', fontsize=12)
    ax.set_title('SSIM vs LPIPS: Contradiction Analysis\n(Negative correlation expected)',
                fontsize=13, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(alpha=0.3)

    # Add quadrant lines (if data range allows)
    median_ssim = df_clean['ssim'].median()
    median_lpips = df_clean['lpips'].median()
    ax.axhline(median_ssim, color='gray', linestyle=':', alpha=0.5)
    ax.axvline(median_lpips, color='gray', linestyle=':', alpha=0.5)

    # Annotate quadrants
    ax.text(0.05, 0.95, 'Good SSIM\nPoor LPIPS',
           transform=ax.transAxes, fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    ax.text(0.95, 0.05, 'Poor SSIM\nGood LPIPS',
           transform=ax.transAxes, fontsize=9, verticalalignment='bottom',
           horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def generate_report(df: pd.DataFrame, pearson_corr: pd.DataFrame,
                   spearman_corr: pd.DataFrame, ranking_df: pd.DataFrame,
                   contradictions: List[Dict], output_path: Path):
    """Generate markdown report with findings"""

    report = []
    report.append("# Metric Agreement Analysis Report\n")
    report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n\n")

    # Overview
    report.append("## Overview\n\n")
    report.append(f"- **Comparisons analyzed:** {len(df)}\n")
    report.append(f"- **Resolutions:** {', '.join(sorted(df['resolution'].unique()))}\n")
    report.append(f"- **Modes:** {', '.join(sorted(df['mode'].unique()))}\n\n")

    # Correlation findings
    report.append("## Correlation Analysis\n\n")
    report.append("### Pearson Correlation (Linear Relationship)\n\n")
    report.append("| Metric | SSIM | PSNR | LPIPS | FLIP |\n")
    report.append("|--------|------|------|-------|------|\n")
    for idx, row in pearson_corr.iterrows():
        report.append(f"| **{idx.upper()}** | {row['ssim']:.3f} | {row['psnr']:.3f} | "
                     f"{row['lpips']:.3f} | {row['flip']:.3f} |\n")
    report.append("\n")

    # Key correlations
    report.append("### Key Findings\n\n")

    ssim_lpips_corr = pearson_corr.loc['ssim', 'lpips']
    ssim_flip_corr = pearson_corr.loc['ssim', 'flip']
    lpips_flip_corr = pearson_corr.loc['lpips', 'flip']

    report.append(f"1. **SSIM vs LPIPS:** r = {ssim_lpips_corr:.3f}")
    if ssim_lpips_corr < -0.5:
        report.append(" → Strong negative correlation (expected)\n")
    elif ssim_lpips_corr < -0.3:
        report.append(" → Moderate negative correlation\n")
    else:
        report.append(" → Weak correlation ⚠️\n")

    report.append(f"2. **SSIM vs FLIP:** r = {ssim_flip_corr:.3f}")
    if ssim_flip_corr < -0.5:
        report.append(" → Strong negative correlation (expected)\n")
    else:
        report.append(" → Weaker than expected ⚠️\n")

    report.append(f"3. **LPIPS vs FLIP:** r = {lpips_flip_corr:.3f}")
    if lpips_flip_corr > 0.7:
        report.append(" → Strong positive correlation (both perceptual metrics)\n")
    else:
        report.append(" → Moderate correlation\n")

    report.append("\n**Interpretation:**\n")
    if abs(ssim_lpips_corr) < 0.5:
        report.append("- ⚠️ **Low SSIM-LPIPS correlation suggests metrics capture different quality aspects**\n")
        report.append("- SSIM focuses on structural similarity (pixel-level)\n")
        report.append("- LPIPS focuses on perceptual features (neural network-based)\n")
        report.append("- This explains contradictory rankings (Performance > Quality in SSIM but opposite in LPIPS)\n")

    report.append("\n")

    # Ranking contradictions
    if contradictions:
        report.append(f"## Ranking Contradictions\n\n")
        report.append(f"Found {len(contradictions)} cases where metrics disagree on best mode:\n\n")

        for contradiction in contradictions:
            report.append(f"### {contradiction['resolution']} - {contradiction['type']}\n\n")
            report.append(f"- **{contradiction['metric1']} ranks {contradiction['metric1_best']} best** "
                         f"(value: {contradiction['metric1_value']:.3f})\n")
            report.append(f"- **{contradiction['metric2']} ranks {contradiction['metric2_best']} best** "
                         f"(value: {contradiction['metric2_value']:.3f})\n")
            report.append("\n")

    # Ranking table
    report.append("## Detailed Rankings by Resolution\n\n")
    for resolution in sorted(ranking_df['resolution'].unique()):
        res_df = ranking_df[ranking_df['resolution'] == resolution].sort_values('ssim_rank')

        report.append(f"### {resolution}\n\n")
        report.append("| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |\n")
        report.append("|------|-------------|-------------|--------------|-------------|\n")

        for _, row in res_df.iterrows():
            report.append(f"| {row['mode']} | {row['ssim']:.3f} ({int(row['ssim_rank'])}) | "
                         f"{row['psnr']:.1f} ({int(row['psnr_rank'])}) | "
                         f"{row['lpips']:.3f} ({int(row['lpips_rank'])}) | "
                         f"{row['flip']:.1f} ({int(row['flip_rank'])}) |\n")
        report.append("\n")

    # Write report
    with open(output_path, 'w') as f:
        f.writelines(report)

    print(f"  📄 Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Analyze metric agreement/disagreement')
    parser.add_argument('--results-dir', type=str,
                       help='Directory with comparison JSON files')
    parser.add_argument('--aggregated-data', type=str,
                       help='CSV file from aggregate_all_games.py')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("METRIC AGREEMENT ANALYSIS")
    print("="*70)

    # Load data
    if args.results_dir:
        print(f"📂 Loading from: {args.results_dir}")
        df = load_comparison_results(Path(args.results_dir))
    elif args.aggregated_data:
        print(f"📂 Loading aggregated data: {args.aggregated_data}")
        df = pd.read_csv(args.aggregated_data)
        # Filter only DLSS mode comparisons
        df = df[df['comparison_type'] == 'dlss_mode']
        # Rename columns to match expected format
        if 'ssim_mean' in df.columns:
            df = df.rename(columns={
                'ssim_mean': 'ssim', 'psnr_mean': 'psnr',
                'lpips_mean': 'lpips', 'flip_mean': 'flip'
            })
    else:
        print("❌ Must provide --results-dir or --aggregated-data")
        return

    if df.empty:
        print("❌ No data loaded. Exiting.")
        return

    print(f"✅ Loaded {len(df)} comparisons\n")

    # Compute correlations
    print("📊 Computing correlation matrices...")
    pearson_corr, spearman_corr = compute_correlation_matrix(df)

    # Compute rankings
    print("📊 Computing rankings...")
    ranking_df = compute_ranking_disagreement(df)

    # Find contradictions
    print("🔍 Identifying ranking contradictions...")
    contradictions = find_contradictions(ranking_df)
    print(f"  Found {len(contradictions)} contradictions\n")

    # Save data
    df.to_csv(output_dir / "metric_data.csv", index=False)
    ranking_df.to_csv(output_dir / "rankings.csv", index=False)
    pearson_corr.to_csv(output_dir / "pearson_correlation.csv")
    spearman_corr.to_csv(output_dir / "spearman_correlation.csv")

    if contradictions:
        pd.DataFrame(contradictions).to_csv(output_dir / "contradictions.csv", index=False)

    # Generate visualizations
    print("🎨 Generating visualizations...")
    plot_correlation_matrix(pearson_corr, spearman_corr,
                           output_dir / "correlation_matrix.png")
    plot_scatter_matrix(df, output_dir / "scatter_matrix.png")
    plot_ranking_comparison(ranking_df, output_dir / "ranking_comparison.png")
    plot_ssim_vs_lpips(df, output_dir / "ssim_vs_lpips.png")

    # Generate report
    print("\n📝 Generating analysis report...")
    generate_report(df, pearson_corr, spearman_corr, ranking_df, contradictions,
                   output_dir / "METRIC_AGREEMENT_REPORT.md")

    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutputs saved to: {output_dir}/")


if __name__ == "__main__":
    main()
