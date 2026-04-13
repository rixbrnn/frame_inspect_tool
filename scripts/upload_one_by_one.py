#!/usr/bin/env python3
"""
Upload trimmed videos one at a time to HuggingFace
"""
import sys
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_url
import time

DATASET_REPO = "rixbrnn/frame_inspect_tool_data"

def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_one_by_one.py <game_name>")
        print("Example: python upload_one_by_one.py cyberpunk")
        sys.exit(1)

    game = sys.argv[1]
    api = HfApi()

    # Get all trimmed videos
    trimmed_dir = Path("recordings") / game / "trimmed"
    if not trimmed_dir.exists():
        print(f"Error: {trimmed_dir} not found")
        sys.exit(1)

    videos = sorted(trimmed_dir.glob("*.mp4"))
    print(f"Found {len(videos)} videos to upload\n")

    uploaded = 0
    skipped = 0
    failed = 0

    for i, video in enumerate(videos, 1):
        size_mb = video.stat().st_size / (1024 * 1024)
        print(f"[{i}/{len(videos)}] {video.name} ({size_mb:.1f} MB)...", flush=True)

        try:
            path_in_repo = f"{game}/trimmed/{video.name}"
            result = api.upload_file(
                path_or_fileobj=str(video),
                path_in_repo=path_in_repo,
                repo_id=DATASET_REPO,
                repo_type="dataset",
                commit_message=f"Update trimmed video: {path_in_repo}"
            )

            if "No files have been modified" in str(result):
                print(f"  ⊘ Skipped (already uploaded)")
                skipped += 1
            else:
                print(f"  ✓ Uploaded")
                uploaded += 1

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed += 1

        # Small delay between uploads
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  ✓ Uploaded: {uploaded}")
    print(f"  ⊘ Skipped:  {skipped}")
    print(f"  ✗ Failed:   {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
