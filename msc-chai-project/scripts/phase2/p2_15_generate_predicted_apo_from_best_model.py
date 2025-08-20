#!/usr/bin/env python3
"""
File: p2_15_generate_predicted_apo_from_best_model.py
Description:
    Step 1: Read the best_model_per_complex.tsv (Phase 2).
    Step 2: Locate the corresponding predicted structure (.cif) for each complex.
    Step 3: Remove ligands (keep only standard protein residues) and save apo PDB.

Usage:
    python scripts/phase2/p2_15_generate_predicted_apo_from_best_model.py \
        --root-dir results/phase2/analysis \
        --summary results/phase2/best_model_per_complex.tsv

Notes:
    - Input directory layout (per complex):
        results/phase2/analysis/<complex_id>/output_<complex_id}_noTemplate/pred.model_idx_*.cif
    - Apo output path:
        results/phase2/analysis/<complex_id>/<complex_id>_pred_apo.pdb
    - Requires Biopython.
"""

import os
import argparse
import pandas as pd
from Bio.PDB import MMCIFParser, PDBIO


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Generate apo PDBs (remove ligands) from best Phase 2 models.")
    parser.add_argument("--root-dir", type=str, default="results/phase2/analysis",
                        help="Root directory containing complex subfolders (default: results/phase2/analysis)")
    parser.add_argument("--summary", type=str, default="results/phase2/best_model_per_complex.tsv",
                        help="Path to best_model_per_complex.tsv (default: results/phase2/best_model_per_complex.tsv)")
    return parser.parse_args()


# === Step 2: Selection class for protein-only ===
class KeepProteinOnly:
    def accept_model(self, model):
        return True

    def accept_chain(self, chain):
        return True

    def accept_residue(self, residue):
        # Keep only standard residues (exclude HETATM/ligands/waters)
        return residue.id[0] == " "

    def accept_atom(self, atom):
        return True


# === Step 3: Main logic ===
def generate_apo_structures(root_dir: str, summary_file: str):
    df = pd.read_csv(summary_file, sep="\t")

    parser = MMCIFParser(QUIET=True)
    io = PDBIO()

    for _, row in df.iterrows():
        complex_id = row["Complex"]
        model_id = row["Model"]  # e.g., model_idx_0

        # Step 3.1: Locate predicted CIF
        output_dir = os.path.join(root_dir, complex_id, f"output_{complex_id}_noTemplate")
        cif_path = os.path.join(output_dir, f"pred.{model_id}.cif")

        if not os.path.exists(cif_path):
            print(f"[SKIP] Missing predicted CIF for {complex_id}: {cif_path}")
            continue

        # Step 3.2: Apo output path
        apo_file = os.path.join(root_dir, complex_id, f"{complex_id}_pred_apo.pdb")
        os.makedirs(os.path.dirname(apo_file), exist_ok=True)

        # Step 3.3: Load, select, and save apo
        try:
            structure = parser.get_structure(complex_id, cif_path)
            io.set_structure(structure)
            io.save(apo_file, select=KeepProteinOnly())
            print(f"[OK] Saved apo PDB → {apo_file}")
        except Exception as e:
            print(f"[ERROR] {complex_id}: {e}")


# === Step 4: Entry point ===
def main():
    args = parse_args()
    generate_apo_structures(args.root_dir, args.summary)


if __name__ == "__main__":
    main()
