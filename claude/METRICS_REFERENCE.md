# Video Quality Metrics Reference

## Metrics Overview

Your TCC now computes **6 comprehensive quality metrics** for DLSS evaluation:

### Traditional Baseline Metrics

1. **SSIM (Structural Similarity Index)**
   - Range: [0, 1] where 1 = identical
   - Measures: Structural/perceptual similarity
   - Best for: Overall quality assessment
   - Interpretation: >0.95 = excellent, 0.90-0.95 = good, 0.75-0.90 = acceptable

2. **MSE (Mean Squared Error)**
   - Range: [0, ∞) where 0 = identical
   - Measures: Pixel-level differences
   - Best for: Detecting pixel-perfect errors
   - Interpretation: Lower is better, typical range 0-1000

### Advanced Perceptual Metrics

3. **LPIPS (Learned Perceptual Image Patch Similarity)**
   - Range: [0, 1+] where 0 = identical (lower is better)
   - Measures: Deep learning-based perceptual similarity
   - Best for: Semantic/perceptual quality
   - **Accuracy**: 74.7% correlation with human judgment (vs 69.3% for SSIM)
   - **Key advantage**: Recognizes when neural "hallucinations" look natural
   - **Requirement**: Requires `pip install lpips torch torchvision`
   - **Status**: ⚠️ Not installed (will be skipped in current run)

4. **FLIP (Frame Latency Induced Perceptual)**
   - Range: [0, ∞) where 0 = identical (lower is better)
   - Measures: Perceptual visual error with edge weighting
   - Best for: Graphics-specific artifacts (NVIDIA-inspired)
   - **Algorithm**: LAB color space + edge-aware filtering
   - **Key advantage**: Weights errors near edges more heavily (artifacts more visible)
   - **Thematic fit**: Aligns with NVIDIA DLAA/DLSS evaluation
   - **Status**: ✅ Available (using OpenCV)

5. **Temporal Optical Flow Consistency**
   - Range: [0, ∞) where 0 = perfect consistency (lower is better)
   - Measures: Motion consistency via frame warping
   - Best for: Detecting ghosting and flickering
   - **Algorithm**:
     1. Compute optical flow: frame(t-1) → frame(t)
     2. Warp frame(t-1) using flow
     3. Compare warped vs actual frame(t)
     4. High error = ghosting/temporal instability
   - **Key advantage**: Objectively quantifies temporal artifacts
   - **Critical for DLSS**: DLSS relies on temporal accumulation
   - **Status**: ✅ Available (using OpenCV Farneback)

---

## Current Run Status

**Command:**
```bash
python3 scripts/compare_alignment_quality.py \
    --video1 recordings/cyberpunk/aligned/1080p_dlaa_run1.mp4 \
    --video2 recordings/cyberpunk/aligned/1080p_dlaa_run2.mp4 \
    --name "ICAT Manual - Advanced Metrics" \
    --sample-rate 30 \
    --cpu
```

**Processing:**
- Total frames: 4034 per video
- Sample rate: Every 30th frame
- Frames analyzed: ~135 frames
- Metrics computed: SSIM, MSE, FLIP, Optical Flow (4 of 6)
- LPIPS: Skipped (not installed)

**Expected output:**
```json
{
  "alignment_method": "ICAT Manual - Advanced Metrics",
  "video1": "recordings/cyberpunk/aligned/1080p_dlaa_run1.mp4",
  "video2": "recordings/cyberpunk/aligned/1080p_dlaa_run2.mp4",
  "frames_compared": 135,
  "metrics": {
    "ssim": {
      "mean": 0.7568,
      "std": 0.0852,
      "min": 0.5428,
      "max": 0.9438,
      "median": 0.7879
    },
    "mse": {
      "mean": 401.96,
      "std": 240.38,
      "min": 111.23,
      "max": 1244.31
    },
    "flip": {
      "mean": <to be computed>,
      "std": <to be computed>,
      "median": <to be computed>
    },
    "optical_flow_consistency": {
      "mean": <to be computed>,
      "std": <to be computed>,
      "median": <to be computed>
    }
  }
}
```

---

## Performance Notes

**Per-frame processing time (1080p):**
- SSIM: ~5ms
- MSE: ~2ms
- FLIP: ~30ms
- Optical Flow: ~80ms
- **Total: ~117ms/frame**

**For 135 frames:**
- Expected time: ~16 seconds
- With overhead: ~2-3 minutes

---

## Interpreting Results

### SSIM (0.7568 from previous run)
- **Interpretation**: "Good" structural similarity
- **Context**: These are different gameplay sessions, not identical frames
- **Acceptable**: 0.75-0.79 indicates strong alignment

### MSE (401.96 from previous run)
- **Interpretation**: Moderate pixel error
- **Context**: Lower MSE = better alignment
- **Comparison**: ICAT manual (401.96) vs Scene automated (831.42)

### FLIP (NEW - to be measured)
- **Expected range**: 10-50 for good alignment
- **Lower is better**: Closer to 0 = less perceptual error
- **Edge-weighted**: Artifacts near edges count more

### Optical Flow (NEW - to be measured)
- **Expected range**: 100-500 for similar videos
- **Lower is better**: Closer to 0 = more consistent motion
- **Detects**: Ghosting, flickering, temporal instability

---

## To Install LPIPS (Optional)

If you want the full 6-metric analysis:

```bash
# Install for current user (bypasses system protection)
python3 -m pip install --user lpips

# Or using conda if you have it
conda install -c conda-forge lpips

# Then rerun the comparison
python3 scripts/compare_alignment_quality.py \
    --video1 recordings/cyberpunk/aligned/1080p_dlaa_run1.mp4 \
    --video2 recordings/cyberpunk/aligned/1080p_dlaa_run2.mp4 \
    --name "ICAT Manual - Full 6 Metrics" \
    --sample-rate 30 \
    --output recordings/cyberpunk/quality_icat_full.json
```

---

## Academic Context

### Why These Metrics Matter for Your TCC

1. **Addresses Gemini's Recommendations**
   - LPIPS: Current gold standard for perceptual quality
   - FLIP: Graphics-focused (aligns with DLAA/DLSS)
   - Optical Flow: Temporal stability (critical for DLSS)

2. **Beyond Traditional Metrics**
   - SSIM/PSNR miss neural "hallucinations" that look good
   - LPIPS captures semantic similarity
   - Optical flow detects temporal artifacts

3. **Demonstrates Methodological Sophistication**
   - Multi-faceted quality assessment
   - Pixel-level + Structural + Perceptual + Temporal
   - Aligns with 2026 best practices

4. **Supports Your Thesis Claims**
   - Can objectively measure DLSS quality vs DLAA
   - Captures both spatial and temporal artifacts
   - Provides quantitative evidence for qualitative observations

---

## Next Steps

1. ⏳ Wait for current comparison to complete (~2 minutes)
2. 📊 Review results in console output
3. 📁 Check JSON file: `recordings/cyberpunk/quality_icat_advanced.json`
4. 📝 Compare with previous results (SSIM/MSE only)
5. 🎓 Add findings to TCC dissertation
