#!/usr/bin/env python3
"""
Temporal Quality-Performance Analyzer

Analyzes frame-by-frame correlation between FPS and image quality over time.
Shows how performance and quality trade-offs vary throughout the benchmark.

Usage:
    python temporal_analyzer.py \
        --fps-csv ../tcc/recordings/frameview/Quality_frameview.csv \
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
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from tqdm import tqdm
import cv2
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr


def load_frameview_temporal_data(
    csv_path: Path,
    video_path: Path,
    fps: int = 60,
    manual_start: float = None,
    manual_end: float = None
) -> pd.DataFrame:
    """
    Load FrameView CSV and aggregate by second, aligned to video timing

    Uses the video file and CSV file timestamps to automatically determine
    which portion of the CSV corresponds to the video recording.

    Args:
        csv_path: Path to FrameView CSV
        video_path: Path to corresponding video file (for timestamp alignment)
        fps: Video FPS for alignment (default: 60)
        manual_start: Manual start time override (optional)
        manual_end: Manual end time override (optional)

    Returns:
        DataFrame with columns: second, avg_fps, min_fps, max_fps
    """
    import os

    df = pd.read_csv(csv_path)

    # Manual override
    if manual_start is not None and manual_end is not None:
        print(f"  Using manual CSV timerange: {manual_start:.2f}s - {manual_end:.2f}s")
        df_filtered = df[(df['Time'] >= manual_start) & (df['Time'] <= manual_end)].copy()

        if len(df_filtered) < 10:
            print(f"  ⚠ Warning: Only {len(df_filtered)} samples in timerange.")
    else:
        # Automatic alignment using file timestamps
        video_stat = os.stat(video_path)
        csv_stat = os.stat(csv_path)

        # Calculate time offset: when did video start relative to CSV logging?
        video_created = video_stat.st_mtime
        csv_created = csv_stat.st_mtime
        time_offset = video_created - csv_created

        # Get video duration
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        video_duration = frame_count / video_fps if video_fps > 0 else 60
        cap.release()

        print(f"  Video-CSV sync:")
        print(f"    Video created: {video_created:.2f}")
        print(f"    CSV created:   {csv_created:.2f}")
        print(f"    Time offset:   {time_offset:.2f}s")
        print(f"    Video duration: {video_duration:.2f}s")

        # Find corresponding CSV segment
        csv_start_time = df['Time'].min()
        csv_total_duration = df['Time'].max() - csv_start_time

        # Calculate where video recording appears in CSV timeline
        if 0 <= time_offset <= csv_total_duration:
            # Video started during CSV logging
            segment_start = csv_start_time + time_offset
            segment_end = segment_start + video_duration

            print(f"    CSV segment:   {segment_start:.2f}s - {segment_end:.2f}s")

            # Filter CSV to video timerange
            df_filtered = df[(df['Time'] >= segment_start) & (df['Time'] <= segment_end)].copy()

            if len(df_filtered) < 10:
                print(f"  ⚠ Warning: Only {len(df_filtered)} samples in timerange. Using full CSV.")
                df_filtered = df.copy()
        else:
            print(f"  ⚠ Warning: Time offset ({time_offset:.1f}s) outside CSV range. Using full CSV.")
            print(f"    Consider using --csv-start-time and --csv-end-time for manual alignment")
            df_filtered = df.copy()

    # Normalize time to start at 0 (relative to video start)
    if len(df_filtered) > 0:
        df_filtered['Time'] = df_filtered['Time'] - df_filtered['Time'].min()

    # Aggregate by second
    df_filtered['second'] = (df_filtered['Time']).astype(int)

    temporal_data = df_filtered.groupby('second').agg({
        'FPS': ['mean', 'min', 'max', 'std']
    }).reset_index()

    temporal_data.columns = ['second', 'avg_fps', 'min_fps', 'max_fps', 'std_fps']

    print(f"    ✓ Extracted {len(temporal_data)} seconds of FPS data")

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
        description="Temporal Quality-Performance Analyzer"
    )
    parser.add_argument(
        "--fps-csv",
        type=Path,
        required=True,
        help="FrameView CSV with temporal FPS data"
    )
    parser.add_argument(
        "--video-test",
        type=Path,
        required=True,
        help="Test video (used for CSV alignment AND quality comparison)"
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
    parser.add_argument(
        "--csv-start-time",
        type=float,
        help="Manual CSV start time in seconds (overrides auto-sync)"
    )
    parser.add_argument(
        "--csv-end-time",
        type=float,
        help="Manual CSV end time in seconds (overrides auto-sync)"
    )

    args = parser.parse_args()

    try:
        print("=" * 60)
        print("Temporal Quality-Performance Analysis".center(60))
        print("=" * 60)

        # Load FPS data
        print("\n[1/4] Loading FPS temporal data...")
        fps_data = load_frameview_temporal_data(
            args.fps_csv,
            args.video_test,  # Use test video for alignment
            args.fps
        )
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
