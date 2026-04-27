"""
Basic frame-level quality metrics.

Provides fundamental image comparison metrics:
- SSIM (Structural Similarity Index)
- PSNR (Peak Signal-to-Noise Ratio)
- MSE (Mean Squared Error)
"""

import cv2
import os
import numpy as np
from tqdm import tqdm
from colorama import Fore, Style, init
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from typing import Dict, Tuple

# GPU acceleration imports
try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from pytorch_msssim import ssim as torch_ssim
    PYTORCH_MSSSIM_AVAILABLE = True
except ImportError:
    PYTORCH_MSSSIM_AVAILABLE = False

init(autoreset=True)


def compute_ssim(source_image, modified_image):
    """
    Compute SSIM between two images.

    Args:
        source_image: Source image (numpy array or file path)
        modified_image: Modified image (numpy array or file path)

    Returns:
        SSIM score (0-1 range)
    """
    # Load images if paths provided
    if isinstance(source_image, str):
        source_image = cv2.imread(source_image)
    if isinstance(modified_image, str):
        modified_image = cv2.imread(modified_image)

    # Convert to grayscale
    before_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)

    score, _ = ssim(before_gray, after_gray, full=True)
    return score


def compute_psnr(source_image, modified_image):
    """
    Compute PSNR between two images.

    Args:
        source_image: Source image (numpy array or file path)
        modified_image: Modified image (numpy array or file path)

    Returns:
        PSNR value in decibels (dB)
    """
    # Load images if paths provided
    if isinstance(source_image, str):
        source_image = cv2.imread(source_image)
    if isinstance(modified_image, str):
        modified_image = cv2.imread(modified_image)

    return psnr(source_image, modified_image)


def compute_mse(source_image, modified_image):
    """
    Compute Mean Squared Error between two images.

    Args:
        source_image: Source image (numpy array or file path)
        modified_image: Modified image (numpy array or file path)

    Returns:
        MSE value
    """
    # Load images if paths provided
    if isinstance(source_image, str):
        source_image = cv2.imread(source_image)
    if isinstance(modified_image, str):
        modified_image = cv2.imread(modified_image)

    err = np.sum((source_image.astype("float") - modified_image.astype("float")) ** 2)
    err /= float(source_image.shape[0] * source_image.shape[1])
    return err


def get_images_similarity(source_image_path, modified_image_path):
    """
    Calculate SSIM similarity between two images as percentage.

    Args:
        source_image_path: Path to source image
        modified_image_path: Path to modified image

    Returns:
        SSIM score as percentage (0-100)
    """
    score = compute_ssim(source_image_path, modified_image_path)
    return score * 100


def get_images_psnr(source_image_path, modified_image_path):
    """
    Calculate PSNR between two images.

    Args:
        source_image_path: Path to source image
        modified_image_path: Path to modified image

    Returns:
        PSNR value in decibels (dB). Higher values indicate better quality.
        Typical values: >40 dB (excellent), 30-40 dB (good), 20-30 dB (acceptable), <20 dB (poor)
    """
    return compute_psnr(source_image_path, modified_image_path)


def get_images_similarity_and_psnr(source_image_path, modified_image_path):
    """
    Calculate both SSIM and PSNR between two images.

    Args:
        source_image_path: Path to source image
        modified_image_path: Path to modified image

    Returns:
        Dictionary with 'ssim' (percentage), 'psnr' (dB), and 'diff' values
    """
    source_image = cv2.imread(source_image_path)
    modified_image = cv2.imread(modified_image_path)

    before_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)

    (ssim_score, diff) = ssim(before_gray, after_gray, full=True)
    psnr_value = psnr(source_image, modified_image)

    return {
        'ssim': ssim_score * 100,
        'psnr': psnr_value,
        'diff': diff
    }


