#!/usr/bin/env bash
set -uo pipefail

# === Meta ===
# File: p1_03_run_chai_with_template.sh
# Description:
#   Step 1: Batch run Chai predictions with templates enabled.
#   Step 2: One subfolder per complex; requires *_chai.txt as input.
#   Step 3: Save logs for each prediction.
#
# Usage:
#   ROOT_DIR=data/phase1 \
#   bash scripts/phase1/run_chai_with_template.sh
#
# Notes:
#   - Each subfolder in ROOT_DIR should contain a *_chai.txt input file.
#   - Outputs will be written to {subfolder}/output_<name>.
#   - Log files are stored in ROOT_DIR.
#   - chai-lab must be in PATH.

# === Config ===
ROOT_DIR="${ROOT_DIR:-data/phase1}"        # Root folder containing monomer subfolders
LOG_DIR="${LOG_DIR:-$ROOT_DIR/logs}" 
mkdir -p "$LOG_DIR"

echo "[INFO] Using chai-lab from PATH: $(which chai-lab || echo 'not found')"
echo "[INFO] Starting batch prediction WITH templates..."

# === Step 1: Clean old logs ===
find "$ROOT_DIR" -maxdepth 1 -name "*_chai_run.log" -exec rm -f {} \;

# === Step 2: Loop through each subdirectory ===
for dir in "$ROOT_DIR"/*/; do
    cd "$dir" || continue

    # Step 2.1: Locate input file
    txt_file=$(ls *_chai.txt 2>/dev/null | head -n1)

    if [[ -f "$txt_file" ]]; then
        complex_name=$(basename "$dir")
        output_folder="$dir/output_${complex_name}"
        log_file="$LOG_DIR/${complex_name}_chai_run.log"

        # Step 2.2: Skip if already finished
        if ls "$output_folder"/pred.model_idx_0.cif &>/dev/null; then
            echo "[SKIP] $(date) $complex_name already predicted (with template)." | tee "$log_file"
            continue
        fi

        echo "[LOG] $(date) Running $complex_name WITH templates" | tee "$log_file"

        # Step 2.3: Run Chai prediction
        chai-lab fold --use-msa-server --use-templates-server \
            "$txt_file" "$output_folder" >> "$log_file" 2>&1

        # Step 2.4: Check status
        if [[ $? -eq 0 ]]; then
            echo "[SUCCESS] $(date) $complex_name prediction completed (with template)." | tee -a "$log_file"
        else
            echo "[ERROR] $(date) $complex_name prediction failed (with template)." | tee -a "$log_file"
        fi
    fi
done

# === Step 3: Final message ===
echo "[INFO] All with-template predictions completed. Logs in $LOG_DIR"
