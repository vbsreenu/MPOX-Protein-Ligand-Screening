#!/usr/bin/env bash
set -euo pipefail

# === Meta ===
# File: p1_01_generate_inputs.sh
# Description:
#   Step 1: Prepare Chai-1 input files from protein PDB and ligand SDF.
#   Step 2: Generate FASTA (.fa), SMILES (.smi), and Chai-1 input (.txt) files.
#   Step 3: Save logs for each processed monomer.
#
# Usage:
#   ROOT_DIR=data/phase1 \
#   PDB2FASTA=/path/to/pdb2fasta \
#   OBABEL=/path/to/obabel \
#   bash scripts/phase1/generate_chai_inputs.sh
#
# Notes:
#   - ROOT_DIR should contain one subdirectory per monomer with *_protein.pdb and *_ligand.sdf.
#   - PDB2FASTA and OBABEL paths must be set or available in PATH.

# === Config ===
ROOT_DIR="${ROOT_DIR:-data/phase1}"       # Root directory containing monomer subfolders
PDB2FASTA="${PDB2FASTA:-pdb2fasta}"       # Tool to convert PDB → FASTA
OBABEL="${OBABEL:-obabel}"                # Open Babel tool for SDF → SMILES
LOG_DIR="${LOG_DIR:-logs/phase1}"         # Directory for logs
mkdir -p "$LOG_DIR"

# === Step 1: Loop through each monomer subdirectory ===
for dir in "$ROOT_DIR"/*/; do
    (
        cd "$dir" || exit 1

        # Step 1.1: Locate structure files
        pdb_file=$(ls *_protein.pdb 2>/dev/null | head -n1)
        sdf_file=$(ls *_ligand.sdf 2>/dev/null | head -n1)

        # Step 1.2: Check required files exist
        if [[ -f "$pdb_file" && -f "$sdf_file" ]]; then
            base=$(basename "$pdb_file" _protein.pdb)
            fa_file="${base}_protein.fa"
            smi_file="${base}_ligand.smi"
            txt_file="${base}_chai.txt"

            echo "[INFO] Processing $base..."

            # Step 2: Generate FASTA file from PDB
            "$PDB2FASTA" "$pdb_file" > "$fa_file"

            # Step 3: Convert ligand SDF → SMILES
            "$OBABEL" -i sdf "$sdf_file" -o smi -O "$smi_file"

            # Step 4: Build Chai input file (.txt) in required FASTA+SMILES format for Chai-1
            > "$txt_file"

            # Step 4.1: Add protein sequence(s)
            awk -v base="$base" '
                BEGIN { i=1 }
                /^>/ {
                    print ">protein|" base "_protein_chain" i
                    i++
                    next
                }
                { print }
            ' "$fa_file" >> "$txt_file"

            # Step 4.2: Add ligand SMILES
            echo ">ligand|${base}_ligand" >> "$txt_file"
            cut -f1 "$smi_file" >> "$txt_file"

            echo "[DONE] Created $txt_file"
        else
            echo "[WARN] Missing *_protein.pdb or *_ligand.sdf in $dir"
        fi
    ) &> "$LOG_DIR/$(basename "$dir").log"
done

# === Step 2: Final message ===
echo "All processing complete. Logs saved in $LOG_DIR."
