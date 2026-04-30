# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:27:33
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 4251
- **FPS range:** 10.0 - 298.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.00 | 0.01 | 0.13 | 0.36 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.01 | 0.07 | 0.15 |
| 1080p_DLAA_vs_Balanced | 0.02 | 0.01 | 0.11 | 0.32 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.01 | 0.08 | 0.21 |
| 1440p_DLAA_vs_Quality | 0.00 | 0.01 | 0.09 | 0.30 |
| 4K_DLAA_vs_Performance | 0.00 | 0.01 | 0.07 | 0.27 |
| 1080p_DLAA_vs_Performance | 0.01 | 0.01 | 0.09 | 0.20 |
| 4K_DLAA_vs_Balanced | 0.01 | 0.01 | 0.05 | 0.11 |
| 1440p_DLAA_vs_Performance | 0.00 | 0.01 | 0.10 | 0.33 |
| 4K_DLAA_vs_Quality | 0.00 | 0.01 | 0.14 | 0.30 |
| 4K_DLAA_vs_Ultra_Performance | 0.00 | 0.01 | 0.04 | 0.13 |
| 1080p_DLAA_vs_Ultra_Performance | 0.01 | 0.01 | 0.09 | 0.28 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.037 | 0.4849 | -0.032 | 118 |
| 1440p_DLAA_vs_Ultra_Performance | 0.112 | 0.0355 | 0.146 | 118 |
| 1080p_DLAA_vs_Balanced | 0.048 | 0.3708 | 0.059 | 119 |
| 1440p_DLAA_vs_Balanced | -0.018 | 0.7354 | -0.011 | 118 |
| 1440p_DLAA_vs_Quality | -0.052 | 0.3289 | -0.019 | 118 |
| 4K_DLAA_vs_Performance | 0.051 | 0.3355 | 0.107 | 118 |
| 1080p_DLAA_vs_Performance | -0.105 | 0.0476 | -0.011 | 118 |
| 4K_DLAA_vs_Balanced | -0.169 | 0.0014 | -0.066 | 119 |
| 1440p_DLAA_vs_Performance | 0.143 | 0.0072 | 0.133 | 118 |
| 4K_DLAA_vs_Quality | -0.074 | 0.1622 | -0.122 | 119 |
| 4K_DLAA_vs_Ultra_Performance | 0.175 | 0.0009 | 0.163 | 119 |
| 1080p_DLAA_vs_Ultra_Performance | -0.001 | 0.9916 | 0.043 | 118 |

**Average:** Pearson r = 0.006, Spearman ρ = 0.032

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.178 | 0.0008 | 0.270 | 121 |
| 1440p_DLAA_vs_Ultra_Performance | 0.232 | 0.0000 | 0.247 | 119 |
| 1080p_DLAA_vs_Balanced | 0.135 | 0.0111 | 0.203 | 121 |
| 1440p_DLAA_vs_Balanced | 0.178 | 0.0008 | 0.253 | 120 |
| 1440p_DLAA_vs_Quality | 0.139 | 0.0087 | 0.214 | 120 |
| 4K_DLAA_vs_Performance | 0.236 | 0.0000 | 0.264 | 119 |
| 1080p_DLAA_vs_Performance | 0.131 | 0.0133 | 0.259 | 120 |
| 4K_DLAA_vs_Balanced | 0.364 | 0.0000 | 0.362 | 119 |
| 1440p_DLAA_vs_Performance | 0.165 | 0.0019 | 0.242 | 120 |
| 4K_DLAA_vs_Quality | 0.046 | 0.3909 | 0.113 | 121 |
| 4K_DLAA_vs_Ultra_Performance | 0.178 | 0.0008 | 0.215 | 119 |
| 1080p_DLAA_vs_Ultra_Performance | 0.171 | 0.0013 | 0.212 | 120 |

**Average:** Pearson r = 0.179, Spearman ρ = 0.238

**Interpretation:** Weak positive correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.000 | 0.9993 | 0.113 | 126 |
| 1440p_DLAA_vs_Ultra_Performance | 0.050 | 0.3463 | 0.087 | 121 |
| 1080p_DLAA_vs_Balanced | -0.032 | 0.5431 | -0.039 | 125 |
| 1440p_DLAA_vs_Balanced | -0.040 | 0.4585 | 0.038 | 122 |
| 1440p_DLAA_vs_Quality | -0.128 | 0.0162 | -0.107 | 124 |
| 4K_DLAA_vs_Performance | -0.034 | 0.5211 | 0.072 | 124 |
| 1080p_DLAA_vs_Performance | 0.038 | 0.4804 | 0.110 | 122 |
| 4K_DLAA_vs_Balanced | 0.257 | 0.0000 | 0.240 | 121 |
| 1440p_DLAA_vs_Performance | -0.095 | 0.0732 | -0.091 | 125 |
| 4K_DLAA_vs_Quality | -0.138 | 0.0090 | -0.134 | 125 |
| 4K_DLAA_vs_Ultra_Performance | -0.145 | 0.0063 | -0.086 | 121 |
| 1080p_DLAA_vs_Ultra_Performance | 0.023 | 0.6669 | 0.089 | 124 |

**Average:** Pearson r = -0.020, Spearman ρ = 0.024

**Interpretation:** Weak negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.00, Quality DW = 0.12
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~66%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.006
   - FPS vs LPIPS: r = 0.179
   - FPS vs FLIP: r = -0.020

