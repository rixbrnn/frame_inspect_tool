#!/usr/bin/env python3
"""
Benchmark Stability Validator

Validates that a game benchmark is deterministic enough for DLSS comparison.
Records the benchmark twice with identical settings and compares them.

According to methodology:
- SSIM ≥ 0.99 → benchmark is stable (acceptable)
- SSIM < 0.99 → benchmark has non-deterministic elements (reject)

Usage:
    python validate_benchmark_stability.py \
        --video1 DLAA_run1.mp4 \
        --video2 DLAA_run2.mp4 \
        --game "Cyberpunk 2077" \
        --settings "DLAA 4K, Ultra, RT On" \
        --output validation_report.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import cv2
from tqdm import tqdm
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr


class BenchmarkValidator:
    """Validate benchmark reproducibility for DLSS testing"""

    # Thresholds from methodology
    SSIM_THRESHOLD = 0.99
    SSIM_STD_THRESHOLD = 0.01
    MIN_SSIM_THRESHOLD = 0.95

    def __init__(self, video1_path: Path, video2_path: Path):
        self.video1_path = video1_path
        self.video2_path = video2_path

    def load_videos(self) -> Tuple[list, list, float]:
        """Load both video recordings"""
        print("\n[1/4] Loading videos...")

        cap1 = cv2.VideoCapture(str(self.video1_path))
        cap2 = cv2.VideoCapture(str(self.video2_path))

        if not cap1.isOpened() or not cap2.isOpened():
            raise ValueError("Could not open one or both videos")

        fps1 = cap1.get(cv2.CAP_PROP_FPS)
        fps2 = cap2.get(cv2.CAP_PROP_FPS)
        frame_count1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"  Video 1: {frame_count1} frames @ {fps1:.2f} FPS")
        print(f"  Video 2: {frame_count2} frames @ {fps2:.2f} FPS")

        # Load frames
        frames1 = []
        frames2 = []

        with tqdm(total=frame_count1, desc="Loading video 1", unit="frame") as pbar:
            while True:
                ret, frame = cap1.read()
                if not ret:
                    break
                frames1.append(frame)
                pbar.update(1)

        with tqdm(total=frame_count2, desc="Loading video 2", unit="frame") as pbar:
            while True:
                ret, frame = cap2.read()
                if not ret:
                    break
                frames2.append(frame)
                pbar.update(1)

        cap1.release()
        cap2.release()

        # Ensure same length
        min_frames = min(len(frames1), len(frames2))
        if len(frames1) != len(frames2):
            print(f"  ⚠ Frame count mismatch: {len(frames1)} vs {len(frames2)}")
            print(f"    Using first {min_frames} frames from both")
            frames1 = frames1[:min_frames]
            frames2 = frames2[:min_frames]

        print(f"  ✓ Loaded {len(frames1)} frames from each video")

        return frames1, frames2, fps1

    def compare_frames(self, frames1: list, frames2: list) -> Dict:
        """Compare frames using SSIM and PSNR"""
        print("\n[2/4] Comparing frames (this may take a while)...")

        ssim_scores = []
        psnr_scores = []
        low_ssim_frames = []  # Track frames with SSIM < threshold

        for i in tqdm(range(len(frames1)), desc="Computing SSIM/PSNR", unit="frame"):
            frame1 = frames1[i]
            frame2 = frames2[i]

            # Convert to grayscale for SSIM
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            # Calculate SSIM
            ssim_score, _ = ssim(gray1, gray2, full=True)
            ssim_scores.append(ssim_score)

            # Track problematic frames
            if ssim_score < self.MIN_SSIM_THRESHOLD:
                low_ssim_frames.append({
                    'frame': i,
                    'ssim': ssim_score,
                    'timestamp': i / 60.0  # Assume 60 FPS
                })

            # Calculate PSNR
            try:
                psnr_score = psnr(frame1, frame2)
                psnr_scores.append(psnr_score)
            except ValueError:
                # Identical frames can cause issues
                psnr_scores.append(float('inf'))

        ssim_scores = np.array(ssim_scores)
        psnr_scores = np.array([p for p in psnr_scores if p != float('inf')])

        results = {
            'ssim': {
                'mean': float(ssim_scores.mean()),
                'std': float(ssim_scores.std()),
                'min': float(ssim_scores.min()),
                'max': float(ssim_scores.max()),
                'median': float(np.median(ssim_scores))
            },
            'psnr': {
                'mean': float(psnr_scores.mean()) if len(psnr_scores) > 0 else None,
                'std': float(psnr_scores.std()) if len(psnr_scores) > 0 else None,
                'min': float(psnr_scores.min()) if len(psnr_scores) > 0 else None,
                'max': float(psnr_scores.max()) if len(psnr_scores) > 0 else None,
                'median': float(np.median(psnr_scores)) if len(psnr_scores) > 0 else None
            },
            'frames_analyzed': len(frames1),
            'low_ssim_frames': low_ssim_frames[:10]  # Keep only first 10
        }

        print(f"  ✓ Analyzed {len(frames1)} frames")

        return results

    def evaluate_stability(self, comparison: Dict) -> Dict:
        """Evaluate if benchmark meets stability criteria"""
        print("\n[3/4] Evaluating stability...")

        ssim_mean = comparison['ssim']['mean']
        ssim_std = comparison['ssim']['std']
        ssim_min = comparison['ssim']['min']

        # Check against thresholds
        passes_mean = ssim_mean >= self.SSIM_THRESHOLD
        passes_std = ssim_std < self.SSIM_STD_THRESHOLD
        passes_min = ssim_min >= self.MIN_SSIM_THRESHOLD

        is_stable = passes_mean and passes_std and passes_min

        evaluation = {
            'is_stable': is_stable,
            'checks': {
                'mean_ssim': {
                    'value': ssim_mean,
                    'threshold': self.SSIM_THRESHOLD,
                    'passes': passes_mean,
                    'description': 'Average SSIM across all frames'
                },
                'std_ssim': {
                    'value': ssim_std,
                    'threshold': self.SSIM_STD_THRESHOLD,
                    'passes': passes_std,
                    'description': 'Standard deviation (variability)'
                },
                'min_ssim': {
                    'value': ssim_min,
                    'threshold': self.MIN_SSIM_THRESHOLD,
                    'passes': passes_min,
                    'description': 'Worst single frame SSIM'
                }
            }
        }

        # Print results
        print("\n  Stability Checks:")
        print(f"    Mean SSIM:   {ssim_mean:.4f} (threshold: {self.SSIM_THRESHOLD}) {'✓' if passes_mean else '✗'}")
        print(f"    Std Dev:     {ssim_std:.4f} (threshold: < {self.SSIM_STD_THRESHOLD}) {'✓' if passes_std else '✗'}")
        print(f"    Min SSIM:    {ssim_min:.4f} (threshold: ≥ {self.MIN_SSIM_THRESHOLD}) {'✓' if passes_min else '✗'}")
        print()

        if is_stable:
            print(f"  ✓ BENCHMARK IS STABLE - Suitable for DLSS comparison")
        else:
            print(f"  ✗ BENCHMARK IS UNSTABLE - Not suitable for DLSS comparison")

        return evaluation

    def generate_report(
        self,
        comparison: Dict,
        evaluation: Dict,
        game_name: str,
        settings: str
    ) -> Dict:
        """Generate comprehensive validation report"""
        print("\n[4/4] Generating report...")

        report = {
            'game': game_name,
            'settings': settings,
            'videos': {
                'video1': str(self.video1_path),
                'video2': str(self.video2_path)
            },
            'comparison': comparison,
            'evaluation': evaluation,
            'recommendation': self._get_recommendation(evaluation, comparison)
        }

        print("  ✓ Report generated")

        return report

    def _get_recommendation(self, evaluation: Dict, comparison: Dict) -> Dict:
        """Generate actionable recommendations"""
        if evaluation['is_stable']:
            return {
                'verdict': 'ACCEPT',
                'action': 'This benchmark is suitable for DLSS comparison. Proceed with data collection.',
                'confidence': 'HIGH'
            }

        # Diagnose why it failed
        issues = []
        checks = evaluation['checks']

        if not checks['mean_ssim']['passes']:
            diff = self.SSIM_THRESHOLD - checks['mean_ssim']['value']
            issues.append(f"Average SSIM too low (by {diff:.4f})")

        if not checks['std_ssim']['passes']:
            issues.append(f"High variability between runs (σ={checks['std_ssim']['value']:.4f})")

        if not checks['min_ssim']['passes']:
            low_frames = comparison.get('low_ssim_frames', [])
            if low_frames:
                issues.append(f"Found {len(low_frames)} frames with SSIM < {self.MIN_SSIM_THRESHOLD}")

        return {
            'verdict': 'REJECT',
            'action': 'This benchmark has non-deterministic elements. Do not use for DLSS comparison.',
            'confidence': 'HIGH',
            'issues': issues,
            'possible_causes': [
                'Random AI behavior (NPCs, enemies)',
                'Procedural animations (vegetation, particles)',
                'Physics simulation variations',
                'Random spawn positions',
                'Frame timing inconsistencies'
            ],
            'suggestions': [
                'Try a different benchmark scene',
                'Look for benchmark modes without AI/physics',
                'Use photo mode if available',
                'Consider manual alignment of start frames'
            ]
        }


def main():
    parser = argparse.ArgumentParser(
        description="Validate benchmark stability for DLSS comparison"
    )
    parser.add_argument(
        "--video1",
        type=Path,
        required=True,
        help="First benchmark recording"
    )
    parser.add_argument(
        "--video2",
        type=Path,
        required=True,
        help="Second benchmark recording (identical settings)"
    )
    parser.add_argument(
        "--game",
        required=True,
        help="Game name (e.g., 'Cyberpunk 2077')"
    )
    parser.add_argument(
        "--settings",
        required=True,
        help="Graphics settings used (e.g., 'DLAA 4K, Ultra, RT On')"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output JSON report file"
    )

    args = parser.parse_args()

    try:
        print("=" * 80)
        print("BENCHMARK STABILITY VALIDATION".center(80))
        print("=" * 80)
        print(f"\nGame:     {args.game}")
        print(f"Settings: {args.settings}")
        print(f"Video 1:  {args.video1}")
        print(f"Video 2:  {args.video2}")

        # Validate
        validator = BenchmarkValidator(args.video1, args.video2)

        frames1, frames2, fps = validator.load_videos()
        comparison = validator.compare_frames(frames1, frames2)
        evaluation = validator.evaluate_stability(comparison)
        report = validator.generate_report(comparison, evaluation, args.game, args.settings)

        # Save report
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n  ✓ Report saved to: {args.output}")

        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY".center(80))
        print("=" * 80)

        rec = report['recommendation']
        verdict_color = '\033[92m' if rec['verdict'] == 'ACCEPT' else '\033[91m'
        reset_color = '\033[0m'

        print(f"\nVERDICT: {verdict_color}{rec['verdict']}{reset_color}")
        print(f"\n{rec['action']}")

        if rec['verdict'] == 'REJECT':
            print(f"\nIssues detected:")
            for issue in rec['issues']:
                print(f"  • {issue}")

            print(f"\nPossible causes:")
            for cause in rec['possible_causes']:
                print(f"  • {cause}")

            print(f"\nSuggestions:")
            for suggestion in rec['suggestions']:
                print(f"  • {suggestion}")

        print("\n" + "=" * 80)

        # Exit code based on verdict
        sys.exit(0 if rec['verdict'] == 'ACCEPT' else 1)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
