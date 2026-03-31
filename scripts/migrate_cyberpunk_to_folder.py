#!/usr/bin/env python3
"""
Migrate cyberpunk recordings from root to /cyberpunk folder in HuggingFace dataset
"""

from huggingface_hub import HfApi, login
from huggingface_hub.utils import RepositoryNotFoundError
import sys

DATASET_REPO = "rixbrnn/frame_inspect_tool_data"

def main():
    print("=" * 80)
    print("Migrate Cyberpunk Files to /cyberpunk Folder")
    print("=" * 80)
    print()

    # Login
    print("Logging in to HuggingFace...")
    print("Please enter your HuggingFace token (from https://huggingface.co/settings/tokens)")
    print("Or press Ctrl+C if you're already logged in")
    print()

    try:
        token = input("Token: ").strip()
        if token:
            login(token=token)
            print("✓ Logged in successfully\n")
    except KeyboardInterrupt:
        print("\nSkipping login (assuming already authenticated)\n")
    except Exception as e:
        print(f"Login error: {e}")
        print("Continuing anyway (you might already be logged in)\n")

    api = HfApi()

    # Get list of files
    print(f"Fetching file list from {DATASET_REPO}...")
    try:
        files = api.list_repo_files(repo_id=DATASET_REPO, repo_type="dataset")
    except Exception as e:
        print(f"Error: Could not access dataset: {e}")
        return 1

    # Filter files that need to be moved (root level files for cyberpunk)
    files_to_move = []
    for file in files:
        # Skip files already in subdirectories
        if '/' in file:
            continue

        # Skip README and .gitattributes
        if file in ['README.md', '.gitattributes']:
            continue

        # Include video files, txt files, json files, png files
        if any(file.endswith(ext) for ext in ['.mp4', '.txt', '.json', '.png']):
            files_to_move.append(file)

    if not files_to_move:
        print("No files found to move!")
        return 0

    print(f"\nFound {len(files_to_move)} files to move to /cyberpunk:")
    for f in files_to_move[:10]:
        print(f"  • {f}")
    if len(files_to_move) > 10:
        print(f"  • ... and {len(files_to_move) - 10} more")

    print("\nThis will:")
    print("  1. Move all files into cyberpunk/ folder")
    print("  2. Keep the same filenames")
    print()

    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        return 0

    print("\nMoving files...")
    moved = 0
    failed = 0

    for file in files_to_move:
        new_path = f"cyberpunk/{file}"
        try:
            print(f"Moving {file} → {new_path}")

            # Move file by copying to new location and deleting old
            api.upload_file(
                path_or_fileobj=api.hf_hub_download(
                    repo_id=DATASET_REPO,
                    repo_type="dataset",
                    filename=file
                ),
                path_in_repo=new_path,
                repo_id=DATASET_REPO,
                repo_type="dataset",
            )

            # Delete old file
            api.delete_file(
                path_in_repo=file,
                repo_id=DATASET_REPO,
                repo_type="dataset",
                commit_message=f"Move {file} to cyberpunk folder"
            )

            moved += 1
            print(f"  ✓ Moved")

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"✓ Moved: {moved} files")
    if failed > 0:
        print(f"✗ Failed: {failed} files")
    print("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
