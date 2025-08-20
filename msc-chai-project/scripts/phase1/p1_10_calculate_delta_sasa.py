#!/usr/bin/env python3
"""
File: p1_10_calculate_delta_sasa.py
Description:
    Step 1: Load best_model_per_complex.tsv
    Step 2: For each best model, calculate solvent accessible surface area (SASA):
            - Apo (ligand removed)
            - Holo (with ligand)
    Step 3: Compute ΔSASA = SASA_apo - SASA_holo
    Step 4: Save results to a summary .tsv file

Usage:
    python scripts/phase1/calculate_delta_sasa.py \
        --summary results/phase1/best_model_per_complex.tsv \
        --root-dir results/phase1 \
        --out results/phase1/delta_sasa_biopython.tsv

Notes:
    - Requires Biopython
    - Apo structures must be pre-generated using generate_all_predicted_apo_from_best_model.py
"""

import os
import argparse
import pandas as pd
from Bio.PDB import PDBParser, MMCIFParser, ShrakeRupley


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Compute ΔSASA for apo vs holo structures.")
    parser.add_argument("--summary", type=str,
                        default="results/phase1/best_model_per_complex.tsv",
                        help="Path to best_model_per_complex.tsv file.")
    parser.add_argument("--root-dir", type=str,
                        default="results/phase1",
                        help="Root directory containing complex subfolders.")
    parser.add_argument("--out", type=str,
                        default="results/phase1/delta_sasa_biopython.tsv",
                        help="Output file path for ΔSASA results.")
    return parser.parse_args()


# === Step 2: SASA calculation ===
def compute_total_sasa(file_path: str) -> float:
    """Compute the total SASA for a structure file (.pdb or .cif)."""
    if file_path.endswith(".pdb"):
        parser = PDBParser(QUIET=True)
    elif file_path.endswith(".cif"):
        parser = MMCIFParser(QUIET=True)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

    structure = parser.get_structure("structure", file_path)

    sr = ShrakeRupley()
    sr.compute(structure, level="S")

    sasa_total = 0.0
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    if atom.sasa is not None:
                        sasa_total += atom.sasa
    return sasa_total


# === Step 3: Process best models ===
def calculate_delta_sasa(summary_file: str, root_dir: str, out_file: str):
    df = pd.read_csv(summary_file, sep="\t")
    results = []

    for _, row in df.iterrows():
        complex_id = row["Complex"]
        mode = row["Mode"]        # "with-template" or "no-template"
        model_id = row["Model"]

        # Holo: predicted complex with ligand
        subdir = f"output_{complex_id}" if mode == "with-template" else f"output_{complex_id}_noTemplate"
        holo_file = os.path.join(root_dir, complex_id, subdir, f"pred.{model_id}.cif")

        # Apo: ligand removed
        apo_file = os.path.join(root_dir, complex_id, f"{complex_id}_pred_apo_{mode.replace('-', '')}.pdb")

        if not (os.path.exists(apo_file) and os.path.exists(holo_file)):
            print(f"[WARN] Missing structure for {complex_id} ({mode})")
            continue

        try:
            sasa_apo = compute_total_sasa(apo_file)
            sasa_holo = compute_total_sasa(holo_file)
            delta_sasa = sasa_apo - sasa_holo

            results.append({
                "Complex": complex_id,
                "Mode": mode,
                "Apo_SASA": round(sasa_apo, 2),
                "Holo_SASA": round(sasa_holo, 2),
                "Delta_SASA": round(delta_sasa, 2)
            })

            print(f"[OK] {complex_id} ({mode}): ΔSASA = {delta_sasa:.2f}")

        except Exception as e:
            print(f"[ERROR] Failed for {complex_id} ({mode}): {e}")

    df_out = pd.DataFrame(results)
    df_out.to_csv(out_file, index=False, sep="\t")
    print(f"\n[INFO] ΔSASA results saved to: {out_file}")


# === Step 4: Main ===
def main():
    args = parse_args()
    calculate_delta_sasa(args.summary, args.root_dir, args.out)


if __name__ == "__main__":
    main()
