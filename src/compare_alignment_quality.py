#!/usr/bin/env python3
"""
Compare alignment quality between ICAT and Scene-based methods

Computes SSIM and other metrics across all frames to determine
which alignment produces better frame-to-frame similarity.

Now includes advanced perceptual metrics: LPIPS, FLIP, and Temporal Optical Flow
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from pathlib import Path
import json
from tqdm import tqdm
import sys
import os

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metrics.frame.perceptual import AdvancedMetrics, compute_all_metrics, LPIPS_AVAILABLE
from src.metrics.frame.basic import BasicMetricsGPU, TORCH_AVAILABLE, PYTORCH_MSSSIM_AVAILABLE

# Check for torch availability (for GPU detection) - already imported above via basic.py
# (removing duplicate import check)


# ============================================================================
# FPS Extraction Integration
# ============================================================================

class FPSExtractionError(Exception):
    """Raised when FPS extraction fails but comparison can continue."""
    pass


def parse_fps_roi(roi_arg: str = None) -> tuple:
    """
    Parse ROI from CLI argument or config file.

    Args:
        roi_arg: Either "x,y,width,height" or path to fps_roi.json

    Returns:
        ROI tuple (x, y, w, h) or None for auto-detection
    """
    if not roi_arg:
        return None

    # Try parsing as coordinates
    if ',' in roi_arg:
        try:
            x, y, w, h = map(int, roi_arg.split(','))
            return (x, y, w, h)
        except ValueError:
            print(f"⚠️  Invalid ROI format: {roi_arg}")
            return None

    # Try loading from JSON file
    roi_path = Path(roi_arg)
    if roi_path.exists():
        with open(roi_path) as f:
            config = json.load(f)
            roi_dict = config.get('roi', {})
            return (
                roi_dict['x'],
                roi_dict['y'],
                roi_dict['width'],
                roi_dict['height']
            )

    print(f"⚠️  ROI file not found: {roi_arg}")
    return None


def extract_fps_from_video(
    video_path: str,
    roi: tuple = None,
    sample_rate: int = 1
) -> tuple:
    """
    Extract FPS data from video with FPS overlay.

    Args:
        video_path: Path to video with FPS counter
        roi: Optional ROI as (x, y, width, height)
        sample_rate: Extract every Nth frame

    Returns:
        Tuple of (fps_data_list, detected_roi)

    Raises:
        FPSExtractionError: If extraction fails
    """
    from src.extraction.fps_ocr import FPSOCRExtractor

    print(f"  Extracting FPS from: {Path(video_path).name}")

    if not Path(video_path).exists():
        raise FPSExtractionError(f"Video file not found: {video_path}")

    try:
        extractor = FPSOCRExtractor(roi=roi, use_easyocr=True)
        fps_data, _ = extractor.extract_from_video(
            Path(video_path),
            sample_rate=sample_rate
        )

        detected_roi = extractor.roi

        if not fps_data:
            raise FPSExtractionError(f"No FPS data extracted from {video_path}")

        print(f"  ✓ Extracted {len(fps_data)} FPS measurements")

        if detected_roi:
            print(f"  ✓ ROI: x={detected_roi[0]}, y={detected_roi[1]}, w={detected_roi[2]}, h={detected_roi[3]}")

        return fps_data, detected_roi

    except Exception as e:
        raise FPSExtractionError(f"FPS extraction failed: {e}")


def build_fps_lookup(fps_data_list: list) -> dict:
    """
    Build frame index -> FPS data lookup dict for O(1) access.

    Args:
        fps_data_list: List from FPSOCRExtractor.extract_from_video()

    Returns:
        Dict mapping frame_index to fps_data entry
    """
    return {entry['frame']: entry for entry in fps_data_list}


def export_per_frame_to_csv(per_frame_data: dict, output_path: str):
    """
    Export per-frame data to CSV for easy plotting/analysis.

    Args:
        per_frame_data: Dict from results['per_frame_data']
        output_path: Path to save CSV
    """
    import csv

    if not per_frame_data.get('enabled', False):
        print("⚠️  No per-frame data to export")
        return

    frames = per_frame_data['frames']
    if not frames:
        print("⚠️  No frame data to export")
        return

    # Determine columns from first frame
    fieldnames = ['frame_index', 'timestamp']

    # Collect all possible columns from all frames (not just first frame)
    all_cols = set()
    for frame in frames:
        all_cols.update(frame.keys())

    # Add standard columns in preferred order if they exist
    for col in ['fps', 'fps_interpolated', 'ssim', 'mse', 'psnr',
                'lpips', 'flip', 'optical_flow']:
        if col in all_cols and col not in fieldnames:
            fieldnames.append(col)

    # Write CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(frames)

    print(f"\n✓ Per-frame data exported to: {output_path}")
    print(f"  Rows: {len(frames)}")
    print(f"  Columns: {', '.join(fieldnames)}")


def compare_alignment_quality(
    video1_path: str,
    video2_path: str,
    alignment_name: str,
    sample_rate: int = 1,
    compute_advanced: bool = True,
    use_gpu: bool = True,
    extract_fps: bool = False,
    fps_video1: str = None,
    fps_video2: str = None,
    fps_roi: tuple = None,
    fps_sample_rate: int = 1,
    store_per_frame: bool = True
):
    """
    Compare two aligned videos frame-by-frame.

    Args:
        video1_path: Path to first video (reference/ground truth)
        video2_path: Path to second video (distorted/to evaluate)
        alignment_name: Name of alignment method (for display)
        sample_rate: Sample every Nth frame for frame-by-frame metrics (1 = all frames)
        compute_advanced: Enable advanced metrics (LPIPS, FLIP, optical flow)
        use_gpu: Use GPU acceleration for LPIPS if available
        extract_fps: Extract FPS data from source videos with overlays
        fps_video1: Path to source video with FPS overlay for video1 (if different from video1)
        fps_video2: Path to source video with FPS overlay for video2 (if different from video2)
        fps_roi: ROI as (x, y, width, height) or None for auto-detection
        fps_sample_rate: FPS extraction sample rate (1 = every frame)
        store_per_frame: Store per-frame data in output dict (vs only CSV)

    Returns:
        Dictionary with metrics
    """
    print(f"\n{'='*80}")
    print(f"Analyzing: {alignment_name}".center(80))
    print(f"{'='*80}")

    # FPS extraction (if enabled)
    fps_lookup_v1 = None
    fps_lookup_v2 = None
    fps_roi_used = None

    if extract_fps:
        print(f"\n{'='*80}")
        print("Extracting FPS Data".center(80))
        print(f"{'='*80}\n")

        try:
            if fps_video1:
                fps_data_v1, roi_v1 = extract_fps_from_video(
                    fps_video1, fps_roi, fps_sample_rate
                )
                fps_lookup_v1 = build_fps_lookup(fps_data_v1)
                fps_roi_used = roi_v1

            if fps_video2:
                fps_data_v2, roi_v2 = extract_fps_from_video(
                    fps_video2, fps_roi, fps_sample_rate
                )
                fps_lookup_v2 = build_fps_lookup(fps_data_v2)
                fps_roi_used = fps_roi_used or roi_v2

        except FPSExtractionError as e:
            print(f"\n⚠️  {e}")
            print("Continuing with quality comparison only...\n")
            extract_fps = False

    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)

    total_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
    total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))

    frames_to_compare = min(total_frames1, total_frames2)

    print(f"\nVideo 1: {Path(video1_path).name}")
    print(f"  Frames: {total_frames1}")
    print(f"\nVideo 2: {Path(video2_path).name}")
    print(f"  Frames: {total_frames2}")
    print(f"\nComparing: {frames_to_compare} frames (sampling every {sample_rate} frame)")

    # Initialize advanced metrics if requested
    advanced_metrics = None
    basic_metrics_gpu = None
    device = 'cpu'

    if use_gpu and TORCH_AVAILABLE:
        # Check if CUDA is available
        import torch  # Import here since TORCH_AVAILABLE is True
        if torch.cuda.is_available():
            device = 'cuda'
            print(f"\n✓ GPU acceleration enabled (device: {device})")

            # Initialize GPU basic metrics
            try:
                basic_metrics_gpu = BasicMetricsGPU(device=device)
                print("  • Basic metrics (SSIM/MSE/PSNR): GPU-accelerated")
                if not PYTORCH_MSSSIM_AVAILABLE:
                    print("    ⚠️  pytorch-msssim not found, SSIM will use CPU fallback")
            except Exception as e:
                print(f"  ⚠️  Failed to initialize GPU basic metrics: {e}")
                print("     Falling back to CPU for basic metrics")
        else:
            print("\n⚠️  GPU requested but CUDA not available, using CPU")

    if compute_advanced:
        advanced_metrics = AdvancedMetrics(device=device)
        print(f"\n✓ Advanced metrics initialized (device: {device})")
        if LPIPS_AVAILABLE:
            print("  • LPIPS: Available")
        else:
            print("  • LPIPS: Not available (install: pip install lpips torch torchvision)")
        print("  • FLIP: Available")
        print("  • Optical Flow: Available")

    print()

    # Metric storage
    ssim_scores = []
    mse_scores = []
    psnr_scores = []
    lpips_scores = []
    flip_scores = []
    optical_flow_diffs = []

    # Per-frame data storage
    per_frame_data_list = []

    # Frame history for temporal metrics (need t-1, t, t+1)
    frame1_history = []
    frame2_history = []

    frame_idx = 0
    compared_count = 0

    pbar = tqdm(total=frames_to_compare, desc="Comparing frames", unit="frame")

    while frame_idx < frames_to_compare:
        # Read frames
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break

        # Sample frames
        if frame_idx % sample_rate == 0:
            # Compute basic metrics (SSIM, MSE, PSNR)
            if basic_metrics_gpu is not None:
                # GPU-accelerated path
                gpu_results = basic_metrics_gpu.compute_all(frame1, frame2)
                ssim_score = gpu_results['ssim']
                mse = gpu_results['mse']
                psnr = gpu_results['psnr']
            else:
                # CPU fallback path
                gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

                # Compute SSIM
                ssim_score = ssim(gray1, gray2)

                # Compute MSE
                mse = np.mean((frame1.astype(float) - frame2.astype(float)) ** 2)

                # Compute PSNR
                psnr = cv2.PSNR(frame1, frame2)

            ssim_scores.append(ssim_score)
            mse_scores.append(mse)
            psnr_scores.append(psnr)

            # Advanced metrics
            if compute_advanced and advanced_metrics is not None:
                # Maintain frame history (need 3 frames for optical flow)
                frame1_history.append(frame1.copy())
                frame2_history.append(frame2.copy())

                if len(frame1_history) > 3:
                    frame1_history.pop(0)
                    frame2_history.pop(0)

                # Compute advanced metrics (need at least 3 frames for optical flow)
                prev1 = frame1_history[-2] if len(frame1_history) >= 2 else None
                prev2 = frame2_history[-2] if len(frame2_history) >= 2 else None
                next1 = frame1_history[-1] if len(frame1_history) >= 3 else None
                next2 = frame2_history[-1] if len(frame2_history) >= 3 else None

                adv_results = compute_all_metrics(
                    frame1, frame2,
                    prev_frame1=prev1, prev_frame2=prev2,
                    next_frame1=next1, next_frame2=next2,
                    metrics_instance=advanced_metrics
                )

                if 'lpips' in adv_results:
                    lpips_scores.append(adv_results['lpips'])
                if 'flip' in adv_results:
                    flip_scores.append(adv_results['flip'])
                if 'optical_flow' in adv_results:
                    optical_flow_diffs.append(adv_results['optical_flow']['difference'])

            # Collect per-frame data (if FPS extraction enabled)
            if extract_fps and store_per_frame:
                frame_data = {
                    'frame_index': frame_idx,
                    'timestamp': round(frame_idx / cap2.get(cv2.CAP_PROP_FPS), 3),
                    'ssim': float(ssim_score),
                    'mse': float(mse),
                    'psnr': float(psnr)
                }

                # Add FPS from video2 if available
                if fps_lookup_v2 and frame_idx in fps_lookup_v2:
                    fps_entry = fps_lookup_v2[frame_idx]
                    frame_data['fps'] = fps_entry['fps']
                    frame_data['fps_interpolated'] = fps_entry.get('interpolated', False)

                # Add advanced metrics if computed
                if 'lpips' in adv_results:
                    frame_data['lpips'] = adv_results['lpips']
                if 'flip' in adv_results:
                    frame_data['flip'] = adv_results['flip']
                if 'optical_flow' in adv_results:
                    frame_data['optical_flow'] = adv_results['optical_flow']['difference']

                per_frame_data_list.append(frame_data)

            compared_count += 1

        frame_idx += 1
        pbar.update(1)

    pbar.close()
    cap1.release()
    cap2.release()

    # Calculate statistics
    ssim_array = np.array(ssim_scores)
    mse_array = np.array(mse_scores)
    psnr_array = np.array(psnr_scores)

    results = {
        "alignment_method": alignment_name,
        "video1": str(video1_path),
        "video2": str(video2_path),
        "frames_compared": compared_count,
        "metrics": {
            "ssim": {
                "mean": float(np.mean(ssim_array)),
                "std": float(np.std(ssim_array)),
                "min": float(np.min(ssim_array)),
                "max": float(np.max(ssim_array)),
                "median": float(np.median(ssim_array))
            },
            "mse": {
                "mean": float(np.mean(mse_array)),
                "std": float(np.std(mse_array)),
                "min": float(np.min(mse_array)),
                "max": float(np.max(mse_array)),
                "median": float(np.median(mse_array))
            },
            "psnr": {
                "mean": float(np.mean(psnr_array)),
                "std": float(np.std(psnr_array)),
                "min": float(np.min(psnr_array)),
                "max": float(np.max(psnr_array)),
                "median": float(np.median(psnr_array))
            }
        }
    }

    # Add advanced metrics if computed
    if compute_advanced:
        if lpips_scores:
            lpips_array = np.array(lpips_scores)
            results["metrics"]["lpips"] = {
                "mean": float(np.mean(lpips_array)),
                "std": float(np.std(lpips_array)),
                "min": float(np.min(lpips_array)),
                "max": float(np.max(lpips_array)),
                "median": float(np.median(lpips_array))
            }

        if flip_scores:
            flip_array = np.array(flip_scores)
            results["metrics"]["flip"] = {
                "mean": float(np.mean(flip_array)),
                "std": float(np.std(flip_array)),
                "min": float(np.min(flip_array)),
                "max": float(np.max(flip_array)),
                "median": float(np.median(flip_array))
            }

        if optical_flow_diffs:
            of_array = np.array(optical_flow_diffs)
            results["metrics"]["optical_flow_consistency"] = {
                "mean": float(np.mean(of_array)),
                "std": float(np.std(of_array)),
                "min": float(np.min(of_array)),
                "max": float(np.max(of_array)),
                "median": float(np.median(of_array))
            }

    # Print results
    print("\n" + "="*80)
    print("RESULTS".center(80))
    print("="*80)
    print(f"\nFrames Compared: {compared_count}")
    print(f"\nSSIM (Structural Similarity):")
    print(f"  Mean:   {results['metrics']['ssim']['mean']:.4f}")
    print(f"  Std:    {results['metrics']['ssim']['std']:.4f}")
    print(f"  Min:    {results['metrics']['ssim']['min']:.4f}")
    print(f"  Max:    {results['metrics']['ssim']['max']:.4f}")
    print(f"  Median: {results['metrics']['ssim']['median']:.4f}")
    print(f"\nMSE (Mean Squared Error):")
    print(f"  Mean:   {results['metrics']['mse']['mean']:.2f}")
    print(f"  Std:    {results['metrics']['mse']['std']:.2f}")
    print(f"  Min:    {results['metrics']['mse']['min']:.2f}")
    print(f"  Max:    {results['metrics']['mse']['max']:.2f}")
    print(f"\nPSNR (Peak Signal-to-Noise Ratio) [dB]:")
    print(f"  Mean:   {results['metrics']['psnr']['mean']:.2f}")
    print(f"  Std:    {results['metrics']['psnr']['std']:.2f}")
    print(f"  Min:    {results['metrics']['psnr']['min']:.2f}")
    print(f"  Max:    {results['metrics']['psnr']['max']:.2f}")

    # Advanced metrics output
    if 'lpips' in results['metrics']:
        print(f"\nLPIPS (Perceptual Similarity) [lower is better]:")
        print(f"  Mean:   {results['metrics']['lpips']['mean']:.4f}")
        print(f"  Std:    {results['metrics']['lpips']['std']:.4f}")
        print(f"  Median: {results['metrics']['lpips']['median']:.4f}")

    if 'flip' in results['metrics']:
        print(f"\nFLIP (Visual Error) [lower is better]:")
        print(f"  Mean:   {results['metrics']['flip']['mean']:.2f}")
        print(f"  Std:    {results['metrics']['flip']['std']:.2f}")
        print(f"  Median: {results['metrics']['flip']['median']:.2f}")

    if 'optical_flow_consistency' in results['metrics']:
        print(f"\nTemporal Flow Consistency [lower is better]:")
        print(f"  Mean:   {results['metrics']['optical_flow_consistency']['mean']:.2f}")
        print(f"  Std:    {results['metrics']['optical_flow_consistency']['std']:.2f}")
        print(f"  Median: {results['metrics']['optical_flow_consistency']['median']:.2f}")

    # Add per-frame data (if FPS extraction enabled)
    if extract_fps and per_frame_data_list:
        results['per_frame_data'] = {
            "enabled": True,
            "sample_rate": sample_rate,
            "fps_sample_rate": fps_sample_rate,
            "fps_source_video1": fps_video1,
            "fps_source_video2": fps_video2,
            "fps_roi": {
                "x": fps_roi_used[0],
                "y": fps_roi_used[1],
                "width": fps_roi_used[2],
                "height": fps_roi_used[3]
            } if fps_roi_used else None,
            "frames": per_frame_data_list
        }

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Compare alignment quality with advanced perceptual metrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison (SSIM + MSE only)
  python scripts/compare_alignment_quality.py \\
      --video1 recordings/cyberpunk/aligned/run1.mp4 \\
      --video2 recordings/cyberpunk/aligned/run2.mp4 \\
      --no-advanced

  # Full comparison with advanced metrics (LPIPS, FLIP, Optical Flow)
  python scripts/compare_alignment_quality.py \\
      --video1 recordings/cyberpunk/aligned/run1.mp4 \\
      --video2 recordings/cyberpunk/aligned/run2.mp4 \\
      --name "ICAT Manual" \\
      --sample-rate 30 \\
      --output quality_advanced.json

Advanced Metrics:
  • LPIPS: Perceptual similarity using deep learning (requires PyTorch + GPU)
  • FLIP: Visual error with perceptual weighting (NVIDIA-inspired)
  • Optical Flow: Temporal consistency for ghosting detection
        """
    )
    parser.add_argument('--video1', required=True, help='First video path (reference/ground truth)')
    parser.add_argument('--video2', required=True, help='Second video path (distorted/to evaluate)')
    parser.add_argument('--name', default='Alignment', help='Alignment method name')
    parser.add_argument('--sample-rate', type=int, default=10,
                        help='Sample every Nth frame for frame-by-frame metrics (default: 10)')
    parser.add_argument('--output', help='Save results to JSON file')
    parser.add_argument('--no-advanced', action='store_true',
                        help='Skip advanced frame metrics (LPIPS, FLIP, optical flow)')
    parser.add_argument('--cpu', action='store_true',
                        help='Force CPU mode (no GPU acceleration for LPIPS)')

    # FPS extraction arguments
    parser.add_argument('--extract-fps', action='store_true',
                        help='Extract FPS data from source videos with overlays and enable per-frame correlation')
    parser.add_argument('--fps-video1', type=str,
                        help='Source video with FPS overlay for video1 (if different from video1)')
    parser.add_argument('--fps-video2', type=str,
                        help='Source video with FPS overlay for video2 (if different from video2)')
    parser.add_argument('--fps-roi', type=str,
                        help='ROI as "x,y,width,height" or path to fps_roi.json. Omit for auto-detection.')
    parser.add_argument('--fps-sample-rate', type=int, default=1,
                        help='FPS extraction sample rate (1=every frame, default: 1)')
    parser.add_argument('--export-csv', type=str,
                        help='Export per-frame data to CSV file for plotting/analysis')
    parser.add_argument('--no-per-frame-data', action='store_true',
                        help='Skip storing per-frame data in JSON (only export CSV)')

    args = parser.parse_args()

    # Parse FPS ROI if provided
    fps_roi = parse_fps_roi(args.fps_roi) if hasattr(args, 'fps_roi') and args.fps_roi else None

    results = compare_alignment_quality(
        args.video1,
        args.video2,
        args.name,
        args.sample_rate,
        compute_advanced=not args.no_advanced,
        use_gpu=not args.cpu,
        extract_fps=args.extract_fps if hasattr(args, 'extract_fps') else False,
        fps_video1=args.fps_video1 if hasattr(args, 'fps_video1') else None,
        fps_video2=args.fps_video2 if hasattr(args, 'fps_video2') else None,
        fps_roi=fps_roi,
        fps_sample_rate=args.fps_sample_rate if hasattr(args, 'fps_sample_rate') else 1,
        store_per_frame=not args.no_per_frame_data if hasattr(args, 'no_per_frame_data') else True
    )

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {args.output}")

    # Export CSV if requested
    if hasattr(args, 'export_csv') and args.export_csv and 'per_frame_data' in results:
        export_per_frame_to_csv(results['per_frame_data'], args.export_csv)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
