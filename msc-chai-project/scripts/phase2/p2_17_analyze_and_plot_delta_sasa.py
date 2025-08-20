#!/usr/bin/env python3
"""
File: p2_17_analyze_and_plot_delta_sasa.py
Description:
    Step 1: Load ΔSASA table and best-model scores.
    Step 2: Merge tables and compute descriptive statistics.
    Step 3: Plot ΔSASA distribution (hist + KDE).
    Step 4: Plot correlations (ΔSASA vs AggregateScore / pTM) with regression line.
    Step 5: Plot Positive vs Negative ΔSASA boxplot + jitter.
    Step 6: Save stats TSV and publication-ready figures.

Usage:
    python scripts/phase2/p2_17_analyze_and_plot_delta_sasa.py \
        --root-dir results/phase2/analysis \
        --sasa-file results/phase2/analysis/delta_sasa_biopython.tsv \
        --score-file results/phase2/analysis/best_model_per_complex.tsv \
        --stats-out results/phase2/analysis/delta_sasa_stats.tsv \
        --plot-dir results/phase2/analysis/plots_pub

Notes:
    - Required inputs:
        delta_sasa_biopython.tsv  (columns: Complex, Apo_SASA, Holo_SASA, Delta_SASA)
        best_model_per_complex.tsv (columns include: Complex, AggregateScore, pTM)
    - Outputs:
        delta_sasa_stats.tsv
        plots_pub/delta_sasa_distribution.(png|pdf)
        plots_pub/delta_sasa_vs_aggregate.(png|pdf)
        plots_pub/delta_sasa_vs_ptm.(png|pdf)
        plots_pub/delta_sasa_boxplot.(png|pdf)
"""

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Analyze and plot ΔSASA for Phase 2 best models.")
    parser.add_argument("--root-dir", type=str, default="results/phase2/analysis",
                        help="Root analysis directory (default: results/phase2/analysis)")
    parser.add_argument("--sasa-file", type=str, default="results/phase2/analysis/delta_sasa_biopython.tsv",
                        help="ΔSASA TSV path (default: results/phase2/analysis/delta_sasa_biopython.tsv)")
    parser.add_argument("--score-file", type=str, default="results/phase2/analysis/best_model_per_complex.tsv",
                        help="Best model score TSV path (default: results/phase2/analysis/best_model_per_complex.tsv)")
    parser.add_argument("--stats-out", type=str, default="results/phase2/analysis/delta_sasa_stats.tsv",
                        help="Output TSV for summary stats (default: results/phase2/analysis/delta_sasa_stats.tsv)")
    parser.add_argument("--plot-dir", type=str, default="results/phase2/analysis/plots_pub",
                        help="Directory to save plots (default: results/phase2/analysis/plots_pub)")
    return parser.parse_args()


# === Step 2: Compute descriptive statistics ===
def compute_stats(df: pd.DataFrame) -> pd.DataFrame:
    total_count = len(df)
    mean_val = df["Delta_SASA"].mean()
    median_val = df["Delta_SASA"].median()
    min_val = df["Delta_SASA"].min()
    max_val = df["Delta_SASA"].max()
    std_val = df["Delta_SASA"].std()
    neg_count = (df["Delta_SASA"] < 0).sum()
    neg_ratio = neg_count / total_count * 100 if total_count > 0 else 0.0

    stats_df = pd.DataFrame([{
        "Total": total_count,
        "Mean": round(mean_val, 2),
        "Median": round(median_val, 2),
        "Min": round(min_val, 2),
        "Max": round(max_val, 2),
        "Std": round(std_val, 2),
        "Negative_Count": int(neg_count),
        "Negative_Ratio(%)": round(neg_ratio, 2),
    }])
    return stats_df


# === Step 3: Plot helpers ===
def plot_distribution(df: pd.DataFrame, plot_dir: str):
    plt.figure(figsize=(7, 5))
    sns.histplot(df["Delta_SASA"], bins=20, kde=True, color="#1f77b4",
                 edgecolor="black", alpha=0.8)
    plt.axvline(0, color="#d62728", linestyle="--", linewidth=1.5)
    plt.xlabel("ΔSASA (Å²)", fontweight="bold")
    plt.ylabel("Count", fontweight="bold")
    plt.title("Distribution of ΔSASA", fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "delta_sasa_distribution.png"), dpi=300)
    plt.savefig(os.path.join(plot_dir, "delta_sasa_distribution.pdf"))
    plt.close()


