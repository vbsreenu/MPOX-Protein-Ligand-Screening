#!/usr/bin/env bash
set -euo pipefail

# === Meta ===
# File: p2_04_convert_cif_to_pdb.sh
# Description:
#   Step 1: Convert all best model .cif files into .pdb format using Open Babel.
#   Step 2: Store converted .pdb files in a separate output directory.
#
# Usage:
#   INPUT_DIR=data/phase2/mpox_best_models \
#   OUTPUT_DIR=results/phase2/mpox_best_models_pdb \
#   OBABEL=/usr/bin/obabel \
#   bash scripts/phase2/p2_04_convert_cif_to_pdb.sh
#
# Notes:
#   - INPUT_DIR must contain .cif files (best models).
#   - OBABEL should be installed and available in PATH or specified explicitly.

# === Config ===
INPUT_DIR="${INPUT_DIR:-data/phase2/mpox_best_models}"           # Input directory with .cif files
OUTPUT_DIR="${OUTPUT_DIR:-results/phase2/mpox_best_models_pdb}"  # Output directory for .pdb files
OBABEL="${OBABEL:-obabel}"                                       # Open Babel executable
mkdir -p "$OUTPUT_DIR"

# === Step 1: Loop through .cif files and convert ===
for cif_file in "$INPUT_DIR"/*.cif; do
    base_name=$(basename "$cif_file" .cif)
    output_file="$OUTPUT_DIR/$base_name.pdb"

    echo "[INFO] Converting $base_name.cif → $base_name.pdb"
    "$OBABEL" "$cif_file" -O "$output_file"
done

# === Step 2: Final message ===
echo "[INFO] All .cif files converted to .pdb in $OUTPUT_DIR"
