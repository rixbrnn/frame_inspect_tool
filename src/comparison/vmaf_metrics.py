"""
VMAF (Video Multi-method Assessment Fusion) metric computation.

VMAF is Netflix's perceptual video quality metric that combines:
- VIF (Visual Information Fidelity)
- DLM (Detail Loss Metric)
- Motion analysis
- Temporal consistency

Unlike frame-by-frame metrics (SSIM, LPIPS), VMAF operates at video level
with temporal context and motion compensation.

Reference:
Li et al. (2016) "Toward a Practical Perceptual Video Quality Metric"
https://netflixtechblog.com/toward-a-practical-perceptual-video-quality-metric-653f208b9652
"""

import subprocess
import json
import tempfile
import os
from typing import Dict, List, Optional
import warnings


class VMAFMetrics:
    """VMAF computation using FFmpeg's libvmaf filter."""

    def __init__(self, model: str = 'vmaf_v0.6.1', n_threads: int = 0):
        """
        Initialize VMAF metrics computer.

        Args:
            model: VMAF model version. Options:
                - 'vmaf_v0.6.1' (default, recommended)
                - 'vmaf_4k_v0.6.1' (optimized for 4K content)
                - 'vmaf_v0.6.1neg' (includes negative scores)
            n_threads: Number of threads (0 = auto, default)
        """
        self.model = model
        self.n_threads = n_threads
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Verify FFmpeg is installed with libvmaf support."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-filters'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'libvmaf' not in result.stdout:
                raise RuntimeError(
                    "FFmpeg does not have libvmaf support. "
                    "Please install FFmpeg with --enable-libvmaf"
                )
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
        except subprocess.TimeoutExpired:
            warnings.warn("FFmpeg check timed out, proceeding anyway...")

    def compute_vmaf(self,
                     reference_video: str,
                     distorted_video: str,
                     output_file: Optional[str] = None,
                     subsample: int = 1,
                     phone_model: bool = False) -> Dict:
        """
        Compute VMAF score between reference and distorted videos.

        Args:
            reference_video: Path to reference (ground truth) video
            distorted_video: Path to distorted video to evaluate
            output_file: Optional path to save full JSON results
            subsample: Sample every Nth frame (1 = all frames, 2 = every 2nd frame)
            phone_model: Use phone viewing model (default: False = HD model)

        Returns:
            Dict containing:
                - vmaf_mean: Mean VMAF score (0-100)
                - vmaf_harmonic_mean: Harmonic mean (conservative estimate)
                - vmaf_min: Minimum VMAF score
                - vmaf_max: Maximum VMAF score
                - vmaf_median: Median VMAF score
                - vmaf_std: Standard deviation
                - vmaf_per_frame: List[float] of per-frame scores
                - frames_processed: Number of frames analyzed

        Raises:
            RuntimeError: If VMAF computation fails
            FileNotFoundError: If video files don't exist
        """
        # Validate inputs
        if not os.path.exists(reference_video):
            raise FileNotFoundError(f"Reference video not found: {reference_video}")
        if not os.path.exists(distorted_video):
            raise FileNotFoundError(f"Distorted video not found: {distorted_video}")

        # Create temporary file for JSON output
        if output_file is None:
            temp_fd, output_file = tempfile.mkstemp(suffix='.json', prefix='vmaf_')
            os.close(temp_fd)
            cleanup_temp = True
        else:
            cleanup_temp = False

        try:
            # Build VMAF filter string
            vmaf_filter = f'libvmaf=log_path={output_file}:log_fmt=json'
            vmaf_filter += f':model=version={self.model}'

            if self.n_threads > 0:
                vmaf_filter += f':n_threads={self.n_threads}'

            if subsample > 1:
                vmaf_filter += f':n_subsample={subsample}'

            if phone_model:
                vmaf_filter += ':enable_transform=true'

            # Build FFmpeg command
            # Format: ffmpeg -i distorted.mp4 -i reference.mp4 -lavfi "[0:v][1:v]libvmaf" -f null -
            cmd = [
                'ffmpeg',
                '-i', distorted_video,  # Input 0 (distorted)
                '-i', reference_video,  # Input 1 (reference)
                '-lavfi', f'[0:v][1:v]{vmaf_filter}',
                '-f', 'null',
                '-'
            ]

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"VMAF computation failed with return code {result.returncode}\n"
                    f"stderr: {result.stderr}"
                )

            # Parse JSON results
            with open(output_file, 'r') as f:
                vmaf_data = json.load(f)

            # Extract per-frame scores
            frames = vmaf_data.get('frames', [])
            if not frames:
                raise RuntimeError("No frames found in VMAF output")

            vmaf_scores = []
            for frame in frames:
                metrics = frame.get('metrics', {})
                if 'vmaf' in metrics:
                    vmaf_scores.append(float(metrics['vmaf']))

            if not vmaf_scores:
                raise RuntimeError("No VMAF scores found in output")

            # Extract pooled metrics
            pooled = vmaf_data.get('pooled_metrics', {}).get('vmaf', {})

            # Compute additional statistics if not in pooled
            import numpy as np
            vmaf_array = np.array(vmaf_scores)

            return {
                'vmaf_mean': pooled.get('mean', float(np.mean(vmaf_array))),
                'vmaf_harmonic_mean': pooled.get('harmonic_mean',
                    float(len(vmaf_array) / np.sum(1.0 / (vmaf_array + 1e-10)))),
                'vmaf_min': pooled.get('min', float(np.min(vmaf_array))),
                'vmaf_max': pooled.get('max', float(np.max(vmaf_array))),
                'vmaf_median': float(np.median(vmaf_array)),
                'vmaf_std': float(np.std(vmaf_array)),
                'vmaf_per_frame': vmaf_scores,
                'frames_processed': len(vmaf_scores)
            }

        finally:
            # Cleanup temporary file if we created it
            if cleanup_temp and os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except Exception:
                    pass


