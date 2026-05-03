# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:28:51
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 9546
- **FPS range:** 10.0 - 168.2

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.00 | 0.00 | 0.00 | 0.01 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.00 | 0.01 |
| 1080p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.00 | 0.01 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.00 | 0.01 |
| 1440p_DLAA_vs_Quality | 0.01 | 0.00 | 0.00 | 0.00 |
| 4K_DLAA_vs_Performance | 0.00 | 0.00 | 0.00 | 0.00 |
| 1080p_DLAA_vs_Performance | 0.00 | 0.00 | 0.01 | 0.01 |
| 4K_DLAA_vs_Balanced | 0.00 | 0.00 | 0.00 | 0.00 |
| 1440p_DLAA_vs_Performance | 0.00 | 0.00 | 0.01 | 0.01 |
| 4K_DLAA_vs_Quality | 0.00 | 0.00 | 0.00 | 0.01 |
| 4K_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.00 | 0.00 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.00 | 0.01 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.090 | 0.0112 | 0.121 | 263 |
| 1440p_DLAA_vs_Ultra_Performance | -0.015 | 0.6743 | -0.020 | 265 |
| 1080p_DLAA_vs_Balanced | -0.042 | 0.2407 | 0.014 | 263 |
| 1440p_DLAA_vs_Balanced | 0.066 | 0.0637 | 0.102 | 263 |
| 1440p_DLAA_vs_Quality | 0.058 | 0.1040 | 0.093 | 263 |
| 4K_DLAA_vs_Performance | 0.094 | 0.0078 | 0.048 | 269 |
| 1080p_DLAA_vs_Performance | -0.013 | 0.7206 | 0.035 | 264 |
| 4K_DLAA_vs_Balanced | 0.103 | 0.0044 | 0.119 | 255 |
| 1440p_DLAA_vs_Performance | 0.043 | 0.2188 | 0.078 | 268 |
| 4K_DLAA_vs_Quality | 0.277 | 0.0000 | 0.293 | 265 |
| 4K_DLAA_vs_Ultra_Performance | 0.188 | 0.0000 | 0.207 | 265 |
| 1080p_DLAA_vs_Ultra_Performance | -0.018 | 0.6106 | -0.017 | 267 |

**Average:** Pearson r = 0.069, Spearman ρ = 0.089

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.042 | 0.2398 | -0.044 | 263 |
| 1440p_DLAA_vs_Ultra_Performance | 0.039 | 0.2767 | 0.052 | 265 |
| 1080p_DLAA_vs_Balanced | 0.075 | 0.0347 | 0.069 | 263 |
| 1440p_DLAA_vs_Balanced | 0.019 | 0.5856 | 0.020 | 264 |
| 1440p_DLAA_vs_Quality | -0.003 | 0.9358 | 0.028 | 263 |
| 4K_DLAA_vs_Performance | 0.060 | 0.0866 | 0.272 | 269 |
| 1080p_DLAA_vs_Performance | 0.077 | 0.0313 | 0.091 | 264 |
| 4K_DLAA_vs_Balanced | 0.199 | 0.0000 | 0.202 | 255 |
| 1440p_DLAA_vs_Performance | 0.003 | 0.9333 | 0.022 | 268 |
| 4K_DLAA_vs_Quality | -0.076 | 0.0319 | 0.104 | 265 |
| 4K_DLAA_vs_Ultra_Performance | -0.090 | 0.0112 | -0.095 | 265 |
| 1080p_DLAA_vs_Ultra_Performance | 0.063 | 0.0733 | 0.124 | 267 |

**Average:** Pearson r = 0.027, Spearman ρ = 0.071

**Interpretation:** Weak positive correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.077 | 0.0305 | -0.083 | 263 |
| 1440p_DLAA_vs_Ultra_Performance | -0.055 | 0.1189 | 0.006 | 265 |
| 1080p_DLAA_vs_Balanced | 0.088 | 0.0135 | 0.045 | 263 |
| 1440p_DLAA_vs_Balanced | -0.015 | 0.6782 | -0.022 | 264 |
| 1440p_DLAA_vs_Quality | -0.022 | 0.5339 | -0.003 | 263 |
| 4K_DLAA_vs_Performance | 0.009 | 0.7994 | 0.121 | 269 |
| 1080p_DLAA_vs_Performance | 0.071 | 0.0469 | 0.042 | 264 |
| 4K_DLAA_vs_Balanced | 0.075 | 0.0382 | 0.134 | 255 |
| 1440p_DLAA_vs_Performance | -0.043 | 0.2190 | -0.022 | 268 |
| 4K_DLAA_vs_Quality | -0.130 | 0.0002 | -0.073 | 265 |
| 4K_DLAA_vs_Ultra_Performance | -0.139 | 0.0001 | -0.136 | 265 |
| 1080p_DLAA_vs_Ultra_Performance | 0.024 | 0.5047 | 0.071 | 267 |

**Average:** Pearson r = -0.018, Spearman ρ = 0.007

**Interpretation:** Weak negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.00, Quality DW = 0.00
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~67%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.069
   - FPS vs LPIPS: r = 0.027
   - FPS vs FLIP: r = -0.018

