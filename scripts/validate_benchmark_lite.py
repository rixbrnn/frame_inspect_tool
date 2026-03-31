#!/usr/bin/env python3
"""
Lightweight Benchmark Stability Validator

Uses frame sampling to avoid memory issues with large videos.
Samples every Nth frame instead of loading entire videos.
"""

import argparse
import json
import sys
from pathlib import Path
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def sample_frames(video_path, sample_rate=10, skip_start=0, max_frames=None):
    """Sample every Nth frame from video, optionally skipping start"""
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    frame_idx = 0

    # Skip initial frames
    if skip_start > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, skip_start)
        frame_idx = skip_start

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if (frame_idx - skip_start) % sample_rate == 0:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)

            if max_frames and len(frames) >= max_frames:
                break

        frame_idx += 1

    cap.release()
    return frames, frame_idx

def compute_ssim(frame1, frame2):
    """Compute SSIM between two frames"""
    # Convert to grayscale for SSIM
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)

    score, _ = ssim(gray1, gray2, full=True)
    return score * 100  # Convert to percentage

def main():
    parser = argparse.ArgumentParser(description='Validate benchmark stability (memory-efficient version)')
    parser.add_argument('--video1', type=Path, required=True)
    parser.add_argument('--video2', type=Path, required=True)
    parser.add_argument('--game', type=str, required=True)
    parser.add_argument('--output', type=Path, default=None)
    parser.add_argument('--sample-rate', type=int, default=10,
                       help='Sample every Nth frame (default: 10)')
    parser.add_argument('--skip-start', type=int, default=0,
                       help='Skip first N seconds from both videos (default: 0)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Compare only first N seconds (default: all)')

    args = parser.parse_args()

    print("=" * 80)
    print("BENCHMARK STABILITY VALIDATION (LITE)".center(80))
    print("=" * 80)
    print(f"\nGame: {args.game}")
    print(f"Comparing: {args.video1.name} vs {args.video2.name}")
    print(f"Sample rate: Every {args.sample_rate} frames")
    if args.skip_start > 0:
        print(f"Skipping: First {args.skip_start} seconds")
    if args.duration:
        print(f"Duration: {args.duration} seconds")
    print()

    # Calculate frame parameters (assuming 60 FPS)
    fps = 60
    skip_frames = args.skip_start * fps if args.skip_start else 0
    max_frames = (args.duration * fps // args.sample_rate) if args.duration else None

    # Load frames with sampling
    print("Loading video 1 (sampled)...")
    frames1, total1 = sample_frames(args.video1, args.sample_rate, skip_frames, max_frames)
    print(f"  → Loaded {len(frames1)} frames (of {total1} total)")

    print("Loading video 2 (sampled)...")
    frames2, total2 = sample_frames(args.video2, args.sample_rate, skip_frames, max_frames)
    print(f"  → Loaded {len(frames2)} frames (of {total2} total)")

    # Compare frame counts - use minimum if different
    if len(frames1) != len(frames2):
        print(f"\nℹ Video lengths differ:")
        print(f"  Video 1: {total1} frames ({len(frames1)} sampled)")
        print(f"  Video 2: {total2} frames ({len(frames2)} sampled)")
        min_len = min(len(frames1), len(frames2))
        print(f"  → Comparing first {min_len} sampled frames from each")
        frames1 = frames1[:min_len]
        frames2 = frames2[:min_len]

    # Compute SSIM for each frame pair
    print(f"\nComputing SSIM on {len(frames1)} frame pairs...")
    ssim_scores = []

    for i, (f1, f2) in enumerate(zip(frames1, frames2)):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(frames1)} frames", end='\r')

        score = compute_ssim(f1, f2)
        ssim_scores.append(score)

    print(f"  Progress: {len(frames1)}/{len(frames1)} frames - Done!")

    # Calculate statistics
    avg_ssim = np.mean(ssim_scores)
    min_ssim = np.min(ssim_scores)
    std_ssim = np.std(ssim_scores)

    # Results
    print("\n" + "=" * 80)
    print("RESULTS".center(80))
    print("=" * 80)
    print(f"\nAverage SSIM: {avg_ssim:.2f}%")
    print(f"Min SSIM:     {min_ssim:.2f}%")
    print(f"Std Dev:      {std_ssim:.2f}%")
    print(f"Threshold:    99.00%")
    print()

    # Verdict
    THRESHOLD = 99.0
    is_stable = avg_ssim >= THRESHOLD

    if is_stable:
        print("✓ BENCHMARK IS STABLE")
        print(f"  → Suitable for DLSS comparison")
        print(f"  → Proceed with data collection")
        verdict = "ACCEPT"
    else:
        diff = THRESHOLD - avg_ssim
        print("✗ BENCHMARK IS UNSTABLE")
        print(f"  → SSIM too low by {diff:.2f}%")
        print(f"  → Contains non-deterministic elements")
        print(f"  → Do NOT use for DLSS comparison")
        verdict = "REJECT"

    print("\n" + "=" * 80)

    # Save results
    if args.output:
        results = {
            "game": args.game,
            "video1": str(args.video1),
            "video2": str(args.video2),
            "sample_rate": args.sample_rate,
            "frames_compared": len(frames1),
            "total_frames": total1,
            "avg_ssim": float(avg_ssim),
            "min_ssim": float(min_ssim),
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
