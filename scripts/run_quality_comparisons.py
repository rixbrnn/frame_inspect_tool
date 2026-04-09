#!/usr/bin/env python3
"""
Batch quality comparison for Cyberpunk trimmed videos
Compares DLSS modes against DLAA reference at each resolution
Captures execution time metrics for TCC methodology documentation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compare_alignment_quality import compare_alignment_quality, export_per_frame_to_csv
import json
from datetime import datetime
import time
import cv2


def parse_percentage_roi(roi_str: str, video_path: str) -> tuple:
    """
    Parse percentage-based ROI (e.g., "top-left 15%") into pixel coordinates.

    Args:
        roi_str: ROI string like "top-left 15%"
        video_path: Path to video to get dimensions

    Returns:
        (x, y, width, height) in pixels
    """
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    roi_str = roi_str.strip().lower()

    if '%' not in roi_str:
        # Already pixel format "x,y,w,h"
        return tuple(map(int, roi_str.split(',')))

    # Parse "top-left 15%" format
    parts = roi_str.replace('%', '').split()
    if len(parts) != 2:
        raise ValueError(f"Percentage ROI must be 'position percent%', got: {roi_str}")

    position = parts[0]
    percent = float(parts[1]) / 100.0

    # Calculate ROI size
    roi_w = int(frame_width * percent)
    roi_h = int(frame_height * percent)

    # Calculate position
    if position == "top-left":
        x, y = 0, 0
    elif position == "top-right":
        x, y = frame_width - roi_w, 0
    elif position == "bottom-left":
        x, y = 0, frame_height - roi_h
    elif position == "bottom-right":
        x, y = frame_width - roi_w, frame_height - roi_h
    else:
        raise ValueError(f"Unknown position: {position}")

    return (x, y, roi_w, roi_h)


def run_comparisons():
    base_path = Path("recordings/cyberpunk/trimmed")
    results_path = Path("results/cyberpunk/quality_comparison")
    results_path.mkdir(parents=True, exist_ok=True)

    # Use top-left 15% ROI (same as trim tool)
    roi_spec = "top-left 15%"
    roi = None  # Will be calculated per video

    # Define comparison pairs
    comparisons = [
        # 1080p
        ("1080p_dlaa_run1.mp4", "1080p_dlss_quality.mp4", "1080p_DLAA_vs_Quality"),
        ("1080p_dlaa_run1.mp4", "1080p_dlss_balanced.mp4", "1080p_DLAA_vs_Balanced"),
        ("1080p_dlaa_run1.mp4", "1080p_dlss_performance.mp4", "1080p_DLAA_vs_Performance"),
        ("1080p_dlaa_run1.mp4", "1080p_dlss_ultra_performance.mp4", "1080p_DLAA_vs_Ultra_Performance"),
        ("1080p_dlaa_run1.mp4", "1080p_dlaa_run2.mp4", "1080p_DLAA_Consistency"),

        # 1440p
        ("1440p_dlaa_run1.mp4", "1440p_dlss_quality.mp4", "1440p_DLAA_vs_Quality"),
        ("1440p_dlaa_run1.mp4", "1440p_dlss_balanced.mp4", "1440p_DLAA_vs_Balanced"),
        ("1440p_dlaa_run1.mp4", "1440p_dlss_performance.mp4", "1440p_DLAA_vs_Performance"),
        ("1440p_dlaa_run1.mp4", "1440p_dlss_ultra_performance.mp4", "1440p_DLAA_vs_Ultra_Performance"),
        ("1440p_dlaa_run1.mp4", "1440p_dlaa_run2.mp4", "1440p_DLAA_Consistency"),

        # 4K
        ("4k_dlaa_run1.mp4", "4k_dlss_quality.mp4", "4K_DLAA_vs_Quality"),
        ("4k_dlaa_run1.mp4", "4k_dlss_balanced.mp4", "4K_DLAA_vs_Balanced"),
        ("4k_dlaa_run1.mp4", "4k_dlss_performance.mp4", "4K_DLAA_vs_Performance"),
        ("4k_dlaa_run1.mp4", "4k_dlss_ultra_performance.mp4", "4K_DLAA_vs_Ultra_Performance"),
        ("4k_dlaa_run1.mp4", "4k_dlaa_run2.mp4", "4K_DLAA_Consistency"),
    ]

    summary = []
    batch_start_time = time.time()

    for idx, (ref_video, cmp_video, name) in enumerate(comparisons, 1):
        print(f"\n{'='*80}")
        print(f"Comparison {idx}/{len(comparisons)}: {name}")
        print(f"{'='*80}")

        comparison_start_time = time.time()

        ref_path = str(base_path / ref_video)
        cmp_path = str(base_path / cmp_video)

        # FPS source videos - use trimmed videos (they still have FPS overlays)
        fps_ref_path = ref_path
        fps_cmp_path = cmp_path

        output_json = str(results_path / f"{name}.json")
        output_csv = str(results_path / f"{name}.csv")

        # Calculate ROI for this video (in case resolutions differ)
        if roi is None:
            roi = parse_percentage_roi(roi_spec, fps_cmp_path)
            print(f"  Using ROI: {roi} ({roi_spec})")

        try:
            results = compare_alignment_quality(
                video1_path=ref_path,
                video2_path=cmp_path,
                alignment_name=name,
                sample_rate=10,  # Sample every 10 frames for metrics
                compute_advanced=True,
                use_gpu=True,
                compute_vmaf=True,  # Include VMAF metric
                extract_fps=True,
                fps_video1=fps_ref_path,
                fps_video2=fps_cmp_path,
                fps_roi=roi,
                fps_sample_rate=10,  # Extract FPS at same rate as metrics
                store_per_frame=True
            )

            comparison_end_time = time.time()
            comparison_duration = comparison_end_time - comparison_start_time

            # Add timing information to results
            results['execution_time'] = {
                'start_time': datetime.fromtimestamp(comparison_start_time).isoformat(),
                'end_time': datetime.fromtimestamp(comparison_end_time).isoformat(),
                'duration_seconds': round(comparison_duration, 2),
                'duration_formatted': f"{int(comparison_duration // 60)}m {int(comparison_duration % 60)}s"
            }

            # Save JSON
            with open(output_json, 'w') as f:
                json.dump(results, f, indent=2)

            # Export CSV
            if 'per_frame_data' in results:
                export_per_frame_to_csv(results['per_frame_data'], output_csv)

            # Note: ROI already set from first video, no need to update

            summary.append({
                "name": name,
                "status": "success",
                "resolution": name.split('_')[0],  # Extract resolution (1080p, 1440p, 4K)
                "comparison_type": name.split('_')[-1],  # Extract type (Quality, Balanced, etc.)
                "frames_compared": results['frames_compared'],
                "video1": ref_video,
                "video2": cmp_video,
                "ssim_mean": results['metrics']['ssim']['mean'],
                "vmaf_mean": results['metrics']['vmaf']['mean'] if 'vmaf' in results['metrics'] else None,
                "execution_time_seconds": round(comparison_duration, 2),
                "execution_time_formatted": results['execution_time']['duration_formatted'],
                "output_json": output_json,
                "output_csv": output_csv
            })

            print(f"\n✓ Comparison completed in {results['execution_time']['duration_formatted']}")

        except Exception as e:
            comparison_end_time = time.time()
            comparison_duration = comparison_end_time - comparison_start_time

            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()

            summary.append({
                "name": name,
                "status": "failed",
                "resolution": name.split('_')[0] if '_' in name else "unknown",
                "video1": ref_video,
                "video2": cmp_video,
                "error": str(e),
                "execution_time_seconds": round(comparison_duration, 2),
                "execution_time_formatted": f"{int(comparison_duration // 60)}m {int(comparison_duration % 60)}s"
            })

    batch_end_time = time.time()
    batch_duration = batch_end_time - batch_start_time

    # Calculate timing statistics
    successful_runs = [s for s in summary if s['status'] == 'success']
    if successful_runs:
        avg_time = sum(s['execution_time_seconds'] for s in successful_runs) / len(successful_runs)
        min_time = min(s['execution_time_seconds'] for s in successful_runs)
        max_time = max(s['execution_time_seconds'] for s in successful_runs)

        # Calculate per-resolution statistics
        resolution_stats = {}
        for res in ['1080p', '1440p', '4K']:
            res_runs = [s for s in successful_runs if s.get('resolution') == res]
            if res_runs:
                resolution_stats[res] = {
                    "count": len(res_runs),
                    "average_seconds": round(sum(s['execution_time_seconds'] for s in res_runs) / len(res_runs), 2),
                    "min_seconds": round(min(s['execution_time_seconds'] for s in res_runs), 2),
                    "max_seconds": round(max(s['execution_time_seconds'] for s in res_runs), 2)
                }
    else:
        avg_time = min_time = max_time = 0
        resolution_stats = {}

    # Add batch timing to summary
    summary_metadata = {
        "batch_execution": {
            "start_time": datetime.fromtimestamp(batch_start_time).isoformat(),
            "end_time": datetime.fromtimestamp(batch_end_time).isoformat(),
            "total_duration_seconds": round(batch_duration, 2),
            "total_duration_formatted": f"{int(batch_duration // 3600)}h {int((batch_duration % 3600) // 60)}m {int(batch_duration % 60)}s",
            "average_comparison_time_seconds": round(avg_time, 2),
            "min_comparison_time_seconds": round(min_time, 2),
            "max_comparison_time_seconds": round(max_time, 2),
            "total_comparisons": len(comparisons),
            "successful_comparisons": len(successful_runs),
            "failed_comparisons": len(summary) - len(successful_runs),
            "resolution_statistics": resolution_stats
        },
        "results": summary
    }

    # Save summary
    summary_path = results_path / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_path, 'w') as f:
        json.dump(summary_metadata, f, indent=2)

    print(f"\n{'='*80}")
    print("Batch Comparison Complete")
    print(f"{'='*80}")
    print(f"Total time: {summary_metadata['batch_execution']['total_duration_formatted']}")
    print(f"Average per comparison: {summary_metadata['batch_execution']['average_comparison_time_seconds']:.1f}s")
    print(f"Successful: {summary_metadata['batch_execution']['successful_comparisons']}/{summary_metadata['batch_execution']['total_comparisons']}")

    # Print per-resolution timing
    if resolution_stats:
        print(f"\nPer-Resolution Timing:")
        for res, stats in resolution_stats.items():
            print(f"  {res}: avg={stats['average_seconds']:.1f}s, min={stats['min_seconds']:.1f}s, max={stats['max_seconds']:.1f}s ({stats['count']} comparisons)")

    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    run_comparisons()
