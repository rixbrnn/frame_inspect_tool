#!/usr/bin/env python3
"""
Trim video to the range where FPS counter is visible.

Usage:
    python scripts/trim_by_fps_presence.py \
        --video recordings/cyberpunk/1080p_dlaa_run1.mp4 \
        --roi "0,0,150,50" \
        --output recordings/cyberpunk/trimmed/1080p_dlaa_run1.mp4

Logic:
    - Scans video from start to find FIRST frame where FPS counter appears
    - Scans video from end backwards to find LAST frame where FPS counter is visible
    - Trims video to [first_frame, last_frame] range
    - This excludes intro screens and benchmark result screens
"""

import argparse
import sys
import cv2
import json
from pathlib import Path
from typing import Optional, Tuple
import subprocess

# Import FPS OCR extractor
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from src.extraction.fps_ocr import FPSOCRExtractor


def parse_roi(roi_str: str, frame_width: int = None, frame_height: int = None) -> Tuple[int, int, int, int]:
    """
    Parse ROI from string - supports pixels or percentages.

    Formats:
        - Pixels: "5,5,80,25" (x,y,width,height in pixels)
        - Percentage: "top-left 15%" (15% of screen from top-left corner)
        - Percentage: "top-right 10%" (10% of screen from top-right corner)

    Args:
        roi_str: ROI specification
        frame_width: Video width (required for percentage mode)
        frame_height: Video height (required for percentage mode)

    Returns:
        (x, y, width, height) in pixels
    """
    roi_str = roi_str.strip().lower()

    # Check if percentage format
    if '%' in roi_str:
        if frame_width is None or frame_height is None:
            raise ValueError("Frame dimensions required for percentage ROI")

        # Parse "top-left 15%" or "top-right 10%", etc.
        parts = roi_str.replace('%', '').split()
        if len(parts) != 2:
            raise ValueError(f"Percentage ROI must be 'position percent%', got: {roi_str}")

        position = parts[0]
        percent = float(parts[1]) / 100.0

        # Calculate ROI size based on percentage
        roi_w = int(frame_width * percent)
        roi_h = int(frame_height * percent)

        # Calculate position
        if position == "top-left":
            x, y = 0, 0
        elif position == "top-right":
            x, y = frame_width - roi_w, 0
        elif position == "bottom-left":
            x, y = 0, frame_height - roi_h
        elif position == "bottom-right":
            x, y = frame_width - roi_w, frame_height - roi_h
        else:
            raise ValueError(f"Unknown position: {position}. Use top-left, top-right, bottom-left, or bottom-right")

        return (x, y, roi_w, roi_h)

    # Pixel format: "x,y,width,height"
    parts = roi_str.split(',')
    if len(parts) != 4:
        raise ValueError(f"Pixel ROI must be 'x,y,width,height', got: {roi_str}")
    return tuple(map(int, parts))


