#!/usr/bin/env python3
"""
Cross-Resolution Analysis - Sweet Spot Identification

Compares DLSS modes across resolutions to find optimal FPS/quality tradeoffs.
Addresses TCC Results Section 5.2.5: Sweet spot identification.

Usage:
    python src/insights/cross_resolution_analysis.py \
        --aggregated-data results/aggregated/all_games_summary.csv \
        --output results/aggregated/cross_resolution

    # With FPS data (if available)
    python src/insights/cross_resolution_analysis.py \
        --aggregated-data results/aggregated/all_games_summary.csv \
        --fps-data results/aggregated/fps_data.csv \
        --output results/aggregated/cross_resolution
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial import ConvexHull
from typing import Dict, List, Tuple, Optional
import argparse


def load_data(aggregated_csv: Path, fps_csv: Optional[Path] = None) -> pd.DataFrame:
    """
    Load aggregated comparison data and optionally FPS data

    Returns:
        DataFrame with quality metrics and FPS (if available)
    """
    df = pd.read_csv(aggregated_csv)

    # Filter only DLSS mode comparisons
    df = df[df['comparison_type'] == 'dlss_mode'].copy()

    # Rename columns for consistency
    if 'ssim_mean' in df.columns:
        df = df.rename(columns={
            'ssim_mean': 'ssim', 'psnr_mean': 'psnr',
            'lpips_mean': 'lpips', 'flip_mean': 'flip'
        })

    # Load FPS data if provided
    if fps_csv and fps_csv.exists():
        fps_df = pd.read_csv(fps_csv)
        # Merge on game, resolution, mode
        df = df.merge(fps_df, on=['game', 'resolution', 'mode'], how='left')

    return df


def create_configuration_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create table of all configurations (game × resolution × mode)
    with aggregated metrics
    """
    # Group by game, resolution, mode
    configs = []

    for (game, resolution, mode), group in df.groupby(['game', 'resolution', 'mode']):
        config = {
            'game': game,
            'resolution': resolution,
            'mode': mode,
            'config_name': f"{resolution}_{mode}",
            'ssim': group['ssim'].mean(),
            'psnr': group['psnr'].mean(),
            'lpips': group['lpips'].mean(),
            'flip': group['flip'].mean(),
        }

        # Add FPS if available
        if 'fps' in group.columns:
            config['fps'] = group['fps'].mean()

        configs.append(config)

    return pd.DataFrame(configs)


def compute_efficiency_score(df: pd.DataFrame, weights: Optional[Dict] = None) -> pd.DataFrame:
    """
    Compute efficiency score balancing FPS and quality

    Args:
        df: DataFrame with configurations
        weights: Optional weights dict, e.g., {'fps': 0.4, 'ssim': 0.3, 'lpips': 0.3}

    Returns:
        DataFrame with efficiency scores
    """
    if weights is None:
        # Default weights: balanced FPS and quality
        weights = {'fps': 0.4, 'ssim': 0.3, 'lpips': 0.3}

    df = df.copy()

    # Normalize metrics to 0-1 scale
    if 'fps' in df.columns and pd.notna(df['fps']).any():
        df['fps_norm'] = (df['fps'] - df['fps'].min()) / (df['fps'].max() - df['fps'].min())
    else:
        # If no FPS data, estimate based on typical DLSS performance
        # Ultra Performance > Performance > Balanced > Quality
        mode_fps_estimate = {
            'Ultra_Performance': 1.0,
            'Performance': 0.8,
            'Balanced': 0.6,
            'Quality': 0.4
        }
        df['fps_norm'] = df['mode'].map(mode_fps_estimate)

    # SSIM: higher is better
    df['ssim_norm'] = (df['ssim'] - df['ssim'].min()) / (df['ssim'].max() - df['ssim'].min())

    # LPIPS: lower is better (invert)
    df['lpips_norm'] = 1 - ((df['lpips'] - df['lpips'].min()) / (df['lpips'].max() - df['lpips'].min()))

    # Compute weighted efficiency score
    df['efficiency_score'] = (
        weights.get('fps', 0) * df['fps_norm'] +
        weights.get('ssim', 0) * df['ssim_norm'] +
        weights.get('lpips', 0) * df['lpips_norm']
    )

    return df


