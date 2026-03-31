#!/usr/bin/env python3
"""
Manual Video Synchronization and Trimming Tool

Interactive side-by-side video player to:
1. Find synchronization points between videos
2. Set trim points to remove menus/non-gameplay sections

Controls:
  SPACE       - Play/Pause
  LEFT/RIGHT  - Step 1 frame (when paused)
  UP/DOWN     - Jump 30 frames (when paused)
  HOME/END    - Jump to start/end of video
  [/]         - Jump backward/forward 5 seconds
  T           - Toggle timelapse preview mode
  1/2         - Adjust video1 offset (-1/+1 frame)
  3/4         - Adjust video2 offset (-1/+1 frame)
  Q/R         - Adjust video1 offset (-10/+10 frames)
  W/E         - Adjust video2 offset (-10/+10 frames)
  I/O         - Set IN/OUT trim points for current video
  V           - Switch active video (for trim points)
  C           - Clear trim points
  X           - Execute trim (create trimmed videos)
  S           - Save sync offsets to JSON
  ESC         - Quit
"""

import cv2
import argparse
import json
import sys
import subprocess
from pathlib import Path
import numpy as np
from skimage.metrics import structural_similarity as ssim

class ManualVideoSync:
    def __init__(self, video1_path, video2_path, output_path=None):
        self.video1_path = video1_path
        self.video2_path = video2_path
        self.output_path = output_path

        # Open videos
        self.cap1 = cv2.VideoCapture(str(video1_path))
        self.cap2 = cv2.VideoCapture(str(video2_path))

        if not self.cap1.isOpened() or not self.cap2.isOpened():
            raise RuntimeError("Could not open videos")

        # Get video properties
        self.fps1 = self.cap1.get(cv2.CAP_PROP_FPS)
        self.fps2 = self.cap2.get(cv2.CAP_PROP_FPS)
        self.total_frames1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_COUNT))
        self.total_frames2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_COUNT))
        self.width1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height1 = int(self.cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height2 = int(self.cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Sync state
        self.offset1 = 0  # Frame offset for video1
        self.offset2 = 0  # Frame offset for video2
        self.current_frame = 0  # Current playback position
        self.playing = False
        self.timelapse_mode = False  # Timelapse preview mode
        self.timelapse_frame_skip = 30  # Show every 30th frame in timelapse

        # Trim points
        self.in_point1 = None   # Video 1 IN point (absolute frame)
        self.out_point1 = None  # Video 1 OUT point (absolute frame)
        self.in_point2 = None   # Video 2 IN point (absolute frame)
        self.out_point2 = None  # Video 2 OUT point (absolute frame)
        self.active_video = 1   # Which video to set trim points for (1 or 2)

        print(f"\nVideo 1: {video1_path.name}")
        print(f"  {self.width1}x{self.height1} @ {self.fps1:.2f} FPS, {self.total_frames1} frames")
        print(f"\nVideo 2: {video2_path.name}")
        print(f"  {self.width2}x{self.height2} @ {self.fps2:.2f} FPS, {self.total_frames2} frames")
        print(f"\nActive video for trim points: Video {self.active_video} (press V to switch)")
        print()

    def read_frame(self, cap, offset, frame_num):
        """Read a specific frame from video with offset"""
        target_frame = offset + frame_num
        if target_frame < 0 or target_frame >= cap.get(cv2.CAP_PROP_FRAME_COUNT):
            # Return black frame if out of bounds
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            return np.zeros((height, width, 3), dtype=np.uint8)

        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        if not ret:
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            return np.zeros((height, width, 3), dtype=np.uint8)
        return frame

    def compute_frame_ssim(self, frame1, frame2):
        """Compute SSIM between two frames"""
        # Convert to grayscale
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Resize to same size if needed
        if gray1.shape != gray2.shape:
            h = min(gray1.shape[0], gray2.shape[0])
            w = min(gray1.shape[1], gray2.shape[1])
            gray1 = cv2.resize(gray1, (w, h))
            gray2 = cv2.resize(gray2, (w, h))

        # Compute SSIM
        score, _ = ssim(gray1, gray2, full=True)
        return score * 100  # Convert to percentage

    def format_time(self, frame_num, fps):
        """Convert frame number to timestamp"""
        seconds = frame_num / fps if fps > 0 else 0
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}:{secs:06.3f}"

    def create_timelapse_strip(self, num_frames=10):
        """Create a timelapse strip showing frames across the video timeline"""
        max_playback_frame = min(self.total_frames1 - self.offset1,
                                  self.total_frames2 - self.offset2) - 1

        # Calculate frame indices to sample
        step = max(1, max_playback_frame // (num_frames - 1))
        frame_indices = [i * step for i in range(num_frames)]
        if frame_indices[-1] != max_playback_frame:
            frame_indices[-1] = max_playback_frame

        # Collect thumbnail frames
        thumbnails1 = []
        thumbnails2 = []
        thumb_width = 160
        thumb_height = 90

        for idx in frame_indices:
            f1 = self.read_frame(self.cap1, self.offset1, idx)
            f2 = self.read_frame(self.cap2, self.offset2, idx)

            # Resize to thumbnail
            t1 = cv2.resize(f1, (thumb_width, thumb_height))
            t2 = cv2.resize(f2, (thumb_width, thumb_height))

            # Highlight current frame with green
            if abs(idx - self.current_frame) < step // 2:
                cv2.rectangle(t1, (0, 0), (thumb_width-1, thumb_height-1), (0, 255, 0), 3)
                cv2.rectangle(t2, (0, 0), (thumb_width-1, thumb_height-1), (0, 255, 0), 3)

            # Get absolute frame numbers
            abs_frame1 = self.offset1 + idx
            abs_frame2 = self.offset2 + idx

            # Highlight trim points
            # Video 1 IN/OUT points (cyan/orange)
            if self.in_point1 is not None and abs(abs_frame1 - self.in_point1) < step // 2:
                cv2.rectangle(t1, (2, 2), (thumb_width-3, thumb_height-3), (255, 255, 0), 2)  # Cyan
            if self.out_point1 is not None and abs(abs_frame1 - self.out_point1) < step // 2:
                cv2.rectangle(t1, (2, 2), (thumb_width-3, thumb_height-3), (0, 165, 255), 2)  # Orange

            # Video 2 IN/OUT points
            if self.in_point2 is not None and abs(abs_frame2 - self.in_point2) < step // 2:
                cv2.rectangle(t2, (2, 2), (thumb_width-3, thumb_height-3), (255, 255, 0), 2)  # Cyan
            if self.out_point2 is not None and abs(abs_frame2 - self.out_point2) < step // 2:
                cv2.rectangle(t2, (2, 2), (thumb_width-3, thumb_height-3), (0, 165, 255), 2)  # Orange

            # Add frame number
            cv2.putText(t1, f"{idx}", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(t2, f"{idx}", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            thumbnails1.append(t1)
            thumbnails2.append(t2)

        # Stack horizontally
        strip1 = np.hstack(thumbnails1)
        strip2 = np.hstack(thumbnails2)

        # Add separator
        separator = np.ones((10, strip1.shape[1], 3), dtype=np.uint8) * 128

        # Stack vertically with labels
        label_height = 30
        label1 = np.zeros((label_height, strip1.shape[1], 3), dtype=np.uint8)
        label2 = np.zeros((label_height, strip2.shape[1], 3), dtype=np.uint8)

        # Show which video is active for trim points
        v1_indicator = " [ACTIVE]" if self.active_video == 1 else ""
        v2_indicator = " [ACTIVE]" if self.active_video == 2 else ""

        cv2.putText(label1, f"Video 1 Timeline{v1_indicator}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(label2, f"Video 2 Timeline{v2_indicator}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        timelapse_strip = np.vstack([label1, strip1, separator, label2, strip2])

        return timelapse_strip

    def create_display(self, frame1, frame2):
        """Create side-by-side display with both frames and SSIM"""
        # Compute SSIM between current frames
        ssim_score = self.compute_frame_ssim(frame1, frame2)

        # Resize to fit side by side (max 1920px wide)
        target_height = 540
        scale1 = target_height / frame1.shape[0]
        scale2 = target_height / frame2.shape[0]

        resized1 = cv2.resize(frame1, None, fx=scale1, fy=scale1)
        resized2 = cv2.resize(frame2, None, fx=scale2, fy=scale2)

        # Make same height
        h = min(resized1.shape[0], resized2.shape[0])
        resized1 = cv2.resize(resized1, (int(resized1.shape[1] * h / resized1.shape[0]), h))
        resized2 = cv2.resize(resized2, (int(resized2.shape[1] * h / resized2.shape[0]), h))

        # Add separator
        separator = np.ones((h, 4, 3), dtype=np.uint8) * 255

        # Combine side by side
        combined = np.hstack([resized1, separator, resized2])

        # Add info overlay (taller to fit SSIM + trim info + commands)
        info_bg = np.zeros((260, combined.shape[1], 3), dtype=np.uint8)

        # Video 1 info (left)
        frame1_num = self.offset1 + self.current_frame
        time1 = frame1_num / self.fps1 if self.fps1 > 0 else 0
        v1_active = " [TRIM ACTIVE]" if self.active_video == 1 else ""
        cv2.putText(info_bg, f"Video 1: Frame {frame1_num} | {time1:.2f}s{v1_active}",
                   (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(info_bg, f"Offset: {self.offset1} frames",
                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Trim points for video 1
        if self.in_point1 is not None or self.out_point1 is not None:
            in_str = f"IN:{self.in_point1}" if self.in_point1 is not None else "IN:--"
            out_str = f"OUT:{self.out_point1}" if self.out_point1 is not None else "OUT:--"
            cv2.putText(info_bg, f"Trim: {in_str} {out_str}",
                       (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        # Video 2 info (right)
        frame2_num = self.offset2 + self.current_frame
        time2 = frame2_num / self.fps2 if self.fps2 > 0 else 0
        v2_active = " [TRIM ACTIVE]" if self.active_video == 2 else ""
        x_offset = combined.shape[1] // 2 + 10
        cv2.putText(info_bg, f"Video 2: Frame {frame2_num} | {time2:.2f}s{v2_active}",
                   (x_offset, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(info_bg, f"Offset: {self.offset2} frames",
                   (x_offset, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Trim points for video 2
        if self.in_point2 is not None or self.out_point2 is not None:
            in_str = f"IN:{self.in_point2}" if self.in_point2 is not None else "IN:--"
            out_str = f"OUT:{self.out_point2}" if self.out_point2 is not None else "OUT:--"
            cv2.putText(info_bg, f"Trim: {in_str} {out_str}",
                       (x_offset, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        # Status and SSIM
        mode_indicator = " [TIMELAPSE]" if self.timelapse_mode else ""
        status = f"{'PLAYING' if self.playing else 'PAUSED'}{mode_indicator}"

        # Color code SSIM (green if good, yellow if medium, red if bad)
        if ssim_score >= 95:
            ssim_color = (0, 255, 0)  # Green
        elif ssim_score >= 80:
            ssim_color = (0, 255, 255)  # Yellow
        else:
            ssim_color = (0, 0, 255)  # Red

        cv2.putText(info_bg, f"Status: {status} | Playback Frame: {self.current_frame}",
                   (10, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(info_bg, f"SSIM: {ssim_score:.2f}%",
                   (10, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.7, ssim_color, 2)

        # Controls (detailed)
        y = 170
        cv2.putText(info_bg, "Controls:", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        y += 20
        cv2.putText(info_bg, "Nav: SPACE=Play | LEFT/RIGHT=±1 | UP/DOWN=±30 | HOME/END=Start/End | [/]=±5sec | T=Timelapse",
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)
        y += 18
        cv2.putText(info_bg, "Sync: 1/2=V1±1 | 3/4=V2±1 | Q/R=V1±10 | W/E=V2±10 | S=Save",
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)
        y += 18
        cv2.putText(info_bg, "Trim: V=Switch video | I=IN | O=OUT | C=Clear | X=Execute trim | ESC=Quit",
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)
        y += 20
        cv2.putText(info_bg, "Legend: Green=Current | Cyan=IN point | Orange=OUT point",
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (150, 150, 150), 1)

        # Combine with info
        result = np.vstack([combined, info_bg])

        return result

    def save_sync_info(self):
        """Save synchronization offsets to JSON"""
        if not self.output_path:
            print("\nNo output path specified, cannot save")
            return

        sync_info = {
            "video1": str(self.video1_path),
            "video2": str(self.video2_path),
            "video1_offset": self.offset1,
            "video2_offset": self.offset2,
            "video1_trim": {
                "in_point": self.in_point1,
                "out_point": self.out_point1
            } if self.in_point1 is not None or self.out_point1 is not None else None,
            "video2_trim": {
                "in_point": self.in_point2,
                "out_point": self.out_point2
            } if self.in_point2 is not None or self.out_point2 is not None else None,
            "notes": "Frame offsets to align videos. Trim points are absolute frame numbers."
        }

        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, 'w') as f:
            json.dump(sync_info, f, indent=2)

        print(f"\n✓ Sync info saved to: {self.output_path}")
        print(f"  Video 1 offset: {self.offset1} frames ({self.offset1/self.fps1:.2f}s)")
        print(f"  Video 2 offset: {self.offset2} frames ({self.offset2/self.fps2:.2f}s)")
        if self.in_point1 is not None or self.out_point1 is not None:
            print(f"  Video 1 trim: IN={self.in_point1} OUT={self.out_point1}")
        if self.in_point2 is not None or self.out_point2 is not None:
            print(f"  Video 2 trim: IN={self.in_point2} OUT={self.out_point2}")

    def execute_trim(self):
        """Execute FFmpeg trim for videos with trim points set"""
        trim_count = 0

        # Trim video 1 if points are set
        if self.in_point1 is not None and self.out_point1 is not None:
            if self.in_point1 >= self.out_point1:
                print("\n✗ Video 1: IN point must be before OUT point")
            else:
                output1 = self.video1_path.parent / f"{self.video1_path.stem}_trimmed{self.video1_path.suffix}"
                success = self._trim_video(self.video1_path, output1, self.in_point1, self.out_point1, self.fps1, "Video 1")
                if success:
                    trim_count += 1

        # Trim video 2 if points are set
        if self.in_point2 is not None and self.out_point2 is not None:
            if self.in_point2 >= self.out_point2:
                print("\n✗ Video 2: IN point must be before OUT point")
            else:
                output2 = self.video2_path.parent / f"{self.video2_path.stem}_trimmed{self.video2_path.suffix}"
                success = self._trim_video(self.video2_path, output2, self.in_point2, self.out_point2, self.fps2, "Video 2")
                if success:
                    trim_count += 1

        if trim_count == 0:
            print("\n✗ No videos trimmed. Set IN and OUT points first (press I and O).")
        else:
            print(f"\n✓ Trimmed {trim_count} video(s) successfully!")

    def _trim_video(self, input_path, output_path, in_point, out_point, fps, video_name):
        """Execute FFmpeg trim command for a single video"""
        print(f"\n{'='*60}")
        print(f"TRIMMING {video_name}".center(60))
        print(f"{'='*60}")
        print(f"Input:  {input_path.name}")
        print(f"Output: {output_path.name}")
        print(f"IN:     Frame {in_point} ({self.format_time(in_point, fps)})")
        print(f"OUT:    Frame {out_point} ({self.format_time(out_point, fps)})")
        print(f"Frames: {out_point - in_point + 1}")

        # Build FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-vf', f"select='between(n\\,{in_point}\\,{out_point})',setpts=PTS-STARTPTS",
            '-af', 'aselect=concatdemo',
            '-vsync', '0',
            '-y',
            str(output_path)
        ]

        print("\nRunning FFmpeg...")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ {video_name} trimmed successfully: {output_path.name}")
                return True
            else:
                print(f"✗ FFmpeg failed for {video_name}:")
                print(result.stderr[:500])  # Show first 500 chars of error
                return False
        except Exception as e:
            print(f"✗ Error running FFmpeg for {video_name}: {e}")
            return False

    def run(self):
        """Run interactive sync tool"""
        print("=" * 80)
        print("MANUAL VIDEO SYNCHRONIZATION & TRIMMING".center(80))
        print("=" * 80)
        print("\nSync: Adjust offsets until both videos show the same frame.")
        print("Trim: Set IN/OUT points to remove menus (press V to switch video, I/O to mark)")
        print("Use T for timelapse preview, HOME/END to jump, [/] to skip 5 seconds.")
        print("Press S to save sync offsets, X to execute trim.")
        print("=" * 80 + "\n")

        while True:
            # Check if we should show timelapse mode
            if self.timelapse_mode:
                # Show timelapse strip
                timelapse = self.create_timelapse_strip(num_frames=10)
                cv2.imshow('Manual Video Sync - Timelapse', timelapse)
                cv2.imshow('Manual Video Sync', np.zeros((100, 800, 3), dtype=np.uint8))  # Placeholder

                # In timelapse mode, wait for key
                key = cv2.waitKey(0) & 0xFF
            else:
                # Normal mode: read and display current frames
                frame1 = self.read_frame(self.cap1, self.offset1, self.current_frame)
                frame2 = self.read_frame(self.cap2, self.offset2, self.current_frame)

                # Create display
                display = self.create_display(frame1, frame2)

                # Show
                cv2.imshow('Manual Video Sync', display)
                cv2.destroyWindow('Manual Video Sync - Timelapse')  # Close timelapse if open

                # Handle input
                key = cv2.waitKey(1 if self.playing else 0) & 0xFF

            # Process key input
            if key == 27:  # ESC only (not Q, which is for offset adjustment)
                break
            elif key == ord(' '):  # SPACE - play/pause
                self.playing = not self.playing
                print(f"{'Playing' if self.playing else 'Paused'}")
            elif key == 83:  # RIGHT arrow
                self.current_frame = min(self.current_frame + 1,
                                        min(self.total_frames1 - self.offset1,
                                            self.total_frames2 - self.offset2) - 1)
            elif key == 81:  # LEFT arrow
                self.current_frame = max(0, self.current_frame - 1)
            elif key == 82:  # UP arrow
                self.current_frame = min(self.current_frame + 30,
                                        min(self.total_frames1 - self.offset1,
                                            self.total_frames2 - self.offset2) - 1)
            elif key == 84:  # DOWN arrow
                self.current_frame = max(0, self.current_frame - 30)
            elif key == ord('1'):  # Decrease video1 offset
                self.offset1 = max(0, self.offset1 - 1)
                print(f"Video1 offset: {self.offset1}")
            elif key == ord('2'):  # Increase video1 offset
                self.offset1 = min(self.total_frames1 - 1, self.offset1 + 1)
                print(f"Video1 offset: {self.offset1}")
            elif key == ord('3'):  # Decrease video2 offset
                self.offset2 = max(0, self.offset2 - 1)
                print(f"Video2 offset: {self.offset2}")
            elif key == ord('4'):  # Increase video2 offset
                self.offset2 = min(self.total_frames2 - 1, self.offset2 + 1)
                print(f"Video2 offset: {self.offset2}")
            elif key == ord('q'):  # Large decrease video1
                self.offset1 = max(0, self.offset1 - 10)
                print(f"Video1 offset: {self.offset1}")
            elif key == ord('r'):  # Large increase video1
                self.offset1 = min(self.total_frames1 - 1, self.offset1 + 10)
                print(f"Video1 offset: {self.offset1}")
            elif key == ord('w'):  # Large decrease video2
                self.offset2 = max(0, self.offset2 - 10)
                print(f"Video2 offset: {self.offset2}")
            elif key == ord('e'):  # Large increase video2
                self.offset2 = min(self.total_frames2 - 1, self.offset2 + 10)
                print(f"Video2 offset: {self.offset2}")
            elif key == ord('s'):  # Save
                self.save_sync_info()
            elif key == ord('t'):  # Toggle timelapse mode
                self.timelapse_mode = not self.timelapse_mode
                if self.timelapse_mode:
                    print("Timelapse preview mode: ON")
                else:
                    print("Timelapse preview mode: OFF")
            elif key == ord('['):  # Jump backward 5 seconds
                jump_frames = int(5 * min(self.fps1, self.fps2))
                self.current_frame = max(0, self.current_frame - jump_frames)
                print(f"Jumped backward 5 seconds to frame {self.current_frame}")
            elif key == ord(']'):  # Jump forward 5 seconds
                jump_frames = int(5 * min(self.fps1, self.fps2))
                max_frame = min(self.total_frames1 - self.offset1,
                              self.total_frames2 - self.offset2) - 1
                self.current_frame = min(max_frame, self.current_frame + jump_frames)
                print(f"Jumped forward 5 seconds to frame {self.current_frame}")
            elif key == 2:  # HOME key
                self.current_frame = 0
                print("Jumped to start")
            elif key == 3:  # END key
                max_frame = min(self.total_frames1 - self.offset1,
                              self.total_frames2 - self.offset2) - 1
                self.current_frame = max_frame
                print(f"Jumped to end (frame {self.current_frame})")
            elif key == ord('v'):  # Switch active video for trim points
                self.active_video = 2 if self.active_video == 1 else 1
                print(f"Active video for trim points: Video {self.active_video}")
            elif key == ord('i'):  # Set IN point for active video
                if self.active_video == 1:
                    self.in_point1 = self.offset1 + self.current_frame
                    print(f"✓ Video 1 IN point: Frame {self.in_point1} ({self.format_time(self.in_point1, self.fps1)})")
                else:
                    self.in_point2 = self.offset2 + self.current_frame
                    print(f"✓ Video 2 IN point: Frame {self.in_point2} ({self.format_time(self.in_point2, self.fps2)})")
            elif key == ord('o'):  # Set OUT point for active video
                if self.active_video == 1:
                    self.out_point1 = self.offset1 + self.current_frame
                    print(f"✓ Video 1 OUT point: Frame {self.out_point1} ({self.format_time(self.out_point1, self.fps1)})")
                else:
                    self.out_point2 = self.offset2 + self.current_frame
                    print(f"✓ Video 2 OUT point: Frame {self.out_point2} ({self.format_time(self.out_point2, self.fps2)})")
            elif key == ord('c'):  # Clear trim points
                self.in_point1 = None
                self.out_point1 = None
                self.in_point2 = None
                self.out_point2 = None
                print("✓ All trim points cleared")
            elif key == ord('x'):  # Execute trim
                self.execute_trim()

            # Auto-advance when playing
            if self.playing:
                self.current_frame += 1
                max_frame = min(self.total_frames1 - self.offset1,
                              self.total_frames2 - self.offset2) - 1
                if self.current_frame >= max_frame:
                    self.current_frame = 0  # Loop

        self.cap1.release()
        self.cap2.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description='Manually synchronize two videos side-by-side',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--video1', type=Path, required=True)
    parser.add_argument('--video2', type=Path, required=True)
    parser.add_argument('--output', type=Path,
                       help='Output JSON file for sync offsets')

    args = parser.parse_args()

    if not args.video1.exists():
        print(f"Error: Video 1 not found: {args.video1}")
        return 1

    if not args.video2.exists():
        print(f"Error: Video 2 not found: {args.video2}")
        return 1

    try:
        sync_tool = ManualVideoSync(args.video1, args.video2, args.output)
        sync_tool.run()
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
