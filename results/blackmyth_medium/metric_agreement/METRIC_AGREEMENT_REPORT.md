# Metric Agreement Analysis Report
Generated: 2026-04-30 11:27:11
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.965 | -0.487 | -0.921 |
| **PSNR** | 0.965 | 1.000 | -0.550 | -0.966 |
| **LPIPS** | -0.487 | -0.550 | 1.000 | 0.701 |
| **FLIP** | -0.921 | -0.966 | 0.701 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.487 → Moderate negative correlation
2. **SSIM vs FLIP:** r = -0.921 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.701 → Strong positive correlation (both perceptual metrics)

**Interpretation:**
- ⚠️ **Low SSIM-LPIPS correlation suggests metrics capture different quality aspects**
- SSIM focuses on structural similarity (pixel-level)
- LPIPS focuses on perceptual features (neural network-based)
- This explains contradictory rankings (Performance > Quality in SSIM but opposite in LPIPS)

## Ranking Contradictions

Found 3 cases where metrics disagree on best mode:

### 1080p - SSIM-LPIPS disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.740)
- **LPIPS ranks Quality best** (value: 0.196)

### 1080p - SSIM-FLIP disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.740)
- **FLIP ranks Balanced best** (value: 5.155)

### 1440p - SSIM-LPIPS disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.735)
- **LPIPS ranks Balanced best** (value: 0.195)

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.740 (1) | 24.7 (1) | 0.232 (4) | 5.2 (2) |
| Balanced | 0.731 (2) | 24.5 (2) | 0.197 (2) | 5.2 (1) |
| Quality | 0.730 (3) | 24.4 (3) | 0.196 (1) | 5.3 (3) |
| Performance | 0.729 (4) | 24.1 (4) | 0.227 (3) | 5.5 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.735 (1) | 24.7 (1) | 0.225 (4) | 5.1 (1) |
| Performance | 0.723 (2) | 24.3 (3) | 0.206 (2) | 5.2 (3) |
| Balanced | 0.723 (3) | 24.4 (2) | 0.195 (1) | 5.2 (2) |
| Quality | 0.711 (4) | 23.8 (4) | 0.217 (3) | 5.6 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Quality | 0.717 (1) | 23.7 (1) | 0.197 (1) | 5.4 (1) |
| Performance | 0.701 (2) | 23.2 (3) | 0.237 (3) | 5.9 (2) |
| Ultra_Performance | 0.700 (3) | 23.2 (2) | 0.273 (4) | 6.1 (4) |
| Balanced | 0.699 (4) | 23.1 (4) | 0.232 (2) | 6.0 (3) |

