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
