#!/usr/bin/env python3
"""
Video Preprocessing - Convert videos to constant frame rate for analysis
"""

import subprocess
from pathlib import Path
from typing import Optional
import json


def get_video_info(video_path: Path) -> dict:
    """
    Get video metadata using ffprobe

    Returns:
        {
            'fps': float,
            'frame_count': int,
            'duration': float,
            'width': int,
            'height': int,
            'is_cfr': bool
        }
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        '-select_streams', 'v:0',
        str(video_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)
    stream = data['streams'][0]

    # Parse frame rate
    fps_parts = stream['r_frame_rate'].split('/')
    fps = float(fps_parts[0]) / float(fps_parts[1])

    # Check if CFR (avg_frame_rate == r_frame_rate)
    avg_fps_parts = stream['avg_frame_rate'].split('/')
    avg_fps = float(avg_fps_parts[0]) / float(avg_fps_parts[1])
    is_cfr = abs(fps - avg_fps) < 0.01

    return {
        'fps': fps,
        'frame_count': int(stream.get('nb_frames', 0)),
        'duration': float(stream.get('duration', 0)),
        'width': int(stream['width']),
        'height': int(stream['height']),
        'is_cfr': is_cfr
    }


def convert_to_cfr(input_path: Path, output_path: Optional[Path] = None,
                   target_fps: int = 60, crf: int = 18) -> Path:
    """
    Convert video to constant frame rate (CFR) using FFmpeg

    Args:
        input_path: Input video file
        output_path: Output file path (default: input_60fps.mp4)
        target_fps: Target frame rate (default: 60)
        crf: Quality level (default: 18, lower = better quality)

    Returns:
        Path to the converted video
    """
    input_path = Path(input_path)

    if output_path is None:
        # Default: add _60fps suffix
        output_path = input_path.parent / f"{input_path.stem}_{target_fps}fps{input_path.suffix}"
    else:
        output_path = Path(output_path)

    # Check if already exists and is CFR
    if output_path.exists():
        try:
            info = get_video_info(output_path)
            if info['is_cfr'] and abs(info['fps'] - target_fps) < 0.01:
                print(f"✓ CFR video already exists: {output_path}")
                return output_path
        except:
            pass  # File exists but invalid, recreate

    print(f"Converting to CFR {target_fps} FPS: {input_path.name}")
    print(f"  → {output_path.name}")

    # FFmpeg command for CFR conversion
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output
        '-i', str(input_path),
        '-vf', f'fps={target_fps}',  # Force constant frame rate
        '-c:v', 'libx264',  # H.264 codec
        '-preset', 'slow',  # Better compression
        '-crf', str(crf),  # Quality level
        '-c:a', 'copy',  # Copy audio without re-encoding
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")

    # Verify output
    info = get_video_info(output_path)
    print(f"✓ Conversion complete:")
    print(f"  FPS: {info['fps']:.2f} (CFR: {info['is_cfr']})")
    print(f"  Frames: {info['frame_count']}")
    print(f"  Duration: {info['duration']:.2f}s")

    return output_path


def ensure_cfr(video_path: Path, target_fps: int = 60, crf: int = 18) -> Path:
    """
    Ensure video is CFR at target FPS, converting only if necessary

    Args:
        video_path: Input video
        target_fps: Target frame rate
        crf: Quality level for conversion

    Returns:
        Path to CFR video (original if already CFR, converted otherwise)
    """
    info = get_video_info(video_path)

    if info['is_cfr'] and abs(info['fps'] - target_fps) < 0.01:
        print(f"✓ Video is already CFR @ {target_fps} FPS: {video_path.name}")
        return video_path

    print(f"Video needs CFR conversion:")
    print(f"  Current: {info['fps']:.2f} FPS (CFR: {info['is_cfr']})")
    print(f"  Target: {target_fps} FPS (CFR: True)")

    return convert_to_cfr(video_path, target_fps=target_fps, crf=crf)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Convert video to constant frame rate')
    parser.add_argument('input', type=Path, help='Input video file')
    parser.add_argument('--output', type=Path, help='Output file (default: input_60fps.mp4)')
    parser.add_argument('--fps', type=int, default=60, help='Target FPS (default: 60)')
    parser.add_argument('--crf', type=int, default=18, help='Quality (default: 18, lower=better)')
    parser.add_argument('--info', action='store_true', help='Just show video info')

    args = parser.parse_args()

    if args.info:
        info = get_video_info(args.input)
        print(f"Video: {args.input}")
        print(f"  FPS: {info['fps']:.2f}")
        print(f"  CFR: {info['is_cfr']}")
        print(f"  Frames: {info['frame_count']}")
        print(f"  Duration: {info['duration']:.2f}s")
        print(f"  Resolution: {info['width']}x{info['height']}")
    else:
        output = convert_to_cfr(args.input, args.output, args.fps, args.crf)
        print(f"\n✓ Done: {output}")
