# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:27:20
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 10180
- **FPS range:** 87.0 - 222.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.00 | 0.00 | 0.01 | 0.01 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.01 | 0.01 |
| 1080p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.01 | 0.01 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.01 | 0.01 |
| 1440p_DLAA_vs_Quality | 0.00 | 0.00 | 0.01 | 0.01 |
| 4K_DLAA_vs_Performance | 0.00 | 0.00 | 0.01 | 0.00 |
| 1080p_DLAA_vs_Performance | 0.00 | 0.00 | 0.01 | 0.01 |
| 4K_DLAA_vs_Balanced | 0.00 | 0.00 | 0.01 | 0.00 |
| 1440p_DLAA_vs_Performance | 0.00 | 0.00 | 0.01 | 0.01 |
| 4K_DLAA_vs_Quality | 0.00 | 0.00 | 0.01 | 0.01 |
| 4K_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.01 | 0.00 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.00 | 0.01 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.218 | 0.0000 | 0.241 | 284 |
| 1440p_DLAA_vs_Ultra_Performance | 0.197 | 0.0000 | 0.219 | 283 |
| 1080p_DLAA_vs_Balanced | 0.203 | 0.0000 | 0.199 | 284 |
| 1440p_DLAA_vs_Balanced | 0.111 | 0.0012 | 0.148 | 283 |
| 1440p_DLAA_vs_Quality | 0.132 | 0.0001 | 0.161 | 283 |
| 4K_DLAA_vs_Performance | 0.170 | 0.0000 | 0.220 | 282 |
| 1080p_DLAA_vs_Performance | 0.179 | 0.0000 | 0.181 | 284 |
| 4K_DLAA_vs_Balanced | 0.134 | 0.0001 | 0.189 | 282 |
| 1440p_DLAA_vs_Performance | 0.154 | 0.0000 | 0.175 | 283 |
| 4K_DLAA_vs_Quality | 0.208 | 0.0000 | 0.246 | 282 |
| 4K_DLAA_vs_Ultra_Performance | 0.110 | 0.0013 | 0.159 | 282 |
| 1080p_DLAA_vs_Ultra_Performance | 0.200 | 0.0000 | 0.179 | 284 |

**Average:** Pearson r = 0.168, Spearman ρ = 0.193

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.346 | 0.0000 | -0.366 | 284 |
| 1440p_DLAA_vs_Ultra_Performance | -0.227 | 0.0000 | -0.200 | 283 |
| 1080p_DLAA_vs_Balanced | -0.202 | 0.0000 | -0.215 | 284 |
| 1440p_DLAA_vs_Balanced | -0.130 | 0.0001 | -0.142 | 283 |
| 1440p_DLAA_vs_Quality | -0.273 | 0.0000 | -0.273 | 283 |
| 4K_DLAA_vs_Performance | -0.375 | 0.0000 | -0.388 | 282 |
| 1080p_DLAA_vs_Performance | -0.115 | 0.0008 | -0.108 | 284 |
| 4K_DLAA_vs_Balanced | -0.279 | 0.0000 | -0.331 | 282 |
| 1440p_DLAA_vs_Performance | -0.194 | 0.0000 | -0.196 | 283 |
| 4K_DLAA_vs_Quality | -0.563 | 0.0000 | -0.579 | 282 |
| 4K_DLAA_vs_Ultra_Performance | -0.278 | 0.0000 | -0.298 | 282 |
| 1080p_DLAA_vs_Ultra_Performance | -0.163 | 0.0000 | -0.088 | 284 |

**Average:** Pearson r = -0.262, Spearman ρ = -0.265

**Interpretation:** Weak negative correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.435 | 0.0000 | -0.473 | 284 |
| 1440p_DLAA_vs_Ultra_Performance | -0.355 | 0.0000 | -0.353 | 283 |
| 1080p_DLAA_vs_Balanced | -0.325 | 0.0000 | -0.321 | 284 |
| 1440p_DLAA_vs_Balanced | -0.243 | 0.0000 | -0.276 | 283 |
| 1440p_DLAA_vs_Quality | -0.383 | 0.0000 | -0.429 | 283 |
| 4K_DLAA_vs_Performance | -0.485 | 0.0000 | -0.516 | 282 |
| 1080p_DLAA_vs_Performance | -0.319 | 0.0000 | -0.314 | 284 |
| 4K_DLAA_vs_Balanced | -0.407 | 0.0000 | -0.436 | 282 |
| 1440p_DLAA_vs_Performance | -0.320 | 0.0000 | -0.346 | 283 |
| 4K_DLAA_vs_Quality | -0.540 | 0.0000 | -0.555 | 282 |
| 4K_DLAA_vs_Ultra_Performance | -0.425 | 0.0000 | -0.434 | 282 |
| 1080p_DLAA_vs_Ultra_Performance | -0.294 | 0.0000 | -0.238 | 284 |

**Average:** Pearson r = -0.378, Spearman ρ = -0.391

**Interpretation:** Moderate negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.00, Quality DW = 0.01
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~67%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.168
   - FPS vs LPIPS: r = -0.262
   - FPS vs FLIP: r = -0.378

