#!/usr/bin/env bash
set -euo pipefail

# === Meta ===
# File: p2_02_run_chai_batch_mpxv_no_template.sh
# Description:
#   Step 1: Loop over all monkeypox protein input folders.
#   Step 2: Run Chai predictions WITHOUT templates (--no-use-templates-server).
#   Step 3: Save outputs to subdirectories and log files.
#
# Usage:
#   ROOT_DIR=data/phase2/proteins \
#   LOG_DIR=logs/phase2/no_template \
#   bash scripts/phase2/p2_02_run_chai_batch_mpxv_no_template.sh
#
# Notes:
#   - Each subdirectory in ROOT_DIR must contain *_input.txt (protein sequence).
#   - Outputs are written to output_<protein>_noTemplate/.
#   - Failed runs are recorded in failed_noTemplate_list.txt.

# === Config ===
ROOT_DIR="${ROOT_DIR:-data/phase2/proteins}"     # Root folder containing protein subdirectories
LOG_DIR="${LOG_DIR:-logs/phase2/no_template}"    # Directory for logs
mkdir -p "$LOG_DIR"

FAILED_LIST="$ROOT_DIR/failed_noTemplate_list.txt"
rm -f "$FAILED_LIST"

echo "[INFO] Starting batch prediction WITHOUT templates for monkeypox proteins..."

# === Step 1: Loop through each protein subdirectory ===
for dir in "$ROOT_DIR"/*/; do
    cd "$dir" || continue

    # Step 1.1: Locate input file
    txt_file=$(ls *_input.txt 2>/dev/null | head -n1)
    if [[ ! -f "$txt_file" ]]; then
        echo "[WARN] No input file found in $dir"
        continue
    fi

    # Step 1.2: Define paths
    complex_name=$(basename "$dir")
    output_folder="$dir/output_${complex_name}_noTemplate"
    log_file="$LOG_DIR/${complex_name}_chai_run_noTemplate.log"

    # Step 1.3: Skip if already predicted
    if ls "$output_folder"/pred.model_idx_0.cif &>/dev/null; then
        echo "[SKIP] $complex_name already predicted (no template)." | tee "$log_file"
        continue
    fi

    echo "[LOG] $(date) Running $complex_name WITHOUT templates" | tee "$log_file"

    # Step 2: Clean old output if exists
    if [ -d "$output_folder" ] && [ "$(ls -A "$output_folder")" ]; then
        echo "[WARN] Cleaning old output: $output_folder" | tee -a "$log_file"
        rm -rf "$output_folder"
    fi

    # Step 3: Run Chai prediction
    if chai-lab fold --use-msa-server --no-use-templates-server "$txt_file" "$output_folder" >> "$log_file" 2>&1; then
        echo "[SUCCESS] $complex_name prediction completed (no templates)" | tee -a "$log_file"
    else
        echo "[ERROR] $complex_name prediction failed (no templates)" | tee -a "$log_file"
        echo "$complex_name" >> "$FAILED_LIST"
    fi
done

echo "[INFO] All no-template predictions completed. Logs saved in $LOG_DIR"