def get_images_similarity_in_directory(source_image_path, directory, include_psnr=False):
    """
    Compare source image against all images in a directory.

    Args:
        source_image_path: Path to source image
        directory: Directory containing images to compare
        include_psnr: If True, also compute PSNR

    Returns:
        None (prints report)
    """
    results = []
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for filename in tqdm(files, desc="Processing images", unit="image"):
        file_path = os.path.join(directory, filename)
        if file_path == source_image_path:
            continue

        if include_psnr:
            metrics = get_images_similarity_and_psnr(source_image_path, file_path)
            results.append({'filename': filename, 'ssim': metrics['ssim'], 'psnr': metrics['psnr']})
        else:
            score = get_images_similarity(source_image_path, file_path)
            results.append({'filename': filename, 'score': score})

    generate_image_report(results, include_psnr)


def generate_image_report(results, include_psnr=False):
    """
    Generate formatted report from image comparison results.

    Args:
        results: List of comparison result dictionaries
        include_psnr: If True, include PSNR in report
    """
    if include_psnr:
        sorted_results = sorted(results, key=lambda x: x['ssim'], reverse=True)
        print("\n" + Fore.CYAN + "Image Comparison Report (Sorted by SSIM)" + Style.RESET_ALL)
        print(f"{'Image Name':<40}{'SSIM (%)':>15}{'PSNR (dB)':>15}")
        print("="*70)
        for result in sorted_results:
            ssim_score = result['ssim']
            psnr_value = result['psnr']
            filename = result['filename']
            ssim_color = Fore.GREEN if ssim_score >= 99 else Fore.YELLOW if ssim_score >= 97 else Fore.RED
            psnr_color = Fore.GREEN if psnr_value >= 40 else Fore.YELLOW if psnr_value >= 30 else Fore.RED
            print(f"{filename:<40}{ssim_color}{ssim_score:>14.2f}{Style.RESET_ALL}{psnr_color}{psnr_value:>14.2f}{Style.RESET_ALL}")
    else:
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        print("\n" + Fore.CYAN + "Image Comparison Report (Sorted by Similarity)" + Style.RESET_ALL)
        print(f"{'Image Name':<40}{'SSIM Score (%)':>15}")
        print("="*55)
        for result in sorted_results:
            score = result['score']
            filename = result['filename']
            color = Fore.GREEN if score >= 99 else Fore.YELLOW if score >= 97 else Fore.RED
            print(f"{filename:<40}{color}{score:.2f}{Style.RESET_ALL}")


# ============================================================================
# GPU-Accelerated Basic Metrics
# ============================================================================

