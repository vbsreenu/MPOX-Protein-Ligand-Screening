#!/usr/bin/env python3
"""
File: p2_03_select_best_models.py
Description:
    Step 1: Traverse all monkeypox protein output folders (no-template only).
    Step 2: For each protein, evaluate 5 predicted models (model_idx_0 ~ model_idx_4).
    Step 3: Select the model with the highest aggregate_score.
    Step 4: Copy the best model .cif file into a central directory.

Usage:
    python scripts/phase2/p2_03_select_best_models.py \
        --root-dir data/phase2/proteins \
        --out-dir results/phase2/mpox_best_models

Notes:
    - Each protein directory must contain output_<protein>_noTemplate/scores.model_idx_*.npz
    - Output directory will contain one best .cif per protein.
"""

import os
import numpy as np
import shutil
import argparse


# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Select best Chai models (highest aggregate_score).")
parser.add_argument("--root-dir", type=str, default="data/phase2/proteins",
                    help="Root folder containing protein subdirectories (default: data/phase2/proteins)")
parser.add_argument("--out-dir", type=str, default="results/phase2/mpox_best_models",
                    help="Output folder for best models (default: results/phase2/mpox_best_models)")
args = parser.parse_args()

root_dir = args.root_dir
out_dir = args.out_dir
os.makedirs(out_dir, exist_ok=True)


# === Step 2: Function to get best model index from one output folder ===
def get_best_model(output_path):
    """
    Identify the model index with the highest aggregate_score.

    Parameters:
        output_path (str): Path to Chai output folder

    Returns:
        int or None: Best model index (0–4) or None if unavailable
    """
    best_score = -float("inf")
    best_idx = None

    for i in range(5):  # model_idx_0 ~ model_idx_4
        score_file = os.path.join(output_path, f"scores.model_idx_{i}.npz")
        if not os.path.exists(score_file):
            continue
        try:
            data = np.load(score_file)
            score = float(data["aggregate_score"].item()) if "aggregate_score" in data else None
            if score is not None and score > best_score:
                best_score = score
                best_idx = i
        except Exception as e:
            print(f"[WARN] Failed to read {score_file}: {e}")

    return best_idx


# === Step 3: Traverse proteins and copy best models ===
for entry in sorted(os.listdir(root_dir)):
    entry_path = os.path.join(root_dir, entry)
    if not os.path.isdir(entry_path):
        continue

    output_path = os.path.join(entry_path, f"output_{entry}_noTemplate")
    if not os.path.isdir(output_path):
        print(f"[SKIP] No no-template output found for {entry}")
        continue

    best_idx = get_best_model(output_path)
    if best_idx is None:
        print(f"[SKIP] No valid score found for {entry}")
        continue

    src_cif = os.path.join(output_path, f"pred.model_idx_{best_idx}.cif")
    dst_cif = os.path.join(out_dir, f"{entry}.cif")

    if os.path.exists(src_cif):
        shutil.copyfile(src_cif, dst_cif)
        print(f"[OK] {entry}: best model_idx_{best_idx} copied → {dst_cif}")
    else:
        print(f"[WARN] CIF file missing for best model: {src_cif}")

print(f"\n[INFO] All best models saved to: {out_dir}")
