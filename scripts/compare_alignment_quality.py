#!/usr/bin/env python3
"""
Compare alignment quality between ICAT and Scene-based methods

Computes SSIM and other metrics across all frames to determine
which alignment produces better frame-to-frame similarity.
"""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from pathlib import Path
import json
from tqdm import tqdm


def compare_alignment_quality(
    video1_path: str,
    video2_path: str,
    alignment_name: str,
    sample_rate: int = 1
):
    """
    Compare two aligned videos frame-by-frame.

    Args:
        video1_path: Path to first video
        video2_path: Path to second video
        alignment_name: Name of alignment method (for display)
        sample_rate: Sample every Nth frame (1 = all frames)

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
    print()

    ssim_scores = []
    mse_scores = []

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
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            # Compute SSIM
            ssim_score = ssim(gray1, gray2)
            ssim_scores.append(ssim_score)

            # Compute MSE
            mse = np.mean((frame1.astype(float) - frame2.astype(float)) ** 2)
            mse_scores.append(mse)

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

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Compare alignment quality')
    parser.add_argument('--video1', required=True, help='First video')
    parser.add_argument('--video2', required=True, help='Second video')
    parser.add_argument('--name', default='Alignment', help='Alignment method name')
    parser.add_argument('--sample-rate', type=int, default=10, help='Sample every Nth frame (default: 10)')
    parser.add_argument('--output', help='Save results to JSON')

    args = parser.parse_args()

    results = compare_alignment_quality(
        args.video1,
        args.video2,
        args.name,
        args.sample_rate
    )

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {args.output}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
