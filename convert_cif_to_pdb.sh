#!/bin/bash

# Directory containing input .cif files
INPUT_DIR="/home4/2948645s/chai_project/Work/monkeypox/mpox_best_models"

# Directory to store converted .pdb files
OUTPUT_DIR="/home4/2948645s/chai_project/Work/monkeypox/mpox_best_models_pdb"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Loop through each .cif file and convert it to .pdb using obabel
for cif_file in "$INPUT_DIR"/*.cif; do
    base_name=$(basename "$cif_file" .cif)
    output_file="$OUTPUT_DIR/$base_name.pdb"
    echo "[INFO] Converting $base_name.cif -> $base_name.pdb"
    /usr/bin/obabel "$cif_file" -O "$output_file"
done

echo "All .cif files converted to .pdb in $OUTPUT_DIR"
