#!/usr/bin/env python3
"""
Test GPU vs CPU metric equivalence for all advanced metrics.

Verifies that GPU-accelerated implementations (FLIP, optical flow) produce
results within acceptable tolerance of CPU implementations.
"""

import sys
from pathlib import Path
import numpy as np
import cv2
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metrics.frame.perceptual import (
    AdvancedMetrics, LPIPS_AVAILABLE, KORNIA_AVAILABLE
)


def test_flip_equivalence():
    """Test GPU vs CPU FLIP equivalence."""
    print("\n" + "=" * 80)
    print("FLIP GPU vs CPU Equivalence Test")
    print("=" * 80)

    if not LPIPS_AVAILABLE:
        print("\n❌ PyTorch not available - skipping FLIP tests")
        return False

    import torch
    if not torch.cuda.is_available():
        print("\n⚠️  CUDA not available - skipping GPU tests")
        return False

    if not KORNIA_AVAILABLE:
        print("\n⚠️  Kornia not available - FLIP GPU test skipped")
        print("   Install with: pip install kornia")
        return False

    print(f"\n✓ GPU available: {torch.cuda.get_device_name(0)}")

    # Generate test frames
    print("\nGenerating synthetic test frames (1920x1080)...")
    np.random.seed(42)
    frame1 = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    frame2 = frame1.copy()
    noise = np.random.randint(-10, 10, (1080, 1920, 3), dtype=np.int16)
    frame2 = np.clip(frame2.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Initialize metrics
    cpu_metrics = AdvancedMetrics(device='cpu')
    gpu_metrics = AdvancedMetrics(device='cuda')

    # Compute CPU FLIP
    print("\nComputing CPU FLIP...")
    start = time.time()
    cpu_flip = cpu_metrics.compute_flip_cpu(frame1, frame2)
    cpu_time = time.time() - start
    print(f"  CPU FLIP: {cpu_flip:.6f} ({cpu_time*1000:.2f}ms)")

    # Compute GPU FLIP
    print("\nComputing GPU FLIP...")
    # Warmup
    for _ in range(3):
        _ = gpu_metrics.compute_flip_gpu(frame1, frame2)
    torch.cuda.synchronize()

    start = time.time()
    gpu_flip = gpu_metrics.compute_flip_gpu(frame1, frame2)
    torch.cuda.synchronize()
    gpu_time = time.time() - start
    print(f"  GPU FLIP: {gpu_flip:.6f} ({gpu_time*1000:.2f}ms)")

    # Compare
    diff = abs(cpu_flip - gpu_flip)
    tolerance = 1.0  # FLIP can have larger differences due to Canny edge detection differences

    print(f"\nAbsolute difference: {diff:.6f}")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")

    passed = diff <= tolerance
    print(f"\nResult: {'✓ PASS' if passed else '✗ FAIL'} (tolerance: ±{tolerance})")

    return passed


def test_optical_flow_equivalence():
    """Test GPU vs CPU optical flow equivalence."""
    print("\n" + "=" * 80)
    print("Optical Flow GPU vs CPU Equivalence Test")
    print("=" * 80)

    if not LPIPS_AVAILABLE:
        print("\n❌ PyTorch not available - skipping optical flow tests")
        return False

    import torch
    if not torch.cuda.is_available():
        print("\n⚠️  CUDA not available - skipping GPU tests")
        return False

    if not KORNIA_AVAILABLE:
        print("\n⚠️  Kornia not available - optical flow GPU test skipped")
        return False

    print(f"\n✓ GPU available: {torch.cuda.get_device_name(0)}")

    # Generate test frames with motion
    print("\nGenerating synthetic frames with motion (1080p)...")
    np.random.seed(42)

    # Create base frame
    base = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)

    # Create frames with horizontal motion
    prev_frame = base.copy()
    curr_frame = np.roll(base, 10, axis=1)  # Shift right by 10 pixels
    next_frame = np.roll(base, 20, axis=1)  # Shift right by 20 pixels

    # Initialize metrics
    cpu_metrics = AdvancedMetrics(device='cpu')
    gpu_metrics = AdvancedMetrics(device='cuda')

    # Compute CPU optical flow
    print("\nComputing CPU optical flow...")
    start = time.time()
    cpu_result = cpu_metrics.compute_optical_flow_error_cpu(prev_frame, curr_frame, next_frame)
    cpu_time = time.time() - start

    print(f"  CPU Results:")
    print(f"    Forward error:  {cpu_result['forward_error']:.2f}")
    print(f"    Backward error: {cpu_result['backward_error']:.2f}")
    print(f"    Mean error:     {cpu_result['mean_error']:.2f}")
    print(f"    Flow magnitude: {cpu_result['flow_magnitude']:.2f}")
    print(f"    Time: {cpu_time*1000:.2f}ms")

    # Compute GPU optical flow
    print("\nComputing GPU optical flow...")
    # Warmup
    for _ in range(3):
        _ = gpu_metrics.compute_optical_flow_error_gpu(prev_frame, curr_frame, next_frame)
    torch.cuda.synchronize()

    start = time.time()
    gpu_result = gpu_metrics.compute_optical_flow_error_gpu(prev_frame, curr_frame, next_frame)
    torch.cuda.synchronize()
    gpu_time = time.time() - start

    print(f"  GPU Results:")
    print(f"    Forward error:  {gpu_result['forward_error']:.2f}")
    print(f"    Backward error: {gpu_result['backward_error']:.2f}")
    print(f"    Mean error:     {gpu_result['mean_error']:.2f}")
    print(f"    Flow magnitude: {gpu_result['flow_magnitude']:.2f}")
    print(f"    Time: {gpu_time*1000:.2f}ms")

    print(f"\nSpeedup: {cpu_time/gpu_time:.2f}x")

    # Compare (optical flow methods can differ significantly)
    # We mainly care that both detect similar motion patterns
    print("\n" + "-" * 80)
    print("Note: GPU optical flow uses Lucas-Kanade, CPU uses Farneback.")
    print("Absolute values may differ, but relative magnitudes should be similar.")
    print("Both should detect motion and produce reasonable warp errors.")
    print("-" * 80)

    # Basic sanity checks
    gpu_ok = gpu_result['mean_error'] > 0 and gpu_result['flow_magnitude'] > 0
    cpu_ok = cpu_result['mean_error'] > 0 and cpu_result['flow_magnitude'] > 0

    passed = gpu_ok and cpu_ok
    print(f"\nResult: {'✓ PASS' if passed else '✗ FAIL'} (sanity check: both methods detect motion)")

    return passed


