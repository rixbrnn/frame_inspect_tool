#!/usr/bin/env python3
"""
FPS Extractor - Multiple methods for extracting FPS from game recordings
"""

import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import json

class FPSExtractor:
    """Extract FPS data from various sources"""

    def __init__(self):
        self.fps_data = {}

    # Method 1: Parse FrameView CSV
    def from_frameview(self, csv_path: str) -> Dict:
        """
        Parse NVIDIA FrameView CSV export

        Returns:
            {
                'avg_fps': float,
                '1%_low': float,
                '0.1%_low': float,
                'min_fps': float,
                'max_fps': float,
                'fps_by_second': [float, ...],
                'frame_times_ms': [float, ...]
            }
        """
        df = pd.read_csv(csv_path)

        # FrameView CSV columns: Time, Application, MsBetweenPresents, FPS
        fps_values = df['FPS'].values

        result = {
            'source': 'frameview',
            'avg_fps': float(fps_values.mean()),
            '1%_low': float(np.percentile(fps_values, 1)),
            '0.1%_low': float(np.percentile(fps_values, 0.1)),
            'min_fps': float(fps_values.min()),
            'max_fps': float(fps_values.max()),
            'std_dev': float(fps_values.std()),
            'frame_times_ms': df['MsBetweenPresents'].values.tolist()
        }

        # FPS by second (useful for correlating with video)
        df['second'] = (df['Time'] // 1.0).astype(int)
        result['fps_by_second'] = df.groupby('second')['FPS'].mean().to_dict()

        return result

    # Method 2: Parse CapFrameX JSON
    def from_capframex(self, json_path: str) -> Dict:
        """
        Parse CapFrameX JSON export

        Returns: Same format as from_frameview()
        """
        with open(json_path, 'r') as f:
            data = json.load(f)

        # CapFrameX format varies, adjust as needed
        fps_values = np.array(data.get('FPS', []))

        return {
            'source': 'capframex',
            'avg_fps': float(fps_values.mean()),
            '1%_low': float(np.percentile(fps_values, 1)),
            '0.1%_low': float(np.percentile(fps_values, 0.1)),
            'min_fps': float(fps_values.min()),
            'max_fps': float(fps_values.max()),
            'std_dev': float(fps_values.std())
        }

    # Method 3: OCR from video overlay
    def from_overlay_ocr(self, video_path: str, roi: tuple,
                         sample_rate: int = 30) -> Dict:
        """
        Extract FPS from on-screen overlay using OCR

        Args:
            video_path: Path to video file
            roi: (x, y, width, height) - region of FPS counter
            sample_rate: Process every Nth frame (default: 30)

        Returns: Same format as from_frameview()

        NOTE: Requires pytesseract installed
        """
        try:
            import pytesseract
        except ImportError:
            raise ImportError("pytesseract not installed. Install with: pip install pytesseract")

        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)

        fps_readings = []
        frame_count = 0

        x, y, w, h = roi

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Sample every Nth frame for performance
            if frame_count % sample_rate == 0:
                # Extract FPS counter region
                fps_region = frame[y:y+h, x:x+w]

                # Preprocess for better OCR
                gray = cv2.cvtColor(fps_region, cv2.COLOR_BGR2GRAY)
                # Assuming yellow text on dark background
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

                # OCR configuration for digits
                config = '--psm 7 -c tessedit_char_whitelist=0123456789.'
                text = pytesseract.image_to_string(thresh, config=config)

                try:
                    fps = float(text.strip().replace('O', '0').replace('o', '0'))
                    if 10 < fps < 300:  # Sanity check
                        fps_readings.append(fps)
                except:
                    pass  # Skip failed reads

            frame_count += 1

        cap.release()

        if not fps_readings:
            raise ValueError("No FPS readings extracted. Check ROI coordinates.")

        fps_array = np.array(fps_readings)

        return {
            'source': 'overlay_ocr',
            'avg_fps': float(fps_array.mean()),
            '1%_low': float(np.percentile(fps_array, 1)),
            '0.1%_low': float(np.percentile(fps_array, 0.1)),
            'min_fps': float(fps_array.min()),
            'max_fps': float(fps_array.max()),
            'std_dev': float(fps_array.std()),
            'sample_count': len(fps_readings),
            'warning': 'OCR-based, may have reading errors'
        }

    # Method 4: Manual CSV input
    def from_manual_csv(self, csv_path: str) -> Dict:
        """
        Load manually entered FPS data

        CSV format:
            mode,avg_fps,1%_low,0.1%_low
            DLAA_4K,58.3,52.1,48.7
            Quality,72.5,65.3,61.2

        Returns: Dict of {mode_name: fps_data}
        """
        df = pd.read_csv(csv_path)
        results = {}

        for _, row in df.iterrows():
            mode = row['mode']
            results[mode] = {
                'source': 'manual',
                'avg_fps': float(row['avg_fps']),
                '1%_low': float(row.get('1%_low', row['avg_fps'])),
                '0.1%_low': float(row.get('0.1%_low', row['avg_fps']))
            }

        return results

    # Helper: Detect FPS overlay region automatically
    def detect_overlay_region(self, video_path: str,
                               sample_frame: int = 60) -> Optional[tuple]:
        """
        Attempt to auto-detect FPS overlay region

        Looks for yellow/white text in corners (common OSD locations)

        Returns: (x, y, width, height) or None
        """
        cap = cv2.VideoCapture(video_path)

        # Jump to sample frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, sample_frame)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None

        # Convert to HSV to detect yellow text (MSI Afterburner default)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Yellow color range
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Get bounding box of largest contour
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)

            # Expand slightly for safety
            padding = 5
            return (max(0, x-padding), max(0, y-padding),
                    w+2*padding, h+2*padding)

        return None


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Extract FPS from recordings')
    parser.add_argument('--source', required=True, help='Data source file')
    parser.add_argument('--type', choices=['frameview', 'capframex', 'overlay', 'manual'],
                        default='frameview', help='Source type')
    parser.add_argument('--roi', type=str, help='ROI for overlay (x,y,w,h)')
    parser.add_argument('--output', help='Output JSON file')

    args = parser.parse_args()

    extractor = FPSExtractor()

    if args.type == 'frameview':
        data = extractor.from_frameview(args.source)
    elif args.type == 'capframex':
        data = extractor.from_capframex(args.source)
    elif args.type == 'overlay':
        if not args.roi:
            print("Attempting auto-detection...")
            roi = extractor.detect_overlay_region(args.source)
            if roi:
                print(f"Detected ROI: {roi}")
            else:
                print("Auto-detection failed. Please specify --roi x,y,w,h")
                exit(1)
        else:
            roi = tuple(map(int, args.roi.split(',')))
        data = extractor.from_overlay_ocr(args.source, roi)
    elif args.type == 'manual':
        data = extractor.from_manual_csv(args.source)

    print(json.dumps(data, indent=2))

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved to {args.output}")
