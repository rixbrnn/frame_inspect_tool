#!/usr/bin/env python3
"""
Cross-Game Aggregation Analysis

Aggregates quality metrics from all games into unified tables and visualizations.
Addresses TCC Peer Review #5: Complete multi-game analysis.

Usage:
    python src/insights/aggregate_all_games.py \
        --results-dir results \
        --output results/aggregated \
        --generate-charts

Output:
    - all_games_summary.csv: Table with all metrics across games
    - all_games_summary.json: Machine-readable version
    - Charts:
      - ssim_heatmap_by_game.png: SSIM heatmap (game × mode × resolution)
      - mean_metrics_by_mode.png: Average metrics per mode across all games
      - variance_by_game.png: Which games show most variability
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from typing import Dict, List, Tuple
from collections import defaultdict


def load_all_game_results(results_dir: Path) -> pd.DataFrame:
    """
    Load all comparison results from all game directories

    Returns:
        DataFrame with columns: game, resolution, mode, frames, ssim_mean, ssim_std,
                                psnr_mean, psnr_std, lpips_mean, lpips_std,
                                flip_mean, flip_std, optical_flow_mean, optical_flow_std
    """
    all_data = []

    # Iterate through all game directories
    for game_dir in results_dir.iterdir():
        if not game_dir.is_dir():
            continue

        game_name = game_dir.name
        comparison_dir = game_dir / "quality_comparison"

        if not comparison_dir.exists():
            print(f"⏭️  Skipping {game_name} - no quality_comparison directory")
            continue

        # Load all comparison JSON files
        json_files = list(comparison_dir.glob("*.json"))
        json_files = [f for f in json_files if not f.name.startswith("summary")]

        if not json_files:
            print(f"⚠️  {game_name}: No comparison files found")
            continue

        print(f"📊 Loading {game_name}: {len(json_files)} comparisons")

        for json_file in json_files:
            try:
                with open(json_file) as f:
                    data = json.load(f)

                # Parse comparison name: e.g., "1080p_DLAA_vs_Quality" or "1440p_DLAA_Consistency"
                comparison_name = json_file.stem
                parts = comparison_name.split('_')

                resolution = parts[0]

                # Determine mode
                if 'Consistency' in comparison_name:
                    mode = 'Consistency'
                    comparison_type = 'consistency'
                elif 'vs' in comparison_name:
                    vs_idx = parts.index('vs')
                    mode = '_'.join(parts[vs_idx+1:])
                    comparison_type = 'dlss_mode'
                else:
                    print(f"  ⚠️  Could not parse: {comparison_name}")
                    continue

                # Extract metrics
                metrics = data.get('metrics', {})

                row = {
                    'game': game_name,
                    'resolution': resolution,
                    'mode': mode,
                    'comparison_type': comparison_type,
                    'comparison_name': comparison_name,
                    'frames': data.get('frames_compared', 0),
                }

                # Add all metrics
                for metric_name in ['ssim', 'mse', 'psnr', 'lpips', 'flip', 'optical_flow_consistency']:
                    metric_data = metrics.get(metric_name, {})
                    if metric_data:
                        row[f'{metric_name}_mean'] = metric_data.get('mean')
                        row[f'{metric_name}_std'] = metric_data.get('std')
                        row[f'{metric_name}_min'] = metric_data.get('min')
                        row[f'{metric_name}_max'] = metric_data.get('max')
                        row[f'{metric_name}_median'] = metric_data.get('median')
                    else:
                        row[f'{metric_name}_mean'] = None
                        row[f'{metric_name}_std'] = None
                        row[f'{metric_name}_min'] = None
                        row[f'{metric_name}_max'] = None
                        row[f'{metric_name}_median'] = None

                all_data.append(row)

            except Exception as e:
                print(f"  ❌ Error loading {json_file.name}: {e}")
                continue

    df = pd.DataFrame(all_data)
    print(f"\n✅ Loaded {len(df)} comparisons from {df['game'].nunique()} games")
    return df


def generate_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary statistics across games"""

    # Filter only DLSS mode comparisons (exclude Consistency)
    dlss_df = df[df['comparison_type'] == 'dlss_mode'].copy()

    # Group by resolution and mode, compute statistics across games
    summary = dlss_df.groupby(['resolution', 'mode']).agg({
        'ssim_mean': ['mean', 'std', 'min', 'max', 'count'],
        'psnr_mean': ['mean', 'std', 'min', 'max'],
        'lpips_mean': ['mean', 'std', 'min', 'max'],
        'flip_mean': ['mean', 'std', 'min', 'max'],
    }).round(4)

    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()

    return summary


