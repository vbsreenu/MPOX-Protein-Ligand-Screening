#!/usr/bin/env python3
"""
File: p2_16_calculate_delta_sasa.py
Description:
    Step 1: Read best_model_per_complex.tsv (Phase 2).
    Step 2: For each complex, compute SASA for apo (PDB) and holo (CIF).
    Step 3: Calculate ΔSASA = SASA_apo - SASA_holo and save to TSV.

Usage:
    python scripts/phase2/p2_16_calculate_delta_sasa.py \
        --root-dir results/phase2/analysis \
        --summary results/phase2/best_model_per_complex.tsv \
        --out-file results/phase2/delta_sasa_biopython.tsv

Notes:
    - Expected files per complex:
        results/phase2/analysis/<complex_id>/output_<complex_id>_noTemplate/pred.<model_id>.cif  (holo)
        results/phase2/analysis/<complex_id>/<complex_id>_pred_apo.pdb                            (apo)
    - Output columns: Complex, Apo_SASA, Holo_SASA, Delta_SASA
"""

import os
import argparse
import pandas as pd
from Bio.PDB import PDBParser, MMCIFParser, ShrakeRupley


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Compute ΔSASA (apo - holo) for Phase 2 best models.")
    parser.add_argument("--root-dir", type=str, default="results/phase2/analysis",
                        help="Root directory containing complex subfolders (default: results/phase2/analysis)")
    parser.add_argument("--summary", type=str, default="results/phase2/best_model_per_complex.tsv",
                        help="Path to best_model_per_complex.tsv (default: results/phase2/best_model_per_complex.tsv)")
    parser.add_argument("--out-file", type=str, default="results/phase2/delta_sasa_biopython.tsv",
                        help="Output TSV file (default: results/phase2/delta_sasa_biopython.tsv)")
    return parser.parse_args()


# === Step 2: SASA computation ===
def compute_total_sasa(file_path: str) -> float:
    """Compute total SASA for a structure file (.pdb or .cif)."""
    if file_path.endswith(".pdb"):
        parser = PDBParser(QUIET=True)
    elif file_path.endswith(".cif"):
        parser = MMCIFParser(QUIET=True)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    structure = parser.get_structure("structure", file_path)
    sr = ShrakeRupley()
    sr.compute(structure, level="S")

    sasa_total = 0.0
    for model in structure:
        for chain in model:
            for residue in chain:
                for atom in residue:
                    if getattr(atom, "sasa", None) is not None:
                        sasa_total += atom.sasa
    return sasa_total


# === Step 3: Main ===
def main():
    args = parse_args()
    root_dir = args.root_dir
    summary_file = args.summary
    out_file = args.out_file

    df = pd.read_csv(summary_file, sep="\t")
    results = []

    for _, row in df.iterrows():
        complex_id = row["Complex"]
        model_id = row["Model"]

        holo_file = os.path.join(root_dir, complex_id,
                                 f"output_{complex_id}_noTemplate",
                                 f"pred.{model_id}.cif")
        apo_file = os.path.join(root_dir, complex_id, f"{complex_id}_pred_apo.pdb")

        if not (os.path.exists(apo_file) and os.path.exists(holo_file)):
            print(f"[WARN] Missing structure for {complex_id}")
            continue

        try:
            sasa_apo = compute_total_sasa(apo_file)
            sasa_holo = compute_total_sasa(holo_file)
            delta_sasa = sasa_apo - sasa_holo

            results.append({
                "Complex": complex_id,
                "Apo_SASA": round(sasa_apo, 2),
                "Holo_SASA": round(sasa_holo, 2),
                "Delta_SASA": round(delta_sasa, 2),
            })
            print(f"[INFO] {complex_id}: ΔSASA = {delta_sasa:.2f}")
        except Exception as e:
            print(f"[ERROR] Failed to process {complex_id}: {e}")

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    pd.DataFrame(results).to_csv(out_file, index=False, sep="\t")
    print(f"\n[INFO] SASA results saved to: {out_file}")


if __name__ == "__main__":
    main()
