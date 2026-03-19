# Recordings Directory Structure

This directory contains all benchmark recordings organized by game and resolution.

## Directory Structure

```
recordings/
├── <game_name>/
│   ├── <resolution>/
│   │   ├── validation/           # Phase 0: Benchmark stability
│   │   │   ├── run1_60fps.mp4
│   │   │   ├── run2_60fps.mp4
│   │   │   └── validation.json
│   │   │
│   │   ├── raw/                  # Phase 1: Raw recordings (optional backup)
│   │   │   ├── DLAA.mp4
│   │   │   ├── Quality.mp4
│   │   │   ├── Balanced.mp4
│   │   │   ├── Performance.mp4
│   │   │   └── UltraPerformance.mp4
│   │   │
│   │   ├── processed/            # Phase 2: CFR 60 FPS versions
│   │   │   ├── DLAA_60fps.mp4
│   │   │   ├── Quality_60fps.mp4
│   │   │   ├── Balanced_60fps.mp4
│   │   │   ├── Performance_60fps.mp4
│   │   │   └── UltraPerformance_60fps.mp4
│   │   │
│   │   ├── extracted/            # Phase 3: Extracted FPS data
│   │   │   ├── DLAA_fps.json
│   │   │   ├── Quality_fps.json
│   │   │   ├── Balanced_fps.json
│   │   │   ├── Performance_fps.json
│   │   │   └── UltraPerformance_fps.json
│   │   │
│   │   ├── results/              # Phase 4: Analysis results
│   │   │   ├── quality_comparison.csv
│   │   │   ├── sync_info.json
│   │   │   └── tradeoff_analysis.json
│   │   │
│   │   └── metadata.json         # Recording session metadata
│   │
│   └── fps_roi.json              # FPS counter ROI (shared across resolutions)
│
└── README.md                     # This file
```

## Example Structure

```
recordings/
├── cyberpunk2077/
│   ├── 1080p/
│   │   ├── validation/
│   │   ├── processed/
│   │   ├── extracted/
│   │   ├── results/
│   │   └── metadata.json
│   ├── 1440p/
│   │   └── ...
│   ├── 4k/
│   │   └── ...
│   └── fps_roi.json
│
├── blackmyth/
│   ├── 1080p/
│   ├── 1440p/
│   ├── 4k/
│   └── fps_roi.json
│
└── eldenring/
    ├── 1080p/
    ├── 1440p/
    └── fps_roi.json
```

## Naming Conventions

### Game Names
- Use lowercase, no spaces
- Use full name or common abbreviation
- Examples: `cyberpunk2077`, `blackmyth`, `eldenring`, `rdr2`

### Resolutions
- Use standard names: `1080p`, `1440p`, `4k`
- Alternative: `1920x1080`, `2560x1440`, `3840x2160`

### DLSS Modes
- `DLAA` - Deep Learning Anti-Aliasing (baseline quality)
- `Quality` - DLSS Quality mode
- `Balanced` - DLSS Balanced mode
- `Performance` - DLSS Performance mode
- `UltraPerformance` - DLSS Ultra Performance mode

### File Suffixes
- `_60fps.mp4` - CFR 60 FPS processed video
- `_fps.json` - Extracted FPS data from OCR
- `run1`, `run2` - Validation recordings

## Metadata Files

### metadata.json (per resolution)
```json
{
  "game": "cyberpunk2077",
  "resolution": "1080p",
  "recording_date": "2026-03-19",
  "system": {
    "gpu": "RTX 4090",
    "cpu": "AMD Ryzen 9 7950X",
    "ram": "32GB DDR5-6000",
    "driver": "566.03"
  },
  "game_settings": {
    "preset": "Ultra",
    "ray_tracing": "Ultra",
    "dlss_frame_generation": false
  },
  "benchmark": {
    "name": "Benchmark scene name or description",
    "duration": 60,
    "validated": true,
    "ssim": 99.34
  }
}
```

### validation.json
```json
{
  "date": "2026-03-19",
  "video1": "run1_60fps.mp4",
  "video2": "run2_60fps.mp4",
  "results": {
    "avg_ssim": 99.34,
    "threshold": 99.0,
    "is_stable": true
  },
  "verdict": "ACCEPT"
}
```

### fps_roi.json (per game, shared across resolutions)
```json
{
  "game": "cyberpunk2077",
  "roi": {
    "x": 50,
    "y": 50,
    "width": 120,
    "height": 40
  },
  "notes": "MSI Afterburner FPS counter, top-left corner",
  "tested_resolutions": ["1080p", "1440p", "4k"]
}
```

## Workflow Commands

### 1. Validate Benchmark
```bash
python scripts/validate_benchmark.py \
    --video1 recordings/cyberpunk2077/1080p/validation/run1.mp4 \
    --video2 recordings/cyberpunk2077/1080p/validation/run2.mp4 \
    --game "Cyberpunk 2077" \
    --output recordings/cyberpunk2077/1080p/validation/validation.json
```

### 2. Convert All Recordings to CFR
```bash
for mode in DLAA Quality Balanced Performance UltraPerformance; do
    python scripts/convert_to_cfr.py \
        recordings/cyberpunk2077/1080p/raw/${mode}.mp4 \
        --output recordings/cyberpunk2077/1080p/processed/${mode}_60fps.mp4
done
```

### 3. Calibrate FPS ROI (once per game)
```bash
python scripts/calibrate_fps_roi.py \
    --video recordings/cyberpunk2077/1080p/processed/DLAA_60fps.mp4 \
    --output recordings/cyberpunk2077/fps_roi.json
```

### 4. Extract FPS Data
```bash
python scripts/extract_fps.py \
    --video recordings/cyberpunk2077/1080p/processed/DLAA_60fps.mp4 \
    --roi recordings/cyberpunk2077/fps_roi.json \
    --output recordings/cyberpunk2077/1080p/extracted/DLAA_fps.json
```

## Storage Recommendations

### Local Development
- Keep `processed/` and `extracted/` for active work
- `raw/` is optional (can delete after CFR conversion to save space)

### Git Repository
- **DO NOT** commit video files (.mp4)
- **DO** commit metadata files (.json)
- Add to `.gitignore`:
  ```
  recordings/**/*.mp4
  recordings/**/*.avi
  recordings/**/*.mkv
  ```

### Zenodo Upload Structure
```
dataset_v1.0.zip
├── README.md
├── methodology.pdf
└── data/
    ├── cyberpunk2077/
    │   ├── 1080p/
    │   │   ├── processed/
    │   │   ├── extracted/
    │   │   ├── results/
    │   │   └── metadata.json
    │   └── fps_roi.json
    └── blackmyth/
        └── ...
```

## Notes

- Each game/resolution combination should have its own complete workflow
- ROI coordinates may differ slightly between resolutions (recalibrate if needed)
- Validation must pass (SSIM ≥ 99%) before proceeding to full data collection
- Keep metadata.json updated with system specs and game settings for reproducibility
