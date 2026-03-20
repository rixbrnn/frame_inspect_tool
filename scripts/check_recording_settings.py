#!/usr/bin/env python3
"""
Pre-Recording Checklist - Verify settings before capturing benchmark data

Usage:
    python scripts/check_recording_settings.py --game cyberpunk2077 --resolution 1080p
"""

import argparse
import json
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)


def print_header(text):
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80)


def print_check(passed, message):
    if passed:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} {message}")
    else:
        print(f"{Fore.RED}✗{Style.RESET_ALL} {message}")
    return passed


def check_metadata_file(game: str, resolution: str, base_dir: Path):
    """Check if metadata file exists and has required fields"""
    metadata_file = base_dir / game / resolution / "metadata.json"

    if not metadata_file.exists():
        print_check(False, f"Metadata file not found: {metadata_file}")
        print(f"\n{Fore.YELLOW}Run: python scripts/setup_recording.py --game {game} --resolution {resolution}{Style.RESET_ALL}\n")
        return False

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    all_ok = True

    # Check HDR setting
    hdr_disabled = metadata.get("display_settings", {}).get("hdr") == False
    all_ok &= print_check(hdr_disabled, "HDR is disabled (REQUIRED)")
    if not hdr_disabled:
        print(f"  {Fore.RED}→ HDR MUST be disabled! See methodology for justification.{Style.RESET_ALL}")

    # Check codec setting
    codec = metadata.get("capture_settings", {}).get("codec", "").upper()
    codec_ok = codec == "H.264" or codec == "H264"
    all_ok &= print_check(codec_ok, "Codec is H.264 (recommended)")
    if not codec_ok:
        if "HEVC" in codec or "H.265" in codec or "265" in codec:
            print(f"  {Fore.YELLOW}→ HEVC is acceptable but slower. H.264 recommended for best performance.{Style.RESET_ALL}")
            all_ok = True  # Don't fail, just warn
        elif "AV1" in codec:
            print(f"  {Fore.RED}→ AV1 NOT RECOMMENDED! Will cause slow decode and compatibility issues.{Style.RESET_ALL}")
            all_ok = False
        else:
            print(f"  {Fore.YELLOW}→ Set codec to H.264 in metadata.json capture_settings{Style.RESET_ALL}")

    # Check if system specs updated
    system_note = metadata.get("system", {}).get("note", "")
    specs_updated = "UPDATE" not in system_note.upper()
    all_ok &= print_check(specs_updated, "System specs have been updated")
    if not specs_updated:
        print(f"  {Fore.YELLOW}→ Update GPU, CPU, RAM, driver in metadata.json{Style.RESET_ALL}")

    # Check if game settings updated
    game_note = metadata.get("game_settings", {}).get("note", "")
    settings_updated = "UPDATE" not in game_note.upper()
    all_ok &= print_check(settings_updated, "Game settings have been documented")
    if not settings_updated:
        print(f"  {Fore.YELLOW}→ Update preset, ray tracing, etc. in metadata.json{Style.RESET_ALL}")

    # Check FPS limit
    fps_limit = metadata.get("game_settings", {}).get("fps_limit")
    fps_ok = fps_limit == 60
    all_ok &= print_check(fps_ok, "FPS limit set to 60")
    if not fps_ok:
        print(f"  {Fore.YELLOW}→ Set fps_limit: 60 in metadata.json{Style.RESET_ALL}")

    # Check VSync
    vsync = metadata.get("game_settings", {}).get("vsync")
    vsync_ok = vsync == False
    all_ok &= print_check(vsync_ok, "VSync is disabled")
    if not vsync_ok:
        print(f"  {Fore.YELLOW}→ Set vsync: false in metadata.json{Style.RESET_ALL}")

    return all_ok


