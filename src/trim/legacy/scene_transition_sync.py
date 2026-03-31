#!/usr/bin/env python3
"""
Scene Transition-Based Video Synchronization

Uses scene cuts/transitions as anchor points for alignment.
Scene transitions happen at the same timestamps regardless of camera angle.

Algorithm:
1. Detect scene transitions in both videos (using frame difference)
2. Match transition timestamps between videos
3. Find longest sequence of matching transitions
4. Use transitions to determine aligned regions

Advantages:
- Works with different camera angles (transitions are consistent)
- Robust to gameplay differences
- Fast detection (just frame differencing)
- Scene cuts happen at same times in both recordings
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from tqdm import tqdm
import json


def detect_scene_transitions(
    video_path: str,
    threshold: float = 30.0,
    min_scene_length: int = 30
) -> List[int]:
    """
    Detect scene transitions (cuts) in video.

    Uses frame difference histogram comparison to find sudden changes.

    Args:
        video_path: Path to video file
        threshold: Difference threshold for scene cut (0-100, higher = more strict)
        min_scene_length: Minimum frames between transitions (avoid false positives)

    Returns:
        List of frame numbers where scene transitions occur
    """
    print(f"\n{'='*70}")
    print(f"Detecting scene transitions: {Path(video_path).name}")
    print(f"{'='*70}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    print(f"  FPS: {fps:.2f}")
    print(f"  Total frames: {total_frames}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Threshold: {threshold}")
    print()

    transitions = []
    prev_hist = None
    frames_since_last_transition = min_scene_length + 1

    pbar = tqdm(total=total_frames, desc="Scanning frames", unit="frame")

    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale for histogram
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Compute histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        # Compare with previous frame
        if prev_hist is not None and frames_since_last_transition >= min_scene_length:
            # Chi-square distance between histograms
            diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CHISQR)

            if diff > threshold:
                transitions.append(frame_num)
                frames_since_last_transition = 0

        prev_hist = hist
        frames_since_last_transition += 1
        frame_num += 1
        pbar.update(1)

    pbar.close()
    cap.release()

    print(f"\n✓ Found {len(transitions)} scene transitions")

    if transitions:
        print(f"  First transition at frame {transitions[0]} ({transitions[0]/fps:.2f}s)")
        print(f"  Last transition at frame {transitions[-1]} ({transitions[-1]/fps:.2f}s)")

    return transitions


def match_transitions(
    transitions1: List[int],
    transitions2: List[int],
    fps1: float,
    fps2: float,
    max_time_diff: float = 0.5
) -> List[Tuple[int, int]]:
    """
    Match scene transitions between two videos based on timestamps.

    Args:
        transitions1: Frame numbers of transitions in video 1
        transitions2: Frame numbers of transitions in video 2
        fps1: FPS of video 1
        fps2: FPS of video 2
        max_time_diff: Maximum time difference to consider a match (seconds)

    Returns:
        List of (frame1, frame2) matched transition pairs
    """
    print("\nMatching scene transitions...")

    # Convert frame numbers to timestamps
    times1 = [f / fps1 for f in transitions1]
    times2 = [f / fps2 for f in transitions2]

    matches = []

    # For each transition in video 1, find closest in video 2
    for i, t1 in enumerate(times1):
        best_match = None
        best_diff = float('inf')

        for j, t2 in enumerate(times2):
            diff = abs(t1 - t2)
            if diff < best_diff and diff <= max_time_diff:
                best_diff = diff
                best_match = j

        if best_match is not None:
            matches.append((transitions1[i], transitions2[best_match]))

    print(f"  ✓ Matched {len(matches)} transition pairs")
    print(f"    Video 1: {len(transitions1)} transitions")
    print(f"    Video 2: {len(transitions2)} transitions")
    print(f"    Match rate: {len(matches)/max(len(transitions1), len(transitions2))*100:.1f}%")

    return matches


def find_aligned_region_from_transitions(
    matched_transitions: List[Tuple[int, int]],
    total_frames1: int,
    total_frames2: int,
    min_matches: int = 3
) -> Optional[Tuple[int, int, int, int]]:
    """
    Find aligned region using matched scene transitions as anchors.

    Strategy:
    - Use first and last matched transitions as boundaries
    - Ensure we have enough transitions for confidence

    Args:
        matched_transitions: List of (frame1, frame2) pairs
        total_frames1: Total frames in video 1
        total_frames2: Total frames in video 2
        min_matches: Minimum number of matched transitions needed

    Returns:
        (start1, end1, start2, end2) or None if insufficient matches
    """
    if len(matched_transitions) < min_matches:
        print(f"\n✗ Not enough matched transitions: {len(matched_transitions)} (need {min_matches})")
        return None

    print(f"\nDetermining aligned region from {len(matched_transitions)} transition matches...")

    # Sort by video 1 frame number
    matched_transitions.sort()

    # Use first transition as start, last as end
    start1, start2 = matched_transitions[0]
    end1, end2 = matched_transitions[-1]

    # Calculate offset between videos
    offset = start2 - start1

    print(f"  First matched transition: frame1={start1}, frame2={start2}")
    print(f"  Last matched transition: frame1={end1}, frame2={end2}")
    print(f"  Offset: video2 is {offset:+d} frames relative to video1")

    # Extend to full video length if possible, maintaining offset
    # Use transitions as anchors but include all frames between them
    if start1 > 0 and start2 > 0:
        # Can we extend to start?
        extend_start = min(start1, start2)
        start1 -= extend_start
        start2 -= extend_start

    if end1 < total_frames1 - 1 and end2 < total_frames2 - 1:
        # Can we extend to end?
        extend_end = min(total_frames1 - 1 - end1, total_frames2 - 1 - end2)
        end1 += extend_end
        end2 += extend_end

    aligned_frames = end1 - start1 + 1

    print(f"\n  ✓ Aligned region (extended to boundaries):")
    print(f"    Video 1: frames {start1} to {end1} ({aligned_frames} frames)")
    print(f"    Video 2: frames {start2} to {end2} ({end2 - start2 + 1} frames)")

    return start1, end1, start2, end2


def sync_videos_by_scene_transitions(
    video1_path: str,
    video2_path: str,
    threshold: float = 30.0,
    min_scene_length: int = 30,
    max_time_diff: float = 0.5,
    min_matches: int = 3,
    save_alignment: str = None,
    save_transitions: bool = True
) -> Optional[Dict]:
    """
    Synchronize videos using scene transition detection.

    Args:
        video1_path: Path to first video
        video2_path: Path to second video
        threshold: Scene detection threshold (higher = stricter)
        min_scene_length: Minimum frames between transitions
        max_time_diff: Max time difference for matching transitions (seconds)
        min_matches: Minimum matched transitions needed
        save_alignment: Save result to JSON file
        save_transitions: Save detected transitions to JSON files

    Returns:
        Alignment dictionary or None if failed
    """
    print("=" * 80)
    print("SCENE TRANSITION-BASED VIDEO SYNCHRONIZATION".center(80))
    print("=" * 80)

    # Get video properties
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)

    fps1 = cap1.get(cv2.CAP_PROP_FPS)
    fps2 = cap2.get(cv2.CAP_PROP_FPS)
    total_frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
    total_frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
    duration1 = total_frames1 / fps1
    duration2 = total_frames2 / fps2

    cap1.release()
    cap2.release()

    print(f"\nVideo 1: {Path(video1_path).name}")
    print(f"  Duration: {duration1:.2f}s, FPS: {fps1:.2f}")
    print(f"\nVideo 2: {Path(video2_path).name}")
    print(f"  Duration: {duration2:.2f}s, FPS: {fps2:.2f}")
    print()

    # Detect transitions in both videos
    transitions1 = detect_scene_transitions(video1_path, threshold, min_scene_length)
    transitions2 = detect_scene_transitions(video2_path, threshold, min_scene_length)

    if not transitions1 or not transitions2:
        print("\n✗ No scene transitions detected in one or both videos!")
        return None

    # Save transitions if requested
    if save_transitions:
        trans_file1 = Path(video1_path).parent / f"{Path(video1_path).stem}_transitions.json"
        trans_file2 = Path(video2_path).parent / f"{Path(video2_path).stem}_transitions.json"

        with open(trans_file1, 'w') as f:
            json.dump({"video": video1_path, "fps": fps1, "transitions": transitions1}, f, indent=2)
        with open(trans_file2, 'w') as f:
            json.dump({"video": video2_path, "fps": fps2, "transitions": transitions2}, f, indent=2)

        print(f"\n✓ Saved transitions to:")
        print(f"  {trans_file1}")
        print(f"  {trans_file2}")

    # Match transitions between videos
    matched = match_transitions(transitions1, transitions2, fps1, fps2, max_time_diff)

    if not matched:
        print("\n✗ No matching scene transitions found!")
        return None

    # Find aligned region
    result = find_aligned_region_from_transitions(
        matched,
        total_frames1,
        total_frames2,
        min_matches
    )

    if result is None:
        return None

    start1, end1, start2, end2 = result

    # Build alignment result
    alignment = {
        "method": "scene_transition_detection",
        "video1": {
            "path": video1_path,
            "name": Path(video1_path).name,
            "fps": fps1,
            "start_frame": start1,
            "end_frame": end1,
            "start_time": float(start1 / fps1),
            "end_time": float(end1 / fps1),
            "aligned_frames": end1 - start1 + 1
        },
        "video2": {
            "path": video2_path,
            "name": Path(video2_path).name,
            "fps": fps2,
            "start_frame": start2,
            "end_frame": end2,
            "start_time": float(start2 / fps2),
            "end_time": float(end2 / fps2),
            "aligned_frames": end2 - start2 + 1
        },
        "scene_transitions": {
            "video1_transitions": len(transitions1),
            "video2_transitions": len(transitions2),
            "matched_transitions": len(matched),
            "matched_pairs": [[int(f1), int(f2)] for f1, f2 in matched[:10]]  # First 10 for reference
        },
        "parameters": {
            "threshold": threshold,
            "min_scene_length": min_scene_length,
            "max_time_diff": max_time_diff,
            "min_matches": min_matches
        }
    }

    # Print results
    print("\n" + "=" * 80)
    print("ALIGNMENT RESULT".center(80))
    print("=" * 80)
    print(f"\nVideo 1: {Path(video1_path).name}")
    print(f"  Frames: {start1} to {end1} ({end1-start1+1} frames)")
    print(f"  Time:   {start1/fps1:.2f}s to {end1/fps1:.2f}s")
    print(f"\nVideo 2: {Path(video2_path).name}")
    print(f"  Frames: {start2} to {end2} ({end2-start2+1} frames)")
    print(f"  Time:   {start2/fps2:.2f}s to {end2/fps2:.2f}s")
    print(f"\nScene Transitions:")
    print(f"  Video 1: {len(transitions1)} transitions detected")
    print(f"  Video 2: {len(transitions2)} transitions detected")
    print(f"  Matched: {len(matched)} transition pairs")

    # Save alignment
    if save_alignment:
        with open(save_alignment, 'w') as f:
            json.dump(alignment, f, indent=2)
        print(f"\n✓ Alignment saved to: {save_alignment}")

    return alignment


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Scene transition-based video synchronization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Detect and sync using scene transitions
  python scene_transition_sync.py \\
    --video1 recordings/cyberpunk/1080p_dlaa_run1.mp4 \\
    --video2 recordings/cyberpunk/1080p_dlaa_run2.mp4 \\
    --output scene_alignment.json

  # Adjust sensitivity
  python scene_transition_sync.py \\
    --video1 recordings/cyberpunk/1080p_dlaa_run1.mp4 \\
    --video2 recordings/cyberpunk/1080p_dlaa_run2.mp4 \\
    --threshold 25 \\
    --min-matches 5

How it works:
  1. Detects scene cuts/transitions in both videos
  2. Matches transitions by timestamp
  3. Uses matched transitions as alignment anchors
  4. Works with different camera angles (transitions occur at same times)
        """
    )

    parser.add_argument('--video1', required=True, help='First video file')
    parser.add_argument('--video2', required=True, help='Second video file')
    parser.add_argument('--output', help='Save alignment to JSON file')
    parser.add_argument('--threshold', type=float, default=30.0,
                       help='Scene detection threshold (default: 30, higher = stricter)')
    parser.add_argument('--min-scene-length', type=int, default=30,
                       help='Minimum frames between transitions (default: 30)')
    parser.add_argument('--max-time-diff', type=float, default=0.5,
                       help='Max time difference for matching transitions in seconds (default: 0.5)')
    parser.add_argument('--min-matches', type=int, default=3,
                       help='Minimum matched transitions needed (default: 3)')
    parser.add_argument('--no-save-transitions', action='store_true',
                       help='Do not save transition data to JSON files')

    args = parser.parse_args()

    alignment = sync_videos_by_scene_transitions(
        video1_path=args.video1,
        video2_path=args.video2,
        threshold=args.threshold,
        min_scene_length=args.min_scene_length,
        max_time_diff=args.max_time_diff,
        min_matches=args.min_matches,
        save_alignment=args.output,
        save_transitions=not args.no_save_transitions
    )

    return 0 if alignment else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
