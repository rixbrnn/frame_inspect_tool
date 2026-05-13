# Cross-Game Analysis Report
Generated: 2026-05-03 22:17:21
---

## Overview

- **Games analyzed:** 11
- **Total comparisons:** 160
- **DLSS mode comparisons:** 128
- **Consistency checks:** 32

### Games Included

- **blackmyth_medium**: 15 comparisons (1080p, 1440p, 4K)
- **cod_mw2_extreme**: 15 comparisons (1080p, 1440p, 4K)
- **cyberpunk**: 15 comparisons (1080p, 1440p, 4K)
- **cyberpunk_low**: 10 comparisons (1080p, 1440p)
- **forza_extreme**: 15 comparisons (1080p, 1440p, 4K)
- **forza_motorsport_ultra**: 15 comparisons (1080p, 1440p, 4K)
- **marvel_rivals_low**: 15 comparisons (1080p, 1440p, 4K)
- **rdr2_ultra**: 15 comparisons (1080p, 1440p, 4K)
- **returnal_epic**: 15 comparisons (1080p, 1440p, 4K)
- **tomb_raider_highest_scene_1**: 15 comparisons (1080p, 1440p, 4K)
- **watch_dogs_legion_very_high**: 15 comparisons (1080p, 1440p, 4K)

## Key Findings

### 1. SSIM Counter-Intuitive Rankings

- **1080p**: Performance SSIM (0.766) > Quality SSIM (0.751) by 2.0% ⚠️
- **1440p**: Performance SSIM (0.759) > Quality SSIM (0.743) by 2.2% ⚠️

### 2. Reproducibility (DLAA Consistency)

SSIM between two independent DLAA captures:

- **1080p**: 0.749 ± 0.113 ⚠️ HIGH VARIANCE
- **1440p**: 0.758 ± 0.114 ⚠️ HIGH VARIANCE
- **4K**: 0.731 ± 0.117 ⚠️ HIGH VARIANCE

**Implication:** High variance in ground truth (DLAA) affects confidence in DLSS comparisons.

### 3. Average Metrics by Mode (Across All Games)

| Resolution | Mode | SSIM (mean±std) | PSNR (mean±std) | LPIPS (mean±std) | Games |
|-----------|------|-----------------|-----------------|------------------|-------|
| 1080p | Balanced | 0.775±0.124 | 23.3±3.2 | 0.221±0.105 | 11 |
| 1080p | Performance | 0.766±0.128 | 23.1±3.7 | 0.220±0.096 | 11 |
| 1080p | Quality | 0.751±0.115 | 22.5±2.8 | 0.237±0.099 | 11 |
| 1080p | Ultra_Performance | 0.771±0.117 | 23.2±3.4 | 0.234±0.097 | 11 |
| 1440p | Balanced | 0.708±0.117 | 20.5±3.9 | 0.303±0.140 | 11 |
| 1440p | Performance | 0.759±0.109 | 22.4±3.2 | 0.231±0.085 | 11 |
| 1440p | Quality | 0.743±0.134 | 21.8±4.3 | 0.266±0.163 | 11 |
| 1440p | Ultra_Performance | 0.737±0.125 | 21.5±4.7 | 0.289±0.148 | 11 |
| 4K | Balanced | 0.734±0.139 | 21.0±3.6 | 0.300±0.145 | 10 |
| 4K | Performance | 0.701±0.134 | 19.8±3.8 | 0.346±0.153 | 10 |
| 4K | Quality | 0.723±0.126 | 20.6±3.8 | 0.305±0.150 | 10 |
| 4K | Ultra_Performance | 0.721±0.108 | 20.2±3.0 | 0.332±0.087 | 10 |

