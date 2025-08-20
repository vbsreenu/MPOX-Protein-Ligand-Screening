#!/usr/bin/env python3
"""
File: p2_20_merge_overall_results.py
Description:
    Step 1: Load Phase 2 result tables (best model, ΔSASA, PoseBuster).
    Step 2: Merge them into one summary table.
    Step 3: Save merged overall summary.

Usage:
    python scripts/phase2/p2_20_merge_overall_results.py \
        --root-dir results/phase2/analysis \
        --best-model results/phase2/analysis/best_model_per_complex.tsv \
        --delta-sasa results/phase2/analysis/delta_sasa_biopython.tsv \
        --posebuster results/phase2/analysis/posebuster_bust_sdf_stdout/bust_stdout_summary.tsv \
        --out-file results/phase2/analysis/phase2_overall_summary.tsv
"""

import os
import argparse
import pandas as pd


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Merge Phase 2 results into overall summary table.")
    parser.add_argument("--root-dir", type=str, default="results/phase2/analysis",
                        help="Root analysis directory (default: results/phase2/analysis)")
    parser.add_argument("--best-model", type=str, default="results/phase2/analysis/best_model_per_complex.tsv",
                        help="Best model summary file (default: results/phase2/analysis/best_model_per_complex.tsv)")
    parser.add_argument("--delta-sasa", type=str, default="results/phase2/analysis/delta_sasa_biopython.tsv",
                        help="ΔSASA result file (default: results/phase2/analysis/delta_sasa_biopython.tsv)")
    parser.add_argument("--posebuster", type=str,
                        default="results/phase2/analysis/posebuster_bust_sdf_stdout/bust_stdout_summary.tsv",
                        help="PoseBuster result file (default: results/phase2/analysis/posebuster_bust_sdf_stdout/bust_stdout_summary.tsv)")
    parser.add_argument("--out-file", type=str, default="results/phase2/analysis/phase2_overall_summary.tsv",
                        help="Output merged summary TSV (default: results/phase2/analysis/phase2_overall_summary.tsv)")
    return parser.parse_args()


# === Step 2: Load inputs ===
def load_inputs(best_model_file: str, delta_sasa_file: str, posebuster_file: str):
    df_best = pd.read_csv(best_model_file, sep="\t")
    df_sasa = pd.read_csv(delta_sasa_file, sep="\t")
    df_pose = pd.read_csv(posebuster_file, sep="\t")

    # Keep only relevant PoseBuster columns
    if set(["Complex", "Pass_Status", "Passed", "Total", "Pass_Rate"]).issubset(df_pose.columns):
        df_pose = df_pose[["Complex", "Pass_Status", "Passed", "Total", "Pass_Rate"]]
    return df_best, df_sasa, df_pose


# === Step 3: Merge ===
def merge_results(df_best, df_sasa, df_pose) -> pd.DataFrame:
    # Merge best model with ΔSASA
    df_merge = pd.merge(df_best, df_sasa, on="Complex", how="left")
    # Merge with PoseBuster
    df_merge = pd.merge(df_merge, df_pose, on="Complex", how="left")
    return df_merge


# === Step 4: Save ===
def save_output(df: pd.DataFrame, out_file: str):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    df.to_csv(out_file, sep="\t", index=False)
    print(f"[INFO] Overall Phase 2 summary saved to: {out_file}")
    print(f"[INFO] Total complexes in summary: {len(df)}")


# === Step 5: Main ===
def main():
    args = parse_args()
    df_best, df_sasa, df_pose = load_inputs(args.best_model, args.delta_sasa, args.posebuster)
    df_merge = merge_results(df_best, df_sasa, df_pose)
    save_output(df_merge, args.out_file)


if __name__ == "__main__":
    main()
