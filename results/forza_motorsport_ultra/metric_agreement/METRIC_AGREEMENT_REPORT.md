# Metric Agreement Analysis Report
Generated: 2026-04-30 11:28:17
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.990 | -0.916 | -0.978 |
| **PSNR** | 0.990 | 1.000 | -0.905 | -0.984 |
| **LPIPS** | -0.916 | -0.905 | 1.000 | 0.954 |
| **FLIP** | -0.978 | -0.984 | 0.954 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.916 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.978 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.954 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Ranking Contradictions

Found 2 cases where metrics disagree on best mode:

### 1440p - SSIM-LPIPS disagreement

- **SSIM ranks Performance best** (value: 0.885)
- **LPIPS ranks Quality best** (value: 0.180)

### 4K - SSIM-LPIPS disagreement

- **SSIM ranks Balanced best** (value: 0.846)
- **LPIPS ranks Quality best** (value: 0.220)

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Balanced | 0.885 (1) | 24.9 (1) | 0.183 (1) | 4.2 (1) |
| Ultra_Performance | 0.879 (2) | 24.8 (2) | 0.214 (2) | 4.6 (2) |
| Performance | 0.853 (3) | 23.4 (3) | 0.225 (3) | 5.3 (3) |
| Quality | 0.843 (4) | 22.6 (4) | 0.229 (4) | 5.7 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Performance | 0.885 (1) | 24.9 (1) | 0.188 (2) | 4.0 (1) |
| Quality | 0.882 (2) | 24.7 (3) | 0.180 (1) | 4.2 (2) |
| Ultra_Performance | 0.880 (3) | 24.9 (2) | 0.212 (3) | 4.4 (3) |
| Balanced | 0.823 (4) | 21.7 (4) | 0.258 (4) | 6.6 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Balanced | 0.846 (1) | 23.4 (1) | 0.222 (2) | 5.2 (1) |
| Quality | 0.845 (2) | 23.1 (2) | 0.220 (1) | 5.2 (2) |
| Performance | 0.832 (3) | 22.2 (3) | 0.248 (3) | 6.0 (3) |
| Ultra_Performance | 0.821 (4) | 21.8 (4) | 0.280 (4) | 6.5 (4) |

