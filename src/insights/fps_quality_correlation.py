#!/usr/bin/env python3
"""
FPS-Quality Correlation Analysis

Analyzes temporal correlation between FPS and image quality metrics.
Addresses TCC Peer Review #9: Temporal Autocorrelation Violates Statistical Assumptions.

Usage:
    python src/insights/fps_quality_correlation.py \
        --results-dir results/cyberpunk/quality_comparison \
        --output results/cyberpunk/fps_correlation

    # Cross-game analysis
    python src/insights/fps_quality_correlation.py \
        --aggregated-data results/aggregated/all_games_summary.csv \
        --results-base-dir results \
        --output results/aggregated/fps_correlation
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from statsmodels.stats.stattools import durbin_watson
from typing import Dict, List, Tuple, Optional
import argparse


def load_per_frame_data(json_file: Path) -> Optional[pd.DataFrame]:
    """
    Load per-frame data from comparison JSON

    Returns:
        DataFrame with columns: frame_index, timestamp, fps, ssim, lpips, flip, etc.
    """
    try:
        with open(json_file) as f:
            data = json.load(f)

        per_frame = data.get('per_frame_data', {})

        if not per_frame.get('enabled', False):
            return None

        frames = per_frame.get('frames', [])

        if not frames:
            return None

        # Convert to DataFrame
        df = pd.DataFrame(frames)

        # Add metadata
        comparison_name = json_file.stem
        parts = comparison_name.split('_')
        df['resolution'] = parts[0]
        df['comparison'] = comparison_name

        return df

    except Exception as e:
        print(f"  ⚠️  Error loading {json_file.name}: {e}")
        return None


def load_all_per_frame_data(results_dir: Path) -> pd.DataFrame:
    """Load all per-frame data from a results directory"""
    all_frames = []

    json_files = list(results_dir.glob("*.json"))

    for json_file in json_files:
        # Skip consistency comparisons (no meaningful FPS comparison)
        if 'Consistency' in json_file.stem:
            continue

        df = load_per_frame_data(json_file)
        if df is not None and not df.empty:
            all_frames.append(df)

    if not all_frames:
        return pd.DataFrame()

    return pd.concat(all_frames, ignore_index=True)


def test_autocorrelation(series: pd.Series) -> Dict:
    """
    Test for temporal autocorrelation using Durbin-Watson statistic

    DW statistic ranges from 0 to 4:
    - 2: no autocorrelation
    - 0-2: positive autocorrelation
    - 2-4: negative autocorrelation
    - Values close to 2 (1.5-2.5) indicate no serious autocorrelation

    Returns:
        Dict with statistic, interpretation, and lag-1 autocorrelation
    """
    # Remove NaN values
    clean_series = series.dropna()

    if len(clean_series) < 2:
        return {'dw_statistic': np.nan, 'interpretation': 'insufficient data'}

    # Durbin-Watson test
    dw = durbin_watson(clean_series)

    # Lag-1 autocorrelation (approximation: r ≈ 1 - DW/2)
    lag1_autocorr = 1 - (dw / 2)

    # Interpretation
    if 1.5 <= dw <= 2.5:
        interpretation = 'no significant autocorrelation'
    elif dw < 1.5:
        interpretation = 'positive autocorrelation (values persist over time)'
    else:
        interpretation = 'negative autocorrelation (values alternate)'

    return {
        'dw_statistic': dw,
        'lag1_autocorrelation': lag1_autocorr,
        'interpretation': interpretation
    }


def compute_correlation_with_autocorr(df: pd.DataFrame, x_col: str, y_col: str) -> Dict:
    """
    Compute correlation accounting for autocorrelation

    Returns:
        Dict with Pearson r, Spearman rho, p-values, effective sample size
    """
    # Drop NaN values
    clean_df = df[[x_col, y_col]].dropna()

    if len(clean_df) < 10:
        return {
            'n': len(clean_df),
            'pearson_r': np.nan,
            'pearson_p': np.nan,
            'spearman_rho': np.nan,
            'spearman_p': np.nan,
            'x_dw': np.nan,
            'y_dw': np.nan,
            'effective_n': np.nan
        }

    # Pearson correlation
    pearson_r, pearson_p = pearsonr(clean_df[x_col], clean_df[y_col])

    # Spearman correlation (rank-based, more robust to autocorrelation)
    spearman_rho, spearman_p = spearmanr(clean_df[x_col], clean_df[y_col])

    # Test autocorrelation in both variables
    x_autocorr = test_autocorrelation(clean_df[x_col])
    y_autocorr = test_autocorrelation(clean_df[y_col])

    # Effective sample size accounting for autocorrelation
    # Formula: N_eff = N / (1 + 2ρ) where ρ is lag-1 autocorrelation
    x_lag1 = abs(x_autocorr['lag1_autocorrelation'])
    y_lag1 = abs(y_autocorr['lag1_autocorrelation'])
    avg_lag1 = (x_lag1 + y_lag1) / 2

    effective_n = len(clean_df) / (1 + 2 * avg_lag1)

    return {
        'n': len(clean_df),
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_rho': spearman_rho,
        'spearman_p': spearman_p,
        'x_dw': x_autocorr['dw_statistic'],
        'y_dw': y_autocorr['dw_statistic'],
        'x_autocorr': x_lag1,
        'y_autocorr': y_lag1,
        'effective_n': effective_n,
        'x_autocorr_interpretation': x_autocorr['interpretation'],
        'y_autocorr_interpretation': y_autocorr['interpretation']
    }


def compute_fps_quality_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute FPS vs quality metric correlations for all comparisons
    """
    results = []

    quality_metrics = ['ssim', 'lpips', 'flip']

    for comparison in df['comparison'].unique():
        comp_df = df[df['comparison'] == comparison]

        for metric in quality_metrics:
            if metric not in comp_df.columns:
                continue

            corr_result = compute_correlation_with_autocorr(comp_df, 'fps', metric)

            results.append({
                'comparison': comparison,
                'resolution': comp_df['resolution'].iloc[0],
                'metric': metric,
                **corr_result
            })

    return pd.DataFrame(results)


