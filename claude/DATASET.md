# DLSS Quality Analysis Dataset

## Overview

This dataset contains benchmark recordings for analyzing NVIDIA DLSS (Deep Learning Super Sampling) quality vs performance trade-offs.

**Dataset Repository:** https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data

**Analysis Tool:** https://github.com/rixbrnn/frame_inspect_tool

**Research Paper:** [Link to TCC when available]

## Dataset Contents

### Structure

```
frame_inspect_tool_data/
├── [game_name]/
│   ├── [resolution]/
│   │   ├── validation/
│   │   │   ├── run1_60fps.mp4        # Validation recording 1
│   │   │   ├── run2_60fps.mp4        # Validation recording 2
│   │   │   └── validation.json       # SSIM validation results
│   │   │
│   │   ├── processed/
│   │   │   ├── DLAA_60fps.mp4        # Baseline (ground truth)
│   │   │   ├── Quality_60fps.mp4     # DLSS Quality mode
│   │   │   ├── Balanced_60fps.mp4    # DLSS Balanced mode
│   │   │   ├── Performance_60fps.mp4 # DLSS Performance mode
│   │   │   └── UltraPerformance_60fps.mp4  # DLSS Ultra Performance
│   │   │
│   │   ├── extracted/
│   │   │   ├── DLAA_fps.json         # OCR-extracted FPS data
│   │   │   ├── Quality_fps.json
│   │   │   ├── Balanced_fps.json
│   │   │   ├── Performance_fps.json
│   │   │   └── UltraPerformance_fps.json
│   │   │
│   │   ├── results/
│   │   │   ├── quality_comparison.csv
│   │   │   ├── sync_info.json
│   │   │   └── tradeoff_analysis.json
│   │   │
│   │   └── metadata.json             # Recording metadata
│   │
│   └── fps_roi.json                  # FPS counter ROI coordinates
│
└── README.md                         # This file
```

### File Formats

**Videos (.mp4):**
- Codec: H.264 (High Profile, 4:2:0)
- Resolution: Native (1080p/1440p/4K)
- Frame Rate: Constant 60 FPS
- Bitrate: High quality (CRF 18 or 50+ Mbps)
- Color Space: sRGB (BT.709), SDR only
- Duration: ~60 seconds per recording

**FPS Data (.json):**
```json
{
  "video_path": "DLAA_60fps.mp4",
  "extraction_date": "2026-03-19",
  "fps_data": [
    {
      "frame_number": 0,
      "timestamp": 0.0,
      "fps": 58.3,
      "confidence": 0.95
    },
    ...
  ],
  "statistics": {
    "avg_fps": 58.7,
    "min_fps": 52.1,
    "max_fps": 60.0,
    "std_dev": 2.3,
    "percentile_1": 54.2,
    "percentile_0_1": 52.8
  }
}
```

