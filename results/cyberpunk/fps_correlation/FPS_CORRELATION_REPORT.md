# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:27:59
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 4751
- **FPS range:** 31.0 - 224.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.00 | 0.00 | 0.00 | 0.02 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.00 | 0.01 |
| 1080p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.01 | 0.02 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.00 | 0.01 |
| 1440p_DLAA_vs_Quality | 0.00 | 0.00 | 0.00 | 0.01 |
| 4K_DLAA_vs_Performance | 0.00 | 0.00 | 0.00 | 0.02 |
| 1080p_DLAA_vs_Performance | 0.00 | 0.00 | 0.03 | 0.05 |
| 4K_DLAA_vs_Balanced | 0.00 | 0.00 | 0.01 | 0.02 |
| 1440p_DLAA_vs_Performance | 0.00 | 0.00 | 0.06 | 0.06 |
| 4K_DLAA_vs_Quality | 0.00 | 0.00 | 0.00 | 0.01 |
| 4K_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.01 | 0.03 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.03 | 0.07 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | nan | nan | nan | 3 |
| 1440p_DLAA_vs_Ultra_Performance | 0.273 | 0.0000 | 0.238 | 128 |
| 1080p_DLAA_vs_Balanced | nan | nan | nan | 3 |
| 1440p_DLAA_vs_Balanced | -0.080 | 0.1167 | 0.025 | 128 |
| 1440p_DLAA_vs_Quality | 0.008 | 0.8781 | 0.106 | 111 |
| 4K_DLAA_vs_Performance | 0.151 | 0.0078 | 0.259 | 103 |
| 1080p_DLAA_vs_Performance | 0.011 | 0.8279 | -0.003 | 131 |
| 4K_DLAA_vs_Balanced | -0.046 | 0.3593 | 0.102 | 132 |
| 1440p_DLAA_vs_Performance | -0.011 | 0.8285 | 0.025 | 131 |
| 4K_DLAA_vs_Quality | -0.221 | 0.0000 | -0.239 | 130 |
| 4K_DLAA_vs_Ultra_Performance | -0.032 | 0.5241 | 0.032 | 133 |
| 1080p_DLAA_vs_Ultra_Performance | 0.252 | 0.0000 | 0.143 | 131 |

**Average:** Pearson r = 0.031, Spearman ρ = 0.069

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | nan | nan | nan | 3 |
| 1440p_DLAA_vs_Ultra_Performance | -0.176 | 0.0005 | -0.092 | 128 |
| 1080p_DLAA_vs_Balanced | nan | nan | nan | 3 |
| 1440p_DLAA_vs_Balanced | 0.115 | 0.0236 | 0.041 | 128 |
| 1440p_DLAA_vs_Quality | 0.002 | 0.9760 | -0.042 | 111 |
| 4K_DLAA_vs_Performance | -0.142 | 0.0124 | -0.244 | 103 |
| 1080p_DLAA_vs_Performance | 0.054 | 0.2865 | 0.054 | 131 |
| 4K_DLAA_vs_Balanced | 0.132 | 0.0083 | 0.053 | 133 |
| 1440p_DLAA_vs_Performance | -0.175 | 0.0005 | -0.206 | 132 |
| 4K_DLAA_vs_Quality | 0.261 | 0.0000 | 0.270 | 130 |
| 4K_DLAA_vs_Ultra_Performance | 0.052 | 0.3035 | -0.038 | 133 |
| 1080p_DLAA_vs_Ultra_Performance | -0.185 | 0.0002 | -0.030 | 132 |

**Average:** Pearson r = -0.006, Spearman ρ = -0.023

**Interpretation:** Weak negative correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | nan | nan | nan | 3 |
| 1440p_DLAA_vs_Ultra_Performance | -0.180 | 0.0004 | -0.192 | 128 |
| 1080p_DLAA_vs_Balanced | nan | nan | nan | 3 |
| 1440p_DLAA_vs_Balanced | -0.021 | 0.6819 | -0.105 | 128 |
| 1440p_DLAA_vs_Quality | -0.067 | 0.2199 | -0.169 | 111 |
| 4K_DLAA_vs_Performance | -0.245 | 0.0000 | -0.312 | 103 |
| 1080p_DLAA_vs_Performance | 0.045 | 0.3758 | 0.075 | 132 |
| 4K_DLAA_vs_Balanced | 0.137 | 0.0062 | 0.018 | 133 |
| 1440p_DLAA_vs_Performance | -0.065 | 0.2008 | -0.147 | 132 |
| 4K_DLAA_vs_Quality | 0.193 | 0.0001 | 0.247 | 130 |
| 4K_DLAA_vs_Ultra_Performance | 0.022 | 0.6577 | -0.182 | 134 |
| 1080p_DLAA_vs_Ultra_Performance | -0.128 | 0.0111 | 0.009 | 133 |

**Average:** Pearson r = -0.031, Spearman ρ = -0.076

**Interpretation:** Weak negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.00, Quality DW = 0.01
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~67%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.031
   - FPS vs LPIPS: r = -0.006
   - FPS vs FLIP: r = -0.031

