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
│   ├── download_dataset.py           # Download from HuggingFace
│   ├── upload_one_by_one.py          # Upload to HuggingFace
│   └── utils/                        # Utility scripts
│
├── src/                       # Core library
│   ├── run_analysis.py        # Generic analysis runner (config-driven)
│   ├── compare_alignment_quality.py  # Low-level comparison engine
│   ├── preprocessing/         # Video preprocessing (CFR conversion)
│   ├── extraction/            # FPS data extraction
│   ├── comparison/            # Image/video comparison
│   ├── sync/                  # Video synchronization
│   ├── analysis/              # Analysis tools
│   ├── metrics/               # Quality metrics (SSIM, PSNR, LPIPS, FLIP, VMAF)
│   ├── trim/                  # Video trimming (OCR-based)
│   └── validation/            # Benchmark validation
│
├── configs/                   # Analysis configuration files (YAML)
│   ├── analysis_retrimmed.yaml                    # Cyberpunk 2077 (re-trimmed)
│   ├── analysis_cyberpunk_low.yaml                # Cyberpunk 2077 (low graphics)
│   ├── analysis_tomb_raider_highest_scene_1.yaml  # Shadow of the Tomb Raider (highest graphics)
│   ├── analysis_blackmyth_medium.yaml             # Black Myth: Wukong (medium graphics)
│   ├── analysis_cod_mw2_extreme.yaml              # Call of Duty: MW2 (extreme graphics)
│   ├── analysis_forza_extreme.yaml                # Forza Horizon 5 (extreme graphics)
│   ├── analysis_marvel_rivals_low.yaml            # Marvel Rivals (low graphics)
│   ├── analysis_rdr2_ultra.yaml                   # Red Dead Redemption 2 (ultra graphics)
│   └── analysis_returnal_epic.yaml                # Returnal (epic graphics)
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

#### Step 6: Run Quality Analysis

The analysis system uses a generic, config-driven approach via YAML files:

```bash
# Run analysis with a configuration file
python src/run_analysis.py --config configs/analysis_retrimmed.yaml
```

**Configuration Format (YAML):**
```yaml
paths:
  base_dir: recordings/cyberpunk/trimmed
  results_dir: results/cyberpunk/analysis

settings:
  roi: "top-left 10%"           # FPS counter ROI
  sample_rate: 10                # Analyze every 10th frame
  compute_advanced: true         # Enable LPIPS, FLIP, Optical Flow
  use_gpu: true                  # Use GPU acceleration
  compute_vmaf: true             # Include VMAF metric
  extract_fps: true              # Extract FPS from overlay

comparisons:
  - reference: 1080p_dlaa_run1.mp4
    compare: 1080p_dlss_quality.mp4
    name: 1080p_DLAA_vs_Quality
```

**ROI Specification:**
- Pixel format: `"10,10,100,50"` (x,y,width,height)
- Percentage format: `"top-left 10%"` (recommended - resolution independent)

**Output:** Each comparison produces a JSON file with:
- Frame-by-frame metrics (SSIM, PSNR, LPIPS, FLIP, etc.)
- Extracted FPS data
- Execution time
- Summary statistics

**Creating New Analyses:**
1. Copy an existing config: `cp configs/analysis_retrimmed.yaml configs/my_analysis.yaml`
2. Edit paths, settings, and comparisons
3. Run: `python src/run_analysis.py --config configs/my_analysis.yaml`

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

## 🎬 Video Trimming Workflow

Videos recorded from games often include intro menus, loading screens, and result screens. The trimming workflow removes these non-gameplay sections using OCR-based marker detection.

### Why Trim Videos?

- **Remove non-gameplay content**: Menus, loading screens, benchmark result screens
- **Focus on gameplay**: Keep only frames where FPS counter is visible
- **Consistent duration**: All videos trimmed to the same gameplay section
- **Automated process**: No manual video editing required

### Step 1: Select ROI for Trimming

First, identify where the FPS counter appears on screen:

```bash
# Select the ROI for the FPS counter (for trimming)
python3 scripts/roi_selector.py \
    --video recordings/blackmyth_medium/1080p_dlaa_run1.mp4 \
    --roi-name trim \
    --marker-pattern "numeric"
```

