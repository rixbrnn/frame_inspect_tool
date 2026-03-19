#!/usr/bin/env python3
"""
Video Synchronization - Align videos with different frame counts for comparison
"""

import cv2
import numpy as np
from typing import List, Tuple
from tqdm import tqdm


def align_videos_by_timestamps(video1_frames: List[np.ndarray],
                                 video2_frames: List[np.ndarray],
                                 fps1: float, fps2: float) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """
    Align two videos by interpolating frames to match timestamps

    Strategy:
    1. Create timestamp arrays for both videos
    2. Interpolate shorter video to match longer video's frame count
    3. Return aligned frame lists

    Args:
        video1_frames: List of frames from video 1
        video2_frames: List of frames from video 2
        fps1: FPS of video 1
        fps2: FPS of video 2

    Returns:
        (aligned_frames1, aligned_frames2) - same length
    """
    len1 = len(video1_frames)
    len2 = len(video2_frames)

    if len1 == len2:
        return video1_frames, video2_frames

    print(f"Aligning videos: {len1} frames vs {len2} frames")

    # Generate timestamps for each frame
    timestamps1 = np.array([i / fps1 for i in range(len1)])
    timestamps2 = np.array([i / fps2 for i in range(len2)])

    # Use the longer video as reference
    if len1 > len2:
        reference_timestamps = timestamps1
        interpolate_video2 = True
    else:
        reference_timestamps = timestamps2
        interpolate_video2 = False

    if interpolate_video2:
        # Interpolate video2 to match video1's frame count
        aligned_frames2 = []
        for t in tqdm(reference_timestamps, desc="Interpolating video 2"):
            frame_idx = np.searchsorted(timestamps2, t)

            if frame_idx >= len2:
                # Beyond video2 duration, duplicate last frame
                aligned_frames2.append(video2_frames[-1])
            elif frame_idx == 0:
                aligned_frames2.append(video2_frames[0])
            else:
                # Linear interpolation between frames
                t1 = timestamps2[frame_idx - 1]
                t2 = timestamps2[frame_idx]
                alpha = (t - t1) / (t2 - t1) if t2 != t1 else 0

                frame1 = video2_frames[frame_idx - 1].astype(np.float32)
                frame2 = video2_frames[frame_idx].astype(np.float32)
                interpolated = (1 - alpha) * frame1 + alpha * frame2
                aligned_frames2.append(interpolated.astype(np.uint8))

        return video1_frames, aligned_frames2
    else:
        # Interpolate video1 to match video2's frame count
        aligned_frames1 = []
        for t in tqdm(reference_timestamps, desc="Interpolating video 1"):
            frame_idx = np.searchsorted(timestamps1, t)

            if frame_idx >= len1:
                aligned_frames1.append(video1_frames[-1])
            elif frame_idx == 0:
                aligned_frames1.append(video1_frames[0])
            else:
                t1 = timestamps1[frame_idx - 1]
                t2 = timestamps1[frame_idx]
                alpha = (t - t1) / (t2 - t1) if t2 != t1 else 0

                frame1 = video1_frames[frame_idx - 1].astype(np.float32)
                frame2 = video1_frames[frame_idx].astype(np.float32)
                interpolated = (1 - alpha) * frame1 + alpha * frame2
                aligned_frames1.append(interpolated.astype(np.uint8))

        return aligned_frames1, video2_frames


def align_videos_by_duration(video1_frames: List[np.ndarray],
                               video2_frames: List[np.ndarray],
                               target_duration: float,
                               target_fps: float) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """
    Align videos to a target duration and FPS by resampling

    Args:
        video1_frames: Frames from video 1
        video2_frames: Frames from video 2
        target_duration: Desired duration in seconds
        target_fps: Desired FPS

    Returns:
        (resampled_frames1, resampled_frames2) - both with target_duration * target_fps frames
    """
    target_frame_count = int(target_duration * target_fps)

    print(f"Resampling videos to {target_frame_count} frames ({target_duration}s @ {target_fps} FPS)")

    def resample_video(frames, target_count):
        """Resample a video to target frame count"""
        original_count = len(frames)
        indices = np.linspace(0, original_count - 1, target_count)

        resampled = []
        for idx in tqdm(indices, desc="Resampling"):
            lower_idx = int(np.floor(idx))
            upper_idx = int(np.ceil(idx))

            if lower_idx == upper_idx:
                resampled.append(frames[lower_idx])
            else:
                # Linear interpolation
                alpha = idx - lower_idx
                frame1 = frames[lower_idx].astype(np.float32)
                frame2 = frames[upper_idx].astype(np.float32)
                interpolated = (1 - alpha) * frame1 + alpha * frame2
                resampled.append(interpolated.astype(np.uint8))

        return resampled

    aligned_frames1 = resample_video(video1_frames, target_frame_count)
    aligned_frames2 = resample_video(video2_frames, target_frame_count)

    return aligned_frames1, aligned_frames2


if __name__ == "__main__":
    import argparse
    import imageio

    parser = argparse.ArgumentParser(description='Align videos for frame-by-frame comparison')
    parser.add_argument('--video1', required=True, help='First video file')
    parser.add_argument('--video2', required=True, help='Second video file')
    parser.add_argument('--method', choices=['timestamps', 'duration'], default='duration',
                        help='Alignment method')
    parser.add_argument('--target-duration', type=float, help='Target duration in seconds (duration mode)')
    parser.add_argument('--target-fps', type=float, default=60, help='Target FPS (duration mode)')
    parser.add_argument('--output1', help='Output aligned video 1')
    parser.add_argument('--output2', help='Output aligned video 2')

    args = parser.parse_args()

    # Load videos
    print("Loading videos...")
    reader1 = imageio.get_reader(args.video1)
    reader2 = imageio.get_reader(args.video2)

    frames1 = [frame for frame in reader1]
    frames2 = [frame for frame in reader2]

    fps1 = reader1.get_meta_data()['fps']
    fps2 = reader2.get_meta_data()['fps']

    print(f"Video 1: {len(frames1)} frames @ {fps1} FPS")
    print(f"Video 2: {len(frames2)} frames @ {fps2} FPS")

    # Align
    if args.method == 'timestamps':
        aligned1, aligned2 = align_videos_by_timestamps(frames1, frames2, fps1, fps2)
    else:  # duration
        if not args.target_duration:
            args.target_duration = min(len(frames1) / fps1, len(frames2) / fps2)
        aligned1, aligned2 = align_videos_by_duration(frames1, frames2,
                                                       args.target_duration, args.target_fps)

    print(f"\nAligned: {len(aligned1)} frames, {len(aligned2)} frames")

    # Save if output specified
    if args.output1:
        print(f"Saving {args.output1}...")
        writer1 = imageio.get_writer(args.output1, fps=args.target_fps)
        for frame in tqdm(aligned1, desc="Writing video 1"):
            writer1.append_data(frame)
        writer1.close()

    if args.output2:
        print(f"Saving {args.output2}...")
        writer2 = imageio.get_writer(args.output2, fps=args.target_fps)
        for frame in tqdm(aligned2, desc="Writing video 2"):
            writer2.append_data(frame)
        writer2.close()

    print("Done!")
