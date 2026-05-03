# FPS-Quality Correlation Analysis Report
Generated: 2026-04-30 11:28:38
---

## Overview

- **Comparisons analyzed:** 12
- **Total frames:** 6529
- **FPS range:** 10.0 - 299.0

## Temporal Autocorrelation Analysis

**Durbin-Watson statistic** (closer to 2 = less autocorrelation):

| Comparison | FPS DW | SSIM DW | LPIPS DW | FLIP DW |
|-----------|--------|---------|----------|----------|
| 1080p_DLAA_vs_Quality | 0.01 | 0.00 | 0.03 | 0.08 |
| 1440p_DLAA_vs_Ultra_Performance | 0.00 | 0.01 | 0.08 | 0.07 |
| 1080p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.02 | 0.03 |
| 1440p_DLAA_vs_Balanced | 0.00 | 0.00 | 0.03 | 0.05 |
| 1440p_DLAA_vs_Quality | 0.00 | 0.00 | 0.11 | 0.19 |
| 4K_DLAA_vs_Performance | 0.00 | 0.00 | 0.03 | 0.05 |
| 1080p_DLAA_vs_Performance | 0.00 | 0.00 | 0.08 | 0.12 |
| 4K_DLAA_vs_Balanced | 0.00 | 0.00 | 0.02 | 0.06 |
| 1440p_DLAA_vs_Performance | 0.00 | 0.00 | 0.04 | 0.09 |
| 4K_DLAA_vs_Quality | 0.00 | 0.01 | 0.03 | 0.07 |
| 4K_DLAA_vs_Ultra_Performance | 0.01 | 0.00 | 0.01 | 0.04 |
| 1080p_DLAA_vs_Ultra_Performance | 0.00 | 0.00 | 0.03 | 0.07 |

**Interpretation:**
- DW values between 1.5-2.5: no significant autocorrelation
- DW < 1.5: positive autocorrelation (adjacent frames similar)
- DW > 2.5: negative autocorrelation (adjacent frames different)

## FPS-Quality Correlation Summary

### SSIM

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | 0.209 | 0.0000 | 0.204 | 182 |
| 1440p_DLAA_vs_Ultra_Performance | 0.121 | 0.0047 | 0.162 | 182 |
| 1080p_DLAA_vs_Balanced | 0.206 | 0.0000 | 0.235 | 182 |
| 1440p_DLAA_vs_Balanced | 0.128 | 0.0027 | 0.169 | 182 |
| 1440p_DLAA_vs_Quality | 0.366 | 0.0000 | 0.410 | 182 |
| 4K_DLAA_vs_Performance | 0.198 | 0.0000 | 0.240 | 182 |
| 1080p_DLAA_vs_Performance | 0.149 | 0.0005 | 0.143 | 182 |
| 4K_DLAA_vs_Balanced | 0.227 | 0.0000 | 0.243 | 181 |
| 1440p_DLAA_vs_Performance | 0.165 | 0.0001 | 0.199 | 182 |
| 4K_DLAA_vs_Quality | 0.143 | 0.0008 | 0.214 | 182 |
| 4K_DLAA_vs_Ultra_Performance | 0.135 | 0.0016 | 0.153 | 181 |
| 1080p_DLAA_vs_Ultra_Performance | 0.098 | 0.0215 | 0.111 | 182 |

**Average:** Pearson r = 0.179, Spearman ρ = 0.207

**Interpretation:** Weak positive correlation between FPS and SSIM

### LPIPS

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.250 | 0.0000 | -0.235 | 182 |
| 1440p_DLAA_vs_Ultra_Performance | -0.236 | 0.0000 | -0.266 | 184 |
| 1080p_DLAA_vs_Balanced | -0.201 | 0.0000 | -0.182 | 182 |
| 1440p_DLAA_vs_Balanced | -0.185 | 0.0000 | -0.181 | 182 |
| 1440p_DLAA_vs_Quality | -0.477 | 0.0000 | -0.589 | 185 |
| 4K_DLAA_vs_Performance | -0.181 | 0.0000 | -0.171 | 182 |
| 1080p_DLAA_vs_Performance | -0.248 | 0.0000 | -0.238 | 184 |
| 4K_DLAA_vs_Balanced | -0.213 | 0.0000 | -0.188 | 182 |
| 1440p_DLAA_vs_Performance | -0.196 | 0.0000 | -0.201 | 183 |
| 4K_DLAA_vs_Quality | -0.143 | 0.0008 | -0.182 | 182 |
| 4K_DLAA_vs_Ultra_Performance | -0.223 | 0.0000 | -0.229 | 182 |
| 1080p_DLAA_vs_Ultra_Performance | -0.155 | 0.0003 | -0.169 | 183 |

**Average:** Pearson r = -0.226, Spearman ρ = -0.236

**Interpretation:** Weak negative correlation between FPS and LPIPS

### FLIP

| Comparison | Pearson r | p-value | Spearman ρ | Effective N |
|-----------|-----------|---------|------------|-------------|
| 1080p_DLAA_vs_Quality | -0.299 | 0.0000 | -0.270 | 184 |
| 1440p_DLAA_vs_Ultra_Performance | -0.281 | 0.0000 | -0.258 | 184 |
| 1080p_DLAA_vs_Balanced | -0.301 | 0.0000 | -0.275 | 182 |
| 1440p_DLAA_vs_Balanced | -0.335 | 0.0000 | -0.316 | 183 |
| 1440p_DLAA_vs_Quality | -0.461 | 0.0000 | -0.584 | 187 |
| 4K_DLAA_vs_Performance | -0.389 | 0.0000 | -0.380 | 183 |
| 1080p_DLAA_vs_Performance | -0.270 | 0.0000 | -0.233 | 185 |
| 4K_DLAA_vs_Balanced | -0.415 | 0.0000 | -0.412 | 183 |
| 1440p_DLAA_vs_Performance | -0.299 | 0.0000 | -0.258 | 184 |
| 4K_DLAA_vs_Quality | -0.343 | 0.0000 | -0.400 | 184 |
| 4K_DLAA_vs_Ultra_Performance | -0.372 | 0.0000 | -0.395 | 182 |
| 1080p_DLAA_vs_Ultra_Performance | -0.232 | 0.0000 | -0.198 | 184 |

**Average:** Pearson r = -0.333, Spearman ρ = -0.332

**Interpretation:** Moderate negative correlation between FPS and FLIP

## Key Findings

1. **Autocorrelation present:** Average FPS DW = 0.00, Quality DW = 0.04
   - ⚠️ **Significant positive autocorrelation detected** - adjacent frames are not independent
   - Implication: Standard correlation p-values may be inflated
   - Effective sample size reduced by ~66%

2. **FPS-quality relationship:**
   - FPS vs SSIM: r = 0.179
   - FPS vs LPIPS: r = -0.226
   - FPS vs FLIP: r = -0.333

