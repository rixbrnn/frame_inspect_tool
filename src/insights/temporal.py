#!/usr/bin/env python3
"""
Temporal Quality-Performance Analyzer (OCR version)

Analyzes frame-by-frame correlation between FPS and image quality over time.
Uses FPS data extracted via OCR from on-screen display instead of CSV files.

Usage:
    python temporal_analyzer_ocr.py \
        --fps-json ../tcc/fps_data/Quality_fps_ocr.json \
        --video-ground-truth ../tcc/recordings/processed/DLAA_4K_60fps.mp4 \
        --video-test ../tcc/recordings/processed/Quality_60fps.mp4 \
        --output ../tcc/results/temporal_analysis_Quality.json \
        --plot-timeline ../tcc/results/charts/temporal_Quality.png \
        --plot-correlation ../tcc/results/charts/correlation_Quality.png
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from tqdm import tqdm
import cv2
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr


def load_fps_from_ocr_json(json_path: Path) -> pd.DataFrame:
    """
    Load FPS data from OCR extraction JSON and aggregate by second

    Args:
        json_path: Path to OCR JSON file (output from fps_ocr_extractor.py)

    Returns:
        DataFrame with columns: second, avg_fps, min_fps, max_fps, std_fps
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    fps_data = data['fps_data']

    if not fps_data:
        raise ValueError(f"No FPS data in {json_path}")

    # Convert to DataFrame
    df = pd.DataFrame(fps_data)

    # Group by second (timestamp already in seconds)
    df['second'] = df['timestamp'].astype(int)

    temporal_data = df.groupby('second').agg({
        'fps': ['mean', 'min', 'max', 'std']
    }).reset_index()

    temporal_data.columns = ['second', 'avg_fps', 'min_fps', 'max_fps', 'std_fps']

    print(f"  ✓ Loaded {len(temporal_data)} seconds of FPS data from OCR")

    return temporal_data


def calculate_temporal_quality(
    ground_truth_video: Path,
    test_video: Path,
    fps: int = 60
) -> pd.DataFrame:
    """
    Calculate SSIM and PSNR for each second of video

    Args:
        ground_truth_video: Path to baseline video
        test_video: Path to test video
        fps: Video FPS (default: 60)

    Returns:
        DataFrame with columns: second, avg_ssim, avg_psnr, frame_count
    """
    cap_gt = cv2.VideoCapture(str(ground_truth_video))
    cap_test = cv2.VideoCapture(str(test_video))

    total_frames = int(cap_gt.get(cv2.CAP_PROP_FRAME_COUNT))

    results = []
    current_second = 0
    frame_in_second = 0
    ssim_values = []
    psnr_values = []

    for frame_idx in tqdm(range(total_frames), desc="Analyzing frames", unit="frame"):
        ret_gt, frame_gt = cap_gt.read()
        ret_test, frame_test = cap_test.read()

        if not ret_gt or not ret_test:
            break

        # Convert to grayscale for SSIM
        gray_gt = cv2.cvtColor(frame_gt, cv2.COLOR_BGR2GRAY)
        gray_test = cv2.cvtColor(frame_test, cv2.COLOR_BGR2GRAY)

        # Calculate metrics
        ssim_value, _ = ssim(gray_gt, gray_test, full=True)
        psnr_value = psnr(frame_gt, frame_test)

        ssim_values.append(ssim_value * 100)  # Convert to percentage
        psnr_values.append(psnr_value)

        frame_in_second += 1

        # Aggregate by second
        if frame_in_second >= fps:
            results.append({
                'second': current_second,
                'avg_ssim': np.mean(ssim_values),
                'min_ssim': np.min(ssim_values),
                'max_ssim': np.max(ssim_values),
                'std_ssim': np.std(ssim_values),
                'avg_psnr': np.mean(psnr_values),
                'min_psnr': np.min(psnr_values),
                'max_psnr': np.max(psnr_values),
                'std_psnr': np.std(psnr_values),
                'frame_count': len(ssim_values)
            })

            current_second += 1
            frame_in_second = 0
            ssim_values = []
            psnr_values = []

    # Handle remaining frames
    if ssim_values:
        results.append({
            'second': current_second,
            'avg_ssim': np.mean(ssim_values),
            'min_ssim': np.min(ssim_values),
            'max_ssim': np.max(ssim_values),
            'std_ssim': np.std(ssim_values),
            'avg_psnr': np.mean(psnr_values),
            'min_psnr': np.min(psnr_values),
            'max_psnr': np.max(psnr_values),
            'std_psnr': np.std(psnr_values),
            'frame_count': len(ssim_values)
        })

    cap_gt.release()
    cap_test.release()

    return pd.DataFrame(results)


