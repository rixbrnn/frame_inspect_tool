# Reproducibility Analysis Report
Generated: 2026-04-30 11:27:40
---

## Overview

- **Games analyzed:** 2
- **Resolutions:** 1080p, 1440p
- **Total frames:** 797

## Noise Floor Analysis

Minimum Detectable Difference (MDD) = 2 × standard deviation (95% confidence)

| Resolution | SSIM Consistency | SSIM MDD (±) | LPIPS Consistency | LPIPS MDD (±) |
|-----------|-----------------|--------------|-------------------|---------------|
| 1440p | 0.864 | 0.137 | 0.137 | 0.111 |
| 1080p | 0.828 | 0.151 | 0.142 | 0.093 |

### Interpretation

1. **Worst reproducibility:** 1080p with SSIM = 0.828
   - Ideal threshold: SSIM ≥ 0.99
   - Observed: SSIM = 0.828 → **17.2% structural dissimilarity**

2. **Implication for DLSS comparisons:**
   - **1440p**: Quality differences < ±0.137 SSIM may be noise
   - **1080p**: Quality differences < ±0.151 SSIM may be noise

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

