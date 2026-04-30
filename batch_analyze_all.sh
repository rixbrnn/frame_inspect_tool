#!/bin/bash

GAMES=(
  "blackmyth_medium"
  "cod_mw2_extreme"
  "cyberpunk_low"
  "cyberpunk"
  "forza_extreme"
  "forza_motorsport_ultra"
  "marvel_rivals_low"
  "rdr2_ultra"
  "returnal_epic"
  "tomb_raider_highest_scene_1"
)

echo "========================================================================"
echo "BATCH ANALYSIS: ALL 10 GAMES"
echo "========================================================================"

for game in "${GAMES[@]}"; do
  echo ""
  echo "========================================================================"
  echo "Processing: $game"
  echo "========================================================================"
  
  # Statistical Analysis
  echo "  → Running statistical analysis..."
  python src/insights/statistical_analysis.py \
    --results-dir results/$game/quality_comparison \
    --output-dir results/$game/statistical_analysis
  
  # Metric Agreement
  echo "  → Running metric agreement analysis..."
  python src/insights/metric_agreement.py \
    --results-dir results/$game/quality_comparison \
    --output results/$game/metric_agreement
  
  # Reproducibility Analysis
  echo "  → Running reproducibility analysis..."
  python src/insights/reproducibility_analysis.py \
    --results-dir results/$game/quality_comparison \
    --output results/$game/reproducibility
  
  # FPS Correlation
  echo "  → Running FPS correlation analysis..."
  python src/insights/fps_quality_correlation.py \
    --results-dir results/$game/quality_comparison \
    --output results/$game/fps_correlation
  
  echo "  ✅ $game complete!"
done

echo ""
echo "========================================================================"
echo "✅ ALL GAMES PROCESSED"
echo "========================================================================"
