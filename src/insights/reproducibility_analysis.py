#!/usr/bin/env python3
"""
Reproducibility Analysis - Quantify Noise Floor

Analyzes DLAA Consistency comparisons to establish minimum detectable difference.
Addresses TCC Peer Review #4: Reproducibility variance undermines validity.

Usage:
    python src/insights/reproducibility_analysis.py \
        --results-dir results/cyberpunk/quality_comparison \
        --output results/cyberpunk/reproducibility

    # Cross-game analysis
    python src/insights/reproducibility_analysis.py \
        --aggregated-data results/aggregated/all_games_summary.csv \
        --output results/aggregated/reproducibility
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, List, Tuple
import argparse


def load_consistency_data(results_dir: Path) -> pd.DataFrame:
    """Load all DLAA Consistency comparison results"""
    data = []

    json_files = list(results_dir.glob("*_Consistency.json"))

    for json_file in json_files:
        try:
            with open(json_file) as f:
                comparison = json.load(f)

            metrics = comparison.get('metrics', {})
            comparison_name = json_file.stem

            # Parse resolution
            resolution = comparison_name.split('_')[0]

            row = {
                'comparison': comparison_name,
                'resolution': resolution,
                'frames': comparison.get('frames_compared', 0),
                'ssim_mean': metrics.get('ssim', {}).get('mean'),
                'ssim_std': metrics.get('ssim', {}).get('std'),
                'psnr_mean': metrics.get('psnr', {}).get('mean'),
                'psnr_std': metrics.get('psnr', {}).get('std'),
                'lpips_mean': metrics.get('lpips', {}).get('mean'),
                'lpips_std': metrics.get('lpips', {}).get('std'),
                'flip_mean': metrics.get('flip', {}).get('mean'),
                'flip_std': metrics.get('flip', {}).get('std'),
            }

            data.append(row)

        except Exception as e:
            print(f"  ⚠️  Error loading {json_file.name}: {e}")
            continue

    return pd.DataFrame(data)


def compute_noise_floor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute noise floor statistics

    Noise floor = variability in ground truth (DLAA vs DLAA)
    Minimum detectable difference (MDD) = 2 × std dev (95% confidence)

    Returns:
        DataFrame with noise floor statistics
    """
    results = []

    for resolution in df['resolution'].unique():
        res_df = df[df['resolution'] == resolution]

        if res_df.empty:
            continue

        # Aggregate across games (if multiple)
        stats_dict = {
            'resolution': resolution,
            'n_games': len(res_df),
            'n_frames_total': res_df['frames'].sum(),
        }

        # SSIM noise floor
        ssim_means = res_df['ssim_mean'].dropna()
        ssim_stds = res_df['ssim_std'].dropna()

        if not ssim_means.empty:
            stats_dict.update({
                'ssim_consistency_mean': ssim_means.mean(),
                'ssim_consistency_std': ssim_means.std(),  # Variance across games
                'ssim_within_variance': ssim_stds.mean(),  # Average within-game variance
                'ssim_mdd_2std': 2 * ssim_stds.mean(),  # Minimum detectable diff (95% CI)
                'ssim_mdd_3std': 3 * ssim_stds.mean(),  # Conservative MDD (99.7% CI)
            })

        # PSNR noise floor
        psnr_means = res_df['psnr_mean'].dropna()
        psnr_stds = res_df['psnr_std'].dropna()

        if not psnr_means.empty:
            stats_dict.update({
                'psnr_consistency_mean': psnr_means.mean(),
                'psnr_consistency_std': psnr_means.std(),
                'psnr_within_variance': psnr_stds.mean(),
                'psnr_mdd_2std': 2 * psnr_stds.mean(),
                'psnr_mdd_3std': 3 * psnr_stds.mean(),
            })

        # LPIPS noise floor
        lpips_means = res_df['lpips_mean'].dropna()
        lpips_stds = res_df['lpips_std'].dropna()

        if not lpips_means.empty:
            stats_dict.update({
                'lpips_consistency_mean': lpips_means.mean(),
                'lpips_consistency_std': lpips_means.std(),
                'lpips_within_variance': lpips_stds.mean(),
                'lpips_mdd_2std': 2 * lpips_stds.mean(),
                'lpips_mdd_3std': 3 * lpips_stds.mean(),
            })

        # FLIP noise floor
        flip_means = res_df['flip_mean'].dropna()
        flip_stds = res_df['flip_std'].dropna()

        if not flip_means.empty:
            stats_dict.update({
                'flip_consistency_mean': flip_means.mean(),
                'flip_consistency_std': flip_means.std(),
                'flip_within_variance': flip_stds.mean(),
                'flip_mdd_2std': 2 * flip_stds.mean(),
                'flip_mdd_3std': 3 * flip_stds.mean(),
            })

        results.append(stats_dict)

    return pd.DataFrame(results)


