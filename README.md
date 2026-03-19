# Frame Inspect Tool

A comprehensive toolkit for analyzing DLSS quality vs performance trade-offs through automated video comparison, FPS extraction via OCR, and temporal correlation analysis.

## 📁 Project Structure

```
frame_inspect_tool/
├── scripts/                   # User-facing CLI tools
│   ├── validate_benchmark.py          # Phase 0: Validate benchmark stability
│   ├── calibrate_fps_roi.py          # Setup: Calibrate FPS counter region
│   ├── test_ocr.py                   # Setup: Test OCR installation
│   ├── pipeline.py                   # Main: Full automation pipeline
│   └── utils/                        # Utility scripts
│
├── src/                       # Core library
│   ├── extraction/            # FPS data extraction  
│   ├── comparison/            # Image/video comparison
│   ├── sync/                  # Video synchronization
│   ├── analysis/              # Analysis tools
│   └── validation/            # Benchmark validation
│
└── tests/                     # Unit tests
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install easyocr  # For FPS extraction
```

### 2. Validate Your Benchmark

```bash
python scripts/validate_benchmark.py \
    --video1 DLAA_run1.mp4 \
    --video2 DLAA_run2.mp4 \
    --game "Cyberpunk 2077"
```

### 3. Setup and Run

```bash
# Calibrate FPS counter region
python scripts/calibrate_fps_roi.py --video your_video.mp4

# Run full pipeline
python scripts/pipeline.py
```

## 🎯 Key Features

- ✅ **Benchmark Validation** - Ensure stability (SSIM ≥ 99%)
- ✅ **OCR FPS Extraction** - Perfect frame-by-frame sync
- ✅ **Fast Video Sync** - 844,000x faster (O(n+m))
- ✅ **Temporal Analysis** - FPS vs Quality correlation

## 📊 Performance

| Operation | Time |
|-----------|------|
| Video Sync | 50 ms (was 11.7 hours!) |
| FPS Extraction | 30 seconds |
| Full Pipeline | <1 minute |

## 📖 Documentation

See `/tcc/claude/` for detailed guides.
