#!/usr/bin/env python3
"""
Test single comparison with FPS extraction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compare_alignment_quality import compare_alignment_quality, export_per_frame_to_csv
import json
import cv2


def parse_percentage_roi(roi_str: str, video_path: str) -> tuple:
    """Parse percentage-based ROI into pixel coordinates."""
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
    elif position == "top-right":
        x, y = frame_width - roi_w, 0
    elif position == "bottom-left":
        x, y = 0, frame_height - roi_h
    elif position == "bottom-right":
        x, y = frame_width - roi_w, frame_height - roi_h
    else:
        raise ValueError(f"Unknown position: {position}")

    return (x, y, roi_w, roi_h)


# Test with 1080p DLAA vs Quality
ref_video = "recordings/cyberpunk/trimmed/1080p_dlaa_run1.mp4"
cmp_video = "recordings/cyberpunk/trimmed/1080p_dlss_quality.mp4"

# FPS source videos - USE TRIMMED VIDEOS (they still have FPS overlays)
fps_ref = "recordings/cyberpunk/trimmed/1080p_dlaa_run1.mp4"
fps_cmp = "recordings/cyberpunk/trimmed/1080p_dlss_quality.mp4"

# Calculate ROI
roi = parse_percentage_roi("top-left 15%", fps_cmp)
print(f"Using ROI: {roi} (top-left 15%)")

# Run comparison
results = compare_alignment_quality(
    video1_path=ref_video,
    video2_path=cmp_video,
    alignment_name="TEST_1080p_DLAA_vs_Quality",
    sample_rate=10,
    compute_advanced=True,
    use_gpu=True,
    compute_vmaf=False,  # Skip VMAF for faster testing
    extract_fps=True,
    fps_video1=fps_ref,
    fps_video2=fps_cmp,
    fps_roi=roi,
    fps_sample_rate=10,
    store_per_frame=True
)

# Save outputs
output_path = Path("results/cyberpunk/quality_comparison")
output_path.mkdir(parents=True, exist_ok=True)

with open(output_path / "TEST_comparison.json", 'w') as f:
    json.dump(results, f, indent=2)

if 'per_frame_data' in results:
    export_per_frame_to_csv(results['per_frame_data'], str(output_path / "TEST_comparison.csv"))
    print(f"\n✓ CSV exported with {len(results['per_frame_data']['frames'])} frames")
else:
    print("\n✗ No per_frame_data found - FPS extraction may have failed")

print(f"\n✓ Test complete. Check {output_path} for outputs.")
