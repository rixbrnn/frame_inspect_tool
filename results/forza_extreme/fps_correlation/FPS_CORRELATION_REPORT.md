# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:28:12
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 6496
- **FPS range:** 10.0 - 195.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.02 | 0.00 | 0.03 | 0.06 |
| 1440p_DLAA_vs_Ultra_Performance | 0.03 | 0.00 | 0.00 | 0.02 |
| 1080p_DLAA_vs_Balanced | 0.02 | 0.00 | 0.05 | 0.11 |
| 1440p_DLAA_vs_Balanced | 0.03 | 0.00 | 0.01 | 0.03 |
| 1440p_DLAA_vs_Quality | 0.02 | 0.00 | 0.01 | 0.04 |
| 4K_DLAA_vs_Performance | 0.03 | 0.00 | 0.02 | 0.06 |
| 1080p_DLAA_vs_Performance | 0.01 | 0.00 | 0.01 | 0.06 |
| 4K_DLAA_vs_Balanced | 0.03 | 0.00 | 0.08 | 0.11 |
| 1440p_DLAA_vs_Performance | 0.03 | 0.00 | 0.01 | 0.02 |
| 4K_DLAA_vs_Quality | 0.02 | 0.00 | 0.03 | 0.05 |
| 4K_DLAA_vs_Ultra_Performance | 0.01 | 0.00 | 0.01 | 0.04 |
| 1080p_DLAA_vs_Ultra_Performance | 0.01 | 0.00 | 0.02 | 0.07 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.056 | 0.1985 | 0.144 | 180 |
| 1440p_DLAA_vs_Ultra_Performance | 0.249 | 0.0000 | 0.142 | 181 |
| 1080p_DLAA_vs_Balanced | 0.029 | 0.4946 | -0.031 | 180 |
| 1440p_DLAA_vs_Balanced | 0.246 | 0.0000 | 0.200 | 181 |
| 1440p_DLAA_vs_Quality | 0.185 | 0.0000 | 0.141 | 181 |
| 4K_DLAA_vs_Performance | 0.145 | 0.0007 | 0.264 | 182 |
| 1080p_DLAA_vs_Performance | 0.146 | 0.0007 | 0.039 | 180 |
| 4K_DLAA_vs_Balanced | 0.115 | 0.0073 | 0.309 | 181 |
| 1440p_DLAA_vs_Performance | 0.110 | 0.0106 | 0.041 | 181 |
| 4K_DLAA_vs_Quality | 0.278 | 0.0000 | 0.493 | 181 |
| 4K_DLAA_vs_Ultra_Performance | 0.196 | 0.0000 | 0.318 | 181 |
| 1080p_DLAA_vs_Ultra_Performance | 0.088 | 0.0404 | 0.125 | 180 |

**Average:** Pearson r = 0.154, Spearman ρ = 0.182

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.013 | 0.7612 | -0.075 | 181 |
| 1440p_DLAA_vs_Ultra_Performance | -0.236 | 0.0000 | -0.118 | 181 |
| 1080p_DLAA_vs_Balanced | -0.053 | 0.2216 | 0.141 | 182 |
| 1440p_DLAA_vs_Balanced | -0.232 | 0.0000 | -0.110 | 181 |
| 1440p_DLAA_vs_Quality | -0.151 | 0.0004 | -0.052 | 181 |
| 4K_DLAA_vs_Performance | -0.071 | 0.0977 | -0.071 | 182 |
| 1080p_DLAA_vs_Performance | -0.014 | 0.7433 | 0.116 | 180 |
| 4K_DLAA_vs_Balanced | -0.093 | 0.0300 | -0.216 | 184 |
| 1440p_DLAA_vs_Performance | -0.087 | 0.0442 | 0.046 | 181 |
| 4K_DLAA_vs_Quality | -0.292 | 0.0000 | -0.455 | 182 |
| 4K_DLAA_vs_Ultra_Performance | -0.159 | 0.0002 | -0.269 | 181 |
| 1080p_DLAA_vs_Ultra_Performance | -0.081 | 0.0612 | -0.085 | 180 |

**Average:** Pearson r = -0.123, Spearman ρ = -0.096

**Interpretation:** Weak negative correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.007 | 0.8682 | -0.076 | 182 |
| 1440p_DLAA_vs_Ultra_Performance | -0.180 | 0.0000 | -0.043 | 182 |
| 1080p_DLAA_vs_Balanced | -0.032 | 0.4641 | 0.140 | 184 |
| 1440p_DLAA_vs_Balanced | -0.196 | 0.0000 | -0.037 | 182 |
| 1440p_DLAA_vs_Quality | -0.116 | 0.0068 | 0.013 | 182 |
| 4K_DLAA_vs_Performance | -0.050 | 0.2481 | -0.038 | 183 |
| 1080p_DLAA_vs_Performance | -0.001 | 0.9729 | 0.130 | 182 |
| 4K_DLAA_vs_Balanced | -0.082 | 0.0574 | -0.194 | 185 |
| 1440p_DLAA_vs_Performance | -0.048 | 0.2613 | 0.109 | 182 |
| 4K_DLAA_vs_Quality | -0.289 | 0.0000 | -0.409 | 183 |
| 4K_DLAA_vs_Ultra_Performance | -0.119 | 0.0057 | -0.179 | 182 |
| 1080p_DLAA_vs_Ultra_Performance | -0.051 | 0.2356 | -0.083 | 182 |

**Average:** Pearson r = -0.098, Spearman ρ = -0.056

**Interpretation:** Weak negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.02, Quality DW = 0.03
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~66%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.154
   - FPS vs LPIPS: r = -0.123
   - FPS vs FLIP: r = -0.098

