# Available Datasets

This document lists all datasets available on HuggingFace with their corresponding analysis configurations.

**🤗 Repository:** https://huggingface.co/datasets/rixbrnn/frame_inspect_tool_data

## Datasets with Analysis Configs

| Dataset | Game | Graphics Setting | Config File | Status |
|---------|------|------------------|-------------|--------|
| `cyberpunk` | Cyberpunk 2077 | High (re-trimmed) | `analysis_retrimmed.yaml` | ✅ Config exists |
| `cyberpunk_low` | Cyberpunk 2077 | Low | `analysis_cyberpunk_low.yaml` | ✅ Config exists |
| `tomb_raider_highest_scene_1` | Shadow of the Tomb Raider | Highest | `analysis_tomb_raider_highest_scene_1.yaml` | ✅ Config exists |
| `blackmyth_medium` | Black Myth: Wukong | Medium | `analysis_blackmyth_medium.yaml` | ✅ Config exists |
| `cod_mw2_extreme` | Call of Duty: MW2 | Extreme | `analysis_cod_mw2_extreme.yaml` | ✅ Config exists |
| `forza_extreme` | Forza Horizon 5 | Extreme | `analysis_forza_extreme.yaml` | ✅ Config exists |
| `marvel_rivals_low` | Marvel Rivals | Low | `analysis_marvel_rivals_low.yaml` | ✅ Config exists |
| `rdr2_ultra` | Red Dead Redemption 2 | Ultra | `analysis_rdr2_ultra.yaml` | ✅ Config exists |
| `returnal_epic` | Returnal | Epic | `analysis_returnal_epic.yaml` | ✅ Config exists |

## Datasets without Trimmed Videos

| Dataset | Game | Graphics Setting | Notes |
|---------|------|------------------|-------|
| `forza_motorsport_ultra` | Forza Motorsport | Ultra | No `/trimmed/` subdirectory available |

## Dataset Structure

Each dataset with analysis configs contains:
- 18 video files across 3 resolutions (1080p, 1440p, 4K)
- 6 videos per resolution:
  - `dlaa_run1.mp4` - Reference (ground truth)
  - `dlaa_run2.mp4` - Consistency check
  - `dlss_quality.mp4`
  - `dlss_balanced.mp4`
  - `dlss_performance.mp4`
  - `dlss_ultra_performance.mp4`

## Running Analysis

To analyze any dataset:

```bash
# Download the dataset
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='rixbrnn/frame_inspect_tool_data',
    repo_type='dataset',
    allow_patterns='<dataset_name>/*',
    local_dir='recordings'
)
"

# Run analysis
python src/run_analysis.py --config configs/analysis_<dataset_name>.yaml
```

## Analysis Configuration

All configs follow the same pattern:
- **ROI:** `"top-left 10%"` - FPS counter detection region
- **Sample rate:** 10 frames - Temporal sampling for efficiency
- **Metrics:** SSIM, PSNR, LPIPS, FLIP, Optical Flow
- **GPU acceleration:** Enabled for LPIPS
- **FPS extraction:** Enabled via OCR
- **Comparisons:** 15 total (5 per resolution)
  - 4 DLSS modes vs DLAA reference
  - 1 DLAA consistency check (run1 vs run2)

## Results Output

Results are saved to `results/<dataset_name>/quality_comparison/` with:
- JSON files containing frame-by-frame metrics
- Execution time and summary statistics
- Extracted FPS data for temporal correlation analysis
