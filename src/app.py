import cv2
import os
import imagehash
from PIL import Image
import numpy as np
from tqdm import tqdm
import argparse
from colorama import Fore, Style, init
from skimage.metrics import structural_similarity as ssim

# Initialize colorama
init(autoreset=True)

# Compare two images using SSIM
def get_images_similarity(source_image_path, modified_image_path):
    source_image = cv2.imread(source_image_path)
    modified_image = cv2.imread(modified_image_path)

    before_gray = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(modified_image, cv2.COLOR_BGR2GRAY)

    (score, diff) = ssim(before_gray, after_gray, full=True)
    return score * 100

# Compare all images in a directory with the source image
def compare_with_directory(source_image_path, directory):
    results = []
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for filename in tqdm(files, desc="Processing images", unit="image"):
        file_path = os.path.join(directory, filename)
        if file_path == source_image_path:
            continue
        score = get_images_similarity(source_image_path, file_path)
        results.append({'filename': filename, 'score': score})
    generate_image_report(results)

# Generate a report for image comparisons
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

# Convert OpenCV image to PIL image
def cv2_to_pil_image(cv2_img):
    return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))

# Function to calculate perceptual hash of a frame
def get_frame_hash(cv2_img):
    pil_img = cv2_to_pil_image(cv2_img)
    return imagehash.phash(pil_img)  # Using perceptual hash (pHash)

# Compare hashes with tolerance
def compare_hashes(hash1, hash2, max_distance=5):
    return hash1 - hash2 <= max_distance


# Function to extract frames from a video
def get_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def find_video_overlap(frames1, frames2, hash_size=16, threshold=3):
    len1 = len(frames1)
    len2 = len(frames2)

    best_match_start1 = None
    best_match_start2 = None
    longest_match_length = 0

    # Get perceptual hashes for both sets of frames
    hashes1 = [get_frame_hash(frame) for frame in tqdm(frames1, desc="Hashing video 1 frames")]
    hashes2 = [get_frame_hash(frame) for frame in tqdm(frames2, desc="Hashing video 2 frames")]

    # Iterate over all possible starting points in video1 to find the best match
    for i1 in range(len1):
        for i2 in range(len2):
            match_length = 0
            offset1 = i1
            offset2 = i2

            # Compare frames at the current starting point
            while offset1 < len1 and offset2 < len2:
                if compare_hashes(hashes1[offset1], hashes2[offset2]):
                    match_length += 1
                    offset1 += 1
                    offset2 += 1
                else:
                    break  # Break the loop if hashes don't match

            # Check if we found a longer match
            if match_length > longest_match_length and match_length >= threshold:
                longest_match_length = match_length
                best_match_start1 = i1
                best_match_start2 = i2

    # If no match is found, return None for both starts
    if longest_match_length == 0:
        return None, None, 0

    return best_match_start1, best_match_start2, longest_match_length





# Generate a report for video comparisons
def generate_video_report(video_path1, video_path2, start1, start2, match_length):
    print("\n" + Fore.CYAN + "Video Comparison Report" + Style.RESET_ALL)
    print(f"Video 1: {video_path1} (Frames {start1} to {start1 + match_length - 1})")
    print(f"Video 2: {video_path2} (Frames {start2} to {start2 + match_length - 1})")
    print(f"Overlap length: {match_length} frames")

def main():
    parser = argparse.ArgumentParser(description="Compare images or videos using SSIM or perceptual hashes.")
    
    # Add arguments for image comparison
    parser.add_argument('-s', '--source', required=False, help="Path to the source image.")
    parser.add_argument('-m', '--modified', required=False, help="Path to the modified image.")
    parser.add_argument('-d', '--directory', required=False, help="Path to the directory containing images to compare.")

    # Add arguments for video comparison
    parser.add_argument('-v1', '--video1', required=False, help="Path to the first video.")
    parser.add_argument('-v2', '--video2', required=False, help="Path to the second video.")
    parser.add_argument('--find-intersection', action='store_true', help="Find common section between two videos using perceptual hashing.")

    args = parser.parse_args()

    # Image comparison logic
    if args.source and args.modified:
        score = get_images_similarity(args.source, args.modified)
        color = Fore.GREEN if score >= 99 else Fore.YELLOW if score >= 97 else Fore.RED
        print(f"{Fore.CYAN}Image Similarity (SSIM): {color}{score:.2f}%{Style.RESET_ALL}")

    elif args.source and args.directory:
        compare_with_directory(args.source, args.directory)

    # Video comparison logic
    elif args.video1 and args.video2:
        # Get frames from both videos
        frames1 = get_video_frames(args.video1)
        frames2 = get_video_frames(args.video2)

        # If --find-intersection flag is provided, find the intersection using perceptual hashing
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