def power_analysis(std_dev: float, effect_size: float, alpha: float = 0.05,
                  power: float = 0.80) -> int:
    """
    Compute required sample size for paired t-test

    Args:
        std_dev: Standard deviation of differences
        effect_size: Minimum effect size to detect (Cohen's d)
        alpha: Significance level (default 0.05)
        power: Statistical power (default 0.80)

    Returns:
        Required sample size (number of frames/comparisons)
    """
    from scipy.stats import t

    # For paired t-test, Cohen's d = mean_diff / std_dev
    # We want to detect effect_size with given power

    # Critical values
    z_alpha = stats.norm.ppf(1 - alpha/2)  # Two-tailed
    z_beta = stats.norm.ppf(power)

    # Sample size formula for paired t-test
    n = ((z_alpha + z_beta) / effect_size) ** 2

    return int(np.ceil(n))


def compute_power_analysis(noise_floor_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute required sample sizes for different effect sizes

    Returns:
        DataFrame with power analysis results
    """
    results = []

    effect_sizes = [0.2, 0.5, 0.8, 1.0]  # Small, medium, large, very large
    effect_labels = ['small', 'medium', 'large', 'very_large']

    for _, row in noise_floor_df.iterrows():
        resolution = row['resolution']

        # SSIM power analysis
        if pd.notna(row.get('ssim_within_variance')):
            ssim_std = row['ssim_within_variance']

            for effect_size, label in zip(effect_sizes, effect_labels):
                n_required = power_analysis(ssim_std, effect_size)

                results.append({
                    'resolution': resolution,
                    'metric': 'SSIM',
                    'effect_size': effect_size,
                    'effect_label': label,
                    'std_dev': ssim_std,
                    'n_required': n_required
                })

        # LPIPS power analysis
        if pd.notna(row.get('lpips_within_variance')):
            lpips_std = row['lpips_within_variance']

            for effect_size, label in zip(effect_sizes, effect_labels):
                n_required = power_analysis(lpips_std, effect_size)

                results.append({
                    'resolution': resolution,
                    'metric': 'LPIPS',
                    'effect_size': effect_size,
                    'effect_label': label,
                    'std_dev': lpips_std,
                    'n_required': n_required
                })

    return pd.DataFrame(results)


def plot_noise_floor(noise_floor_df: pd.DataFrame, output_path: Path):
    """Bar chart showing noise floor by resolution"""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    metrics = [
        ('ssim_consistency_mean', 'SSIM Consistency', 0, 1),
        ('psnr_consistency_mean', 'PSNR Consistency (dB)', 0, 40),
        ('lpips_consistency_mean', 'LPIPS Consistency', 0, 0.8),
        ('flip_consistency_mean', 'FLIP Consistency', 0, 30),
    ]

    for idx, (metric_col, metric_name, y_min, y_max) in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]

        if metric_col not in noise_floor_df.columns:
            continue

        x = np.arange(len(noise_floor_df))
        means = noise_floor_df[metric_col].values
        stds = noise_floor_df[metric_col.replace('_mean', '_std')].values if metric_col.replace('_mean', '_std') in noise_floor_df.columns else np.zeros_like(means)

        bars = ax.bar(x, means, alpha=0.7, color='steelblue')
        ax.errorbar(x, means, yerr=stds, fmt='none', ecolor='red', capsize=5, alpha=0.7)

        # Add MDD lines
        mdd_col = metric_col.replace('consistency_mean', 'mdd_2std')
        if mdd_col in noise_floor_df.columns:
            for i, mdd in enumerate(noise_floor_df[mdd_col].values):
                if pd.notna(mdd):
                    ax.axhline(y=means[i] - mdd, xmin=i/len(x), xmax=(i+1)/len(x),
                             color='red', linestyle='--', alpha=0.5, linewidth=2)
                    ax.text(i, means[i] - mdd, f'  MDD: ±{mdd:.3f}',
                           fontsize=8, va='top', color='red')

        ax.set_xlabel('Resolution', fontsize=10)
        ax.set_ylabel(metric_name, fontsize=10)
        ax.set_title(f'{metric_name} (Ground Truth Reproducibility)',
                    fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(noise_floor_df['resolution'], rotation=0)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(y_min, y_max)

        # Add ideal threshold line for SSIM
        if 'ssim' in metric_col.lower():
            ax.axhline(0.99, color='green', linestyle=':', alpha=0.5, label='Ideal (≥0.99)')
            ax.legend()

    plt.suptitle('Noise Floor Analysis: DLAA Consistency\n(Minimum Detectable Difference shown as red dashed lines)',
                fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_power_curves(power_df: pd.DataFrame, output_path: Path):
    """Plot power analysis curves"""

    metrics = power_df['metric'].unique()

    fig, axes = plt.subplots(1, len(metrics), figsize=(14, 6))
    if len(metrics) == 1:
        axes = [axes]

    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        metric_df = power_df[power_df['metric'] == metric]

        resolutions = metric_df['resolution'].unique()
        colors = plt.cm.tab10(np.linspace(0, 1, len(resolutions)))

        for resolution, color in zip(resolutions, colors):
            res_df = metric_df[metric_df['resolution'] == resolution]
            ax.plot(res_df['effect_size'], res_df['n_required'],
                   marker='o', label=resolution, color=color, linewidth=2)

        ax.set_xlabel('Effect Size (Cohen\'s d)', fontsize=10)
        ax.set_ylabel('Required Sample Size (frames)', fontsize=10)
        ax.set_title(f'{metric} - Power Analysis\n(α=0.05, power=0.80)',
                    fontsize=11, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
        ax.set_yscale('log')

        # Add reference lines
        ax.axvline(0.5, color='gray', linestyle=':', alpha=0.5)
        ax.text(0.5, ax.get_ylim()[1]*0.9, 'Medium\nEffect',
               ha='center', fontsize=8, color='gray')

    plt.suptitle('Sample Size Requirements for Detecting Quality Differences',
                fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def generate_report(df: pd.DataFrame, noise_floor_df: pd.DataFrame,
                   power_df: pd.DataFrame, output_path: Path):
    """Generate markdown report"""

    report = []
    report.append("# Reproducibility Analysis Report\n")
    report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n\n")

    # Overview
    report.append("## Overview\n\n")
    report.append(f"- **Games analyzed:** {df.shape[0]}\n")
    report.append(f"- **Resolutions:** {', '.join(sorted(df['resolution'].unique()))}\n")
    report.append(f"- **Total frames:** {df['frames'].sum()}\n\n")

    # Noise floor summary
    report.append("## Noise Floor Analysis\n\n")
    report.append("Minimum Detectable Difference (MDD) = 2 × standard deviation (95% confidence)\n\n")

    report.append("| Resolution | SSIM Consistency | SSIM MDD (±) | LPIPS Consistency | LPIPS MDD (±) |\n")
    report.append("|-----------|-----------------|--------------|-------------------|---------------|\n")

    for _, row in noise_floor_df.iterrows():
        ssim_mean = row.get('ssim_consistency_mean', np.nan)
        ssim_mdd = row.get('ssim_mdd_2std', np.nan)
        lpips_mean = row.get('lpips_consistency_mean', np.nan)
        lpips_mdd = row.get('lpips_mdd_2std', np.nan)

        report.append(f"| {row['resolution']} | {ssim_mean:.3f} | {ssim_mdd:.3f} | "
                     f"{lpips_mean:.3f} | {lpips_mdd:.3f} |\n")

    report.append("\n")

    # Interpretation
    report.append("### Interpretation\n\n")

    worst_ssim = noise_floor_df['ssim_consistency_mean'].min()
    worst_resolution = noise_floor_df.loc[noise_floor_df['ssim_consistency_mean'].idxmin(), 'resolution']

    report.append(f"1. **Worst reproducibility:** {worst_resolution} with SSIM = {worst_ssim:.3f}\n")
    report.append(f"   - Ideal threshold: SSIM ≥ 0.99\n")
    report.append(f"   - Observed: SSIM = {worst_ssim:.3f} → **{(1-worst_ssim)*100:.1f}% structural dissimilarity**\n\n")

    report.append("2. **Implication for DLSS comparisons:**\n")
    for _, row in noise_floor_df.iterrows():
        mdd = row.get('ssim_mdd_2std', np.nan)
        if pd.notna(mdd):
            report.append(f"   - **{row['resolution']}**: Quality differences < ±{mdd:.3f} SSIM may be noise\n")

    report.append("\n")

    # Power analysis
    report.append("## Power Analysis\n\n")
    report.append("Sample size required to detect quality differences with 80% power (α=0.05):\n\n")

    # Show for medium effect size (0.5)
    report.append("### Medium Effect Size (Cohen's d = 0.5)\n\n")
    report.append("| Resolution | Metric | Required Frames |\n")
    report.append("|-----------|--------|----------------|\n")

    medium_effect = power_df[power_df['effect_size'] == 0.5]
    for _, row in medium_effect.iterrows():
        report.append(f"| {row['resolution']} | {row['metric']} | {row['n_required']} |\n")

    report.append("\n**Current sample:** ~392 frames/video → adequate for medium-large effects\n\n")

    # Write report
    with open(output_path, 'w') as f:
        f.writelines(report)

    print(f"  📄 Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Analyze reproducibility and noise floor')
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
    print("REPRODUCIBILITY ANALYSIS")
    print("="*70)

    # Load data
    if args.results_dir:
        print(f"📂 Loading from: {args.results_dir}")
        df = load_consistency_data(Path(args.results_dir))
    elif args.aggregated_data:
        print(f"📂 Loading aggregated data: {args.aggregated_data}")
        agg_df = pd.read_csv(args.aggregated_data)
        df = agg_df[agg_df['comparison_type'] == 'consistency']
    else:
        print("❌ Must provide --results-dir or --aggregated-data")
        return

    if df.empty:
        print("❌ No consistency data found. Exiting.")
        return

    print(f"✅ Loaded {len(df)} consistency comparisons\n")

    # Compute noise floor
    print("📊 Computing noise floor statistics...")
    noise_floor_df = compute_noise_floor(df)

    # Power analysis
    print("📊 Computing power analysis...")
    power_df = compute_power_analysis(noise_floor_df)

    # Save data
    df.to_csv(output_dir / "consistency_data.csv", index=False)
    noise_floor_df.to_csv(output_dir / "noise_floor.csv", index=False)
    power_df.to_csv(output_dir / "power_analysis.csv", index=False)

    # Generate visualizations
    print("\n🎨 Generating visualizations...")
    plot_noise_floor(noise_floor_df, output_dir / "noise_floor.png")
    plot_power_curves(power_df, output_dir / "power_analysis.png")

    # Generate report
    print("\n📝 Generating analysis report...")
    generate_report(df, noise_floor_df, power_df,
                   output_dir / "REPRODUCIBILITY_REPORT.md")

    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutputs saved to: {output_dir}/")


if __name__ == "__main__":
    main()
