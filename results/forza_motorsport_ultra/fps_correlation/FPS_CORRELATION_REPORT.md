# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:28:24
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 2148
- **FPS range:** 0.0 - 111.7

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.02 | 0.00 | 0.01 | 0.03 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.01 | 0.03 |
| 1080p_DLAA_vs_Balanced | 0.02 | 0.00 | 0.01 | 0.04 |
| 1440p_DLAA_vs_Balanced | 0.02 | 0.00 | 0.01 | 0.05 |
| 1440p_DLAA_vs_Quality | 0.01 | 0.00 | 0.02 | 0.05 |
| 4K_DLAA_vs_Performance | 0.00 | 0.00 | 0.01 | 0.04 |
| 1080p_DLAA_vs_Performance | 0.01 | 0.00 | 0.01 | 0.04 |
| 4K_DLAA_vs_Balanced | 0.00 | 0.00 | 0.02 | 0.05 |
| 1440p_DLAA_vs_Performance | 0.00 | 0.00 | 0.02 | 0.04 |
| 4K_DLAA_vs_Quality | 0.01 | 0.00 | 0.02 | 0.04 |
| 4K_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.01 | 0.04 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.01 | 0.03 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.100 | 0.1830 | 0.284 | 60 |
| 1440p_DLAA_vs_Ultra_Performance | 0.328 | 0.0000 | 0.356 | 60 |
| 1080p_DLAA_vs_Balanced | -0.067 | 0.3717 | 0.062 | 60 |
| 1440p_DLAA_vs_Balanced | 0.059 | 0.4314 | 0.128 | 60 |
| 1440p_DLAA_vs_Quality | 0.093 | 0.2155 | 0.234 | 60 |
| 4K_DLAA_vs_Performance | 0.188 | 0.0117 | 0.077 | 60 |
| 1080p_DLAA_vs_Performance | 0.098 | 0.1915 | 0.209 | 59 |
| 4K_DLAA_vs_Balanced | 0.341 | 0.0000 | 0.129 | 60 |
| 1440p_DLAA_vs_Performance | 0.279 | 0.0002 | 0.273 | 60 |
| 4K_DLAA_vs_Quality | 0.138 | 0.0655 | 0.162 | 60 |
| 4K_DLAA_vs_Ultra_Performance | 0.120 | 0.1110 | 0.038 | 59 |
| 1080p_DLAA_vs_Ultra_Performance | 0.371 | 0.0000 | 0.356 | 60 |

**Average:** Pearson r = 0.171, Spearman ρ = 0.192

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.134 | 0.0744 | -0.442 | 60 |
| 1440p_DLAA_vs_Ultra_Performance | -0.438 | 0.0000 | -0.443 | 60 |
| 1080p_DLAA_vs_Balanced | 0.313 | 0.0000 | 0.190 | 60 |
| 1440p_DLAA_vs_Balanced | -0.106 | 0.1585 | -0.397 | 60 |
| 1440p_DLAA_vs_Quality | 0.036 | 0.6329 | -0.074 | 60 |
| 4K_DLAA_vs_Performance | -0.421 | 0.0000 | -0.417 | 60 |
| 1080p_DLAA_vs_Performance | -0.099 | 0.1881 | -0.261 | 60 |
| 4K_DLAA_vs_Balanced | -0.535 | 0.0000 | -0.347 | 60 |
| 1440p_DLAA_vs_Performance | -0.058 | 0.4444 | -0.038 | 60 |
| 4K_DLAA_vs_Quality | -0.107 | 0.1531 | -0.365 | 60 |
| 4K_DLAA_vs_Ultra_Performance | -0.576 | 0.0000 | -0.580 | 59 |
| 1080p_DLAA_vs_Ultra_Performance | -0.281 | 0.0001 | -0.254 | 60 |

**Average:** Pearson r = -0.200, Spearman ρ = -0.286

**Interpretation:** Weak negative correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.174 | 0.0200 | -0.642 | 60 |
| 1440p_DLAA_vs_Ultra_Performance | -0.626 | 0.0000 | -0.669 | 60 |
| 1080p_DLAA_vs_Balanced | 0.043 | 0.5708 | -0.444 | 60 |
| 1440p_DLAA_vs_Balanced | -0.160 | 0.0334 | -0.655 | 60 |
| 1440p_DLAA_vs_Quality | -0.217 | 0.0035 | -0.480 | 60 |
| 4K_DLAA_vs_Performance | -0.523 | 0.0000 | -0.646 | 60 |
| 1080p_DLAA_vs_Performance | -0.181 | 0.0158 | -0.572 | 60 |
| 4K_DLAA_vs_Balanced | -0.577 | 0.0000 | -0.624 | 60 |
| 1440p_DLAA_vs_Performance | -0.450 | 0.0000 | -0.487 | 60 |
| 4K_DLAA_vs_Quality | -0.172 | 0.0212 | -0.643 | 60 |
| 4K_DLAA_vs_Ultra_Performance | -0.627 | 0.0000 | -0.710 | 60 |
| 1080p_DLAA_vs_Ultra_Performance | -0.556 | 0.0000 | -0.611 | 60 |

**Average:** Pearson r = -0.352, Spearman ρ = -0.599

**Interpretation:** Moderate negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.01, Quality DW = 0.02
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~67%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.171
   - FPS vs LPIPS: r = -0.200
   - FPS vs FLIP: r = -0.352

