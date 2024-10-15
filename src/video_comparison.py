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

def find_video_overlap(frames1, frames2, hash_size=16, threshold=3):
    len1 = len(frames1)
    len2 = len(frames2)

    best_match_start1 = None
    best_match_start2 = None
    longest_match_length = 0

    hashes1 = [get_frame_hash(frame) for frame in tqdm(frames1, desc="Hashing video 1 frames")]
    hashes2 = [get_frame_hash(frame) for frame in tqdm(frames2, desc="Hashing video 2 frames")]

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

            if match_length > longest_match_length and match_length >= threshold:
                longest_match_length = match_length
                best_match_start1 = i1
                best_match_start2 = i2

    if longest_match_length == 0:
        return None, None, 0

    return best_match_start1, best_match_start2, longest_match_length


def generate_video_report(video_path1, video_path2, start1, start2, match_length):
    print("\n" + Fore.CYAN + "Video Comparison Report" + Style.RESET_ALL)
    print(f"Video 1: {video_path1} (Frames {start1} to {start1 + match_length - 1})")
    print(f"Video 2: {video_path2} (Frames {start2} to {start2 + match_length - 1})")
    print(f"Overlap length: {match_length} frames")
