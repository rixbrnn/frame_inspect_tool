#!/usr/bin/env python3
"""
Quick verification that the MSE fix works correctly.
"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.metrics.frame.basic import compute_mse, BasicMetricsGPU, TORCH_AVAILABLE

print("Testing MSE computation fix...")
print("=" * 60)

# Create simple test image
np.random.seed(42)
frame1 = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
frame2 = frame1.copy()
frame2[40:60, 40:60] = 200  # Add difference

# CPU MSE (standalone function)
cpu_mse_standalone = compute_mse(frame1, frame2)
print(f"CPU MSE (standalone function): {cpu_mse_standalone:.6f}")

# CPU MSE (using np.mean directly - this is correct)
cpu_mse_correct = np.mean((frame1.astype(float) - frame2.astype(float)) ** 2)
print(f"CPU MSE (np.mean - correct):   {cpu_mse_correct:.6f}")

# GPU MSE (if available)
if TORCH_AVAILABLE:
    import torch
    if torch.cuda.is_available():
        print(f"\nGPU: {torch.cuda.get_device_name(0)}")
        gpu_metrics = BasicMetricsGPU(device='cuda')
        gpu_results = gpu_metrics.compute_all(frame1, frame2)
        print(f"GPU MSE:                       {gpu_results['mse']:.6f}")

        # Check they match
        diff = abs(cpu_mse_standalone - gpu_results['mse'])
        print(f"\nDifference: {diff:.6f}")

        if diff < 0.5:
            print("✓ MSE values match! Fix successful.")
        else:
            print("✗ MSE values still differ - something is wrong")
    else:
        print("\n⚠️  CUDA not available - skipping GPU test")
else:
    print("\n⚠️  PyTorch not available - skipping GPU test")

# Verify the fix
print("\n" + "=" * 60)
print("Verification:")
print("=" * 60)
diff_standalone_correct = abs(cpu_mse_standalone - cpu_mse_correct)
print(f"CPU standalone vs np.mean difference: {diff_standalone_correct:.6f}")

if diff_standalone_correct < 0.01:
    print("✓ CPU MSE function now matches np.mean() - Fix successful!")
else:
    print("✗ CPU MSE function still differs from np.mean()")
