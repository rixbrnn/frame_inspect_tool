# Graphics Settings Comparison Report

## Ultra Graphics vs Low Graphics

### Overall Statistics

- **Comparisons analyzed:** 15
- **Mean SSIM improvement:** 0.0951 (15.82%)
- **Mean PSNR improvement:** 2.88 dB (21.46%)
- **Mean LPIPS improvement:** -0.1887
- **Mean FLIP improvement:** -5.9939
- **Mean VMAF improvement:** 15.68

### Top Improvements (by SSIM)

| resolution   | mode              |   delta_ssim |   ssim_change_pct |
|:-------------|:------------------|-------------:|------------------:|
| 1440p        | Quality           |     0.264934 |           51.7737 |
| 1440p        | Balanced          |     0.232903 |           41.6906 |
| 1440p        | Ultra_Performance |     0.218054 |           38.7741 |
| 4K           | Quality           |     0.206412 |           34.7267 |
| 1440p        | Consistency       |     0.112872 |           15.2761 |

### Top Declines (by SSIM)

| resolution   | mode              |   delta_ssim |   ssim_change_pct |
|:-------------|:------------------|-------------:|------------------:|
| 1080p        | Ultra_Performance |   -0.0787042 |          -8.70402 |
| 1080p        | Performance       |   -0.0392917 |          -4.36082 |
| 1440p        | Performance       |   -0.0325129 |          -3.77775 |
| 1080p        | Consistency       |    0.0176176 |           2.21752 |
| 4K           | Balanced          |    0.0601152 |           8.2399  |

### Detailed Comparison Table

| resolution   | mode              |   ssim_mean_ds1 |   ssim_mean_ds2 |   delta_ssim |   psnr_mean_ds1 |   psnr_mean_ds2 |   delta_psnr |
|:-------------|:------------------|----------------:|----------------:|-------------:|----------------:|----------------:|-------------:|
| 1440p        | Consistency       |        0.738882 |        0.851755 |    0.112872  |         20.4204 |         24.301  |     3.8806   |
| 1080p        | Quality           |        0.761176 |        0.862524 |    0.101348  |         23.3655 |         25.161  |     1.79541  |
| 1440p        | Ultra_Performance |        0.562371 |        0.780426 |    0.218054  |         13.4006 |         21.9987 |     8.59811  |
| 1080p        | Balanced          |        0.809158 |        0.901404 |    0.0922462 |         25.7326 |         26.3929 |     0.660333 |
| 1440p        | Balanced          |        0.558645 |        0.791547 |    0.232903  |         13.4154 |         22.4479 |     9.03244  |
| 1440p        | Quality           |        0.511716 |        0.77665  |    0.264934  |         12.9765 |         22.0629 |     9.08634  |
| 4K           | Performance       |        0.732711 |        0.836681 |    0.10397   |         19.2559 |         23.424  |     4.16812  |
| 1080p        | Consistency       |        0.794472 |        0.81209  |    0.0176176 |         24.852  |         23.5463 |    -1.30566  |
| 1080p        | Performance       |        0.901016 |        0.861724 |   -0.0392917 |         29.3345 |         24.7543 |    -4.58019  |
| 4K           | Balanced          |        0.729562 |        0.789677 |    0.0601152 |         19.1155 |         21.8876 |     2.77208  |
| 4K           | Consistency       |        0.733699 |        0.815756 |    0.0820573 |         19.4116 |         22.7194 |     3.30781  |
| 1440p        | Performance       |        0.860641 |        0.828128 |   -0.0325129 |         24.3979 |         23.5152 |    -0.88264  |
| 4K           | Quality           |        0.594389 |        0.8008   |    0.206412  |         13.7356 |         22.2855 |     8.54991  |
| 4K           | Ultra_Performance |        0.736665 |        0.82049  |    0.0838255 |         19.2668 |         22.9145 |     3.64769  |
| 1080p        | Ultra_Performance |        0.904228 |        0.825524 |   -0.0787042 |         29.2896 |         23.8028 |    -5.48675  |
