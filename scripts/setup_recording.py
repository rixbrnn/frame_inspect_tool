#!/usr/bin/env python3
"""
Create organized directory structure for a new game/resolution recording

Usage:
    python scripts/setup_recording.py --game cyberpunk2077 --resolution 1080p
    python scripts/setup_recording.py --game blackmyth --resolution 4k
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def create_recording_structure(game: str, resolution: str, base_dir: Path = None):
    """
    Create standardized directory structure for game recordings

    Args:
        game: Game name (lowercase, no spaces)
        resolution: Resolution (e.g., 1080p, 1440p, 4k)
        base_dir: Base recordings directory (default: ./recordings)
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent / "recordings"

    game_dir = base_dir / game
    res_dir = game_dir / resolution

    # Create directory structure
    directories = [
        res_dir / "validation",
        res_dir / "raw",
        res_dir / "processed",
        res_dir / "extracted",
        res_dir / "results",
    ]

    print(f"Creating recording structure for {game} @ {resolution}")
    print(f"Base directory: {base_dir}")
    print()

    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {dir_path.relative_to(base_dir)}")

    # Create metadata template
    metadata_file = res_dir / "metadata.json"
    if not metadata_file.exists():
        metadata = {
            "game": game,
            "resolution": resolution,
            "recording_date": datetime.now().strftime("%Y-%m-%d"),
            "system": {
                "gpu": "RTX 4090",
                "cpu": "AMD Ryzen 9 7950X",
                "ram": "32GB DDR5-6000",
                "driver": "566.03",
                "note": "UPDATE WITH YOUR SYSTEM SPECS"
            },
            "game_settings": {
                "preset": "Ultra",
                "ray_tracing": "Ultra",
                "dlss_frame_generation": False,
                "note": "UPDATE WITH YOUR GAME SETTINGS"
            },
            "benchmark": {
                "name": "Describe benchmark scene/location",
                "duration": 60,
                "validated": False,
                "ssim": None,
                "note": "Fill after validation"
            }
        }

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✓ Created: {metadata_file.relative_to(base_dir)}")
        print(f"  → Update system specs and game settings!")

    # Create FPS ROI template if game is new
    fps_roi_file = game_dir / "fps_roi.json"
    if not fps_roi_file.exists():
        roi_template = {
            "game": game,
            "roi": {
                "x": 50,
                "y": 50,
                "width": 120,
                "height": 40,
                "note": "RUN calibrate_fps_roi.py TO SET CORRECT VALUES"
            },
            "notes": "MSI Afterburner FPS counter location",
            "tested_resolutions": [resolution]
        }

        with open(fps_roi_file, 'w') as f:
            json.dump(roi_template, f, indent=2)

        print(f"\n✓ Created: {fps_roi_file.relative_to(base_dir)}")
        print(f"  → Run calibrate_fps_roi.py to set correct ROI!")
    else:
        # Update tested_resolutions
        with open(fps_roi_file, 'r') as f:
            roi_data = json.load(f)

        if resolution not in roi_data.get("tested_resolutions", []):
            roi_data.setdefault("tested_resolutions", []).append(resolution)
            with open(fps_roi_file, 'w') as f:
                json.dump(roi_data, f, indent=2)

            print(f"\n✓ Updated: {fps_roi_file.relative_to(base_dir)}")
            print(f"  → Added {resolution} to tested resolutions")

    # Create README in validation folder
    validation_readme = res_dir / "validation" / "README.md"
    if not validation_readme.exists():
        readme_content = f"""# Validation Recordings - {game} @ {resolution}

## Purpose
Record the same benchmark twice to verify it's deterministic (no random AI, physics, etc.)

## Steps

1. **Record first run:**
   - Start benchmark
   - Record 60+ seconds
   - Save as `run1.mp4`

2. **Record second run:**
   - **Immediately** restart and run the exact same benchmark
   - Record 60+ seconds
   - Save as `run2.mp4`

3. **Validate stability:**
   ```bash
   python scripts/validate_benchmark.py \\
       --video1 recordings/{game}/{resolution}/validation/run1.mp4 \\
       --video2 recordings/{game}/{resolution}/validation/run2.mp4 \\
       --game "{game.replace('_', ' ').title()}" \\
       --output recordings/{game}/{resolution}/validation/validation.json
   ```

4. **Check results:**
   - ✅ SSIM ≥ 99% → Benchmark is stable, proceed with data collection
   - ❌ SSIM < 99% → Benchmark has non-deterministic elements, find different scene

## Expected Files
- `run1.mp4` - First recording
- `run2.mp4` - Second recording
- `run1_60fps.mp4` - CFR version (auto-generated)
- `run2_60fps.mp4` - CFR version (auto-generated)
- `validation.json` - Validation results
"""
        validation_readme.write_text(readme_content)
        print(f"\n✓ Created: {validation_readme.relative_to(base_dir)}")

    print("\n" + "=" * 80)
    print("NEXT STEPS".center(80))
    print("=" * 80)
    print(f"\n1. Record validation videos:")
    print(f"   → Save to: recordings/{game}/{resolution}/validation/")
    print(f"   → Files: run1.mp4, run2.mp4")
    print(f"\n2. Update metadata:")
    print(f"   → Edit: recordings/{game}/{resolution}/metadata.json")
    print(f"   → Fill system specs and game settings")
    print(f"\n3. Calibrate FPS ROI (if first time for this game):")
    print(f"   python scripts/calibrate_fps_roi.py \\")
    print(f"       --video recordings/{game}/{resolution}/validation/run1.mp4 \\")
    print(f"       --output recordings/{game}/fps_roi.json")
    print(f"\n4. Validate benchmark:")
    print(f"   python scripts/validate_benchmark.py \\")
    print(f"       --video1 recordings/{game}/{resolution}/validation/run1.mp4 \\")
    print(f"       --video2 recordings/{game}/{resolution}/validation/run2.mp4 \\")
    print(f"       --game \"{game.replace('_', ' ').title()}\" \\")
    print(f"       --output recordings/{game}/{resolution}/validation/validation.json")
    print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Set up recording directory structure for a game',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First game recording
  python scripts/setup_recording.py --game cyberpunk2077 --resolution 1080p

  # Add another resolution to existing game
  python scripts/setup_recording.py --game cyberpunk2077 --resolution 4k

  # New game
  python scripts/setup_recording.py --game blackmyth --resolution 1440p

