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

def cv2_to_pil_image(cv2_img):
    return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))

def get_frame_hash(cv2_img):
    pil_img = cv2_to_pil_image(cv2_img)
    return imagehash.phash(pil_img)

def compare_hashes(hash1, hash2, max_distance=5):
    return hash1 - hash2 <= max_distance


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

from tqdm import tqdm

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

    # Convert each frame of both videos to a perceptual hash
    hashes1 = [get_frame_hash(frame) for frame in tqdm(video1_frames, desc="Hashing video 1 frames")]
    hashes2 = [get_frame_hash(frame) for frame in tqdm(video2_frames, desc="Hashing video 2 frames")]

    len1 = len(hashes1)
    len2 = len(hashes2)

    best_match_start1 = None
    best_match_start2 = None
    longest_match_length = 0

    # Iterate through the frames in both videos
    for i1 in range(len1):
        for i2 in range(len2):
            match_length = 0
            offset1 = i1
            offset2 = i2

            # Check for matching consecutive frames
            while offset1 < len1 and offset2 < len2:
                if compare_hashes(hashes1[offset1], hashes2[offset2]):
                    match_length += 1
                    offset1 += 1
                    offset2 += 1
                else:
                    break

            # Update the best match if this one is longer than the previous
            if match_length > longest_match_length and match_length >= min_match_length:
                longest_match_length = match_length
                best_match_start1 = i1
                best_match_start2 = i2

    if longest_match_length == 0:
        return None, None, None, None

    best_end1 = best_match_start1 + longest_match_length - 1
    best_end2 = best_match_start2 + longest_match_length - 1

    return best_match_start1, best_end1, best_match_start2, best_end2



def generate_video_report(video_path1, video_path2, start1, start2, match_length):
    print("\n" + Fore.CYAN + "Video Comparison Report" + Style.RESET_ALL)
    print(f"Video 1: {video_path1} (Frames {start1} to {start1 + match_length - 1})")
    print(f"Video 2: {video_path2} (Frames {start2} to {start2 + match_length - 1})")
    print(f"Overlap length: {match_length} frames")
