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



def measure_video_stability(video_path, method='ssim'):
    """
    Measure the stability of a video using SSIM, PSNR, or pixel-by-pixel comparison between consecutive frames.
    If a directory is provided, it processes all video files in the directory.

    Parameters:
    - video_path: Path to a single video file or a directory of video files.
    - method: The method used to measure stability ('ssim' for structural similarity, 'psnr' for PSNR, 'pixel' for pixel-by-pixel comparison).
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
            measure_video_stability(video_file, method)
        return
    # If it's a single file, measure the stability based on the chosen method
    print(f"{Fore.CYAN}Measuring stability for: {video_path} using {method.upper()}{Style.RESET_ALL}")
    frames = get_video_frames_with_imageio(video_path)

    if len(frames) < 2:
        print(f"{Fore.RED}Not enough frames to compare in video: {video_path}{Style.RESET_ALL}")
        return

    if method == 'ssim':
        # SSIM-based stability measurement
        ssim_scores = []
        print(f"{Fore.CYAN}Comparing frames using SSIM for stability in: {video_path}{Style.RESET_ALL}")

        for i in tqdm(range(1, len(frames)), desc="Comparing frames", unit="frame"):
            frame1_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            frame2_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            score, _ = ssim(frame1_gray, frame2_gray, full=True)
            ssim_scores.append(score)
        average_ssim = np.mean(ssim_scores) * 100  # Convert to percentage
        print(f"{Fore.GREEN}Average SSIM for video stability in {video_path}: {average_ssim:.2f}%{Style.RESET_ALL}")
        return average_ssim
    elif method == 'psnr':
        # PSNR-based stability measurement
        psnr_scores = []
        print(f"{Fore.CYAN}Comparing frames using PSNR for stability in: {video_path}{Style.RESET_ALL}")

        for i in tqdm(range(1, len(frames)), desc="Comparing frames", unit="frame"):
            # PSNR works on full color images
            frame1 = frames[i-1]
            frame2 = frames[i]
            psnr_value = psnr(frame1, frame2)
            psnr_scores.append(psnr_value)
        average_psnr = np.mean(psnr_scores)
        print(f"{Fore.GREEN}Average PSNR for video stability in {video_path}: {average_psnr:.2f} dB{Style.RESET_ALL}")
        return average_psnr
    elif method == 'pixel':
        # Pixel-by-pixel stability measurement
        differences = []
        print(f"{Fore.CYAN}Comparing frames using pixel-by-pixel method for stability in: {video_path}{Style.RESET_ALL}")

        for i in tqdm(range(1, len(frames)), desc="Comparing frames", unit="frame"):
            current_frame = frames[i]
            previous_frame = frames[i - 1]
            diff = np.sum(np.abs(current_frame.astype(np.float32) - previous_frame.astype(np.float32)))
            num_pixels = current_frame.shape[0] * current_frame.shape[1] * current_frame.shape[2]
            normalized_diff = diff / num_pixels
            differences.append(normalized_diff)

        avg_difference = np.mean(differences)
        avg_difference_percentage = (1 - avg_difference) * 100  # Convert to percentage
        print(f"{Fore.GREEN}Average pixel-by-pixel frame difference for {video_path}: {avg_difference_percentage:.2f}%{Style.RESET_ALL}")
        return avg_difference_percentage
    else:
        print(f"{Fore.RED}Invalid method selected. Use 'ssim', 'psnr', or 'pixel'.{Style.RESET_ALL}")
        return


def get_video_similarity(video1_path, video2_path, find_intersection=False, metric='ssim'):
    """
    Calculate similarity between two videos using SSIM or PSNR.

    Parameters:
    - video1_path: Path to the first video.
    - video2_path: Path to the second video.
    - find_intersection: If True, automatically find overlapping section using perceptual hashing.
    - metric: Metric to use ('ssim' or 'psnr').

    Returns:
    - Average similarity score (SSIM as percentage or PSNR in dB).
    """
    print(f"{Fore.CYAN}Loading videos...{Style.RESET_ALL}")
    video1_frames = get_video_frames_with_imageio(video1_path)
    video2_frames = get_video_frames_with_imageio(video2_path)

    if find_intersection:
        print(f"{Fore.CYAN}Finding overlap between videos...{Style.RESET_ALL}")
        start1, end1, start2, end2 = find_video_overlap(video1_frames, video2_frames)

        if start1 is None:
            print(f"{Fore.RED}No overlap found between videos.{Style.RESET_ALL}")
            return None

        print(f"{Fore.GREEN}Overlap found: Video1[{start1}:{end1}] <-> Video2[{start2}:{end2}]{Style.RESET_ALL}")
        video1_frames = video1_frames[start1:end1+1]
        video2_frames = video2_frames[start2:end2+1]

    # Ensure both videos have the same number of frames
    min_frames = min(len(video1_frames), len(video2_frames))
    video1_frames = video1_frames[:min_frames]
    video2_frames = video2_frames[:min_frames]

    scores = []
    print(f"{Fore.CYAN}Comparing frames using {metric.upper()}...{Style.RESET_ALL}")

    for i in tqdm(range(len(video1_frames)), desc=f"Computing {metric.upper()}", unit="frame"):
        if metric == 'ssim':
            frame1_gray = cv2.cvtColor(video1_frames[i], cv2.COLOR_BGR2GRAY)
            frame2_gray = cv2.cvtColor(video2_frames[i], cv2.COLOR_BGR2GRAY)
            score, _ = ssim(frame1_gray, frame2_gray, full=True)
            scores.append(score * 100)  # Convert to percentage
        elif metric == 'psnr':
            psnr_value = psnr(video1_frames[i], video2_frames[i])
            scores.append(psnr_value)

    average_score = np.mean(scores)
    return average_score


def generate_video_similarity_report(video1_path, video2_path, find_intersection=False, include_psnr=False):
    """
    Generate a video similarity report based on SSIM and optionally PSNR between two videos.
    Optionally, only compare the overlapping section if find_intersection is True.

    Parameters:
    - video1_path: Path to the first video.
    - video2_path: Path to the second video.
    - find_intersection: If True, only compare the overlapping section.
    - include_psnr: If True, also calculate and display PSNR.

    Returns:
    - None: Prints the similarity report.
    """
    average_ssim = get_video_similarity(video1_path, video2_path, find_intersection, metric='ssim')

    if average_ssim is None:
        return

    print("\n" + Fore.CYAN + "Video Similarity Report" + Style.RESET_ALL)
    print(f"Average SSIM Similarity Score: {Fore.GREEN if average_ssim >= 99 else Fore.YELLOW if average_ssim >= 97 else Fore.RED}{average_ssim:.2f}%{Style.RESET_ALL}")

    if include_psnr:
        average_psnr = get_video_similarity(video1_path, video2_path, find_intersection, metric='psnr')
        if average_psnr is not None:
            psnr_color = Fore.GREEN if average_psnr >= 40 else Fore.YELLOW if average_psnr >= 30 else Fore.RED
            print(f"Average PSNR: {psnr_color}{average_psnr:.2f} dB{Style.RESET_ALL}")