Game name guidelines:
  - Use lowercase
  - No spaces (use underscore if needed)
  - Examples: cyberpunk2077, blackmyth, eldenring, rdr2

Resolution options:
  - 1080p (1920x1080)
  - 1440p (2560x1440)
  - 4k (3840x2160)
        """
    )

    parser.add_argument('--game', required=True, help='Game name (lowercase, no spaces)')
    parser.add_argument('--resolution', required=True, help='Resolution (1080p, 1440p, 4k)')
    parser.add_argument('--base-dir', type=Path, help='Base recordings directory (default: ./recordings)')

    args = parser.parse_args()

    # Validate game name
    if ' ' in args.game:
        print(f"✗ Game name cannot contain spaces. Use underscore instead.")
        print(f"  Example: '{args.game}' → '{args.game.replace(' ', '_')}'")
        return 1

    if args.game != args.game.lower():
        print(f"✗ Game name must be lowercase.")
        print(f"  Example: '{args.game}' → '{args.game.lower()}'")
        return 1

    # Validate resolution
    valid_resolutions = ['1080p', '1440p', '4k', '1920x1080', '2560x1440', '3840x2160']
    if args.resolution.lower() not in valid_resolutions:
        print(f"✗ Invalid resolution: {args.resolution}")
        print(f"  Valid options: {', '.join(valid_resolutions)}")
        return 1

    create_recording_structure(args.game, args.resolution.lower(), args.base_dir)

    return 0


if __name__ == "__main__":
    exit(main())