def detect_fps_range(video_path: str, roi: Tuple[int, int, int, int]) -> Optional[Tuple[int, int]]:
    """
    Detect frame range where FPS counter is visible with frame-perfect precision.

    Scans every frame to find:
    - First frame where FPS is detected
    - Last frame where FPS is detected

    Args:
        video_path: Path to video file
        roi: (x, y, width, height) for FPS counter location

    Returns:
        (first_frame, last_frame) or None if FPS never detected
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Video: {total_frames} frames @ {fps:.2f} FPS")
    print(f"Scanning for FPS counter in ROI: x={roi[0]}, y={roi[1]}, w={roi[2]}, h={roi[3]}")

    # Initialize OCR extractor (loaded once, reused for all frames)
    extractor = FPSOCRExtractor(roi=roi, use_easyocr=True)

    x, y, w, h = roi

    # Scan forward to find FIRST frame with FPS
    print("\n[1/2] Scanning forward for first FPS appearance (every frame)...")
    first_frame = None

    from tqdm import tqdm

    for frame_idx in tqdm(range(total_frames), desc="Scanning forward", unit="frame"):
        ret, frame = cap.read()
        if not ret:
            break

        # Extract ROI
        roi_crop = frame[y:y+h, x:x+w]

        # Try OCR
        fps_value = extractor.read_fps_from_roi(roi_crop)

        if fps_value is not None and fps_value > 0:
            first_frame = frame_idx
            print(f"\n  ✓ First FPS detection at frame {first_frame} (t={first_frame/fps:.2f}s): {fps_value:.1f} FPS")
            break

    if first_frame is None:
        print("\n  ✗ FPS counter never detected in video")
        cap.release()
        return None

    # Scan backward to find LAST frame with FPS
    print(f"\n[2/2] Scanning backward from end for last FPS appearance (every frame)...")
    last_frame = None

    for frame_idx in tqdm(range(total_frames - 1, first_frame - 1, -1),
                          desc="Scanning backward", unit="frame"):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            continue

        # Extract ROI
        roi_crop = frame[y:y+h, x:x+w]

        # Try OCR
        fps_value = extractor.read_fps_from_roi(roi_crop)

        if fps_value is not None and fps_value > 0:
            last_frame = frame_idx
            print(f"\n  ✓ Last FPS detection at frame {last_frame} (t={last_frame/fps:.2f}s): {fps_value:.1f} FPS")
            break

    if last_frame is None:
        print(f"  ✗ FPS counter disappeared after frame {first_frame}, using end of video")
        last_frame = total_frames - 1

    cap.release()

    print(f"\n{'='*80}")
    print(f"FPS Counter Range Detected".center(80))
    print(f"{'='*80}")
    print(f"First frame: {first_frame} (t={first_frame/fps:.2f}s)")
    print(f"Last frame:  {last_frame} (t={last_frame/fps:.2f}s)")
    print(f"Duration:    {(last_frame - first_frame)/fps:.2f}s ({last_frame - first_frame} frames)")

    return first_frame, last_frame


def trim_video(input_path: str, output_path: str,
               first_frame: int, last_frame: int):
    """
    Trim video using FFmpeg with frame-accurate seeking.

    Args:
        input_path: Source video
        output_path: Output trimmed video
        first_frame: First frame to include
        last_frame: Last frame to include
    """
    # Get video FPS
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    # Convert frames to timestamps
    start_time = first_frame / fps
    duration = (last_frame - first_frame) / fps

    print(f"\nTrimming video with FFmpeg...")
    print(f"  Start: {start_time:.3f}s (frame {first_frame})")
    print(f"  Duration: {duration:.3f}s ({last_frame - first_frame} frames)")

    # Create output directory
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # FFmpeg command for frame-accurate trimming
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output
        '-ss', str(start_time),  # Seek to start
        '-i', input_path,
        '-t', str(duration),  # Duration
        '-c:v', 'libx264',  # Re-encode to ensure frame accuracy
        '-crf', '18',  # High quality
        '-preset', 'fast',
        '-c:a', 'aac',
        '-b:a', '128k',
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"✗ FFmpeg failed:")
        print(result.stderr)
        sys.exit(1)

    # Verify output
    cap_out = cv2.VideoCapture(output_path)
    output_frames = int(cap_out.get(cv2.CAP_PROP_FRAME_COUNT))
    cap_out.release()

    print(f"  ✓ Trimmed video saved: {output_path}")
    print(f"  Output: {output_frames} frames")


def main():
    parser = argparse.ArgumentParser(
        description='Trim video to range where FPS counter is visible'
    )
    parser.add_argument('--video', required=True,
                       help='Input video path')
    parser.add_argument('--output', required=True,
                       help='Output trimmed video path')
    parser.add_argument('--roi', type=str,
                       help='ROI as "x,y,width,height" (pixels) or "top-left 15%%" (percentage). If omitted, attempts auto-detection.')
    parser.add_argument('--dry-run', action='store_true',
                       help='Only detect range, do not trim')

    args = parser.parse_args()

    # Parse or auto-detect ROI
    roi = None
    if args.roi:
        # For percentage ROI, we need video dimensions first
        if '%' in args.roi:
            cap = cv2.VideoCapture(args.video)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            roi = parse_roi(args.roi, frame_width, frame_height)
            print(f"Using percentage ROI: {args.roi} -> {roi}")
        else:
            roi = parse_roi(args.roi)
            print(f"Using manual ROI: {roi}")
    else:
        print("Attempting auto-detection of FPS counter...")
        # Try to auto-detect (using FPSOCRExtractor's built-in method)
        extractor = FPSOCRExtractor(roi=None, use_easyocr=True)
        cap = cv2.VideoCapture(args.video)
        ret, first_frame = cap.read()
        cap.release()
        if ret:
            roi = extractor.auto_detect_roi(first_frame, "top_left")
        if roi is None:
            print("✗ Auto-detection failed. Please provide ROI manually with --roi")
            sys.exit(1)
        print(f"✓ Auto-detected ROI: {roi}")

    # Detect FPS range
    fps_range = detect_fps_range(args.video, roi)

    if fps_range is None:
        print("\n✗ FPS counter never detected in video. Cannot trim.")
        sys.exit(1)

    first_frame, last_frame = fps_range

    # Trim video (unless dry-run)
    if args.dry_run:
        print("\n[Dry run] Skipping actual trim")
        print(f"Would trim: {args.video} -> {args.output}")
        print(f"Range: frames {first_frame}-{last_frame}")
    else:
        trim_video(args.video, args.output, first_frame, last_frame)
        print("\n✓ Video trimming complete")


if __name__ == '__main__':
    main()
