# Cross-Resolution Analysis Report
Generated: 2026-04-30 10:55:35
---

## Overview

- **Games analyzed:** 10
- **Configurations:** 112 (game × resolution × mode combinations)
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Sweet Spot Recommendations

### By Resolution

#### 1080p

**Most common sweet spot:** Ultra_Performance (9/10 games)

| Game | Mode | SSIM | LPIPS | Efficiency |
|------|------|------|-------|------------|
| blackmyth_medium | Ultra_Performance | 0.740 | 0.232 | 0.833 |
| cod_mw2_extreme | Ultra_Performance | 0.700 | 0.301 | 0.774 |
| cyberpunk | Ultra_Performance | 0.917 | 0.135 | 0.981 |
| cyberpunk_low | Ultra_Performance | 0.841 | 0.161 | 0.926 |
| forza_extreme | Ultra_Performance | 0.782 | 0.218 | 0.863 |
| forza_motorsport_ultra | Ultra_Performance | 0.879 | 0.214 | 0.919 |
| marvel_rivals_low | Performance | 0.785 | 0.141 | 0.825 |
| rdr2_ultra | Ultra_Performance | 0.496 | 0.481 | 0.567 |
| returnal_epic | Ultra_Performance | 0.830 | 0.206 | 0.896 |
| tomb_raider_highest_scene_1 | Ultra_Performance | 0.850 | 0.200 | 0.910 |

#### 1440p

**Most common sweet spot:** Ultra_Performance (8/10 games)

| Game | Mode | SSIM | LPIPS | Efficiency |
|------|------|------|-------|------------|
| blackmyth_medium | Ultra_Performance | 0.735 | 0.225 | 0.834 |
| cod_mw2_extreme | Ultra_Performance | 0.737 | 0.276 | 0.808 |
| cyberpunk | Performance | 0.871 | 0.133 | 0.877 |
| cyberpunk_low | Ultra_Performance | 0.802 | 0.224 | 0.871 |
| forza_extreme | Ultra_Performance | 0.642 | 0.422 | 0.679 |
| forza_motorsport_ultra | Ultra_Performance | 0.880 | 0.212 | 0.920 |
| marvel_rivals_low | Ultra_Performance | 0.777 | 0.182 | 0.879 |
| rdr2_ultra | Performance | 0.551 | 0.361 | 0.581 |
| returnal_epic | Ultra_Performance | 0.843 | 0.212 | 0.900 |
| tomb_raider_highest_scene_1 | Ultra_Performance | 0.915 | 0.155 | 0.970 |

#### 4K

**Most common sweet spot:** Ultra_Performance (8/8 games)

| Game | Mode | SSIM | LPIPS | Efficiency |
|------|------|------|-------|------------|
| blackmyth_medium | Ultra_Performance | 0.700 | 0.273 | 0.789 |
| cod_mw2_extreme | Ultra_Performance | 0.713 | 0.354 | 0.754 |
| cyberpunk | Ultra_Performance | 0.762 | 0.357 | 0.779 |
| forza_extreme | Ultra_Performance | 0.702 | 0.356 | 0.746 |
| forza_motorsport_ultra | Ultra_Performance | 0.821 | 0.280 | 0.852 |
| marvel_rivals_low | Ultra_Performance | 0.698 | 0.379 | 0.733 |
| rdr2_ultra | Ultra_Performance | 0.500 | 0.529 | 0.544 |
| tomb_raider_highest_scene_1 | Ultra_Performance | 0.858 | 0.233 | 0.897 |

## General Recommendations

### Top 10 Configurations (All Games)

| Rank | Game | Config | SSIM | LPIPS | Efficiency |
|------|------|--------|------|-------|------------|
| 1 | cyberpunk | 1080p Ultra_Performance | 0.917 | 0.135 | 0.981 |
| 2 | tomb_raider_highest_scene_1 | 1440p Ultra_Performance | 0.915 | 0.155 | 0.970 |
| 3 | cyberpunk_low | 1080p Ultra_Performance | 0.841 | 0.161 | 0.926 |
| 4 | forza_motorsport_ultra | 1440p Ultra_Performance | 0.880 | 0.212 | 0.920 |
| 5 | forza_motorsport_ultra | 1080p Ultra_Performance | 0.879 | 0.214 | 0.919 |
| 6 | tomb_raider_highest_scene_1 | 1080p Ultra_Performance | 0.850 | 0.200 | 0.910 |
| 7 | cyberpunk | 1080p Performance | 0.913 | 0.126 | 0.904 |
| 8 | returnal_epic | 1440p Ultra_Performance | 0.843 | 0.212 | 0.900 |
| 9 | tomb_raider_highest_scene_1 | 4K Ultra_Performance | 0.858 | 0.233 | 0.897 |
| 10 | returnal_epic | 1080p Ultra_Performance | 0.830 | 0.206 | 0.896 |

## Key Insights

1. **Most efficient mode overall:** Ultra_Performance (avg efficiency: 0.805)
2. **Best quality resolution:** 1080p (avg SSIM: 0.770)
3. **Resolution with most Pareto-optimal configs:** 1080p (1 configs)

