# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:27:46
---

## Overview

- **Comparisons analyzed:** 8
- **Total frames:** 3187
- **FPS range:** 153.0 - 245.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.00 | 0.00 | 0.03 | 0.04 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.01 | 0.03 |
| 1080p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.04 | 0.12 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.02 | 0.04 |
| 1440p_DLAA_vs_Quality | 0.00 | 0.00 | 0.02 | 0.03 |
| 1080p_DLAA_vs_Performance | 0.00 | 0.00 | 0.03 | 0.04 |
| 1440p_DLAA_vs_Performance | 0.00 | 0.00 | 0.05 | 0.06 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.02 | 0.03 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.279 | 0.0000 | 0.245 | 133 |
| 1440p_DLAA_vs_Ultra_Performance | 0.270 | 0.0000 | 0.221 | 133 |
| 1080p_DLAA_vs_Balanced | 0.434 | 0.0000 | 0.392 | 133 |
| 1440p_DLAA_vs_Balanced | 0.329 | 0.0000 | 0.307 | 133 |
| 1440p_DLAA_vs_Quality | 0.357 | 0.0000 | 0.331 | 133 |
| 1080p_DLAA_vs_Performance | 0.246 | 0.0000 | 0.297 | 133 |
| 1440p_DLAA_vs_Performance | 0.237 | 0.0000 | 0.237 | 133 |
| 1080p_DLAA_vs_Ultra_Performance | 0.240 | 0.0000 | 0.193 | 133 |

**Average:** Pearson r = 0.299, Spearman ρ = 0.278

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.297 | 0.0000 | -0.328 | 133 |
| 1440p_DLAA_vs_Ultra_Performance | -0.010 | 0.8396 | -0.013 | 133 |
| 1080p_DLAA_vs_Balanced | -0.341 | 0.0000 | -0.359 | 134 |
| 1440p_DLAA_vs_Balanced | 0.000 | 0.9957 | -0.014 | 133 |
| 1440p_DLAA_vs_Quality | -0.078 | 0.1220 | -0.122 | 133 |
| 1080p_DLAA_vs_Performance | -0.260 | 0.0000 | -0.280 | 133 |
| 1440p_DLAA_vs_Performance | -0.147 | 0.0033 | -0.187 | 134 |
| 1080p_DLAA_vs_Ultra_Performance | -0.301 | 0.0000 | -0.323 | 133 |

**Average:** Pearson r = -0.179, Spearman ρ = -0.203

**Interpretation:** Weak negative correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.229 | 0.0000 | -0.249 | 134 |
| 1440p_DLAA_vs_Ultra_Performance | -0.099 | 0.0477 | -0.230 | 134 |
| 1080p_DLAA_vs_Balanced | -0.221 | 0.0000 | -0.313 | 135 |
| 1440p_DLAA_vs_Balanced | -0.080 | 0.1126 | -0.231 | 134 |
| 1440p_DLAA_vs_Quality | -0.182 | 0.0003 | -0.341 | 134 |
| 1080p_DLAA_vs_Performance | -0.199 | 0.0001 | -0.192 | 133 |
| 1440p_DLAA_vs_Performance | -0.108 | 0.0314 | -0.220 | 134 |
| 1080p_DLAA_vs_Ultra_Performance | -0.190 | 0.0001 | -0.228 | 133 |

**Average:** Pearson r = -0.164, Spearman ρ = -0.250

**Interpretation:** Weak negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.00, Quality DW = 0.03
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~67%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.299
   - FPS vs LPIPS: r = -0.179
   - FPS vs FLIP: r = -0.164

