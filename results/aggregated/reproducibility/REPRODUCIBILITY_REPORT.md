# Reproducibility Analysis Report
Generated: 2026-04-30 10:50:11
---

## Overview

- **Games analyzed:** 28
- **Resolutions:** 1080p, 1440p, 4K
- **Total frames:** 13915

## Noise Floor Analysis

Minimum Detectable Difference (MDD) = 2 × standard deviation (95% confidence)

| Resolution | SSIM Consistency | SSIM MDD (±) | LPIPS Consistency | LPIPS MDD (±) |
|-----------|-----------------|--------------|-------------------|---------------|
| 1440p | 0.769 | 0.163 | 0.216 | 0.154 |
| 1080p | 0.761 | 0.163 | 0.218 | 0.146 |
| 4K | 0.713 | 0.165 | 0.312 | 0.155 |

### Interpretation

1. **Worst reproducibility:** 4K with SSIM = 0.713
   - Ideal threshold: SSIM ≥ 0.99
   - Observed: SSIM = 0.713 → **28.7% structural dissimilarity**

2. **Implication for DLSS comparisons:**
   - **1440p**: Quality differences < ±0.163 SSIM may be noise
   - **1080p**: Quality differences < ±0.163 SSIM may be noise
   - **4K**: Quality differences < ±0.165 SSIM may be noise

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

