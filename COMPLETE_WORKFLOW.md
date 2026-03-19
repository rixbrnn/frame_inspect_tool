# Complete Workflow: From Recording to Analysis

This guide shows the complete pipeline from recording benchmarks to generating results.

## Phase 0: Validate Benchmark Stability (REQUIRED FIRST!)

Before doing ANY data collection, validate that your benchmark is reproducible.

### Step 1: Record Same Benchmark Twice

```bash
# Record benchmark with DLAA twice (or any consistent setting)
# In game: Run benchmark → Record as DLAA_run1.mp4
# In game: Run benchmark → Record as DLAA_run2.mp4

# IMPORTANT: Use IDENTICAL settings:
# - Same graphics settings
# - Same resolution (4K)
# - Same DLSS/DLAA mode
# - Same MSI Afterburner OSD
```

### Step 2: Validate Stability

```bash
python validate_benchmark.py \
    --video1 ../tcc/recordings/validation/DLAA_run1.mp4 \
    --video2 ../tcc/recordings/validation/DLAA_run2.mp4 \
    --game "Cyberpunk 2077" \
    --output ../tcc/results/benchmark_validation.json
```

**Expected Output:**
```
BENCHMARK STABILITY VALIDATION
============================================================
Game: Cyberpunk 2077
Comparing: DLAA_run1.mp4 vs DLAA_run2.mp4

Running comparison (using existing tools)...
Comparing frames using SSIM...

============================================================
                            RESULTS
============================================================

Average SSIM: 99.3%
Threshold:    99.0%

✓ BENCHMARK IS STABLE
  → Suitable for DLSS comparison
  → Proceed with data collection
```

### Step 3: Interpret Results

**If SSIM ≥ 99.0%:** ✅ **PROCEED**
- Benchmark is deterministic
- Safe to use for DLSS comparison
- Continue to Phase 1

**If SSIM < 99.0%:** ❌ **DO NOT PROCEED**
- Benchmark has random elements
- Results will be unreliable
- Try different game/benchmark

## Phase 1: Data Collection (After Validation!)

Once benchmark is validated, record all DLSS modes:

```bash
# Record each mode once (benchmark is proven stable!)
# 1. DLAA 4K    → DLAA_4K.mp4
# 2. Quality    → Quality.mp4
# 3. Balanced   → Balanced.mp4
# 4. Performance → Performance.mp4
# 5. Ultra Performance → Ultra_Performance.mp4
```

**Recording Settings:**
- MSI Afterburner OSD enabled (FPS counter visible)
- Same graphics settings for all modes
- 60 seconds minimum
- FFV1 or lossless codec

## Phase 2: Process Videos

### Step 1: Convert to CFR 60 FPS

```bash
for mode in DLAA_4K Quality Balanced Performance Ultra_Performance; do
    ffmpeg -i ../tcc/recordings/raw/${mode}.mp4 \
        -vf "fps=60" -t 60 \
        -c:v libx264 -crf 18 -preset slow \
        -pix_fmt yuv420p \
        ../tcc/recordings/processed/${mode}_60fps.mp4
done
```

### Step 2: Calibrate FPS ROI (Once)

```bash
python calibrate_fps_roi.py \
    --video ../tcc/recordings/processed/DLAA_4K_60fps.mp4
```

Press SPACE to test, S to save coordinates.

### Step 3: Extract FPS from OSD

```bash
ROI="1700,50,200,80"  # From calibration

for mode in DLAA_4K Quality Balanced Performance Ultra_Performance; do
    python src/fps_ocr_extractor.py \
        --video ../tcc/recordings/processed/${mode}_60fps.mp4 \
        --roi ${ROI} \
        --output ../tcc/fps_data/${mode}_fps.json
done
```

## Phase 3: Quality Analysis

### Step 1: Find Video Overlap (Fast!)

```bash
# Sync each mode with baseline
for mode in Quality Balanced Performance Ultra_Performance; do
    python src/video_sync_fast.py \
        --video1 ../tcc/recordings/processed/DLAA_4K_60fps.mp4 \
        --video2 ../tcc/recordings/processed/${mode}_60fps.mp4 \
        --sample-rate 30 \
        --refine

    # Note the output frame ranges for cutting
done
```

