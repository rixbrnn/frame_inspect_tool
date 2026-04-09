#!/usr/bin/env python3
"""
Minimal test to check FPS lookup matching
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extraction.fps_ocr import FPSOCRExtractor
import cv2

def parse_percentage_roi(roi_str: str, video_path: str) -> tuple:
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    roi_str = roi_str.strip().lower()
    parts = roi_str.replace('%', '').split()
    position = parts[0]
    percent = float(parts[1]) / 100.0

    roi_w = int(frame_width * percent)
    roi_h = int(frame_height * percent)

    if position == "top-left":
        x, y = 0, 0
    else:
        raise ValueError(f"Unknown position: {position}")

    return (x, y, roi_w, roi_h)

def build_fps_lookup(fps_data_list: list) -> dict:
    """Build frame index -> FPS data lookup dict"""
    return {entry['frame']: entry for entry in fps_data_list}

video_path = Path("recordings/cyberpunk/trimmed/1080p_dlss_quality.mp4")
roi = parse_percentage_roi("top-left 15%", str(video_path))

print(f"Extracting FPS...")
extractor = FPSOCRExtractor(roi=roi, use_easyocr=True)
fps_data, _ = extractor.extract_from_video(video_path, sample_rate=10)

print(f"Building lookup dict...")
fps_lookup = build_fps_lookup(fps_data)

print(f"\nFPS lookup has {len(fps_lookup)} entries")
print(f"Sample keys: {sorted(list(fps_lookup.keys()))[:10]}")

# Simulate the comparison loop
print(f"\nSimulating comparison loop (sample_rate=10):")
sample_rate = 10
total_frames = 3927  # from video

frames_with_fps = 0
frames_without_fps = 0

for frame_idx in range(0, total_frames, sample_rate):
    if frame_idx % sample_rate == 0:  # This is the sampling condition
        if frame_idx in fps_lookup:
            frames_with_fps += 1
            if frame_idx < 50:
                print(f"  Frame {frame_idx}: HAS FPS = {fps_lookup[frame_idx]['fps']}")
        else:
            frames_without_fps += 1
            if frame_idx < 50:
                print(f"  Frame {frame_idx}: NO FPS")

print(f"\nSummary:")
print(f"  Frames with FPS: {frames_with_fps}")
print(f"  Frames without FPS: {frames_without_fps}")
print(f"  Total frames sampled: {frames_with_fps + frames_without_fps}")
