# Metric Agreement Analysis Report
Generated: 2026-05-03 22:15:20
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.991 | -0.895 | -0.977 |
| **PSNR** | 0.991 | 1.000 | -0.942 | -0.992 |
| **LPIPS** | -0.895 | -0.942 | 1.000 | 0.963 |
| **FLIP** | -0.977 | -0.992 | 0.963 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.895 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.977 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.963 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Balanced | 0.811 (1) | 24.9 (1) | 0.135 (1) | 5.3 (1) |
| Ultra_Performance | 0.756 (2) | 23.6 (2) | 0.145 (2) | 6.2 (2) |
| Quality | 0.676 (3) | 21.4 (3) | 0.195 (3) | 7.8 (3) |
| Performance | 0.623 (4) | 20.2 (4) | 0.241 (4) | 9.3 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Quality | 0.738 (1) | 23.1 (1) | 0.159 (1) | 6.3 (1) |
| Performance | 0.704 (2) | 22.3 (2) | 0.181 (2) | 7.2 (2) |
| Ultra_Performance | 0.679 (3) | 21.7 (3) | 0.188 (3) | 7.7 (3) |
| Balanced | 0.629 (4) | 20.2 (4) | 0.241 (4) | 9.1 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Balanced | 0.794 (1) | 24.2 (1) | 0.151 (1) | 5.4 (1) |
| Quality | 0.656 (2) | 20.9 (2) | 0.229 (2) | 8.4 (2) |
| Performance | 0.629 (3) | 19.8 (3) | 0.274 (3) | 9.6 (3) |
| Ultra_Performance | 0.618 (4) | 19.3 (4) | 0.323 (4) | 10.4 (4) |

