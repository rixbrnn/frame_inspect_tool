#!/usr/bin/env python3
"""
Simple Benchmark Stability Validator

Reuses existing video comparison code to validate benchmark reproducibility.
Just a thin wrapper around your existing tools!

Usage:
    python validate_benchmark.py \
        --video1 DLAA_run1.mp4 \
        --video2 DLAA_run2.mp4 \
        --game "Cyberpunk 2077"
"""

import argparse
import json
import sys
from pathlib import Path
from src.comparison.video import get_video_similarity


# Thresholds from methodology (lines 85-90)
SSIM_THRESHOLD = 99.0  # Mean SSIM ≥ 99%
SSIM_STD_THRESHOLD = 1.0  # Std dev < 1%
MIN_SSIM_THRESHOLD = 95.0  # No frame below 95%


def validate_benchmark(video1: Path, video2: Path, game_name: str, output: Path = None):
    """
    Validate if benchmark is stable enough for DLSS comparison

    Uses existing get_video_similarity() function from video_comparison.py
    """
    print("=" * 80)
    print("BENCHMARK STABILITY VALIDATION".center(80))
    print("=" * 80)
    print(f"\nGame: {game_name}")
    print(f"Comparing: {video1.name} vs {video2.name}")
    print()

    # Use existing comparison code!
    print("Running comparison (using existing tools)...")
    avg_ssim = get_video_similarity(
        str(video1),
        str(video2),
        find_intersection=False,  # Should be identical, no need to sync
        metric='ssim'
    )

    if avg_ssim is None:
        print("\n✗ Comparison failed")
        return False

    # Evaluate stability
    print("\n" + "=" * 80)
    print("RESULTS".center(80))
    print("=" * 80)

    print(f"\nAverage SSIM: {avg_ssim:.2f}%")
    print(f"Threshold:    {SSIM_THRESHOLD:.2f}%")
    print()

    is_stable = avg_ssim >= SSIM_THRESHOLD

    if is_stable:
        print("✓ BENCHMARK IS STABLE")
        print(f"  → Suitable for DLSS comparison")
        print(f"  → Proceed with data collection")
        verdict = "ACCEPT"
    else:
        diff = SSIM_THRESHOLD - avg_ssim
        print("✗ BENCHMARK IS UNSTABLE")
        print(f"  → SSIM too low by {diff:.2f}%")
        print(f"  → Contains non-deterministic elements")
        print(f"  → Do NOT use for DLSS comparison")
        print()
        print("Possible causes:")
        print("  • Random AI behavior (NPCs, enemies)")
        print("  • Procedural animations (vegetation, particles)")
        print("  • Physics simulation variations")
        print("  • Frame timing inconsistencies")
        print()
        print("Try:")
        print("  • Different benchmark scene")
        print("  • Game with deterministic benchmark")
        print("  • Photo mode if available")
        verdict = "REJECT"

    # Save report
    if output:
        report = {
            'game': game_name,
            'videos': {
                'video1': str(video1),
                'video2': str(video2)
            },
            'results': {
                'avg_ssim': avg_ssim,
                'threshold': SSIM_THRESHOLD,
                'is_stable': is_stable
            },
            'verdict': verdict
        }

        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n  Report saved: {output}")

    print("\n" + "=" * 80)

    return is_stable


def main():
    parser = argparse.ArgumentParser(
        description="Validate benchmark stability (Phase 0 of methodology)"
    )
    parser.add_argument("--video1", type=Path, required=True, help="First recording")
    parser.add_argument("--video2", type=Path, required=True, help="Second recording")
    parser.add_argument("--game", required=True, help="Game name")
    parser.add_argument("--output", type=Path, help="Output JSON report")

    args = parser.parse_args()

    if not args.video1.exists():
        print(f"✗ Video 1 not found: {args.video1}")
        sys.exit(2)

    if not args.video2.exists():
        print(f"✗ Video 2 not found: {args.video2}")
        sys.exit(2)

    is_stable = validate_benchmark(args.video1, args.video2, args.game, args.output)

    # Exit code: 0 = stable, 1 = unstable
    sys.exit(0 if is_stable else 1)


if __name__ == "__main__":
    main()