def plot_fps_vs_quality_scatter(df: pd.DataFrame, output_dir: Path):
    """
    Scatter plots: FPS vs quality metrics
    """
    quality_metrics = ['ssim', 'lpips', 'flip']

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for idx, metric in enumerate(quality_metrics):
        ax = axes[idx]

        if metric not in df.columns:
            continue

        # Plot all points
        for comparison in df['comparison'].unique():
            comp_df = df[df['comparison'] == comparison]
            ax.scatter(comp_df['fps'], comp_df[metric],
                      alpha=0.3, s=20, label=comparison)

        # Compute overall correlation
        corr_result = compute_correlation_with_autocorr(df, 'fps', metric)

        # Add regression line
        clean_df = df[['fps', metric]].dropna()
        if len(clean_df) > 10:
            z = np.polyfit(clean_df['fps'], clean_df[metric], 1)
            p = np.poly1d(z)
            x_line = np.linspace(clean_df['fps'].min(), clean_df['fps'].max(), 100)
            ax.plot(x_line, p(x_line), 'r--', linewidth=2, alpha=0.8,
                   label=f"r={corr_result['pearson_r']:.3f}")

        ax.set_xlabel('FPS', fontsize=11)
        ax.set_ylabel(metric.upper(), fontsize=11)
        ax.set_title(f'FPS vs {metric.upper()}\n(Durbin-Watson: {corr_result["y_dw"]:.2f})',
                    fontsize=11, fontweight='bold')
        ax.grid(alpha=0.3)

        # Only show legend for first plot
        if idx == 0:
            ax.legend(fontsize=7, loc='best', ncol=2)

    plt.suptitle('FPS vs Quality Metrics Correlation',
                fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / "fps_vs_quality_scatter.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_dir / 'fps_vs_quality_scatter.png'}")