def merge_temporal_data(fps_data: pd.DataFrame, quality_data: pd.DataFrame) -> pd.DataFrame:
    """
    Merge FPS and quality data by second

    Args:
        fps_data: DataFrame with FPS data per second
        quality_data: DataFrame with quality metrics per second

    Returns:
        Merged DataFrame
    """
    merged = pd.merge(fps_data, quality_data, on='second', how='inner')
    return merged


def calculate_correlation(merged_data: pd.DataFrame) -> Dict:
    """
    Calculate correlation statistics between FPS and quality

    Args:
        merged_data: DataFrame with FPS and quality columns

    Returns:
        Dict with correlation statistics
    """
    # Pearson correlation
    corr_fps_ssim, p_fps_ssim = stats.pearsonr(
        merged_data['avg_fps'],
        merged_data['avg_ssim']
    )

    corr_fps_psnr, p_fps_psnr = stats.pearsonr(
        merged_data['avg_fps'],
        merged_data['avg_psnr']
    )

    # Spearman correlation (rank-based, handles non-linear)
    spearman_fps_ssim, sp_p_fps_ssim = stats.spearmanr(
        merged_data['avg_fps'],
        merged_data['avg_ssim']
    )

    return {
        'pearson_fps_ssim': {
            'correlation': float(corr_fps_ssim),
            'p_value': float(p_fps_ssim),
            'significant': p_fps_ssim < 0.05
        },
        'pearson_fps_psnr': {
            'correlation': float(corr_fps_psnr),
            'p_value': float(p_fps_psnr),
            'significant': p_fps_psnr < 0.05
        },
        'spearman_fps_ssim': {
            'correlation': float(spearman_fps_ssim),
            'p_value': float(sp_p_fps_ssim),
            'significant': sp_p_fps_ssim < 0.05
        }
    }