def plot_ssim_heatmap_by_game(df: pd.DataFrame, output_path: Path):
    """
    Heatmap showing SSIM for each game × mode × resolution
    """
    # Filter DLSS modes only
    dlss_df = df[df['comparison_type'] == 'dlss_mode'].copy()

    # Create separate heatmap for each resolution
    resolutions = sorted(dlss_df['resolution'].unique())

    fig, axes = plt.subplots(1, len(resolutions), figsize=(18, 8))
    if len(resolutions) == 1:
        axes = [axes]

    for idx, resolution in enumerate(resolutions):
        res_df = dlss_df[dlss_df['resolution'] == resolution]

        # Pivot: games × modes, values = SSIM
        pivot = res_df.pivot(index='game', columns='mode', values='ssim_mean')

        # Sort columns by typical DLSS mode order
        mode_order = ['Quality', 'Balanced', 'Performance', 'Ultra_Performance']
        existing_modes = [m for m in mode_order if m in pivot.columns]
        pivot = pivot[existing_modes]

        # Create heatmap
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.3f',
            cmap='RdYlGn',
            vmin=0.5,
            vmax=1.0,
            cbar_kws={'label': 'SSIM'},
            ax=axes[idx],
            linewidths=0.5,
            linecolor='gray'
        )
        axes[idx].set_title(f'{resolution} - SSIM by Game & Mode', fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('DLSS Mode', fontsize=10)
        axes[idx].set_ylabel('Game', fontsize=10)

    plt.suptitle('SSIM Comparison Across All Games', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_mean_metrics_by_mode(df: pd.DataFrame, output_path: Path):
    """
    Bar chart showing average metrics per mode (averaged across all games)
    """
    dlss_df = df[df['comparison_type'] == 'dlss_mode'].copy()

    # Group by resolution and mode
    grouped = dlss_df.groupby(['resolution', 'mode']).agg({
        'ssim_mean': 'mean',
        'psnr_mean': 'mean',
        'lpips_mean': 'mean',
        'flip_mean': 'mean',
    }).reset_index()

    # Create subplots for each metric
    metrics = [
        ('ssim_mean', 'SSIM', 0, 1),
        ('psnr_mean', 'PSNR (dB)', 15, 30),
        ('lpips_mean', 'LPIPS', 0, 0.6),
        ('flip_mean', 'FLIP', 0, 15),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for idx, (metric_col, metric_name, y_min, y_max) in enumerate(metrics):
        ax = axes[idx]

        # Prepare data for grouped bar chart
        resolutions = sorted(grouped['resolution'].unique())
        modes = ['Quality', 'Balanced', 'Performance', 'Ultra_Performance']
        existing_modes = [m for m in modes if m in grouped['mode'].values]

        x = np.arange(len(existing_modes))
        width = 0.25

        for i, resolution in enumerate(resolutions):
            res_data = grouped[grouped['resolution'] == resolution]
            values = [res_data[res_data['mode'] == mode][metric_col].values[0]
                     if len(res_data[res_data['mode'] == mode]) > 0 else 0
                     for mode in existing_modes]

            offset = width * (i - len(resolutions)/2 + 0.5)
            ax.bar(x + offset, values, width, label=resolution, alpha=0.8)

        ax.set_xlabel('DLSS Mode', fontsize=10)
        ax.set_ylabel(metric_name, fontsize=10)
        ax.set_title(f'{metric_name} by Mode (Averaged Across Games)', fontsize=11, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(existing_modes, rotation=15, ha='right')
        ax.legend(title='Resolution')
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(y_min, y_max)

    plt.suptitle('Average Metrics Across All Games', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_variance_by_game(df: pd.DataFrame, output_path: Path):
    """
    Bar chart showing which games have most metric variability
    """
    dlss_df = df[df['comparison_type'] == 'dlss_mode'].copy()

    # Calculate variance per game (std dev of SSIM across all modes/resolutions)
    variance = dlss_df.groupby('game').agg({
        'ssim_mean': ['std', 'mean'],
        'psnr_mean': 'std',
        'lpips_mean': 'std',
        'flip_mean': 'std',
    }).reset_index()

    variance.columns = ['game', 'ssim_std', 'ssim_mean', 'psnr_std', 'lpips_std', 'flip_std']
    variance = variance.sort_values('ssim_std', ascending=False)

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))

    x = np.arange(len(variance))

    ax.bar(x, variance['ssim_std'], alpha=0.7, color='steelblue')
    ax.set_xlabel('Game', fontsize=11)
    ax.set_ylabel('SSIM Standard Deviation', fontsize=11)
    ax.set_title('Metric Variability by Game\n(Higher = More difference between DLSS modes)',
                 fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(variance['game'], rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)

    # Annotate with mean SSIM
    for i, (idx, row) in enumerate(variance.iterrows()):
        ax.text(i, row['ssim_std'] + 0.01, f"μ={row['ssim_mean']:.2f}",
               ha='center', va='bottom', fontsize=8, color='gray')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_consistency_comparison(df: pd.DataFrame, output_path: Path):
    """
    Chart showing reproducibility (DLAA Consistency) across games and resolutions
    """
    consistency_df = df[df['comparison_type'] == 'consistency'].copy()

    if consistency_df.empty:
        print("  ⚠️  No consistency data found, skipping reproducibility chart")
        return

    # Pivot: games × resolutions, values = SSIM
    pivot = consistency_df.pivot(index='game', columns='resolution', values='ssim_mean')

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        pivot,
        annot=True,
        fmt='.3f',
        cmap='RdYlGn',
        vmin=0.5,
        vmax=1.0,
        cbar_kws={'label': 'SSIM (DLAA run1 vs run2)'},
        ax=ax,
        linewidths=0.5,
        linecolor='gray'
    )

    ax.set_title('Reproducibility Analysis: DLAA Consistency\n(SSIM between two independent DLAA captures)',
                fontsize=12, fontweight='bold')
    ax.set_xlabel('Resolution', fontsize=10)
    ax.set_ylabel('Game', fontsize=10)

    # Add threshold line annotation
    ax.text(0.5, -0.15, 'Ideal threshold: SSIM ≥ 0.99 | Observed: 0.56-0.82 (high variance)',
           ha='center', transform=ax.transAxes, fontsize=9, color='red', style='italic')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def generate_markdown_report(df: pd.DataFrame, summary_df: pd.DataFrame, output_path: Path):
    """
    Generate markdown report with key findings
    """
    dlss_df = df[df['comparison_type'] == 'dlss_mode'].copy()
    consistency_df = df[df['comparison_type'] == 'consistency'].copy()

    report = []
    report.append("# Cross-Game Analysis Report\n")
    report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n\n")

    # Overview
    report.append("## Overview\n\n")
    report.append(f"- **Games analyzed:** {df['game'].nunique()}\n")
    report.append(f"- **Total comparisons:** {len(df)}\n")
    report.append(f"- **DLSS mode comparisons:** {len(dlss_df)}\n")
    report.append(f"- **Consistency checks:** {len(consistency_df)}\n\n")

    # Games list
    report.append("### Games Included\n\n")
    for game in sorted(df['game'].unique()):
        game_df = df[df['game'] == game]
        comparisons = len(game_df)
        resolutions = sorted(game_df['resolution'].unique())
        report.append(f"- **{game}**: {comparisons} comparisons ({', '.join(resolutions)})\n")
    report.append("\n")

    # Key findings - SSIM anomalies
    report.append("## Key Findings\n\n")
    report.append("### 1. SSIM Counter-Intuitive Rankings\n\n")

    # Find cases where Performance > Quality in SSIM
    for resolution in ['1080p', '1440p', '4K']:
        res_df = dlss_df[dlss_df['resolution'] == resolution]

        quality_df = res_df[res_df['mode'] == 'Quality']
        perf_df = res_df[res_df['mode'] == 'Performance']

        if not quality_df.empty and not perf_df.empty:
            quality_mean = quality_df['ssim_mean'].mean()
            perf_mean = perf_df['ssim_mean'].mean()

            if perf_mean > quality_mean:
                diff = ((perf_mean - quality_mean) / quality_mean) * 100
                report.append(f"- **{resolution}**: Performance SSIM ({perf_mean:.3f}) > Quality SSIM ({quality_mean:.3f}) "
                            f"by {diff:.1f}% ⚠️\n")
    report.append("\n")

    # Reproducibility analysis
    report.append("### 2. Reproducibility (DLAA Consistency)\n\n")
    if not consistency_df.empty:
        report.append("SSIM between two independent DLAA captures:\n\n")
        for resolution in ['1080p', '1440p', '4K']:
            res_consistency = consistency_df[consistency_df['resolution'] == resolution]
            if not res_consistency.empty:
                mean_ssim = res_consistency['ssim_mean'].mean()
                std_ssim = res_consistency['ssim_mean'].std()
                report.append(f"- **{resolution}**: {mean_ssim:.3f} ± {std_ssim:.3f}")
                if mean_ssim < 0.80:
                    report.append(" ⚠️ HIGH VARIANCE")
                report.append("\n")
        report.append("\n**Implication:** High variance in ground truth (DLAA) affects confidence in DLSS comparisons.\n\n")

    # Summary statistics table
    report.append("### 3. Average Metrics by Mode (Across All Games)\n\n")
    report.append("| Resolution | Mode | SSIM (mean±std) | PSNR (mean±std) | LPIPS (mean±std) | Games |\n")
    report.append("|-----------|------|-----------------|-----------------|------------------|-------|\n")

    for _, row in summary_df.iterrows():
        report.append(f"| {row['resolution']} | {row['mode']} | "
                     f"{row['ssim_mean_mean']:.3f}±{row['ssim_mean_std']:.3f} | "
                     f"{row['psnr_mean_mean']:.1f}±{row['psnr_mean_std']:.1f} | "
                     f"{row['lpips_mean_mean']:.3f}±{row['lpips_mean_std']:.3f} | "
                     f"{int(row['ssim_mean_count'])} |\n")
    report.append("\n")

    # Write report
    with open(output_path, 'w') as f:
        f.writelines(report)

    print(f"  📄 Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Aggregate quality metrics from all games')
    parser.add_argument('--results-dir', type=str, default='results',
                       help='Directory containing game result folders')
    parser.add_argument('--output', type=str, default='results/aggregated',
                       help='Output directory for aggregated results')
    parser.add_argument('--generate-charts', action='store_true',
                       help='Generate visualization charts')

    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("CROSS-GAME AGGREGATION ANALYSIS")
    print("="*70)
    print(f"Results directory: {results_dir}")
    print(f"Output directory: {output_dir}")
    print()

    # Load all results
    print("📂 Loading results from all games...")
    df = load_all_game_results(results_dir)

    if df.empty:
        print("❌ No data found. Exiting.")
        return

    # Save raw aggregated data
    csv_path = output_dir / "all_games_summary.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n💾 Saved raw data: {csv_path}")

    json_path = output_dir / "all_games_summary.json"
    df.to_json(json_path, orient='records', indent=2)
    print(f"💾 Saved JSON: {json_path}")

    # Generate summary statistics
    print("\n📊 Computing summary statistics...")
    summary_df = generate_summary_statistics(df)
    summary_csv = output_dir / "summary_by_mode.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"💾 Saved summary: {summary_csv}")

    # Generate charts
    if args.generate_charts:
        print("\n🎨 Generating visualization charts...")

        plot_ssim_heatmap_by_game(df, output_dir / "ssim_heatmap_by_game.png")
        plot_mean_metrics_by_mode(df, output_dir / "mean_metrics_by_mode.png")
        plot_variance_by_game(df, output_dir / "variance_by_game.png")
        plot_consistency_comparison(df, output_dir / "reproducibility_analysis.png")

    # Generate markdown report
    print("\n📝 Generating analysis report...")
    generate_markdown_report(df, summary_df, output_dir / "ANALYSIS_REPORT.md")

    print("\n" + "="*70)
    print("✅ AGGREGATION COMPLETE")
    print("="*70)
    print(f"\nOutputs saved to: {output_dir}/")
    print("  - all_games_summary.csv (raw data)")
    print("  - summary_by_mode.csv (statistics)")
    print("  - ANALYSIS_REPORT.md (findings)")
    if args.generate_charts:
        print("  - *.png (charts)")


if __name__ == "__main__":
    main()
