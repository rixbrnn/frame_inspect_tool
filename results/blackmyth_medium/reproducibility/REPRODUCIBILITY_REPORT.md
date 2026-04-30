# Reproducibility Analysis Report
Generated: 2026-04-30 11:27:14
---

## Overview

- **Games analyzed:** 3
- **Resolutions:** 1080p, 1440p, 4K
- **Total frames:** 2545

## Noise Floor Analysis

Minimum Detectable Difference (MDD) = 2 × standard deviation (95% confidence)

| Resolution | SSIM Consistency | SSIM MDD (±) | LPIPS Consistency | LPIPS MDD (±) |
|-----------|-----------------|--------------|-------------------|---------------|
| 1440p | 0.716 | 0.145 | 0.175 | 0.101 |
| 1080p | 0.726 | 0.139 | 0.167 | 0.104 |
| 4K | 0.690 | 0.133 | 0.215 | 0.108 |

### Interpretation

1. **Worst reproducibility:** 4K with SSIM = 0.690
   - Ideal threshold: SSIM ≥ 0.99
   - Observed: SSIM = 0.690 → **31.0% structural dissimilarity**

2. **Implication for DLSS comparisons:**
   - **1440p**: Quality differences < ±0.145 SSIM may be noise
   - **1080p**: Quality differences < ±0.139 SSIM may be noise
   - **4K**: Quality differences < ±0.133 SSIM may be noise

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

