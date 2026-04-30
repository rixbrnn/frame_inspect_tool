#!/usr/bin/env python3
"""
Statistical Analysis for DLSS Quality Comparisons

Adds statistical rigor to metric comparisons:
- Paired t-tests or Wilcoxon signed-rank tests
- 95% Confidence intervals
- Cohen's d effect sizes
- Bonferroni correction for multiple comparisons

Addresses TCC Peer Review #8: Add statistical inference

Usage:
    python src/insights/statistical_analysis.py \
        --comparison-file results/cyberpunk/quality_comparison/1080p_DLAA_vs_Quality.json \
        --output results/cyberpunk/statistical_analysis/1080p_Quality.json

    # Or batch process all comparisons:
    python src/insights/statistical_analysis.py \
        --results-dir results/cyberpunk/quality_comparison \
        --output-dir results/cyberpunk/statistical_analysis
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional
import argparse


def load_comparison_data(json_file: Path) -> Dict:
    """Load comparison JSON with per-frame data"""
    with open(json_file) as f:
        return json.load(f)


def compute_paired_test(baseline: np.ndarray, test: np.ndarray,
                        metric_name: str) -> Dict:
    """
    Compute paired statistical test (t-test or Wilcoxon)

    Args:
        baseline: Reference values (e.g., DLAA)
        test: Test values (e.g., DLSS Quality)
        metric_name: Name of metric for reporting

    Returns:
        Dictionary with test results
    """
    # Remove NaN values
    valid_mask = ~(np.isnan(baseline) | np.isnan(test))
    baseline_clean = baseline[valid_mask]
    test_clean = test[valid_mask]

    n_samples = len(baseline_clean)

    if n_samples < 2:
        return {
            'test': 'insufficient_data',
            'n_samples': n_samples,
            'statistic': None,
            'p_value': None,
            'significant': False
        }

    # Compute differences
    differences = test_clean - baseline_clean
    mean_diff = np.mean(differences)
    std_diff = np.std(differences, ddof=1)

    # Check normality (if n>30, can assume normal via CLT)
    if n_samples >= 30:
        use_ttest = True
    else:
        # Shapiro-Wilk test for normality
        _, p_normality = stats.shapiro(differences)
        use_ttest = p_normality > 0.05

    # Perform appropriate test
    if use_ttest:
        # Paired t-test
        t_stat, p_value = stats.ttest_rel(test_clean, baseline_clean)
        test_name = 'paired_t_test'
        statistic = t_stat
    else:
        # Wilcoxon signed-rank test (non-parametric)
        stat, p_value = stats.wilcoxon(test_clean, baseline_clean)
        test_name = 'wilcoxon_signed_rank'
        statistic = stat

    # Compute 95% confidence interval for mean difference
    se_diff = std_diff / np.sqrt(n_samples)
    t_critical = stats.t.ppf(0.975, n_samples - 1)  # 95% CI
    ci_lower = mean_diff - t_critical * se_diff
    ci_upper = mean_diff + t_critical * se_diff

    # Cohen's d effect size
    cohens_d = mean_diff / std_diff if std_diff > 0 else 0.0

    # Effect size interpretation
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        effect_magnitude = 'negligible'
    elif abs_d < 0.5:
        effect_magnitude = 'small'
    elif abs_d < 0.8:
        effect_magnitude = 'medium'
    else:
        effect_magnitude = 'large'

    return {
        'test': test_name,
        'n_samples': int(n_samples),
        'statistic': float(statistic),
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05),
        'mean_difference': float(mean_diff),
        'std_difference': float(std_diff),
        'ci_95_lower': float(ci_lower),
        'ci_95_upper': float(ci_upper),
        'cohens_d': float(cohens_d),
        'effect_magnitude': effect_magnitude
    }


def bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> Tuple[float, List[bool]]:
    """
    Apply Bonferroni correction for multiple comparisons

    Args:
        p_values: List of p-values
        alpha: Significance level (default 0.05)

    Returns:
        (corrected_alpha, list of significant flags)
    """
    n_tests = len(p_values)
    corrected_alpha = alpha / n_tests
    significant = [p < corrected_alpha for p in p_values]
    return corrected_alpha, significant


def analyze_comparison(comparison_data: Dict) -> Dict:
    """
    Perform statistical analysis on comparison data

    Returns:
        Dictionary with statistical test results for all metrics
    """
    per_frame = comparison_data.get('per_frame_data', {})

    if not per_frame.get('enabled'):
        return {'error': 'Per-frame data not available'}

    frames = per_frame.get('frames', [])

    if not frames:
        return {'error': 'No frame data found'}

    # Extract metrics into arrays
    # Note: For DLAA vs DLSS comparison, "baseline" is implicitly perfect (DLAA)
    # and we're measuring degradation in test (DLSS mode)

    metrics_data = {}
    metric_names = ['ssim', 'psnr', 'lpips', 'flip']

    for metric in metric_names:
        values = []
        for frame in frames:
            if metric in frame:
                values.append(frame[metric])

        if values:
            metrics_data[metric] = np.array(values)

    # For consistency comparison (DLAA run1 vs run2), we have actual paired data
    # For DLSS mode comparison, we compare against baseline (DLAA assumed perfect = 1.0 for SSIM)

    comparison_name = comparison_data.get('alignment_method', 'unknown')

    results = {
        'comparison': comparison_name,
        'n_frames_analyzed': len(frames),
        'statistical_tests': {}
    }

    # Run tests for each metric
    # Note: For SSIM, higher is better; test against perfect (1.0)
    # For PSNR, higher is better; test against ideal
    # For LPIPS/FLIP, lower is better; test against perfect (0.0)

    for metric, values in metrics_data.items():
        if metric == 'ssim':
            # Test: How much worse than perfect (1.0)?
            baseline = np.ones_like(values)  # Perfect SSIM
            test = values
        elif metric == 'psnr':
            # For PSNR, we can't use infinity as baseline
            # Instead, test difference from observed mean
            # Use one-sample t-test against hypothetical perfect value
            # Skip for now as we need actual paired data
            continue
        elif metric in ['lpips', 'flip']:
            # Test: How much worse than perfect (0.0)?
            baseline = np.zeros_like(values)  # Perfect perceptual quality
            test = values
        else:
            continue

        test_result = compute_paired_test(baseline, test, metric)
        results['statistical_tests'][metric] = test_result

    return results


def analyze_multiple_comparisons(results_dir: Path, output_dir: Path,
                                 apply_bonferroni: bool = True):
    """
    Batch process all comparisons in a directory with multiple comparisons correction
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all comparison JSON files
    json_files = list(results_dir.glob("*_vs_*.json"))
    json_files += list(results_dir.glob("*_Consistency.json"))

    if not json_files:
        print(f"❌ No comparison files found in {results_dir}")
        return

    print(f"📊 Found {len(json_files)} comparison files")
    print(f"Bonferroni correction: {'Enabled' if apply_bonferroni else 'Disabled'}\n")

    all_results = []
    all_p_values = []

    # First pass: collect all p-values for Bonferroni
    for json_file in json_files:
        print(f"  Analyzing: {json_file.name}")

        try:
            comparison_data = load_comparison_data(json_file)
            results = analyze_comparison(comparison_data)

            if 'error' not in results:
                all_results.append((json_file, results))

                # Collect p-values for each metric
                for metric, test_result in results['statistical_tests'].items():
                    if test_result['p_value'] is not None:
                        all_p_values.append(test_result['p_value'])

        except Exception as e:
            print(f"    ❌ Error: {e}")
            continue

    # Apply Bonferroni correction
    if apply_bonferroni and all_p_values:
        corrected_alpha, _ = bonferroni_correction(all_p_values)
        print(f"\n🔬 Bonferroni correction:")
        print(f"  Original α = 0.05")
        print(f"  Corrected α = {corrected_alpha:.6f} ({len(all_p_values)} tests)\n")
    else:
        corrected_alpha = 0.05

    # Second pass: save results with corrected significance
    summary_data = []

    for json_file, results in all_results:
        # Update significance flags with corrected alpha
        for metric, test_result in results['statistical_tests'].items():
            if test_result['p_value'] is not None:
                test_result['significant_bonferroni'] = bool(test_result['p_value'] < corrected_alpha)

        results['bonferroni_corrected_alpha'] = float(corrected_alpha)

        # Save individual result
        output_file = output_dir / f"{json_file.stem}_stats.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Add to summary
        for metric, test_result in results['statistical_tests'].items():
            summary_data.append({
                'comparison': results['comparison'],
                'metric': metric,
                'n_samples': test_result['n_samples'],
                'test': test_result['test'],
                'statistic': test_result.get('statistic'),
                'p_value': test_result.get('p_value'),
                'significant': test_result['significant'],
                'significant_bonferroni': test_result.get('significant_bonferroni', False),
                'mean_difference': test_result.get('mean_difference'),
                'ci_95_lower': test_result.get('ci_95_lower'),
                'ci_95_upper': test_result.get('ci_95_upper'),
                'cohens_d': test_result.get('cohens_d'),
                'effect_magnitude': test_result.get('effect_magnitude')
            })

    # Create summary CSV
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_csv = output_dir / "statistical_summary.csv"
        summary_df.to_csv(summary_csv, index=False)
        print(f"✅ Summary saved: {summary_csv}")

        # Print key findings
        print("\n" + "="*70)
        print("KEY STATISTICAL FINDINGS")
        print("="*70)

        # Count significant results
        n_significant_uncorrected = summary_df['significant'].sum()
        n_significant_corrected = summary_df['significant_bonferroni'].sum()

        print(f"\nSignificant results (α=0.05, uncorrected): {n_significant_uncorrected}/{len(summary_df)}")
        print(f"Significant results (Bonferroni corrected): {n_significant_corrected}/{len(summary_df)}")

        # Large effect sizes
        large_effects = summary_df[summary_df['effect_magnitude'] == 'large']
        if not large_effects.empty:
            print(f"\n📈 Large effect sizes (Cohen's d > 0.8): {len(large_effects)}")
            for _, row in large_effects.iterrows():
                print(f"  - {row['comparison']} ({row['metric']}): d={row['cohens_d']:.2f}, p={row['p_value']:.4f}")


