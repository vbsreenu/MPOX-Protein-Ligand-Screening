# Phase 2: Prediction of Mpox Proteins’ interactions with ligands

## Workflow Overview
This phase extends the evaluation of **Chai-1** to **novel viral proteins and potential drug interactions**, focusing on **Mpox proteins**.  
The workflow integrates **protein structure prediction, structural similarity search, drug annotation, and protein–ligand complex modeling** into a multi-step pipeline.

**Generalization pipeline (Phase 2):**
1. **Collect Mpox proteins** from UniProt (reviewed entries).  
2. **Predict protein structures** using Chai-1 (no-template mode).  
3. **Search FoldSeek** for structural homologs against reference databases.  
4. **Filter human hits** and extract annotated UniProt IDs.  
5. **Identify DrugBank links** for candidate proteins.  
6. **Retrieve drug SMILES** via PubChem API.  
7. **Filter & finalize protein–drug pairs** (E-value threshold).  
8. **Predict Mpox–drug complexes** with Chai-1.  
9. **Select best models** (aggregate score).  
10. **Generate apo structures** (ligand removed).  
11. **Compute ΔSASA** (apo vs holo).  
12. **Analyze ΔSASA** distribution and correlations.  
13. **Run PoseBuster** for ligand geometry validation.  
14. **Merge overall results** into a summary table.  

---

## Scripts and Functions

| Step | Script | Function |
|------|--------|----------|
| 1 | `p2_01_prepare_mpxv_inputs.py` | Generate per-protein FASTA and Chai-1 input files from UniProt sequences |
| 2 | `p2_02_run_chai_batch_mpxv_no_template.sh` | Batch Chai-1 runs for Mpox proteins (no-template mode) |
| 3 | `p2_03_select_best_models.py` | Select best model per protein (aggregate score) |
| 4 | `p2_04_convert_cif_to_pdb.sh` | Convert `.cif` models to `.pdb` for downstream analysis |
| 5 | `p2_05_foldseek_batch.py` | Submit Mpox proteins to FoldSeek (APA API) |
| 6 | `p2_06_extract_foldseek_human_hits.py` | Extract Homo sapiens hits from FoldSeek results |
| 7 | `p2_07_filter_drugbank_hits.py` | Map UniProt IDs to DrugBank annotations |
| 8 | `p2_08_get_drug_smiles_from_pubchem.py` | Retrieve SMILES strings for DrugBank compounds |
| 9 | `p2_09_filter_by_evalue.py` | Apply E-value threshold to refine protein–drug hits |
| 10 | `p2_10_count_summary.py` | Summarize candidate protein–drug pairs |
| 11 | `p2_11_predict_mpxv_drug_complexes.sh` | Predict Mpox protein–drug complexes with Chai-1 |
| 12 | `p2_12_prepare_mpxv_analysis_dir.py` | Organize analysis directory for downstream evaluation |
| 13 | `p2_13_mpxv_extract_scores.py` | Extract aggregate and pTM scores for all models |
| 14 | `p2_14_mpxv_select_best_model.py` | Select best complex per protein–drug pair |
| 15 | `p2_15_generate_predicted_apo_from_best_model.py` | Remove ligands to create apo structures |
| 16 | `p2_16_calculate_delta_sasa.py` | Compute ΔSASA (apo vs holo) |
| 17 | `p2_17_analyze_and_plot_delta_sasa.py` | Statistical analysis + plots of ΔSASA |
| 18 | `p2_18_run_posebuster_on_best_models.py` | Evaluate ligand geometries using PoseBuster |
| 19 | `p2_19_plot_posebuster.py` | Plot PoseBuster results (pie, bar charts) |
| 20 | `p2_20_merge_overall_results.py` | Merge scores, ΔSASA, and PoseBuster into one summary |

---

## Key Outputs

- **Protein–Drug Complex Predictions**  
  - `results/phase2/analysis/<protein>_<drug>/output_*_noTemplate/`  
  - Contains `.cif` models and `.npz` score files.  

- **Best Models**  
  - `results/phase2/analysis/best_model_per_complex.tsv`  
  - Selected by aggregate score.  

- **ΔSASA Analysis**  
  - `results/phase2/analysis/delta_sasa_biopython.tsv`  
  - `results/phase2/analysis/plots_pub/` (distribution, scatter, boxplots).  

- **PoseBuster Evaluation**  
  - `results/phase2/analysis/posebuster_bust_sdf_stdout/bust_stdout_summary.tsv`  
  - `results/phase2/analysis/posebuster_bust_sdf_stdout/plots_pub/` (pie & bar charts).  

- **Overall Summary**  
  - `results/phase2/analysis/phase2_overall_summary.tsv`  
  - Integrates: Complex ID, scores, ΔSASA, PoseBuster classification.  

---

## Notes

- **Mode**: All Mpox predictions in Phase 2 were run in **no-template mode** to assess **true generalization**.  
- **Input**: Only **reviewed Mpox UniProt entries** were used (high confidence sequences).  
- **Drug Filtering**: Only protein–drug pairs with **DrugBank annotation** and valid SMILES were tested.  
- **Scalability**: Pipeline designed to extend to other viruses and large drug libraries.  
- **Reproducibility**: Scripts are modular, can be run step-by-step or end-to-end. Large intermediate files (models, logs) are excluded from version control.  