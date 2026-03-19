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
import os
from datetime import datetime

class FPSExtractor:
    """Extract FPS data from various sources"""

    def __init__(self):
        self.fps_data = {}

    # Method 1: Parse FrameView CSV
    def from_frameview(self, csv_path: str, video_path: Optional[str] = None,
                       start_time: Optional[float] = None,
                       end_time: Optional[float] = None) -> Dict:
        """
        Parse NVIDIA FrameView CSV export with automatic video sync

        Args:
            csv_path: Path to FrameView CSV file
            video_path: Optional video file to auto-sync timestamps
            start_time: Manual start time in seconds (overrides auto-sync)
            end_time: Manual end time in seconds (overrides auto-sync)

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

        # Auto-sync with video if provided
        if video_path and start_time is None:
            start_time, end_time = self._sync_frameview_with_video(
                csv_path, video_path, df
            )
            if start_time is not None:
                print(f"Auto-detected video segment: {start_time:.2f}s - {end_time:.2f}s")

        # Filter by time range if provided
        if start_time is not None:
            df = df[df['Time'] >= start_time]
        if end_time is not None:
            df = df[df['Time'] <= end_time]

        if len(df) == 0:
            raise ValueError("No data in specified time range")

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
            'frame_times_ms': df['MsBetweenPresents'].values.tolist(),
            'duration_seconds': float(df['Time'].max() - df['Time'].min())
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


    def _sync_frameview_with_video(self, csv_path: str, video_path: str,
                                     df: pd.DataFrame) -> tuple:
        """
        Automatically sync FrameView CSV with video recording

        Strategy:
        1. Get video file creation time and duration
        2. Get CSV file creation time
        3. Calculate time offset between them
        4. Find CSV rows that correspond to video duration

        Returns: (start_time, end_time) in CSV time units, or (None, None)
        """
        try:
            # Get video metadata
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            video_duration = frame_count / video_fps if video_fps > 0 else 0
            cap.release()

            # Get file creation times
            video_stat = os.stat(video_path)
            csv_stat = os.stat(csv_path)

            # Use modification time as proxy for recording time
            video_created = video_stat.st_mtime
            csv_created = csv_stat.st_mtime

            # Calculate offset: how many seconds into the CSV does the video start?
            # If video was created AFTER CSV started logging, offset is positive
            time_offset = video_created - csv_created

            # Find CSV rows that match video duration
            # FrameView's Time column is elapsed seconds from start
            csv_start_time = df['Time'].min()
            csv_total_duration = df['Time'].max() - csv_start_time

            # If time_offset is reasonable (video started during CSV logging)
            if 0 <= time_offset <= csv_total_duration:
                start_time = csv_start_time + time_offset
                end_time = start_time + video_duration

                # Validate that this range exists in CSV
                matching_rows = df[(df['Time'] >= start_time) &
                                  (df['Time'] <= end_time)]

                if len(matching_rows) > 10:  # At least 10 samples
                    return (start_time, end_time)

            # Fallback: If timestamps don't align, try heuristic approach
            # Look for a segment matching video duration
            return self._find_segment_by_duration(df, video_duration)

        except Exception as e:
            print(f"Auto-sync failed: {e}. Using full CSV data.")
            return (None, None)


    def _find_segment_by_duration(self, df: pd.DataFrame,
                                   target_duration: float) -> tuple:
        """
        Find a segment in the CSV matching the target duration

        Heuristic: Look for the most stable FPS segment of the right length
        """
        csv_duration = df['Time'].max() - df['Time'].min()

        # If CSV is close to target duration, use entire CSV
        if abs(csv_duration - target_duration) < 5.0:  # Within 5 seconds
            return (df['Time'].min(), df['Time'].max())

        # Otherwise, try to find a stable segment
        # (This is a fallback - manual trimming is more accurate)
        print(f"Warning: Could not auto-sync. CSV duration: {csv_duration:.1f}s, "
              f"Video duration: {target_duration:.1f}s")
        print("Consider using --start-time and --end-time for manual sync.")

        return (None, None)


    # Method 5: Hybrid FrameView + Overlay Validation
    def from_frameview_validated(self, csv_path: str, video_path: str,
                                  roi: Optional[tuple] = None,
                                  sample_rate: int = 30,
                                  tolerance: float = 5.0) -> Dict:
        """
        Extract FPS from FrameView CSV and validate against video overlay

        This hybrid method:
        1. Extracts FPS from FrameView CSV (primary source)
        2. Samples overlay from video via OCR (validation)
        3. Compares both sources and warns if discrepancies found
        4. Returns FrameView data with validation metrics

        Args:
            csv_path: Path to FrameView CSV
            video_path: Path to video with FPS overlay
            roi: (x, y, width, height) for overlay region (auto-detected if None)
            sample_rate: Check overlay every Nth frame (default: 30)
            tolerance: Max acceptable FPS difference % (default: 5.0%)

        Returns:
            FrameView data dict + validation info:
            {
                ...standard FrameView output...,
                'validation': {
                    'overlay_samples': int,
                    'avg_difference': float,
                    'max_difference': float,
                    'discrepancy_detected': bool,
                    'warnings': [str, ...]
                }
            }
        """
        print("Running hybrid extraction (FrameView + Overlay validation)...")

        # Step 1: Extract from FrameView (with auto-sync)
        print("\n[1/3] Extracting from FrameView CSV...")
        frameview_data = self.from_frameview(csv_path, video_path=video_path)

        # Step 2: Auto-detect overlay region if not provided
        if roi is None:
            print("\n[2/3] Auto-detecting FPS overlay region...")
            roi = self.detect_overlay_region(video_path)
            if roi:
                print(f"✓ Detected overlay at: x={roi[0]}, y={roi[1]}, w={roi[2]}, h={roi[3]}")
            else:
                print("✗ Could not auto-detect overlay. Skipping validation.")
                frameview_data['validation'] = {
                    'overlay_samples': 0,
                    'warnings': ['Could not detect FPS overlay for validation']
                }
                return frameview_data

        # Step 3: Sample overlay FPS from video
        print(f"\n[3/3] Sampling overlay FPS (every {sample_rate} frames)...")
        overlay_samples = self._sample_overlay_fps(video_path, roi, sample_rate)

        if not overlay_samples:
            print("✗ No overlay readings extracted. Validation skipped.")
            frameview_data['validation'] = {
                'overlay_samples': 0,
                'warnings': ['OCR failed to read overlay. Check ROI or overlay visibility.']
            }
            return frameview_data

        # Step 4: Compare FrameView vs Overlay
        print(f"✓ Extracted {len(overlay_samples)} overlay samples")
        validation = self._validate_fps_sources(
            frameview_data, overlay_samples, tolerance
        )

        frameview_data['validation'] = validation

        # Print validation summary
        print("\n" + "="*60)
        print("VALIDATION RESULTS")
        print("="*60)
        print(f"Overlay samples:     {validation['overlay_samples']}")
        print(f"Avg difference:      {validation['avg_difference']:.2f} FPS ({validation['avg_difference_percent']:.1f}%)")
        print(f"Max difference:      {validation['max_difference']:.2f} FPS")
        print(f"Discrepancy:         {'⚠️  YES' if validation['discrepancy_detected'] else '✓ NO'}")

        if validation['warnings']:
            print("\nWarnings:")
            for warning in validation['warnings']:
                print(f"  ⚠️  {warning}")

        print("="*60 + "\n")

        return frameview_data


    def _sample_overlay_fps(self, video_path: str, roi: tuple,
                            sample_rate: int) -> List[float]:
        """
        Sample FPS overlay from video using OCR

        Returns: List of FPS readings
        """
        try:
            import pytesseract
        except ImportError:
            print("⚠️  pytesseract not installed. Install with: pip install pytesseract")
            return []

        cap = cv2.VideoCapture(video_path)
        fps_readings = []
        frame_count = 0
        x, y, w, h = roi

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % sample_rate == 0:
                fps_region = frame[y:y+h, x:x+w]
                gray = cv2.cvtColor(fps_region, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

                config = '--psm 7 -c tessedit_char_whitelist=0123456789.'
                text = pytesseract.image_to_string(thresh, config=config)

                try:
                    fps = float(text.strip().replace('O', '0').replace('o', '0'))
                    if 10 < fps < 300:  # Sanity check
                        fps_readings.append(fps)
                except:
                    pass

            frame_count += 1

        cap.release()
        return fps_readings


    def _validate_fps_sources(self, frameview_data: Dict,
                               overlay_samples: List[float],
                               tolerance: float) -> Dict:
        """
        Compare FrameView CSV data with overlay OCR samples

        Returns validation metrics dict
        """
        frameview_avg = frameview_data['avg_fps']
        overlay_avg = np.mean(overlay_samples)

        # Calculate differences
        avg_diff = abs(frameview_avg - overlay_avg)
        avg_diff_percent = (avg_diff / frameview_avg) * 100

        # Find max difference by comparing overlay samples to FrameView average
        differences = [abs(sample - frameview_avg) for sample in overlay_samples]
        max_diff = max(differences) if differences else 0

        # Detect discrepancies
        discrepancy = avg_diff_percent > tolerance
        warnings = []

        if discrepancy:
            warnings.append(
                f"FrameView avg ({frameview_avg:.1f}) differs from overlay avg ({overlay_avg:.1f}) "
                f"by {avg_diff_percent:.1f}% (tolerance: {tolerance}%)"
            )

        # Check for outliers in overlay samples
        overlay_std = np.std(overlay_samples)
        if overlay_std > 10.0:
            warnings.append(
                f"High variance in overlay readings (std={overlay_std:.1f}). "
                f"OCR may be unreliable."
            )

        # Check sample size
        if len(overlay_samples) < 10:
            warnings.append(
                f"Low sample count ({len(overlay_samples)}). "
                f"Consider lower sample_rate for more validation points."
            )

        return {
            'overlay_samples': len(overlay_samples),
            'overlay_avg_fps': float(overlay_avg),
            'overlay_std_fps': float(overlay_std),
            'avg_difference': float(avg_diff),
            'avg_difference_percent': float(avg_diff_percent),
            'max_difference': float(max_diff),
            'discrepancy_detected': discrepancy,
            'warnings': warnings
        }


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Extract FPS from recordings')
    parser.add_argument('--source', required=True, help='Data source file')
    parser.add_argument('--type', choices=['frameview', 'capframex', 'overlay', 'manual', 'validated'],
                        default='frameview', help='Source type')
    parser.add_argument('--video', help='Video file for auto-sync or validation')
    parser.add_argument('--start-time', type=float, help='Manual start time in seconds')
    parser.add_argument('--end-time', type=float, help='Manual end time in seconds')
    parser.add_argument('--roi', type=str, help='ROI for overlay (x,y,w,h)')
    parser.add_argument('--sample-rate', type=int, default=30,
                        help='Sample overlay every N frames (validated mode only)')
    parser.add_argument('--tolerance', type=float, default=5.0,
                        help='Max acceptable FPS difference %% for validation')
    parser.add_argument('--output', help='Output JSON file')

    args = parser.parse_args()

    extractor = FPSExtractor()

    if args.type == 'frameview':
        data = extractor.from_frameview(
            args.source,
            video_path=args.video,
            start_time=args.start_time,
            end_time=args.end_time
        )
    elif args.type == 'validated':
        if not args.video:
            print("Error: --video is required for validated mode")
            exit(1)
        roi = tuple(map(int, args.roi.split(','))) if args.roi else None
        data = extractor.from_frameview_validated(
            args.source,
            args.video,
            roi=roi,
            sample_rate=args.sample_rate,
            tolerance=args.tolerance
        )
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
