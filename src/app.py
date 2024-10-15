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
from video_comparison import get_video_frames, find_video_overlap

init(autoreset=True)

def main():
    parser = argparse.ArgumentParser(description="Compare images or videos using SSIM or perceptual hashes.")
    
    parser.add_argument('-s', '--source', required=False, help="Path to the source image.")
    parser.add_argument('-m', '--modified', required=False, help="Path to the modified image.")
    parser.add_argument('-d', '--directory', required=False, help="Path to the directory containing images to compare.")

    parser.add_argument('-v1', '--video1', required=False, help="Path to the first video.")
    parser.add_argument('-v2', '--video2', required=False, help="Path to the second video.")
    parser.add_argument('--find-intersection', action='store_true', help="Find common section between two videos using perceptual hashing.")

    args = parser.parse_args()

    if args.source and args.modified:
        score = get_images_similarity(args.source, args.modified)
        color = Fore.GREEN if score >= 99 else Fore.YELLOW if score >= 97 else Fore.RED
        print(f"{Fore.CYAN}Image Similarity (SSIM): {color}{score:.2f}%{Style.RESET_ALL}")

    elif args.source and args.directory:
        get_images_similarity_in_directory(args.source, args.directory)

    elif args.video1 and args.video2:
        frames1 = get_video_frames(args.video1)
        frames2 = get_video_frames(args.video2)

        if args.find_intersection:
            best_start1, best_start2, match_length = find_video_overlap(frames1, frames2)
            if best_start1 is not None and best_start2 is not None:
                generate_video_report(args.video1, args.video2, best_start1, best_start2, match_length)
            else:
                print("No common section found.")
        else:
            print(f"{Fore.RED}Please provide the --find-intersection flag to find video overlap.{Style.RESET_ALL}")

    else:
        print(f"{Fore.RED}Please provide valid arguments for either image or video comparison.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
