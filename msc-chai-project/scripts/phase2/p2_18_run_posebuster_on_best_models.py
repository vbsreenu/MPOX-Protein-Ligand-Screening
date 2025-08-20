#!/usr/bin/env python3
"""
File: p2_18_run_posebuster_on_best_models.py
Description:
    Step 1: Read best_model_per_complex.tsv.
    Step 2: For each complex, extract ligand atoms from predicted CIF.
    Step 3: Convert ligand PDB → SDF (Open Babel).
    Step 4: Run PoseBuster `bust` to check ligand geometry.
    Step 5: Parse output (pass/fail counts) and classify results.
    Step 6: Save results summary to TSV.

Usage:
    python scripts/phase2/p2_18_run_posebuster_on_best_models.py \
        --root-dir results/phase2/analysis \
        --summary-file results/phase2/analysis/best_model_per_complex.tsv \
        --out-dir results/phase2/analysis/posebuster_bust_sdf_stdout

Outputs:
    - {out-dir}/{complex_id}_ligand.{pdb,sdf}
    - bust_stdout_summary.tsv
"""

import os
import re
import argparse
import pandas as pd
import subprocess
from Bio.PDB import MMCIFParser, Select, PDBIO


# === Step 1: CLI ===
def parse_args():
    parser = argparse.ArgumentParser(description="Run PoseBuster checks on best models.")
    parser.add_argument("--root-dir", type=str, default="results/phase2/analysis",
                        help="Root analysis directory (default: results/phase2/analysis)")
    parser.add_argument("--summary-file", type=str, default="results/phase2/analysis/best_model_per_complex.tsv",
                        help="Best model summary TSV (default: results/phase2/analysis/best_model_per_complex.tsv)")
    parser.add_argument("--out-dir", type=str, default="results/phase2/analysis/posebuster_bust_sdf_stdout",
                        help="Output directory for ligand files + results (default: results/phase2/analysis/posebuster_bust_sdf_stdout)")
    return parser.parse_args()


# === Step 2: Ligand selector (exclude water molecules) ===
class LigandSelect(Select):
    def accept_residue(self, residue):
        hetfield, _, _ = residue.id
        return hetfield != " " and residue.get_resname() not in ["HOH", "WAT"]


# === Step 3: Run PoseBuster ===
def run_posebuster(cif_file, protein_file, ligand_pdb, ligand_sdf):
    """Extract ligand, convert to SDF, run PoseBuster, return parsed results."""
    # 3.1 Extract ligand from CIF
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure("model", cif_file)
    io = PDBIO()
    io.set_structure(structure)
    io.save(ligand_pdb, LigandSelect())

    # 3.2 Skip if too small (likely no ligand)
    if os.path.getsize(ligand_pdb) < 200:
        return None, "NO_LIGAND"

    # 3.3 Convert ligand PDB → SDF (Open Babel)
    subprocess.run(["obabel", ligand_pdb, "-O", ligand_sdf], check=True)

    # 3.4 Run PoseBuster
    result = subprocess.run(
        ["bust", ligand_sdf, "-p", protein_file],
        capture_output=True,
        text=True
    )
    out = result.stdout.strip()

    # 3.5 Parse pass/fail counts
    match = re.search(r"passes\s*\((\d+)\s*/\s*(\d+)\)", out)
    if match:
        passed = int(match.group(1))
        total = int(match.group(2))
        pass_rate = round(passed / total, 3)
    else:
        passed = total = pass_rate = None

    # 3.6 Classify status
    if passed is None or total is None:
        pass_status = "UNKNOWN"
    elif passed == total:
        pass_status = "FULL_PASS"
    elif pass_rate >= 0.8:
        pass_status = "PARTIAL_PASS"
    else:
        pass_status = "FAIL"

    return {
        "Passed": passed,
        "Total": total,
        "Pass_Rate": pass_rate,
        "Pass_Status": pass_status,
        "Raw_Output": out,
    }, None


# === Step 4: Main ===
def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    df = pd.read_csv(args.summary_file, sep="\t")
    results = []

    for _, row in df.iterrows():
        complex_id = row["Complex"]
        model_id = row["Model"]

        subdir = f"output_{complex_id}_noTemplate"
        cif_file = os.path.join(args.root_dir, complex_id, subdir, f"pred.{model_id}.cif")
        protein_file = os.path.join(args.root_dir, complex_id, f"{complex_id}_pred_apo.pdb")
        ligand_pdb = os.path.join(args.out_dir, f"{complex_id}_ligand.pdb")
        ligand_sdf = os.path.join(args.out_dir, f"{complex_id}_ligand.sdf")

        if not (os.path.exists(cif_file) and os.path.exists(protein_file)):
            print(f"[SKIP] Missing files for {complex_id}")
            continue

        try:
            result, skip_reason = run_posebuster(cif_file, protein_file, ligand_pdb, ligand_sdf)
            if skip_reason == "NO_LIGAND":
                print(f"[SKIP] No ligand atoms found in {complex_id}")
                continue

            if result:
                results.append({"Complex": complex_id, **result})
                print(f"[RESULT] {complex_id}: {result['Pass_Status']} "
                      f"({result['Passed']}/{result['Total']})")
        except Exception as e:
            print(f"[ERROR] Failed on {complex_id}: {e}")

    # Save results
    out_file = os.path.join(args.out_dir, "bust_stdout_summary.tsv")
    pd.DataFrame(results).to_csv(out_file, sep="\t", index=False)
    print(f"\n[INFO] PoseBuster summary saved to: {out_file}")


if __name__ == "__main__":
    main()
