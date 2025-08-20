#!/usr/bin/env python3
"""
File: p1_08_analyze_rmsd.py
Description:
    Step 1: Load RMSD summary from compute_rmsd_best_models.py.
    Step 2: Compare RMSD distributions between with-template and no-template predictions.
    Step 3: Perform Welch's t-test.
    Step 4: Generate publication-ready boxplot (PNG/PDF).

Usage:
    python scripts/phase1/analyze_rmsd.py \
        --rmsd-file results/phase1/best_model_rmsd_summary.tsv \
        --out-dir results/phase1

Notes:
    - Input file must have columns: Complex, Mode, Model, RMSD
"""

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Analyze RMSD results for with vs no-template predictions.")
    parser.add_argument("--rmsd-file", type=str,
                        default="results/phase1/best_model_rmsd_summary.tsv",
                        help="Path to RMSD summary file.")
    parser.add_argument("--out-dir", type=str, default="results/phase1",
                        help="Directory to save plots.")
    return parser.parse_args()


# === Step 2: Load RMSD summary ===
def load_rmsd(rmsd_file: str) -> pd.DataFrame:
    return pd.read_csv(rmsd_file, sep="\t")


# === Step 3: Statistical analysis ===
def compare_groups(df: pd.DataFrame):
    group_with = df[df["Mode"] == "with-template"]["RMSD"]
    group_no = df[df["Mode"] == "no-template"]["RMSD"]

    print("Mean RMSD by Mode:")
    print(df.groupby("Mode")["RMSD"].mean())

    t_stat, p_val = ttest_ind(group_with, group_no, equal_var=False)
    print(f"\nT-test Result: t = {t_stat:.4f}, p = {p_val:.4f}")


# === Step 4: Plotting ===
def plot_rmsd(df: pd.DataFrame, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    out_png = os.path.join(out_dir, "rmsd_comparison.png")
    out_pdf = os.path.join(out_dir, "rmsd_comparison.pdf")

    plt.figure(figsize=(6, 5))
    sns.set_style("whitegrid")

    palette = {"with-template": "#1f77b4", "no-template": "#ff7f0e"}

    sns.boxplot(
        data=df,
        x="Mode",
        y="RMSD",
        palette=palette,
        showfliers=False,
        width=0.6
    )
    sns.stripplot(
        data=df,
        x="Mode",
        y="RMSD",
        color="black",
        size=3,
        alpha=0.6
    )

    plt.xlabel("Prediction Mode", fontsize=12)
    plt.ylabel("Backbone RMSD (Å)", fontsize=12)
    plt.title("Backbone RMSD by Prediction Mode", fontsize=14, weight="bold")

    sns.despine()
    plt.tight_layout()

    plt.savefig(out_png, dpi=300)
    plt.savefig(out_pdf, dpi=300)
    plt.close()

    print(f"[OK] Plots saved: {out_png}, {out_pdf}")


# === Main ===
def main():
    args = parse_args()
    df = load_rmsd(args.rmsd_file)
    compare_groups(df)
    plot_rmsd(df, args.out_dir)


if __name__ == "__main__":
    main()
