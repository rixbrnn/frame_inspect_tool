#!/usr/bin/env python3
"""
FPS OCR Extractor - Extract FPS data directly from on-screen display in video recordings

Reads MSI Afterburner or RivaTuner OSD overlay from video frames using OCR.
This eliminates the need for external CSV files and provides perfect frame-by-frame synchronization.

Usage:
    python fps_ocr_extractor.py \
        --video ../tcc/recordings/processed/Quality_60fps.mp4 \
        --roi 1700,50,200,80 \
        --output ../tcc/fps_data/Quality_fps_ocr.json \
        --preview roi_preview.png
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2
from tqdm import tqdm
import statistics


class FPSOCRExtractor:
    """Extract FPS values from on-screen display using OCR"""

    def __init__(self, roi: Tuple[int, int, int, int] = None, use_easyocr: bool = True):
        """
        Initialize OCR extractor

        Args:
            roi: Region of interest as (x, y, width, height). If None, will attempt auto-detection
            use_easyocr: Use EasyOCR (True) or Tesseract (False)
        """
        self.roi = roi
        self.use_easyocr = use_easyocr
        self.reader = None

        if use_easyocr:
            try:
                import easyocr
                print("  Initializing EasyOCR (this may take a moment on first run)...")
                self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                print("  ✓ EasyOCR ready")
            except ImportError:
                print("  ⚠ EasyOCR not installed. Install with: pip install easyocr")
                print("  Falling back to Tesseract...")
                self.use_easyocr = False

        if not self.use_easyocr:
            try:
                import pytesseract
                # Test if tesseract is available
                pytesseract.get_tesseract_version()
                print("  ✓ Tesseract ready")
            except Exception as e:
                print(f"  ✗ Tesseract not available: {e}")
                print("  Install Tesseract: brew install tesseract (macOS) or apt install tesseract-ocr (Linux)")
                raise RuntimeError("No OCR engine available")

    def auto_detect_roi(self, frame: np.ndarray, search_region: str = "top_right") -> Optional[Tuple[int, int, int, int]]:
        """
        Attempt to automatically detect FPS counter region

        Args:
            frame: Video frame
            search_region: Where to look ("top_right", "top_left", "bottom_right", "bottom_left")

        Returns:
            ROI as (x, y, width, height) or None if not found
        """
        h, w = frame.shape[:2]

        # Define search area based on region
        if search_region == "top_right":
            search_x, search_y = int(w * 0.7), 0
            search_w, search_h = int(w * 0.3), int(h * 0.15)
        elif search_region == "top_left":
            search_x, search_y = 0, 0
            search_w, search_h = int(w * 0.3), int(h * 0.15)
        elif search_region == "bottom_right":
            search_x, search_y = int(w * 0.7), int(h * 0.85)
            search_w, search_h = int(w * 0.3), int(h * 0.15)
        else:  # bottom_left
            search_x, search_y = 0, int(h * 0.85)
            search_w, search_h = int(w * 0.3), int(h * 0.15)

        # Extract search region
        search_frame = frame[search_y:search_y+search_h, search_x:search_x+search_w]

        # Look for bright text (OSD is usually bright on dark background)
        gray = cv2.cvtColor(search_frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # Find contours of bright regions
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest bright region (likely the OSD)
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)

            # Add padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(search_w - x, w + 2 * padding)
            h = min(search_h - y, h + 2 * padding)

            # Convert to absolute coordinates
            abs_x = search_x + x
            abs_y = search_y + y

            return (abs_x, abs_y, w, h)

        return None

    def preprocess_roi(self, roi_img: np.ndarray) -> np.ndarray:
        """
        Preprocess ROI for better OCR accuracy

        Args:
            roi_img: Cropped ROI image

        Returns:
            Preprocessed image optimized for digit recognition
        """
        # Convert to grayscale
        if len(roi_img.shape) == 3:
            gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi_img

        # Resize for better OCR (OCR works better on larger text)
        scale_factor = 2
        h, w = gray.shape
        resized = cv2.resize(gray, (w * scale_factor, h * scale_factor), interpolation=cv2.INTER_CUBIC)

        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(resized)

        # Threshold to get clean black text on white background
        # MSI Afterburner typically uses bright text, so invert for OCR
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, h=10, templateWindowSize=7, searchWindowSize=21)

        return denoised

    def extract_fps_from_text(self, text: str) -> Optional[float]:
        """
        Parse FPS value from OCR text

        Handles formats like:
        - "60 FPS"
        - "60FPS"
        - "FPS: 60"
        - "60.5"
        - "60"

        Args:
            text: OCR output text

        Returns:
            FPS value or None if not found
        """
        if not text:
            return None

        # Clean text
        text = text.upper().strip()

        # Pattern 1: "60 FPS" or "60FPS"
        match = re.search(r'(\d+(?:\.\d+)?)\s*FPS', text)
        if match:
            return float(match.group(1))

        # Pattern 2: "FPS: 60" or "FPS 60"
        match = re.search(r'FPS[:\s]+(\d+(?:\.\d+)?)', text)
        if match:
            return float(match.group(1))

        # Pattern 3: Just a number (assume it's FPS if between 10-300)
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            value = float(match.group(1))
            if 10 <= value <= 300:  # Reasonable FPS range
                return value

        return None

    def read_fps_from_roi(self, roi_img: np.ndarray) -> Optional[float]:
        """
        Extract FPS value from ROI using OCR

        Args:
            roi_img: Cropped ROI image

        Returns:
            FPS value or None if OCR failed
        """
        # Preprocess
        processed = self.preprocess_roi(roi_img)

        # Run OCR
        if self.use_easyocr:
            try:
                results = self.reader.readtext(processed, detail=0)
                text = ' '.join(results) if results else ''
            except Exception as e:
                return None
        else:
            import pytesseract
            # Configure tesseract for digits
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789FPSfps.:, '
            text = pytesseract.image_to_string(processed, config=custom_config)

        # Parse FPS
        return self.extract_fps_from_text(text)

    def extract_from_video(
        self,
        video_path: Path,
        sample_rate: int = 1,
        preview_frame: int = 0
    ) -> Tuple[List[Dict], Optional[np.ndarray]]:
        """
        Extract FPS data from video

        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame (1 = every frame, 30 = every 30th frame)
            preview_frame: Frame number to extract as ROI preview (default: 0)

        Returns:
            Tuple of (fps_data_list, preview_image)
        """
        cap = cv2.VideoCapture(str(video_path))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"  Video: {total_frames} frames @ {video_fps:.2f} FPS")

        # Auto-detect ROI if not provided
        if self.roi is None:
            print("  Attempting auto-detection of FPS counter...")
            ret, first_frame = cap.read()
            if ret:
                self.roi = self.auto_detect_roi(first_frame, "top_right")
                if self.roi:
                    print(f"  ✓ Auto-detected ROI: x={self.roi[0]}, y={self.roi[1]}, w={self.roi[2]}, h={self.roi[3]}")
                else:
                    print("  ✗ Auto-detection failed. Please provide ROI manually with --roi")
                    cap.release()
                    return [], None
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning

        fps_data = []
        preview_image = None
        last_valid_fps = None
        consecutive_failures = 0

        with tqdm(total=total_frames // sample_rate, desc="Extracting FPS", unit="frame") as pbar:
            for frame_idx in range(0, total_frames, sample_rate):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()

                if not ret:
                    break

                # Extract ROI
                x, y, w, h = self.roi
                roi_img = frame[y:y+h, x:x+w]

                # Save preview
                if frame_idx == preview_frame:
                    preview_image = frame.copy()
                    cv2.rectangle(preview_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(preview_image, "FPS ROI", (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Extract FPS
                fps_value = self.read_fps_from_roi(roi_img)

                if fps_value is not None:
                    fps_data.append({
                        'frame': frame_idx,
                        'timestamp': frame_idx / video_fps,
                        'fps': fps_value
                    })
                    last_valid_fps = fps_value
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    # If OCR fails, use last valid value (common for brief frame drops)
                    if last_valid_fps is not None and consecutive_failures < 10:
                        fps_data.append({
                            'frame': frame_idx,
                            'timestamp': frame_idx / video_fps,
                            'fps': last_valid_fps,
                            'interpolated': True
                        })

                pbar.update(1)

        cap.release()

        return fps_data, preview_image

    def calculate_statistics(self, fps_data: List[Dict]) -> Dict:
        """
        Calculate FPS statistics from extracted data

        Args:
            fps_data: List of FPS measurements

        Returns:
            Dictionary with statistics
        """
        if not fps_data:
            return {}

        fps_values = [d['fps'] for d in fps_data]

        # Sort for percentile calculations
        sorted_fps = sorted(fps_values)

        return {
            'avg_fps': statistics.mean(fps_values),
            'median_fps': statistics.median(fps_values),
            'min_fps': min(fps_values),
            'max_fps': max(fps_values),
            'std_fps': statistics.stdev(fps_values) if len(fps_values) > 1 else 0,
            '1%_low': sorted_fps[int(len(sorted_fps) * 0.01)],
            '0.1%_low': sorted_fps[int(len(sorted_fps) * 0.001)],
            'frame_count': len(fps_data),
            'interpolated_count': sum(1 for d in fps_data if d.get('interpolated', False))
        }


def main():
    parser = argparse.ArgumentParser(
        description="Extract FPS data from on-screen display using OCR"
    )
    parser.add_argument(
        "--video",
        type=Path,
        required=True,
        help="Video file with FPS counter overlay"
    )
    parser.add_argument(
        "--roi",
        type=str,
        help="Region of interest as 'x,y,width,height' (e.g., '1700,50,200,80'). If omitted, will auto-detect."
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output JSON file"
    )
    parser.add_argument(
        "--preview",
        type=Path,
        help="Save preview image showing detected ROI"
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=1,
        help="Process every Nth frame (default: 1 = every frame)"
    )
    parser.add_argument(
        "--preview-frame",
        type=int,
        default=0,
        help="Frame number to use for ROI preview (default: 0)"
    )
    parser.add_argument(
        "--use-tesseract",
        action="store_true",
        help="Use Tesseract instead of EasyOCR"
    )

    args = parser.parse_args()

    try:
        print("=" * 60)
        print("FPS OCR Extractor".center(60))
        print("=" * 60)

        # Parse ROI
        roi = None
        if args.roi:
            try:
                x, y, w, h = map(int, args.roi.split(','))
                roi = (x, y, w, h)
                print(f"\n  Using ROI: x={x}, y={y}, w={w}, h={h}")
            except ValueError:
                print("\n  ✗ Invalid ROI format. Use: x,y,width,height")
                sys.exit(1)
        else:
            print("\n  No ROI specified, will attempt auto-detection")

        # Initialize extractor
        extractor = FPSOCRExtractor(roi=roi, use_easyocr=not args.use_tesseract)

        # Extract FPS data
        print("\n[1/2] Extracting FPS from video...")
        fps_data, preview_image = extractor.extract_from_video(
            args.video,
            sample_rate=args.sample_rate,
            preview_frame=args.preview_frame
        )

        if not fps_data:
            print("\n  ✗ No FPS data extracted. Check ROI and OCR setup.")
            sys.exit(1)

        print(f"  ✓ Extracted {len(fps_data)} FPS measurements")

        # Calculate statistics
        print("\n[2/2] Calculating statistics...")
        stats = extractor.calculate_statistics(fps_data)

        print(f"  ✓ Average FPS: {stats['avg_fps']:.1f}")
        print(f"  ✓ 1% Low: {stats['1%_low']:.1f}")
        print(f"  ✓ 0.1% Low: {stats['0.1%_low']:.1f}")

        if stats['interpolated_count'] > 0:
            print(f"  ⚠ {stats['interpolated_count']} frames interpolated due to OCR failures")

        # Save output
        output_data = {
            'video_path': str(args.video),
            'roi': extractor.roi,
            'statistics': stats,
            'fps_data': fps_data
        }

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n  ✓ Saved to: {args.output}")

        # Save preview
        if args.preview and preview_image is not None:
            cv2.imwrite(str(args.preview), preview_image)
            print(f"  ✓ Preview saved to: {args.preview}")

        print("\n" + "=" * 60)
        print("Extraction Complete!".center(60))
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