def plot_scatter_with_corr(df: pd.DataFrame, x: str, y: str,
                           xlabel: str, ylabel: str, filename: str,
                           plot_dir: str):
    # remove rows with NaNs in x or y
    sub = df[[x, y]].dropna()
    if len(sub) == 0:
        return
    pearson_corr, _ = pearsonr(sub[x], sub[y])
    spearman_corr, _ = spearmanr(sub[x], sub[y])

    plt.figure(figsize=(7, 5))
    sns.regplot(data=sub, x=x, y=y,
                scatter_kws={"s": 40, "alpha": 0.7},
                line_kws={"color": "red"},
                color="#1f77b4")
    plt.xlabel(xlabel, fontweight="bold")
    plt.ylabel(ylabel, fontweight="bold")
    plt.title(f"{ylabel} vs {xlabel}\nPearson={pearson_corr:.2f}, Spearman={spearman_corr:.2f}",
              fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, f"{filename}.png"), dpi=300)
    plt.savefig(os.path.join(plot_dir, f"{filename}.pdf"))
    plt.close()


def plot_pos_neg_box(df: pd.DataFrame, plot_dir: str):
    df = df.copy()
    df["DeltaSASA_sign"] = df["Delta_SASA"].apply(lambda x: "Negative" if x < 0 else "Positive")

    plt.figure(figsize=(6, 5))
    sns.boxplot(data=df, x="DeltaSASA_sign", y="Delta_SASA",
                hue="DeltaSASA_sign",
                palette={"Positive": "#1f77b4", "Negative": "#ff7f0e"},
                legend=False)
    sns.stripplot(data=df, x="DeltaSASA_sign", y="Delta_SASA",
                  color="black", size=3, jitter=True, alpha=0.5)
    plt.xlabel("ΔSASA Sign", fontweight="bold")
    plt.ylabel("ΔSASA (Å²)", fontweight="bold")
    plt.title("Positive vs Negative ΔSASA", fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(plot_dir, "delta_sasa_boxplot.png"), dpi=300)
    plt.savefig(os.path.join(plot_dir, "delta_sasa_boxplot.pdf"))
    plt.close()


# === Step 4: Main ===
def main():
    args = parse_args()

    # Step 4.1: Load data
    os.makedirs(args.plot_dir, exist_ok=True)
    df_sasa = pd.read_csv(args.sasa_file, sep="\t")
    df_score = pd.read_csv(args.score_file, sep="\t")

    # Step 4.2: Merge ΔSASA with scores
    df = pd.merge(df_sasa, df_score[["Complex", "AggregateScore", "pTM"]],
                  on="Complex", how="left")

    # Step 4.3: Stats
    stats_df = compute_stats(df)
    os.makedirs(os.path.dirname(args.stats_out), exist_ok=True)
    stats_df.to_csv(args.stats_out, sep="\t", index=False)

    # Step 4.4: Style
    sns.set_theme(style="whitegrid")
    sns.set_context("talk", font_scale=1.1)

    # Step 4.5: Plots
    plot_distribution(df, args.plot_dir)
    plot_scatter_with_corr(df, "AggregateScore", "Delta_SASA",
                           "Aggregate Score", "ΔSASA (Å²)",
                           "delta_sasa_vs_aggregate", args.plot_dir)
    plot_scatter_with_corr(df, "pTM", "Delta_SASA",
                           "pTM Score", "ΔSASA (Å²)",
                           "delta_sasa_vs_ptm", args.plot_dir)
    plot_pos_neg_box(df, args.plot_dir)

    print(f"[INFO] Stats saved to: {args.stats_out}")
    print(f"[INFO] Publication-ready plots saved to: {args.plot_dir}")


if __name__ == "__main__":
    main()
