# Reproducibility Analysis Report
Generated: 2026-04-30 11:28:58
---

## Overview

- **Games analyzed:** 2
- **Resolutions:** 1080p, 1440p
- **Total frames:** 1409

## Noise Floor Analysis

Minimum Detectable Difference (MDD) = 2 × standard deviation (95% confidence)

| Resolution | SSIM Consistency | SSIM MDD (±) | LPIPS Consistency | LPIPS MDD (±) |
|-----------|-----------------|--------------|-------------------|---------------|
| 1440p | 0.815 | 0.186 | 0.199 | 0.169 |
| 1080p | 0.864 | 0.212 | 0.146 | 0.154 |

### Interpretation

1. **Worst reproducibility:** 1440p with SSIM = 0.815
   - Ideal threshold: SSIM ≥ 0.99
   - Observed: SSIM = 0.815 → **18.5% structural dissimilarity**

2. **Implication for DLSS comparisons:**
   - **1440p**: Quality differences < ±0.186 SSIM may be noise
   - **1080p**: Quality differences < ±0.212 SSIM may be noise

## Power Analysis

Sample size required to detect quality differences with 80% power (α=0.05):

### Medium Effect Size (Cohen's d = 0.5)

| Resolution | Metric | Required Frames |
|-----------|--------|----------------|
| 1440p | SSIM | 32 |
| 1440p | LPIPS | 32 |
| 1080p | SSIM | 32 |
| 1080p | LPIPS | 32 |

**Current sample:** ~392 frames/video → adequate for medium-large effects

