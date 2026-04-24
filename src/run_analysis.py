#!/usr/bin/env python3
"""
Generic video quality analysis runner

Usage:
    python src/run_analysis.py --config configs/analysis_retrimmed.yaml
    python src/run_analysis.py --config configs/analysis_cyberpunk_full.yaml
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compare_alignment_quality import compare_alignment_quality
import yaml
import json
from datetime import datetime
import time
import cv2
import argparse


def parse_percentage_roi(roi_str: str, video_path: str) -> tuple:
    """
    Parse percentage-based ROI (e.g., "top-left 10%") into pixel coordinates.

    Args:
        roi_str: ROI string like "top-left 10%" or "x,y,w,h"
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

    # Parse "top-left 10%" format
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


def run_analysis(config_path: str):
    """
    Run analysis based on YAML configuration file.

    Args:
        config_path: Path to YAML config file
    """
    # Load configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Extract settings
    base_path = Path(config['paths']['base_dir'])
    results_path = Path(config['paths']['results_dir'])
    results_path.mkdir(parents=True, exist_ok=True)

    roi_spec = config['settings']['roi']
    sample_rate = config['settings'].get('sample_rate', 10)
    compute_advanced = config['settings'].get('compute_advanced', True)
    use_gpu = config['settings'].get('use_gpu', True)
    extract_fps = config['settings'].get('extract_fps', True)

    comparisons = config['comparisons']

    print(f"{'='*80}")
    print(f"Video Quality Analysis Runner")
    print(f"{'='*80}")
    print(f"Config: {config_path}")
    print(f"Base path: {base_path}")
    print(f"Results path: {results_path}")
    print(f"ROI: {roi_spec}")
    print(f"Sample rate: every {sample_rate} frames")
    print(f"Advanced metrics: {compute_advanced}")
    print(f"GPU: {use_gpu}")
    print(f"FPS extraction: {extract_fps}")
    print(f"Total comparisons: {len(comparisons)}")
    print()

    summary = []
    batch_start_time = time.time()

    for idx, comparison in enumerate(comparisons, 1):
        ref_video = comparison['reference']
        cmp_video = comparison['compare']
        name = comparison['name']

        print(f"\n{'='*80}")
        print(f"Comparison {idx}/{len(comparisons)}: {name}")
        print(f"{'='*80}")

        ref_path = str(base_path / ref_video)
        cmp_path = str(base_path / cmp_video)

        output_json = str(results_path / f"{name}.json")

        # Calculate ROI for this video
        roi = parse_percentage_roi(roi_spec, cmp_path)
        print(f"  Reference: {ref_video}")
        print(f"  Compare: {cmp_video}")
        print(f"  ROI: {roi}")

        comparison_start_time = time.time()

        try:
            results = compare_alignment_quality(
                video1_path=ref_path,
                video2_path=cmp_path,
                alignment_name=name,
                sample_rate=sample_rate,
                compute_advanced=compute_advanced,
                use_gpu=use_gpu,
                extract_fps=extract_fps,
                fps_video1=ref_path,
                fps_video2=cmp_path,
                fps_roi=roi,
                fps_sample_rate=sample_rate,
                store_per_frame=True
            )

            comparison_duration = time.time() - comparison_start_time

            # Add timing and metadata
            results['execution_time'] = {
                'start_time': datetime.fromtimestamp(comparison_start_time).isoformat(),
                'end_time': datetime.fromtimestamp(time.time()).isoformat(),
                'duration_seconds': round(comparison_duration, 2),
                'frames_analyzed': results.get('frame_count', 0)
            }

            results['config'] = {
                'roi': roi_spec,
                'sample_rate': sample_rate,
                'compute_advanced': compute_advanced
            }

            # Save results
            with open(output_json, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"  ✓ Complete in {comparison_duration:.1f}s")
            print(f"  Mean SSIM: {results.get('ssim', {}).get('mean', 0):.4f}")

            summary.append({
                'name': name,
                'status': 'success',
                'duration_seconds': round(comparison_duration, 2),
                'mean_ssim': results.get('ssim', {}).get('mean', 0)
            })

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            import traceback
            traceback.print_exc()

            summary.append({
                'name': name,
                'status': 'failed',
                'error': str(e)
            })

    batch_duration = time.time() - batch_start_time

    # Save summary
    summary_data = {
        'config_file': str(config_path),
        'batch_start': datetime.fromtimestamp(batch_start_time).isoformat(),
        'batch_end': datetime.now().isoformat(),
        'total_duration_seconds': round(batch_duration, 2),
        'comparisons': summary
    }

    summary_path = results_path / "summary.json"
    with open(summary_path, 'w') as f:
        json.dump(summary_data, f, indent=2)

    print(f"\n{'='*80}")
    print("Batch Analysis Complete!")
    print(f"{'='*80}")
    print(f"Total time: {batch_duration/60:.1f} minutes")
    print(f"Results saved to: {results_path}")
    print(f"Summary: {summary_path}")

    # Print summary table
    print(f"\nSummary:")
    successful = sum(1 for s in summary if s['status'] == 'success')
    failed = sum(1 for s in summary if s['status'] == 'failed')
    print(f"  ✓ Successful: {successful}/{len(summary)}")
    if failed > 0:
        print(f"  ✗ Failed: {failed}/{len(summary)}")


def main():
    parser = argparse.ArgumentParser(
        description='Generic video quality analysis runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis for re-trimmed videos
  python src/run_analysis.py --config configs/analysis_retrimmed.yaml

  # Run full cyberpunk analysis
  python src/run_analysis.py --config configs/analysis_cyberpunk_full.yaml

  # Run cyberpunk_low analysis
  python src/run_analysis.py --config configs/analysis_cyberpunk_low.yaml

Config file format (YAML):
  paths:
    base_dir: recordings/cyberpunk/trimmed
    results_dir: results/cyberpunk/retrimmed

  settings:
    roi: "top-left 10%"
    sample_rate: 10
    compute_advanced: true
    use_gpu: true
    extract_fps: true

  comparisons:
    - reference: 1080p_dlaa_run1.mp4
      compare: 1080p_dlss_quality.mp4
      name: 1080p_DLAA_vs_Quality
        """
    )

    parser.add_argument('--config', type=str, required=True,
                       help='Path to YAML configuration file')

    args = parser.parse_args()

    if not Path(args.config).exists():
        print(f"Error: Config file not found: {args.config}")
        return 1

    try:
        run_analysis(args.config)
        return 0
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
