#!/usr/bin/env python3
"""
Performance-Quality Analyzer
Correlates FPS data with SSIM/PSNR quality metrics to analyze DLSS efficiency
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass

@dataclass
class ModeAnalysis:
    """Analysis results for a single DLSS mode"""
    mode_name: str
    # Performance
    avg_fps: float
    fps_1percent_low: float
    fps_gain_percent: float
    # Quality
    ssim: float
    psnr: float
    ssim_loss_percent: float
    psnr_loss_db: float
    # Efficiency
    efficiency_ratio: float  # fps_gain / quality_loss
    cost_per_fps: float      # quality_loss / fps_gain
    # Categorization
    is_pareto_optimal: bool = False
    recommendation: str = ""


class PerformanceQualityAnalyzer:
    """Analyze FPS vs Quality tradeoffs for DLSS modes"""

    def __init__(self):
        self.modes_data = {}
        self.baseline_mode = None

    def load_fps_data(self, fps_file: str, mode_mapping: Optional[Dict] = None) -> None:
        """
        Load FPS data from JSON (fps_extractor.py output) or CSV

        Args:
            fps_file: Path to FPS data file
            mode_mapping: Optional mapping of video filenames to mode names
                         e.g., {"Quality.mp4": "Quality"}
        """
        fps_path = Path(fps_file)

        if fps_path.suffix == '.json':
            with open(fps_file, 'r') as f:
                data = json.load(f)

            # Handle different JSON formats
            if isinstance(data, dict):
                if 'source' in data:  # Single mode from fps_extractor
                    mode_name = mode_mapping.get(fps_path.stem, fps_path.stem)
                    self.modes_data[mode_name] = {'fps': data}
                else:  # Multiple modes
                    for mode_name, fps_data in data.items():
                        if mode_mapping and mode_name in mode_mapping:
                            mode_name = mode_mapping[mode_name]
                        self.modes_data[mode_name] = {'fps': fps_data}

        elif fps_path.suffix == '.csv':
            # Manual CSV format: mode,avg_fps,1%_low,0.1%_low
            df = pd.read_csv(fps_file)
            for _, row in df.iterrows():
                mode = row['mode']
                self.modes_data[mode] = {
                    'fps': {
                        'avg_fps': float(row['avg_fps']),
                        '1%_low': float(row.get('1%_low', row['avg_fps'])),
                        '0.1%_low': float(row.get('0.1%_low', row['avg_fps']))
                    }
                }

    def load_quality_data(self, quality_file: str, mode_mapping: Optional[Dict] = None) -> None:
        """
        Load SSIM/PSNR data from JSON or CSV

        Expected JSON format (from video_comparison.py):
        {
            "Quality.mp4": {
                "avg_ssim": 98.5,
                "avg_psnr": 42.3
            },
            ...
        }

        Or CSV format:
        mode,ssim,psnr
        DLAA_4K,100.0,inf
        Quality,98.5,42.3
        """
        quality_path = Path(quality_file)

        if quality_path.suffix == '.json':
            with open(quality_file, 'r') as f:
                data = json.load(f)

            for file_or_mode, metrics in data.items():
                mode_name = mode_mapping.get(file_or_mode, file_or_mode) if mode_mapping else file_or_mode

                # Remove .mp4 extension if present
                mode_name = mode_name.replace('.mp4', '').replace('.mkv', '')

                if mode_name not in self.modes_data:
                    self.modes_data[mode_name] = {}

                self.modes_data[mode_name]['quality'] = {
                    'ssim': float(metrics.get('avg_ssim', metrics.get('ssim', 0))),
                    'psnr': float(metrics.get('avg_psnr', metrics.get('psnr', 0)))
                }

        elif quality_path.suffix == '.csv':
            df = pd.read_csv(quality_file)
            for _, row in df.iterrows():
                mode = row['mode']
                if mode not in self.modes_data:
                    self.modes_data[mode] = {}

                psnr = row['psnr']
                # Handle inf values
                if isinstance(psnr, str) and psnr.lower() == 'inf':
                    psnr = float('inf')
                else:
                    psnr = float(psnr)

                self.modes_data[mode]['quality'] = {
                    'ssim': float(row['ssim']),
                    'psnr': psnr
                }

    def set_baseline(self, mode_name: str) -> None:
        """Set the baseline mode (typically DLAA_4K or Native_4K)"""
        if mode_name not in self.modes_data:
            raise ValueError(f"Mode '{mode_name}' not found in data")
        self.baseline_mode = mode_name

    def analyze_tradeoffs(self) -> List[ModeAnalysis]:
        """
        Calculate efficiency metrics for all modes

        Returns:
            List of ModeAnalysis objects sorted by efficiency ratio
        """
        if not self.baseline_mode:
            raise ValueError("Baseline mode not set. Call set_baseline() first.")

        baseline = self.modes_data[self.baseline_mode]
        baseline_fps = baseline['fps']['avg_fps']
        baseline_ssim = baseline['quality']['ssim']
        baseline_psnr = baseline['quality']['psnr']

        results = []

        for mode_name, data in self.modes_data.items():
            if mode_name == self.baseline_mode:
                # Baseline has 0 gain/loss by definition
                results.append(ModeAnalysis(
                    mode_name=mode_name,
                    avg_fps=baseline_fps,
                    fps_1percent_low=baseline['fps'].get('1%_low', baseline_fps),
                    fps_gain_percent=0.0,
                    ssim=baseline_ssim,
                    psnr=baseline_psnr,
                    ssim_loss_percent=0.0,
                    psnr_loss_db=0.0,
                    efficiency_ratio=float('inf'),
                    cost_per_fps=0.0,
                    recommendation="Baseline (highest quality)"
                ))
                continue

            # Calculate FPS metrics
            fps = data['fps']['avg_fps']
            fps_gain = ((fps - baseline_fps) / baseline_fps) * 100

            # Calculate quality metrics
            ssim = data['quality']['ssim']
            psnr = data['quality']['psnr']
            ssim_loss = baseline_ssim - ssim  # absolute loss
            ssim_loss_percent = (ssim_loss / baseline_ssim) * 100

            # PSNR loss (careful with inf baseline)
            if np.isinf(baseline_psnr):
                psnr_loss = 0 if np.isinf(psnr) else float('inf')
            else:
                psnr_loss = baseline_psnr - psnr

            # Efficiency metrics
            if ssim_loss_percent > 0:
                efficiency_ratio = fps_gain / ssim_loss_percent
                cost_per_fps = ssim_loss_percent / fps_gain
            else:
                efficiency_ratio = float('inf')
                cost_per_fps = 0.0

            # Generate recommendation
            recommendation = self._generate_recommendation(
                fps_gain, ssim_loss_percent, efficiency_ratio
            )

            results.append(ModeAnalysis(
                mode_name=mode_name,
                avg_fps=fps,
                fps_1percent_low=data['fps'].get('1%_low', fps),
                fps_gain_percent=fps_gain,
                ssim=ssim,
                psnr=psnr,
                ssim_loss_percent=ssim_loss_percent,
                psnr_loss_db=psnr_loss,
                efficiency_ratio=efficiency_ratio,
                cost_per_fps=cost_per_fps,
                recommendation=recommendation
            ))

        # Sort by efficiency ratio (descending, best first)
        results.sort(key=lambda x: x.efficiency_ratio if not np.isinf(x.efficiency_ratio) else -1,
                     reverse=True)

        # Mark Pareto optimal modes
        results = self._mark_pareto_optimal(results)

        return results

    def _generate_recommendation(self, fps_gain: float,
                                  quality_loss: float,
                                  efficiency: float) -> str:
        """Generate human-readable recommendation"""
        if efficiency > 15:
            return "Excellent (Best FPS/quality ratio)"
        elif efficiency > 12:
            return "Very Good (Recommended for balanced play)"
        elif efficiency > 10:
            return "Good (Decent performance boost)"
        elif efficiency > 8:
            return "Acceptable (High FPS, noticeable quality loss)"
        else:
            return "Poor (Diminishing returns)"

    def _mark_pareto_optimal(self, results: List[ModeAnalysis]) -> List[ModeAnalysis]:
        """
        Mark modes that are Pareto optimal
        (No other mode has both higher FPS AND higher quality)
        """
        for i, mode_a in enumerate(results):
            if mode_a.mode_name == self.baseline_mode:
                mode_a.is_pareto_optimal = True
                continue

            is_optimal = True
            for mode_b in results:
                if mode_b.mode_name == mode_a.mode_name:
                    continue
                # Check if mode_b dominates mode_a
                if (mode_b.avg_fps >= mode_a.avg_fps and
                    mode_b.ssim >= mode_a.ssim and
                    (mode_b.avg_fps > mode_a.avg_fps or mode_b.ssim > mode_a.ssim)):
                    is_optimal = False
                    break

            mode_a.is_pareto_optimal = is_optimal

        return results

    def print_summary(self, results: List[ModeAnalysis]) -> None:
        """Print analysis results to console"""
        print("\n" + "="*80)
        print("DLSS PERFORMANCE-QUALITY ANALYSIS")
        print(f"Baseline: {self.baseline_mode}")
        print("="*80 + "\n")

        # Create table
        headers = ["Mode", "FPS", "FPS Gain", "SSIM", "SSIM Loss",
                   "Efficiency", "Pareto", "Recommendation"]
        rows = []

        for mode in results:
            rows.append([
                mode.mode_name,
                f"{mode.avg_fps:.1f}",
                f"+{mode.fps_gain_percent:.1f}%" if mode.fps_gain_percent > 0 else "0%",
                f"{mode.ssim:.2f}%",
                f"-{mode.ssim_loss_percent:.2f}%" if mode.ssim_loss_percent > 0 else "0%",
                f"{mode.efficiency_ratio:.1f}" if not np.isinf(mode.efficiency_ratio) else "∞",
                "✓" if mode.is_pareto_optimal else "",
                mode.recommendation
            ])

        # Print formatted table
        col_widths = [max(len(str(row[i])) for row in [headers] + rows)
                      for i in range(len(headers))]

        def print_row(row):
            print(" | ".join(str(item).ljust(width)
                            for item, width in zip(row, col_widths)))

        print_row(headers)
        print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
        for row in rows:
            print_row(row)

        print("\n" + "="*80)
        print("KEY FINDINGS:")
        print("="*80)

        # Find best efficiency
        non_baseline = [r for r in results if r.mode_name != self.baseline_mode]
        if non_baseline:
            best_efficiency = max(non_baseline, key=lambda x: x.efficiency_ratio)
            print(f"\n✓ Best Efficiency: {best_efficiency.mode_name}")
            print(f"  - Delivers {best_efficiency.fps_gain_percent:.1f}% more FPS")
            print(f"  - Sacrifices only {best_efficiency.ssim_loss_percent:.2f}% SSIM")
            print(f"  - Efficiency ratio: {best_efficiency.efficiency_ratio:.1f}")

            # Find highest FPS
            highest_fps = max(non_baseline, key=lambda x: x.avg_fps)
            print(f"\n✓ Highest FPS: {highest_fps.mode_name}")
            print(f"  - {highest_fps.avg_fps:.1f} FPS (vs {results[-1].avg_fps:.1f} baseline)")
            print(f"  - Quality cost: {highest_fps.ssim_loss_percent:.2f}% SSIM loss")

            # Pareto optimal count
            pareto_count = sum(1 for r in results if r.is_pareto_optimal)
            print(f"\n✓ Pareto Optimal Modes: {pareto_count}")
            print(f"  (These modes are 'sweet spots' - no better alternatives)")

    def export_to_csv(self, results: List[ModeAnalysis], output_file: str) -> None:
        """Export results to CSV for LaTeX tables"""
        rows = []
        for mode in results:
            rows.append({
                'Mode': mode.mode_name,
                'Avg_FPS': mode.avg_fps,
                '1%_Low_FPS': mode.fps_1percent_low,
                'FPS_Gain_%': mode.fps_gain_percent,
                'SSIM_%': mode.ssim,
                'SSIM_Loss_%': mode.ssim_loss_percent,
                'PSNR_dB': mode.psnr if not np.isinf(mode.psnr) else 'inf',
                'PSNR_Loss_dB': mode.psnr_loss_db if not np.isinf(mode.psnr_loss_db) else 'inf',
                'Efficiency_Ratio': mode.efficiency_ratio if not np.isinf(mode.efficiency_ratio) else 'inf',
                'Cost_Per_FPS': mode.cost_per_fps,
                'Pareto_Optimal': 'Yes' if mode.is_pareto_optimal else 'No',
                'Recommendation': mode.recommendation
            })

        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False, float_format='%.2f')
        print(f"\n✓ Results exported to: {output_file}")

    def export_to_json(self, results: List[ModeAnalysis], output_file: str) -> None:
        """Export results to JSON"""
        output = {
            'baseline': self.baseline_mode,
            'modes': []
        }

        for mode in results:
            output['modes'].append({
                'name': mode.mode_name,
                'performance': {
                    'avg_fps': mode.avg_fps,
                    '1%_low': mode.fps_1percent_low,
                    'fps_gain_percent': mode.fps_gain_percent
                },
                'quality': {
                    'ssim': mode.ssim,
                    'psnr': mode.psnr if not np.isinf(mode.psnr) else None,
                    'ssim_loss_percent': mode.ssim_loss_percent,
                    'psnr_loss_db': mode.psnr_loss_db if not np.isinf(mode.psnr_loss_db) else None
                },
                'efficiency': {
                    'ratio': mode.efficiency_ratio if not np.isinf(mode.efficiency_ratio) else None,
                    'cost_per_fps': mode.cost_per_fps
                },
                'pareto_optimal': mode.is_pareto_optimal,
                'recommendation': mode.recommendation
            })

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"✓ Results exported to: {output_file}")

    def plot_fps_vs_quality(self, results: List[ModeAnalysis],
                            output_file: Optional[str] = None) -> None:
        """
        Create scatter plot: FPS vs SSIM with efficiency frontier

        Args:
            results: Analysis results
            output_file: If provided, save to file (PNG). Otherwise show plot.
        """
        # Set style
        sns.set_style("whitegrid")
        plt.figure(figsize=(12, 8))

        # Extract data
        fps_values = [r.avg_fps for r in results]
        ssim_values = [r.ssim for r in results]
        mode_names = [r.mode_name for r in results]
        pareto_optimal = [r.is_pareto_optimal for r in results]

        # Color by Pareto optimality
        colors = ['green' if p else 'blue' for p in pareto_optimal]

        # Size by efficiency
        sizes = [max(100, min(500, r.efficiency_ratio * 30))
                 if not np.isinf(r.efficiency_ratio) else 800
                 for r in results]

        # Scatter plot
        scatter = plt.scatter(fps_values, ssim_values,
                             c=colors, s=sizes, alpha=0.6, edgecolors='black')

        # Add labels
        for i, (fps, ssim, name) in enumerate(zip(fps_values, ssim_values, mode_names)):
            plt.annotate(name, (fps, ssim),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=9, fontweight='bold')

        # Draw efficiency frontier (Pareto optimal curve)
        pareto_results = [r for r in results if r.is_pareto_optimal]
        pareto_results.sort(key=lambda x: x.avg_fps)
        pareto_fps = [r.avg_fps for r in pareto_results]
        pareto_ssim = [r.ssim for r in pareto_results]

        if len(pareto_fps) > 1:
            plt.plot(pareto_fps, pareto_ssim, 'g--', linewidth=2,
                    alpha=0.5, label='Efficiency Frontier (Pareto Optimal)')

        plt.xlabel('Average FPS', fontsize=12, fontweight='bold')
        plt.ylabel('SSIM (%)', fontsize=12, fontweight='bold')
        plt.title('DLSS Performance-Quality Tradeoff Analysis',
                 fontsize=14, fontweight='bold')

        plt.legend(['Pareto Optimal', 'Dominated'], loc='lower right')
        plt.grid(True, alpha=0.3)

        # Add quadrant lines at baseline
        baseline = next(r for r in results if r.mode_name == self.baseline_mode)
        plt.axhline(y=baseline.ssim, color='red', linestyle=':', alpha=0.3,
                   label=f'Baseline SSIM ({baseline.ssim:.1f}%)')
        plt.axvline(x=baseline.avg_fps, color='red', linestyle=':', alpha=0.3,
                   label=f'Baseline FPS ({baseline.avg_fps:.1f})')

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Chart saved to: {output_file}")
        else:
            plt.show()

    def plot_efficiency_bars(self, results: List[ModeAnalysis],
                            output_file: Optional[str] = None) -> None:
        """Create bar chart showing efficiency ratios"""
        # Filter out baseline
        plot_results = [r for r in results if r.mode_name != self.baseline_mode]
        plot_results.sort(key=lambda x: x.efficiency_ratio, reverse=True)

        fig, ax = plt.subplots(figsize=(12, 6))

        modes = [r.mode_name for r in plot_results]
        efficiency = [r.efficiency_ratio for r in plot_results]
        colors = ['green' if r.is_pareto_optimal else 'steelblue' for r in plot_results]

        bars = ax.bar(modes, efficiency, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar, eff in zip(bars, efficiency):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{eff:.1f}',
                   ha='center', va='bottom', fontweight='bold')

        ax.set_ylabel('Efficiency Ratio (FPS Gain % / SSIM Loss %)',
                     fontsize=11, fontweight='bold')
        ax.set_xlabel('DLSS Mode', fontsize=11, fontweight='bold')
        ax.set_title('DLSS Mode Efficiency Comparison\n(Higher = Better FPS/Quality Tradeoff)',
                    fontsize=13, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Chart saved to: {output_file}")
        else:
            plt.show()


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze DLSS Performance-Quality Tradeoffs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis with manual CSV files
  python performance_quality_analyzer.py \\
    --fps fps_data.csv \\
    --quality quality_data.csv \\
    --baseline DLAA_4K

  # Full analysis with visualizations
  python performance_quality_analyzer.py \\
    --fps frameview_fps.json \\
    --quality video_comparison_results.json \\
    --baseline DLAA_4K \\
    --output-csv results_table.csv \\
    --plot-fps-vs-quality charts/fps_vs_quality.png \\
    --plot-efficiency charts/efficiency.png
        """
    )

    parser.add_argument('--fps', required=True,
                       help='FPS data file (JSON or CSV)')
    parser.add_argument('--quality', required=True,
                       help='Quality metrics file (JSON or CSV)')
    parser.add_argument('--baseline', required=True,
                       help='Baseline mode name (e.g., DLAA_4K)')
    parser.add_argument('--output-csv',
                       help='Export results to CSV')
    parser.add_argument('--output-json',
                       help='Export results to JSON')
    parser.add_argument('--plot-fps-vs-quality',
                       help='Save FPS vs SSIM scatter plot')
    parser.add_argument('--plot-efficiency',
                       help='Save efficiency bar chart')

    args = parser.parse_args()

    # Run analysis
    analyzer = PerformanceQualityAnalyzer()

    print("Loading FPS data...")
    analyzer.load_fps_data(args.fps)

    print("Loading quality data...")
    analyzer.load_quality_data(args.quality)

    print(f"Setting baseline: {args.baseline}")
    analyzer.set_baseline(args.baseline)

    print("Analyzing tradeoffs...")
    results = analyzer.analyze_tradeoffs()

    # Print summary
    analyzer.print_summary(results)

    # Export data
    if args.output_csv:
        analyzer.export_to_csv(results, args.output_csv)

    if args.output_json:
        analyzer.export_to_json(results, args.output_json)

    # Generate plots
    if args.plot_fps_vs_quality:
        print("\nGenerating FPS vs Quality plot...")
        analyzer.plot_fps_vs_quality(results, args.plot_fps_vs_quality)

    if args.plot_efficiency:
        print("\nGenerating efficiency chart...")
        analyzer.plot_efficiency_bars(results, args.plot_efficiency)

    print("\n✓ Analysis complete!")
