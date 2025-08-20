#!/usr/bin/env python3
"""
File: p1_07_compute_rmsd_best_models.py
Description:
    Step 1: Load the best model per complex (from select_best_models.py).
    Step 2: For each (Complex, Mode), compute CA-atom backbone RMSD
            against the experimental reference structure.
    Step 3: Save results into a summary TSV.

Usage:
    python scripts/phase1/compute_rmsd_best_models.py \
        --root-dir data/phase1 \
        --summary-file results/phase1/best_model_per_complex.tsv \
        --out-file results/phase1/best_model_rmsd_summary.tsv

Notes:
    - Requires Biopython
    - Reference file: {complex_id}_complex.pdb (from RCSB download)
    - Predicted file: pred.<Model>.cif (from Chai output)
"""

import os
import argparse
import warnings
import pandas as pd
from Bio.PDB import PDBParser, MMCIFParser, Superimposer

warnings.filterwarnings("ignore", category=UserWarning)


# === Step 1: Structure loading ===
def load_structure(file_path: str, structure_id: str):
    """Load a PDB or mmCIF file into a Biopython Structure."""
    if file_path.endswith(".pdb"):
        parser = PDBParser(QUIET=True)
    elif file_path.endswith(".cif"):
        parser = MMCIFParser(QUIET=True)
    else:
        raise ValueError(f"Unsupported format: {file_path}")
    return parser.get_structure(structure_id, file_path)


def get_ca_atoms(structure):
    """Extract all CA atoms from all residues."""
    return [residue["CA"]
            for model in structure
            for chain in model
            for residue in chain
            if "CA" in residue]


def calculate_rmsd(ref_pdb: str, model_path: str) -> float:
    """Superimpose on CA atoms and compute RMSD."""
    ref_structure = load_structure(ref_pdb, "ref")
    model_structure = load_structure(model_path, "model")

    ref_atoms = get_ca_atoms(ref_structure)
    model_atoms = get_ca_atoms(model_structure)

    min_len = min(len(ref_atoms), len(model_atoms))
    ref_atoms = ref_atoms[:min_len]
    model_atoms = model_atoms[:min_len]

    super_imposer = Superimposer()
    super_imposer.set_atoms(ref_atoms, model_atoms)
    super_imposer.apply(model_structure.get_atoms())

    return super_imposer.rms


# === Step 2: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Compute RMSD for best models.")
    parser.add_argument("--root-dir", type=str, default="data/phase1",
                        help="Root directory containing complex subfolders.")
    parser.add_argument("--summary-file", type=str,
                        default="results/phase1/best_model_per_complex.tsv",
                        help="TSV file with best model per complex.")
    parser.add_argument("--out-file", type=str,
                        default="results/phase1/best_model_rmsd_summary.tsv",
                        help="Output TSV file with RMSD results.")
    return parser.parse_args()


# === Step 3: Main ===
def main():
    args = parse_args()

    df = pd.read_csv(args.summary_file, sep="\t")

    os.makedirs(os.path.dirname(args.out_file), exist_ok=True)
    with open(args.out_file, "w") as out:
        out.write("Complex\tMode\tModel\tRMSD\n")

        for _, row in df.iterrows():
            complex_id, mode, model_name = row["Complex"], row["Mode"], row["Model"]

            ref_pdb = os.path.join(args.root_dir, complex_id, f"{complex_id}_complex.pdb")

            if not os.path.isfile(ref_pdb):
                print(f"[SKIP] Missing reference: {ref_pdb}")
                continue

            if mode == "with-template":
                model_path = os.path.join(args.root_dir, complex_id,
                                          f"output_{complex_id}", f"pred.{model_name}.cif")
            else:
                model_path = os.path.join(args.root_dir, complex_id,
                                          f"output_{complex_id}_noTemplate", f"pred.{model_name}.cif")

            if not os.path.isfile(model_path):
                print(f"[WARN] Missing predicted model: {model_path}")
                continue

            try:
                rmsd = calculate_rmsd(ref_pdb, model_path)
                out.write(f"{complex_id}\t{mode}\t{model_name}\t{rmsd:.4f}\n")
            except Exception as e:
                print(f"[ERROR] RMSD failed for {complex_id} {mode}: {e}")
                continue

    print(f"[OK] RMSD summary saved to: {args.out_file}")


if __name__ == "__main__":
    main()
