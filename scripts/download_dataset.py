#!/usr/bin/env python3
"""
Download benchmark recordings from Hugging Face dataset

This script downloads pre-recorded benchmark data for DLSS quality analysis.

Dataset: https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data

Usage:
    # Download all data
    python scripts/download_dataset.py

    # Download specific game
    python scripts/download_dataset.py --game cyberpunk2077

    # Download specific game and resolution
    python scripts/download_dataset.py --game cyberpunk2077 --resolution 1080p

    # List available data without downloading
    python scripts/download_dataset.py --list
"""

import argparse
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files
from tqdm import tqdm
import json


DATASET_REPO = "rixbrnn/frame_inspect_tool_data"


def list_available_data():
    """List all available recordings in the dataset"""
    print(f"Fetching file list from {DATASET_REPO}...")

    try:
        files = list_repo_files(DATASET_REPO, repo_type="dataset")
    except Exception as e:
        print(f"Error: Could not fetch dataset files: {e}")
        print(f"Make sure the dataset exists: https://huggingface.co/datasets/{DATASET_REPO}")
        return []

    # Organize by game and resolution
    structure = {}
    for file in files:
        if '/' in file:
            parts = file.split('/')
            if len(parts) >= 2:
                game = parts[0]
                resolution = parts[1] if len(parts) > 1 else None

                if game not in structure:
                    structure[game] = {}
                if resolution and resolution not in structure[game]:
                    structure[game][resolution] = []
                if len(parts) > 2:
                    structure[game][resolution].append('/'.join(parts[2:]))

    print("\nAvailable recordings:\n")
    print("=" * 80)

    for game in sorted(structure.keys()):
        print(f"\n📁 {game}/")
        for resolution in sorted(structure[game].keys()):
            file_count = len(structure[game][resolution])
            print(f"   └─ {resolution}/ ({file_count} files)")

            # Show sample files
            sample_files = [f for f in structure[game][resolution] if f.endswith('.mp4')][:3]
            for f in sample_files:
                print(f"      • {f}")
            if len(sample_files) < len([f for f in structure[game][resolution] if f.endswith('.mp4')]):
                remaining = len([f for f in structure[game][resolution] if f.endswith('.mp4')]) - len(sample_files)
                print(f"      • ... and {remaining} more files")

    print("\n" + "=" * 80)
    print(f"\nTotal games: {len(structure)}")
    print(f"Dataset URL: https://huggingface.co/datasets/{DATASET_REPO}\n")

    return structure


def download_file(repo_id, filename, local_dir):
    """Download a single file from HuggingFace"""
    try:
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset",
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        return downloaded_path
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return None


def download_dataset(game=None, resolution=None, output_dir=None):
    """Download dataset from Hugging Face"""

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "recordings"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading from: https://huggingface.co/datasets/{DATASET_REPO}")
    print(f"Output directory: {output_dir}\n")

    # Get list of files
    try:
        all_files = list_repo_files(DATASET_REPO, repo_type="dataset")
    except Exception as e:
        print(f"Error: Could not access dataset: {e}")
        print(f"Make sure the dataset exists and is public: https://huggingface.co/datasets/{DATASET_REPO}")
        return False

    # Filter files based on game and resolution
    files_to_download = []
    for file in all_files:
        # Skip if not relevant path
        if not '/' in file:
            continue

        parts = file.split('/')
        file_game = parts[0]
        file_resolution = parts[1] if len(parts) > 1 else None

        # Filter by game
        if game and file_game != game:
            continue

        # Filter by resolution
        if resolution and file_resolution != resolution:
            continue

        files_to_download.append(file)

    if not files_to_download:
        print("No files match your criteria.")
        if game:
            print(f"Game '{game}' not found in dataset.")
        if resolution:
            print(f"Resolution '{resolution}' not found.")
        print("\nRun with --list to see available data.")
        return False

    print(f"Found {len(files_to_download)} files to download\n")

    # Download files with progress bar
    downloaded = 0
    failed = 0

    for file in tqdm(files_to_download, desc="Downloading", unit="file"):
        result = download_file(DATASET_REPO, file, output_dir)
        if result:
            downloaded += 1
        else:
            failed += 1

    print(f"\n✓ Downloaded: {downloaded} files")
    if failed > 0:
        print(f"✗ Failed: {failed} files")

    print(f"\nFiles saved to: {output_dir}")

    # Check for metadata files and display info
    metadata_files = [f for f in files_to_download if f.endswith('metadata.json')]
    if metadata_files:
        print(f"\n📋 Found {len(metadata_files)} metadata files")
        print("Review metadata for recording details (system specs, game settings, etc.)")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Download DLSS benchmark recordings from Hugging Face',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available recordings
  python scripts/download_dataset.py --list

  # Download everything
  python scripts/download_dataset.py

  # Download specific game
  python scripts/download_dataset.py --game cyberpunk2077

  # Download specific game and resolution
  python scripts/download_dataset.py --game cyberpunk2077 --resolution 1080p

  # Download to custom directory
  python scripts/download_dataset.py --output /path/to/recordings

Dataset URL: https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data
        """
    )

    parser.add_argument('--list', action='store_true',
                       help='List available recordings without downloading')
    parser.add_argument('--game', type=str,
                       help='Download only specific game (e.g., cyberpunk2077)')
    parser.add_argument('--resolution', type=str,
                       help='Download only specific resolution (e.g., 1080p, 1440p, 4k)')
    parser.add_argument('--output', type=Path,
                       help='Output directory (default: ./recordings)')

    args = parser.parse_args()

    # List mode
    if args.list:
        list_available_data()
        return 0

    # Download mode
    print("=" * 80)
    print("DLSS Benchmark Dataset Downloader".center(80))
    print("=" * 80)
    print()

    success = download_dataset(
        game=args.game,
        resolution=args.resolution,
        output_dir=args.output
    )

    if success:
        print("\n" + "=" * 80)
        print("Download complete!".center(80))
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Review metadata.json files for recording details")
        print("  2. Run analysis pipeline on downloaded data")
        print("  3. See README.md for usage instructions")
        print()
        return 0
    else:
        print("\nDownload failed or incomplete.")
        return 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        exit(1)
