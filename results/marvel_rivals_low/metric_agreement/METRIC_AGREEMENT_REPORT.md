# Metric Agreement Analysis Report
Generated: 2026-04-30 11:28:30
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.942 | -0.859 | -0.937 |
| **PSNR** | 0.942 | 1.000 | -0.979 | -0.993 |
| **LPIPS** | -0.859 | -0.979 | 1.000 | 0.980 |
| **FLIP** | -0.937 | -0.993 | 0.980 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.859 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.937 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.980 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Ranking Contradictions

Found 2 cases where metrics disagree on best mode:

### 4K - SSIM-LPIPS disagreement

- **SSIM ranks Performance best** (value: 0.711)
- **LPIPS ranks Quality best** (value: 0.323)

### 4K - SSIM-FLIP disagreement

- **SSIM ranks Performance best** (value: 0.711)
- **FLIP ranks Quality best** (value: 10.887)

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Performance | 0.785 (1) | 22.3 (1) | 0.141 (1) | 6.4 (1) |
| Ultra_Performance | 0.687 (2) | 19.2 (2) | 0.278 (2) | 10.5 (2) |
| Quality | 0.665 (3) | 18.8 (3) | 0.295 (3) | 11.2 (3) |
| Balanced | 0.657 (4) | 18.5 (4) | 0.315 (4) | 11.7 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Quality | 0.862 (1) | 23.8 (1) | 0.113 (1) | 5.0 (1) |
| Ultra_Performance | 0.777 (2) | 21.5 (2) | 0.182 (2) | 6.9 (2) |
| Performance | 0.687 (3) | 18.8 (3) | 0.300 (3) | 10.9 (3) |
| Balanced | 0.680 (4) | 18.6 (4) | 0.315 (4) | 11.2 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Performance | 0.711 (1) | 18.8 (2) | 0.327 (2) | 10.9 (2) |
| Quality | 0.710 (2) | 18.8 (1) | 0.323 (1) | 10.9 (1) |
| Balanced | 0.707 (3) | 18.6 (3) | 0.338 (3) | 11.3 (3) |
| Ultra_Performance | 0.698 (4) | 18.1 (4) | 0.379 (4) | 12.4 (4) |

