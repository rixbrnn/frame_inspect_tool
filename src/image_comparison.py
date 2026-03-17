import cv2
import os
import imagehash
from PIL import Image
import numpy as np
from tqdm import tqdm
import argparse
from colorama import Fore, Style, init
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr

init(autoreset=True)

def get_images_similarity(source_image_path, modified_image_path):
    source_image = cv2.imread(source_image_path)
    modified_image = cv2.imread(modified_image_path)

    before_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)

    (score, diff) = ssim(before_gray, after_gray, full=True)
    return score * 100

def get_images_psnr(source_image_path, modified_image_path):
    """
    Calculate PSNR (Peak Signal-to-Noise Ratio) between two images.

    Parameters:
    - source_image_path: Path to the source/reference image.
    - modified_image_path: Path to the modified/test image.

    Returns:
    - PSNR value in decibels (dB). Higher values indicate better quality.
      Typical values: >40 dB (excellent), 30-40 dB (good), 20-30 dB (acceptable), <20 dB (poor)
    """
    source_image = cv2.imread(source_image_path)
    modified_image = cv2.imread(modified_image_path)

    # PSNR works on full color images, no need to convert to grayscale
    psnr_value = psnr(source_image, modified_image)
    return psnr_value

def get_images_similarity_and_psnr(source_image_path, modified_image_path):
    """
    Calculate both SSIM and PSNR between two images.

    Parameters:
    - source_image_path: Path to the source/reference image.
    - modified_image_path: Path to the modified/test image.

    Returns:
    - Dictionary with 'ssim' (percentage) and 'psnr' (dB) values.
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
