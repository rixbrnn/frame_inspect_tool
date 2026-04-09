#!/usr/bin/env python3
"""
Upload trimmed benchmark videos to Hugging Face dataset

This script uploads trimmed video files to the HuggingFace dataset repository.

Dataset: https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data

Usage:
    # Upload all trimmed videos for a specific game
    python scripts/upload_trimmed_videos.py --game cyberpunk

    # Dry run (show what would be uploaded without actually uploading)
    python scripts/upload_trimmed_videos.py --game cyberpunk --dry-run
"""

import argparse
import sys
from pathlib import Path
from huggingface_hub import HfApi, login
from tqdm import tqdm


DATASET_REPO = "rixbrnn/frame_inspect_tool_data"


def find_trimmed_videos(recordings_dir, game):
    """Find all trimmed video files for a specific game"""
    game_dir = Path(recordings_dir) / game / "trimmed"

    if not game_dir.exists():
        print(f"Error: Trimmed videos directory not found: {game_dir}")
        return []

    # Find all .mp4 files in the trimmed directory
    video_files = list(game_dir.glob("*.mp4"))

    if not video_files:
        print(f"Error: No trimmed videos found in {game_dir}")
        return []

    return sorted(video_files)


def upload_videos(game, recordings_dir=None, dry_run=False, yes=False):
    """Upload trimmed videos to HuggingFace"""

    if recordings_dir is None:
        recordings_dir = Path(__file__).parent.parent / "recordings"
    else:
        recordings_dir = Path(recordings_dir)

    if not recordings_dir.exists():
        print(f"Error: Recordings directory not found: {recordings_dir}")
        return False

    # Find all trimmed videos
    video_files = find_trimmed_videos(recordings_dir, game)

    if not video_files:
        return False

    print(f"Found {len(video_files)} trimmed videos to upload:\n")

    total_size = 0
    for video in video_files:
        size_mb = video.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  • {video.name} ({size_mb:.1f} MB)")

    print(f"\nTotal size: {total_size:.1f} MB ({total_size/1024:.2f} GB)")
    print(f"Destination: {DATASET_REPO}/{game}/trimmed/")

    if dry_run:
        print("\n[DRY RUN] No files will be uploaded.")
        return True

    # Confirm upload
    if not yes:
        print("\n" + "=" * 80)
        response = input("Continue with upload? (y/N): ")
        if response.lower() != 'y':
            print("Upload cancelled.")
            return False
    else:
        print("\n[AUTO-CONFIRMED] Proceeding with upload...")

    print("\nAuthenticating with HuggingFace...")
    try:
        api = HfApi()
        # This will use the token from huggingface-cli login or HF_TOKEN env var
    except Exception as e:
        print(f"Error: Authentication failed: {e}")
        print("\nPlease login with: huggingface-cli login")
        print("Or set HF_TOKEN environment variable")
        return False

    print(f"\nUploading to dataset: {DATASET_REPO}")
    print("=" * 80)

    uploaded = 0
    failed = 0

    for video_file in tqdm(video_files, desc="Uploading", unit="file"):
        try:
            # Upload to {game}/trimmed/{filename}
            path_in_repo = f"{game}/trimmed/{video_file.name}"

            api.upload_file(
                path_or_fileobj=str(video_file),
                path_in_repo=path_in_repo,
                repo_id=DATASET_REPO,
                repo_type="dataset",
                commit_message=f"Add trimmed video: {path_in_repo}"
            )
            uploaded += 1

        except Exception as e:
            print(f"\nError uploading {video_file.name}: {e}")
            failed += 1

    print(f"\n✓ Uploaded: {uploaded} files")
    if failed > 0:
        print(f"✗ Failed: {failed} files")

    print(f"\nVideos uploaded to: https://huggingface.co/datasets/{DATASET_REPO}/tree/main/{game}/trimmed")

    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='Upload trimmed benchmark videos to Hugging Face dataset',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload trimmed Cyberpunk videos
  python scripts/upload_trimmed_videos.py --game cyberpunk

  # Dry run to see what would be uploaded
  python scripts/upload_trimmed_videos.py --game cyberpunk --dry-run

  # Upload from custom directory
  python scripts/upload_trimmed_videos.py --game cyberpunk --recordings /path/to/recordings

Dataset URL: https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data

Note: You must be authenticated with HuggingFace to upload.
Run: huggingface-cli login
        """
    )

    parser.add_argument('--game', type=str, required=True,
                       help='Game name (e.g., cyberpunk, blackmyth)')
    parser.add_argument('--recordings', type=Path,
                       help='Recordings directory (default: ./recordings)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be uploaded without actually uploading')
    parser.add_argument('-y', '--yes', action='store_true',
                       help='Skip confirmation prompt and proceed with upload')

    args = parser.parse_args()

    print("=" * 80)
    print("Trimmed Video Uploader for DLSS Benchmark Dataset".center(80))
    print("=" * 80)
    print()

    success = upload_videos(
        game=args.game,
        recordings_dir=args.recordings,
        dry_run=args.dry_run,
        yes=args.yes
    )

    if success:
        print("\n" + "=" * 80)
        print("Upload complete!".center(80))
        print("=" * 80)
        return 0
    else:
        print("\nUpload failed or incomplete.")
        return 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nUpload cancelled by user.")
        exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
