# Reproducibility Analysis Report
Generated: 2026-05-03 22:16:12
---

## Overview

- **Games analyzed:** 3
- **Resolutions:** 1080p, 1440p, 4K
- **Total frames:** 1575

## Noise Floor Analysis

Minimum Detectable Difference (MDD) = 2 × standard deviation (95% confidence)

| Resolution | SSIM Consistency | SSIM MDD (±) | LPIPS Consistency | LPIPS MDD (±) |
|-----------|-----------------|--------------|-------------------|---------------|
| 1440p | 0.646 | 0.128 | 0.188 | 0.150 |
| 1080p | 0.628 | 0.119 | 0.195 | 0.131 |
| 4K | 0.763 | 0.169 | 0.139 | 0.116 |

### Interpretation

1. **Worst reproducibility:** 1080p with SSIM = 0.628
   - Ideal threshold: SSIM ≥ 0.99
   - Observed: SSIM = 0.628 → **37.2% structural dissimilarity**

2. **Implication for DLSS comparisons:**
   - **1440p**: Quality differences < ±0.128 SSIM may be noise
   - **1080p**: Quality differences < ±0.119 SSIM may be noise
   - **4K**: Quality differences < ±0.169 SSIM may be noise

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

