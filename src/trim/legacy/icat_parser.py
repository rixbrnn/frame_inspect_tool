#!/usr/bin/env python3
"""
ICAT Manual Alignment Parser

Extracts video alignment information from NVIDIA ICAT manual cut settings JSON files.

ICAT (Image Comparison and Analysis Tool) allows manual frame-by-frame video alignment.
This parser reads the alignment data saved by ICAT and converts it to our format.

ICAT JSON Structure:
- startTime: Aligned start time (seconds)
- endTime: Aligned end time (seconds)
- media[]: Array of video files with metadata
  - fps: Frame rate
  - duration: Total video duration
  - timestamps[]: Frame timestamps

Usage:
    from src.trim.legacy.icat_parser import parse_icat_alignment

    alignment = parse_icat_alignment('recordings/cyberpunk/icat_1080p_derived_modes_cut_settings.json')
    print(alignment)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class VideoAlignment:
    """Alignment information for a single video"""
    video_id: str
    video_name: Optional[str]
    fps: float
    duration: float
    width: int
    height: int
    start_time: float
    end_time: float
    start_frame: int
    end_frame: int
    aligned_duration: float
    aligned_frames: int


@dataclass
class ICATAlignment:
    """Complete ICAT alignment data"""
    set_id: str
    set_label: str
    start_time: float
    end_time: float
    aligned_duration: float
    videos: List[VideoAlignment]

    def get_video_by_name(self, name: str) -> Optional[VideoAlignment]:
        """Find video alignment by filename"""
        for video in self.videos:
            if video.video_name and name in video.video_name:
                return video
        return None


def parse_icat_alignment(json_path: str) -> ICATAlignment:
    """
    Parse ICAT manual alignment JSON file.

    Args:
        json_path: Path to ICAT JSON file (e.g., icat_1080p_derived_modes_cut_settings.json)

    Returns:
        ICATAlignment object with parsed alignment data

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        ValueError: If JSON structure is invalid
    """
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"ICAT JSON not found: {json_path}")

    # Load JSON
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Find active set
    active_set_id = data.get('activeSet')
    if not active_set_id:
        raise ValueError("No activeSet found in ICAT JSON")

    # Find the active set in sets array
    sets = data.get('sets', [])
    active_set = None
    for s in sets:
        if s.get('id') == active_set_id:
            active_set = s
            break

    if not active_set:
        raise ValueError(f"Active set '{active_set_id}' not found in sets array")

    # Extract alignment times
    start_time = active_set.get('startTime', 0.0)
    end_time = active_set.get('endTime', 0.0)
    aligned_duration = end_time - start_time

    # Parse media
    media_list = active_set.get('media', [])
    if not media_list:
        raise ValueError("No media found in active set")

    videos = []
    for media in media_list:
        if media.get('type') != 'video':
            continue

        fps = media.get('fps', 60.0)
        duration = media.get('duration', 0.0)
        width = media.get('width', 0)
        height = media.get('height', 0)
        video_id = media.get('id', '')

        # Try to get filename from ICAT (not always available)
        video_name = media.get('name') or media.get('filename')

        # Calculate frame numbers
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        aligned_frames = end_frame - start_frame + 1

        video_alignment = VideoAlignment(
            video_id=video_id,
            video_name=video_name,
            fps=fps,
            duration=duration,
            width=width,
            height=height,
            start_time=start_time,
            end_time=end_time,
            start_frame=start_frame,
            end_frame=end_frame,
            aligned_duration=aligned_duration,
            aligned_frames=aligned_frames
        )

        videos.append(video_alignment)

    return ICATAlignment(
        set_id=active_set_id,
        set_label=active_set.get('label', 'Unknown'),
        start_time=start_time,
        end_time=end_time,
        aligned_duration=aligned_duration,
        videos=videos
    )


def find_icat_file(recordings_dir: str, resolution: str, mode: str = 'derived') -> Optional[Path]:
    """
    Find ICAT JSON file for a specific resolution and mode.

    Args:
        recordings_dir: Path to recordings directory (e.g., recordings/cyberpunk)
        resolution: Resolution string (1080p, 1440p, 4k)
        mode: Mode type ('derived' for DLSS modes, 'dlaa' for DLAA validation)

    Returns:
        Path to ICAT JSON file if found, None otherwise
    """
    recordings_path = Path(recordings_dir)

    # Construct expected filename
    filename = f"icat_{resolution}_{mode}_modes_cut_settings.json"
    icat_path = recordings_path / filename

    if icat_path.exists():
        return icat_path

    return None


def extract_alignment_for_videos(
    json_path: str,
    video_names: List[str]
) -> Dict[str, VideoAlignment]:
    """
    Extract alignment data for specific videos.

    Args:
        json_path: Path to ICAT JSON
        video_names: List of video filenames to extract (e.g., ['1080p_dlaa', '1080p_dlss_quality'])

    Returns:
        Dict mapping video name to VideoAlignment
    """
    alignment = parse_icat_alignment(json_path)

    result = {}
    for name in video_names:
        video = alignment.get_video_by_name(name)
        if video:
            result[name] = video

    return result


def get_trim_commands(alignment: ICATAlignment, video_mapping: Dict[str, str]) -> List[str]:
    """
    Generate ffmpeg trim commands from ICAT alignment.

    Args:
        alignment: ICATAlignment object
        video_mapping: Dict mapping video IDs to actual filenames
                      (e.g., {"video_id": "recordings/cyberpunk/1080p_dlaa.mp4"})

    Returns:
        List of ffmpeg commands
    """
    commands = []

    for video in alignment.videos:
        # Get actual filename
        video_path = video_mapping.get(video.video_id)
        if not video_path:
            # Try using video_name if available
            if video.video_name:
                video_path = video.video_name
            else:
                continue

        video_path = Path(video_path)
        output_path = video_path.parent / f"{video_path.stem}_trimmed{video_path.suffix}"

        # Build ffmpeg command
        # Use frame selection for precise cuts
        cmd = (
            f'ffmpeg -i "{video_path}" '
            f'-vf "select=\'between(n\\,{video.start_frame}\\,{video.end_frame})\',setpts=PTS-STARTPTS" '
            f'-af "aselect=\'between(n\\,{video.start_frame}\\,{video.end_frame})\',asetpts=PTS-STARTPTS" '
            f'-vsync 0 '
            f'-y "{output_path}"'
        )

        commands.append(cmd)

    return commands


def main():
    """CLI for testing ICAT parser"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Parse NVIDIA ICAT manual alignment JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse and display alignment
  python icat_parser.py recordings/cyberpunk/icat_1080p_derived_modes_cut_settings.json

  # Generate ffmpeg trim commands
  python icat_parser.py recordings/cyberpunk/icat_1080p_dlaa_modes_cut_settings.json --generate-commands
        """
    )

    parser.add_argument('json_file', help='Path to ICAT JSON file')
    parser.add_argument('--generate-commands', action='store_true',
                       help='Generate ffmpeg trim commands')
    parser.add_argument('--video-dir', default='.',
                       help='Directory containing video files (default: same as JSON)')

    args = parser.parse_args()

    # Parse alignment
    try:
        alignment = parse_icat_alignment(args.json_file)
    except Exception as e:
        print(f"Error parsing ICAT JSON: {e}")
        return 1

    # Display results
    print("=" * 80)
    print("ICAT MANUAL ALIGNMENT".center(80))
    print("=" * 80)
    print(f"\nSet: {alignment.set_label} (ID: {alignment.set_id})")
    print(f"Aligned Time Range: {alignment.start_time:.3f}s to {alignment.end_time:.3f}s")
    print(f"Aligned Duration: {alignment.aligned_duration:.3f}s ({int(alignment.aligned_duration * 60)} frames @ 60fps)")
    print(f"\nVideos: {len(alignment.videos)}")
    print("-" * 80)

    for i, video in enumerate(alignment.videos, 1):
        print(f"\n#{i} Video ID: {video.video_id}")
        if video.video_name:
            print(f"   Name: {video.video_name}")
        print(f"   Resolution: {video.width}x{video.height} @ {video.fps} FPS")
        print(f"   Total Duration: {video.duration:.2f}s")
        print(f"   Aligned Range: frames {video.start_frame} to {video.end_frame}")
        print(f"   Aligned Frames: {video.aligned_frames} frames ({video.aligned_duration:.3f}s)")

    # Generate commands if requested
    if args.generate_commands:
        print("\n" + "=" * 80)
        print("FFMPEG TRIM COMMANDS".center(80))
        print("=" * 80)

        # Build video mapping (simplified - assumes video files are in same dir as JSON)
        json_path = Path(args.json_file)
        video_dir = Path(args.video_dir) if args.video_dir != '.' else json_path.parent

        video_mapping = {}
        for video in alignment.videos:
            if video.video_name:
                # Try to find the video file
                potential_paths = [
                    video_dir / video.video_name,
                    video_dir / f"{video.video_name}.mp4"
                ]
                for p in potential_paths:
                    if p.exists():
                        video_mapping[video.video_id] = str(p)
                        break

        commands = get_trim_commands(alignment, video_mapping)

        if commands:
            print()
            for cmd in commands:
                print(cmd)
                print()
        else:
            print("\n⚠ Could not generate commands: video files not found")
            print("   Specify --video-dir to point to the video files")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
