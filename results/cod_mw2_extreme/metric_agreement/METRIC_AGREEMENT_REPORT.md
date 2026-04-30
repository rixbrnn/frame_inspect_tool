# Metric Agreement Analysis Report
Generated: 2026-04-30 11:27:25
---

## Overview

- **Comparisons analyzed:** 12
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Correlation Analysis

### Pearson Correlation (Linear Relationship)

| Metric | SSIM | PSNR | LPIPS | FLIP |
|--------|------|------|-------|------|
| **SSIM** | 1.000 | 0.559 | -0.683 | -0.644 |
| **PSNR** | 0.559 | 1.000 | -0.969 | -0.986 |
| **LPIPS** | -0.683 | -0.969 | 1.000 | 0.977 |
| **FLIP** | -0.644 | -0.986 | 0.977 | 1.000 |

### Key Findings

1. **SSIM vs LPIPS:** r = -0.683 → Strong negative correlation (expected)
2. **SSIM vs FLIP:** r = -0.644 → Strong negative correlation (expected)
3. **LPIPS vs FLIP:** r = 0.977 → Strong positive correlation (both perceptual metrics)

**Interpretation:**

## Ranking Contradictions

Found 1 cases where metrics disagree on best mode:

### 1440p - SSIM-LPIPS disagreement

- **SSIM ranks Ultra_Performance best** (value: 0.737)
- **LPIPS ranks Quality best** (value: 0.267)

## Detailed Rankings by Resolution

### 1080p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Quality | 0.733 (1) | 21.6 (1) | 0.246 (1) | 9.2 (1) |
| Balanced | 0.732 (2) | 21.4 (2) | 0.250 (2) | 9.5 (2) |
| Performance | 0.727 (3) | 21.3 (3) | 0.260 (3) | 9.5 (3) |
| Ultra_Performance | 0.700 (4) | 20.2 (4) | 0.301 (4) | 11.0 (4) |

### 1440p

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Ultra_Performance | 0.737 (1) | 21.4 (1) | 0.276 (3) | 9.5 (1) |
| Quality | 0.729 (2) | 21.0 (2) | 0.267 (1) | 10.1 (3) |
| Performance | 0.726 (3) | 20.9 (3) | 0.271 (2) | 9.9 (2) |
| Balanced | 0.712 (4) | 20.3 (4) | 0.299 (4) | 10.7 (4) |

### 4K

| Mode | SSIM (rank) | PSNR (rank) | LPIPS (rank) | FLIP (rank) |
|------|-------------|-------------|--------------|-------------|
| Quality | 0.786 (1) | 21.8 (1) | 0.218 (1) | 8.4 (1) |
| Performance | 0.728 (2) | 19.3 (2) | 0.323 (2) | 11.6 (2) |
| Balanced | 0.720 (3) | 18.9 (3) | 0.341 (3) | 12.3 (3) |
| Ultra_Performance | 0.713 (4) | 18.4 (4) | 0.354 (4) | 13.5 (4) |

