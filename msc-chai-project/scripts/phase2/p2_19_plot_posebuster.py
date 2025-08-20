#!/usr/bin/env python3
"""
File: p2_19_plot_posebuster.py
Description:
    Step 1: Load PoseBuster summary (bust_stdout_summary.tsv).
    Step 2: Compute status counts and proportions.
    Step 3: Save stats table.
    Step 4: Plot pie chart and bar chart (publication-ready).

Usage:
    python scripts/phase2/p2_19_plot_posebuster.py \
        --root-dir results/phase2/analysis \
        --input-file results/phase2/analysis/posebuster_bust_sdf_stdout/bust_stdout_summary.tsv \
        --stats-file results/phase2/analysis/posebuster_bust_sdf_stdout/posebuster_stats.tsv \
        --plot-dir results/phase2/analysis/posebuster_bust_sdf_stdout/plots_pub
"""

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Visualize PoseBuster results (Phase 2).")
    parser.add_argument("--root-dir", type=str, default="results/phase2/analysis",
                        help="Root analysis directory (default: results/phase2/analysis)")
    parser.add_argument("--input-file", type=str,
                        default="results/phase2/analysis/posebuster_bust_sdf_stdout/bust_stdout_summary.tsv",
                        help="Input TSV from p2_18 (default: results/phase2/analysis/posebuster_bust_sdf_stdout/bust_stdout_summary.tsv)")
    parser.add_argument("--stats-file", type=str,
                        default="results/phase2/analysis/posebuster_bust_sdf_stdout/posebuster_stats.tsv",
                        help="Output TSV for aggregated stats (default: results/phase2/analysis/posebuster_bust_sdf_stdout/posebuster_stats.tsv)")
    parser.add_argument("--plot-dir", type=str,
                        default="results/phase2/analysis/posebuster_bust_sdf_stdout/plots_pub",
                        help="Directory to save plots (default: results/phase2/analysis/posebuster_bust_sdf_stdout/plots_pub)")
    return parser.parse_args()


# === Step 2: Load and aggregate ===
def load_and_aggregate(input_file: str) -> pd.DataFrame:
    df = pd.read_csv(input_file, sep="\t")
    df_clean = df[df["Pass_Status"] != "UNKNOWN"].copy()

    status_counts = df_clean["Pass_Status"].value_counts().reset_index()
    status_counts.columns = ["Pass_Status", "Count"]

    # Standard order/colors
    colors = {
        "FULL_PASS": "#4C78A8",
        "PARTIAL_PASS": "#F58518",
        "FAIL": "#E45756",
    }

    status_counts_sorted = (
        status_counts.set_index("Pass_Status")
        .reindex(list(colors.keys()), fill_value=0)
        .reset_index()
    )
    total = max(status_counts_sorted["Count"].sum(), 1)
    status_counts_sorted["Proportion(%)"] = (status_counts_sorted["Count"] / total * 100).round(1)
    return status_counts_sorted


# === Step 3: Save stats ===
def save_stats(stats_df: pd.DataFrame, stats_file: str):
    os.makedirs(os.path.dirname(stats_file), exist_ok=True)
    stats_df.to_csv(stats_file, sep="\t", index=False)
    print(f"[INFO] PoseBuster stats saved to: {stats_file}")


# === Step 4: Plotting ===
def plot_pie(stats_df: pd.DataFrame, plot_dir: str):
    colors = {
        "FULL_PASS": "#4C78A8",
        "PARTIAL_PASS": "#F58518",
        "FAIL": "#E45756",
    }
    plt.figure(figsize=(6, 6))
    plt.pie(
        stats_df["Count"],
        labels=stats_df["Pass_Status"],
        autopct="%1.1f%%",
        startangle=90,
        colors=[colors.get(s, "#cccccc") for s in stats_df["Pass_Status"]],
        wedgeprops={"edgecolor": "black"},
    )
    plt.title("PoseBuster Result Proportions", fontweight="bold", pad=15)
    plt.tight_layout()
    os.makedirs(plot_dir, exist_ok=True)
    plt.savefig(os.path.join(plot_dir, "posebuster_pie.png"), dpi=300, bbox_inches="tight", transparent=True)
    plt.savefig(os.path.join(plot_dir, "posebuster_pie.pdf"), bbox_inches="tight", transparent=True)
    plt.close()


def plot_bar(stats_df: pd.DataFrame, plot_dir: str):
    colors = {
        "FULL_PASS": "#4C78A8",
        "PARTIAL_PASS": "#F58518",
        "FAIL": "#E45756",
    }
    plt.figure(figsize=(6, 5))
    sns.barplot(
        data=stats_df,
        x="Pass_Status",
        y="Count",
        hue="Pass_Status",
        palette=colors,
        legend=False,
    )
    plt.xlabel("Pass Status", fontweight="bold")
    plt.ylabel("Count", fontweight="bold")
    plt.title("PoseBuster Result Counts", fontweight="bold", pad=15)
    plt.tick_params(direction="in")
    for i, row in stats_df.iterrows():
        plt.text(i, row["Count"] + 0.5, str(row["Count"]), ha="center", fontweight="bold")
    plt.tight_layout()
    os.makedirs(plot_dir, exist_ok=True)
    plt.savefig(os.path.join(plot_dir, "posebuster_bar.png"), dpi=300, bbox_inches="tight", transparent=True)
    plt.savefig(os.path.join(plot_dir, "posebuster_bar.pdf"), bbox_inches="tight", transparent=True)
    plt.close()


# === Step 5: Main ===
def main():
    args = parse_args()

    # Global style
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42
    plt.rcParams["axes.linewidth"] = 1.0
    sns.set_theme(style="whitegrid", context="talk")

    stats_df = load_and_aggregate(args.input_file)
    save_stats(stats_df, args.stats_file)
    plot_pie(stats_df, args.plot_dir)
    plot_bar(stats_df, args.plot_dir)

    print(f"[INFO] Plots saved to: {args.plot_dir}")


if __name__ == "__main__":
    main()
