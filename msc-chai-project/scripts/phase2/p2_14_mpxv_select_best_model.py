#!/usr/bin/env python3
"""
File: p2_14_mpxv_select_best_model.py
Description:
    Step 1: Load all Chai model scores (from Phase 2).
    Step 2: For each complex, select the model with the highest aggregate_score.
    Step 3: Save best models into a TSV file.

Usage:
    python scripts/phase2/p2_14_mpxv_select_best_model.py \
        --root-dir results/phase2/analysis \
        --score-file results/phase2/all_scores_summary.tsv \
        --out-file results/phase2/best_model_per_complex.tsv
"""

import os
import pandas as pd
import argparse


# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Select best model per complex (Phase 2).")
parser.add_argument("--root-dir", type=str, default="results/phase2/analysis",
                    help="Root directory containing score summary file (default: results/phase2/analysis)")
parser.add_argument("--score-file", type=str, default="results/phase2/all_scores_summary.tsv",
                    help="Input TSV file containing all model scores")
parser.add_argument("--out-file", type=str, default="results/phase2/best_model_per_complex.tsv",
                    help="Output TSV file to save best model per complex")
args = parser.parse_args()

root_dir = args.root_dir
score_file = args.score_file
out_file = args.out_file


# === Step 2: Load score summary ===
df = pd.read_csv(score_file, sep="\t")

# === Step 3: Ensure numeric conversion ===
df["AggregateScore"] = pd.to_numeric(df["AggregateScore"], errors="coerce")
df["pTM"] = pd.to_numeric(df["pTM"], errors="coerce")

# === Step 4: Select best model (highest AggregateScore per complex) ===
best_df = df.loc[df.groupby("Complex")["AggregateScore"].idxmax()]

# === Step 5: Save results ===
os.makedirs(os.path.dirname(out_file), exist_ok=True)
best_df.to_csv(out_file, sep="\t", index=False)

print(f"[INFO] Best model summary saved to: {out_file}")