def print_recording_checklist():
    """Print manual checklist for user to verify"""
    print_header("PRE-RECORDING MANUAL CHECKLIST")

    print(f"\n{Fore.CYAN}Before recording, verify IN-GAME settings:{Style.RESET_ALL}\n")

    checklist = [
        ("HDR", "Display → HDR → OFF (CRITICAL!)"),
        ("Graphics Preset", "Ultra/Maximum settings"),
        ("Ray Tracing", "Ultra (if supported)"),
        ("DLSS Frame Gen", "OFF (test DLSS SR only)"),
        ("VSync", "OFF (prevents stuttering)"),
        ("FPS Limiter", "60 FPS (for consistency)"),
        ("Resolution", "Match target (1080p/1440p/4K)"),
        ("MSI Afterburner", "FPS counter visible on screen"),
    ]

    for item, setting in checklist:
        print(f"  [ ] {item:20s} → {setting}")

    print(f"\n{Fore.CYAN}Windows Settings (if on Windows):{Style.RESET_ALL}\n")
    print(f"  [ ] {'HDR':20s} → Settings → Display → Use HDR → OFF")
    print(f"  [ ] {'Game Bar':20s} → Disable (can interfere with capture)")
    print(f"  [ ] {'Game Mode':20s} → ON (better performance)")

    print(f"\n{Fore.CYAN}Recording Software:{Style.RESET_ALL}\n")
    print(f"  [ ] {'Software':20s} → NVIDIA ShadowPlay / GeForce Experience")
    print(f"  [ ] {'Codec':20s} → H.264 (RECOMMENDED - fastest, best compatibility)")
    print(f"  [ ] {'Quality':20s} → High Quality or 50+ Mbps")
    print(f"  [ ] {'Frame Rate':20s} → 60 FPS")
    print(f"  [ ] {'Audio':20s} → Optional (not used in analysis)")
    print(f"\n  {Fore.YELLOW}Codec notes:{Style.RESET_ALL}")
    print(f"    • H.264:  ✅ Recommended (fast, universal compatibility)")
    print(f"    • HEVC:   ⚠️  Acceptable (smaller files, slower decode)")
    print(f"    • AV1:    ❌ DO NOT USE (very slow, compatibility issues)")

    print(f"\n{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}CRITICAL: SHADER COMPILATION WARMUP{Style.RESET_ALL}".center(80))
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")

    print(f"{Fore.RED}Before recording each mode (DLAA, Quality, Balanced, etc.):{Style.RESET_ALL}\n")
    print(f"  1. Run the benchmark 2-3 times WITHOUT recording")
    print(f"  2. This eliminates shader compilation stuttering")
    print(f"  3. First run compiles shaders → causes frame spikes")
    print(f"  4. Second/third runs use cached shaders → smooth FPS")
    print(f"  5. ONLY THEN start recording the 4th run\n")

    print(f"{Fore.CYAN}Why warmup is critical:{Style.RESET_ALL}")
    print(f"  • Modern games compile shaders at runtime")
    print(f"  • First execution = compilation overhead + stuttering")
    print(f"  • Cached execution = true DLSS/DLAA performance")
    print(f"  • Without warmup: FPS data includes compilation artifacts\n")

    print(f"{Fore.CYAN}Per-mode warmup required:{Style.RESET_ALL}")
    print(f"  • Each DLSS mode may use different shader variants")
    print(f"  • Changing from Quality → Balanced requires new warmup")
    print(f"  • Don't skip warmup even if game was run before")


def main():
    parser = argparse.ArgumentParser(
        description='Verify settings before recording benchmark data'
    )
    parser.add_argument('--game', required=True, help='Game name')
    parser.add_argument('--resolution', required=True, help='Resolution (1080p, 1440p, 4k)')
    parser.add_argument('--base-dir', type=Path, help='Base recordings directory')

    args = parser.parse_args()

    base_dir = args.base_dir or Path(__file__).parent.parent / "recordings"

    print_header("PRE-RECORDING SETTINGS CHECK")
    print(f"\nGame: {args.game}")
    print(f"Resolution: {args.resolution}")
    print(f"Recordings directory: {base_dir}")

    print_header("AUTOMATED CHECKS (metadata.json)")

    metadata_ok = check_metadata_file(args.game, args.resolution, base_dir)

    print_recording_checklist()

    print_header("SUMMARY")

    if metadata_ok:
        print(f"\n{Fore.GREEN}✓ Automated checks passed!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Next steps:{Style.RESET_ALL}")
        print(f"  1. Verify manual checklist above")
        print(f"  2. Record validation videos (run1.mp4, run2.mp4)")
        print(f"  3. Validate benchmark stability")
    else:
        print(f"\n{Fore.RED}✗ Some checks failed!{Style.RESET_ALL}")
        print(f"\nFix the issues above before recording.")

    print("\n" + "=" * 80 + "\n")

    return 0 if metadata_ok else 1


if __name__ == "__main__":
    exit(main())
