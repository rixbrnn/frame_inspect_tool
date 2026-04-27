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

try:
    import kornia
    KORNIA_AVAILABLE = True
except ImportError:
    KORNIA_AVAILABLE = False
    warnings.warn("Kornia not available. Install with: pip install kornia")


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

    def _frame_to_tensor(self, frame: np.ndarray) -> 'torch.Tensor':
        """
        Convert OpenCV BGR frame to PyTorch tensor.

        Args:
            frame: OpenCV frame (H, W, C) in BGR format

        Returns:
            PyTorch tensor (1, C, H, W) in BGR format on device
        """
        if not LPIPS_AVAILABLE:
            raise ImportError("PyTorch required for tensor conversion")

        import torch
        # Convert to tensor and permute to (C, H, W)
        tensor = torch.from_numpy(frame).float().permute(2, 0, 1)
        # Add batch dimension and move to device
        return tensor.unsqueeze(0).to(self.device)

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
        # Try GPU version first if available
        if self.device == 'cuda' and KORNIA_AVAILABLE and LPIPS_AVAILABLE:
            try:
                return self.compute_optical_flow_error_gpu(prev_frame, curr_frame, next_frame)
            except Exception as e:
                warnings.warn(f"GPU optical flow failed, falling back to CPU: {e}")

        # CPU fallback
        return self.compute_optical_flow_error_cpu(prev_frame, curr_frame, next_frame)

    def compute_optical_flow_error_cpu(self, prev_frame: np.ndarray,
                                        curr_frame: np.ndarray,
                                        next_frame: np.ndarray) -> Dict[str, float]:
        """
        CPU implementation of optical flow consistency.

        Args:
            prev_frame, curr_frame, next_frame: BGR frames

        Returns:
            Dict with forward_error, backward_error, mean_error, flow_magnitude
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

    def compute_optical_flow_error_gpu(self, prev_frame: np.ndarray,
                                        curr_frame: np.ndarray,
                                        next_frame: np.ndarray) -> Dict[str, float]:
        """
        GPU-accelerated optical flow using Lucas-Kanade pyramid method.

        This uses a simplified GPU optical flow based on image pyramids and
        gradient-based matching, which is faster than CPU Farneback while
        maintaining reasonable accuracy for temporal consistency measurement.

        Args:
            prev_frame, curr_frame, next_frame: BGR frames

        Returns:
            Dict with forward_error, backward_error, mean_error, flow_magnitude
        """
        import torch
        import torch.nn.functional as F

        # Convert frames to grayscale tensors
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

        # Convert to tensors (1, 1, H, W)
        prev_t = torch.from_numpy(prev_gray).float().unsqueeze(0).unsqueeze(0).to(self.device)
        curr_t = torch.from_numpy(curr_gray).float().unsqueeze(0).unsqueeze(0).to(self.device)
        next_t = torch.from_numpy(next_gray).float().unsqueeze(0).unsqueeze(0).to(self.device)

        # Convert color frames to tensors for warping
        prev_color = self._frame_to_tensor(prev_frame)
        curr_color = self._frame_to_tensor(curr_frame)
        next_color = self._frame_to_tensor(next_frame)

        with torch.no_grad():
            # Compute forward flow (prev → curr) using gradient-based method
            flow_forward = self._compute_flow_gpu_simple(prev_t, curr_t)

            # Warp prev frame using flow
            warped_prev = self._warp_frame_gpu(prev_color, flow_forward)

            # Compute forward warp error
            forward_error = F.mse_loss(warped_prev, curr_color).item()

            # Compute backward flow (next → curr)
            flow_backward = self._compute_flow_gpu_simple(next_t, curr_t)

            # Warp next frame using flow
            warped_next = self._warp_frame_gpu(next_color, flow_backward)

            # Compute backward warp error
            backward_error = F.mse_loss(warped_next, curr_color).item()

            # Compute flow magnitude
            flow_magnitude = torch.mean(torch.sqrt(
                flow_forward[:, 0, :, :] ** 2 + flow_forward[:, 1, :, :] ** 2
            )).item()

        return {
            'forward_error': float(forward_error),
            'backward_error': float(backward_error),
            'mean_error': float((forward_error + backward_error) / 2),
            'flow_magnitude': float(flow_magnitude)
        }

    def _compute_flow_gpu_simple(self, img1: 'torch.Tensor', img2: 'torch.Tensor') -> 'torch.Tensor':
        """
        Simplified GPU optical flow using image gradients and correlation.

        This is a lightweight implementation that's much faster than CPU Farneback
        while maintaining reasonable accuracy for temporal consistency measurement.

        Args:
            img1, img2: Grayscale tensors (1, 1, H, W)

        Returns:
            Flow tensor (1, 2, H, W) where [0] is x-flow, [1] is y-flow
        """
        import torch
        import torch.nn.functional as F

        # Compute image gradients
        sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32).view(1, 1, 3, 3).to(self.device)
        sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=torch.float32).view(1, 1, 3, 3).to(self.device)

        # Pad images
        img1_pad = F.pad(img1, (1, 1, 1, 1), mode='replicate')
        img2_pad = F.pad(img2, (1, 1, 1, 1), mode='replicate')

        # Compute spatial gradients
        Ix = F.conv2d(img2_pad, sobel_x)
        Iy = F.conv2d(img2_pad, sobel_y)

        # Temporal gradient
        It = img2 - img1

        # Lucas-Kanade: solve for flow using local window
        # For speed, we use a simplified version with Gaussian weighting
        window_size = 15
        sigma = 3.0

        # Create Gaussian kernel
        kernel_1d = torch.exp(-torch.arange(-(window_size // 2), window_size // 2 + 1, dtype=torch.float32, device=self.device) ** 2 / (2 * sigma ** 2))
        kernel_1d = kernel_1d / kernel_1d.sum()
        kernel_2d = kernel_1d.unsqueeze(1) * kernel_1d.unsqueeze(0)
        kernel_2d = kernel_2d.view(1, 1, window_size, window_size)

        # Pad for convolution
        pad_size = window_size // 2

        # Compute local sums (weighted by Gaussian)
        IxIx = F.conv2d(F.pad((Ix * Ix), (pad_size, pad_size, pad_size, pad_size), mode='replicate'), kernel_2d)
        IxIy = F.conv2d(F.pad((Ix * Iy), (pad_size, pad_size, pad_size, pad_size), mode='replicate'), kernel_2d)
        IyIy = F.conv2d(F.pad((Iy * Iy), (pad_size, pad_size, pad_size, pad_size), mode='replicate'), kernel_2d)
        IxIt = F.conv2d(F.pad((Ix * It), (pad_size, pad_size, pad_size, pad_size), mode='replicate'), kernel_2d)
        IyIt = F.conv2d(F.pad((Iy * It), (pad_size, pad_size, pad_size, pad_size), mode='replicate'), kernel_2d)

        # Solve 2x2 system for flow (u, v)
        # [IxIx  IxIy] [u]   [-IxIt]
        # [IxIy  IyIy] [v] = [-IyIt]

        # Add regularization to avoid singularities
        eps = 1e-6
        det = IxIx * IyIy - IxIy * IxIy + eps

        # Compute flow components
        u = (IyIy * (-IxIt) - IxIy * (-IyIt)) / det
        v = (IxIx * (-IyIt) - IxIy * (-IxIt)) / det

        # Stack into flow tensor (1, 2, H, W)
        flow = torch.cat([u, v], dim=1)

        # Clamp extreme values
        flow = torch.clamp(flow, -50, 50)

        return flow

    def _warp_frame_gpu(self, frame: 'torch.Tensor', flow: 'torch.Tensor') -> 'torch.Tensor':
        """
        Warp frame using optical flow on GPU.

        Args:
            frame: Frame tensor (1, C, H, W)
            flow: Flow tensor (1, 2, H, W) where [0] is x-flow, [1] is y-flow

        Returns:
            Warped frame tensor (1, C, H, W)
        """
        import torch
        import torch.nn.functional as F

        B, C, H, W = frame.shape

        # Create coordinate grid (y, x format for meshgrid)
        grid_y, grid_x = torch.meshgrid(
            torch.arange(H, dtype=torch.float32, device=self.device),
            torch.arange(W, dtype=torch.float32, device=self.device),
            indexing='ij'
        )

        # Apply flow to grid (flow is in x, y format)
        warped_x = grid_x + flow[0, 0, :, :]
        warped_y = grid_y + flow[0, 1, :, :]

        # Normalize to [-1, 1] for grid_sample
        warped_x = 2.0 * warped_x / (W - 1) - 1.0
        warped_y = 2.0 * warped_y / (H - 1) - 1.0

        # Stack to grid (1, H, W, 2) - grid_sample expects (x, y) order
        grid = torch.stack([warped_x, warped_y], dim=-1).unsqueeze(0)

        # Warp using bilinear interpolation
        warped = F.grid_sample(
            frame, grid, mode='bilinear', padding_mode='border', align_corners=True
        )

        return warped

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
        # Try GPU version first if available
        if self.device == 'cuda' and KORNIA_AVAILABLE and LPIPS_AVAILABLE:
            try:
                return self.compute_flip_gpu(frame1, frame2)
            except Exception as e:
                warnings.warn(f"GPU FLIP failed, falling back to CPU: {e}")

        # CPU fallback
        return self.compute_flip_cpu(frame1, frame2)

    def compute_flip_cpu(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        CPU implementation of FLIP metric.

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

    def compute_flip_gpu(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        GPU-accelerated FLIP metric using Kornia.

        Args:
            frame1, frame2: BGR images (OpenCV format)

        Returns:
            FLIP score (lower is better)
        """
        import torch

        # Convert frames to tensors (1, 3, H, W) in BGR format
        f1 = self._frame_to_tensor(frame1)
        f2 = self._frame_to_tensor(frame2)

        with torch.no_grad():
            # Convert BGR → LAB on GPU (perceptually uniform color space)
            # Kornia expects RGB, so we need to flip channels
            f1_rgb = torch.flip(f1, dims=[1])  # BGR → RGB
            f2_rgb = torch.flip(f2, dims=[1])

            lab1 = kornia.color.rgb_to_lab(f1_rgb)
            lab2 = kornia.color.rgb_to_lab(f2_rgb)

            # Compute per-channel absolute differences
            diff_l = torch.abs(lab1[:, 0:1, :, :] - lab2[:, 0:1, :, :])
            diff_a = torch.abs(lab1[:, 1:2, :, :] - lab2[:, 1:2, :, :])
            diff_b = torch.abs(lab1[:, 2:3, :, :] - lab2[:, 2:3, :, :])

            # Perceptual weighting (L channel more sensitive)
            weighted_diff = diff_l * 0.5 + diff_a * 0.25 + diff_b * 0.25

            # Edge detection on GPU (Canny via Kornia)
            gray1 = kornia.color.rgb_to_grayscale(f1_rgb)
            # Kornia's Canny returns (magnitude, edges)
            _, edges1 = kornia.filters.canny(gray1, low_threshold=50.0, high_threshold=150.0)
            edge_mask = (edges1 > 0).float()

            # Weight errors near edges more heavily
            weighted_diff = weighted_diff * (1.0 + edge_mask * 0.5)

            # Compute mean
            flip_score = torch.mean(weighted_diff).item()

        return flip_score


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