def compute_vmaf_simple(reference_video: str,
                       distorted_video: str,
                       model: str = 'vmaf_v0.6.1',
                       subsample: int = 1) -> float:
    """
    Simple wrapper to get mean VMAF score.

    Args:
        reference_video: Path to reference video
        distorted_video: Path to distorted video
        model: VMAF model version
        subsample: Sample every Nth frame

    Returns:
        Mean VMAF score (0-100)
    """
    vmaf = VMAFMetrics(model=model)
    results = vmaf.compute_vmaf(reference_video, distorted_video, subsample=subsample)
    return results['vmaf_mean']


def interpret_vmaf_score(score: float) -> str:
    """
    Interpret VMAF score with human-readable quality rating.

    Args:
        score: VMAF score (0-100)

    Returns:
        Quality interpretation string
    """
    if score >= 95:
        return "Excellent (imperceptible differences)"
    elif score >= 90:
        return "Very Good (minor differences)"
    elif score >= 80:
        return "Good (small visible differences)"
    elif score >= 70:
        return "Fair (noticeable differences)"
    elif score >= 60:
        return "Acceptable (clearly visible differences)"
    elif score >= 50:
        return "Poor (significant degradation)"
    else:
        return "Very Poor (severe artifacts)"


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) < 3:
        print("Usage: python vmaf_metrics.py <reference_video> <distorted_video>")
        sys.exit(1)

    ref = sys.argv[1]
    dist = sys.argv[2]

    print(f"Computing VMAF for:")
    print(f"  Reference:  {ref}")
    print(f"  Distorted:  {dist}")
    print()

    vmaf = VMAFMetrics()
    results = vmaf.compute_vmaf(ref, dist)

    print("=" * 60)
    print("VMAF Results")
    print("=" * 60)
    print(f"Mean:          {results['vmaf_mean']:.2f} - {interpret_vmaf_score(results['vmaf_mean'])}")
    print(f"Harmonic Mean: {results['vmaf_harmonic_mean']:.2f} (conservative estimate)")
    print(f"Median:        {results['vmaf_median']:.2f}")
    print(f"Std Dev:       {results['vmaf_std']:.2f}")
    print(f"Min:           {results['vmaf_min']:.2f}")
    print(f"Max:           {results['vmaf_max']:.2f}")
    print(f"Frames:        {results['frames_processed']}")
    print("=" * 60)
