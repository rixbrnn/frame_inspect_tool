#!/usr/bin/env python3
"""
Interactive ROI Calibrator for FPS Counter

Helps you determine the correct ROI coordinates for the FPS counter in your recordings.
Opens an interactive window where you can adjust the ROI box and test OCR in real-time.

Usage:
    python calibrate_fps_roi.py --video ../tcc/recordings/raw/Quality_raw.mp4
"""

import argparse
import sys
from pathlib import Path
import cv2
import numpy as np


class ROICalibrator:
    """Interactive ROI calibration tool"""

    def __init__(self, video_path: Path, frame_number: int = 0):
        self.video_path = video_path
        self.frame_number = frame_number
        self.frame = None
        self.roi = [1700, 50, 200, 80]  # Default for 1920x1080 MSI Afterburner top-right
        self.dragging = False
        self.drag_start = None
        self.window_name = "FPS ROI Calibrator - Press SPACE to test OCR, Q to quit, S to save"

    def load_frame(self):
        """Load the specified frame from video"""
        cap = cv2.VideoCapture(str(self.video_path))

        if not cap.isOpened():
            print(f"Error: Cannot open video {self.video_path}")
            return False

        # Get video info
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"Video: {width}x{height}, {total_frames} frames")

        if self.frame_number >= total_frames:
            self.frame_number = 0

        cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)
        ret, self.frame = cap.read()
        cap.release()

        if not ret:
            print(f"Error: Cannot read frame {self.frame_number}")
            return False

        # Adjust default ROI based on resolution
        if width >= 3840:  # 4K
            self.roi = [3400, 100, 400, 160]
        elif width >= 2560:  # 1440p
            self.roi = [2200, 70, 300, 120]

        return True

    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for ROI adjustment"""

        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if clicking inside current ROI
            rx, ry, rw, rh = self.roi
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                self.dragging = True
                self.drag_start = (x - rx, y - ry)
            else:
                # Start new ROI
                self.roi[0] = x
                self.roi[1] = y
                self.dragging = True
                self.drag_start = (0, 0)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.dragging:
                if self.drag_start == (0, 0):
                    # Resizing
                    self.roi[2] = max(50, x - self.roi[0])
                    self.roi[3] = max(30, y - self.roi[1])
                else:
                    # Moving
                    self.roi[0] = x - self.drag_start[0]
                    self.roi[1] = y - self.drag_start[1]

        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False

    def draw_roi(self, frame: np.ndarray) -> np.ndarray:
        """Draw ROI rectangle on frame"""
        display = frame.copy()
        x, y, w, h = self.roi

        # Draw rectangle
        cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Draw corner handles
        corner_size = 10
        cv2.circle(display, (x, y), corner_size, (0, 255, 0), -1)
        cv2.circle(display, (x + w, y), corner_size, (0, 255, 0), -1)
        cv2.circle(display, (x, y + h), corner_size, (0, 255, 0), -1)
        cv2.circle(display, (x + w, y + h), corner_size, (0, 255, 0), -1)

        # Draw coordinates
        coord_text = f"ROI: {x},{y},{w},{h}"
        cv2.putText(display, coord_text, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Extract and show ROI preview
        roi_img = frame[y:y+h, x:x+w]
        if roi_img.size > 0:
            # Resize ROI for display
            scale = min(300 / w, 200 / h, 3.0)
            preview_w = int(w * scale)
            preview_h = int(h * scale)
            roi_preview = cv2.resize(roi_img, (preview_w, preview_h), interpolation=cv2.INTER_CUBIC)

            # Position preview in bottom-left corner
            preview_y = display.shape[0] - preview_h - 20
            preview_x = 20

            # Add black background for preview
            cv2.rectangle(display,
                         (preview_x - 5, preview_y - 25),
                         (preview_x + preview_w + 5, preview_y + preview_h + 5),
                         (0, 0, 0), -1)

            # Add title
            cv2.putText(display, "ROI Preview:",
                       (preview_x, preview_y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Overlay preview
            display[preview_y:preview_y+preview_h, preview_x:preview_x+preview_w] = roi_preview

        return display

    def test_ocr(self):
        """Test OCR on current ROI"""
        x, y, w, h = self.roi
        roi_img = self.frame[y:y+h, x:x+w]

        print("\nTesting OCR on current ROI...")
        print(f"  ROI: x={x}, y={y}, w={w}, h={h}")

        # Try with EasyOCR
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False, verbose=False)

            # Preprocess (same as in fps_ocr_extractor.py)
            gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
            scale_factor = 2
            resized = cv2.resize(gray, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_CUBIC)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(resized)
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            results = reader.readtext(binary, detail=1)

            if results:
                print(f"  ✓ EasyOCR detected: {len(results)} text region(s)")
                for detection in results:
                    bbox, text, confidence = detection
                    print(f"    - '{text}' (confidence: {confidence:.2f})")
            else:
                print("  ⚠ EasyOCR: No text detected")

        except ImportError:
            print("  ⚠ EasyOCR not installed")
        except Exception as e:
            print(f"  ✗ EasyOCR error: {e}")

        # Try with Tesseract
        try:
            import pytesseract

            # Preprocess
            gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
            scale_factor = 2
            resized = cv2.resize(gray, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_CUBIC)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(resized)
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789FPSfps.:, '
            text = pytesseract.image_to_string(binary, config=custom_config)

            if text.strip():
                print(f"  ✓ Tesseract detected: '{text.strip()}'")
            else:
                print("  ⚠ Tesseract: No text detected")

        except ImportError:
            print("  ⚠ Tesseract not installed")
        except Exception as e:
            print(f"  ✗ Tesseract error: {e}")

    def run(self):
        """Run interactive calibration"""
        if not self.load_frame():
            return None

        # Create window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        # Instructions
        print("\n" + "=" * 60)
        print("ROI Calibration Instructions:")
        print("  • Click and drag to move the ROI box")
        print("  • Click outside and drag to create new ROI")
        print("  • Press SPACE to test OCR on current ROI")
        print("  • Press S to save coordinates and exit")
        print("  • Press Q to quit without saving")
        print("  • Press +/- to change frame")
        print("=" * 60)

        while True:
            display = self.draw_roi(self.frame)
            cv2.imshow(self.window_name, display)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q') or key == 27:  # Q or ESC
                print("\nCalibration cancelled")
                cv2.destroyAllWindows()
                return None

            elif key == ord('s'):  # Save
                print(f"\n✓ ROI saved: {self.roi[0]},{self.roi[1]},{self.roi[2]},{self.roi[3]}")
                cv2.destroyAllWindows()
                return self.roi

            elif key == ord(' '):  # Test OCR
                self.test_ocr()

            elif key == ord('+') or key == ord('='):  # Next frame
                cap = cv2.VideoCapture(str(self.video_path))
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()

                self.frame_number = min(self.frame_number + 30, total_frames - 1)
                self.load_frame()
                print(f"  Frame: {self.frame_number}")

            elif key == ord('-') or key == ord('_'):  # Previous frame
                self.frame_number = max(self.frame_number - 30, 0)
                self.load_frame()
                print(f"  Frame: {self.frame_number}")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive ROI calibration for FPS counter"
    )
    parser.add_argument(
        "--video",
        type=Path,
        required=True,
        help="Video file with FPS counter"
    )
    parser.add_argument(
        "--frame",
        type=int,
        default=0,
        help="Frame number to use for calibration (default: 0)"
    )

    args = parser.parse_args()

    if not args.video.exists():
        print(f"Error: Video file not found: {args.video}")
        sys.exit(1)

    calibrator = ROICalibrator(args.video, args.frame)
    roi = calibrator.run()

    if roi:
        print("\nUse this ROI in your extraction command:")
        print(f"  --roi {roi[0]},{roi[1]},{roi[2]},{roi[3]}")
        print("\nExample:")
        print(f"  python src/fps_ocr_extractor.py \\")
        print(f"      --video {args.video} \\")
        print(f"      --roi {roi[0]},{roi[1]},{roi[2]},{roi[3]} \\")
        print(f"      --output fps_data.json")


if __name__ == "__main__":
    main()
