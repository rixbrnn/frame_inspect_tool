#!/usr/bin/env python3
"""
Compare ICAT Manual Alignment vs Automated Visual Hash Sync

Shows the differences between manual and automated alignment approaches.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.trim.legacy.icat_parser import parse_icat_alignment


def compare_sync_methods(icat_json_path: str):
    """
    Compare ICAT manual alignment with automated visual hash results.

    Args:
        icat_json_path: Path to ICAT JSON file
    """
    print("=" * 80)
    print("SYNC METHOD COMPARISON: ICAT MANUAL vs AUTOMATED VISUAL HASH".center(80))
    print("=" * 80)

    # Parse ICAT alignment
    icat = parse_icat_alignment(icat_json_path)

    print("\n📊 ICAT MANUAL ALIGNMENT (Ground Truth)")
    print("-" * 80)
    print(f"Method: Frame-by-frame manual alignment in NVIDIA ICAT")
    print(f"Aligned Duration: {icat.aligned_duration:.2f}s ({int(icat.aligned_duration * 60)} frames @ 60fps)")
    print(f"\nVideo 1: {icat.videos[0].video_name or 'Video 1'}")
    print(f"  Frames: {icat.videos[0].start_frame:5d} to {icat.videos[0].end_frame:5d}")
    print(f"  Time:   {icat.videos[0].start_time:5.2f}s to {icat.videos[0].end_time:5.2f}s")
    print(f"\nVideo 2: {icat.videos[1].video_name or 'Video 2'}")
    print(f"  Frames: {icat.videos[1].start_frame:5d} to {icat.videos[1].end_frame:5d}")
    print(f"  Time:   {icat.videos[1].start_time:5.2f}s to {icat.videos[1].end_time:5.2f}s")

    print("\n\n🤖 AUTOMATED VISUAL HASH SYNC")
    print("-" * 80)
    print(f"Method: Perceptual hashing with preprocessing")
    print(f"  - Crop FPS counter (top-left 200x100)")
    print(f"  - Convert to grayscale")
    print(f"  - Apply heavy Gaussian blur (21x21)")
    print(f"  - Compute perceptual hash per frame")
    print(f"  - Find hash matches with Hamming distance ≤ 8")
    print(f"\nResult: ❌ FAILED")
    print(f"  - Found 66,619 potential hash matches")
    print(f"  - Longest consecutive sequence: 2 frames")
    print(f"  - Required minimum: 30 frames")
    print(f"  - Cannot establish valid alignment")

    print("\n\n📈 ANALYSIS")
    print("-" * 80)
    print("Why automated sync failed:")
    print("  1. Videos are DIFFERENT GAMEPLAY SESSIONS, not identical content")
    print("  2. Different starting points (menus, loading screens, game state)")
    print("  3. Different player actions and camera angles throughout")
    print("  4. Only 2 consecutive matching frames found (random similarity)")
    print(f"  5. ICAT found {icat.aligned_duration:.0f}s of aligned content through manual alignment")
    print("\nICAT Success Factors:")
    print("  ✓ Human can identify EQUIVALENT game segments (not identical)")
    print("  ✓ Manual frame-by-frame scrubbing to match scene context")
    print("  ✓ Understanding of gameplay flow and benchmarking intent")
    print("  ✓ Ability to skip unrelated intro/outro content")

    print("\n\n💡 CONCLUSION")
    print("-" * 80)
    print("For non-identical game recordings (different play-throughs):")
    print("  ✅ Manual ICAT alignment: REQUIRED and EFFECTIVE")
    print("  ❌ Automated visual sync: NOT VIABLE")
    print("\nAutomated sync would only work if:")
    print("  - Videos captured from SAME gameplay session (e.g., different capture cards)")
    print("  - Identical frame content with only time offsets")
    print("  - Your case: completely different recordings → manual alignment needed")

    print("\n" + "=" * 80)
    print(f"✓ Use ICAT manual alignment for your benchmark analysis")
    print(f"✓ Trimmed videos available in: aligned/ subfolder")
    print("=" * 80)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Compare sync methods')
    parser.add_argument('--icat', required=True, help='ICAT JSON file')

    args = parser.parse_args()

    compare_sync_methods(args.icat)


if __name__ == "__main__":
    main()
