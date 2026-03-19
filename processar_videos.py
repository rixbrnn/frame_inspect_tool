#!/usr/bin/env python3
"""
Video CFR Processor - Convert videos to Constant Frame Rate

Converts raw video recordings to CFR (Constant Frame Rate) at 60 FPS
with exactly 60 seconds duration, ensuring all videos have exactly 3600 frames
for frame-by-frame comparison.

Usage:
    python processar_videos.py
    python processar_videos.py --modes DLAA_4K Quality
    python processar_videos.py --input ../tcc/recordings/raw --output ../tcc/recordings/processed
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Dict
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Default directories
DEFAULT_INPUT_DIR = Path("../tcc/recordings/raw")
DEFAULT_OUTPUT_DIR = Path("../tcc/recordings/processed")

# DLSS modes
ALL_MODES = ["DLAA_4K", "Quality", "Balanced", "Performance", "Ultra_Performance"]


def print_success(text: str):
    """Print success message"""
    print(f"{Fore.GREEN}  ✓ {text}{Style.RESET_ALL}")


def print_error(text: str):
    """Print error message"""
    print(f"{Fore.RED}  ✗ {text}{Style.RESET_ALL}")


def verify_frame_count(video_path: Path) -> int:
    """
    Verify frame count of a video using ffprobe

    Args:
        video_path: Path to video file

    Returns:
        Number of frames in the video
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-count_packets",
        "-show_entries", "stream=nb_read_packets",
        "-of", "csv=p=0",
        str(video_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return int(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to verify frame count: {e.stderr}")
        return -1
    except FileNotFoundError:
        print_error("ffprobe not found. Please install FFmpeg.")
        sys.exit(1)


def convert_to_cfr(
    input_file: Path,
    output_file: Path,
    fps: int = 60,
    duration: int = 60,
    crf: int = 18
) -> bool:
    """
    Convert video to CFR (Constant Frame Rate)

    Args:
        input_file: Input video path
        output_file: Output video path
        fps: Target frame rate (default: 60)
        duration: Target duration in seconds (default: 60)
        crf: Quality setting (0=lossless, 18=very high, 23=default, 51=worst)

    Returns:
        True if successful, False otherwise
    """
    cmd = [
        "ffmpeg",
        "-i", str(input_file),
        "-vf", f"fps={fps}",
        "-t", str(duration),
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-an",  # Remove audio
        str(output_file),
        "-y",  # Overwrite output file
        "-loglevel", "error"  # Only show errors
    ]

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"FFmpeg failed: {e}")
        return False
    except FileNotFoundError:
        print_error("ffmpeg not found. Please install FFmpeg.")
        sys.exit(1)


def process_videos(
    modes: List[str],
    input_dir: Path,
    output_dir: Path,
    fps: int = 60,
    duration: int = 60,
    crf: int = 18
) -> Dict[str, int]:
    """
    Process multiple videos to CFR

    Args:
        modes: List of DLSS modes to process
        input_dir: Input directory containing raw videos
        output_dir: Output directory for processed videos
        fps: Target frame rate
        duration: Target duration in seconds
        crf: Quality setting

    Returns:
        Dict mapping mode to frame count
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Validate input files
    missing_files = []
    for mode in modes:
        input_file = input_dir / f"{mode}_raw.mp4"
        if not input_file.exists():
            missing_files.append(mode)

    if missing_files:
        print_error(f"Missing input files: {', '.join(missing_files)}")
        print_error(f"Expected location: {input_dir}/")
        sys.exit(1)

    print(f"{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{'Processando gravações para CFR 60 FPS'.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

    frame_counts = {}

    for mode in tqdm(modes, desc="Processing videos", unit="video"):
        input_file = input_dir / f"{mode}_raw.mp4"
        output_file = output_dir / f"{mode}_60fps.mp4"

        # Convert to CFR
        success = convert_to_cfr(input_file, output_file, fps, duration, crf)

        if not success:
            tqdm.write(f"{Fore.RED}    ✗ {mode}: Failed to process{Style.RESET_ALL}")
            frame_counts[mode] = -1
            continue

        # Verify frame count
        frame_count = verify_frame_count(output_file)
        frame_counts[mode] = frame_count

        expected_frames = fps * duration

        if frame_count == expected_frames:
            tqdm.write(f"{Fore.GREEN}    ✓ {mode}: {frame_count} frames{Style.RESET_ALL}")
        elif frame_count > 0:
            tqdm.write(f"{Fore.YELLOW}    ⚠ {mode}: {frame_count} frames (expected {expected_frames}){Style.RESET_ALL}")
        else:
            tqdm.write(f"{Fore.RED}    ✗ {mode}: Failed to verify frame count{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.GREEN}{'Processamento concluído!'.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

    return frame_counts


def main():
    parser = argparse.ArgumentParser(
        description="Convert videos to CFR (Constant Frame Rate) for frame-by-frame comparison"
    )
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=ALL_MODES,
        default=ALL_MODES,
        help="DLSS modes to process (default: all)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Input directory (default: {DEFAULT_INPUT_DIR})"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=60,
        help="Target frame rate (default: 60)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Target duration in seconds (default: 60)"
    )
    parser.add_argument(
        "--crf",
        type=int,
        default=18,
        help="Quality setting (0=lossless, 18=very high, 23=default, 51=worst)"
    )

    args = parser.parse_args()

    try:
        frame_counts = process_videos(
            args.modes,
            args.input,
            args.output,
            args.fps,
            args.duration,
            args.crf
        )

        # Summary
        print(f"{Fore.YELLOW}Summary:{Style.RESET_ALL}")
        for mode, count in frame_counts.items():
            if count == args.fps * args.duration:
                print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {mode}: {count} frames")
            elif count > 0:
                print(f"  {Fore.YELLOW}⚠{Style.RESET_ALL} {mode}: {count} frames")
            else:
                print(f"  {Fore.RED}✗{Style.RESET_ALL} {mode}: Failed")

        # Check if all succeeded
        failed = [m for m, c in frame_counts.items() if c != args.fps * args.duration]
        if failed:
            print(f"\n{Fore.YELLOW}Note: Some videos have incorrect frame count.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}This may cause issues with frame-by-frame comparison.{Style.RESET_ALL}")
            sys.exit(1)

    except KeyboardInterrupt:
        print_error("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
