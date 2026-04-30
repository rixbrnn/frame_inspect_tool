# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:29:04
---

## Overview

- **Comparisons analyzed:** 8
- **Total frames:** 5636
- **FPS range:** 107.9 - 257.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.00 | 0.00 | 0.02 | 0.07 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.02 | 0.08 |
| 1080p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.04 | 0.11 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.02 | 0.08 |
| 1440p_DLAA_vs_Quality | 0.00 | 0.00 | 0.02 | 0.08 |
| 1080p_DLAA_vs_Performance | 0.00 | 0.00 | 0.03 | 0.09 |
| 1440p_DLAA_vs_Performance | 0.00 | 0.00 | 0.03 | 0.10 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.02 | 0.09 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.009 | 0.8019 | 0.061 | 235 |
| 1440p_DLAA_vs_Ultra_Performance | -0.075 | 0.0456 | 0.037 | 235 |
| 1080p_DLAA_vs_Balanced | 0.094 | 0.0129 | 0.157 | 235 |
| 1440p_DLAA_vs_Balanced | 0.024 | 0.5218 | 0.114 | 235 |
| 1440p_DLAA_vs_Quality | 0.140 | 0.0002 | 0.154 | 235 |
| 1080p_DLAA_vs_Performance | 0.147 | 0.0001 | 0.186 | 235 |
| 1440p_DLAA_vs_Performance | -0.035 | 0.3470 | 0.083 | 235 |
| 1080p_DLAA_vs_Ultra_Performance | 0.068 | 0.0713 | 0.108 | 235 |

**Average:** Pearson r = 0.046, Spearman ρ = 0.113

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.119 | 0.0016 | -0.180 | 236 |
| 1440p_DLAA_vs_Ultra_Performance | -0.134 | 0.0004 | -0.175 | 235 |
| 1080p_DLAA_vs_Balanced | -0.208 | 0.0000 | -0.235 | 237 |
| 1440p_DLAA_vs_Balanced | -0.141 | 0.0002 | -0.183 | 236 |
| 1440p_DLAA_vs_Quality | -0.207 | 0.0000 | -0.225 | 236 |
| 1080p_DLAA_vs_Performance | -0.271 | 0.0000 | -0.285 | 236 |
| 1440p_DLAA_vs_Performance | -0.103 | 0.0064 | -0.158 | 236 |
| 1080p_DLAA_vs_Ultra_Performance | -0.197 | 0.0000 | -0.217 | 236 |

**Average:** Pearson r = -0.173, Spearman ρ = -0.207

**Interpretation:** Weak negative correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.143 | 0.0001 | 0.023 | 238 |
| 1440p_DLAA_vs_Ultra_Performance | 0.123 | 0.0011 | 0.011 | 238 |
| 1080p_DLAA_vs_Balanced | 0.077 | 0.0417 | -0.037 | 239 |
| 1440p_DLAA_vs_Balanced | 0.121 | 0.0012 | 0.011 | 238 |
| 1440p_DLAA_vs_Quality | 0.067 | 0.0743 | -0.034 | 238 |
| 1080p_DLAA_vs_Performance | 0.022 | 0.5560 | -0.097 | 239 |
| 1440p_DLAA_vs_Performance | 0.153 | 0.0000 | 0.034 | 239 |
| 1080p_DLAA_vs_Ultra_Performance | 0.027 | 0.4792 | -0.065 | 239 |

**Average:** Pearson r = 0.092, Spearman ρ = -0.019

**Interpretation:** Weak positive correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.00, Quality DW = 0.04
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~66%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.046
   - FPS vs LPIPS: r = -0.173
   - FPS vs FLIP: r = 0.092

