# Cross-Game Analysis Report
Generated: 2026-04-30 09:48:32
---

## Overview

- **Games analyzed:** 10
- **Total comparisons:** 140
- **DLSS mode comparisons:** 112
- **Consistency checks:** 28

### Games Included

- **blackmyth_medium**: 15 comparisons (1080p, 1440p, 4K)
- **cod_mw2_extreme**: 15 comparisons (1080p, 1440p, 4K)
- **cyberpunk**: 15 comparisons (1080p, 1440p, 4K)
- **cyberpunk_low**: 10 comparisons (1080p, 1440p)
- **forza_extreme**: 15 comparisons (1080p, 1440p, 4K)
- **forza_motorsport_ultra**: 15 comparisons (1080p, 1440p, 4K)
- **marvel_rivals_low**: 15 comparisons (1080p, 1440p, 4K)
- **rdr2_ultra**: 15 comparisons (1080p, 1440p, 4K)
- **returnal_epic**: 10 comparisons (1080p, 1440p)
- **tomb_raider_highest_scene_1**: 15 comparisons (1080p, 1440p, 4K)

## Key Findings

### 1. SSIM Counter-Intuitive Rankings

- **1080p**: Performance SSIM (0.780) > Quality SSIM (0.758) by 2.9% ⚠️
- **1440p**: Performance SSIM (0.765) > Quality SSIM (0.744) by 2.8% ⚠️

### 2. Reproducibility (DLAA Consistency)

SSIM between two independent DLAA captures:

- **1080p**: 0.761 ± 0.111 ⚠️ HIGH VARIANCE
- **1440p**: 0.769 ± 0.114 ⚠️ HIGH VARIANCE
- **4K**: 0.713 ± 0.124 ⚠️ HIGH VARIANCE

**Implication:** High variance in ground truth (DLAA) affects confidence in DLSS comparisons.

### 3. Average Metrics by Mode (Across All Games)

| Resolution | Mode | SSIM (mean±std) | PSNR (mean±std) | LPIPS (mean±std) | Games |
|-----------|------|-----------------|-----------------|------------------|-------|
| 1080p | Balanced | 0.771±0.131 | 23.2±3.3 | 0.230±0.107 | 10 |
| 1080p | Performance | 0.780±0.125 | 23.4±3.8 | 0.218±0.100 | 10 |
| 1080p | Quality | 0.758±0.118 | 22.6±3.0 | 0.241±0.103 | 10 |
| 1080p | Ultra_Performance | 0.772±0.123 | 23.1±3.6 | 0.243±0.097 | 10 |
| 1440p | Balanced | 0.716±0.120 | 20.5±4.1 | 0.309±0.146 | 10 |
| 1440p | Performance | 0.765±0.113 | 22.4±3.4 | 0.236±0.087 | 10 |
| 1440p | Quality | 0.744±0.141 | 21.6±4.5 | 0.277±0.168 | 10 |
| 1440p | Ultra_Performance | 0.743±0.130 | 21.5±4.9 | 0.300±0.152 | 10 |
| 4K | Balanced | 0.717±0.152 | 20.5±3.8 | 0.325±0.151 | 8 |
| 4K | Performance | 0.691±0.137 | 19.3±4.0 | 0.372±0.161 | 8 |
| 4K | Quality | 0.715±0.132 | 20.2±4.1 | 0.328±0.162 | 8 |
| 4K | Ultra_Performance | 0.719±0.107 | 20.0±3.1 | 0.345±0.090 | 8 |

