# Reproducibility Analysis Report
Generated: 2026-04-30 11:29:12
---

## Overview

- **Games analyzed:** 3
- **Resolutions:** 1080p, 1440p, 4K
- **Total frames:** 723

## Noise Floor Analysis

Minimum Detectable Difference (MDD) = 2 × standard deviation (95% confidence)

| Resolution | SSIM Consistency | SSIM MDD (±) | LPIPS Consistency | LPIPS MDD (±) |
|-----------|-----------------|--------------|-------------------|---------------|
| 1440p | 0.859 | 0.045 | 0.132 | 0.052 |
| 1080p | 0.842 | 0.049 | 0.143 | 0.058 |
| 4K | 0.865 | 0.048 | 0.149 | 0.090 |

### Interpretation

1. **Worst reproducibility:** 1080p with SSIM = 0.842
   - Ideal threshold: SSIM ≥ 0.99
   - Observed: SSIM = 0.842 → **15.8% structural dissimilarity**

2. **Implication for DLSS comparisons:**
   - **1440p**: Quality differences < ±0.045 SSIM may be noise
   - **1080p**: Quality differences < ±0.049 SSIM may be noise
   - **4K**: Quality differences < ±0.048 SSIM may be noise

## Power Analysis

Sample size required to detect quality differences with 80% power (α=0.05):

### Medium Effect Size (Cohen's d = 0.5)

| Resolution | Metric | Required Frames |
|-----------|--------|----------------|
| 1440p | SSIM | 32 |
| 1440p | LPIPS | 32 |
| 1080p | SSIM | 32 |
| 1080p | LPIPS | 32 |
| 4K | SSIM | 32 |
| 4K | LPIPS | 32 |

**Current sample:** ~392 frames/video → adequate for medium-large effects

