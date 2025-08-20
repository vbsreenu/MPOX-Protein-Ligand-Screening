# Phase 1: Benchmark Evaluation on Known Protein–Ligand Complexes using Chai-1

This phase evaluates the performance of the Chai model on a benchmark dataset of known protein–ligand complexes. Both **with-template** and **no-template** prediction modes were tested. The workflow includes data preparation, structure prediction, model ranking, structural evaluation, and ligand geometry checks.

---

## Workflow Overview

1. **Prepare Chai input files**  
   - Convert PDB proteins to FASTA sequences  
   - Convert ligand SDF files to SMILES  
   - Assemble `.txt` input files required by Chai  

2. **Run Chai predictions**  
   - Batch predictions with and without structural templates  
   - Organize outputs into per-complex folders  

3. **Extract and rank models**  
   - Collect aggregate scores and pTM values  
   - Select the best-scoring model per complex and mode  

4. **Structural evaluation**  
   - Compute backbone RMSD (CA atoms) against experimental crystal structures  
   - Perform statistical comparison between modes  
   - Statistical test results (Welch’s t-test) are printed to console during execution

5. **Surface accessibility analysis**  
   - Compute ΔSASA (apo – holo) values for predicted models using Biopython’s ShrakeRupley implementation 

6. **Geometry validation**  
   - Use PoseBuster to check ligand conformations and steric clashes  
   - Summarize validation outcomes (FULL_PASS / PARTIAL_PASS / FAIL)  

---

## Scripts and Functions

| Script | Description | Output |
|--------|-------------|--------|
| `p1_01_generate_inputs.sh` | Generate FASTA, SMILES, and Chai `.txt` input files from raw protein–ligand complexes | Input files for Chai |
| `p1_02_run_chai_no_template.sh` | Run Chai predictions without templates | Predicted `.cif` models |
| `p1_03_run_chai_with_template.sh` | Run Chai predictions with templates | Predicted `.cif` models |
| `p1_04_extract_scores.py` | Extract aggregate and pTM scores from Chai outputs | `all_scores_summary.tsv` |
| `p1_05_select_best_models.py` | Select the best model per complex (highest aggregate score) | `best_model_per_complex.tsv` |
| `p1_06_download_pdb_complexes.sh` | Download experimental crystal structures from RCSB | `<complex>_complex.pdb` |
| `p1_07_compute_rmsd.py` | Calculate backbone RMSD (CA atoms) vs. crystal structures | `best_model_rmsd_summary.tsv` |
| `p1_08_analyze_rmsd.py` | Perform statistical test and generate RMSD comparison plots | `rmsd_comparison.png/pdf` |
| `p1_10_generate_apo_structures.py` | Remove ligands from predicted complexes to create apo structures | `<complex>_pred_apo_<mode>.pdb` |
| `p1_11_calculate_delta_sasa.py` | Compute ΔSASA (apo – holo) using Biopython | `delta_sasa_biopython.tsv` |
| `p1_13_run_posebuster.py` | Run PoseBuster geometry validation on ligands | `posebuster_stats.tsv`, `bust_stdout_summary.tsv` |

---

## Key Outputs

- **Model ranking:**  
  - `all_scores_summary.tsv`  
  - `best_model_per_complex.tsv`  

- **Structural evaluation:**  
  - `best_model_rmsd_summary.tsv`  
  - `rmsd_comparison.png/pdf`  

- **Surface accessibility:**  
  - `delta_sasa_biopython.tsv` 

- **Geometry validation:**  
  - `posebuster_stats.tsv`  
  - `bust_stdout_summary.tsv`  

---

## Notes

- Phase 1 strictly benchmarks Chai predictions against **known experimental complexes**.  
- RMSD comparison is the primary structural evaluation metric.  
- ΔSASA values are calculated in this phase.  
- PoseBuster results are summarized textually.  

---
