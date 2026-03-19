#!/usr/bin/env python3
"""
Simple CLI wrapper for CFR conversion

Usage:
    python scripts/convert_to_cfr.py video.mp4
    python scripts/convert_to_cfr.py video.mp4 --fps 120
    python scripts/convert_to_cfr.py video.mp4 --info
"""

import sys
sys.path.insert(0, '.')

from pathlib import Path
import argparse
from src.preprocessing.video import convert_to_cfr, get_video_info, ensure_cfr

def main():
    parser = argparse.ArgumentParser(
        description='Convert video to constant frame rate (CFR)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show video info
  python scripts/convert_to_cfr.py video.mp4 --info

  # Convert to CFR 60 FPS (auto-skips if already CFR)
  python scripts/convert_to_cfr.py video.mp4

  # Force conversion to 120 FPS
  python scripts/convert_to_cfr.py video.mp4 --fps 120

  # High quality conversion (lower CRF = better quality)
  python scripts/convert_to_cfr.py video.mp4 --crf 15
        """
    )

    parser.add_argument('video', type=Path, help='Input video file')
    parser.add_argument('--fps', type=int, default=60, help='Target FPS (default: 60)')
    parser.add_argument('--crf', type=int, default=18, help='Quality: 0-51, lower=better (default: 18)')
    parser.add_argument('--output', type=Path, help='Output file (default: input_60fps.mp4)')
    parser.add_argument('--info', action='store_true', help='Just show video info, no conversion')
    parser.add_argument('--force', action='store_true', help='Force conversion even if already CFR')

    args = parser.parse_args()

    if not args.video.exists():
        print(f"✗ File not found: {args.video}")
        sys.exit(1)

    if args.info:
        # Just show info
        print(f"Video Info: {args.video}")
        print("=" * 60)
        info = get_video_info(args.video)
        print(f"  FPS:        {info['fps']:.2f}")
        print(f"  CFR:        {info['is_cfr']}")
        print(f"  Frames:     {info['frame_count']:,}")
        print(f"  Duration:   {info['duration']:.2f}s")
        print(f"  Resolution: {info['width']}x{info['height']}")

        if info['is_cfr']:
            print(f"\n✓ Video is already constant frame rate")
        else:
            print(f"\n⚠️  Video has variable frame rate (VFR)")
            print(f"   Run without --info to convert to CFR")
    else:
        # Convert
        if args.force:
            output = convert_to_cfr(args.video, args.output, args.fps, args.crf)
        else:
            output = ensure_cfr(args.video, args.fps, args.crf)

        print(f"\n✓ Done: {output}")

if __name__ == "__main__":
    main()