### Step 2: Cut Videos to Overlap (Optional)

If videos don't perfectly overlap, cut them:

```bash
# Example: Video 1 overlap is frames 120-3500
# Example: Video 2 overlap is frames 150-3530

ffmpeg -i DLAA_4K_60fps.mp4 \
    -vf "select='between(n\,120\,3500)'" \
    -vsync 0 DLAA_cut.mp4

ffmpeg -i Quality_60fps.mp4 \
    -vf "select='between(n\,150\,3530)'" \
    -vsync 0 Quality_cut.mp4
```

### Step 3: Compare Quality

```bash
for mode in Quality Balanced Performance Ultra_Performance; do
    python src/app.py \
        --ground-truth ../tcc/recordings/processed/DLAA_4K_60fps.mp4 \
        --compare ../tcc/recordings/processed/${mode}_60fps.mp4 \
        --output ../tcc/quality_data/${mode}_comparison.json
done
```

### Step 4: Temporal Analysis

```bash
for mode in Quality Balanced Performance Ultra_Performance; do
    python temporal_analyzer_ocr.py \
        --fps-json ../tcc/fps_data/${mode}_fps.json \
        --video-test ../tcc/recordings/processed/${mode}_60fps.mp4 \
        --video-ground-truth ../tcc/recordings/processed/DLAA_4K_60fps.mp4 \
        --mode-name ${mode} \
        --output ../tcc/temporal_data/${mode}_temporal.json \
        --plot-timeline ../tcc/results/charts/${mode}_timeline.png \
        --plot-correlation ../tcc/results/charts/${mode}_correlation.png
done
```

## Phase 4: Generate Final Results

```bash
# Consolidate all data and generate trade-off analysis
python src/performance_quality_analyzer.py \
    --fps-dir ../tcc/fps_data \
    --quality-dir ../tcc/quality_data \
    --baseline DLAA_4K \
    --output-csv ../tcc/results/final_results.csv \
    --output-json ../tcc/results/final_results.json \
    --plot-fps-vs-quality ../tcc/results/charts/fps_vs_quality.png
```

## Summary Timeline

| Phase | Task | Time | Can Fail? |
|-------|------|------|-----------|
| **Phase 0** | Validate benchmark | ~5 min | ✅ YES - Try different game |
| **Phase 1** | Record 5 modes | ~30 min | ❌ Must succeed |
| **Phase 2** | Process videos | ~10 min | ❌ Automated |
| **Phase 3** | Extract FPS (OCR) | ~30 sec | ❌ Usually works |
| **Phase 4** | Sync videos (fast!) | ~5 sec | ❌ Should work |
| **Phase 5** | Quality analysis | ~20 min | ❌ Automated |
| **Phase 6** | Generate results | ~2 min | ❌ Automated |
| **TOTAL** | | ~1 hour | Phase 0 is gate |

## Key Points

1. **Always validate first** - Phase 0 is mandatory
2. **Validation is per-game** - Must validate each game's benchmark
3. **Recording is once** - Validated benchmarks are stable
4. **OCR eliminates sync issues** - FPS extracted from frames
5. **Fast sync** - 844,000x faster than old method
6. **Automated pipeline** - Mostly hands-off after recording

## Troubleshooting

### Validation fails (SSIM < 99%)
- Try different benchmark scene
- Check for AI/physics elements
- Consider different game

### OCR can't read FPS
- Re-calibrate ROI
- Check MSI Afterburner OSD is visible
- Try different font/color

### Sync finds no overlap
- Benchmarks might be different scenes
- Check videos are from same game
- Manually verify start/end match

### Quality comparison seems wrong
- Verify videos are synced correctly
- Check frame counts match
- Inspect a few frames visually

## Next Steps

1. **Choose game** with integrated benchmark
2. **Validate** benchmark stability (Phase 0)
3. If validated, **record all modes** (Phase 1)
4. **Run automated pipeline** (Phases 2-6)
5. **Analyze results** for thesis
