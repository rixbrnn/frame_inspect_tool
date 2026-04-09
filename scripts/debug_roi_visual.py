#!/usr/bin/env python3
"""
Visual debug: Extract and save the ROI from frame 0 to see what OCR sees
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import numpy as np

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

video_path = "recordings/cyberpunk/trimmed/1080p_dlss_quality.mp4"
roi = parse_percentage_roi("top-left 15%", video_path)

print(f"Video: {video_path}")
print(f"ROI: {roi}")

cap = cv2.VideoCapture(video_path)
x, y, w, h = roi

# Extract frames 0, 10, 20
for frame_num in [0, 10, 20]:
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()

    if ret:
        # Extract ROI
        roi_img = frame[y:y+h, x:x+w]

        # Save both full frame and ROI
        output_dir = Path("results/cyberpunk/debug_fps")
        output_dir.mkdir(parents=True, exist_ok=True)

        cv2.imwrite(str(output_dir / f"frame_{frame_num}_full.png"), frame)
        cv2.imwrite(str(output_dir / f"frame_{frame_num}_roi.png"), roi_img)

        print(f"\nFrame {frame_num}:")
        print(f"  Full: {output_dir}/frame_{frame_num}_full.png")
        print(f"  ROI: {output_dir}/frame_{frame_num}_roi.png")
        print(f"  ROI size: {roi_img.shape}")

cap.release()
print(f"\n✓ Debug images saved to: results/cyberpunk/debug_fps/")
