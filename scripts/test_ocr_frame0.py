#!/usr/bin/env python3
"""
Test OCR on specific frame ROI
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extraction.fps_ocr import FPSOCRExtractor
import cv2

# Load the saved ROI image
roi_img = cv2.imread("results/cyberpunk/debug_fps/frame_0_roi.png")

print("Testing OCR on frame 0 ROI...")
print(f"Image shape: {roi_img.shape}")

# Initialize extractor (no ROI needed since we're testing directly)
extractor = FPSOCRExtractor(roi=(0, 0, 288, 162), use_easyocr=True)

# Test OCR directly
fps_value = extractor.read_fps_from_roi(roi_img)

print(f"\nOCR Result: {fps_value}")

if fps_value is None:
    print("\n❌ OCR failed to extract FPS")
    print("Trying to see what text was detected...")

    # Get raw OCR output
    processed = extractor.preprocess_roi(roi_img)

    if extractor.use_easyocr:
        results = extractor.reader.readtext(processed, detail=0)
        raw_text = ' '.join(results) if results else ''
    else:
        import pytesseract
        raw_text = pytesseract.image_to_string(processed)

    print(f"Raw OCR text: '{raw_text}'")
else:
    print(f"✓ Successfully extracted: {fps_value} FPS")
