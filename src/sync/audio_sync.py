#!/usr/bin/env python3
"""
Audio-Based Video Synchronization

Uses audio cross-correlation to automatically align videos by matching their audio tracks.
This is robust to visual differences and works well for game recordings with identical audio.

Algorithm:
1. Extract audio from both videos
2. Convert to mono, resample to consistent rate
3. Compute cross-correlation between audio signals
4. Find peak correlation to determine time offset
5. Convert time offset to frame numbers

Advantages:
- Works with different visual content (different gameplay)
- Robust to compression artifacts
- Fast computation (audio is much smaller than video)
- No manual alignment needed if audio is identical

References:
- Audio fingerprinting: https://en.wikipedia.org/wiki/Acoustic_fingerprint
- Cross-correlation: https://en.wikipedia.org/wiki/Cross-correlation
"""

import subprocess
import tempfile
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict
from scipy import signal
from scipy.io import wavfile
import json


def extract_audio_to_wav(
    video_path: str,
    output_wav: str = None,
    sample_rate: int = 8000,
    mono: bool = True
) -> str:
    """
    Extract audio from video to WAV file using ffmpeg.

    Args:
        video_path: Path to video file
        output_wav: Output WAV path (temp file if None)
        sample_rate: Audio sample rate (lower = faster, 8kHz sufficient for sync)
        mono: Convert to mono (recommended for sync)

    Returns:
        Path to output WAV file
    """
    if output_wav is None:
        temp_dir = tempfile.mkdtemp()
        output_wav = str(Path(temp_dir) / "audio.wav")

    # Build ffmpeg command
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vn',  # No video
        '-acodec', 'pcm_s16le',  # PCM 16-bit
        '-ar', str(sample_rate),  # Sample rate
        '-y',  # Overwrite
    ]

    if mono:
        cmd.extend(['-ac', '1'])  # Mono

    cmd.append(output_wav)

    print(f"Extracting audio from {Path(video_path).name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    print(f"  ✓ Saved to {output_wav}")
    return output_wav


def load_audio_data(wav_path: str) -> Tuple[np.ndarray, int]:
    """
    Load audio data from WAV file.

    Args:
        wav_path: Path to WAV file

    Returns:
        (audio_data, sample_rate) tuple
        audio_data is normalized to [-1, 1]
    """
    sample_rate, data = wavfile.read(wav_path)

    # Convert to float and normalize
    if data.dtype == np.int16:
        data = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / 2147483648.0

    print(f"  Loaded audio: {len(data)} samples @ {sample_rate}Hz ({len(data)/sample_rate:.1f}s)")

    return data, sample_rate


def find_audio_offset_correlation(
    audio1: np.ndarray,
    audio2: np.ndarray,
    sample_rate: int,
    max_offset_seconds: float = 60.0
) -> Tuple[float, float]:
    """
    Find time offset between two audio signals using cross-correlation.

    Args:
        audio1: First audio signal
        audio2: Second audio signal
        sample_rate: Audio sample rate
        max_offset_seconds: Maximum offset to search (limits computation)

    Returns:
        (offset_seconds, correlation_strength) tuple
        Positive offset means audio2 is delayed relative to audio1
    """
    print("\nComputing audio cross-correlation...")

    # Limit search window for performance
    max_offset_samples = int(max_offset_seconds * sample_rate)

    # Trim longer signal if needed
    if len(audio1) > len(audio2):
        audio1 = audio1[:len(audio2) + max_offset_samples]
    else:
        audio2 = audio2[:len(audio1) + max_offset_samples]

    print(f"  Signal 1: {len(audio1)} samples")
    print(f"  Signal 2: {len(audio2)} samples")
    print(f"  Max offset: ±{max_offset_seconds}s")

    # Compute cross-correlation using FFT (fast)
    correlation = signal.correlate(audio1, audio2, mode='valid')

    # Find peak
    peak_idx = np.argmax(np.abs(correlation))
    peak_value = correlation[peak_idx]

    # Convert to time offset
    # Positive lag means audio2 starts later
    offset_samples = peak_idx - len(audio2) + 1
    offset_seconds = offset_samples / sample_rate

    # Normalize correlation strength
    correlation_strength = peak_value / (np.sqrt(np.sum(audio1**2) * np.sum(audio2**2)))

    print(f"\n  ✓ Peak correlation at offset: {offset_seconds:.3f}s")
    print(f"  ✓ Correlation strength: {correlation_strength:.4f}")

    return offset_seconds, float(correlation_strength)


def sync_videos_by_audio(
    video1_path: str,
    video2_path: str,
    sample_rate: int = 8000,
    max_offset_seconds: float = 60.0,
    extract_audio: bool = True,
    audio1_path: str = None,
    audio2_path: str = None,
    save_alignment: str = None
) -> Optional[Dict]:
    """
    Synchronize two videos using their audio tracks.

    Args:
        video1_path: Path to first video
        video2_path: Path to second video
        sample_rate: Audio sample rate for analysis (8kHz recommended)
        max_offset_seconds: Maximum time offset to search
        extract_audio: Extract audio from videos (set False if using cached audio)
        audio1_path: Cached audio WAV path for video 1
        audio2_path: Cached audio WAV path for video 2
        save_alignment: Save alignment result to JSON file

    Returns:
        Dictionary with alignment info:
        {
            "offset_seconds": float,
            "correlation_strength": float,
            "video1": {"start_time": float, "end_time": float, "start_frame": int, "end_frame": int},
            "video2": {"start_time": float, "end_time": float, "start_frame": int, "end_frame": int}
        }
    """
    print("=" * 80)
    print("AUDIO-BASED VIDEO SYNCHRONIZATION".center(80))
    print("=" * 80)

    # Get video info
    def get_video_info(video_path):
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-show_format',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        # Find video stream
        video_stream = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
        fps = eval(video_stream['r_frame_rate'])  # e.g., "60/1" -> 60.0
        duration = float(data['format']['duration'])
        total_frames = int(duration * fps)

        return {
            'fps': fps,
            'duration': duration,
            'total_frames': total_frames,
            'path': video_path,
            'name': Path(video_path).name
        }

    video1_info = get_video_info(video1_path)
    video2_info = get_video_info(video2_path)

    print(f"\nVideo 1: {video1_info['name']}")
    print(f"  Duration: {video1_info['duration']:.2f}s, FPS: {video1_info['fps']:.2f}")
    print(f"\nVideo 2: {video2_info['name']}")
    print(f"  Duration: {video2_info['duration']:.2f}s, FPS: {video2_info['fps']:.2f}")
    print()

    # Extract or load audio
    temp_files = []

    if extract_audio:
        print("Extracting audio tracks...")
        audio1_wav = extract_audio_to_wav(video1_path, audio1_path, sample_rate=sample_rate)
        audio2_wav = extract_audio_to_wav(video2_path, audio2_path, sample_rate=sample_rate)

        if audio1_path is None:
            temp_files.append(audio1_wav)
        if audio2_path is None:
            temp_files.append(audio2_wav)
    else:
        if not audio1_path or not audio2_path:
            raise ValueError("Must provide audio paths if extract_audio=False")
        audio1_wav = audio1_path
        audio2_wav = audio2_path

    # Load audio data
    print("\nLoading audio data...")
    audio1_data, sr1 = load_audio_data(audio1_wav)
    audio2_data, sr2 = load_audio_data(audio2_wav)

    if sr1 != sr2:
        raise ValueError(f"Sample rate mismatch: {sr1} vs {sr2}")

    # Find offset
    offset_seconds, correlation = find_audio_offset_correlation(
        audio1_data,
        audio2_data,
        sr1,
        max_offset_seconds=max_offset_seconds
    )

    # Determine aligned region
    # If offset > 0: video2 starts later, so trim start of video2 and end of video1
    # If offset < 0: video1 starts later, so trim start of video1 and end of video2

    if offset_seconds >= 0:
        # Video2 is delayed
        video1_start = 0.0
        video2_start = offset_seconds

        # Find overlap end
        video1_end = video1_info['duration']
        video2_end = video2_start + (video1_end - video1_start)

        # Clamp to actual durations
        if video2_end > video2_info['duration']:
            video2_end = video2_info['duration']
            video1_end = video1_start + (video2_end - video2_start)

    else:
        # Video1 is delayed
        video1_start = -offset_seconds
        video2_start = 0.0

        # Find overlap end
        video2_end = video2_info['duration']
        video1_end = video1_start + (video2_end - video2_start)

        # Clamp to actual durations
        if video1_end > video1_info['duration']:
            video1_end = video1_info['duration']
            video2_end = video2_start + (video1_end - video1_start)

    # Convert to frames
    video1_start_frame = int(video1_start * video1_info['fps'])
    video1_end_frame = int(video1_end * video1_info['fps'])
    video2_start_frame = int(video2_start * video2_info['fps'])
    video2_end_frame = int(video2_end * video2_info['fps'])

    aligned_duration = min(video1_end - video1_start, video2_end - video2_start)

    # Build result
    alignment = {
        "method": "audio_cross_correlation",
        "offset_seconds": float(offset_seconds),
        "correlation_strength": float(correlation),
        "aligned_duration": float(aligned_duration),
        "video1": {
            "path": video1_path,
            "name": video1_info['name'],
            "fps": video1_info['fps'],
            "start_time": float(video1_start),
            "end_time": float(video1_end),
            "start_frame": video1_start_frame,
            "end_frame": video1_end_frame,
            "aligned_frames": video1_end_frame - video1_start_frame + 1
        },
        "video2": {
            "path": video2_path,
            "name": video2_info['name'],
            "fps": video2_info['fps'],
            "start_time": float(video2_start),
            "end_time": float(video2_end),
            "start_frame": video2_start_frame,
            "end_frame": video2_end_frame,
            "aligned_frames": video2_end_frame - video2_start_frame + 1
        },
        "parameters": {
            "sample_rate": sample_rate,
            "max_offset_seconds": max_offset_seconds
        }
    }

    # Print results
    print("\n" + "=" * 80)
    print("ALIGNMENT RESULT".center(80))
    print("=" * 80)
    print(f"\nAudio Offset: {offset_seconds:.3f}s")
    print(f"Correlation Strength: {correlation:.4f}")
    print(f"Aligned Duration: {aligned_duration:.2f}s")
    print()
    print(f"Video 1: {video1_info['name']}")
    print(f"  Aligned range: {video1_start:.2f}s to {video1_end:.2f}s")
    print(f"  Frames: {video1_start_frame} to {video1_end_frame} ({video1_end_frame - video1_start_frame + 1} frames)")
    print()
    print(f"Video 2: {video2_info['name']}")
    print(f"  Aligned range: {video2_start:.2f}s to {video2_end:.2f}s")
    print(f"  Frames: {video2_start_frame} to {video2_end_frame} ({video2_end_frame - video2_start_frame + 1} frames)")

    # Save alignment
    if save_alignment:
        with open(save_alignment, 'w') as f:
            json.dump(alignment, f, indent=2)
        print(f"\n✓ Alignment saved to: {save_alignment}")

    # Cleanup temp files
    for temp_file in temp_files:
        try:
            Path(temp_file).unlink()
        except:
            pass

    return alignment


def compare_alignments(
    audio_alignment: Dict,
    icat_alignment_json: str
) -> Dict:
    """
    Compare audio-based alignment with ICAT manual alignment.

    Args:
        audio_alignment: Result from sync_videos_by_audio()
        icat_alignment_json: Path to ICAT alignment JSON

    Returns:
        Dictionary with comparison metrics
    """
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.sync.icat_parser import parse_icat_alignment

    print("\n" + "=" * 80)
    print("ALIGNMENT COMPARISON: AUDIO vs ICAT".center(80))
    print("=" * 80)

    # Parse ICAT alignment
    icat = parse_icat_alignment(icat_alignment_json)

    # Assume first two videos in ICAT correspond to the two videos
    icat_v1 = icat.videos[0]
    icat_v2 = icat.videos[1]

    audio_v1 = audio_alignment['video1']
    audio_v2 = audio_alignment['video2']

    # Compare frame ranges
    v1_start_diff = audio_v1['start_frame'] - icat_v1.start_frame
    v1_end_diff = audio_v1['end_frame'] - icat_v1.end_frame
    v2_start_diff = audio_v2['start_frame'] - icat_v2.start_frame
    v2_end_diff = audio_v2['end_frame'] - icat_v2.end_frame

    # Compare durations
    audio_duration = audio_alignment['aligned_duration']
    icat_duration = icat.aligned_duration
    duration_diff = audio_duration - icat_duration

    comparison = {
        "video1": {
            "audio_frames": f"{audio_v1['start_frame']}-{audio_v1['end_frame']}",
            "icat_frames": f"{icat_v1.start_frame}-{icat_v1.end_frame}",
            "start_frame_diff": v1_start_diff,
            "end_frame_diff": v1_end_diff
        },
        "video2": {
            "audio_frames": f"{audio_v2['start_frame']}-{audio_v2['end_frame']}",
            "icat_frames": f"{icat_v2.start_frame}-{icat_v2.end_frame}",
            "start_frame_diff": v2_start_diff,
            "end_frame_diff": v2_end_diff
        },
        "duration": {
            "audio_seconds": audio_duration,
            "icat_seconds": icat_duration,
            "difference_seconds": duration_diff,
            "difference_frames": int(duration_diff * audio_v1['fps'])
        },
        "correlation_strength": audio_alignment['correlation_strength']
    }

    print("\nVideo 1:")
    print(f"  Audio: frames {audio_v1['start_frame']:5d} to {audio_v1['end_frame']:5d}")
    print(f"  ICAT:  frames {icat_v1.start_frame:5d} to {icat_v1.end_frame:5d}")
    print(f"  Diff:  start {v1_start_diff:+4d}, end {v1_end_diff:+4d} frames")

    print("\nVideo 2:")
    print(f"  Audio: frames {audio_v2['start_frame']:5d} to {audio_v2['end_frame']:5d}")
    print(f"  ICAT:  frames {icat_v2.start_frame:5d} to {icat_v2.end_frame:5d}")
    print(f"  Diff:  start {v2_start_diff:+4d}, end {v2_end_diff:+4d} frames")

    print("\nDuration:")
    print(f"  Audio: {audio_duration:.3f}s")
    print(f"  ICAT:  {icat_duration:.3f}s")
    print(f"  Diff:  {duration_diff:+.3f}s ({int(duration_diff * audio_v1['fps']):+d} frames)")

    print(f"\nCorrelation Strength: {audio_alignment['correlation_strength']:.4f}")

    return comparison


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Audio-based video synchronization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync two videos by audio
  python audio_sync.py \\
    --video1 recordings/cyberpunk/1080p_dlaa_run1.mp4 \\
    --video2 recordings/cyberpunk/1080p_dlaa_run2.mp4 \\
    --output audio_alignment.json

  # Compare with ICAT manual alignment
  python audio_sync.py \\
    --video1 recordings/cyberpunk/1080p_dlaa_run1.mp4 \\
    --video2 recordings/cyberpunk/1080p_dlaa_run2.mp4 \\
    --output audio_alignment.json \\
    --compare-icat recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json

  # Use cached audio (faster for repeated runs)
  python audio_sync.py \\
    --video1 recordings/cyberpunk/1080p_dlaa_run1.mp4 \\
    --video2 recordings/cyberpunk/1080p_dlaa_run2.mp4 \\
    --audio1 /tmp/audio1.wav \\
    --audio2 /tmp/audio2.wav \\
    --no-extract
        """
    )

    parser.add_argument('--video1', required=True, help='First video file')
    parser.add_argument('--video2', required=True, help='Second video file')
    parser.add_argument('--output', help='Save alignment to JSON file')
    parser.add_argument('--sample-rate', type=int, default=8000,
                       help='Audio sample rate for analysis (default: 8000Hz)')
    parser.add_argument('--max-offset', type=float, default=60.0,
                       help='Maximum time offset to search in seconds (default: 60)')
    parser.add_argument('--no-extract', action='store_true',
                       help='Use pre-extracted audio (requires --audio1 and --audio2)')
    parser.add_argument('--audio1', help='Pre-extracted audio WAV for video1')
    parser.add_argument('--audio2', help='Pre-extracted audio WAV for video2')
    parser.add_argument('--compare-icat', help='Compare with ICAT manual alignment JSON')

    args = parser.parse_args()

    # Sync videos by audio
    alignment = sync_videos_by_audio(
        video1_path=args.video1,
        video2_path=args.video2,
        sample_rate=args.sample_rate,
        max_offset_seconds=args.max_offset,
        extract_audio=not args.no_extract,
        audio1_path=args.audio1,
        audio2_path=args.audio2,
        save_alignment=args.output
    )

    # Compare with ICAT if requested
    if args.compare_icat and alignment:
        comparison = compare_alignments(alignment, args.compare_icat)

        if args.output:
            # Append comparison to alignment file
            with open(args.output, 'r') as f:
                data = json.load(f)
            data['icat_comparison'] = comparison

            with open(args.output, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"\n✓ Comparison added to: {args.output}")

    return 0 if alignment else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
