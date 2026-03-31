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

from src.comparison.advanced_metrics import AdvancedMetrics, compute_all_metrics, LPIPS_AVAILABLE

# Check for torch availability (for GPU detection)
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def compare_alignment_quality(
    video1_path: str,
    video2_path: str,
    alignment_name: str,
    sample_rate: int = 1,
    compute_advanced: bool = True,
    use_gpu: bool = True
):
    """
    Compare two aligned videos frame-by-frame.

    Args:
        video1_path: Path to first video
        video2_path: Path to second video
        alignment_name: Name of alignment method (for display)
        sample_rate: Sample every Nth frame (1 = all frames)
        compute_advanced: Enable advanced metrics (LPIPS, FLIP, optical flow)
        use_gpu: Use GPU acceleration for LPIPS if available

    Returns:
        Dictionary with metrics
    """
    print(f"\n{'='*80}")
    print(f"Analyzing: {alignment_name}".center(80))
    print(f"{'='*80}")

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
    if compute_advanced:
        device = 'cpu'
        if use_gpu and TORCH_AVAILABLE and torch.cuda.is_available():
            device = 'cuda'

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
    lpips_scores = []
    flip_scores = []
    optical_flow_diffs = []

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
            # Existing metrics: SSIM, MSE
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            # Compute SSIM
            ssim_score = ssim(gray1, gray2)
            ssim_scores.append(ssim_score)

            # Compute MSE
            mse = np.mean((frame1.astype(float) - frame2.astype(float)) ** 2)
            mse_scores.append(mse)

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

            compared_count += 1

        frame_idx += 1
        pbar.update(1)

    pbar.close()
    cap1.release()
    cap2.release()

    # Calculate statistics
    ssim_array = np.array(ssim_scores)
    mse_array = np.array(mse_scores)

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
    parser.add_argument('--video1', required=True, help='First video path')
    parser.add_argument('--video2', required=True, help='Second video path')
    parser.add_argument('--name', default='Alignment', help='Alignment method name')
    parser.add_argument('--sample-rate', type=int, default=10,
                        help='Sample every Nth frame (default: 10)')
    parser.add_argument('--output', help='Save results to JSON file')
    parser.add_argument('--no-advanced', action='store_true',
                        help='Skip advanced metrics (LPIPS, FLIP, optical flow)')
    parser.add_argument('--cpu', action='store_true',
                        help='Force CPU mode (no GPU acceleration for LPIPS)')

    args = parser.parse_args()

    results = compare_alignment_quality(
        args.video1,
        args.video2,
        args.name,
        args.sample_rate,
        compute_advanced=not args.no_advanced,
        use_gpu=not args.cpu
    )

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {args.output}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
