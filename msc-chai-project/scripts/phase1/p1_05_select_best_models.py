#!/usr/bin/env python3
"""
File: p1_05_select_best_models.py
Description:
  Step 1: Load the score summary table (per model per complex).
  Step 2: For each (Complex, Mode), select the model with the highest AggregateScore.
  Step 3: Save the best-per-group table for downstream analysis.

Usage:
  python scripts/phase1/select_best_models.py \
      --score-file results/phase1/all_scores_summary.tsv \
      --out-file results/phase1/best_model_per_complex.tsv

Notes:
  - Input TSV should have columns: Complex, Mode, Model, AggregateScore, pTM
  - AggregateScore and pTM will be coerced to numeric (invalid → NaN)
"""

import argparse
import pandas as pd
import os


# === Step 0: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Select best model per (Complex, Mode) by AggregateScore.")
    parser.add_argument("--score-file", required=False,
                        default="results/phase1/all_scores_summary.tsv",
                        help="Path to the score summary TSV.")
    parser.add_argument("--out-file", required=False,
                        default="results/phase1/best_model_per_complex.tsv",
                        help="Path to save the best-per-group TSV.")
    return parser.parse_args()


# === Step 1: Load and normalize ===
def load_scores(score_file: str) -> pd.DataFrame:
    df = pd.read_csv(score_file, sep="\t")
    # Step 1.1: Ensure numeric types for scores
    df["AggregateScore"] = pd.to_numeric(df["AggregateScore"], errors="coerce")
    df["pTM"] = pd.to_numeric(df.get("pTM", pd.Series(dtype=float)), errors="coerce")
    return df


# === Step 2: Select best per (Complex, Mode) ===
def select_best(df: pd.DataFrame) -> pd.DataFrame:
    # Step 2.1: group and pick idx of max AggregateScore
    idx = df.groupby(["Complex", "Mode"])["AggregateScore"].idxmax()
    best_df = df.loc[idx].copy()

    # Step 2.2: Sort for readability
    best_df.sort_values(by=["Complex", "Mode", "AggregateScore"], ascending=[True, True, False], inplace=True)
    return best_df


# === Step 3: Save ===
def main():
    args = parse_args()
    df = load_scores(args.score_file)
    best_df = select_best(df)

    os.makedirs(os.path.dirname(args.out_file), exist_ok=True)
    best_df.to_csv(args.out_file, sep="\t", index=False)
    print(f"[OK] Best model summary saved to: {args.out_file}")


if __name__ == "__main__":
    main()