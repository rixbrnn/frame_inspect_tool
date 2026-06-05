# Cross-Resolution Analysis Report
Generated: 2026-06-05 12:13:40
---

## Overview

- **Games analyzed:** 10
- **Configurations:** 120 (game × resolution × mode combinations)
- **Resolutions:** 1080p, 1440p, 4K
- **Modes:** Balanced, Performance, Quality, Ultra_Performance

## Sweet Spot Recommendations

### By Resolution

#### 1080p

**Most common sweet spot:** Ultra_Performance (9/10 games)

| Game | Mode | SSIM | LPIPS | Efficiency |
|------|------|------|-------|------------|
| blackmyth_medium | Ultra_Performance | 0.740 | 0.232 | 0.838 |
| cod_mw2_extreme | Ultra_Performance | 0.700 | 0.301 | 0.779 |
| cyberpunk | Ultra_Performance | 0.917 | 0.135 | 0.988 |
| forza_extreme | Ultra_Performance | 0.782 | 0.218 | 0.869 |
| forza_motorsport_ultra | Ultra_Performance | 0.879 | 0.214 | 0.925 |
| marvel_rivals_low | Performance | 0.785 | 0.141 | 0.832 |
| rdr2_ultra | Ultra_Performance | 0.496 | 0.481 | 0.570 |
| returnal_epic | Ultra_Performance | 0.830 | 0.206 | 0.903 |
| tomb_raider_highest_scene_1 | Ultra_Performance | 0.850 | 0.200 | 0.916 |
| watch_dogs_legion_very_high | Ultra_Performance | 0.756 | 0.145 | 0.894 |

#### 1440p

**Most common sweet spot:** Ultra_Performance (8/10 games)

| Game | Mode | SSIM | LPIPS | Efficiency |
|------|------|------|-------|------------|
| blackmyth_medium | Ultra_Performance | 0.735 | 0.225 | 0.840 |
| cod_mw2_extreme | Ultra_Performance | 0.737 | 0.276 | 0.814 |
| cyberpunk | Performance | 0.871 | 0.133 | 0.884 |
| forza_extreme | Ultra_Performance | 0.642 | 0.422 | 0.682 |
| forza_motorsport_ultra | Ultra_Performance | 0.880 | 0.212 | 0.926 |
| marvel_rivals_low | Ultra_Performance | 0.777 | 0.182 | 0.886 |
| rdr2_ultra | Performance | 0.551 | 0.361 | 0.585 |
| returnal_epic | Ultra_Performance | 0.843 | 0.212 | 0.906 |
| tomb_raider_highest_scene_1 | Ultra_Performance | 0.915 | 0.155 | 0.977 |
| watch_dogs_legion_very_high | Ultra_Performance | 0.679 | 0.188 | 0.829 |

#### 4K

**Most common sweet spot:** Ultra_Performance (9/10 games)

| Game | Mode | SSIM | LPIPS | Efficiency |
|------|------|------|-------|------------|
| blackmyth_medium | Ultra_Performance | 0.700 | 0.273 | 0.795 |
| cod_mw2_extreme | Ultra_Performance | 0.713 | 0.354 | 0.758 |
| cyberpunk | Ultra_Performance | 0.762 | 0.357 | 0.783 |
| forza_extreme | Ultra_Performance | 0.702 | 0.356 | 0.751 |
| forza_motorsport_ultra | Ultra_Performance | 0.821 | 0.280 | 0.857 |
| marvel_rivals_low | Ultra_Performance | 0.698 | 0.379 | 0.737 |
| rdr2_ultra | Ultra_Performance | 0.500 | 0.529 | 0.546 |
| returnal_epic | Ultra_Performance | 0.836 | 0.232 | 0.892 |
| tomb_raider_highest_scene_1 | Ultra_Performance | 0.858 | 0.233 | 0.903 |
| watch_dogs_legion_very_high | Balanced | 0.794 | 0.151 | 0.752 |

## General Recommendations

### Top 10 Configurations (All Games)

| Rank | Game | Config | SSIM | LPIPS | Efficiency |
|------|------|--------|------|-------|------------|
| 1 | cyberpunk | 1080p Ultra_Performance | 0.917 | 0.135 | 0.988 |
| 2 | tomb_raider_highest_scene_1 | 1440p Ultra_Performance | 0.915 | 0.155 | 0.977 |
| 3 | forza_motorsport_ultra | 1440p Ultra_Performance | 0.880 | 0.212 | 0.926 |
| 4 | forza_motorsport_ultra | 1080p Ultra_Performance | 0.879 | 0.214 | 0.925 |
| 5 | tomb_raider_highest_scene_1 | 1080p Ultra_Performance | 0.850 | 0.200 | 0.916 |
| 6 | cyberpunk | 1080p Performance | 0.913 | 0.126 | 0.911 |
| 7 | returnal_epic | 1440p Ultra_Performance | 0.843 | 0.212 | 0.906 |
| 8 | tomb_raider_highest_scene_1 | 4K Ultra_Performance | 0.858 | 0.233 | 0.903 |
| 9 | returnal_epic | 1080p Ultra_Performance | 0.830 | 0.206 | 0.903 |
| 10 | watch_dogs_legion_very_high | 1080p Ultra_Performance | 0.756 | 0.145 | 0.894 |

## Key Insights

1. **Most efficient mode overall:** Ultra_Performance (avg efficiency: 0.807)
2. **Best quality resolution:** 1080p (avg SSIM: 0.755)
3. **Resolution with most Pareto-optimal configs:** 1080p (1 configs)