**Metadata (.json):**
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
  "display_settings": {
    "hdr": false,
    "color_space": "sRGB (BT.709)"
  },
  "capture_settings": {
    "software": "NVIDIA ShadowPlay",
    "codec": "H.264",
    "quality": "High Quality (50+ Mbps)",
    "frame_rate": 60
  },
  "game_settings": {
    "preset": "Ultra",
    "ray_tracing": "Ultra",
    "dlss_frame_generation": false,
    "vsync": false,
    "fps_limit": 60
  },
  "benchmark": {
    "name": "Built-in benchmark",
    "duration": 60,
    "validated": true,
    "ssim": 99.34
  }
}
```

## Methodology

### Recording Protocol

1. **Validation Phase** (Phase 0)
   - Benchmark run 2-3 times for shader compilation warmup
   - Record same benchmark twice (run1, run2)
   - Validate reproducibility: SSIM ≥ 99% required
   - Only stable benchmarks proceed to data collection

2. **Data Collection**
   - Record DLAA (baseline) + 4 DLSS modes
   - 2-3 warmup runs before each recording
   - All settings identical except DLSS mode
   - 60 FPS cap, VSync off, HDR off

3. **Processing Pipeline**
   - Convert to CFR 60 FPS using FFmpeg
   - Extract FPS via OCR (MSI Afterburner overlay)
   - Synchronize videos using perceptual hashing
   - Compare quality using SSIM frame-by-frame
   - Analyze performance vs quality trade-offs

### Quality Metrics

- **SSIM (Structural Similarity Index):** Primary quality metric
- **PSNR (Peak Signal-to-Noise Ratio):** Secondary quality metric
- **FPS Statistics:** avg, min, max, 1% low, 0.1% low, std dev
- **Temporal Correlation:** FPS variations correlated with quality drops

### Ground Truth Selection

**DLAA (Deep Learning Anti-Aliasing)** is used as ground truth because:
- Applies DLSS neural network at native resolution (4K→4K)
- No upscaling, only anti-aliasing and detail reconstruction
- Highest quality real-time rendering method available
- Validated superior to TAA in technical literature

See methodology chapter for complete justification.

## Usage

### Download Dataset

**Install dependencies:**
```bash
pip install huggingface-hub
```

**Download all data:**
```bash
python scripts/download_dataset.py
```

**Download specific game:**
```bash
python scripts/download_dataset.py --game cyberpunk2077 --resolution 1080p
```

**List available recordings:**
```bash
python scripts/download_dataset.py --list
```

### Analyze Data

**Run full analysis pipeline:**
```bash
python scripts/pipeline.py \
    --game cyberpunk2077 \
    --resolution 1080p \
    --baseline DLAA
```

**Compare specific modes:**
```bash
python src/app.py \
    --video1 recordings/cyberpunk2077/1080p/processed/DLAA_60fps.mp4 \
    --video2 recordings/cyberpunk2077/1080p/processed/Quality_60fps.mp4
```

## Dataset Statistics

### Games Included

- [To be filled as recordings are uploaded]

### Total Data Size

- Videos: ~[X] GB
- Extracted Data: ~[X] MB
- Total: ~[X] GB

### Resolution Coverage

- 1080p (1920×1080): [X] games
- 1440p (2560×1440): [X] games
- 4K (3840×2160): [X] games

## Citation

If you use this dataset in your research, please cite:

```bibtex
@misc{rixbrnn2026dlss,
  author = {[Your Name]},
  title = {DLSS Quality vs Performance Analysis Dataset},
  year = {2026},
  publisher = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data}}
}
```

## License

**Dataset:** CC BY 4.0 (Creative Commons Attribution 4.0 International)
**Tool:** MIT License

You are free to:
- Share — copy and redistribute the material
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit

## Reproducibility

This dataset enables full reproduction of the study:

1. ✅ **Raw recordings** - Original benchmark captures
2. ✅ **Processing scripts** - Complete analysis pipeline
3. ✅ **Metadata** - System specs, game settings, validation results
4. ✅ **Extracted data** - FPS, SSIM, sync information
5. ✅ **Analysis results** - Trade-off calculations, Pareto frontiers

Other researchers can:
- Verify our results using our data
- Apply our methodology to new games
- Compare alternative analysis methods
- Extend the study with additional metrics

## Limitations

- **Hardware-specific:** Results captured on RTX 4090 may differ on other GPUs
- **Game versions:** Specific game patches/versions used (see metadata)
- **DLSS versions:** DLSS SDK version varies by game
- **Deterministic benchmarks only:** Non-reproducible benchmarks excluded
- **SDR only:** HDR not used (see methodology for justification)

## Contact

For questions or issues:
- GitHub Issues: https://github.com/rixbrnn/frame_inspect_tool/issues
- Hugging Face Discussions: https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data/discussions
- Dataset Repository: https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data

## Acknowledgments

- NVIDIA for DLSS technology and developer resources
- Hugging Face for dataset hosting
- Open source tools: FFmpeg, OpenCV, EasyOCR, Python ecosystem

## Version History

### v1.0 (2026-03-19)
- Initial dataset release
- [X] games included
- Methodology documented
- Analysis tools provided
