import cv2
import os
import imagehash
from PIL import Image
import numpy as np
from tqdm import tqdm
import argparse
from colorama import Fore, Style, init
from skimage.metrics import structural_similarity as ssim
from image_comparison import get_images_similarity, get_images_similarity_in_directory
from video_comparison import generate_video_similarity_report, measure_video_stability

init(autoreset=True)

def main():
    parser = argparse.ArgumentParser(description="Compare images or videos using SSIM or perceptual hashes.")
    
    parser.add_argument('-s', '--source', required=False, help="Path to the source image.")
    parser.add_argument('-m', '--modified', required=False, help="Path to the modified image.")
    parser.add_argument('-d', '--directory', required=False, help="Path to the directory containing images to compare.")
    parser.add_argument('-v1', '--video1', required=False, help="Path to the first video.")
    parser.add_argument('-v2', '--video2', required=False, help="Path to the second video.")
    parser.add_argument('--find-intersection', action='store_true', help="Find common section between two videos using perceptual hashing.")
    parser.add_argument('--stability', required=False, help="Measure the stability of a video using SSIM.")
    parser.add_argument('--method', required=False, help="What method to use when measuring the stability, can be either ssim or pixel (for pixel by pixel)")

    args = parser.parse_args()

    if args.source and args.modified:
        score = get_images_similarity(args.source, args.modified)
        color = Fore.GREEN if score >= 99 else Fore.YELLOW if score >= 97 else Fore.RED
        print(f"{Fore.CYAN}Image Similarity (SSIM): {color}{score:.2f}%{Style.RESET_ALL}")

    elif args.source and args.directory:
        get_images_similarity_in_directory(args.source, args.directory)

    elif args.video1 and args.video2:
        generate_video_similarity_report(args.video1, args.video2, find_intersection=args.find_intersection)

    elif args.stability:
        # Call the stability function
        measure_video_stability(args.stability, args.method)

    else:
        print(f"{Fore.RED}Please provide valid arguments for either image or video comparison.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()