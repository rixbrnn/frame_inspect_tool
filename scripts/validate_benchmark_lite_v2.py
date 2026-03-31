#!/usr/bin/env python3
"""
Memory-Efficient Benchmark Validator with Synchronization

1. Finds intersection using perceptual hashing (sampled)
2. Compares aligned section frame-by-frame (sampled)
"""

import argparse
import json
import sys
from pathlib import Path
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import imagehash
from PIL import Image

def compute_perceptual_hash(frame):
    """Compute perceptual hash for a frame"""
    # Convert numpy array to PIL Image
    pil_image = Image.fromarray(frame)
    # Compute average hash (fast and robust)
    return imagehash.average_hash(pil_image)

def find_sync_point(video1_path, video2_path, sample_rate=30):
    """
    Find where two videos align using perceptual hashing.
    Returns (offset1, offset2) - frame offsets to start comparison
    """
    print("Finding synchronization point...")

    cap1 = cv2.VideoCapture(str(video1_path))
    cap2 = cv2.VideoCapture(str(video2_path))

    # Sample frames and compute hashes
    hashes1 = []
    hashes2 = []

    frame_idx = 0
    while True:
        ret1, frame1 = cap1.read()
        if not ret1:
            break
        if frame_idx % sample_rate == 0:
            frame_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            hashes1.append((frame_idx, compute_perceptual_hash(frame_rgb)))
        frame_idx += 1

    print(f"  Video 1: {len(hashes1)} hash samples")

    frame_idx = 0
    while True:
        ret2, frame2 = cap2.read()
        if not ret2:
            break
        if frame_idx % sample_rate == 0:
            frame_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            hashes2.append((frame_idx, compute_perceptual_hash(frame_rgb)))
        frame_idx += 1

    print(f"  Video 2: {len(hashes2)} hash samples")

    cap1.release()
    cap2.release()

    # Find best alignment using sliding window
    best_match_score = 0
    best_offset1 = 0
    best_offset2 = 0

    # Search window: first 20% of shorter video
    max_search = min(len(hashes1), len(hashes2)) // 5

    print(f"  Searching for alignment (window: {max_search} samples)...")

    for offset1 in range(max_search):
        for offset2 in range(max_search):
            # Compare next 50 hashes
            compare_len = min(50, len(hashes1) - offset1, len(hashes2) - offset2)
            if compare_len < 10:
                continue

            matches = 0
            for i in range(compare_len):
                hash1 = hashes1[offset1 + i][1]
                hash2 = hashes2[offset2 + i][1]
                # Hamming distance (lower = more similar)
                distance = hash1 - hash2
                if distance < 10:  # Threshold for "similar"
                    matches += 1

            score = matches / compare_len
            if score > best_match_score:
                best_match_score = score
                best_offset1 = hashes1[offset1][0]
                best_offset2 = hashes2[offset2][0]

    print(f"  Best match: {best_match_score*100:.1f}% similarity")
    print(f"  Video 1 offset: frame {best_offset1}")
    print(f"  Video 2 offset: frame {best_offset2}")

    if best_match_score < 0.5:
        print(f"  ⚠️  Low confidence ({best_match_score*100:.1f}%), videos may not overlap")

    return best_offset1, best_offset2

def load_frames_from_offset(video_path, start_frame, sample_rate, max_samples):
    """Load sampled frames starting from offset"""
    cap = cv2.VideoCapture(str(video_path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frames = []
    frame_idx = 0

    while len(frames) < max_samples:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_rate == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)

        frame_idx += 1

    cap.release()
    return frames

def compute_ssim(frame1, frame2):
    """Compute SSIM between two frames"""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
    score, _ = ssim(gray1, gray2, full=True)
    return score * 100

def main():
    parser = argparse.ArgumentParser(description='Benchmark validator with sync')
    parser.add_argument('--video1', type=Path, required=True)
    parser.add_argument('--video2', type=Path, required=True)
    parser.add_argument('--game', type=str, required=True)
    parser.add_argument('--output', type=Path, default=None)
    parser.add_argument('--sample-rate', type=int, default=10,
                       help='Compare every Nth frame after sync')
    parser.add_argument('--max-samples', type=int, default=500,
                       help='Max frames to compare after sync')

    args = parser.parse_args()

    print("=" * 80)
    print("BENCHMARK STABILITY VALIDATION".center(80))
    print("=" * 80)
    print(f"\nGame: {args.game}")
    print(f"Videos: {args.video1.name} vs {args.video2.name}")
    print()

    # Step 1: Find synchronization point
    offset1, offset2 = find_sync_point(args.video1, args.video2, sample_rate=30)
    print()

    # Step 2: Load aligned frames
    print(f"Loading aligned frames (sample rate: every {args.sample_rate} frames)...")
    frames1 = load_frames_from_offset(args.video1, offset1, args.sample_rate, args.max_samples)
    frames2 = load_frames_from_offset(args.video2, offset2, args.sample_rate, args.max_samples)

    compare_count = min(len(frames1), len(frames2))
    frames1 = frames1[:compare_count]
    frames2 = frames2[:compare_count]

    print(f"  Loaded {compare_count} frame pairs for comparison")
    print()

    # Step 3: Compute SSIM
    print(f"Computing SSIM on {compare_count} aligned frames...")
    ssim_scores = []

    for i, (f1, f2) in enumerate(zip(frames1, frames2)):
        if i % 50 == 0:
            print(f"  Progress: {i}/{compare_count}", end='\r')

        score = compute_ssim(f1, f2)
        ssim_scores.append(score)

    print(f"  Progress: {compare_count}/{compare_count} - Done!")

    # Results
    avg_ssim = np.mean(ssim_scores)
    min_ssim = np.min(ssim_scores)
    std_ssim = np.std(ssim_scores)

    print("\n" + "=" * 80)
    print("RESULTS".center(80))
    print("=" * 80)
    print(f"\nAverage SSIM: {avg_ssim:.2f}%")
    print(f"Min SSIM:     {min_ssim:.2f}%")
    print(f"Std Dev:      {std_ssim:.2f}%")
    print(f"Threshold:    99.00%")
    print()

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
            "sync_offset1": int(offset1),
            "sync_offset2": int(offset2),
            "frames_compared": int(compare_count),
            "sample_rate": args.sample_rate,
            "avg_ssim": float(avg_ssim),
            "min_ssim": float(min_ssim),
            "std_ssim": float(std_ssim),
            "threshold": float(THRESHOLD),
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
