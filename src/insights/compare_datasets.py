#!/usr/bin/env python3
"""
Compare quality metrics between two datasets (e.g., ultra vs low graphics)

Usage:
    python src/insights/compare_datasets.py \
        --dataset1 results/cyberpunk/quality_comparison \
        --dataset2 results/cyberpunk_low/quality_comparison \
        --label1 "Ultra Graphics" \
        --label2 "Low Graphics" \
        --output results/comparison_ultra_vs_low
"""

import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse


def load_dataset_metrics(results_dir):
    """Load all comparison JSONs from a dataset directory"""
    metrics = []
    results_path = Path(results_dir)

    for json_file in results_path.glob("*.json"):
        if json_file.name.startswith("summary"):
            continue

        with open(json_file) as f:
            data = json.load(f)

        # Extract key info
        comparison_name = data.get('alignment_method', json_file.stem)

        # Parse resolution and mode from name
        # e.g., "1080p_DLAA_vs_Quality" -> resolution=1080p, mode=Quality
        # e.g., "1080p_DLAA_Consistency" -> resolution=1080p, mode=Consistency
        parts = comparison_name.split('_')
        resolution = parts[0]

        if 'Consistency' in comparison_name:
            mode = 'Consistency'
        elif 'vs' in comparison_name:
            # Find the part after "vs"
            vs_idx = parts.index('vs')
            mode = '_'.join(parts[vs_idx+1:])
        else:
            mode = 'Unknown'

        # Extract metrics
        metrics_data = data.get('metrics', {})

        metrics.append({
            'comparison': comparison_name,
            'resolution': resolution,
            'mode': mode,
            'frames': data.get('frames_compared', 0),
            'ssim_mean': metrics_data.get('ssim', {}).get('mean'),
            'ssim_std': metrics_data.get('ssim', {}).get('std'),
            'psnr_mean': metrics_data.get('psnr', {}).get('mean'),
            'psnr_std': metrics_data.get('psnr', {}).get('std'),
            'lpips_mean': metrics_data.get('lpips', {}).get('mean'),
            'lpips_std': metrics_data.get('lpips', {}).get('std'),
            'flip_mean': metrics_data.get('flip', {}).get('mean'),
            'flip_std': metrics_data.get('flip', {}).get('std'),
            'vmaf_mean': metrics_data.get('vmaf', {}).get('mean'),
            'vmaf_std': metrics_data.get('vmaf', {}).get('std'),
        })

    return pd.DataFrame(metrics)


def compute_deltas(df1, df2):
    """Compute metric differences between two datasets"""
    # Merge on resolution + mode
    merged = df1.merge(
        df2,
        on=['resolution', 'mode'],
        suffixes=('_ds1', '_ds2')
    )

    # Calculate deltas (dataset2 - dataset1)
    merged['delta_ssim'] = merged['ssim_mean_ds2'] - merged['ssim_mean_ds1']
    merged['delta_psnr'] = merged['psnr_mean_ds2'] - merged['psnr_mean_ds1']
    merged['delta_lpips'] = merged['lpips_mean_ds2'] - merged['lpips_mean_ds1']
    merged['delta_flip'] = merged['flip_mean_ds2'] - merged['flip_mean_ds1']
    merged['delta_vmaf'] = merged['vmaf_mean_ds2'] - merged['vmaf_mean_ds1']

    # Percentage changes
    merged['ssim_change_pct'] = (merged['delta_ssim'] / merged['ssim_mean_ds1']) * 100
    merged['psnr_change_pct'] = (merged['delta_psnr'] / merged['psnr_mean_ds1']) * 100

    return merged


