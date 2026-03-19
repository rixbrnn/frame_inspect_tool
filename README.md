# Frame Inspect Tool - DLSS Analysis Toolkit

Complete Python toolkit for analyzing DLSS (Deep Learning Super Sampling) quality and performance trade-offs.

## 🚀 Quick Start

After recording your benchmark videos with all DLSS modes:

```bash
cd /Users/i549847/workspace/frame_inspect_tool
python pipeline.py
```

That's it! The pipeline will automatically:
1. ✅ Convert videos to CFR (Constant Frame Rate)
2. ✅ Extract FPS data from FrameView CSVs
3. ✅ Compare image quality (SSIM/PSNR)
4. ✅ Consolidate all data into CSVs
5. ✅ Generate trade-off analysis and charts

## 📋 Prerequisites

### Required Files

Place your recordings in `../tcc/recordings/`:

```
../tcc/recordings/
├── raw/
│   ├── DLAA_4K_raw.mp4
│   ├── Quality_raw.mp4
│   ├── Balanced_raw.mp4
│   ├── Performance_raw.mp4
│   └── Ultra_Performance_raw.mp4
└── frameview/
    ├── DLAA_4K_frameview.csv
    ├── Quality_frameview.csv
    ├── Balanced_frameview.csv
    ├── Performance_frameview.csv
    └── Ultra_Performance_frameview.csv
```

### Required Software

- Python 3.8+
- FFmpeg (for video processing)
- Python packages: see `requirements.txt`

```bash
# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (if not installed)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/
```

## 🛠️ Tools

### 1. **pipeline.py** - Full Automation ⭐ RECOMMENDED

Complete end-to-end analysis pipeline.

**Basic usage:**
```bash
python pipeline.py
```

**Advanced usage:**
```bash
# Skip already completed steps
python pipeline.py --skip-processing  # Skip CFR conversion
python pipeline.py --skip-fps         # Skip FPS extraction
python pipeline.py --skip-quality     # Skip quality comparison

# Process specific modes only
python pipeline.py --modes DLAA_4K Quality Balanced

# Use different baseline
python pipeline.py --baseline Quality
```

---

### 2. **processar_videos.py** - CFR Conversion Only

Converts videos to Constant Frame Rate (60 FPS, 60 seconds, 3600 frames).

**Usage:**
```bash
python processar_videos.py
python processar_videos.py --modes DLAA_4K Quality
python processar_videos.py --fps 120 --duration 30
```

---

### 3. **Individual Analysis Tools**

Located in `src/`:
- `fps_extractor.py` - Extract FPS from FrameView/overlay
- `performance_quality_analyzer.py` - Analyze trade-offs
- `video_comparison.py` - Compare SSIM/PSNR
- `video_sync.py` - Frame alignment (if needed)

See full documentation in each script's docstring.

## 📊 Output Structure

```
../tcc/
├── recordings/processed/          # CFR videos (3600 frames each)
├── fps_data/benchmark_fps.csv     # ⭐ Consolidated FPS data
├── quality_data/benchmark_quality.csv  # ⭐ Consolidated quality data
└── results/
    ├── benchmark_tradeoff.csv     # ⭐ USE IN TCC TABLES
    └── charts/
        ├── benchmark_fps_vs_quality.png  # ⭐ TCC FIGURE
        └── benchmark_efficiency.png      # ⭐ TCC FIGURE
```

## 🎓 TCC Integration

See `../tcc/COLETA_DADOS_PROTOCOLO.md` for complete recording protocol.

## 🐛 Troubleshooting

**"ffmpeg not found"**: Install FFmpeg (`brew install ffmpeg` on macOS)

**"Missing raw recordings"**: Check files are in `../tcc/recordings/raw/`

**"Frame count mismatch"**: Verify original video is ~60 seconds

## 📚 References

- Blau & Michaeli (2018): Perception-Distortion Tradeoff
- Zhang et al. (2018): LPIPS
- Lai et al. (2018): Video Temporal Consistency

---

**Created for TCC research on DLSS quality assessment**
