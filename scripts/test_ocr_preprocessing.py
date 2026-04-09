#!/usr/bin/env python3
"""
Test OCR with different preprocessing options
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import re

# Load frame 0 ROI
roi_img = cv2.imread("results/cyberpunk/debug_fps/frame_0_roi.png")

# Initialize EasyOCR
try:
    import easyocr
    reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    print("✓ EasyOCR initialized\n")
except ImportError:
    print("EasyOCR not available")
    sys.exit(1)

def test_ocr(img, description):
    results = reader.readtext(img, detail=0)
    text = ' '.join(results) if results else ''
    print(f"{description}:")
    print(f"  Raw text: '{text}'")

    # Try to extract FPS
    # Pattern: find all numbers
    numbers = re.findall(r'\d+', text)
    print(f"  Numbers found: {numbers}")

    # Find the largest number (likely the FPS value)
    if numbers:
        fps_candidates = [int(n) for n in numbers if 10 <= int(n) <= 300]
        if fps_candidates:
            print(f"  Valid FPS candidates: {fps_candidates}")
            print(f"  → Using: {max(fps_candidates)}\n")
        else:
            print(f"  → No valid FPS found\n")
    else:
        print(f"  → No numbers found\n")

# Test 1: Original image (no preprocessing)
print("="*60)
test_ocr(roi_img, "Test 1: Original RGB image")

# Test 2: Grayscale only
gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
test_ocr(gray, "Test 2: Grayscale")

# Test 3: Simple threshold
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
test_ocr(binary, "Test 3: Binary threshold (127)")

# Test 4: Otsu threshold
_, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
test_ocr(otsu, "Test 4: Otsu threshold")

# Test 5: Inverted Otsu
_, otsu_inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
test_ocr(otsu_inv, "Test 5: Inverted Otsu threshold")
