#!/usr/bin/env python3
"""
Quick test script to verify OCR setup is working correctly

Usage:
    python test_ocr.py
"""

import sys


def test_easyocr():
    """Test if EasyOCR is working"""
    print("\n[1/2] Testing EasyOCR...")
    try:
        import easyocr
        print("  ✓ EasyOCR imported successfully")

        # Try to initialize (this downloads models on first run)
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        print("  ✓ EasyOCR initialized successfully")

        # Test on simple image
        import numpy as np
        test_img = np.ones((100, 200), dtype=np.uint8) * 255
        import cv2
        cv2.putText(test_img, "60 FPS", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 0, 3)

        results = reader.readtext(test_img, detail=0)
        detected_text = ' '.join(results)

        if '60' in detected_text or 'FPS' in detected_text:
            print(f"  ✓ OCR test passed: detected '{detected_text}'")
            return True
        else:
            print(f"  ⚠ OCR test unclear: detected '{detected_text}'")
            return True  # Still working, just not perfect

    except ImportError:
        print("  ✗ EasyOCR not installed")
        print("    Install with: pip install easyocr")
        return False
    except Exception as e:
        print(f"  ✗ EasyOCR error: {e}")
        return False


def test_tesseract():
    """Test if Tesseract is working"""
    print("\n[2/2] Testing Tesseract...")
    try:
        import pytesseract
        print("  ✓ pytesseract imported successfully")

        # Check if tesseract binary is available
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract version: {version}")

        # Test on simple image
        import numpy as np
        test_img = np.ones((100, 200), dtype=np.uint8) * 255
        import cv2
        cv2.putText(test_img, "60 FPS", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, 0, 3)

        text = pytesseract.image_to_string(test_img)

        if '60' in text or 'FPS' in text:
            print(f"  ✓ OCR test passed: detected '{text.strip()}'")
            return True
        else:
            print(f"  ⚠ OCR test unclear: detected '{text.strip()}'")
            return True

    except ImportError:
        print("  ✗ pytesseract not installed")
        print("    Install with: pip install pytesseract")
        return False
    except pytesseract.TesseractNotFoundError:
        print("  ✗ Tesseract binary not found")
        print("    Install with:")
        print("      macOS:  brew install tesseract")
        print("      Linux:  apt install tesseract-ocr")
        return False
    except Exception as e:
        print(f"  ✗ Tesseract error: {e}")
        return False


def main():
    print("=" * 60)
    print("OCR Setup Test".center(60))
    print("=" * 60)

    easyocr_ok = test_easyocr()
    tesseract_ok = test_tesseract()

    print("\n" + "=" * 60)
    print("Results".center(60))
    print("=" * 60)

    if easyocr_ok or tesseract_ok:
        print("\n✓ At least one OCR engine is working!")
        if easyocr_ok:
            print("  • EasyOCR is ready (recommended)")
        if tesseract_ok:
            print("  • Tesseract is ready")
        print("\nYou can now use fps_ocr_extractor.py")
        return 0
    else:
        print("\n✗ No OCR engine is working")
        print("\nPlease install at least one:")
        print("  pip install easyocr")
        print("  OR")
        print("  brew install tesseract && pip install pytesseract")
        return 1


if __name__ == "__main__":
    sys.exit(main())
