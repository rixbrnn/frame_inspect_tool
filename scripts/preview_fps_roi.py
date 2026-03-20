#!/usr/bin/env python3
"""
FPS ROI Preview Tool - Visualize FPS counter detection region

This tool shows a live preview of where the FPS counter will be detected,
overlaying the ROI rectangle and showing OCR results in real-time.

Usage:
    # Preview with existing ROI config
    python scripts/preview_fps_roi.py \
        --video recordings/blackmyth/1080p/extracted/run1_60fps.mp4 \
        --roi recordings/blackmyth/fps_roi.json

    # Preview with manual ROI coordinates
    python scripts/preview_fps_roi.py \
        --video recordings/blackmyth/1080p/extracted/run1_60fps.mp4 \
        --x 50 --y 50 --width 120 --height 40

    # Interactive mode (use mouse to adjust)
    python scripts/preview_fps_roi.py \
        --video recordings/blackmyth/1080p/extracted/run1_60fps.mp4 \
        --interactive
"""

import cv2
import argparse
import json
from pathlib import Path
import numpy as np
import sys

# Try to import EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️  EasyOCR not available. Install with: pip install easyocr")


class FPSROIPreview:
    def __init__(self, video_path, roi, ocr_enabled=True):
        self.video_path = video_path
        self.roi = roi  # (x, y, width, height)
        self.ocr_enabled = ocr_enabled and EASYOCR_AVAILABLE

        # Initialize OCR reader if available
        if self.ocr_enabled:
            print("Loading OCR model...")
            self.reader = easyocr.Reader(['en'], gpu=True)
            print("✓ OCR ready")
        else:
            self.reader = None

        # Open video
        self.cap = cv2.VideoCapture(str(video_path))
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open video: {video_path}")

        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"\nVideo: {video_path.name}")
        print(f"  Resolution: {self.width}x{self.height}")
        print(f"  FPS: {self.fps:.2f}")
        print(f"  Frames: {self.frame_count}")
        print(f"\nROI: x={roi[0]}, y={roi[1]}, w={roi[2]}, h={roi[3]}")

    def extract_fps_text(self, frame):
        """Extract FPS text from ROI using OCR"""
        if not self.ocr_enabled:
            return None

        x, y, w, h = self.roi
        roi_img = frame[y:y+h, x:x+w]

        # Preprocess: grayscale, resize, enhance contrast
        gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(resized)

        # Threshold
        _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        try:
            # OCR
            results = self.reader.readtext(thresh, detail=0)
            if results:
                text = ' '.join(results)
                # Try to extract number
                import re
                numbers = re.findall(r'\d+\.?\d*', text)
                if numbers:
                    fps_value = float(numbers[0])
                    if 10 < fps_value < 300:  # Sanity check
                        return fps_value
        except:
            pass

        return None

    def draw_overlay(self, frame, fps_value=None):
        """Draw ROI rectangle and FPS value on frame"""
        overlay = frame.copy()
        x, y, w, h = self.roi

        # Draw semi-transparent rectangle
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), -1)

        # Blend with original
        alpha = 0.3
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        # Draw solid border
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Add corner markers
        marker_size = 10
        # Top-left
        cv2.line(frame, (x, y), (x + marker_size, y), (0, 255, 0), 3)
        cv2.line(frame, (x, y), (x, y + marker_size), (0, 255, 0), 3)
        # Top-right
        cv2.line(frame, (x + w, y), (x + w - marker_size, y), (0, 255, 0), 3)
        cv2.line(frame, (x + w, y), (x + w, y + marker_size), (0, 255, 0), 3)
        # Bottom-left
        cv2.line(frame, (x, y + h), (x + marker_size, y + h), (0, 255, 0), 3)
        cv2.line(frame, (x, y + h), (x, y + h - marker_size), (0, 255, 0), 3)
        # Bottom-right
        cv2.line(frame, (x + w, y + h), (x + w - marker_size, y + h), (0, 255, 0), 3)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - marker_size), (0, 255, 0), 3)

        # Add ROI label
        label = f"FPS ROI: {w}x{h}"
        cv2.putText(frame, label, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Display detected FPS value if available
        if fps_value is not None:
            fps_text = f"Detected: {fps_value:.1f} FPS"
            cv2.putText(frame, fps_text, (x, y + h + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        elif self.ocr_enabled:
            cv2.putText(frame, "Detecting...", (x, y + h + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Show ROI zoomed view (enlarged)
        roi_img = frame[y:y+h, x:x+w].copy()
        zoom_scale = 4
        zoomed = cv2.resize(roi_img, None, fx=zoom_scale, fy=zoom_scale,
                           interpolation=cv2.INTER_NEAREST)

        # Place zoomed view in top-right corner
        zh, zw = zoomed.shape[:2]
        offset = 20
        if zh < self.height - offset and zw < self.width - offset:
            frame[offset:offset+zh, self.width-zw-offset:self.width-offset] = zoomed
            # Border around zoom
            cv2.rectangle(frame,
                         (self.width-zw-offset, offset),
                         (self.width-offset, offset+zh),
                         (255, 255, 0), 2)
            cv2.putText(frame, "4x Zoom",
                       (self.width-zw-offset, offset-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        return frame

    def run(self, sample_rate=30):
        """Run preview with real-time OCR"""
        print("\n" + "="*80)
        print("FPS ROI PREVIEW".center(80))
        print("="*80)
        print("\nControls:")
        print("  SPACE  - Pause/Resume")
        print("  R      - Run OCR on current frame")
        print("  Q/ESC  - Quit")
        print("  LEFT   - Previous frame (when paused)")
        print("  RIGHT  - Next frame (when paused)")
        print("\n" + "="*80 + "\n")

        frame_idx = 0
        paused = False
        ocr_result = None

        while True:
            if not paused:
                ret, frame = self.cap.read()
                if not ret:
                    # Loop back to start
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    frame_idx = 0
                    continue

                frame_idx += 1

                # Run OCR every N frames
                if self.ocr_enabled and frame_idx % sample_rate == 0:
                    ocr_result = self.extract_fps_text(frame)

            # Draw overlay
            display_frame = self.draw_overlay(frame.copy(), ocr_result)

            # Add frame info at bottom-left to avoid overlapping with FPS counter
            info_text = f"Frame: {frame_idx}/{self.frame_count} | Time: {frame_idx/self.fps:.2f}s"
            if paused:
                info_text += " | PAUSED"
            cv2.putText(display_frame, info_text, (10, self.height - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Show frame
            cv2.imshow('FPS ROI Preview', display_frame)

            # Handle input
            key = cv2.waitKey(1 if not paused else 0) & 0xFF

            if key == ord('q') or key == 27:  # Q or ESC
                break
            elif key == ord(' '):  # SPACE
                paused = not paused
                print(f"{'Paused' if paused else 'Resumed'}")
            elif key == ord('r'):  # R - Force OCR
                if self.ocr_enabled:
                    print("Running OCR...")
                    ocr_result = self.extract_fps_text(frame)
                    print(f"  Detected: {ocr_result if ocr_result else 'None'}")
            elif key == 81 and paused:  # LEFT arrow (when paused)
                frame_idx = max(0, frame_idx - 1)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = self.cap.read()
            elif key == 83 and paused:  # RIGHT arrow (when paused)
                frame_idx = min(self.frame_count - 1, frame_idx + 1)
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = self.cap.read()

        self.cap.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description='Preview FPS counter detection region',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview with ROI config file
  python scripts/preview_fps_roi.py \\
      --video recordings/blackmyth/1080p/extracted/run1_60fps.mp4 \\
      --roi recordings/blackmyth/fps_roi.json

  # Preview with manual coordinates
  python scripts/preview_fps_roi.py \\
      --video recordings/blackmyth/1080p/extracted/run1_60fps.mp4 \\
      --x 50 --y 50 --width 120 --height 40

  # Preview without OCR (faster)
  python scripts/preview_fps_roi.py \\
      --video recordings/blackmyth/1080p/extracted/run1_60fps.mp4 \\
      --roi recordings/blackmyth/fps_roi.json \\
      --no-ocr
        """
    )

    parser.add_argument('--video', type=Path, required=True,
                       help='Path to video file')
    parser.add_argument('--roi', type=Path,
                       help='Path to ROI config JSON file')
    parser.add_argument('--x', type=int, help='ROI X coordinate')
    parser.add_argument('--y', type=int, help='ROI Y coordinate')
    parser.add_argument('--width', type=int, help='ROI width')
    parser.add_argument('--height', type=int, help='ROI height')
    parser.add_argument('--no-ocr', action='store_true',
                       help='Disable OCR (faster preview)')
    parser.add_argument('--sample-rate', type=int, default=30,
                       help='OCR every N frames (default: 30)')

    args = parser.parse_args()

    # Get ROI coordinates
    roi = None

    if args.roi:
        # Load from JSON
        with open(args.roi, 'r') as f:
            roi_data = json.load(f)
            roi_config = roi_data.get('roi', {})
            roi = (
                roi_config.get('x', 0),
                roi_config.get('y', 0),
                roi_config.get('width', 100),
                roi_config.get('height', 40)
            )
    elif all([args.x is not None, args.y is not None,
              args.width is not None, args.height is not None]):
        # Use manual coordinates
        roi = (args.x, args.y, args.width, args.height)
    else:
        print("Error: Must provide either --roi JSON file or manual coordinates (--x, --y, --width, --height)")
        return 1

    if not args.video.exists():
        print(f"Error: Video file not found: {args.video}")
        return 1

    # Create preview
    try:
        preview = FPSROIPreview(
            args.video,
            roi,
            ocr_enabled=not args.no_ocr
        )
        preview.run(sample_rate=args.sample_rate)
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    print("\nPreview closed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
