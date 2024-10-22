import cv2
import os
import imagehash
from PIL import Image
import numpy as np
from tqdm import tqdm
import argparse
from colorama import Fore, Style, init
from skimage.metrics import structural_similarity as ssim
import imageio

init(autoreset=True)

def cv2_to_pil_image(cv2_img):
    return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))

def get_frame_hash(cv2_img):
    pil_img = cv2_to_pil_image(cv2_img)
    return imagehash.phash(pil_img)

def compare_hashes(hash1, hash2, max_distance=5):
    return hash1 - hash2 <= max_distance

def get_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []

    print(f"{Fore.CYAN}Extracting frames from video: {video_path}{Style.RESET_ALL}")
    
    for i in tqdm(range(total_frames), desc="Extracting frames", unit="frame", dynamic_ncols=True):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    
    cap.release()
    return frames

def get_video_frames_with_imageio(video_path):
    """
    Get frames from a video using imageio.
    """
    reader = imageio.get_reader(video_path)
    frames = []
    for i, frame in enumerate(reader):
        frames.append(frame)
    return frames

def find_video_overlap(video1_frames, video2_frames, hash_size=16, min_match_length=3):
    """
    Find the overlap between two videos by comparing the perceptual hash of each frame.
    
    Parameters:
    - video1_frames: List of frames from the first video.
    - video2_frames: List of frames from the second video.
    - hash_size: The size of the perceptual hash.
    - min_match_length: The minimum number of consecutive matching frames to consider as overlap.
    
    Returns:
    - best_start1: The start frame of the overlap in the first video.
    - best_start2: The start frame of the overlap in the second video.
    - best_end1: The end frame of the overlap in the first video.
    - best_end2: The end frame of the overlap in the second video.
    """
    print(f"{Fore.CYAN}Hashing source video...{Style.RESET_ALL}")
    hashes1 = [get_frame_hash(frame) for frame in tqdm(video1_frames, desc="Hashing source video", unit="frame", dynamic_ncols=True)]
    
    print(f"{Fore.CYAN}Hashing target video...{Style.RESET_ALL}")
    hashes2 = [get_frame_hash(frame) for frame in tqdm(video2_frames, desc="Hashing target video", unit="frame", dynamic_ncols=True)]

    len1 = len(hashes1)
    len2 = len(hashes2)

    best_match_start1 = None
    best_match_start2 = None
    longest_match_length = 0

    for i1 in range(len1):
        for i2 in range(len2):
            match_length = 0
            offset1 = i1
            offset2 = i2

            while offset1 < len1 and offset2 < len2:
                if compare_hashes(hashes1[offset1], hashes2[offset2]):
                    match_length += 1
                    offset1 += 1
                    offset2 += 1
                else:
                    break

            if match_length > longest_match_length and match_length >= min_match_length:
                longest_match_length = match_length
                best_match_start1 = i1
                best_match_start2 = i2

    if longest_match_length == 0:
        return None, None, None, None

    best_end1 = best_match_start1 + longest_match_length - 1
    best_end2 = best_match_start2 + longest_match_length - 1

    return best_match_start1, best_end1, best_match_start2, best_end2


def measure_video_stability(video_path):
    """
    Measures the stability of a video by comparing consecutive frames using SSIM.
    If a directory is provided, it processes all video files in the directory.
    
    Parameters:
    - video_path: Path to a single video file or a directory of video files.
    """
    if os.path.isdir(video_path):
        # If it's a directory, loop through all video files and measure stability
        video_files = [os.path.join(video_path, f) for f in os.listdir(video_path) if f.endswith(('.mp4', '.avi', '.mkv', '.h265'))]
        if not video_files:
            print(f"{Fore.RED}No video files found in directory: {video_path}{Style.RESET_ALL}")
            return

        print(f"{Fore.CYAN}Processing all videos in the directory: {video_path}{Style.RESET_ALL}")
        for video_file in video_files:
            print(f"\nProcessing video: {video_file}")
            measure_video_stability(video_file)
        return

    # If it's a single video file, measure the stability using SSIM
    print(f"{Fore.CYAN}Measuring stability for: {video_path}{Style.RESET_ALL}")
    frames = get_video_frames_with_imageio(video_path)
    
    if len(frames) < 2:
        print(f"{Fore.RED}Not enough frames to compare in video: {video_path}{Style.RESET_ALL}")
        return

    ssim_scores = []
    print(f"{Fore.CYAN}Comparing frames for stability in: {video_path}{Style.RESET_ALL}")
    
    for i in tqdm(range(1, len(frames)), desc="Comparing frames", unit="frame"):
        # Convert the frames to grayscale for SSIM comparison
        frame1_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
        frame2_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)

        # Compute SSIM between the current and the previous frame
        score, _ = ssim(frame1_gray, frame2_gray, full=True)
        ssim_scores.append(score)

    # Calculate the average SSIM across all consecutive frames
    average_ssim = np.mean(ssim_scores) * 100  # Convert to percentage
    print(f"{Fore.GREEN}Average SSIM for video stability in {video_path}: {average_ssim:.2f}%{Style.RESET_ALL}")
    return average_ssim


def generate_video_similarity_report(video1_path, video2_path, find_intersection=False):
    """
    Generate a video similarity report based on SSIM scores between two videos.
    Optionally, only compare the overlapping section if find_intersection is True.

    Parameters:
    - video1_path: Path to the first video.
    - video2_path: Path to the second video.
    - find_intersection: If True, only compare the overlapping section.

    Returns:
    - None: Prints the similarity report.
    """
    average_ssim = get_video_similarity(video1_path, video2_path, find_intersection)

    if average_ssim is None:
        return

    print("\n" + Fore.CYAN + "Video Similarity Report" + Style.RESET_ALL)
    print(f"Average SSIM Similarity Score: {Fore.GREEN if average_ssim >= 99 else Fore.YELLOW if average_ssim >= 97 else Fore.RED}{average_ssim:.2f}%{Style.RESET_ALL}")


