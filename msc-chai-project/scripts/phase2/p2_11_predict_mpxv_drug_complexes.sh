#!/usr/bin/env bash
set -euo pipefail

# === Meta ===
# File: p2_11_predict_mpxv_drug_complexes.sh
# Description:
#   Step 1: Load Mpox protein–drug mappings and SMILES.
#   Step 2: For each Mpox protein–drug pair, generate combined input (.fa).
#   Step 3: Run Chai predictions for protein–ligand complexes.
#
# Usage:
#   BASE_DIR=data/phase2 \
#   bash scripts/phase2/p2_11_predict_mpxv_drug_complexes.sh
#
# Notes:
#   - CSV_MAPPING: protein–drug pairs with e-value filtering.
#   - CSV_SMILES: DrugBank → SMILES lookup table.
#   - Each combination result saved in: <BASE_DIR>/<protein>/<drug_id>/output_<combo_name>_chai

# === Config ===
BASE_DIR="${BASE_DIR:-data/phase2}"
CSV_MAPPING="$BASE_DIR/uniprot_with_drugbank_filtered.csv"
CSV_SMILES="$BASE_DIR/unique_drugs.csv"

# === Step 1: Load DrugBank → SMILES map into associative array ===
declare -A DRUG_SMILES
while IFS=',' read -r drugbank_id smiles; do
    [[ "$drugbank_id" == "DrugBank_ID" ]] && continue
    DRUG_SMILES["$(echo "$drugbank_id" | xargs)"]="$(echo "$smiles" | xargs)"
done < "$CSV_SMILES"

# === Step 2: Cleanup previous runs (remove old drug folders) ===
echo "[INFO] Cleaning previous drug folders..."
for prot_dir in "$BASE_DIR"/*/; do
    find "$prot_dir" -mindepth 1 -maxdepth 1 -type d -name "DB*" -exec rm -rf {} +
done

# === Step 3: Loop through protein–drug mappings ===
tail -n +2 "$CSV_MAPPING" | while IFS=',' read -r query_protein hit_id uniprot db evalue drugbank_ids; do
    query_protein=$(echo "$query_protein" | xargs)
    fasta_path="$BASE_DIR/$query_protein/${query_protein}_protein.fa"

    # Step 3.1: Validate FASTA file exists
    if [[ ! -f "$fasta_path" ]]; then
        echo "[WARN] Missing FASTA: $fasta_path"
        continue
    fi
    protein_seq=$(grep -v "^>" "$fasta_path" | tr -d '\n')

    # Step 3.2: Process all associated DrugBank IDs
    IFS=';' read -ra drug_list <<< "$drugbank_ids"
    for drug_id in "${drug_list[@]}"; do
        drug_id=$(echo "$drug_id" | xargs)
        smiles="${DRUG_SMILES[$drug_id]:-}"

        if [[ -z "$smiles" ]]; then
            echo "[WARN] No SMILES for $drug_id"
            continue
        fi

        combo_name="${query_protein}+${drug_id}"
        combo_dir="$BASE_DIR/$query_protein/$drug_id"
        out_dir="$combo_dir/output_${combo_name}_chai"
        combined_fa="$combo_dir/combined_input.fa"

        # Step 3.3: Skip if already predicted
        if [[ -d "$out_dir" && -n "$(ls -A "$out_dir" 2>/dev/null)" ]]; then
            echo "[SKIP] Already done: $combo_name"
            continue
        fi

        mkdir -p "$combo_dir"

        # Step 3.4: Build Chai input file
        {
            echo ">protein|${query_protein}_protein"
            echo "$protein_seq"
            echo ">ligand|${drug_id}_ligand"
            echo "$smiles"
        } > "$combined_fa"

        # Step 3.5: Run Chai prediction
        echo "[RUNNING] $combo_name"
        if chai-lab fold "$combined_fa" "$out_dir" --low-memory --use-msa-server --no-use-templates-server; then
            echo "[SUCCESS] $combo_name"
        else
            echo "[ERROR] Failed: $combo_name"
        fi
    done
done
