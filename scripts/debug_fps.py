#!/usr/bin/env python3
"""
Debug FPS extraction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extraction.fps_ocr import FPSOCRExtractor
import cv2

# Calculate ROI
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

video_path = Path("recordings/cyberpunk/trimmed/1080p_dlss_quality.mp4")
roi = parse_percentage_roi("top-left 15%", str(video_path))

print(f"Video: {video_path}")
print(f"ROI: {roi}")

# Extract FPS
extractor = FPSOCRExtractor(roi=roi, use_easyocr=True)
fps_data, _ = extractor.extract_from_video(
    video_path,
    sample_rate=10
)

print(f"\nExtracted {len(fps_data)} FPS measurements")
if fps_data:
    print(f"First 5 entries:")
    for entry in fps_data[:5]:
        print(f"  Frame {entry['frame']}: {entry['fps']} FPS")

    # Check if frame 0 and frame 10 exist
    frame_0 = [e for e in fps_data if e['frame'] == 0]
    frame_10 = [e for e in fps_data if e['frame'] == 10]
    frame_20 = [e for e in fps_data if e['frame'] == 20]

    print(f"\nFrame 0 in data: {len(frame_0) > 0}")
    if frame_0:
        print(f"  {frame_0[0]}")

    print(f"Frame 10 in data: {len(frame_10) > 0}")
    if frame_10:
        print(f"  {frame_10[0]}")

    print(f"Frame 20 in data: {len(frame_20) > 0}")
    if frame_20:
        print(f"  {frame_20[0]}")
