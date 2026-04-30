# Metric Agreement Analysis Report
Generated: 2026-04-30 11:28:43
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.935 | -0.939 | -0.966 |
| **PSNR** | 0.935 | 1.000 | -0.997 | -0.991 |
| **LPIPS** | -0.939 | -0.997 | 1.000 | 0.992 |
| **FLIP** | -0.966 | -0.991 | 0.992 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.939 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.966 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.992 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Ranking Contradictions

Found 2 cases where metrics disagree on best mode:

### 1080p - SSIM-LPIPS disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.496)
- **LPIPS ranks Performance best** (value: 0.451)

### 1080p - SSIM-FLIP disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.496)
- **FLIP ranks Performance best** (value: 16.371)

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.496 (1) | 17.2 (2) | 0.481 (3) | 16.5 (2) |
| Performance | 0.495 (2) | 17.7 (1) | 0.451 (1) | 16.4 (1) |
| Quality | 0.477 (3) | 17.1 (3) | 0.473 (2) | 17.0 (3) |
| Balanced | 0.474 (4) | 16.9 (4) | 0.489 (4) | 17.6 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Performance | 0.551 (1) | 19.1 (1) | 0.361 (1) | 12.2 (1) |
| Ultra_Performance | 0.507 (2) | 17.1 (3) | 0.475 (3) | 16.5 (2) |
| Quality | 0.498 (3) | 17.3 (2) | 0.465 (2) | 16.8 (3) |
| Balanced | 0.480 (4) | 16.7 (4) | 0.497 (4) | 17.8 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.500 (1) | 16.0 (1) | 0.529 (1) | 18.5 (1) |
| Quality | 0.447 (2) | 15.0 (2) | 0.579 (2) | 21.1 (2) |
| Performance | 0.437 (3) | 14.6 (3) | 0.595 (3) | 22.5 (3) |
| Balanced | 0.371 (4) | 13.2 (4) | 0.668 (4) | 26.0 (4) |