def main():
    parser = argparse.ArgumentParser(description='Statistical analysis of DLSS comparisons')
    parser.add_argument('--comparison-file', type=str,
                       help='Single comparison JSON file to analyze')
    parser.add_argument('--results-dir', type=str,
                       help='Directory containing comparison files (batch mode)')
    parser.add_argument('--output', type=str,
                       help='Output file for single comparison')
    parser.add_argument('--output-dir', type=str,
                       help='Output directory for batch mode')
    parser.add_argument('--no-bonferroni', action='store_true',
                       help='Disable Bonferroni correction')

    args = parser.parse_args()

    if args.comparison_file:
        # Single file mode
        json_file = Path(args.comparison_file)
        output_file = Path(args.output) if args.output else json_file.parent / f"{json_file.stem}_stats.json"

        print(f"📊 Analyzing: {json_file}")

        comparison_data = load_comparison_data(json_file)
        results = analyze_comparison(comparison_data)

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✅ Saved: {output_file}")

    elif args.results_dir:
        # Batch mode
        results_dir = Path(args.results_dir)
        output_dir = Path(args.output_dir) if args.output_dir else results_dir.parent / "statistical_analysis"

        analyze_multiple_comparisons(results_dir, output_dir,
                                    apply_bonferroni=not args.no_bonferroni)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
