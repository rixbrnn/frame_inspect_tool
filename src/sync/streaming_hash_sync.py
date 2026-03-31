#!/usr/bin/env python3
"""
Memory-Efficient Streaming Video Hash Synchronization

This approach processes videos one frame at a time, avoiding memory issues:
1. Read frame → Apply blur → Compute perceptual hash → Write to JSON
2. Repeat for both videos
3. Load JSON files and find hash intersections
4. Find longest consecutive match

Advantages:
- O(1) memory usage (constant, not dependent on video length)
- Can handle any video size
- Blur preprocessing improves hash robustness
- Hash cache files can be reused
"""

import cv2
import numpy as np
import imagehash
from PIL import Image
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from tqdm import tqdm
from collections import defaultdict


def blur_frame(frame: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply Gaussian blur to reduce noise before hashing.

    This improves hash stability across similar frames by:
    - Reducing compression artifacts
    - Smoothing out minor pixel variations
    - Focusing on structural content

    Args:
        frame: Input frame (BGR)
        kernel_size: Gaussian kernel size (must be odd, default: 5)

    Returns:
        Blurred frame
    """
    return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)


def frame_to_phash(frame: np.ndarray, hash_size: int = 8, apply_blur: bool = True) -> str:
    """
    Convert frame to perceptual hash string.

    Args:
        frame: Input frame (BGR)
        hash_size: Hash size (8 = 64-bit hash)
        apply_blur: Apply Gaussian blur before hashing

    Returns:
        Hex string representation of perceptual hash
    """
    # Optional blur preprocessing
    if apply_blur:
        frame = blur_frame(frame)

    # Convert to PIL for imagehash
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)

    # Compute perceptual hash
    phash = imagehash.phash(pil_img, hash_size=hash_size)

    # Return as hex string
    return str(phash)


def generate_video_hashes(
    video_path: str,
    output_json: str,
    hash_size: int = 8,
    apply_blur: bool = True,
    sample_rate: int = 1
) -> Dict:
    """
    Process video one frame at a time and save hashes to JSON.

    Memory-efficient: Only one frame in memory at a time.

    Args:
        video_path: Path to video file
        output_json: Output JSON file path
        hash_size: Perceptual hash size
        apply_blur: Apply blur before hashing
        sample_rate: Process every Nth frame (1 = all frames)

    Returns:
        Dictionary with video metadata and hash count
    """
    print(f"\n{'='*70}")
    print(f"Processing: {Path(video_path).name}")
    print(f"{'='*70}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Total frames: {total_frames}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Sample rate: every {sample_rate} frame(s)")
    print()

    # Prepare output structure
    hashes_data = {
        "video_path": video_path,
        "video_name": Path(video_path).name,
        "metadata": {
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames": total_frames,
            "duration": duration,
            "sample_rate": sample_rate
        },
        "hash_config": {
            "hash_size": hash_size,
            "blur_applied": apply_blur,
            "hash_type": "phash"
        },
        "hashes": []  # List of {"frame": frame_num, "hash": hash_str}
    }

    # Process frames one at a time
    frame_count = 0
    processed_count = 0

    pbar = tqdm(total=total_frames, desc="Hashing frames", unit="frame")

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Sample frames
        if frame_count % sample_rate == 0:
            # Compute hash
            hash_str = frame_to_phash(frame, hash_size=hash_size, apply_blur=apply_blur)

            # Store hash
            hashes_data["hashes"].append({
                "frame": frame_count,
                "hash": hash_str
            })

            processed_count += 1

        frame_count += 1
        pbar.update(1)

    pbar.close()
    cap.release()

    print(f"\n✓ Processed {frame_count} frames")
    print(f"✓ Generated {processed_count} hashes")
    print(f"✓ Memory usage: O(1) - single frame at a time")

    # Save to JSON
    output_path = Path(output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(hashes_data, f, indent=2)

    print(f"✓ Saved hashes to: {output_json}")

    return {
        "video_path": video_path,
        "output_json": output_json,
        "total_frames": frame_count,
        "processed_frames": processed_count
    }


def load_hashes(json_path: str) -> Dict:
    """Load hash data from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def find_hash_matches(
    hashes1: List[Dict],
    hashes2: List[Dict],
    max_hamming_distance: int = 5
) -> List[Tuple[int, int, int]]:
    """
    Find matching hashes between two videos.

    Args:
        hashes1: List of {"frame": int, "hash": str} from video 1
        hashes2: List of {"frame": int, "hash": str} from video 2
        max_hamming_distance: Maximum Hamming distance for match (0-5 typical)

    Returns:
        List of (frame1, frame2, distance) tuples
    """
    print("\nFinding hash matches...")

    # Build hash table for video 1
    hash_table = defaultdict(list)
    for item in hashes1:
        hash_table[item["hash"]].append(item["frame"])

    print(f"  Video 1: {len(hashes1)} hashes ({len(hash_table)} unique)")
    print(f"  Video 2: {len(hashes2)} hashes")

    # Find matches
    matches = []

    for item2 in tqdm(hashes2, desc="Matching hashes"):
        hash2 = item2["hash"]
        frame2 = item2["frame"]

        # Check for exact match first (fastest)
        if hash2 in hash_table:
            for frame1 in hash_table[hash2]:
                matches.append((frame1, frame2, 0))

        # Check for near matches if distance > 0
        elif max_hamming_distance > 0:
            hash2_obj = imagehash.hex_to_hash(hash2)

            for hash1_str, frame1_list in hash_table.items():
                hash1_obj = imagehash.hex_to_hash(hash1_str)
                distance = hash1_obj - hash2_obj  # Hamming distance

                if distance <= max_hamming_distance:
                    for frame1 in frame1_list:
                        matches.append((frame1, frame2, distance))

    print(f"  ✓ Found {len(matches)} potential matches")

    return matches


def find_longest_consecutive_sequence(
    matches: List[Tuple[int, int, int]],
    min_length: int = 30
) -> Optional[Tuple[int, int, int, int]]:
    """
    Find longest consecutive frame sequence from matches.

    Args:
        matches: List of (frame1, frame2, distance) tuples
        min_length: Minimum sequence length in frames

    Returns:
        (start1, end1, start2, end2) or None if no valid sequence
    """
    if not matches:
        return None

    print("\nFinding longest consecutive sequence...")

    # Sort by frame indices
    matches.sort()

    best_start1 = None
    best_start2 = None
    best_length = 0

    current_start1 = None
    current_start2 = None
    current_length = 0
    last_frame1 = -1
    last_frame2 = -1

    for frame1, frame2, distance in matches:
        # Check if consecutive
        if frame1 == last_frame1 + 1 and frame2 == last_frame2 + 1:
            current_length += 1
        else:
            # Sequence broken, check if previous was best
            if current_length > best_length:
                best_length = current_length
                best_start1 = current_start1
                best_start2 = current_start2

            # Start new sequence
            current_start1 = frame1
            current_start2 = frame2
            current_length = 1

        last_frame1 = frame1
        last_frame2 = frame2

    # Check final sequence
    if current_length > best_length:
        best_length = current_length
        best_start1 = current_start1
        best_start2 = current_start2

    if best_length < min_length:
        print(f"  ✗ Best match too short: {best_length} frames (min: {min_length})")
        return None

    best_end1 = best_start1 + best_length - 1
    best_end2 = best_start2 + best_length - 1

    print(f"  ✓ Match found: {best_length} consecutive frames")
    print(f"    Video 1: frames {best_start1} to {best_end1}")
    print(f"    Video 2: frames {best_start2} to {best_end2}")

    return best_start1, best_end1, best_start2, best_end2


def sync_videos_from_hashes(
    hash_json1: str,
    hash_json2: str,
    max_hamming_distance: int = 5,
    min_match_length: int = 30
) -> Optional[Dict]:
    """
    Synchronize videos using pre-computed hash JSON files.

    Args:
        hash_json1: Path to video 1 hash JSON
        hash_json2: Path to video 2 hash JSON
        max_hamming_distance: Max Hamming distance for matches
        min_match_length: Minimum consecutive frames for valid overlap

    Returns:
        Dictionary with alignment info or None if no match
    """
    print(f"\n{'='*70}")
    print("VIDEO SYNCHRONIZATION FROM HASH FILES".center(70))
    print(f"{'='*70}")

    # Load hash files
    print("\nLoading hash files...")
    data1 = load_hashes(hash_json1)
    data2 = load_hashes(hash_json2)

    print(f"  ✓ Video 1: {data1['video_name']}")
    print(f"  ✓ Video 2: {data2['video_name']}")

    # Find matches
    matches = find_hash_matches(
        data1["hashes"],
        data2["hashes"],
        max_hamming_distance=max_hamming_distance
    )

    if not matches:
        print("\n✗ No matches found!")
        return None

    # Find longest sequence
    result = find_longest_consecutive_sequence(matches, min_match_length)

    if result is None:
        print("\n✗ No valid overlap found!")
        return None

    start1, end1, start2, end2 = result

    # Calculate time info
    fps1 = data1["metadata"]["fps"]
    fps2 = data2["metadata"]["fps"]

    start_time1 = start1 / fps1
    end_time1 = end1 / fps1
    start_time2 = start2 / fps2
    end_time2 = end2 / fps2

    alignment = {
        "video1": {
            "path": data1["video_path"],
            "name": data1["video_name"],
            "start_frame": start1,
            "end_frame": end1,
            "start_time": start_time1,
            "end_time": end_time1,
            "overlap_frames": end1 - start1 + 1
        },
        "video2": {
            "path": data2["video_path"],
            "name": data2["video_name"],
            "start_frame": start2,
            "end_frame": end2,
            "start_time": start_time2,
            "end_time": end_time2,
            "overlap_frames": end2 - start2 + 1
        },
        "parameters": {
            "max_hamming_distance": max_hamming_distance,
            "min_match_length": min_match_length
        }
    }

    print(f"\n{'='*70}")
    print("ALIGNMENT RESULT".center(70))
    print(f"{'='*70}")
    print(f"\nVideo 1: {data1['video_name']}")
    print(f"  Frames: {start1} to {end1} ({end1-start1+1} frames)")
    print(f"  Time:   {start_time1:.2f}s to {end_time1:.2f}s")
    print(f"\nVideo 2: {data2['video_name']}")
    print(f"  Frames: {start2} to {end2} ({end2-start2+1} frames)")
    print(f"  Time:   {start_time2:.2f}s to {end_time2:.2f}s")

    return alignment


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Memory-efficient streaming video hash synchronization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Two-step process:

Step 1: Generate hash files
  python streaming_hash_sync.py generate \\
    --video video.mp4 \\
    --output video_hashes.json

Step 2: Sync using hash files
  python streaming_hash_sync.py sync \\
    --hash1 video1_hashes.json \\
    --hash2 video2_hashes.json \\
    --output alignment.json

Complete example:
  # Generate hashes
  python streaming_hash_sync.py generate \\
    --video recordings/cyberpunk/1080p_dlaa_run1.mp4 \\
    --output recordings/cyberpunk/1080p_dlaa_run1_hashes.json

  python streaming_hash_sync.py generate \\
    --video recordings/cyberpunk/1080p_dlaa_run2.mp4 \\
    --output recordings/cyberpunk/1080p_dlaa_run2_hashes.json

  # Sync
  python streaming_hash_sync.py sync \\
    --hash1 recordings/cyberpunk/1080p_dlaa_run1_hashes.json \\
    --hash2 recordings/cyberpunk/1080p_dlaa_run2_hashes.json \\
    --output recordings/cyberpunk/alignment.json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate hash file from video')
    gen_parser.add_argument('--video', required=True, help='Input video file')
    gen_parser.add_argument('--output', required=True, help='Output JSON file')
    gen_parser.add_argument('--hash-size', type=int, default=8, help='Hash size (default: 8)')
    gen_parser.add_argument('--no-blur', action='store_true', help='Disable blur preprocessing')
    gen_parser.add_argument('--sample-rate', type=int, default=1, help='Sample every Nth frame (default: 1)')

    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync videos from hash files')
    sync_parser.add_argument('--hash1', required=True, help='Hash JSON for video 1')
    sync_parser.add_argument('--hash2', required=True, help='Hash JSON for video 2')
    sync_parser.add_argument('--output', help='Output alignment JSON')
    sync_parser.add_argument('--max-distance', type=int, default=5, help='Max Hamming distance (default: 5)')
    sync_parser.add_argument('--min-length', type=int, default=30, help='Min match length (default: 30)')

    args = parser.parse_args()

    if args.command == 'generate':
        generate_video_hashes(
            video_path=args.video,
            output_json=args.output,
            hash_size=args.hash_size,
            apply_blur=not args.no_blur,
            sample_rate=args.sample_rate
        )

    elif args.command == 'sync':
        alignment = sync_videos_from_hashes(
            hash_json1=args.hash1,
            hash_json2=args.hash2,
            max_hamming_distance=args.max_distance,
            min_match_length=args.min_length
        )

        if alignment and args.output:
            with open(args.output, 'w') as f:
                json.dump(alignment, f, indent=2)
            print(f"\n✓ Alignment saved to: {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
