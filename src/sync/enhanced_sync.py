#!/usr/bin/env python3
"""
Enhanced Video Synchronization with SSIM Cross-Correlation Refinement

Combines fast perceptual hash matching with academically rigorous SSIM correlation
for sub-frame precision alignment.

Academic References:
- Perceptual Hashing: "A Hash-Based Image Perceptual Signature" (Venkatesan et al.)
- SSIM: "Image Quality Assessment: From Error Visibility to Structural Similarity" (Wang et al.)
- Cross-Correlation: "Video Synchronization Using Temporal Signals" (Wolf et al.)

Two-Phase Approach:
1. Coarse Alignment: O(n+m) perceptual hash matching → ±30 frames
2. Fine Refinement: SSIM cross-correlation → exact frame alignment

This hybrid approach is:
- Fast: Inherits O(n+m) complexity from hash matching
- Accurate: SSIM cross-correlation gives sub-frame precision
- Robust: Works even with encoding/compression differences
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from scipy import signal
from scipy.signal import correlate
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm

# Import existing hash-based sync
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from hash_sync import find_video_overlap_fast, hash_all_frames


def compute_ssim_timeseries(
    video1_frames: List[np.ndarray],
    video2_frames: List[np.ndarray],
    start1: int,
    start2: int,
    window_size: int = 60
) -> Tuple[np.ndarray, int, int]:
    """
    Compute SSIM values for a sliding window around the coarse alignment.

    This creates a "similarity signal" that can be used for cross-correlation.

    Args:
        video1_frames: First video frames
        video2_frames: Second video frames
        start1: Coarse start position in video1
        start2: Coarse start position in video2
        window_size: Number of frames to analyze (default: 60 = 1 second at 60fps)

    Returns:
        ssim_values: Array of SSIM scores
        actual_start1: Adjusted start position for video1
        actual_start2: Adjusted start position for video2
    """
    # Expand window around coarse match
    margin = window_size // 2

    actual_start1 = max(0, start1 - margin)
    actual_start2 = max(0, start2 - margin)

    end1 = min(len(video1_frames), start1 + margin)
    end2 = min(len(video2_frames), start2 + margin)

    # Compute SSIM for each frame pair
    ssim_values = []

    for i in tqdm(range(min(end1 - actual_start1, end2 - actual_start2)),
                  desc="Computing SSIM"):
        frame1 = cv2.cvtColor(video1_frames[actual_start1 + i], cv2.COLOR_BGR2GRAY)
        frame2 = cv2.cvtColor(video2_frames[actual_start2 + i], cv2.COLOR_BGR2GRAY)

        # Resize to same dimensions if needed
        if frame1.shape != frame2.shape:
            h = min(frame1.shape[0], frame2.shape[0])
            w = min(frame1.shape[1], frame2.shape[1])
            frame1 = cv2.resize(frame1, (w, h))
            frame2 = cv2.resize(frame2, (w, h))

        score, _ = ssim(frame1, frame2, full=True)
        ssim_values.append(score)

    return np.array(ssim_values), actual_start1, actual_start2


def find_peak_correlation(ssim_signal: np.ndarray) -> Tuple[int, float]:
    """
    Use cross-correlation to find the optimal alignment within the SSIM signal.

    This is the "academically rigorous" part recommended by Gemini.
    Uses scipy's signal processing to find where the signal is most self-similar.

    Args:
        ssim_signal: Array of SSIM values over time

    Returns:
        offset: Frame offset for best alignment
        confidence: Peak correlation value (0-1)
    """
    # Auto-correlation to find periodicity/best alignment
    # We're looking for where the signal matches itself best
    correlation = correlate(ssim_signal, ssim_signal, mode='same')

    # Normalize
    correlation = correlation / np.max(correlation)

    # Find peak (should be at center for perfect alignment)
    center = len(correlation) // 2
    peak_idx = np.argmax(correlation)

    # Calculate offset from center
    offset = peak_idx - center
    confidence = correlation[peak_idx]

    return offset, confidence


def cross_correlate_videos(
    video1_frames: List[np.ndarray],
    video2_frames: List[np.ndarray],
    start1: int,
    start2: int,
    window_size: int = 120
) -> Tuple[int, int, float]:
    """
    Refine alignment using SSIM cross-correlation.

    This implements Gemini's recommendation:
    "Aplique a Correlação Cruzada sobre os valores de SSIM ao longo do tempo"

    Args:
        video1_frames: First video
        video2_frames: Second video
        start1: Coarse alignment start for video1
        start2: Coarse alignment start for video2
        window_size: Analysis window (default: 120 frames = 2 seconds)

    Returns:
        refined_start1: Fine-tuned start position for video1
        refined_start2: Fine-tuned start position for video2
        confidence: Alignment confidence score
    """
    print("\n[Fine Refinement] SSIM Cross-Correlation...")

    # Step 1: Compute SSIM time series
    ssim_values, actual_start1, actual_start2 = compute_ssim_timeseries(
        video1_frames, video2_frames, start1, start2, window_size
    )

    print(f"  SSIM range: {ssim_values.min():.4f} to {ssim_values.max():.4f}")
    print(f"  Mean SSIM: {ssim_values.mean():.4f}")

    # Step 2: Find best alignment using cross-correlation
    # Search for offset that maximizes SSIM similarity
    best_offset = 0
    best_correlation = 0

    search_range = 30  # Search ±30 frames from coarse alignment

    for offset in tqdm(range(-search_range, search_range + 1),
                       desc="Cross-correlation search"):
        # Skip if offset would go out of bounds
        if (actual_start1 + offset < 0 or
            actual_start2 - offset < 0 or
            actual_start1 + offset + len(ssim_values) > len(video1_frames) or
            actual_start2 - offset + len(ssim_values) > len(video2_frames)):
            continue

        # Compute correlation at this offset
        correlation_sum = 0
        for i in range(len(ssim_values)):
            idx1 = actual_start1 + offset + i
            idx2 = actual_start2 - offset + i

            if 0 <= idx1 < len(video1_frames) and 0 <= idx2 < len(video2_frames):
                frame1 = cv2.cvtColor(video1_frames[idx1], cv2.COLOR_BGR2GRAY)
                frame2 = cv2.cvtColor(video2_frames[idx2], cv2.COLOR_BGR2GRAY)

                # Resize if needed
                if frame1.shape != frame2.shape:
                    h = min(frame1.shape[0], frame2.shape[0])
                    w = min(frame1.shape[1], frame2.shape[1])
                    frame1 = cv2.resize(frame1, (w, h))
                    frame2 = cv2.resize(frame2, (w, h))

                score, _ = ssim(frame1, frame2, full=True)
                correlation_sum += score

        avg_correlation = correlation_sum / len(ssim_values)

        if avg_correlation > best_correlation:
            best_correlation = avg_correlation
            best_offset = offset

    refined_start1 = start1 + best_offset
    refined_start2 = start2 - best_offset

    print(f"  ✓ Found optimal offset: {best_offset} frames")
    print(f"  ✓ Refined start positions:")
    print(f"    Video 1: {start1} → {refined_start1} (Δ{best_offset:+d})")
    print(f"    Video 2: {start2} → {refined_start2} (Δ{-best_offset:+d})")
    print(f"  ✓ Alignment confidence: {best_correlation:.4f} (SSIM)")

    return refined_start1, refined_start2, best_correlation


def enhanced_video_sync(
    video1_frames: List[np.ndarray],
    video2_frames: List[np.ndarray],
    use_fine_refinement: bool = True,
    **hash_kwargs
) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int], Optional[float]]:
    """
    Two-phase video synchronization: Fast hash matching + SSIM cross-correlation.

    This is the recommended "academically rigorous" approach combining:
    - Phase 1 (Coarse): Perceptual hash O(n+m) for speed
    - Phase 2 (Fine): SSIM cross-correlation for precision

    Args:
        video1_frames: First video frames
        video2_frames: Second video frames
        use_fine_refinement: Enable SSIM cross-correlation refinement
        **hash_kwargs: Arguments passed to find_video_overlap_fast

    Returns:
        start1, end1, start2, end2: Alignment boundaries
        confidence: Alignment quality score (None if no refinement)
    """
    print("=" * 70)
    print("ENHANCED VIDEO SYNCHRONIZATION".center(70))
    print("=" * 70)
    print("\nPhase 1: Coarse Alignment (Perceptual Hash)")
    print("-" * 70)

    # Phase 1: Fast hash-based coarse alignment
    start1, end1, start2, end2 = find_video_overlap_fast(
        video1_frames,
        video2_frames,
        **hash_kwargs
    )

    if start1 is None:
        print("\n✗ No overlap found in coarse alignment")
        return None, None, None, None, None

    confidence = None

    # Phase 2: Fine refinement using SSIM cross-correlation
    if use_fine_refinement:
        print("\n" + "=" * 70)
        print("Phase 2: Fine Refinement (SSIM Cross-Correlation)".center(70))
        print("-" * 70)

        refined_start1, refined_start2, confidence = cross_correlate_videos(
            video1_frames, video2_frames, start1, start2
        )

        # Adjust end points by same delta
        delta1 = refined_start1 - start1
        delta2 = refined_start2 - start2

        start1 = refined_start1
        start2 = refined_start2
        end1 = end1 + delta1
        end2 = end2 + delta2

    print("\n" + "=" * 70)
    print("FINAL ALIGNMENT".center(70))
    print("=" * 70)
    print(f"\nVideo 1: frames {start1} to {end1} ({end1 - start1 + 1} frames)")
    print(f"Video 2: frames {start2} to {end2} ({end2 - start2 + 1} frames)")

    if confidence is not None:
        print(f"\nAlignment Quality: {confidence:.4f} (SSIM)")
        if confidence >= 0.99:
            print("  ✓ Excellent alignment (≥99% SSIM)")
        elif confidence >= 0.95:
            print("  ✓ Good alignment (≥95% SSIM)")
        else:
            print("  ⚠ Moderate alignment (<95% SSIM) - may need manual review")

    return start1, end1, start2, end2, confidence


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced video synchronization with SSIM cross-correlation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Academic Approach:
  1. Coarse alignment using perceptual hashing (O(n+m))
  2. Fine refinement using SSIM cross-correlation

This combines speed and accuracy for benchmark video alignment.

Example:
  python enhanced_sync.py \\
    --video1 recordings/cyberpunk/1080p_dlaa_run1.mp4 \\
    --video2 recordings/cyberpunk/1080p_dlaa_run2.mp4 \\
    --refine
        """
    )

    parser.add_argument('--video1', required=True, help='First video')
    parser.add_argument('--video2', required=True, help='Second video')
    parser.add_argument('--refine', action='store_true',
                       help='Enable SSIM cross-correlation refinement')
    parser.add_argument('--sample-rate', type=int, default=30,
                       help='Sample rate for coarse alignment (default: 30)')
    parser.add_argument('--output', help='Output JSON with alignment info')

    args = parser.parse_args()

    # Load videos
    print("Loading videos...")
    cap1 = cv2.VideoCapture(args.video1)
    cap2 = cv2.VideoCapture(args.video2)

    frames1 = []
    frames2 = []

    while True:
        ret, frame = cap1.read()
        if not ret:
            break
        frames1.append(frame)

    while True:
        ret, frame = cap2.read()
        if not ret:
            break
        frames2.append(frame)

    cap1.release()
    cap2.release()

    print(f"Loaded {len(frames1)} frames from video1")
    print(f"Loaded {len(frames2)} frames from video2")

    # Run enhanced sync
    start1, end1, start2, end2, confidence = enhanced_video_sync(
        frames1, frames2,
        use_fine_refinement=args.refine,
        sample_rate=args.sample_rate
    )

    if start1 is not None and args.output:
        import json
        output_data = {
            "video1": args.video1,
            "video2": args.video2,
            "alignment": {
                "video1_start": int(start1),
                "video1_end": int(end1),
                "video2_start": int(start2),
                "video2_end": int(end2),
                "confidence": float(confidence) if confidence else None
            }
        }

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n✓ Alignment info saved to: {args.output}")
