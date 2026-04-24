#!/usr/bin/env python3
"""
Simple ROI Selector Tool

Extracts middle frame from video and allows user to visually select
a rectangular region. Saves coordinates to YAML file with marker pattern.

Usage:
    # For trim ROI with text marker (e.g., "PROGRESSO")
    python scripts/roi_selector.py --video recordings/forza_extreme/1080p_dlaa_run1.mp4 --roi-name trim --marker-pattern "PROGRESSO"

    # For FPS ROI with numeric counter
    python scripts/roi_selector.py --video recordings/forza_extreme/1080p_dlaa_run1.mp4 --roi-name fps --marker-pattern "numeric"

    # For any other ROI
    python scripts/roi_selector.py --video recordings/cyberpunk/1080p_dlaa_run1.mp4 --roi-name overlay

Output:
    roi_{name}_coordinates.yaml with selected region coordinates and regex pattern
"""

import argparse
import cv2
import sys
import yaml
from pathlib import Path
from typing import Optional, Tuple


def extract_middle_frame(video_path: str) -> Tuple[any, int, float, int, int]:
    """
    Extract middle frame from video.

    Returns:
        (frame, frame_index, timestamp, width, height)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Get middle frame (50% position)
    middle_frame_idx = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError(f"Failed to read middle frame")

    timestamp = middle_frame_idx / fps

    return frame, middle_frame_idx, timestamp, width, height


class ROISelector:
    """Interactive ROI selection using OpenCV mouse callbacks"""

    def __init__(self, frame):
        self.frame = frame.copy()
        self.display_frame = frame.copy()
        self.roi_start = None
        self.roi_end = None
        self.selecting = False

    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for rectangle selection"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Start selection
            self.roi_start = (x, y)
            self.selecting = True

        elif event == cv2.EVENT_MOUSEMOVE and self.selecting:
            # Update selection preview
            self.display_frame = self.frame.copy()
            cv2.rectangle(self.display_frame, self.roi_start, (x, y),
                         (0, 255, 0), 2)

        elif event == cv2.EVENT_LBUTTONUP:
            # Finish selection
            self.roi_end = (x, y)
            self.selecting = False
            # Draw final rectangle
            self.display_frame = self.frame.copy()
            cv2.rectangle(self.display_frame, self.roi_start, self.roi_end,
                         (0, 255, 0), 2)

    def get_roi(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Convert selected points to (x, y, width, height) format.
        Returns None if no selection made.
        """
        if not self.roi_start or not self.roi_end:
            return None

        x1, y1 = self.roi_start
        x2, y2 = self.roi_end

        # Normalize to top-left and bottom-right
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)

        return (x, y, w, h)

    def run(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Run interactive selection loop.
        Returns selected ROI or None if cancelled.
        """
        window_name = "ROI Selector - Click and drag to select"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)

        print("\nInstructions:")
        print("  • Click and drag to select rectangle")
        print("  • Press ENTER to confirm and save")
        print("  • Press ESC to cancel")

        while True:
            cv2.imshow(window_name, self.display_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 13:  # ENTER
                roi = self.get_roi()
                if roi is None:
                    print("\n⚠ No region selected. Please select a rectangle first.")
                    continue
                cv2.destroyAllWindows()
                return roi

            elif key == 27:  # ESC
                print("\n✗ Selection cancelled")
                cv2.destroyAllWindows()
                return None


def save_coordinates(video_path: str, roi: Tuple[int, int, int, int],
                     frame_idx: int, timestamp: float,
                     width: int, height: int,
                     output_path: str,
                     roi_name: str,
                     marker_pattern: Optional[str] = None):
    """Save ROI coordinates to YAML file"""
    x, y, w, h = roi

    # Determine marker type and regex pattern
    if marker_pattern == "numeric":
        marker_type = "fps"
        regex_pattern = r'\d+\.?\d*'
        description = "Numeric FPS counter"
    elif marker_pattern:
        marker_type = "text"
        regex_pattern = marker_pattern
        description = f"Text pattern: {marker_pattern}"
    else:
        marker_type = "unknown"
        regex_pattern = ""
        description = "Not specified - please fill in marker details"

    config = {
        'roi_name': roi_name,
        'video_info': {
            'source': str(Path(video_path).name),
            'resolution': f"{width}x{height}",
            'frame_index': frame_idx,
            'timestamp': f"{timestamp:.1f}s"
        },
        'roi': {
            'pixels': f"{x},{y},{w},{h}"
        },
        'marker': {
            'type': marker_type,
            'pattern': marker_pattern or "Not specified",
            'regex': regex_pattern,
            'description': description
        }
    }

    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"\n✓ Coordinates saved to: {output_path}")
    print(f"\nROI: {roi_name}")
    print(f"  pixels: {x},{y},{w},{h}")
    print(f"  marker: {description}")
    print(f"  Usage: --roi \"{x},{y},{w},{h}\"")



def main():
    parser = argparse.ArgumentParser(
        description='Simple ROI selector - extract middle frame and select region'
    )
    parser.add_argument('--video', required=True,
                       help='Path to video file')
    parser.add_argument('--roi-name', default='roi',
                       help='Name for the ROI (e.g., "trim", "fps", "overlay"). Used in output filename.')
    parser.add_argument('--marker-pattern', default=None,
                       help='Text pattern to detect (e.g., "PROGRESSO", "numeric" for FPS)')
    parser.add_argument('--output', default=None,
                       help='Output file for coordinates (default: roi_{name}_coordinates.yaml in video directory)')

    args = parser.parse_args()

    # Generate default output path in video's directory if not specified
    if args.output is None:
        video_dir = Path(args.video).parent
        args.output = str(video_dir / f'roi_{args.roi_name}_coordinates.yaml')

    # Extract middle frame
    print(f"Extracting middle frame from: {args.video}")
    try:
        frame, frame_idx, timestamp, width, height = extract_middle_frame(args.video)
        print(f"✓ Frame extracted (frame {frame_idx} at t={timestamp:.1f}s)")
        print(f"✓ Resolution: {width}x{height}")
    except Exception as e:
        print(f"✗ Failed to extract frame: {e}")
        sys.exit(1)

    # Run interactive ROI selection
    selector = ROISelector(frame)
    roi = selector.run()

    if roi is None:
        sys.exit(1)

    # Save coordinates
    save_coordinates(args.video, roi, frame_idx, timestamp,
                     width, height, args.output, args.roi_name, args.marker_pattern)

    print("\n✓ Done!")


if __name__ == '__main__':
    main()
