#!/usr/bin/env python3
"""
DLSS Analysis Pipeline - Complete Automation

Prerequisites:
1. Raw recordings in ../tcc/recordings/raw/ (5 files: *_raw.mp4)
2. FrameView CSVs in ../tcc/recordings/frameview/ (5 files: *_frameview.csv)
3. FFmpeg installed
4. Python packages: see requirements.txt

Usage:
    cd /Users/i549847/workspace/frame_inspect_tool
    python pipeline.py

    # Or with specific options:
    python pipeline.py --skip-processing  # Skip video CFR conversion
    python pipeline.py --baseline DLAA_4K --modes Quality Balanced
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Configuration
TCC_DIR = Path("../tcc")
RAW_DIR = TCC_DIR / "recordings" / "raw"
PROCESSED_DIR = TCC_DIR / "recordings" / "processed"
FRAMEVIEW_DIR = TCC_DIR / "recordings" / "frameview"
FPS_DATA_DIR = TCC_DIR / "fps_data"
QUALITY_DATA_DIR = TCC_DIR / "quality_data"
TEMPORAL_DATA_DIR = TCC_DIR / "temporal_data"
RESULTS_DIR = TCC_DIR / "results"
CHARTS_DIR = RESULTS_DIR / "charts"
TEMPORAL_CHARTS_DIR = CHARTS_DIR / "temporal"

# DLSS modes
ALL_MODES = ["DLAA_4K", "Quality", "Balanced", "Performance", "Ultra_Performance"]
DEFAULT_BASELINE = "DLAA_4K"


class PipelineError(Exception):
    """Custom exception for pipeline errors"""
    pass


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{'=' * 60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def print_step(step: int, total: int, text: str):
    """Print a step header"""
    print(f"\n{Fore.CYAN}[Step {step}/{total}] {text}{Style.RESET_ALL}")


def print_success(text: str):
    """Print success message"""
    print(f"{Fore.GREEN}  ✓ {text}{Style.RESET_ALL}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Fore.YELLOW}  ⚠ {text}{Style.RESET_ALL}")


def print_error(text: str):
    """Print error message"""
    print(f"{Fore.RED}  ✗ {text}{Style.RESET_ALL}")


def run_command(cmd: List[str], description: str, capture_output: bool = True) -> Optional[str]:
    """Run a shell command with error handling"""
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        else:
            subprocess.run(cmd, check=True)
            return None
    except subprocess.CalledProcessError as e:
        raise PipelineError(f"{description} failed: {e.stderr}")
    except FileNotFoundError:
        raise PipelineError(f"Command not found: {cmd[0]}. Please install it.")


def validate_prerequisites(modes: List[str]) -> Dict[str, bool]:
    """
    Validate that all required files exist

    Returns:
        Dict with validation status for each mode
    """
    print_step(0, 5, "Validating prerequisites...")

    # Create directories
    for directory in [PROCESSED_DIR, FPS_DATA_DIR, QUALITY_DATA_DIR, TEMPORAL_DATA_DIR, CHARTS_DIR, TEMPORAL_CHARTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    validation = {}
    missing_raw = []
    missing_csv = []

    # Check raw recordings
    for mode in modes:
        raw_file = RAW_DIR / f"{mode}_raw.mp4"
        csv_file = FRAMEVIEW_DIR / f"{mode}_frameview.csv"

        if not raw_file.exists():
            missing_raw.append(mode)
            validation[mode] = False
        else:
            validation[mode] = True

        if not csv_file.exists():
            missing_csv.append(mode)

    if missing_raw:
        print_error(f"Missing raw recordings: {', '.join(missing_raw)}")
        print_error(f"Expected location: {RAW_DIR}/")
        raise PipelineError("Cannot proceed without raw recordings")

    print_success("All raw recordings found")

    if missing_csv:
        print_warning(f"Missing FrameView CSVs: {', '.join(missing_csv)}")
        print_warning("Will skip FPS validation for these modes")

    return validation


def process_videos_to_cfr(modes: List[str]) -> Dict[str, int]:
    """
    Process all videos to CFR 60 FPS with exactly 60 seconds

    Returns:
        Dict mapping mode to frame count
    """
    print_step(1, 6, "Processing videos to CFR 60 FPS...")

    frame_counts = {}

    for mode in tqdm(modes, desc="Processing videos", unit="video"):
        input_file = RAW_DIR / f"{mode}_raw.mp4"
        output_file = PROCESSED_DIR / f"{mode}_60fps.mp4"

        # FFmpeg command
        cmd = [
            "ffmpeg",
            "-i", str(input_file),
            "-vf", "fps=60",
            "-t", "60",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "slow",
            "-pix_fmt", "yuv420p",
            "-an",
            str(output_file),
            "-y",
            "-loglevel", "error"
        ]

        run_command(cmd, f"Processing {mode}")

        # Verify frame count
        probe_cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-count_packets",
            "-show_entries", "stream=nb_read_packets",
            "-of", "csv=p=0",
            str(output_file)
        ]

        frame_count_str = run_command(probe_cmd, f"Verifying {mode}")
        frame_count = int(frame_count_str.strip())
        frame_counts[mode] = frame_count

        if frame_count == 3600:
            tqdm.write(f"{Fore.GREEN}    ✓ {mode}: {frame_count} frames{Style.RESET_ALL}")
        else:
            tqdm.write(f"{Fore.RED}    ✗ {mode}: {frame_count} frames (expected 3600){Style.RESET_ALL}")

    print_success("Video processing complete")
    return frame_counts


def extract_fps_data(modes: List[str]) -> Dict[str, Dict]:
    """
    Extract FPS data using fps_extractor.py

    Returns:
        Dict mapping mode to FPS data
    """
    print_step(2, 6, "Extracting FPS data...")

    fps_data = {}

    for mode in tqdm(modes, desc="Extracting FPS", unit="mode"):
        csv_file = FRAMEVIEW_DIR / f"{mode}_frameview.csv"
        video_file = PROCESSED_DIR / f"{mode}_60fps.mp4"
        output_file = FPS_DATA_DIR / f"{mode}_fps.json"

        if not csv_file.exists():
            tqdm.write(f"{Fore.YELLOW}    ⚠ Skipping {mode}: No FrameView CSV{Style.RESET_ALL}")
            continue

        # Run fps_extractor
        cmd = [
            sys.executable,
            "src/fps_extractor.py",
            "--type", "validated",
            "--source", str(csv_file),
            "--video", str(video_file),
            "--sample-rate", "30",
            "--tolerance", "5.0",
            "--output", str(output_file)
        ]

        try:
            run_command(cmd, f"Extracting FPS for {mode}", capture_output=False)

            # Load extracted data
            with open(output_file, 'r') as f:
                fps_data[mode] = json.load(f)

            avg_fps = fps_data[mode]['avg_fps']
            tqdm.write(f"{Fore.GREEN}    ✓ {mode}: {avg_fps:.1f} FPS (avg){Style.RESET_ALL}")

        except PipelineError as e:
            tqdm.write(f"{Fore.YELLOW}    ⚠ {mode}: {e}{Style.RESET_ALL}")

    print_success("FPS extraction complete")
    return fps_data


def compare_quality(modes: List[str], baseline: str) -> Dict[str, Dict]:
    """
    Compare quality (SSIM/PSNR) of each mode against baseline

    Returns:
        Dict mapping mode to quality metrics
    """
    print_step(3, 6, "Comparing image quality (SSIM/PSNR)...")

    baseline_video = PROCESSED_DIR / f"{baseline}_60fps.mp4"
    quality_data = {}

    # Baseline compares perfectly with itself
    quality_data[baseline] = {
        'avg_ssim': 100.0,
        'avg_psnr': float('inf'),
        'temporal_stability': 100.0,
        'frames_compared': 3600
    }

    modes_to_compare = [m for m in modes if m != baseline]

    for mode in tqdm(modes_to_compare, desc="Comparing quality", unit="mode"):
        compare_video = PROCESSED_DIR / f"{mode}_60fps.mp4"
        output_file = QUALITY_DATA_DIR / f"{mode}_comparison.json"

        # Run video comparison
        cmd = [
            sys.executable,
            "src/app.py",
            "--ground-truth", str(baseline_video),
            "--compare", str(compare_video),
            "--output", str(output_file)
        ]

        try:
            run_command(cmd, f"Comparing {mode}", capture_output=False)

            # Load comparison results
            with open(output_file, 'r') as f:
                quality_data[mode] = json.load(f)

            ssim = quality_data[mode].get('avg_ssim', 0)
            psnr = quality_data[mode].get('avg_psnr', 0)
            tqdm.write(f"{Fore.GREEN}    ✓ {mode}: SSIM={ssim:.1f}%, PSNR={psnr:.1f} dB{Style.RESET_ALL}")

        except PipelineError as e:
            tqdm.write(f"{Fore.YELLOW}    ⚠ {mode}: {e}{Style.RESET_ALL}")

    print_success("Quality comparison complete")
    return quality_data


def analyze_temporal_correlation(modes: List[str], baseline: str) -> Dict[str, Dict]:
    """
    Analyze temporal correlation between FPS and quality for each mode

    Returns:
        Dict mapping mode to temporal analysis results
    """
    print_step(4, 6, "Analyzing temporal FPS vs Quality correlation...")

    baseline_video = PROCESSED_DIR / f"{baseline}_60fps.mp4"
    temporal_data = {}

    # Skip baseline (no correlation to analyze - perfect quality)
    modes_to_analyze = [m for m in modes if m != baseline]

    for mode in tqdm(modes_to_analyze, desc="Temporal analysis", unit="mode"):
        csv_file = FRAMEVIEW_DIR / f"{mode}_frameview.csv"
        test_video = PROCESSED_DIR / f"{mode}_60fps.mp4"
        output_json = TEMPORAL_DATA_DIR / f"{mode}_temporal.json"
        timeline_plot = TEMPORAL_CHARTS_DIR / f"{mode}_timeline.png"
        correlation_plot = TEMPORAL_CHARTS_DIR / f"{mode}_correlation.png"

        if not csv_file.exists():
            tqdm.write(f"{Fore.YELLOW}    ⚠ Skipping {mode}: No FrameView CSV{Style.RESET_ALL}")
            continue

        # Run temporal_analyzer
        cmd = [
            sys.executable,
            "temporal_analyzer.py",
            "--fps-csv", str(csv_file),
            "--video-test", str(test_video),
            "--video-ground-truth", str(baseline_video),
            "--mode-name", mode,
            "--output", str(output_json),
            "--plot-timeline", str(timeline_plot),
            "--plot-correlation", str(correlation_plot),
            "--fps", "60"
        ]

        try:
            run_command(cmd, f"Temporal analysis for {mode}", capture_output=False)

            # Load temporal analysis results
            with open(output_json, 'r') as f:
                temporal_data[mode] = json.load(f)

            # Extract key metrics
            corr = temporal_data[mode]['correlation_statistics']['pearson_fps_ssim']['correlation']
            p_value = temporal_data[mode]['correlation_statistics']['pearson_fps_ssim']['p_value']
            significant = "significant" if p_value < 0.05 else "not significant"

            tqdm.write(f"{Fore.GREEN}    ✓ {mode}: FPS-SSIM correlation={corr:.3f} ({significant}){Style.RESET_ALL}")

        except PipelineError as e:
            tqdm.write(f"{Fore.YELLOW}    ⚠ {mode}: {e}{Style.RESET_ALL}")

    print_success("Temporal correlation analysis complete")
    return temporal_data


def consolidate_data(fps_data: Dict[str, Dict], quality_data: Dict[str, Dict]) -> tuple:
    """
    Consolidate FPS and quality data into CSVs

    Returns:
        Tuple of (fps_csv_path, quality_csv_path)
    """
    print_step(5, 6, "Consolidating data...")

    # Create FPS CSV
    fps_csv = FPS_DATA_DIR / "benchmark_fps.csv"
    with open(fps_csv, 'w') as f:
        f.write("mode,avg_fps,1%_low,0.1%_low\n")
        for mode, data in fps_data.items():
            avg = data['avg_fps']
            low_1 = data['1%_low']
            low_01 = data['0.1%_low']
            f.write(f"{mode},{avg:.1f},{low_1:.1f},{low_01:.1f}\n")
            print(f"{Fore.GREEN}    ✓ {mode}: {avg:.1f} FPS (avg){Style.RESET_ALL}")

    # Create Quality CSV
    quality_csv = QUALITY_DATA_DIR / "benchmark_quality.csv"
    with open(quality_csv, 'w') as f:
        f.write("mode,ssim,psnr\n")
        for mode, data in quality_data.items():
            ssim = data.get('avg_ssim', 0)
            psnr = data.get('avg_psnr', 0)
            psnr_str = "inf" if psnr == float('inf') else f"{psnr:.1f}"
            f.write(f"{mode},{ssim:.1f},{psnr_str}\n")
            print(f"{Fore.GREEN}    ✓ {mode}: SSIM={ssim:.1f}%, PSNR={psnr_str} dB{Style.RESET_ALL}")

    print_success("Data consolidation complete")
    return fps_csv, quality_csv


def analyze_tradeoffs(fps_csv: Path, quality_csv: Path, baseline: str):
    """
    Run performance_quality_analyzer to analyze trade-offs
    """
    print_step(6, 6, "Analyzing FPS vs Quality trade-offs...")

    cmd = [
        sys.executable,
        "src/performance_quality_analyzer.py",
        "--fps", str(fps_csv),
        "--quality", str(quality_csv),
        "--baseline", baseline,
        "--output-csv", str(RESULTS_DIR / "benchmark_tradeoff.csv"),
        "--output-json", str(RESULTS_DIR / "benchmark_tradeoff.json"),
        "--plot-fps-vs-quality", str(CHARTS_DIR / "benchmark_fps_vs_quality.png"),
        "--plot-efficiency", str(CHARTS_DIR / "benchmark_efficiency.png")
    ]

    run_command(cmd, "Analyzing trade-offs", capture_output=False)
    print_success("Trade-off analysis complete")


def print_summary():
    """Print final summary"""
    print_header("Pipeline Complete!")

    print(f"{Fore.YELLOW}Results available at:{Style.RESET_ALL}")
    print(f"  📊 Trade-off table:  {RESULTS_DIR / 'benchmark_tradeoff.csv'}")
    print(f"  📈 FPS vs Quality:   {CHARTS_DIR / 'benchmark_fps_vs_quality.png'}")
    print(f"  📊 Efficiency chart: {CHARTS_DIR / 'benchmark_efficiency.png'}")
    print(f"  📋 Raw FPS data:     {FPS_DATA_DIR / 'benchmark_fps.csv'}")
    print(f"  📋 Raw quality data: {QUALITY_DATA_DIR / 'benchmark_quality.csv'}")
    print(f"  📈 Temporal charts:  {TEMPORAL_CHARTS_DIR}/")

    print(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
    print("  1. Review charts in results/charts/")
    print("  2. Review temporal correlation charts in results/charts/temporal/")
    print("  3. Import benchmark_tradeoff.csv into your TCC tables")
    print("  4. Include charts as figures in your Results chapter")

    print(f"\n{Fore.GREEN}Done! 🎉{Style.RESET_ALL}\n")


def main():
    parser = argparse.ArgumentParser(
        description="DLSS Analysis Pipeline - Complete Automation"
    )
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=ALL_MODES,
        default=ALL_MODES,
        help="DLSS modes to process (default: all)"
    )
    parser.add_argument(
        "--baseline",
        default=DEFAULT_BASELINE,
        help=f"Baseline mode for comparison (default: {DEFAULT_BASELINE})"
    )
    parser.add_argument(
        "--skip-processing",
        action="store_true",
        help="Skip video CFR processing (use existing processed videos)"
    )
    parser.add_argument(
        "--skip-fps",
        action="store_true",
        help="Skip FPS extraction (use existing FPS data)"
    )
    parser.add_argument(
        "--skip-quality",
        action="store_true",
        help="Skip quality comparison (use existing quality data)"
    )
    parser.add_argument(
        "--skip-temporal",
        action="store_true",
        help="Skip temporal correlation analysis"
    )

    args = parser.parse_args()

    try:
        print_header("DLSS Analysis Pipeline - Full Automation")

        # Step 0: Validation
        validate_prerequisites(args.modes)

        # Step 1: Process videos to CFR
        if args.skip_processing:
            print_step(1, 6, "Skipping video processing (--skip-processing)")
        else:
            process_videos_to_cfr(args.modes)

        # Step 2: Extract FPS data
        if args.skip_fps:
            print_step(2, 6, "Skipping FPS extraction (--skip-fps)")
            # Load existing data
            fps_data = {}
            for mode in args.modes:
                json_file = FPS_DATA_DIR / f"{mode}_fps.json"
                if json_file.exists():
                    with open(json_file, 'r') as f:
                        fps_data[mode] = json.load(f)
        else:
            fps_data = extract_fps_data(args.modes)

        # Step 3: Compare quality
        if args.skip_quality:
            print_step(3, 6, "Skipping quality comparison (--skip-quality)")
            # Load existing data
            quality_data = {args.baseline: {
                'avg_ssim': 100.0,
                'avg_psnr': float('inf'),
                'temporal_stability': 100.0,
                'frames_compared': 3600
            }}
            for mode in args.modes:
                if mode == args.baseline:
                    continue
                json_file = QUALITY_DATA_DIR / f"{mode}_comparison.json"
                if json_file.exists():
                    with open(json_file, 'r') as f:
                        quality_data[mode] = json.load(f)
        else:
            quality_data = compare_quality(args.modes, args.baseline)

        # Step 4: Temporal correlation analysis
        if args.skip_temporal:
            print_step(4, 6, "Skipping temporal analysis (--skip-temporal)")
        else:
            analyze_temporal_correlation(args.modes, args.baseline)

        # Step 5: Consolidate data
        fps_csv, quality_csv = consolidate_data(fps_data, quality_data)

        # Step 6: Analyze trade-offs
        analyze_tradeoffs(fps_csv, quality_csv, args.baseline)

        # Summary
        print_summary()

    except PipelineError as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print_error("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