def find_pareto_frontier(df: pd.DataFrame, x_col: str = 'fps_norm',
                        y_col: str = 'ssim') -> List[int]:
    """
    Find Pareto optimal points (maximize both FPS and quality)

    Returns:
        List of indices of Pareto optimal configurations
    """
    # Higher is better for both metrics
    points = df[[x_col, y_col]].values

    # Find Pareto frontier
    pareto_indices = []

    for i, point in enumerate(points):
        is_pareto = True

        for j, other_point in enumerate(points):
            if i == j:
                continue

            # Check if other point dominates this point
            if (other_point[0] >= point[0] and other_point[1] >= point[1] and
                (other_point[0] > point[0] or other_point[1] > point[1])):
                is_pareto = False
                break

        if is_pareto:
            pareto_indices.append(i)

    return pareto_indices


def identify_sweet_spots(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify sweet spot configurations per game and resolution

    Sweet spot = highest efficiency score in Pareto frontier
    """
    sweet_spots = []

    for game in df['game'].unique():
        game_df = df[df['game'] == game].copy()

        for resolution in game_df['resolution'].unique():
            res_df = game_df[game_df['resolution'] == resolution].copy()

            if len(res_df) < 2:
                continue

            # Find Pareto frontier
            pareto_indices = find_pareto_frontier(res_df, 'fps_norm', 'ssim')

            if not pareto_indices:
                continue

            pareto_configs = res_df.iloc[pareto_indices]

            # Sweet spot = highest efficiency in Pareto frontier
            best_idx = pareto_configs['efficiency_score'].idxmax()
            sweet_spot = res_df.loc[best_idx]

            sweet_spots.append({
                'game': game,
                'resolution': resolution,
                'sweet_spot_mode': sweet_spot['mode'],
                'sweet_spot_config': sweet_spot['config_name'],
                'ssim': sweet_spot['ssim'],
                'lpips': sweet_spot['lpips'],
                'fps_norm': sweet_spot['fps_norm'],
                'efficiency_score': sweet_spot['efficiency_score'],
                'is_pareto_optimal': True
            })

    return pd.DataFrame(sweet_spots)


def compare_across_resolutions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare equivalent modes across resolutions
    E.g., 1080p Performance vs 1440p Quality
    """
    comparisons = []

    for game in df['game'].unique():
        game_df = df[df['game'] == game]

        # Get all unique configurations for this game
        configs = game_df.to_dict('records')

        # Compare every pair
        for i, config1 in enumerate(configs):
            for config2 in configs[i+1:]:
                # Skip same resolution
                if config1['resolution'] == config2['resolution']:
                    continue

                comparison = {
                    'game': game,
                    'config1': f"{config1['resolution']}_{config1['mode']}",
                    'config2': f"{config2['resolution']}_{config2['mode']}",
                    'ssim_diff': config1['ssim'] - config2['ssim'],
                    'lpips_diff': config1['lpips'] - config2['lpips'],
                    'fps_diff': config1.get('fps_norm', 0) - config2.get('fps_norm', 0),
                }

                # Determine winner
                if comparison['ssim_diff'] > 0 and comparison['fps_diff'] > 0:
                    comparison['winner'] = 'config1'
                    comparison['tradeoff'] = 'both_better'
                elif comparison['ssim_diff'] < 0 and comparison['fps_diff'] < 0:
                    comparison['winner'] = 'config2'
                    comparison['tradeoff'] = 'both_better'
                elif comparison['ssim_diff'] > 0 and comparison['fps_diff'] < 0:
                    comparison['winner'] = 'depends'
                    comparison['tradeoff'] = 'quality_vs_fps'
                else:
                    comparison['winner'] = 'depends'
                    comparison['tradeoff'] = 'fps_vs_quality'

                comparisons.append(comparison)

    return pd.DataFrame(comparisons)


def plot_efficiency_scatter(df: pd.DataFrame, output_path: Path):
    """
    Scatter plot: FPS vs SSIM with efficiency scores
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Color by efficiency score
    scatter = ax.scatter(df['fps_norm'], df['ssim'],
                        c=df['efficiency_score'],
                        cmap='RdYlGn', s=100, alpha=0.7,
                        edgecolors='black', linewidth=1)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Efficiency Score', fontsize=11)

    # Annotate configurations
    for _, row in df.iterrows():
        ax.annotate(f"{row['resolution']}\n{row['mode'][:4]}",
                   (row['fps_norm'], row['ssim']),
                   fontsize=7, ha='center', alpha=0.7)

    # Find and plot Pareto frontier
    pareto_indices = find_pareto_frontier(df, 'fps_norm', 'ssim')
    pareto_df = df.iloc[pareto_indices].sort_values('fps_norm')

    ax.plot(pareto_df['fps_norm'], pareto_df['ssim'],
           'r--', linewidth=2, alpha=0.8, label='Pareto Frontier')

    ax.set_xlabel('FPS (Normalized)', fontsize=11)
    ax.set_ylabel('SSIM', fontsize=11)
    ax.set_title('Configuration Efficiency: FPS vs Quality\n(Pareto Frontier in Red)',
                fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_sweet_spots_by_game(sweet_spots_df: pd.DataFrame, output_path: Path):
    """
    Bar chart showing sweet spot modes per game and resolution
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    # Prepare data
    games = sorted(sweet_spots_df['game'].unique())
    resolutions = sorted(sweet_spots_df['resolution'].unique())

    x = np.arange(len(games))
    width = 0.25

    mode_colors = {
        'Quality': '#1f77b4',
        'Balanced': '#ff7f0e',
        'Performance': '#2ca02c',
        'Ultra_Performance': '#d62728'
    }

    for i, resolution in enumerate(resolutions):
        res_df = sweet_spots_df[sweet_spots_df['resolution'] == resolution]

        modes = []
        colors = []
        for game in games:
            game_sweet = res_df[res_df['game'] == game]
            if not game_sweet.empty:
                mode = game_sweet.iloc[0]['sweet_spot_mode']
                modes.append(mode)
                colors.append(mode_colors.get(mode, 'gray'))
            else:
                modes.append('')
                colors.append('lightgray')

        # Use efficiency score as bar height
        heights = []
        for game in games:
            game_sweet = res_df[res_df['game'] == game]
            if not game_sweet.empty:
                heights.append(game_sweet.iloc[0]['efficiency_score'])
            else:
                heights.append(0)

        offset = width * (i - len(resolutions)/2 + 0.5)
        bars = ax.bar(x + offset, heights, width, label=resolution, alpha=0.8)

        # Color each bar individually by mode
        for bar, color in zip(bars, colors):
            bar.set_color(color)

        # Add mode labels on bars
        for j, (bar, mode) in enumerate(zip(bars, modes)):
            if mode and heights[j] > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                       mode[:4], ha='center', va='bottom', fontsize=7, rotation=90)

    ax.set_xlabel('Game', fontsize=11)
    ax.set_ylabel('Efficiency Score', fontsize=11)
    ax.set_title('Sweet Spot Modes by Game and Resolution',
                fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(games, rotation=45, ha='right')
    ax.legend(title='Resolution')
    ax.grid(axis='y', alpha=0.3)

    # Add mode color legend
    from matplotlib.patches import Patch
    mode_patches = [Patch(color=color, label=mode) for mode, color in mode_colors.items()]
    ax.legend(handles=mode_patches, loc='upper left', title='DLSS Mode',
             bbox_to_anchor=(1.02, 1), borderaxespad=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def plot_cross_resolution_comparison(df: pd.DataFrame, output_path: Path):
    """
    Heatmap comparing configurations across resolutions
    """
    # Create pivot: resolution_mode × metrics
    df['config'] = df['resolution'] + '_' + df['mode']

    # Average across games
    avg_df = df.groupby('config').agg({
        'ssim': 'mean',
        'lpips': 'mean',
        'efficiency_score': 'mean'
    }).reset_index()

    # Sort by efficiency
    avg_df = avg_df.sort_values('efficiency_score', ascending=False)

    # Create comparison matrix
    fig, axes = plt.subplots(1, 3, figsize=(18, 8))

    metrics = [
        ('ssim', 'SSIM (Higher = Better)'),
        ('lpips', 'LPIPS (Lower = Better)'),
        ('efficiency_score', 'Efficiency Score')
    ]

    for idx, (metric, title) in enumerate(metrics):
        ax = axes[idx]

        # Create heatmap data
        data = avg_df[[metric]].T

        sns.heatmap(data, annot=True, fmt='.3f',
                   cmap='RdYlGn' if metric != 'lpips' else 'RdYlGn_r',
                   xticklabels=avg_df['config'],
                   yticklabels=[title],
                   cbar_kws={'label': title},
                   ax=ax)

        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xticklabels(avg_df['config'], rotation=45, ha='right')

    plt.suptitle('Cross-Resolution Configuration Comparison\n(Averaged Across Games)',
                fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  📊 Saved: {output_path}")


def generate_report(df: pd.DataFrame, sweet_spots_df: pd.DataFrame,
                   cross_res_df: pd.DataFrame, output_path: Path):
    """Generate markdown report with recommendations"""

    report = []
    report.append("# Cross-Resolution Analysis Report\n")
    report.append(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n\n")

    # Overview
    report.append("## Overview\n\n")
    report.append(f"- **Games analyzed:** {df['game'].nunique()}\n")
    report.append(f"- **Configurations:** {len(df)} (game × resolution × mode combinations)\n")
    report.append(f"- **Resolutions:** {', '.join(sorted(df['resolution'].unique()))}\n")
    report.append(f"- **Modes:** {', '.join(sorted(df['mode'].unique()))}\n\n")

    # Sweet spots summary
    report.append("## Sweet Spot Recommendations\n\n")
    report.append("### By Resolution\n\n")

    for resolution in sorted(sweet_spots_df['resolution'].unique()):
        res_sweet = sweet_spots_df[sweet_spots_df['resolution'] == resolution]

        # Find most common sweet spot mode
        mode_counts = res_sweet['sweet_spot_mode'].value_counts()

        report.append(f"#### {resolution}\n\n")
        report.append(f"**Most common sweet spot:** {mode_counts.index[0]} ({mode_counts.iloc[0]}/{len(res_sweet)} games)\n\n")

        report.append("| Game | Mode | SSIM | LPIPS | Efficiency |\n")
        report.append("|------|------|------|-------|------------|\n")

        for _, row in res_sweet.iterrows():
            report.append(f"| {row['game']} | {row['sweet_spot_mode']} | "
                         f"{row['ssim']:.3f} | {row['lpips']:.3f} | "
                         f"{row['efficiency_score']:.3f} |\n")
        report.append("\n")

    # Overall recommendations
    report.append("## General Recommendations\n\n")

    # Find overall best configurations
    top_configs = df.nlargest(10, 'efficiency_score')

    report.append("### Top 10 Configurations (All Games)\n\n")
    report.append("| Rank | Game | Config | SSIM | LPIPS | Efficiency |\n")
    report.append("|------|------|--------|------|-------|------------|\n")

    for rank, (_, row) in enumerate(top_configs.iterrows(), 1):
        report.append(f"| {rank} | {row['game']} | {row['resolution']} {row['mode']} | "
                     f"{row['ssim']:.3f} | {row['lpips']:.3f} | "
                     f"{row['efficiency_score']:.3f} |\n")
    report.append("\n")

    # Key insights
    report.append("## Key Insights\n\n")

    # Most efficient mode overall
    mode_efficiency = df.groupby('mode')['efficiency_score'].mean().sort_values(ascending=False)
    report.append(f"1. **Most efficient mode overall:** {mode_efficiency.index[0]} "
                 f"(avg efficiency: {mode_efficiency.iloc[0]:.3f})\n")

    # Resolution with best quality
    res_quality = df.groupby('resolution')['ssim'].mean().sort_values(ascending=False)
    report.append(f"2. **Best quality resolution:** {res_quality.index[0]} "
                 f"(avg SSIM: {res_quality.iloc[0]:.3f})\n")

    # Pareto optimal count per resolution
    pareto_counts = {}
    for resolution in df['resolution'].unique():
        res_df = df[df['resolution'] == resolution]
        pareto_indices = find_pareto_frontier(res_df, 'fps_norm', 'ssim')
        pareto_counts[resolution] = len(pareto_indices)

    best_pareto_res = max(pareto_counts, key=pareto_counts.get)
    report.append(f"3. **Resolution with most Pareto-optimal configs:** {best_pareto_res} "
                 f"({pareto_counts[best_pareto_res]} configs)\n\n")

    # Write report
    with open(output_path, 'w') as f:
        f.writelines(report)

    print(f"  📄 Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Cross-resolution sweet spot analysis')
    parser.add_argument('--aggregated-data', type=str, required=True,
                       help='CSV from aggregate_all_games.py')
    parser.add_argument('--fps-data', type=str,
                       help='Optional FPS data CSV')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory')
    parser.add_argument('--weights', type=str,
                       help='Efficiency weights as JSON, e.g., {"fps":0.4,"ssim":0.3,"lpips":0.3}')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*70)
    print("CROSS-RESOLUTION ANALYSIS")
    print("="*70)

    # Load data
    print(f"📂 Loading data: {args.aggregated_data}")
    fps_path = Path(args.fps_data) if args.fps_data else None
    df = load_data(Path(args.aggregated_data), fps_path)

    if df.empty:
        print("❌ No data loaded. Exiting.")
        return

    print(f"✅ Loaded {len(df)} comparisons\n")

    # Parse weights
    weights = None
    if args.weights:
        import json
        weights = json.loads(args.weights)
        print(f"Using custom weights: {weights}")

    # Create configuration table
    print("📊 Creating configuration table...")
    config_df = create_configuration_table(df)

    # Compute efficiency scores
    print("📊 Computing efficiency scores...")
    config_df = compute_efficiency_score(config_df, weights)

    # Identify sweet spots
    print("🎯 Identifying sweet spots...")
    sweet_spots_df = identify_sweet_spots(config_df)
    print(f"  Found {len(sweet_spots_df)} sweet spot configurations")

    # Cross-resolution comparison
    print("📊 Comparing across resolutions...")
    cross_res_df = compare_across_resolutions(config_df)

    # Save data
    config_df.to_csv(output_dir / "configurations.csv", index=False)
    sweet_spots_df.to_csv(output_dir / "sweet_spots.csv", index=False)
    cross_res_df.to_csv(output_dir / "cross_resolution_comparisons.csv", index=False)

    # Generate visualizations
    print("\n🎨 Generating visualizations...")
    plot_efficiency_scatter(config_df, output_dir / "efficiency_scatter.png")
    plot_sweet_spots_by_game(sweet_spots_df, output_dir / "sweet_spots_by_game.png")
    plot_cross_resolution_comparison(config_df, output_dir / "cross_resolution_heatmap.png")

    # Generate report
    print("\n📝 Generating analysis report...")
    generate_report(config_df, sweet_spots_df, cross_res_df,
                   output_dir / "CROSS_RESOLUTION_REPORT.md")

    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nOutputs saved to: {output_dir}/")


if __name__ == "__main__":
    main()
