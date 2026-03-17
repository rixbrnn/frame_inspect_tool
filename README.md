# frame_inspect_tool
A tool to compare graphics rendered with upscaling or frame generation to their source using SSIM and PSNR metrics.

## Features

- **Image Quality Metrics**: SSIM (Structural Similarity Index) and PSNR (Peak Signal-to-Noise Ratio)
- **Automatic Frame Alignment**: Uses perceptual hashing to automatically find overlapping sections in videos
- **Temporal Stability Analysis**: Measure frame-to-frame consistency using SSIM or PSNR
- **Batch Processing**: Compare a source image against a directory of images
- **Video Comparison**: Frame-by-frame comparison of two videos with automatic synchronization

## Metrics Explained

### SSIM (Structural Similarity Index)
- Measures structural similarity between images based on luminance, contrast, and structure
- Range: 0-100% (higher is better)
- More aligned with human perception than pixel-wise metrics
- Interpretation:
  - ≥99%: Excellent (virtually identical)
  - 97-99%: Good (minor differences)
  - <97%: Significant differences

### PSNR (Peak Signal-to-Noise Ratio)
- Measures signal quality in decibels (dB)
- Higher values indicate better quality
- Interpretation:
  - ≥40 dB: Excellent quality
  - 30-40 dB: Good quality
  - 20-30 dB: Acceptable quality
  - <20 dB: Poor quality

# Setup

Install python and then install the dependencies with

`pip install -r requirements.txt`

# Usage

## Image Comparison

Compare two images using SSIM:
```bash
python src/app.py -s source_image.png -m modified_image.png
```

Compare two images using both SSIM and PSNR:
```bash
python src/app.py -s source_image.png -m modified_image.png --psnr
```

Compare source image against all images in a directory:
```bash
python src/app.py -s source_image.png -d ./images_directory/
```

Include PSNR in directory comparison:
```bash
python src/app.py -s source_image.png -d ./images_directory/ --psnr
```

## Video Comparison

Compare two videos (manual frame alignment):
```bash
python src/app.py -v1 video1.mp4 -v2 video2.mp4
```

Compare two videos with automatic frame alignment:
```bash
python src/app.py -v1 video1.mp4 -v2 video2.mp4 --find-intersection
```

Include PSNR in video comparison:
```bash
python src/app.py -v1 video1.mp4 -v2 video2.mp4 --find-intersection --psnr
```

## Temporal Stability Analysis

Measure temporal stability using SSIM:
```bash
python src/app.py --stability video.mp4 --method ssim
```

Measure temporal stability using PSNR:
```bash
python src/app.py --stability video.mp4 --method psnr
```

Measure using pixel-by-pixel difference:
```bash
python src/app.py --stability video.mp4 --method pixel
```

Analyze all videos in a directory:
```bash
python src/app.py --stability ./videos_directory/ --method ssim
```

# Important Notes for Accurate Comparisons

Is very easy to move the mouse around while taking screenshots. This tool requires the screenshot to be at the exact same position as before,
therefore I recommend only using it on scenes in which you can garantee there was no mouse movement from you. Alternatively, if the game you are testing supports
graphics preview feature (such as God of War: Ragnarok) while in the menu settings, that ideal for taking screenshots.
Alternatively, you can take the screenshots disabling the mouse to ensure there wont be any movement.
You must find a spot that does not have variable visuals, it needs to be a still frame.
Also, if the game has a "breathing" camera you must disable it or find a situation in which that is not active.
Otherwise your screenshots might not be a fair comparison.

For video comparisons:
- Use lossless codecs (e.g., FFV1) to avoid compression artifacts
- Ensure both videos have the same frame rate
- Use benchmark tools or photo modes to minimize procedural variation
- The `--find-intersection` flag automatically aligns videos using perceptual hashing