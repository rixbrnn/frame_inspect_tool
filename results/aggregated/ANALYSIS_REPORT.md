# Cross-Game Analysis Report
Generated: 2026-06-05 14:57:55
---

## Overview

- **Games analyzed:** 10
- **Total comparisons:** 150
- **DLSS mode comparisons:** 120
- **Consistency checks:** 30

### Games Included

- **blackmyth_medium**: 15 comparisons (1080p, 1440p, 4K)
- **cod_mw2_extreme**: 15 comparisons (1080p, 1440p, 4K)
- **cyberpunk**: 15 comparisons (1080p, 1440p, 4K)
- **forza_extreme**: 15 comparisons (1080p, 1440p, 4K)
- **forza_motorsport_ultra**: 15 comparisons (1080p, 1440p, 4K)
- **marvel_rivals_low**: 15 comparisons (1080p, 1440p, 4K)
- **rdr2_ultra**: 15 comparisons (1080p, 1440p, 4K)
- **returnal_epic**: 15 comparisons (1080p, 1440p, 4K)
- **tomb_raider_highest_scene_1**: 15 comparisons (1080p, 1440p, 4K)
- **watch_dogs_legion_very_high**: 15 comparisons (1080p, 1440p, 4K)

## Key Findings

### 1. SSIM Counter-Intuitive Rankings

- **1080p**: Performance SSIM (0.755) > Quality SSIM (0.739) by 2.2% ⚠️
- **1440p**: Performance SSIM (0.751) > Quality SSIM (0.738) by 1.8% ⚠️

### 2. Reproducibility (DLAA Consistency)

SSIM between two independent DLAA captures:

- **1080p**: 0.741 ± 0.116 ⚠️ HIGH VARIANCE
- **1440p**: 0.747 ± 0.115 ⚠️ HIGH VARIANCE
- **4K**: 0.731 ± 0.117 ⚠️ HIGH VARIANCE

**Implication:** High variance in ground truth (DLAA) affects confidence in DLSS comparisons.

### 3. Average Metrics by Mode (Across All Games)

| Resolution | Mode | SSIM (mean±std) | PSNR (mean±std) | LPIPS (mean±std) | Games |
|-----------|------|-----------------|-----------------|------------------|-------|
| 1080p | Balanced | 0.761±0.123 | 23.0±3.2 | 0.233±0.102 | 10 |
| 1080p | Performance | 0.755±0.130 | 22.9±3.9 | 0.230±0.095 | 10 |
| 1080p | Quality | 0.739±0.113 | 22.2±2.9 | 0.249±0.096 | 10 |
| 1080p | Ultra_Performance | 0.764±0.121 | 23.1±3.6 | 0.241±0.099 | 10 |
| 1440p | Balanced | 0.698±0.118 | 20.3±4.1 | 0.315±0.142 | 10 |
| 1440p | Performance | 0.751±0.111 | 22.3±3.3 | 0.239±0.085 | 10 |
| 1440p | Quality | 0.738±0.140 | 21.7±4.6 | 0.272±0.170 | 10 |
| 1440p | Ultra_Performance | 0.730±0.130 | 21.4±4.9 | 0.296±0.154 | 10 |
| 4K | Balanced | 0.734±0.139 | 21.0±3.6 | 0.300±0.145 | 10 |
| 4K | Performance | 0.701±0.134 | 19.8±3.8 | 0.346±0.153 | 10 |
| 4K | Quality | 0.723±0.126 | 20.6±3.8 | 0.305±0.150 | 10 |
| 4K | Ultra_Performance | 0.721±0.108 | 20.2±3.0 | 0.332±0.087 | 10 |

