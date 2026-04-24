#!/usr/bin/env python3
"""
Batch trim all videos in a folder sequentially using ROI config.

Usage:
    python scripts/batch_trim.py \
        --input-dir recordings/forza_extreme \
        --roi-config recordings/forza_extreme/roi_trim_coordinates.yaml

    # Custom output directory
    python scripts/batch_trim.py \
        --input-dir recordings/forza_extreme \
        --roi-config recordings/forza_extreme/roi_trim_coordinates.yaml \
        --output-dir recordings/forza_extreme/trimmed_output
"""

import argparse
import sys
import subprocess
from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}


def find_videos(input_dir: Path) -> list:
    """Find all video files in directory (non-recursive)."""
    videos = []
    for file in input_dir.iterdir():
        if file.is_file() and file.suffix.lower() in VIDEO_EXTENSIONS:
            videos.append(file)
    return sorted(videos)


def trim_video(video_path: Path, roi_config: str, output_path: Path) -> bool:
    """
    Trim a single video using the trim_by_marker script.

    Returns:
        True if successful, False otherwise
    """
    cmd = [
        'python3',
        'src/trim/trim_by_marker.py',
        '--video', str(video_path),
        '--roi-config', roi_config,
        '--output', str(output_path)
    ]

    print(f"\n{'='*80}")
    print(f"Trimming: {video_path.name}")
    print(f"{'='*80}")

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"✓ Success: {output_path.name}")
        return True
    else:
        print(f"✗ Failed: {video_path.name}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Batch trim all videos in a folder sequentially',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Trim all videos in forza_extreme folder
  python scripts/batch_trim.py \\
      --input-dir recordings/forza_extreme \\
      --roi-config recordings/forza_extreme/roi_trim_coordinates.yaml

  # Custom output directory
  python scripts/batch_trim.py \\
      --input-dir recordings/cyberpunk \\
      --roi-config recordings/cyberpunk/roi_trim_coordinates.yaml \\
      --output-dir recordings/cyberpunk/output
        """
    )
    parser.add_argument('--input-dir', required=True,
                       help='Directory containing videos to trim')
    parser.add_argument('--roi-config', required=True,
                       help='Path to ROI config YAML file')
    parser.add_argument('--output-dir', default=None,
                       help='Output directory (default: <input-dir>/trimmed)')

    args = parser.parse_args()

    input_dir = Path(args.input_dir)

    # Default output directory is <input-dir>/trimmed
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = input_dir / 'trimmed'

    # Validate input directory
    if not input_dir.exists():
        print(f"✗ Error: Input directory not found: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"✗ Error: Input path is not a directory: {input_dir}")
        sys.exit(1)

    # Find all videos
    videos = find_videos(input_dir)

    if not videos:
        print(f"✗ Error: No video files found in {input_dir}")
        print(f"Supported extensions: {', '.join(VIDEO_EXTENSIONS)}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Batch Trimming Videos")
    print(f"{'='*80}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"ROI config: {args.roi_config}")
    print(f"Total videos: {len(videos)}")
    print()

    successful = []
    failed = []

    for idx, video_path in enumerate(videos, 1):
        output_path = output_dir / video_path.name

        print(f"\n[{idx}/{len(videos)}] Processing: {video_path.name}")

        # Trim video
        success = trim_video(video_path, args.roi_config, output_path)

        if success:
            successful.append(video_path.name)
        else:
            failed.append(video_path.name)

    # Print summary
    print(f"\n{'='*80}")
    print(f"Batch Trimming Complete")
    print(f"{'='*80}")
    print(f"Successful: {len(successful)}/{len(videos)}")
    print(f"Failed: {len(failed)}/{len(videos)}")

    if failed:
        print(f"\nFailed videos:")
        for video in failed:
            print(f"  - {video}")
        sys.exit(1)
    else:
        print(f"\n✓ All videos trimmed successfully!")


if __name__ == '__main__':
    main()
