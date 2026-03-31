# ICAT-Based Video Alignment Solution

## Summary

We've replaced all automated video synchronization code with a simple, reliable approach that uses your existing manual ICAT alignment data.

## What Changed

### ❌ Removed
- `src/sync/enhanced_sync.py` - Complex perceptual hash + SSIM correlation
- `src/sync/streaming_hash_sync.py` - Memory-efficient streaming hash approach
- All automated sync attempts that couldn't handle non-identical recordings

### ✅ Added
- `src/sync/icat_parser.py` - Parser for NVIDIA ICAT manual alignment JSON
- `scripts/trim_from_icat.py` - Video trimmer using ICAT alignment data

## Why This Approach is Better

1. **Uses your existing work**: You already manually aligned videos in ICAT
2. **Frame-perfect accuracy**: ICAT allows precise frame-by-frame alignment
3. **No false assumptions**: Automated sync assumed identical content (not true for your recordings)
4. **Simple and reliable**: Parse JSON → Extract frame ranges → Trim with ffmpeg

## How It Works

### 1. ICAT Manual Alignment
You manually align videos in NVIDIA ICAT and export the settings as JSON:
- `icat_1080p_dlaa_modes_cut_settings.json` - DLAA validation runs
- `icat_1080p_derived_modes_cut_settings.json` - DLSS quality modes
- Similar files for 1440p and 4K

### 2. Parse ICAT Data
```python
from src.sync.icat_parser import parse_icat_alignment

alignment = parse_icat_alignment('recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json')

for video in alignment.videos:
    print(f"{video.video_name}: frames {video.start_frame} to {video.end_frame}")
```

### 3. Trim Videos
```bash
# Dry run (preview)
python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json --dry-run

# Trim videos to aligned/ folder
python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json
```

## Output Structure

```
recordings/cyberpunk/
├── 1080p_dlaa_run1.mp4                    # Original (unchanged)
├── 1080p_dlaa_run2.mp4                    # Original (unchanged)
├── 1080p_dlss_quality.mp4                 # Original (unchanged)
├── 1080p_dlss_balanced.mp4                # Original (unchanged)
├── icat_1080p_dlaa_modes_cut_settings.json
├── icat_1080p_derived_modes_cut_settings.json
└── aligned/                                # New trimmed videos
    ├── 1080p_dlaa_run1.mp4
    ├── 1080p_dlaa_run2.mp4
    ├── 1080p_dlss_quality.mp4
    └── 1080p_dlss_balanced.mp4
```

## Usage Examples

### View ICAT Alignment Info
```bash
python src/sync/icat_parser.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json
```

Output:
```
Set: Set 1
Aligned Time Range: 0.016s to 67.218s
Aligned Duration: 67.202s (4032 frames @ 60fps)

Videos: 2
#1 Video: 1080p_dlaa_run1.mp4
   Aligned Range: frames 0 to 4033

#2 Video: 1080p_dlaa_run2.mp4
   Aligned Range: frames 0 to 4033
```

### Trim Videos
```bash
# DLAA validation (run1 vs run2)
python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json

# DLSS modes comparison
python scripts/trim_from_icat.py recordings/cyberpunk/icat_1080p_derived_modes_cut_settings.json

# All resolutions
python scripts/trim_from_icat.py recordings/cyberpunk/icat_1440p_dlaa_modes_cut_settings.json
python scripts/trim_from_icat.py recordings/cyberpunk/icat_1440p_derived_modes_cut_settings.json
python scripts/trim_from_icat.py recordings/cyberpunk/icat_4k_dlaa_modes_cut_settings.json
python scripts/trim_from_icat.py recordings/cyberpunk/icat_4k_derived_modes_cut_settings.json
```

### Batch Process All
```bash
#!/bin/bash
# Trim all ICAT alignments

for icat_file in recordings/cyberpunk/icat_*.json; do
    echo "Processing: $icat_file"
    python scripts/trim_from_icat.py "$icat_file"
done
```

## ICAT JSON Structure

The ICAT export contains:
- **activeSet**: ID of the active comparison set
- **sets[]**: Array of comparison sets
  - **startTime**: Aligned start time (seconds)
  - **endTime**: Aligned end time (seconds)
  - **media[]**: Array of videos
    - **name**: Video filename
    - **fps**: Frame rate
    - **duration**: Total duration
    - **width/height**: Resolution

## Technical Details

### Frame-Accurate Trimming
Uses ffmpeg's `select` filter for precise frame cuts:
```bash
ffmpeg -i input.mp4 \
  -vf "select='between(n\,0\,4033)',setpts=PTS-STARTPTS" \
  -af "aselect='between(n\,0\,4033)',asetpts=PTS-STARTPTS" \
  -vsync 0 \
  output.mp4
```

### Why Automated Sync Failed
Your Cyberpunk recordings were:
- Different benchmark runs (not identical content)
- Different starting points (menus, loading screens)
- Only 3 consecutive matching frames found (needed 30+)
- SSIM < 85% (needed ≥95% for identical content)

This is **normal** for game recordings! ICAT's manual alignment is the right solution.

## Next Steps in Your Pipeline

After trimming with ICAT alignment:

1. **Validation** (Phase 0):
   ```bash
   python scripts/validate_benchmark.py \
     --video1 recordings/cyberpunk/aligned/1080p_dlaa_run1.mp4 \
     --video2 recordings/cyberpunk/aligned/1080p_dlaa_run2.mp4
   ```

2. **FPS Extraction** (Phase 3):
   ```bash
   python scripts/extract_fps.py \
     --video recordings/cyberpunk/aligned/1080p_dlaa_run1.mp4 \
     --roi recordings/cyberpunk/fps_roi.json
   ```

3. **Quality Analysis** (Phase 4):
   ```bash
   python scripts/pipeline.py \
     --game cyberpunk2077 \
     --resolution 1080p \
     --baseline DLAA
   ```

## Benefits

✅ **Accuracy**: Frame-perfect alignment from manual ICAT work
✅ **Simplicity**: No complex hashing or correlation algorithms
✅ **Reliability**: Works with any video content, not just identical runs
✅ **Reusability**: ICAT JSON saved with recordings for reproducibility
✅ **Non-destructive**: Original videos unchanged, trimmed videos in aligned/

## Files Created

- **src/sync/icat_parser.py** (369 lines)
  - Parses ICAT JSON
  - Extracts alignment info
  - Generates ffmpeg commands

- **scripts/trim_from_icat.py** (192 lines)
  - CLI tool to trim videos
  - Dry-run mode
  - Progress reporting

## Lessons Learned

**Automated sync assumptions:**
- ❌ Identical frame content
- ❌ Simple temporal offset
- ❌ High SSIM between recordings

**Reality of game benchmarks:**
- ✅ Different play-throughs
- ✅ Menu timing variations
- ✅ Manual alignment required
- ✅ ICAT is the right tool for the job

**Conclusion:** Sometimes the best solution is to use the work you've already done rather than trying to automate something that requires human judgment!
