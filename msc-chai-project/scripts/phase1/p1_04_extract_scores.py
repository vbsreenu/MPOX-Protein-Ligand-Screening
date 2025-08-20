#!/usr/bin/env python3
"""
File: p1_04_extract_scores.py
Description:
    Step 1: Traverse all Chai output folders (with/without templates).
    Step 2: Extract aggregate_score and pTM score from .npz files.
    Step 3: Save results into a single summary TSV file.

Usage:
    python scripts/phase1/extract_scores.py --root-dir data/phase1 --out-file results/phase1/all_scores_summary.tsv

Notes:
    - Each subfolder in root_dir should have Chai outputs:
        output_<complex>/scores.model_idx_*.npz
        output_<complex>_noTemplate/scores.model_idx_*.npz
    - Output TSV columns: Complex, Mode, Model, AggregateScore, pTM
"""

import os
import glob
import numpy as np
import argparse


# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Extract Chai model scores into a summary table.")
parser.add_argument("--root-dir", type=str, default="data/phase1",
                    help="Root folder containing complex subdirectories (default: data/phase1)")
parser.add_argument("--out-file", type=str, default="results/phase1/all_scores_summary.tsv",
                    help="Output TSV file (default: results/phase1/all_scores_summary.tsv)")
args = parser.parse_args()

root_dir = args.root_dir
out_file = args.out_file


# === Step 2: Function to extract scores from one Chai output folder ===
def extract_scores(output_dir, mode):
    """
    Extract aggregate_score and pTM from a Chai output folder.

    Parameters:
        output_dir (str): Path to Chai output folder
        mode (str): "with-template" or "no-template"

    Returns:
        list of [complex_name, mode, model_id, aggregate_score, ptm_score]
    """
    results = []
    complex_name = os.path.basename(output_dir).replace("output_", "").replace("_noTemplate", "")

    for npz_path in glob.glob(os.path.join(output_dir, "scores.model_idx_*.npz")):
        model_id = os.path.basename(npz_path).replace("scores.", "").replace(".npz", "")
        try:
            data = np.load(npz_path)
            agg_score = float(data["aggregate_score"].item()) if "aggregate_score" in data else "NA"
            ptm_score = float(data["ptm"].item()) if "ptm" in data else "NA"
            results.append([complex_name, mode, model_id, agg_score, ptm_score])
        except Exception as e:
            print(f"[WARN] Failed to read {npz_path}: {e}")
    return results


# === Step 3: Traverse all subdirectories and collect scores ===
all_results = []
for complex_dir in sorted(os.listdir(root_dir)):
    full_path = os.path.join(root_dir, complex_dir)
    if not os.path.isdir(full_path):
        continue

    output_with = os.path.join(full_path, f"output_{complex_dir}")
    if os.path.isdir(output_with):
        all_results.extend(extract_scores(output_with, mode="with-template"))

    output_no = os.path.join(full_path, f"output_{complex_dir}_noTemplate")
    if os.path.isdir(output_no):
        all_results.extend(extract_scores(output_no, mode="no-template"))


# === Step 4: Write results to TSV ===
os.makedirs(os.path.dirname(out_file), exist_ok=True)
with open(out_file, "w") as f:
    f.write("Complex\tMode\tModel\tAggregateScore\tpTM\n")
    for row in all_results:
        f.write("\t".join(map(str, row)) + "\n")

print(f"[INFO] Summary saved to: {out_file}")