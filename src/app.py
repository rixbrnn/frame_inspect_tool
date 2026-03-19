import cv2
import os
import imagehash
from PIL import Image
import numpy as np
from tqdm import tqdm
import argparse
from colorama import Fore, Style, init
from skimage.metrics import structural_similarity as ssim
from src.comparison.image import get_images_similarity, get_images_similarity_in_directory, get_images_psnr, get_images_similarity_and_psnr
from src.comparison.video import generate_video_similarity_report, measure_video_stability

init(autoreset=True)

def main():
    parser = argparse.ArgumentParser(description="Compare images or videos using SSIM, PSNR, or perceptual hashes.")

    parser.add_argument('-s', '--source', required=False, help="Path to the source image.")
    parser.add_argument('-m', '--modified', required=False, help="Path to the modified image.")
    parser.add_argument('-d', '--directory', required=False, help="Path to the directory containing images to compare.")
    parser.add_argument('-v1', '--video1', required=False, help="Path to the first video.")
    parser.add_argument('-v2', '--video2', required=False, help="Path to the second video.")
    parser.add_argument('--find-intersection', action='store_true', help="Find common section between two videos using perceptual hashing.")
    parser.add_argument('--stability', required=False, help="Measure the stability of a video using SSIM or PSNR.")
    parser.add_argument('--method', required=False, default='ssim', help="Method to use: 'ssim', 'psnr', or 'pixel' (default: ssim)")
    parser.add_argument('--psnr', action='store_true', help="Include PSNR metric in addition to SSIM.")

    args = parser.parse_args()

    if args.source and args.modified:
        if args.psnr:
            metrics = get_images_similarity_and_psnr(args.source, args.modified)
            ssim_color = Fore.GREEN if metrics['ssim'] >= 99 else Fore.YELLOW if metrics['ssim'] >= 97 else Fore.RED
            psnr_color = Fore.GREEN if metrics['psnr'] >= 40 else Fore.YELLOW if metrics['psnr'] >= 30 else Fore.RED
            print(f"{Fore.CYAN}Image Similarity (SSIM): {ssim_color}{metrics['ssim']:.2f}%{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Image Quality (PSNR): {psnr_color}{metrics['psnr']:.2f} dB{Style.RESET_ALL}")
        else:
            score = get_images_similarity(args.source, args.modified)
            color = Fore.GREEN if score >= 99 else Fore.YELLOW if score >= 97 else Fore.RED
            print(f"{Fore.CYAN}Image Similarity (SSIM): {color}{score:.2f}%{Style.RESET_ALL}")

    elif args.source and args.directory:
        get_images_similarity_in_directory(args.source, args.directory, include_psnr=args.psnr)

    elif args.video1 and args.video2:
        generate_video_similarity_report(args.video1, args.video2, find_intersection=args.find_intersection, include_psnr=args.psnr)

    elif args.stability:
        # Call the stability function
        measure_video_stability(args.stability, args.method)

    else:
        print(f"{Fore.RED}Please provide valid arguments for either image or video comparison.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()