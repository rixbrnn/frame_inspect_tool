"""
Advanced video quality metrics for perceptual and temporal analysis.

Frame-by-frame metrics:
- LPIPS: Learned perceptual similarity (deep learning)
- FLIP: Visual error with perceptual weighting
- Temporal Optical Flow: Motion consistency for ghosting detection

Video-level metrics (see vmaf_metrics.py):
- VMAF: Netflix's perceptual video quality metric with motion compensation
"""

import numpy as np
import cv2
from typing import Optional, Dict
import warnings

# Optional imports with graceful fallback
try:
    import torch
    import lpips
    LPIPS_AVAILABLE = True
except ImportError:
    LPIPS_AVAILABLE = False
    warnings.warn("LPIPS not available. Install with: pip install lpips torch torchvision")


class AdvancedMetrics:
    """Container for advanced metric computation."""

    def __init__(self, device='cpu'):
        self.device = device
        self._lpips_model = None

    @property
    def lpips_model(self):
        """Lazy-load LPIPS model."""
        if self._lpips_model is None and LPIPS_AVAILABLE:
            # AlexNet is faster, VGG is more accurate
            self._lpips_model = lpips.LPIPS(net='alex', verbose=False).to(self.device)
        return self._lpips_model

    def compute_lpips(self, frame1: np.ndarray, frame2: np.ndarray) -> Optional[float]:
        """
        Compute LPIPS (Learned Perceptual Image Patch Similarity).

        Args:
            frame1, frame2: BGR images (OpenCV format)

        Returns:
            LPIPS distance (lower is better, range [0, 1+])
        """
        if not LPIPS_AVAILABLE:
            return None

        # Convert BGR → RGB
        img1_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        img2_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

        # Normalize to [-1, 1] and convert to torch tensor
        img1_tensor = torch.from_numpy(img1_rgb).permute(2, 0, 1).float() / 127.5 - 1.0
        img2_tensor = torch.from_numpy(img2_rgb).permute(2, 0, 1).float() / 127.5 - 1.0

        # Add batch dimension
        img1_tensor = img1_tensor.unsqueeze(0).to(self.device)
        img2_tensor = img2_tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            distance = self.lpips_model(img1_tensor, img2_tensor)

        return float(distance.item())

    def compute_optical_flow_error(self, prev_frame: np.ndarray,
                                    curr_frame: np.ndarray,
                                    next_frame: np.ndarray) -> Dict[str, float]:
        """
        Compute temporal optical flow consistency (for ghosting detection).

        Algorithm:
        1. Compute optical flow from prev → curr
        2. Warp prev frame using flow
        3. Compare warped frame to curr frame (should match if motion is consistent)
        4. High error = ghosting/flickering

        Args:
            prev_frame: Frame at time t-1
            curr_frame: Frame at time t (being evaluated)
            next_frame: Frame at time t+1

        Returns:
            Dict with:
                - forward_error: Warp error from t-1 → t
                - backward_error: Warp error from t+1 → t
                - mean_error: Average of both
                - flow_magnitude: Average flow magnitude
        """
        # Convert to grayscale for optical flow
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

        # Compute forward flow (prev → curr)
        flow_forward = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )

        # Warp prev frame to match curr
        h, w = prev_gray.shape
        flow_map = np.column_stack([
            np.repeat(np.arange(w).reshape(1, -1), h, axis=0).ravel(),
            np.repeat(np.arange(h).reshape(-1, 1), w, axis=1).ravel()
        ])
        flow_map = flow_map.reshape(h, w, 2)
        warped_coords = flow_map + flow_forward

        warped_prev = cv2.remap(
            prev_frame,
            warped_coords[:, :, 0].astype(np.float32),
            warped_coords[:, :, 1].astype(np.float32),
            cv2.INTER_LINEAR
        )

        # Compute warp error (MSE between warped and current)
        forward_error = np.mean((warped_prev.astype(float) - curr_frame.astype(float)) ** 2)

        # Compute backward flow (next → curr)
        flow_backward = cv2.calcOpticalFlowFarneback(
            next_gray, curr_gray,
            None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0
        )

        # Warp next frame
        warped_coords_back = flow_map + flow_backward
        warped_next = cv2.remap(
            next_frame,
            warped_coords_back[:, :, 0].astype(np.float32),
            warped_coords_back[:, :, 1].astype(np.float32),
            cv2.INTER_LINEAR
        )

        backward_error = np.mean((warped_next.astype(float) - curr_frame.astype(float)) ** 2)

        return {
            'forward_error': float(forward_error),
            'backward_error': float(backward_error),
            'mean_error': float((forward_error + backward_error) / 2),
            'flow_magnitude': float(np.mean(np.sqrt(flow_forward[..., 0]**2 + flow_forward[..., 1]**2)))
        }

    def compute_flip(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Compute FLIP-like metric (simplified version).

        NVIDIA FLIP considers:
        - Color differences in perceptually uniform space
        - Spatial frequency content
        - Local contrast sensitivity

        This is a simplified version using perceptual color space + edge weighting.

        Args:
            frame1, frame2: BGR images

        Returns:
            FLIP score (lower is better)
        """
        # Convert to LAB color space (perceptually uniform)
        lab1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2LAB)
        lab2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2LAB)

        # Compute per-channel differences
        diff_l = np.abs(lab1[:, :, 0].astype(float) - lab2[:, :, 0].astype(float))
        diff_a = np.abs(lab1[:, :, 1].astype(float) - lab2[:, :, 1].astype(float))
        diff_b = np.abs(lab1[:, :, 2].astype(float) - lab2[:, :, 2].astype(float))

        # Perceptual weighting (L is more sensitive than a/b)
        weighted_diff = diff_l * 0.5 + diff_a * 0.25 + diff_b * 0.25

        # Apply edge-aware filtering (artifacts more visible at edges)
        edges1 = cv2.Canny(cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY), 50, 150)
        edge_mask = (edges1 > 0).astype(float)

        # Weight errors near edges more heavily
        weighted_diff = weighted_diff * (1.0 + edge_mask * 0.5)

        return float(np.mean(weighted_diff))


def compute_all_metrics(frame1: np.ndarray,
                        frame2: np.ndarray,
                        prev_frame1: Optional[np.ndarray] = None,
                        prev_frame2: Optional[np.ndarray] = None,
                        next_frame1: Optional[np.ndarray] = None,
                        next_frame2: Optional[np.ndarray] = None,
                        metrics_instance: Optional[AdvancedMetrics] = None) -> Dict[str, any]:
    """
    Compute all available advanced metrics for a frame pair.

    Args:
        frame1, frame2: Current frames to compare (BGR)
        prev_frame1, prev_frame2: Previous frames (for optical flow)
        next_frame1, next_frame2: Next frames (for optical flow)
        metrics_instance: Reusable AdvancedMetrics instance

    Returns:
        Dict with all computed metrics
    """
    if metrics_instance is None:
        metrics_instance = AdvancedMetrics()

    results = {}

    # LPIPS
    lpips_score = metrics_instance.compute_lpips(frame1, frame2)
    if lpips_score is not None:
        results['lpips'] = lpips_score

    # FLIP
    flip_score = metrics_instance.compute_flip(frame1, frame2)
    if flip_score is not None:
        results['flip'] = flip_score

    # Optical Flow (requires prev/next frames)
    if prev_frame1 is not None and next_frame1 is not None and prev_frame2 is not None and next_frame2 is not None:
        try:
            of_error1 = metrics_instance.compute_optical_flow_error(prev_frame1, frame1, next_frame1)
            of_error2 = metrics_instance.compute_optical_flow_error(prev_frame2, frame2, next_frame2)

            # Combine errors from both videos
            results['optical_flow'] = {
                'video1_mean_error': of_error1['mean_error'],
                'video2_mean_error': of_error2['mean_error'],
                'difference': abs(of_error1['mean_error'] - of_error2['mean_error'])
            }
        except Exception as e:
            warnings.warn(f"Optical flow computation failed: {e}")

    return results
