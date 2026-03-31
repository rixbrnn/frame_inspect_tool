#!/usr/bin/env python3
"""
ICAT Video Trimmer

Reads ICAT manual alignment JSON and trims videos to aligned ranges.
Saves trimmed videos to a new 'aligned/' folder without modifying originals.

Usage:
    # Trim videos from ICAT alignment
    python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json

    # Dry run (show commands without executing)
    python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json --dry-run
"""

import argparse
import subprocess
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.sync.icat_parser import parse_icat_alignment


def trim_videos_from_icat(
    icat_json_path: str,
    video_dir: str = None,
    output_dir: str = None,
    dry_run: bool = False
):
    """
    Trim videos based on ICAT alignment data.

    Args:
        icat_json_path: Path to ICAT JSON file
        video_dir: Directory containing source videos (default: same as JSON)
        output_dir: Output directory for trimmed videos (default: video_dir/aligned/)
        dry_run: If True, show commands without executing
    """
    icat_path = Path(icat_json_path)

    if not icat_path.exists():
        print(f"❌ Error: ICAT JSON not found: {icat_path}")
        return False

    # Parse ICAT alignment
    print("📊 Parsing ICAT alignment...")
    try:
        alignment = parse_icat_alignment(icat_json_path)
    except Exception as e:
        print(f"❌ Error parsing ICAT JSON: {e}")
        return False

    print(f"✓ Found alignment for {len(alignment.videos)} videos")
    print(f"  Aligned range: {alignment.start_time:.3f}s to {alignment.end_time:.3f}s ({alignment.aligned_duration:.3f}s)")
    print()

    # Determine directories
    if video_dir is None:
        video_dir = icat_path.parent
    else:
        video_dir = Path(video_dir)

    if output_dir is None:
        output_dir = video_dir / "aligned"
    else:
        output_dir = Path(output_dir)

    # Create output directory
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")
        print()

    # Process each video
    success_count = 0
    failed_count = 0

    for i, video in enumerate(alignment.videos, 1):
        video_name = video.video_name
        if not video_name:
            print(f"⚠️  Skipping video {i}: No filename in ICAT data")
            continue

        # Find source video file
        source_path = video_dir / video_name
        if not source_path.exists():
            print(f"⚠️  Skipping {video_name}: File not found at {source_path}")
            failed_count += 1
            continue

        # Determine output path
        output_path = output_dir / video_name

        # Build ffmpeg command
        # Use select filter for frame-precise cuts
        cmd = [
            'ffmpeg',
            '-i', str(source_path),
            '-vf', f"select='between(n\\,{video.start_frame}\\,{video.end_frame})',setpts=PTS-STARTPTS",
            '-af', f"aselect='between(n\\,{video.start_frame}\\,{video.end_frame})',asetpts=PTS-STARTPTS",
            '-vsync', '0',
            '-y',  # Overwrite output
            str(output_path)
        ]

        print(f"[{i}/{len(alignment.videos)}] {video_name}")
        print(f"    Source: {source_path}")
        print(f"    Output: {output_path}")
        print(f"    Trim:   frames {video.start_frame}-{video.end_frame} ({video.aligned_frames} frames, {video.aligned_duration:.2f}s)")

        if dry_run:
            print(f"    Command: {' '.join(cmd)}")
            print()
            continue

        # Execute ffmpeg
        try:
            print("    ⏳ Trimming...")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode == 0:
                print(f"    ✓ Trimmed successfully")
                success_count += 1
            else:
                print(f"    ❌ ffmpeg failed:")
                # Show last few lines of error
                error_lines = result.stderr.strip().split('\n')
                for line in error_lines[-5:]:
                    print(f"       {line}")
                failed_count += 1

        except Exception as e:
            print(f"    ❌ Error running ffmpeg: {e}")
            failed_count += 1

        print()

    # Summary
    print("=" * 80)
    if dry_run:
        print("DRY RUN COMPLETE".center(80))
        print(f"\nWould process {len(alignment.videos)} videos")
        print(f"Output directory: {output_dir}")
    else:
        print("TRIMMING COMPLETE".center(80))
        print(f"\n✓ Success: {success_count} videos")
        if failed_count > 0:
            print(f"❌ Failed: {failed_count} videos")
        print(f"\nTrimmed videos saved to: {output_dir}")

    return failed_count == 0


def main():
    parser = argparse.ArgumentParser(
        description='Trim videos using ICAT manual alignment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Trim videos from ICAT alignment
  python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json

  # Specify video directory
  python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_derived_modes_cut_settings.json --video-dir recordings/cyberpunk

  # Custom output directory
  python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json --output-dir my_aligned_videos

  # Dry run (show what would be done)
  python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json --dry-run

Output Structure:
  recordings/cyberpunk/
  ├── 1080p_dlaa_run1.mp4          # Original (unchanged)
  ├── 1080p_dlaa_run2.mp4          # Original (unchanged)
  └── aligned/                      # New trimmed videos
      ├── 1080p_dlaa_run1.mp4
      └── 1080p_dlaa_run2.mp4
        """
    )

    parser.add_argument('icat_json', help='Path to ICAT JSON file')
    parser.add_argument('--video-dir', help='Directory containing source videos (default: same as JSON)')
    parser.add_argument('--output-dir', help='Output directory for trimmed videos (default: video_dir/aligned/)')
    parser.add_argument('--dry-run', action='store_true', help='Show commands without executing')

    args = parser.parse_args()

    print("=" * 80)
    print("ICAT VIDEO TRIMMER".center(80))
    print("=" * 80)
    print()

    success = trim_videos_from_icat(
        icat_json_path=args.icat_json,
        video_dir=args.video_dir,
        output_dir=args.output_dir,
        dry_run=args.dry_run
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
