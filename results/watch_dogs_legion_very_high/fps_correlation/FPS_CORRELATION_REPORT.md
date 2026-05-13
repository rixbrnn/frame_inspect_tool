# FPS-Quality Correlation Analysis Report
Generated: 2026-05-03 22:16:24
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 6300
- **FPS range:** 12.0 - 7184.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.00 | 0.00 | 0.02 | 0.04 |
| 1440p_DLAA_vs_Ultra_Performance | 0.04 | 0.00 | 0.03 | 0.26 |
| 1080p_DLAA_vs_Balanced | 0.04 | 0.00 | 0.04 | 0.20 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.01 | 0.08 |
| 1440p_DLAA_vs_Quality | 0.12 | 0.00 | 0.03 | 0.23 |
| 4K_DLAA_vs_Performance | 0.09 | 0.00 | 0.01 | 0.03 |
| 1080p_DLAA_vs_Performance | 0.04 | 0.00 | 0.01 | 0.01 |
| 4K_DLAA_vs_Balanced | 0.00 | 0.01 | 0.04 | 0.15 |
| 1440p_DLAA_vs_Performance | 0.04 | 0.00 | 0.02 | 0.17 |
| 4K_DLAA_vs_Quality | 0.12 | 0.00 | 0.01 | 0.02 |
| 4K_DLAA_vs_Ultra_Performance | 1.45 | 0.00 | 0.01 | 0.05 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.04 | 0.11 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.052 | 0.2383 | 0.062 | 175 |
| 1440p_DLAA_vs_Ultra_Performance | -0.123 | 0.0049 | -0.069 | 176 |
| 1080p_DLAA_vs_Balanced | -0.053 | 0.2291 | 0.026 | 176 |
| 1440p_DLAA_vs_Balanced | -0.177 | 0.0000 | -0.193 | 175 |
| 1440p_DLAA_vs_Quality | -0.053 | 0.2281 | -0.011 | 179 |
| 4K_DLAA_vs_Performance | -0.007 | 0.8722 | 0.027 | 178 |
| 1080p_DLAA_vs_Performance | -0.145 | 0.0009 | -0.074 | 176 |
| 4K_DLAA_vs_Balanced | 0.255 | 0.0000 | 0.258 | 175 |
| 1440p_DLAA_vs_Performance | -0.079 | 0.0721 | -0.022 | 176 |
| 4K_DLAA_vs_Quality | -0.027 | 0.5320 | 0.128 | 178 |
| 4K_DLAA_vs_Ultra_Performance | -0.044 | 0.3159 | -0.019 | 231 |
| 1080p_DLAA_vs_Ultra_Performance | 0.055 | 0.2068 | 0.052 | 175 |

**Average:** Pearson r = -0.029, Spearman ρ = 0.014

**Interpretation:** Weak negative correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.152 | 0.0005 | -0.144 | 176 |
| 1440p_DLAA_vs_Ultra_Performance | 0.034 | 0.4400 | 0.086 | 177 |
| 1080p_DLAA_vs_Balanced | -0.084 | 0.0544 | -0.242 | 177 |
| 1440p_DLAA_vs_Balanced | 0.088 | 0.0443 | 0.108 | 175 |
| 1440p_DLAA_vs_Quality | -0.030 | 0.4914 | -0.101 | 179 |
| 4K_DLAA_vs_Performance | -0.101 | 0.0212 | -0.185 | 178 |
| 1080p_DLAA_vs_Performance | 0.095 | 0.0295 | -0.021 | 176 |
| 4K_DLAA_vs_Balanced | -0.353 | 0.0000 | -0.342 | 176 |
| 1440p_DLAA_vs_Performance | -0.020 | 0.6497 | -0.007 | 177 |
| 4K_DLAA_vs_Quality | -0.019 | 0.6681 | -0.090 | 179 |
| 4K_DLAA_vs_Ultra_Performance | 0.065 | 0.1380 | -0.106 | 231 |
| 1080p_DLAA_vs_Ultra_Performance | -0.182 | 0.0000 | -0.162 | 176 |

**Average:** Pearson r = -0.055, Spearman ρ = -0.100

**Interpretation:** Weak negative correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.127 | 0.0035 | -0.026 | 176 |
| 1440p_DLAA_vs_Ultra_Performance | 0.024 | 0.5809 | 0.091 | 184 |
| 1080p_DLAA_vs_Balanced | -0.010 | 0.8178 | 0.029 | 182 |
| 1440p_DLAA_vs_Balanced | 0.006 | 0.8874 | 0.123 | 177 |
| 1440p_DLAA_vs_Quality | -0.037 | 0.3989 | -0.045 | 186 |
| 4K_DLAA_vs_Performance | -0.100 | 0.0215 | -0.082 | 179 |
| 1080p_DLAA_vs_Performance | 0.030 | 0.4903 | 0.040 | 177 |
| 4K_DLAA_vs_Balanced | -0.296 | 0.0000 | -0.265 | 179 |
| 1440p_DLAA_vs_Performance | -0.003 | 0.9507 | 0.061 | 181 |
| 4K_DLAA_vs_Quality | -0.010 | 0.8191 | -0.156 | 179 |
| 4K_DLAA_vs_Ultra_Performance | -0.004 | 0.9341 | -0.011 | 233 |
| 1080p_DLAA_vs_Ultra_Performance | -0.170 | 0.0001 | -0.018 | 178 |

**Average:** Pearson r = -0.058, Spearman ρ = -0.022

**Interpretation:** Weak negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.16, Quality DW = 0.05
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~65%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = -0.029
   - FPS vs LPIPS: r = -0.055
   - FPS vs FLIP: r = -0.058

