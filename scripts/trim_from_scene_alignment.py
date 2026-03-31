#!/usr/bin/env python3
"""
Trim videos using scene transition-based alignment

Similar to trim_from_icat.py but uses scene transition alignment JSON.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path


def trim_videos_from_scene_alignment(
    alignment_json_path: str,
    video_dir: str = None,
    output_dir: str = None,
    dry_run: bool = False
):
    """
    Trim videos based on scene transition alignment data.

    Args:
        alignment_json_path: Path to scene alignment JSON file
        video_dir: Directory containing source videos (default: same as JSON)
        output_dir: Output directory for trimmed videos (default: video_dir/aligned_scene/)
        dry_run: If True, show commands without executing
    """
    alignment_path = Path(alignment_json_path)

    if not alignment_path.exists():
        print(f"❌ Error: Alignment JSON not found: {alignment_path}")
        return False

    # Load alignment
    print("📊 Loading scene transition alignment...")
    try:
        with open(alignment_json_path) as f:
            alignment = json.load(f)
    except Exception as e:
        print(f"❌ Error loading alignment JSON: {e}")
        return False

    print(f"✓ Loaded alignment")
    print(f"  Method: {alignment.get('method', 'unknown')}")
    print(f"  Video 1: frames {alignment['video1']['start_frame']}-{alignment['video1']['end_frame']} ({alignment['video1']['aligned_frames']} frames)")
    print(f"  Video 2: frames {alignment['video2']['start_frame']}-{alignment['video2']['end_frame']} ({alignment['video2']['aligned_frames']} frames)")
    print()

    # Determine directories
    if video_dir is None:
        video_dir = alignment_path.parent
    else:
        video_dir = Path(video_dir)

    if output_dir is None:
        output_dir = video_dir / "aligned_scene"
    else:
        output_dir = Path(output_dir)

    # Create output directory
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")
        print()

    # Process both videos
    success_count = 0
    failed_count = 0

    for video_key in ['video1', 'video2']:
        video_info = alignment[video_key]
        video_name = video_info['name']
        start_frame = video_info['start_frame']
        end_frame = video_info['end_frame']

        # Find source video file
        source_path = video_dir / video_name
        if not source_path.exists():
            print(f"⚠️  Skipping {video_name}: File not found at {source_path}")
            failed_count += 1
            continue

        # Determine output path
        output_path = output_dir / video_name

        # Build ffmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(source_path),
            '-vf', f"select='between(n\\,{start_frame}\\,{end_frame})',setpts=PTS-STARTPTS",
            '-af', f"aselect='between(n\\,{start_frame}\\,{end_frame})',asetpts=PTS-STARTPTS",
            '-vsync', '0',
            '-y',  # Overwrite output
            str(output_path)
        ]

        print(f"[{video_key}] {video_name}")
        print(f"    Source: {source_path}")
        print(f"    Output: {output_path}")
        print(f"    Trim:   frames {start_frame}-{end_frame} ({end_frame - start_frame + 1} frames)")

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
        print(f"\nWould process 2 videos")
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
        description='Trim videos using scene transition alignment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Trim videos from scene alignment
  python scripts/trim_from_scene_alignment.py recordings/cyberpunk/scene_transition_alignment.json

  # Dry run (show what would be done)
  python scripts/trim_from_scene_alignment.py recordings/cyberpunk/scene_transition_alignment.json --dry-run

  # Custom output directory
  python scripts/trim_from_scene_alignment.py recordings/cyberpunk/scene_transition_alignment.json --output-dir my_aligned_videos

Output Structure:
  recordings/cyberpunk/
  ├── 1080p_dlaa_run1.mp4          # Original (unchanged)
  ├── 1080p_dlaa_run2.mp4          # Original (unchanged)
  ├── aligned/                      # ICAT-based trimmed videos
  │   ├── 1080p_dlaa_run1.mp4
  │   └── 1080p_dlaa_run2.mp4
  └── aligned_scene/                # Scene-based trimmed videos (NEW)
      ├── 1080p_dlaa_run1.mp4
      └── 1080p_dlaa_run2.mp4
        """
    )

    parser.add_argument('alignment_json', help='Path to scene alignment JSON file')
    parser.add_argument('--video-dir', help='Directory containing source videos (default: same as JSON)')
    parser.add_argument('--output-dir', help='Output directory for trimmed videos (default: video_dir/aligned_scene/)')
    parser.add_argument('--dry-run', action='store_true', help='Show commands without executing')

    args = parser.parse_args()

    print("=" * 80)
    print("SCENE ALIGNMENT VIDEO TRIMMER".center(80))
    print("=" * 80)
    print()

    success = trim_videos_from_scene_alignment(
        alignment_json_path=args.alignment_json,
        video_dir=args.video_dir,
        output_dir=args.output_dir,
        dry_run=args.dry_run
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
