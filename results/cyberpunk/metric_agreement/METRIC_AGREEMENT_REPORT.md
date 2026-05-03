# Metric Agreement Analysis Report
Generated: 2026-04-30 11:27:51
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.977 | -0.993 | -0.985 |
| **PSNR** | 0.977 | 1.000 | -0.971 | -0.958 |
| **LPIPS** | -0.993 | -0.971 | 1.000 | 0.980 |
| **FLIP** | -0.985 | -0.958 | 0.980 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.993 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.985 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.980 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Ranking Contradictions

Found 3 cases where metrics disagree on best mode:

### 1080p - SSIM-LPIPS disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.917)
- **LPIPS ranks Performance best** (value: 0.126)

### 1080p - SSIM-FLIP disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.917)
- **FLIP ranks Performance best** (value: 3.171)

### 4K - SSIM-LPIPS disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.762)
- **LPIPS ranks Balanced best** (value: 0.351)

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.917 (1) | 29.3 (2) | 0.135 (2) | 3.2 (2) |
| Performance | 0.913 (2) | 29.4 (1) | 0.126 (1) | 3.2 (1) |
| Balanced | 0.835 (3) | 25.8 (3) | 0.204 (3) | 4.8 (3) |
| Quality | 0.795 (4) | 23.4 (4) | 0.329 (4) | 6.7 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Performance | 0.871 (1) | 24.4 (1) | 0.133 (1) | 5.3 (1) |
| Ultra_Performance | 0.588 (2) | 13.4 (3) | 0.614 (2) | 24.7 (3) |
| Balanced | 0.584 (3) | 13.4 (2) | 0.615 (3) | 24.6 (2) |
| Quality | 0.537 (4) | 13.0 (4) | 0.656 (4) | 26.2 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.762 (1) | 19.3 (1) | 0.357 (2) | 10.1 (1) |
| Balanced | 0.754 (2) | 19.1 (2) | 0.351 (1) | 10.3 (2) |
| Quality | 0.618 (3) | 13.7 (3) | 0.588 (3) | 23.2 (3) |
| Performance | 0.543 (4) | 12.8 (4) | 0.659 (4) | 27.8 (4) |