def plot_temporal_charts(df: pd.DataFrame, output_dir: Path, max_comparisons: int = 4):
    """
    Temporal dual-axis charts showing FPS and quality over time
    """
    quality_metrics = ['ssim', 'lpips']
    comparisons = df['comparison'].unique()[:max_comparisons]

    for comparison in comparisons:
        comp_df = df[df['comparison'] == comparison].copy()
        comp_df = comp_df.sort_values('timestamp')

        fig, axes = plt.subplots(len(quality_metrics), 1, figsize=(14, 8))
        if len(quality_metrics) == 1:
            axes = [axes]

        for idx, metric in enumerate(quality_metrics):
            ax1 = axes[idx]

            if metric not in comp_df.columns:
                continue

            # Plot quality metric
            color1 = 'tab:blue'
            ax1.set_xlabel('Time (seconds)', fontsize=10)
            ax1.set_ylabel(metric.upper(), color=color1, fontsize=10)
            ax1.plot(comp_df['timestamp'], comp_df[metric],
                    color=color1, linewidth=1.5, label=metric.upper())
            ax1.tick_params(axis='y', labelcolor=color1)
            ax1.grid(alpha=0.3)

            # Plot FPS on secondary axis
            ax2 = ax1.twinx()
            color2 = 'tab:red'
            ax2.set_ylabel('FPS', color=color2, fontsize=10)
            ax2.plot(comp_df['timestamp'], comp_df['fps'],
                    color=color2, linewidth=1.5, alpha=0.7, label='FPS')
            ax2.tick_params(axis='y', labelcolor=color2)

            # Compute correlation
            corr_result = compute_correlation_with_autocorr(comp_df, 'fps', metric)

            ax1.set_title(f'{comparison} - FPS vs {metric.upper()}\n' +
                         f'Pearson r={corr_result["pearson_r"]:.3f}, ' +
                         f'DW(FPS)={corr_result["x_dw"]:.2f}, DW({metric})={corr_result["y_dw"]:.2f}',
                         fontsize=11, fontweight='bold')

            # Add legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

        plt.tight_layout()
        safe_name = comparison.replace('/', '_').replace(' ', '_')
        plt.savefig(output_dir / f"temporal_{safe_name}.png", dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  📊 Saved: {output_dir / f'temporal_{safe_name}.png'}")


def plot_correlation_heatmap(corr_df: pd.DataFrame, output_dir: Path):
    """
    Heatmap of FPS-quality correlations across comparisons
    """
    # Pivot: comparisons × metrics
    pivot_pearson = corr_df.pivot(index='comparison', columns='metric', values='pearson_r')
    pivot_spearman = corr_df.pivot(index='comparison', columns='metric', values='spearman_rho')

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Pearson correlation heatmap
    sns.heatmap(pivot_pearson, annot=True, fmt='.3f', cmap='RdBu_r',
               center=0, vmin=-1, vmax=1, ax=axes[0],
               cbar_kws={'label': 'Pearson r'})
    axes[0].set_title('Pearson Correlation: FPS vs Quality Metrics',
                     fontsize=11, fontweight='bold')
    axes[0].set_xlabel('Quality Metric', fontsize=10)
    axes[0].set_ylabel('Comparison', fontsize=10)

    # Spearman correlation heatmap
    sns.heatmap(pivot_spearman, annot=True, fmt='.3f', cmap='RdBu_r',
               center=0, vmin=-1, vmax=1, ax=axes[1],
               cbar_kws={'label': 'Spearman ρ'})
    axes[1].set_title('Spearman Correlation: FPS vs Quality Metrics',
                     fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Quality Metric', fontsize=10)
    axes[1].set_ylabel('Comparison', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / "fps_correlation_heatmap.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_dir / 'fps_correlation_heatmap.png'}")


def generate_report(df: pd.DataFrame, corr_df: pd.DataFrame, output_path: Path):
    """Generate markdown report"""

    report = []
    report.append("# FPS-Quality Correlation Analysis Report\n")
    report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n\n")

    # Overview
    report.append("## Overview\n\n")
    report.append(f"- **Comparisons analyzed:** {df['comparison'].nunique()}\n")
    report.append(f"- **Total frames:** {len(df)}\n")
    report.append(f"- **FPS range:** {df['fps'].min():.1f} - {df['fps'].max():.1f}\n\n")

    # Autocorrelation summary
    report.append("## Temporal Autocorrelation Analysis\n\n")
    report.append("**Durbin-Watson statistic** (closer to 2 = less autocorrelation):\n\n")

    report.append("| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |\n")
    report.append("|-----------|--------|---------|----------|----------|\n")

    for comparison in df['comparison'].unique():
        comp_df = df[df['comparison'] == comparison]

        fps_dw = test_autocorrelation(comp_df['fps'])['dw_statistic']
        ssim_dw = test_autocorrelation(comp_df['ssim'])['dw_statistic'] if 'ssim' in comp_df else np.nan
        lpips_dw = test_autocorrelation(comp_df['lpips'])['dw_statistic'] if 'lpips' in comp_df else np.nan
        flip_dw = test_autocorrelation(comp_df['flip'])['dw_statistic'] if 'flip' in comp_df else np.nan

        report.append(f"| {comparison} | {fps_dw:.2f} | {ssim_dw:.2f} | {lpips_dw:.2f} | {flip_dw:.2f} |\n")

    report.append("\n**Interpretation:**\n")
    report.append("- DW values between 1.5-2.5: no significant autocorrelation\n")
    report.append("- DW < 1.5: positive autocorrelation (adjacent frames similar)\n")
    report.append("- DW > 2.5: negative autocorrelation (adjacent frames different)\n\n")

    # Correlation summary
    report.append("## FPS-Quality Correlation Summary\n\n")

    for metric in ['ssim', 'lpips', 'flip']:
        metric_corr = corr_df[corr_df['metric'] == metric]

        if metric_corr.empty:
            continue

        report.append(f"### {metric.upper()}\n\n")
        report.append("| Comparison | Pearson r | p-value | Spearman ρ | Effective N |\n")
        report.append("|-----------|-----------|---------|------------|-------------|\n")

        for _, row in metric_corr.iterrows():
            report.append(f"| {row['comparison']} | {row['pearson_r']:.3f} | "
                         f"{row['pearson_p']:.4f} | {row['spearman_rho']:.3f} | "
                         f"{row['effective_n']:.0f} |\n")

        # Overall pattern
        avg_pearson = metric_corr['pearson_r'].mean()
        avg_spearman = metric_corr['spearman_rho'].mean()

        report.append(f"\n**Average:** Pearson r = {avg_pearson:.3f}, Spearman ρ = {avg_spearman:.3f}\n\n")

        # Interpretation
        if abs(avg_pearson) < 0.3:
            strength = "weak"
        elif abs(avg_pearson) < 0.7:
            strength = "moderate"
        else:
            strength = "strong"

        direction = "positive" if avg_pearson > 0 else "negative"

        report.append(f"**Interpretation:** {strength.capitalize()} {direction} correlation between FPS and {metric.upper()}\n\n")

    # Key findings
    report.append("## Key Findings\n\n")

    # Autocorrelation severity
    avg_fps_dw = corr_df['x_dw'].mean()
    avg_quality_dw = corr_df['y_dw'].mean()

    report.append(f"1. **Autocorrelation present:** Average FPS DW = {avg_fps_dw:.2f}, Quality DW = {avg_quality_dw:.2f}\n")

    if avg_fps_dw < 1.5 or avg_quality_dw < 1.5:
        report.append("   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent\n")
        report.append("   - Implication: Standard correlation p-values may be inflated\n")
        report.append("   - Effective sample size reduced by ~{:.0f}%\n".format(
            (1 - corr_df['effective_n'].mean() / corr_df['n'].mean()) * 100))
    else:
        report.append("   - ✓ Autocorrelation within acceptable range\n")

    report.append("\n2. **FPS-quality relationship:**\n")

    for metric in ['ssim', 'lpips', 'flip']:
        metric_corr = corr_df[corr_df['metric'] == metric]
        if not metric_corr.empty:
            avg_r = metric_corr['pearson_r'].mean()
            report.append(f"   - FPS vs {metric.upper()}: r = {avg_r:.3f}\n")

    report.append("\n")

    # Write report
    with open(output_path, 'w') as f:
        f.writelines(report)

    print(f"  📄 Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Analyze FPS-quality correlation with autocorrelation handling')
    parser.add_argument('--results-dir', type=str,
                       help='Directory with comparison JSON files')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory')
    parser.add_argument('--max-temporal-plots', type=int, default=4,
                       help='Maximum number of temporal plots to generate')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("FPS-QUALITY CORRELATION ANALYSIS")
    print("="*70)

    # Load data
    if args.results_dir:
        print(f"📂 Loading from: {args.results_dir}")
        df = load_all_per_frame_data(Path(args.results_dir))
    else:
        print("❌ Must provide --results-dir")
        return

    if df.empty:
        print("❌ No per-frame data found. Ensure comparisons have per_frame_data enabled.")
        return

    print(f"✅ Loaded {len(df)} frames from {df['comparison'].nunique()} comparisons\n")

    # Compute correlations
    print("📊 Computing FPS-quality correlations...")
    corr_df = compute_fps_quality_correlations(df)

    # Save data
    df.to_csv(output_dir / "per_frame_data.csv", index=False)
    corr_df.to_csv(output_dir / "fps_quality_correlations.csv", index=False)

    # Generate visualizations
    print("\n🎨 Generating visualizations...")
    plot_fps_vs_quality_scatter(df, output_dir)
    plot_temporal_charts(df, output_dir, args.max_temporal_plots)
    plot_correlation_heatmap(corr_df, output_dir)

    # Generate report
    print("\n📝 Generating analysis report...")
    generate_report(df, corr_df, output_dir / "FPS_CORRELATION_REPORT.md")

    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutputs saved to: {output_dir}/")


if __name__ == "__main__":
    main()
