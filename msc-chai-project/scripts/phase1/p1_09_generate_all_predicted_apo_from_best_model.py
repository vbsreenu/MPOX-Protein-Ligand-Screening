#!/usr/bin/env python3
"""
File: p1_09_generate_all_predicted_apo_from_best_model.py
Description:
    Step 1: Read the best_model_per_complex.tsv file.
    Step 2: Locate the corresponding predicted structure (best model).
    Step 3: Remove ligands and save apo-only protein structures as PDB.

Usage:
    python scripts/phase1/generate_all_predicted_apo_from_best_model.py \
        --summary results/phase1/best_model_per_complex.tsv \
        --root-dir results/phase1

Notes:
    - Requires Biopython
    - Input: best_model_per_complex.tsv + predicted model .cif files
    - Output: *_pred_apo_*.pdb files (apo form without ligands)
"""

import os
import argparse
import pandas as pd
from Bio.PDB import MMCIFParser, PDBIO


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Generate apo structures (remove ligands) from best models.")
    parser.add_argument("--summary", type=str,
                        default="results/phase1/best_model_per_complex.tsv",
                        help="Path to best_model_per_complex.tsv file.")
    parser.add_argument("--root-dir", type=str,
                        default="results/phase1",
                        help="Root directory containing complex subfolders.")
    return parser.parse_args()


# === Step 2: Selection class for protein-only filtering ===
class KeepProteinOnly:
    def accept_model(self, model):
        return True

    def accept_chain(self, chain):
        return True

    def accept_residue(self, residue):
        # Keep only standard protein residues (exclude HETATM/ligands/water)
        return residue.id[0] == " "

    def accept_atom(self, atom):
        return True


# === Step 3: Process each entry ===
def generate_apo_structures(summary_file: str, root_dir: str):
    df = pd.read_csv(summary_file, sep="\t")

    parser = MMCIFParser(QUIET=True)
    io = PDBIO()

    for _, row in df.iterrows():
        complex_id = row["Complex"]
        mode = row["Mode"]          # "with-template" or "no-template"
        model_id = row["Model"]     # e.g., model_idx_0

        # Path to predicted structure file (.cif)
        output_dir = os.path.join(
            root_dir,
            complex_id,
            f"output_{complex_id}" if mode == "with-template" else f"output_{complex_id}_noTemplate"
        )
        cif_path = os.path.join(output_dir, f"pred.{model_id}.cif")

        if not os.path.exists(cif_path):
            print(f"[SKIP] Missing predicted file for {complex_id} ({mode}): {cif_path}")
            continue

        # Output path for apo PDB file
        apo_file = os.path.join(root_dir, complex_id,
                                f"{complex_id}_pred_apo_{mode.replace('-', '')}.pdb")

        try:
            structure = parser.get_structure(complex_id, cif_path)

            io.set_structure(structure)
            io.save(apo_file, select=KeepProteinOnly())
            print(f"[OK] Saved apo structure: {apo_file}")

        except Exception as e:
            print(f"[ERROR] Failed to process {complex_id} ({mode}): {e}")


# === Step 4: Main ===
def main():
    args = parse_args()
    generate_apo_structures(args.summary, args.root_dir)


if __name__ == "__main__":
    main()
