# Benchmarking AI-based Protein–Ligand Complex Prediction Models: A One-Phase Evaluation of Chai-1

## Overview
This project evaluates the performance and generalization of the **Chai-1 model** for protein–ligand complex prediction.  
The pipeline is divided into two phases:

- **Phase 1**: Benchmarking against known protein–ligand complexes (PDBbind refined set).  
- **Phase 2**: Prediction of Mpox Proteins’ interactions with ligands (generalisation to novel viral proteins and drug candidates).  

Each phase includes **structure prediction, scoring, apo/holo analysis, SASA calculation, and ligand geometry validation**.

---

## Environment & Dependencies

### Computing Environment
All analyses were performed on the **MRC-University of Glasgow Centre for Virus Research (CVR) Alpha2 and GPU2 HPC clusters**.

### Core tools
- **[Chai-1](https://github.com/chai-lab/chai-lab)** (AI-based protein–ligand prediction)
- **[FoldSeek](https://search.foldseek.com/)** (structural similarity search, APA API)
- **OpenBabel** (molecule format conversion)
- **[PoseBuster](https://posebusters.org/)** (ligand geometry validation)

### Python packages
- Python ≥ 3.10  
- numpy, pandas, matplotlib, seaborn  
- biopython (MMCIFParser, ShrakeRupley, Superimposer)  
- scipy (statistical analysis)

### Installation (conda)
```bash
conda create -n chai_env python=3.10
conda activate chai_env
pip install numpy pandas matplotlib seaborn biopython scipy
```



## Notes

- Some scripts were **adapted from the shared repository [MPOX-Protein-Ligand-Screening](https://github.com/vbsreenu/MPOX-Protein-Ligand-Screening)** provided by Dr. Sreenu Vattipally.  
- Certain parts of the code (e.g., automation scripts and data processing) were written with the assistance of **ChatGPT**, and then revised to ensure consistency with the project’s coding style and requirements.  
- Some utility scripts (directory setup, FoldSeek filtering, plotting) are provided in the repository for reproducibility, though not all are described in the Methods section.