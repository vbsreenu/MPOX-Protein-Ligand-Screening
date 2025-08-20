#!/usr/bin/env bash
set -uo pipefail

# === Meta ===
# File: p1_02_run_chai_no_template.sh
# Description:
#   Step 1: Batch run Chai predictions without templates.
#   Step 2: One subfolder per complex; requires *_chai.txt as input.
#   Step 3: Save logs and track failed runs.
#
# Usage:
#   ROOT_DIR=data/phase1 \
#   bash scripts/phase1/run_chai_no_template.sh
#
# Notes:
#   - Each subfolder in ROOT_DIR should contain a *_chai.txt input file.
#   - Outputs will be written to {subfolder}/output_<name>_noTemplate.
#   - Log files and a list of failed jobs are stored in ROOT_DIR.

# === Config ===
ROOT_DIR="${ROOT_DIR:-data/phase1}"        # Root folder containing monomer subfolders
LOG_DIR="${LOG_DIR:-$ROOT_DIR/logs_no_template}" 
mkdir -p "$LOG_DIR"

echo "[INFO] Starting batch prediction WITHOUT templates..."

# === Step 1: Clean old logs ===
rm -f "$ROOT_DIR"/*_chai_run_noTemplate.log
rm -f "$ROOT_DIR"/failed_noTemplate_list.txt

# === Step 2: Loop through each subdirectory ===
for dir in "$ROOT_DIR"/*/; do
    cd "$dir" || continue

    # Step 2.1: Locate input file
    txt_file=$(ls *_chai.txt 2>/dev/null | head -n1)

    if [[ -f "$txt_file" ]]; then
        complex_name=$(basename "$dir")
        output_folder="$dir/output_${complex_name}_noTemplate"
        log_file="$LOG_DIR/${complex_name}_chai_run_noTemplate.log"

        # Step 2.2: Skip if already finished
        if ls "$output_folder"/pred.model_idx_0.cif &>/dev/null; then
            echo "[SKIP] $complex_name already predicted (no template)." | tee "$log_file"
            continue
        fi

        echo "[LOG] $(date) Running $complex_name WITHOUT templates" | tee "$log_file"

        # Step 2.3: Clean old output if not empty
        if [ -d "$output_folder" ] && [ "$(ls -A "$output_folder")" ]; then
            echo "[WARN] Cleaning old output: $output_folder" | tee -a "$log_file"
            rm -rf "$output_folder"
        fi

        # Step 2.4: Run Chai prediction
        chai-lab fold --use-msa-server --no-use-templates-server \
            "$txt_file" "$output_folder" >> "$log_file" 2>&1

        # Step 2.5: Check status
        if [[ $? -eq 0 ]]; then
            echo "[SUCCESS] $complex_name prediction completed (no templates)" | tee -a "$log_file"
        else
            echo "[ERROR] $complex_name prediction failed (no templates)" | tee -a "$log_file"
            echo "$complex_name" >> "$ROOT_DIR/failed_noTemplate_list.txt"
        fi
    fi
done

# === Step 3: Final message ===
echo "[INFO] All no-template predictions completed. Logs in $LOG_DIR"