def plot_metric_comparison(df1, df2, metric='ssim_mean', label1='Dataset 1', label2='Dataset 2', output_path=None):
    """Side-by-side bar chart comparing a metric across datasets"""
    fig, ax = plt.subplots(figsize=(14, 6))

    # Prepare data
    x = df1['mode'].values
    y1 = df1[metric].values
    y2 = df2[metric].values

    x_pos = range(len(x))
    width = 0.35

    ax.bar([p - width/2 for p in x_pos], y1, width, label=label1, alpha=0.8)
    ax.bar([p + width/2 for p in x_pos], y2, width, label=label2, alpha=0.8)

    ax.set_xlabel('DLSS Mode')
    ax.set_ylabel(metric.replace('_', ' ').title())
    ax.set_title(f'{metric.replace("_", " ").title()} Comparison: {label1} vs {label2}')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_delta_heatmap(deltas_df, metric='delta_ssim', title='SSIM Delta', output_path=None):
    """Heatmap showing metric deltas across resolutions and modes"""
    # Pivot for heatmap: resolution x mode, values = metric
    pivot = deltas_df.pivot(index='resolution', columns='mode', values=metric)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(
        pivot,
        annot=True,
        fmt='.4f',
        cmap='RdYlGn',
        center=0,
        cbar_kws={'label': title},
        ax=ax
    )
    ax.set_title(f'{title} (Dataset 2 - Dataset 1)')
    ax.set_xlabel('DLSS Mode')
    ax.set_ylabel('Resolution')

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_summary_report(deltas_df, label1, label2, output_path):
    """Generate markdown summary report"""
    with open(output_path, 'w') as f:
        f.write(f"# Graphics Settings Comparison Report\n\n")
        f.write(f"## {label1} vs {label2}\n\n")

        f.write("### Overall Statistics\n\n")
        f.write(f"- **Comparisons analyzed:** {len(deltas_df)}\n")
        f.write(f"- **Mean SSIM improvement:** {deltas_df['delta_ssim'].mean():.4f} ({deltas_df['ssim_change_pct'].mean():.2f}%)\n")
        f.write(f"- **Mean PSNR improvement:** {deltas_df['delta_psnr'].mean():.2f} dB ({deltas_df['psnr_change_pct'].mean():.2f}%)\n")

        if deltas_df['delta_lpips'].notna().any():
            f.write(f"- **Mean LPIPS improvement:** {deltas_df['delta_lpips'].mean():.4f}\n")
        if deltas_df['delta_flip'].notna().any():
            f.write(f"- **Mean FLIP improvement:** {deltas_df['delta_flip'].mean():.4f}\n")
        if deltas_df['delta_vmaf'].notna().any():
            f.write(f"- **Mean VMAF improvement:** {deltas_df['delta_vmaf'].mean():.2f}\n")
        f.write("\n")

        f.write("### Top Improvements (by SSIM)\n\n")
        top5 = deltas_df.nlargest(5, 'delta_ssim')[['resolution', 'mode', 'delta_ssim', 'ssim_change_pct']]
        f.write(top5.to_markdown(index=False))
        f.write("\n\n")

        f.write("### Top Declines (by SSIM)\n\n")
        bottom5 = deltas_df.nsmallest(5, 'delta_ssim')[['resolution', 'mode', 'delta_ssim', 'ssim_change_pct']]
        f.write(bottom5.to_markdown(index=False))
        f.write("\n\n")

        f.write("### Detailed Comparison Table\n\n")
        cols_to_show = ['resolution', 'mode', 'ssim_mean_ds1', 'ssim_mean_ds2', 'delta_ssim', 'psnr_mean_ds1', 'psnr_mean_ds2', 'delta_psnr']
        f.write(deltas_df[cols_to_show].to_markdown(index=False))
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description='Compare quality metrics between two datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare ultra vs low graphics
  python src/insights/compare_datasets.py \\
      --dataset1 results/cyberpunk/quality_comparison \\
      --dataset2 results/cyberpunk_low/quality_comparison \\
      --label1 "Ultra Graphics" \\
      --label2 "Low Graphics" \\
      --output results/comparison_ultra_vs_low
        """
    )

    parser.add_argument('--dataset1', required=True, help='Path to first dataset results directory')
    parser.add_argument('--dataset2', required=True, help='Path to second dataset results directory')
    parser.add_argument('--label1', default='Dataset 1', help='Label for first dataset')
    parser.add_argument('--label2', default='Dataset 2', help='Label for second dataset')
    parser.add_argument('--output', required=True, help='Output directory for comparison results')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load datasets
    print(f"Loading {args.label1} from {args.dataset1}...")
    df1 = load_dataset_metrics(args.dataset1)
    print(f"  Found {len(df1)} comparisons")

    print(f"Loading {args.label2} from {args.dataset2}...")
    df2 = load_dataset_metrics(args.dataset2)
    print(f"  Found {len(df2)} comparisons")

    # Compute deltas
    print("Computing deltas...")
    deltas = compute_deltas(df1, df2)
    print(f"  Matched {len(deltas)} comparisons")

    # Export deltas to CSV
    deltas.to_csv(output_dir / 'comparison_deltas.csv', index=False)
    print(f"✓ Saved: {output_dir / 'comparison_deltas.csv'}")

    # Generate plots for each resolution
    for resolution in ['1080p', '1440p', '4K']:
        df1_res = df1[df1['resolution'] == resolution].sort_values('mode')
        df2_res = df2[df2['resolution'] == resolution].sort_values('mode')

        if not df1_res.empty and not df2_res.empty:
            # SSIM comparison
            plot_metric_comparison(
                df1_res, df2_res,
                metric='ssim_mean',
                label1=args.label1,
                label2=args.label2,
                output_path=output_dir / f'ssim_comparison_{resolution}.png'
            )
            print(f"✓ Saved: {output_dir / f'ssim_comparison_{resolution}.png'}")

            # PSNR comparison
            plot_metric_comparison(
                df1_res, df2_res,
                metric='psnr_mean',
                label1=args.label1,
                label2=args.label2,
                output_path=output_dir / f'psnr_comparison_{resolution}.png'
            )
            print(f"✓ Saved: {output_dir / f'psnr_comparison_{resolution}.png'}")

    # Delta heatmaps
    plot_delta_heatmap(deltas, metric='delta_ssim', title='SSIM Delta',
                      output_path=output_dir / 'delta_heatmap_ssim.png')
    print(f"✓ Saved: {output_dir / 'delta_heatmap_ssim.png'}")

    plot_delta_heatmap(deltas, metric='delta_psnr', title='PSNR Delta (dB)',
                      output_path=output_dir / 'delta_heatmap_psnr.png')
    print(f"✓ Saved: {output_dir / 'delta_heatmap_psnr.png'}")

    # Summary report
    generate_summary_report(deltas, args.label1, args.label2, output_path=output_dir / 'summary_report.md')
    print(f"✓ Saved: {output_dir / 'summary_report.md'}")

    print(f"\n{'='*80}")
    print(f"✓ Comparison complete! Results in: {output_dir}")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