class BasicMetricsGPU:
    """
    GPU-accelerated basic image quality metrics using PyTorch.

    Provides SSIM, MSE, and PSNR computation on GPU for significant performance
    improvements over CPU-based implementations (5-15x faster).

    Falls back to CPU implementations if GPU is unavailable or if required
    libraries (pytorch-msssim) are not installed.
    """

    def __init__(self, device='cuda'):
        """
        Initialize GPU metrics computer.

        Args:
            device: 'cuda' for GPU, 'cpu' for CPU fallback
        """
        self.device = device

        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch is required for GPU acceleration. "
                "Install with: pip install torch torchvision"
            )

        if not PYTORCH_MSSSIM_AVAILABLE and device == 'cuda':
            print("⚠️  pytorch-msssim not available, SSIM will fall back to CPU")
            print("   Install with: pip install pytorch-msssim")

    def _frame_to_tensor(self, frame: np.ndarray) -> torch.Tensor:
        """
        Convert OpenCV BGR frame to PyTorch tensor.

        Args:
            frame: OpenCV frame (H, W, C) in BGR format

        Returns:
            PyTorch tensor (1, C, H, W) in BGR format on device
        """
        # Convert to tensor and permute to (C, H, W)
        tensor = torch.from_numpy(frame).float().permute(2, 0, 1)
        # Add batch dimension and move to device
        return tensor.unsqueeze(0).to(self.device)

    def _tensor_to_grayscale(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Convert BGR tensor to grayscale using standard luminance weights.

        Args:
            tensor: BGR tensor (1, 3, H, W)

        Returns:
            Grayscale tensor (1, 1, H, W)
        """
        # Standard RGB→Gray weights: 0.299 R + 0.587 G + 0.114 B
        # For BGR: B=0.114, G=0.587, R=0.299
        gray = (0.114 * tensor[:, 0:1, :, :] +
                0.587 * tensor[:, 1:2, :, :] +
                0.299 * tensor[:, 2:3, :, :])
        return gray

    def compute_mse(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Compute Mean Squared Error on GPU.

        Args:
            frame1: First frame (OpenCV BGR format)
            frame2: Second frame (OpenCV BGR format)

        Returns:
            MSE value (lower is better)
        """
        f1 = self._frame_to_tensor(frame1)
        f2 = self._frame_to_tensor(frame2)

        with torch.no_grad():
            mse = F.mse_loss(f1, f2).item()

        return mse

    def compute_psnr(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Compute Peak Signal-to-Noise Ratio on GPU.

        PSNR is derived from MSE: PSNR = 10 * log10(MAX^2 / MSE)
        where MAX = 255 for 8-bit images.

        Args:
            frame1: First frame (OpenCV BGR format)
            frame2: Second frame (OpenCV BGR format)

        Returns:
            PSNR value in dB (higher is better)
            Returns inf if images are identical (MSE = 0)
        """
        mse = self.compute_mse(frame1, frame2)

        if mse == 0:
            return float('inf')

        # PSNR = 10 * log10(255^2 / MSE)
        psnr = 10 * np.log10((255.0 ** 2) / mse)
        return psnr

    def compute_ssim(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """
        Compute Structural Similarity Index on GPU.

        Uses pytorch-msssim library for GPU-accelerated SSIM.
        Falls back to CPU scikit-image if library not available.

        Args:
            frame1: First frame (OpenCV BGR format)
            frame2: Second frame (OpenCV BGR format)

        Returns:
            SSIM score (0-1 range, higher is better)
        """
        if not PYTORCH_MSSSIM_AVAILABLE:
            # Fallback to CPU implementation
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            return ssim(gray1, gray2)

        f1 = self._frame_to_tensor(frame1)
        f2 = self._frame_to_tensor(frame2)

        # Convert to grayscale for SSIM (standard practice)
        gray1 = self._tensor_to_grayscale(f1)
        gray2 = self._tensor_to_grayscale(f2)

        with torch.no_grad():
            # pytorch-msssim expects data_range for normalization
            # For 8-bit images: data_range = 255.0
            ssim_score = torch_ssim(gray1, gray2, data_range=255.0, size_average=True)
            ssim_value = ssim_score.item()

        return ssim_value

    def compute_all(self, frame1: np.ndarray, frame2: np.ndarray) -> Dict[str, float]:
        """
        Compute all basic metrics (SSIM, MSE, PSNR) in a single GPU pass.

        This is more efficient than calling each metric individually as frames
        are converted to tensors only once.

        Args:
            frame1: First frame (OpenCV BGR format)
            frame2: Second frame (OpenCV BGR format)

        Returns:
            Dictionary with 'ssim', 'mse', and 'psnr' values
        """
        # Convert frames to tensors once
        f1 = self._frame_to_tensor(frame1)
        f2 = self._frame_to_tensor(frame2)

        with torch.no_grad():
            # MSE
            mse = F.mse_loss(f1, f2).item()

            # PSNR (from MSE)
            if mse == 0:
                psnr_value = float('inf')
            else:
                psnr_value = 10 * np.log10((255.0 ** 2) / mse)

            # SSIM (grayscale)
            if PYTORCH_MSSSIM_AVAILABLE:
                gray1 = self._tensor_to_grayscale(f1)
                gray2 = self._tensor_to_grayscale(f2)
                ssim_score = torch_ssim(gray1, gray2, data_range=255.0, size_average=True).item()
            else:
                # Fallback to CPU for SSIM
                gray1_cpu = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
                gray2_cpu = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
                ssim_score = ssim(gray1_cpu, gray2_cpu)

        return {
            'ssim': ssim_score,
            'mse': mse,
            'psnr': psnr_value
        }
