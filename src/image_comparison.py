import cv2
import os
import imagehash
from PIL import Image
import numpy as np
from tqdm import tqdm
import argparse
from colorama import Fore, Style, init
from skimage.metrics import structural_similarity as ssim

init(autoreset=True)

def get_images_similarity(source_image_path, modified_image_path):
    source_image = cv2.imread(source_image_path)
    modified_image = cv2.imread(modified_image_path)

    before_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)

    (score, diff) = ssim(before_gray, after_gray, full=True)
    return score * 100

def get_images_similarity_in_directory(source_image_path, directory):
    results = []
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for filename in tqdm(files, desc="Processing images", unit="image"):
        file_path = os.path.join(directory, filename)
        if file_path == source_image_path:
            continue
        score = get_images_similarity(source_image_path, file_path)
        results.append({'filename': filename, 'score': score})
    generate_image_report(results)

def generate_image_report(results):
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    print("\n" + Fore.CYAN + "Image Comparison Report (Sorted by Similarity)" + Style.RESET_ALL)
    print(f"{'Image Name':<40}{'SSIM Score (%)':>15}")
    print("="*55)
    for result in sorted_results:
        score = result['score']
        filename = result['filename']
        color = Fore.GREEN if score >= 99 else Fore.YELLOW if score >= 97 else Fore.RED
        print(f"{filename:<40}{color}{score:.2f}{Style.RESET_ALL}")
