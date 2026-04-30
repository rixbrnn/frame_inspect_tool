# Metric Agreement Analysis Report
Generated: 2026-04-30 11:27:38
---

## Overview

- **Comparisons analyzed:** 8
- **Resolutions:** 1080p, 1440p
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.995 | -0.971 | -0.990 |
| **PSNR** | 0.995 | 1.000 | -0.971 | -0.990 |
| **LPIPS** | -0.971 | -0.971 | 1.000 | 0.988 |
| **FLIP** | -0.990 | -0.990 | 0.988 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.971 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.990 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.988 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Balanced | 0.908 (1) | 26.4 (1) | 0.099 (1) | 4.1 (1) |
| Quality | 0.873 (2) | 25.2 (2) | 0.116 (2) | 4.8 (2) |
| Performance | 0.872 (3) | 24.8 (3) | 0.124 (3) | 4.9 (3) |
| Ultra_Performance | 0.841 (4) | 23.8 (4) | 0.161 (4) | 5.5 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Performance | 0.843 (1) | 23.5 (1) | 0.154 (1) | 5.7 (1) |
| Balanced | 0.811 (2) | 22.4 (2) | 0.183 (2) | 6.4 (2) |
| Ultra_Performance | 0.802 (3) | 22.0 (4) | 0.224 (4) | 7.0 (4) |
| Quality | 0.798 (4) | 22.1 (3) | 0.207 (3) | 6.9 (3) |