def plot_temporal_timeline(
    merged_data: pd.DataFrame,
    output_path: Path,
    mode_name: str
):
    """
    Plot FPS and quality metrics over time (dual-axis line chart)

    Args:
        merged_data: DataFrame with temporal data
        output_path: Path to save plot
        mode_name: DLSS mode name for title
    """
    fig, ax1 = plt.subplots(figsize=(14, 6))

    # FPS on left axis
    ax1.set_xlabel('Time (seconds)', fontsize=12)
    ax1.set_ylabel('FPS', color='tab:blue', fontsize=12)
    ax1.plot(
        merged_data['second'],
        merged_data['avg_fps'],
        color='tab:blue',
        linewidth=2,
        label='Average FPS',
        marker='o',
        markersize=4
    )
    ax1.fill_between(
        merged_data['second'],
        merged_data['min_fps'],
        merged_data['max_fps'],
        color='tab:blue',
        alpha=0.2,
        label='FPS Range (Min-Max)'
    )
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.grid(True, alpha=0.3)

    # SSIM on right axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('SSIM (%)', color='tab:red', fontsize=12)
    ax2.plot(
        merged_data['second'],
        merged_data['avg_ssim'],
        color='tab:red',
        linewidth=2,
        label='Average SSIM',
        marker='s',
        markersize=4
    )
    ax2.fill_between(
        merged_data['second'],
        merged_data['min_ssim'],
        merged_data['max_ssim'],
        color='tab:red',
        alpha=0.2,
        label='SSIM Range (Min-Max)'
    )
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Title and legends
    plt.title(f'Temporal Analysis: FPS vs SSIM Over Time - {mode_name}', fontsize=14, fontweight='bold')

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_correlation_scatter(
    merged_data: pd.DataFrame,
    output_path: Path,
    mode_name: str
):
    """
    Plot FPS vs SSIM scatter plot with time gradient

    Args:
        merged_data: DataFrame with temporal data
        output_path: Path to save plot
        mode_name: DLSS mode name for title
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Scatter plot with time as color
    scatter = ax.scatter(
        merged_data['avg_fps'],
        merged_data['avg_ssim'],
        c=merged_data['second'],
        cmap='viridis',
        s=100,
        alpha=0.7,
        edgecolors='black',
        linewidths=0.5
    )

    # Add colorbar for time
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Time (seconds)', fontsize=12)

    # Labels and title
    ax.set_xlabel('Average FPS', fontsize=12)
    ax.set_ylabel('Average SSIM (%)', fontsize=12)
    ax.set_title(f'FPS vs SSIM Correlation - {mode_name}', fontsize=14, fontweight='bold')

    # Add trend line
    z = np.polyfit(merged_data['avg_fps'], merged_data['avg_ssim'], 1)
    p = np.poly1d(z)
    ax.plot(
        merged_data['avg_fps'],
        p(merged_data['avg_fps']),
        "r--",
        alpha=0.8,
        linewidth=2,
        label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}'
    )

    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Temporal Quality-Performance Analyzer (OCR version)"
    )
    parser.add_argument(
        "--fps-json",
        type=Path,
        required=True,
        help="JSON file with FPS data from OCR extraction"
    )
    parser.add_argument(
        "--video-test",
        type=Path,
        required=True,
        help="Test video"
    )
    parser.add_argument(
        "--video-ground-truth",
        type=Path,
        required=True,
        help="Ground truth video (baseline)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output JSON file with temporal analysis"
    )
    parser.add_argument(
        "--plot-timeline",
        type=Path,
        help="Output PNG for timeline plot"
    )
    parser.add_argument(
        "--plot-correlation",
        type=Path,
        help="Output PNG for correlation scatter plot"
    )
    parser.add_argument(
        "--mode-name",
        default="DLSS",
        help="Mode name for plot titles (default: DLSS)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Video FPS (default: 60)"
    )

    args = parser.parse_args()

    try:
        print("=" * 60)
        print("Temporal Quality-Performance Analysis (OCR)".center(60))
        print("=" * 60)

        # Load FPS data from OCR JSON
        print("\n[1/4] Loading FPS data from OCR...")
        fps_data = load_fps_from_ocr_json(args.fps_json)
        print(f"  ✓ Loaded {len(fps_data)} seconds of FPS data")

        # Calculate quality metrics
        print("\n[2/4] Calculating frame-by-frame quality metrics...")
        quality_data = calculate_temporal_quality(
            args.video_ground_truth,
            args.video_test,
            args.fps
        )
        print(f"  ✓ Analyzed {len(quality_data)} seconds of quality data")

        # Merge data
        print("\n[3/4] Merging and analyzing correlation...")
        merged_data = merge_temporal_data(fps_data, quality_data)
        correlation_stats = calculate_correlation(merged_data)

        print(f"  ✓ Pearson FPS-SSIM: {correlation_stats['pearson_fps_ssim']['correlation']:.3f} "
              f"(p={correlation_stats['pearson_fps_ssim']['p_value']:.4f})")
        print(f"  ✓ Spearman FPS-SSIM: {correlation_stats['spearman_fps_ssim']['correlation']:.3f}")

        # Prepare output
        output_data = {
            'mode': args.mode_name,
            'temporal_data': merged_data.to_dict('records'),
            'correlation_statistics': correlation_stats,
            'summary': {
                'overall_avg_fps': float(merged_data['avg_fps'].mean()),
                'overall_avg_ssim': float(merged_data['avg_ssim'].mean()),
                'overall_avg_psnr': float(merged_data['avg_psnr'].mean()),
                'fps_std': float(merged_data['avg_fps'].std()),
                'ssim_std': float(merged_data['avg_ssim'].std()),
                'duration_seconds': int(len(merged_data))
            }
        }

        # Save JSON
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n  ✓ Saved analysis to: {args.output}")

        # Generate plots
        print("\n[4/4] Generating visualizations...")
        if args.plot_timeline:
            plot_temporal_timeline(merged_data, args.plot_timeline, args.mode_name)
            print(f"  ✓ Timeline plot: {args.plot_timeline}")

        if args.plot_correlation:
            plot_correlation_scatter(merged_data, args.plot_correlation, args.mode_name)
            print(f"  ✓ Correlation plot: {args.plot_correlation}")

        print("\n" + "=" * 60)
        print("Analysis Complete!".center(60))
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
