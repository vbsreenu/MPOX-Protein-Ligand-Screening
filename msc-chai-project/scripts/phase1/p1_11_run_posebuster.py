#!/usr/bin/env python3
"""
File: p1_11_run_posebuster.py
Description:
    Step 1: Load best_model_per_complex.tsv
    Step 2: For each best model, extract ligand from predicted structure
    Step 3: Convert ligand to .sdf (Open Babel)
    Step 4: Run PoseBuster for geometry evaluation
    Step 5: Save raw outputs and summary statistics

Usage:
    python scripts/phase1/run_posebuster.py \
        --summary results/phase1/best_model_per_complex.tsv \
        --root-dir results/phase1 \
        --out-dir results/phase1/posebuster_results

Notes:
    - Requires Biopython, Open Babel (obabel), and PoseBuster (bust)
    - Apo structures must be pre-generated using generate_all_predicted_apo_from_best_model.py
"""

import os
import re
import argparse
import pandas as pd
import subprocess
from Bio.PDB import MMCIFParser, Select, PDBIO


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Run PoseBuster on predicted complexes.")
    parser.add_argument("--summary", type=str,
                        default="results/phase1/best_model_per_complex.tsv",
                        help="Path to best_model_per_complex.tsv file.")
    parser.add_argument("--root-dir", type=str,
                        default="results/phase1",
                        help="Root directory containing complex subfolders.")
    parser.add_argument("--out-dir", type=str,
                        default="results/phase1/posebuster_results",
                        help="Output directory for PoseBuster results.")
    return parser.parse_args()


# === Step 2: Ligand selector ===
class LigandSelect(Select):
    """Keep only non-water hetero residues (ligands)."""
    def accept_residue(self, residue):
        hetfield, _, _ = residue.id
        return hetfield != " " and residue.get_resname() not in ["HOH", "WAT"]


# === Step 3: Run PoseBuster ===
def run_posebuster(summary_file: str, root_dir: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(summary_file, sep="\t")
    results = []

    for _, row in df.iterrows():
        complex_id = row["Complex"]
        mode = row["Mode"]
        model_id = row["Model"]

        subdir = f"output_{complex_id}" if mode == "with-template" else f"output_{complex_id}_noTemplate"
        cif_file = os.path.join(root_dir, complex_id, subdir, f"pred.{model_id}.cif")
        protein_file = os.path.join(root_dir, complex_id, f"{complex_id}_pred_apo_{mode.replace('-', '')}.pdb")
        ligand_pdb = os.path.join(out_dir, f"{complex_id}_{mode.replace('-', '')}_ligand.pdb")
        ligand_sdf = os.path.join(out_dir, f"{complex_id}_{mode.replace('-', '')}_ligand.sdf")

        if not os.path.exists(cif_file) or not os.path.exists(protein_file):
            print(f"[SKIP] Missing files for {complex_id} ({mode})")
            continue

        try:
            # Step 3.1: Extract ligand from CIF
            parser = MMCIFParser(QUIET=True)
            structure = parser.get_structure("model", cif_file)
            io = PDBIO()
            io.set_structure(structure)
            io.save(ligand_pdb, LigandSelect())

            if not os.path.exists(ligand_pdb) or os.path.getsize(ligand_pdb) < 200:
                print(f"[SKIP] No ligand found in {complex_id} ({mode})")
                continue

            # Step 3.2: Convert ligand PDB → SDF
            subprocess.run(["obabel", ligand_pdb, "-O", ligand_sdf], check=True)

            # Step 3.3: Run PoseBuster
            result = subprocess.run(
                ["bust", ligand_sdf, "-p", protein_file],
                capture_output=True,
                text=True
            )
            out_text = result.stdout.strip()

            # Step 3.4: Parse results
            match = re.search(r"passes\s*\((\d+)\s*/\s*(\d+)\)", out_text)
            if match:
                passed = int(match.group(1))
                total = int(match.group(2))
                pass_rate = round(passed / total, 3) if total > 0 else None
            else:
                passed = total = pass_rate = None

            if passed == total and total is not None:
                status = "FULL_PASS"
            elif passed is not None and passed > 0.8:
                status = "PARTIAL_PASS"
            else:
                status = "FAIL"

            results.append({
                "Complex": complex_id,
                "Mode": mode,
                "Status": status,
                "Passed": passed,
                "Total": total,
                "Pass_Rate": pass_rate,
                "Raw_Output": out_text
            })

            print(f"[RESULT] {complex_id} ({mode}): {status} ({passed}/{total})")

        except Exception as e:
            print(f"[ERROR] Failed {complex_id} ({mode}): {e}")

    # Step 4: Save raw PoseBuster results
    summary_out = os.path.join(out_dir, "bust_stdout_summary.tsv")
    pd.DataFrame(results).to_csv(summary_out, sep="\t", index=False)
    print(f"[INFO] Raw results saved to: {summary_out}")

    # Step 5: Save grouped statistics
    if results:
        stats = pd.DataFrame(results).groupby("Status")["Pass_Rate"].agg(
            ["count", "mean", "std", "min", "max"]).reset_index()
        stats_out = os.path.join(out_dir, "posebuster_stats.tsv")
        stats.to_csv(stats_out, sep="\t", index=False)
        print(f"[INFO] Stats saved to: {stats_out}")


# === Step 6: Main ===
def main():
    args = parse_args()
    run_posebuster(args.summary, args.root_dir, args.out_dir)


if __name__ == "__main__":
    main()
