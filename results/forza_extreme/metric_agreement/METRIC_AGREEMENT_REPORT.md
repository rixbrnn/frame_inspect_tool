# Metric Agreement Analysis Report
Generated: 2026-04-30 11:28:04
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.995 | -0.973 | -0.987 |
| **PSNR** | 0.995 | 1.000 | -0.987 | -0.984 |
| **LPIPS** | -0.973 | -0.987 | 1.000 | 0.982 |
| **FLIP** | -0.987 | -0.984 | 0.982 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.973 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.987 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.982 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Ranking Contradictions

Found 2 cases where metrics disagree on best mode:

### 1080p - SSIM-LPIPS disagreement

- **SSIM ranks Quality best** (value: 0.790)
- **LPIPS ranks Balanced best** (value: 0.174)

### 1080p - SSIM-FLIP disagreement

- **SSIM ranks Quality best** (value: 0.790)
- **FLIP ranks Balanced best** (value: 6.320)

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Quality | 0.790 (1) | 22.7 (1) | 0.175 (2) | 6.4 (2) |
| Balanced | 0.790 (2) | 22.5 (2) | 0.174 (1) | 6.3 (1) |
| Ultra_Performance | 0.782 (3) | 21.9 (3) | 0.218 (3) | 7.0 (3) |
| Performance | 0.696 (4) | 18.3 (4) | 0.293 (4) | 10.5 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Quality | 0.679 (1) | 17.6 (1) | 0.334 (1) | 12.0 (1) |
| Balanced | 0.668 (2) | 17.0 (2) | 0.355 (2) | 12.9 (2) |
| Performance | 0.655 (3) | 16.5 (3) | 0.383 (3) | 14.1 (3) |
| Ultra_Performance | 0.642 (4) | 15.7 (4) | 0.422 (4) | 15.5 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Balanced | 0.793 (1) | 22.5 (1) | 0.195 (1) | 6.0 (1) |
| Quality | 0.751 (2) | 20.6 (2) | 0.249 (2) | 8.0 (2) |
| Performance | 0.734 (3) | 19.5 (3) | 0.278 (3) | 8.8 (3) |
| Ultra_Performance | 0.702 (4) | 17.8 (4) | 0.356 (4) | 11.5 (4) |

