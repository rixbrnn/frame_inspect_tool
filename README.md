# Frame Inspect Tool

A comprehensive toolkit for analyzing DLSS quality vs performance trade-offs through automated video comparison, FPS extraction via OCR, and temporal correlation analysis.

## 📊 Public Dataset Available

Pre-recorded benchmark data is available on Hugging Face:

**🤗 Dataset:** https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data

**📦 Tool Repository:** https://github.com/rixbrnn/frame_inspect_tool

Download the dataset to reproduce results or analyze existing recordings:
```bash
# Download all data
python scripts/download_dataset.py

# Download specific game
python scripts/download_dataset.py --game cyberpunk2077 --resolution 1080p

# List available recordings
python scripts/download_dataset.py --list
```

## 📁 Project Structure

```
frame_inspect_tool/
├── scripts/                   # User-facing CLI tools
│   ├── validate_benchmark.py          # Phase 0: Validate benchmark stability
│   ├── calibrate_fps_roi.py          # Setup: Calibrate FPS counter region
│   ├── convert_to_cfr.py             # Preprocessing: Convert to CFR
│   ├── test_ocr.py                   # Setup: Test OCR installation
│   ├── pipeline.py                   # Main: Full automation pipeline
│   └── utils/                        # Utility scripts
│
├── src/                       # Core library
│   ├── preprocessing/         # Video preprocessing (CFR conversion)
│   ├── extraction/            # FPS data extraction
│   ├── comparison/            # Image/video comparison
│   ├── sync/                  # Video synchronization
│   ├── analysis/              # Analysis tools
│   └── validation/            # Benchmark validation
│
└── tests/                     # Unit tests
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install system dependencies
brew install ffmpeg  # macOS
# or
apt install ffmpeg  # Linux

# Install Python dependencies
pip install -r requirements.txt
pip install easyocr  # For FPS extraction
```

### Complete Workflow

#### Step 0: Set Up Recording Directory

```bash
# Create organized structure for your game and resolution
python scripts/setup_recording.py --game cyberpunk2077 --resolution 1080p
```

This creates:
```
recordings/cyberpunk2077/
├── 1080p/
│   ├── validation/    # Phase 0: Benchmark stability check
│   ├── raw/           # Phase 1: Original recordings
│   ├── processed/     # Phase 2: CFR 60 FPS versions
│   ├── extracted/     # Phase 3: OCR FPS data
│   ├── results/       # Phase 4: Analysis results
│   └── metadata.json  # Recording info (UPDATE THIS!)
└── fps_roi.json       # FPS counter location (calibrate once)
```

#### Step 1: Validate Benchmark Stability

**Before collecting any DLSS data**, validate that your benchmark is deterministic:

```bash
# Record the same benchmark twice, then validate
python scripts/validate_benchmark.py \
    --video1 recordings/cyberpunk2077/1080p/validation/run1.mp4 \
    --video2 recordings/cyberpunk2077/1080p/validation/run2.mp4 \
    --game "Cyberpunk 2077" \
    --output recordings/cyberpunk2077/1080p/validation/validation.json
```

**What this does:**
1. Converts both videos to CFR 60 FPS (creates `*_60fps.mp4` files)
2. Synchronizes them using perceptual hashing (finds overlapping section)
3. Compares aligned frames with SSIM

**Acceptance criteria:** SSIM ≥ 99% (from methodology)

If SSIM < 99%, the benchmark contains non-deterministic elements (random AI, physics, etc.) and should NOT be used for DLSS comparison.

#### Step 2: Calibrate FPS Counter ROI

Once per game (ROI is shared across resolutions):

```bash
python scripts/calibrate_fps_roi.py \
    --video recordings/cyberpunk2077/1080p/validation/run1.mp4 \
    --output recordings/cyberpunk2077/fps_roi.json
```

#### Step 3: Record All DLSS Modes

Record each mode, save to `recordings/<game>/<resolution>/raw/`:
- DLAA.mp4
- Quality.mp4
- Balanced.mp4
- Performance.mp4
- UltraPerformance.mp4

#### Step 4: Convert to CFR

```bash
for mode in DLAA Quality Balanced Performance UltraPerformance; do
    python scripts/convert_to_cfr.py \
        recordings/cyberpunk2077/1080p/raw/${mode}.mp4 \
        --output recordings/cyberpunk2077/1080p/processed/${mode}_60fps.mp4
done
```

#### Step 5: Extract FPS Data

```bash
# Extract FPS from each recording using OCR
python scripts/extract_fps.py \
    --video recordings/cyberpunk2077/1080p/processed/DLAA_60fps.mp4 \
    --roi recordings/cyberpunk2077/fps_roi.json \
    --output recordings/cyberpunk2077/1080p/extracted/DLAA_fps.json
# Repeat for other modes...
```

#### Step 6: Run Full Analysis

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
