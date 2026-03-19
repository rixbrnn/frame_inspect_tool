# Validation Recordings - blackmyth @ 1080p

## Purpose
Record the same benchmark twice to verify it's deterministic (no random AI, physics, etc.)

## Steps

1. **Record first run:**
   - Start benchmark
   - Record 60+ seconds
   - Save as `run1.mp4`

2. **Record second run:**
   - **Immediately** restart and run the exact same benchmark
   - Record 60+ seconds
   - Save as `run2.mp4`

3. **Validate stability:**
   ```bash
   python scripts/validate_benchmark.py \
       --video1 recordings/blackmyth/1080p/validation/run1.mp4 \
       --video2 recordings/blackmyth/1080p/validation/run2.mp4 \
       --game "Blackmyth" \
       --output recordings/blackmyth/1080p/validation/validation.json
   ```

4. **Check results:**
   - ✅ SSIM ≥ 99% → Benchmark is stable, proceed with data collection
   - ❌ SSIM < 99% → Benchmark has non-deterministic elements, find different scene

## Expected Files
- `run1.mp4` - First recording
- `run2.mp4` - Second recording
- `run1_60fps.mp4` - CFR version (auto-generated)
- `run2_60fps.mp4` - CFR version (auto-generated)
- `validation.json` - Validation results