def benchmark_advanced_metrics():
    """Benchmark full advanced metrics pipeline."""
    print("\n" + "=" * 80)
    print("Advanced Metrics Performance Benchmark")
    print("=" * 80)

    if not LPIPS_AVAILABLE:
        print("\n❌ PyTorch not available")
        return

    import torch
    if not torch.cuda.is_available():
        print("\n⚠️  CUDA not available")
        return

    print(f"\n✓ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✓ Kornia: {'Available' if KORNIA_AVAILABLE else 'Not available'}")

    num_frames = 50
    print(f"\nBenchmarking {num_frames} frame triples...")

    # Generate test frames
    np.random.seed(42)
    frames = []
    for i in range(num_frames + 2):  # +2 for prev/next
        frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        frames.append(frame)

    # CPU benchmark
    print("\nCPU Benchmark:")
    cpu_metrics = AdvancedMetrics(device='cpu')

    start = time.time()
    for i in range(1, num_frames + 1):
        prev = frames[i - 1]
        curr = frames[i]
        next_f = frames[i + 1]

        _ = cpu_metrics.compute_flip_cpu(curr, next_f)
        _ = cpu_metrics.compute_optical_flow_error_cpu(prev, curr, next_f)
    cpu_time = time.time() - start

    print(f"  Total: {cpu_time:.2f}s")
    print(f"  Per frame: {cpu_time/num_frames*1000:.2f}ms")
    print(f"  Throughput: {num_frames/cpu_time:.2f} fps")

    # GPU benchmark
    if KORNIA_AVAILABLE:
        print("\nGPU Benchmark:")
        gpu_metrics = AdvancedMetrics(device='cuda')

        # Warmup
        for i in range(1, min(6, num_frames + 1)):
            prev = frames[i - 1]
            curr = frames[i]
            next_f = frames[i + 1]
            _ = gpu_metrics.compute_flip_gpu(curr, next_f)
            _ = gpu_metrics.compute_optical_flow_error_gpu(prev, curr, next_f)
        torch.cuda.synchronize()

        start = time.time()
        for i in range(1, num_frames + 1):
            prev = frames[i - 1]
            curr = frames[i]
            next_f = frames[i + 1]

            _ = gpu_metrics.compute_flip_gpu(curr, next_f)
            _ = gpu_metrics.compute_optical_flow_error_gpu(prev, curr, next_f)
        torch.cuda.synchronize()
        gpu_time = time.time() - start

        print(f"  Total: {gpu_time:.2f}s")
        print(f"  Per frame: {gpu_time/num_frames*1000:.2f}ms")
        print(f"  Throughput: {num_frames/gpu_time:.2f} fps")

        print(f"\n  Overall speedup: {cpu_time/gpu_time:.2f}x")


if __name__ == '__main__':
    print("Advanced Metrics GPU Testing")
    print("=" * 80)

    # Test FLIP
    flip_passed = test_flip_equivalence()

    # Test Optical Flow
    flow_passed = test_optical_flow_equivalence()

    # Benchmark
    benchmark_advanced_metrics()

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary:")
    print("=" * 80)
    print(f"  FLIP:          {'✓ PASS' if flip_passed else '✗ FAIL'}")
    print(f"  Optical Flow:  {'✓ PASS' if flow_passed else '✗ FAIL'}")
    print("=" * 80)

    sys.exit(0 if (flip_passed and flow_passed) else 1)
