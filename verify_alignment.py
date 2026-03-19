#!/usr/bin/env python3
"""
Video Alignment Verifier

Checks if two videos are properly aligned by comparing frames at key timestamps.
Useful for verifying that DLAA and DLSS recordings captured the same benchmark sequence.

Usage:
    python verify_alignment.py \
        --video1 ../tcc/recordings/processed/DLAA_4K_60fps.mp4 \
        --video2 ../tcc/recordings/processed/Quality_60fps.mp4 \
        --sample-points 0 15 30 45 59 \
        --output ../tcc/results/alignment_verification.png
"""

import argparse
import sys
from pathlib import Path
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from skimage.metrics import structural_similarity as ssim


def extract_frame(video_path: Path, second: int, fps: int = 60) -> np.ndarray:
    """
    Extract a specific frame from video

    Args:
        video_path: Path to video
        second: Which second to extract
        fps: Video FPS

    Returns:
        Frame as numpy array
    """
    cap = cv2.VideoCapture(str(video_path))
    frame_number = second * fps
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise ValueError(f"Could not read frame at second {second}")

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def calculate_frame_similarity(frame1: np.ndarray, frame2: np.ndarray) -> dict:
    """
    Calculate similarity between two frames

    Args:
        frame1: First frame
        frame2: Second frame

    Returns:
        Dict with similarity metrics
    """
    # Convert to grayscale for SSIM
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)

    # Calculate SSIM
    ssim_value, _ = ssim(gray1, gray2, full=True)

    # Calculate pixel difference (normalized)
    diff = np.abs(frame1.astype(float) - frame2.astype(float))
    avg_diff = np.mean(diff)
    max_diff = np.max(diff)

    return {
        'ssim': ssim_value * 100,  # Convert to percentage
        'avg_pixel_diff': avg_diff,
        'max_pixel_diff': max_diff
    }


def verify_alignment(
    video1_path: Path,
    video2_path: Path,
    sample_points: list,
    fps: int = 60
) -> dict:
    """
    Verify if two videos are aligned by sampling key frames

    Args:
        video1_path: First video path
        video2_path: Second video path
        sample_points: List of seconds to sample
        fps: Video FPS

    Returns:
        Dict with alignment verification results
    """
    results = []

    print(f"Checking alignment between:")
    print(f"  Video 1: {video1_path.name}")
    print(f"  Video 2: {video2_path.name}")
    print(f"  Sample points: {sample_points}\n")

    for second in sample_points:
        print(f"Checking second {second}...", end=" ")

        frame1 = extract_frame(video1_path, second, fps)
        frame2 = extract_frame(video2_path, second, fps)

        similarity = calculate_frame_similarity(frame1, frame2)

        results.append({
            'second': second,
            'frame1': frame1,
            'frame2': frame2,
            'similarity': similarity
        })

        # Alignment check
        # High SSIM (>80%) suggests same scene/alignment
        # Low SSIM (<50%) suggests misalignment or different rendering
        if similarity['ssim'] > 80:
            print(f"✓ Aligned (SSIM: {similarity['ssim']:.1f}%)")
        elif similarity['ssim'] > 50:
            print(f"⚠ Possibly aligned (SSIM: {similarity['ssim']:.1f}%)")
        else:
            print(f"✗ Likely misaligned (SSIM: {similarity['ssim']:.1f}%)")

    return results


def plot_alignment_verification(
    results: list,
    video1_name: str,
    video2_name: str,
    output_path: Path
):
    """
    Create visual verification plot

    Args:
        results: List of alignment check results
        video1_name: Name of first video
        video2_name: Name of second video
        output_path: Where to save plot
    """
    n_samples = len(results)

    fig = plt.figure(figsize=(16, 4 * n_samples))
    gs = GridSpec(n_samples, 3, figure=fig, width_ratios=[1, 1, 0.3])

    for i, result in enumerate(results):
        second = result['second']
        frame1 = result['frame1']
        frame2 = result['frame2']
        similarity = result['similarity']

        # Show frame from video 1
        ax1 = fig.add_subplot(gs[i, 0])
        ax1.imshow(frame1)
        ax1.set_title(f"{video1_name} - Second {second}", fontsize=10)
        ax1.axis('off')

        # Show frame from video 2
        ax2 = fig.add_subplot(gs[i, 1])
        ax2.imshow(frame2)
        ax2.set_title(f"{video2_name} - Second {second}", fontsize=10)
        ax2.axis('off')

        # Show similarity metrics
        ax3 = fig.add_subplot(gs[i, 2])
        ax3.axis('off')

        ssim_val = similarity['ssim']
        ssim_color = 'green' if ssim_val > 80 else 'orange' if ssim_val > 50 else 'red'

        metrics_text = (
            f"SSIM:\n{ssim_val:.1f}%\n\n"
            f"Avg Diff:\n{similarity['avg_pixel_diff']:.1f}\n\n"
            f"Max Diff:\n{similarity['max_pixel_diff']:.0f}"
        )

        ax3.text(
            0.1, 0.5, metrics_text,
            fontsize=12,
            verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor=ssim_color, alpha=0.3)
        )

    plt.suptitle(
        f"Alignment Verification: {video1_name} vs {video2_name}",
        fontsize=14,
        fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n✓ Verification plot saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Verify temporal alignment between two videos"
    )
    parser.add_argument(
        "--video1",
        type=Path,
        required=True,
        help="First video (e.g., DLAA baseline)"
    )
    parser.add_argument(
        "--video2",
        type=Path,
        required=True,
        help="Second video (e.g., Quality mode)"
    )
    parser.add_argument(
        "--sample-points",
        type=int,
        nargs="+",
        default=[0, 15, 30, 45, 59],
        help="Seconds to sample (default: 0 15 30 45 59)"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Video FPS (default: 60)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output PNG file for visual verification"
    )

    args = parser.parse_args()

    try:
        print("=" * 60)
        print("Video Alignment Verification".center(60))
        print("=" * 60)
        print()

        # Verify alignment
        results = verify_alignment(
            args.video1,
            args.video2,
            args.sample_points,
            args.fps
        )

        # Calculate overall alignment score
        avg_ssim = np.mean([r['similarity']['ssim'] for r in results])

        print("\n" + "=" * 60)
        print(f"Overall Alignment Score: {avg_ssim:.1f}% SSIM")

        if avg_ssim > 80:
            print("✓ Videos are well-aligned")
        elif avg_ssim > 50:
            print("⚠ Videos may have alignment issues")
            print("  Consider re-recording or manual synchronization")
        else:
            print("✗ Videos are misaligned")
            print("  Different content or incorrect synchronization")

        print("=" * 60)

        # Generate visual plot
        if args.output:
            plot_alignment_verification(
                results,
                args.video1.stem,
                args.video2.stem,
                args.output
            )

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
