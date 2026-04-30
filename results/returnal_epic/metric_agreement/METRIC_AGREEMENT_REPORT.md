# Metric Agreement Analysis Report
Generated: 2026-04-30 11:28:56
---

## Overview

- **Comparisons analyzed:** 8
- **Resolutions:** 1080p, 1440p
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.979 | -0.691 | -0.972 |
| **PSNR** | 0.979 | 1.000 | -0.807 | -0.968 |
| **LPIPS** | -0.691 | -0.807 | 1.000 | 0.789 |
| **FLIP** | -0.972 | -0.968 | 0.789 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.691 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.972 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.789 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Balanced | 0.866 (1) | 25.2 (1) | 0.169 (1) | 5.1 (1) |
| Performance | 0.835 (2) | 23.9 (2) | 0.186 (2) | 5.9 (2) |
| Ultra_Performance | 0.830 (3) | 23.6 (3) | 0.206 (4) | 6.2 (3) |
| Quality | 0.816 (4) | 23.2 (4) | 0.200 (3) | 6.5 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Quality | 0.848 (1) | 24.3 (1) | 0.184 (1) | 5.5 (1) |
| Performance | 0.844 (2) | 24.1 (2) | 0.196 (2) | 5.7 (2) |
| Ultra_Performance | 0.843 (3) | 23.9 (3) | 0.212 (4) | 5.9 (3) |
| Balanced | 0.822 (4) | 23.3 (4) | 0.205 (3) | 6.3 (4) |

