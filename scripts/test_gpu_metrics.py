#!/usr/bin/env python3
"""
Test GPU vs CPU metric equivalence for basic metrics.

Verifies that GPU-accelerated implementations produce results within
acceptable tolerance of CPU implementations.
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metrics.frame.basic import (
    compute_ssim, compute_mse, compute_psnr,
    BasicMetricsGPU, TORCH_AVAILABLE, PYTORCH_MSSSIM_AVAILABLE
)


def test_metric_equivalence(frame1_path=None, frame2_path=None):
    """
    Test GPU vs CPU metric equivalence.

    Args:
        frame1_path: Path to first test frame (optional, generates synthetic if None)
        frame2_path: Path to second test frame (optional, generates synthetic if None)
    """
    print("=" * 80)
    print("GPU vs CPU Metric Equivalence Test")
    print("=" * 80)

    # Check GPU availability
    if not TORCH_AVAILABLE:
        print("\n❌ PyTorch not available - GPU testing cannot proceed")
        print("   Install with: pip install torch torchvision")
        return False

    import torch
    if not torch.cuda.is_available():
        print("\n⚠️  CUDA not available - skipping GPU tests")
        return False

    if not PYTORCH_MSSSIM_AVAILABLE:
        print("\n⚠️  pytorch-msssim not available - SSIM will use CPU fallback")
        print("   Install with: pip install pytorch-msssim")

    print(f"\n✓ GPU available: {torch.cuda.get_device_name(0)}")
    print(f"✓ CUDA version: {torch.version.cuda}")

    # Load or generate test frames
    if frame1_path and frame2_path:
        print(f"\nLoading test frames:")
        print(f"  Frame 1: {frame1_path}")
        print(f"  Frame 2: {frame2_path}")
        frame1 = cv2.imread(str(frame1_path))
        frame2 = cv2.imread(str(frame2_path))
    else:
        print("\nGenerating synthetic test frames (1920x1080)...")
        # Generate two similar but not identical frames
        np.random.seed(42)
        frame1 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        # Add some noise to frame2
        noise = np.random.randint(-10, 10, (1080, 1920, 3), dtype=np.int16)
        frame2 = np.clip(frame2.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    print(f"  Frame shape: {frame1.shape}")

    # Initialize GPU metrics
    print("\nInitializing GPU metrics...")
    gpu_metrics = BasicMetricsGPU(device='cuda')

    # Compute CPU metrics
    print("\n" + "-" * 80)
    print("Computing CPU metrics...")
    print("-" * 80)

    cpu_ssim = compute_ssim(frame1, frame2)
    cpu_mse = compute_mse(frame1, frame2)
    cpu_psnr = compute_psnr(frame1, frame2)

    print(f"  CPU SSIM: {cpu_ssim:.6f}")
    print(f"  CPU MSE:  {cpu_mse:.6f}")
    print(f"  CPU PSNR: {cpu_psnr:.6f} dB")

    # Compute GPU metrics
    print("\n" + "-" * 80)
    print("Computing GPU metrics...")
    print("-" * 80)

    gpu_results = gpu_metrics.compute_all(frame1, frame2)
    gpu_ssim = gpu_results['ssim']
    gpu_mse = gpu_results['mse']
    gpu_psnr = gpu_results['psnr']

    print(f"  GPU SSIM: {gpu_ssim:.6f}")
    print(f"  GPU MSE:  {gpu_mse:.6f}")
    print(f"  GPU PSNR: {gpu_psnr:.6f} dB")

    # Compare results
    print("\n" + "-" * 80)
    print("Comparison (absolute difference):")
    print("-" * 80)

    ssim_diff = abs(cpu_ssim - gpu_ssim)
    mse_diff = abs(cpu_mse - gpu_mse)
    psnr_diff = abs(cpu_psnr - gpu_psnr)

    print(f"  SSIM difference: {ssim_diff:.8f}")
    print(f"  MSE difference:  {mse_diff:.8f}")
    print(f"  PSNR difference: {psnr_diff:.8f} dB")

    # Define tolerances
    ssim_tolerance = 0.001  # ±0.001 for SSIM
    mse_tolerance = 0.5     # ±0.5 for MSE (very small for typical values)
    psnr_tolerance = 0.1    # ±0.1 dB for PSNR

    print("\n" + "-" * 80)
    print("Validation (within tolerance?):")
    print("-" * 80)

    ssim_pass = ssim_diff <= ssim_tolerance
    mse_pass = mse_diff <= mse_tolerance
    psnr_pass = psnr_diff <= psnr_tolerance

    print(f"  SSIM: {'✓ PASS' if ssim_pass else '✗ FAIL'} (tolerance: ±{ssim_tolerance})")
    print(f"  MSE:  {'✓ PASS' if mse_pass else '✗ FAIL'} (tolerance: ±{mse_tolerance})")
    print(f"  PSNR: {'✓ PASS' if psnr_pass else '✗ FAIL'} (tolerance: ±{psnr_tolerance} dB)")

    all_pass = ssim_pass and mse_pass and psnr_pass

    print("\n" + "=" * 80)
    if all_pass:
        print("✓ ALL TESTS PASSED - GPU metrics are equivalent to CPU")
    else:
        print("✗ SOME TESTS FAILED - Differences exceed tolerance")
    print("=" * 80)

    return all_pass


def benchmark_performance(num_frames=100):
    """
    Benchmark CPU vs GPU performance.

    Args:
        num_frames: Number of frames to process for benchmarking
    """
    import time

    print("\n" + "=" * 80)
    print(f"Performance Benchmark ({num_frames} frames)")
    print("=" * 80)

    if not TORCH_AVAILABLE:
        print("\n❌ PyTorch not available - cannot run benchmark")
        return

    import torch
    if not torch.cuda.is_available():
        print("\n⚠️  CUDA not available - skipping GPU benchmark")
        return

    # Generate test frames
    print("\nGenerating test frames (1920x1080)...")
    np.random.seed(42)
    frames1 = []
    frames2 = []
    for i in range(num_frames):
        frame1 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        frame2 = frame1.copy()
        noise = np.random.randint(-10, 10, (1080, 1920, 3), dtype=np.int16)
        frame2 = np.clip(frame2.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        frames1.append(frame1)
        frames2.append(frame2)

    # Benchmark CPU
    print(f"\nBenchmarking CPU ({num_frames} frames)...")
    cpu_start = time.time()
    for frame1, frame2 in zip(frames1, frames2):
        cpu_ssim = compute_ssim(frame1, frame2)
        cpu_mse = compute_mse(frame1, frame2)
        cpu_psnr = compute_psnr(frame1, frame2)
    cpu_time = time.time() - cpu_start
    cpu_fps = num_frames / cpu_time

    print(f"  Total time: {cpu_time:.2f}s")
    print(f"  Per frame:  {cpu_time / num_frames * 1000:.2f}ms")
    print(f"  Throughput: {cpu_fps:.2f} fps")

    # Benchmark GPU
    print(f"\nBenchmarking GPU ({num_frames} frames)...")
    gpu_metrics = BasicMetricsGPU(device='cuda')

    # Warmup
    for i in range(5):
        _ = gpu_metrics.compute_all(frames1[0], frames2[0])
    torch.cuda.synchronize()

    gpu_start = time.time()
    for frame1, frame2 in zip(frames1, frames2):
        _ = gpu_metrics.compute_all(frame1, frame2)
    torch.cuda.synchronize()
    gpu_time = time.time() - gpu_start
    gpu_fps = num_frames / gpu_time

    print(f"  Total time: {gpu_time:.2f}s")
    print(f"  Per frame:  {gpu_time / num_frames * 1000:.2f}ms")
    print(f"  Throughput: {gpu_fps:.2f} fps")

    # Calculate speedup
    speedup = cpu_time / gpu_time
    print("\n" + "-" * 80)
    print(f"Speedup: {speedup:.2f}x faster on GPU")
    print("-" * 80)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test GPU vs CPU metric equivalence')
    parser.add_argument('--frame1', type=str, help='Path to first test frame')
    parser.add_argument('--frame2', type=str, help='Path to second test frame')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmark')
    parser.add_argument('--num-frames', type=int, default=100, help='Number of frames for benchmark')

    args = parser.parse_args()

    # Run equivalence test
    success = test_metric_equivalence(args.frame1, args.frame2)

    # Run benchmark if requested
    if args.benchmark and success:
        benchmark_performance(args.num_frames)

    sys.exit(0 if success else 1)
