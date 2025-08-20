#!/usr/bin/env bash
set -euo pipefail

# === Meta ===
# File: p1_06_download_pdb_complexes.sh
# Description:
#   Step 1: Download reference PDB complexes (with ligands) from RCSB PDB.
#   Step 2: One subdirectory per PDB ID (lowercase), download file into each folder.
#
# Usage:
#   BASE_DIR=data/phase1 bash scripts/phase1/download_pdb_complexes.sh
#
# Notes:
#   - Each subdirectory under BASE_DIR should be named as the PDB ID (lowercase).
#   - Downloads files from https://files.rcsb.org/download/{PDB}.pdb1.gz
#   - Saves decompressed file as {pdbid}_complex.pdb inside the subfolder.

# === Config ===
BASE_DIR="${BASE_DIR:-data/phase1}"    # Root directory containing PDB subfolders

# === Step 1: Loop over all PDB IDs ===
for pdbid in $(ls -d "${BASE_DIR}"/*/ | xargs -n1 basename); do
    PDB_UPPER=$(echo "$pdbid" | tr '[:lower:]' '[:upper:]')
    URL="https://files.rcsb.org/download/${PDB_UPPER}.pdb1.gz"
    TARGET_DIR="${BASE_DIR}/${pdbid}"
    OUTPUT_FILE="${TARGET_DIR}/${pdbid}_complex.pdb"

    echo "[INFO] Downloading $PDB_UPPER from RCSB..."

    # Step 2: Fetch and decompress
    if wget -q -O - "$URL" | gunzip > "$OUTPUT_FILE"; then
        echo "[OK] Saved to $OUTPUT_FILE"
    else
        echo "[ERROR] Failed to download $PDB_UPPER"
        rm -f "$OUTPUT_FILE"
    fi
done
