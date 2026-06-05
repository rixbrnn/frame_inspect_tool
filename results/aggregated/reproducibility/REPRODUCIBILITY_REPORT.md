# Reproducibility Analysis Report
Generated: 2026-06-05 12:13:31
---

## Overview

- **Games analyzed:** 30
- **Resolutions:** 1080p, 1440p, 4K
- **Total frames:** 15398

## Noise Floor Analysis

Minimum Detectable Difference (MDD) = 2 × standard deviation (95% confidence)

| Resolution | SSIM Consistency | SSIM MDD (±) | LPIPS Consistency | LPIPS MDD (±) |
|-----------|-----------------|--------------|-------------------|---------------|
| 1440p | 0.747 | 0.163 | 0.221 | 0.158 |
| 1080p | 0.741 | 0.160 | 0.223 | 0.150 |
| 4K | 0.731 | 0.166 | 0.283 | 0.151 |

### Interpretation

1. **Worst reproducibility:** 4K with SSIM = 0.731
   - Ideal threshold: SSIM ≥ 0.99
   - Observed: SSIM = 0.731 → **26.9% structural dissimilarity**

2. **Implication for DLSS comparisons:**
   - **1440p**: Quality differences < ±0.163 SSIM may be noise
   - **1080p**: Quality differences < ±0.160 SSIM may be noise
   - **4K**: Quality differences < ±0.166 SSIM may be noise

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

