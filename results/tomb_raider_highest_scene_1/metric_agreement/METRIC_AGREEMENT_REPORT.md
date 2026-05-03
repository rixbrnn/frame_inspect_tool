# Metric Agreement Analysis Report
Generated: 2026-04-30 11:29:09
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.901 | -0.711 | -0.880 |
| **PSNR** | 0.901 | 1.000 | -0.908 | -0.979 |
| **LPIPS** | -0.711 | -0.908 | 1.000 | 0.958 |
| **FLIP** | -0.880 | -0.979 | 0.958 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.711 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.880 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.958 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Ranking Contradictions

Found 1 cases where metrics disagree on best mode:

### 1440p - SSIM-LPIPS disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.915)
- **LPIPS ranks Quality best** (value: 0.147)

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Performance | 0.893 (1) | 28.6 (1) | 0.149 (1) | 2.7 (1) |
| Quality | 0.860 (2) | 27.4 (2) | 0.151 (2) | 3.1 (2) |
| Ultra_Performance | 0.850 (3) | 26.6 (3) | 0.200 (3) | 3.6 (3) |
| Balanced | 0.833 (4) | 25.7 (4) | 0.217 (4) | 4.1 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.915 (1) | 30.1 (1) | 0.155 (2) | 2.3 (1) |
| Quality | 0.895 (2) | 28.7 (2) | 0.147 (1) | 2.6 (2) |
| Performance | 0.864 (3) | 27.2 (3) | 0.170 (3) | 3.2 (3) |
| Balanced | 0.861 (4) | 27.1 (4) | 0.170 (4) | 3.3 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.858 (1) | 25.3 (1) | 0.233 (1) | 4.0 (1) |
| Quality | 0.850 (2) | 24.9 (2) | 0.247 (2) | 4.2 (2) |
| Balanced | 0.849 (3) | 24.8 (3) | 0.254 (3) | 4.3 (3) |
| Performance | 0.838 (4) | 24.1 (4) | 0.313 (4) | 5.1 (4) |

