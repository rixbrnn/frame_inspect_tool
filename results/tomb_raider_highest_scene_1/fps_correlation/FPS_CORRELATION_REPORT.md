# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:29:17
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 2892
- **FPS range:** 8.0 - 342.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.00 | 0.00 | 0.00 | 0.00 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.00 | 0.01 |
| 1080p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.00 | 0.00 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.00 | 0.01 |
| 1440p_DLAA_vs_Quality | 0.00 | 0.00 | 0.00 | 0.01 |
| 4K_DLAA_vs_Performance | 0.00 | 0.00 | 0.00 | 0.00 |
| 1080p_DLAA_vs_Performance | 0.00 | 0.00 | 0.00 | 0.01 |
| 4K_DLAA_vs_Balanced | 0.00 | 0.00 | 0.00 | 0.00 |
| 1440p_DLAA_vs_Performance | 0.01 | 0.00 | 0.01 | 0.00 |
| 4K_DLAA_vs_Quality | 0.00 | 0.00 | 0.00 | 0.00 |
| 4K_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.00 | 0.00 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.00 | 0.00 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.087 | 0.1800 | 0.084 | 80 |
| 1440p_DLAA_vs_Ultra_Performance | 0.487 | 0.0000 | 0.362 | 80 |
| 1080p_DLAA_vs_Balanced | 0.063 | 0.3291 | 0.003 | 80 |
| 1440p_DLAA_vs_Balanced | 0.019 | 0.7677 | 0.004 | 80 |
| 1440p_DLAA_vs_Quality | 0.434 | 0.0000 | 0.390 | 80 |
| 4K_DLAA_vs_Performance | -0.193 | 0.0027 | -0.233 | 80 |
| 1080p_DLAA_vs_Performance | 0.133 | 0.0389 | 0.025 | 80 |
| 4K_DLAA_vs_Balanced | -0.113 | 0.0789 | -0.128 | 80 |
| 1440p_DLAA_vs_Performance | -0.004 | 0.9489 | -0.087 | 80 |
| 4K_DLAA_vs_Quality | -0.091 | 0.1609 | -0.109 | 80 |
| 4K_DLAA_vs_Ultra_Performance | 0.004 | 0.9455 | -0.039 | 80 |
| 1080p_DLAA_vs_Ultra_Performance | 0.145 | 0.0244 | 0.124 | 80 |

**Average:** Pearson r = 0.081, Spearman ρ = 0.033

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.018 | 0.7775 | -0.054 | 80 |
| 1440p_DLAA_vs_Ultra_Performance | -0.266 | 0.0000 | -0.119 | 80 |
| 1080p_DLAA_vs_Balanced | 0.098 | 0.1305 | 0.134 | 80 |
| 1440p_DLAA_vs_Balanced | 0.050 | 0.4383 | 0.015 | 80 |
| 1440p_DLAA_vs_Quality | -0.252 | 0.0001 | -0.145 | 80 |
| 4K_DLAA_vs_Performance | 0.290 | 0.0000 | 0.246 | 80 |
| 1080p_DLAA_vs_Performance | -0.259 | 0.0000 | -0.127 | 80 |
| 4K_DLAA_vs_Balanced | 0.270 | 0.0000 | 0.206 | 80 |
| 1440p_DLAA_vs_Performance | 0.166 | 0.0098 | 0.201 | 81 |
| 4K_DLAA_vs_Quality | 0.273 | 0.0000 | 0.206 | 80 |
| 4K_DLAA_vs_Ultra_Performance | 0.149 | 0.0209 | 0.132 | 80 |
| 1080p_DLAA_vs_Ultra_Performance | -0.139 | 0.0310 | -0.099 | 80 |

**Average:** Pearson r = 0.030, Spearman ρ = 0.050

**Interpretation:** Weak positive correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.126 | 0.0505 | -0.204 | 80 |
| 1440p_DLAA_vs_Ultra_Performance | -0.479 | 0.0000 | -0.355 | 81 |
| 1080p_DLAA_vs_Balanced | -0.065 | 0.3177 | -0.071 | 80 |
| 1440p_DLAA_vs_Balanced | -0.089 | 0.1674 | -0.118 | 80 |
| 1440p_DLAA_vs_Quality | -0.467 | 0.0000 | -0.390 | 80 |
| 4K_DLAA_vs_Performance | 0.145 | 0.0245 | 0.066 | 80 |
| 1080p_DLAA_vs_Performance | -0.353 | 0.0000 | -0.260 | 80 |
| 4K_DLAA_vs_Balanced | 0.049 | 0.4511 | -0.043 | 80 |
| 1440p_DLAA_vs_Performance | -0.040 | 0.5378 | -0.027 | 81 |
| 4K_DLAA_vs_Quality | 0.078 | 0.2278 | -0.002 | 80 |
| 4K_DLAA_vs_Ultra_Performance | -0.153 | 0.0176 | -0.245 | 80 |
| 1080p_DLAA_vs_Ultra_Performance | -0.189 | 0.0032 | -0.225 | 80 |

**Average:** Pearson r = -0.141, Spearman ρ = -0.156

**Interpretation:** Weak negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.00, Quality DW = 0.00
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~67%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.081
   - FPS vs LPIPS: r = 0.030
   - FPS vs FLIP: r = -0.141

