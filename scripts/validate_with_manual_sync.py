#!/usr/bin/env python3
"""
Validate benchmark using manually determined sync offsets
"""

import argparse
import json
import sys
from pathlib import Path
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def compute_ssim(frame1, frame2):
    """Compute SSIM between two frames"""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray1, gray2, full=True)
    return score * 100

def validate_with_offsets(video1_path, video2_path, offset1, offset2, sample_rate=10):
    """Compare videos using known offsets"""
    cap1 = cv2.VideoCapture(str(video1_path))
    cap2 = cv2.VideoCapture(str(video2_path))

    total_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
    total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate how many frames we can compare
    max_comparable = min(total_frames1 - offset1, total_frames2 - offset2)

    print(f"\nComparing {max_comparable} frames (sampling every {sample_rate} frames)")
    print(f"Video 1 starting at frame {offset1}")
    print(f"Video 2 starting at frame {offset2}")

    ssim_scores = []
    frame_idx = 0

    while frame_idx < max_comparable:
        # Set positions
        cap1.set(cv2.CAP_PROP_POS_FRAMES, offset1 + frame_idx)
        cap2.set(cv2.CAP_PROP_POS_FRAMES, offset2 + frame_idx)

        # Read frames
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            break

        # Compute SSIM for sampled frames
        if frame_idx % sample_rate == 0:
            score = compute_ssim(frame1, frame2)
            ssim_scores.append(score)

            if len(ssim_scores) % 50 == 0:
                print(f"  Progress: {len(ssim_scores)} samples, current SSIM: {score:.2f}%", end='\r')

        frame_idx += 1

    print(f"\n  Completed: {len(ssim_scores)} frame samples analyzed")

    cap1.release()
    cap2.release()

    return ssim_scores

def main():
    parser = argparse.ArgumentParser(description='Validate with manual sync offsets')
    parser.add_argument('--sync', type=Path, required=True,
                       help='Manual sync JSON file')
    parser.add_argument('--output', type=Path,
                       help='Output JSON for results')
    parser.add_argument('--sample-rate', type=int, default=10,
                       help='Compare every Nth frame')

    args = parser.parse_args()

    # Load sync info
    with open(args.sync, 'r') as f:
        sync_info = json.load(f)

    video1_path = Path(sync_info['video1'])
    video2_path = Path(sync_info['video2'])
    offset1 = sync_info['video1_offset']
    offset2 = sync_info['video2_offset']

    print("=" * 80)
    print("BENCHMARK VALIDATION WITH MANUAL SYNC".center(80))
    print("=" * 80)
    print(f"\nVideo 1: {video1_path.name}")
    print(f"Video 2: {video2_path.name}")
    print(f"Offsets: Video1={offset1}, Video2={offset2}")

    # Run comparison
    ssim_scores = validate_with_offsets(video1_path, video2_path, offset1, offset2, args.sample_rate)

    # Calculate statistics
    avg_ssim = np.mean(ssim_scores)
    min_ssim = np.min(ssim_scores)
    max_ssim = np.max(ssim_scores)
    std_ssim = np.std(ssim_scores)

    print("\n" + "=" * 80)
    print("RESULTS".center(80))
    print("=" * 80)
    print(f"\nFrames compared: {len(ssim_scores)}")
    print(f"Average SSIM:    {avg_ssim:.2f}%")
    print(f"Min SSIM:        {min_ssim:.2f}%")
    print(f"Max SSIM:        {max_ssim:.2f}%")
    print(f"Std Dev:         {std_ssim:.2f}%")
    print(f"Threshold:       99.00%")
    print()

    THRESHOLD = 99.0
    is_stable = avg_ssim >= THRESHOLD

    if is_stable:
        print("✓ BENCHMARK IS STABLE")
        print(f"  → Suitable for DLSS comparison")
        verdict = "ACCEPT"
    else:
        diff = THRESHOLD - avg_ssim
        print("✗ BENCHMARK IS UNSTABLE")
        print(f"  → SSIM too low by {diff:.2f}%")
        print(f"  → Contains non-deterministic elements")
        verdict = "REJECT"

    print("\n" + "=" * 80)

    # Save results
    if args.output:
        results = {
            "video1": str(video1_path),
            "video2": str(video2_path),
            "video1_offset": offset1,
            "video2_offset": offset2,
            "frames_compared": len(ssim_scores),
            "sample_rate": args.sample_rate,
            "avg_ssim": float(avg_ssim),
            "min_ssim": float(min_ssim),
            "max_ssim": float(max_ssim),
            "std_ssim": float(std_ssim),
            "threshold": THRESHOLD,
            "verdict": verdict,
            "is_stable": bool(is_stable)
        }

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {args.output}")

    return 0 if is_stable else 1

if __name__ == "__main__":
    sys.exit(main())