This opens an interactive window where you:
1. Draw a rectangle around the FPS counter
2. Press 'SPACE' to confirm
3. The coordinates are saved to `recordings/blackmyth_medium/roi_trim_coordinates.yaml`

**Optional:** If you also need FPS extraction, create a separate ROI:
```bash
python3 scripts/roi_selector.py \
    --video recordings/blackmyth_medium/1080p_dlaa_run1.mp4 \
    --roi-name fps \
    --marker-pattern "numeric"
```

### Step 2: Trim Videos

Use the batch trimming script to process all videos automatically:

```bash
# Trim all videos in the directory using ROI config
python3 scripts/batch_trim.py \
    --input-dir recordings/blackmyth_medium \
    --roi-config recordings/blackmyth_medium/roi_trim_coordinates.yaml

# Custom output directory (optional)
python3 scripts/batch_trim.py \
    --input-dir recordings/blackmyth_medium \
    --roi-config recordings/blackmyth_medium/roi_trim_coordinates.yaml \
    --output-dir recordings/blackmyth_medium/custom_output
```

**What `batch_trim.py` does:**
- Finds all video files in the input directory (`.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`)
- Processes videos sequentially (one at a time)
- Creates `<input-dir>/trimmed/` directory automatically
- Provides progress updates for each video
- Shows summary of successful/failed trims at the end

**Alternative: Single Video Trimming**

To trim a single video manually:

```bash
python3 src/trim/trim_by_marker.py \
    --video recordings/blackmyth_medium/1080p_dlaa_run1.mp4 \
    --output recordings/blackmyth_medium/trimmed/1080p_dlaa_run1.mp4 \
    --roi-config recordings/blackmyth_medium/roi_trim_coordinates.yaml
```

**What `trim_by_marker.py` does:**
1. **Forward scan**: Finds first frame where FPS counter appears (gameplay starts)
2. **Backward scan**: Finds last frame where FPS counter is visible (gameplay ends)
3. **FFmpeg trim**: Extracts only the gameplay section using frame-accurate seeking
4. **Output**: High-quality trimmed video (CRF 18, libx264)

### Alternative: Manual ROI Specification

If you don't have a YAML config, you can specify ROI manually:

```bash
# Using percentage (resolution-independent, recommended)
python3 src/trim/trim_by_marker.py \
    --video recordings/blackmyth_medium/1080p_dlaa_run1.mp4 \
    --output recordings/blackmyth_medium/trimmed/1080p_dlaa_run1.mp4 \
    --roi "top-left 10%" \
    --marker-type fps

# Using pixel coordinates (resolution-specific)
python3 src/trim/trim_by_marker.py \
    --video recordings/blackmyth_medium/1080p_dlaa_run1.mp4 \
    --output recordings/blackmyth_medium/trimmed/1080p_dlaa_run1.mp4 \
    --roi "0,0,192,108" \
    --marker-type fps
```

### ROI Config Format

The `roi_trim_coordinates.yaml` file contains:

```yaml
roi_name: trim
video_info:
  source: 1080p_dlaa_run1.mp4
  resolution: 1920x1080
  frame_index: 4090
  timestamp: 68.2s
roi:
  pixels: 885,1013,155,61
marker:
  type: fps
  pattern: numeric
  regex: \d+\.?\d*
  description: Numeric FPS counter
```

The ROI is automatically scaled for different resolutions (e.g., 1080p ROI → 4K ROI).

### Performance Notes

- **Forward scan**: ~10-20 frames/second (OCR on every frame)
- **Backward scan**: Slower due to random seeking (especially for 4K videos)
- **Total time**: ~2-5 minutes per 1080p video, ~15-30 minutes per 4K video
- **Recommendation**: Process videos sequentially to avoid memory issues with large 4K files

### Dry Run Mode

Test trimming detection without actually trimming:

```bash
python3 src/trim/trim_by_marker.py \
    --video recordings/blackmyth_medium/1080p_dlaa_run1.mp4 \
    --output recordings/blackmyth_medium/trimmed/1080p_dlaa_run1.mp4 \
    --roi-config recordings/blackmyth_medium/roi_trim_coordinates.yaml \
    --dry-run
```

This shows you the detected frame range without creating the output file.

## 📖 Documentation

See `/tcc/claude/` for detailed guides.
