#!/usr/bin/env python3
"""
File: p2_01_prepare_mpxv_inputs.py
Description:
    Step 1: Parse monkeypox protein FASTA file (UniProt reviewed entries).
    Step 2: Create one subdirectory per protein using UniProt Accession ID.
    Step 3: Save protein FASTA (.fa) and Chai input (.txt) files.

Usage:
    python scripts/phase2/p2_01_prepare_mpxv_inputs.py \
        --fasta data/phase2/monkeypox_reviewed.fasta \
        --out-dir data/phase2/proteins

Notes:
    - Input FASTA must be in UniProt format (record.id like "sp|A0A7H0DNB6|PG144_MONPV").
    - Each protein gets its own folder named by UniProt Accession.
    - Chai input (.txt) contains only the protein sequence.
"""

import os
import argparse
from pathlib import Path
from Bio import SeqIO


# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Prepare input folders for monkeypox proteins.")
parser.add_argument("--fasta", type=str, default="data/phase2/monkeypox_reviewed.fasta",
                    help="Input FASTA file with UniProt reviewed entries (default: data/phase2/monkeypox_reviewed.fasta)")
parser.add_argument("--out-dir", type=str, default="data/phase2/proteins",
                    help="Output root directory (default: data/phase2/proteins)")
args = parser.parse_args()

fasta_path = args.fasta
output_root = args.out_dir
os.makedirs(output_root, exist_ok=True)


# === Step 2: Parse FASTA and process each record ===
records = list(SeqIO.parse(fasta_path, "fasta"))
for record in records:
    # Step 2.1: Extract UniProt Accession ID from record.id
    # Example: "sp|A0A7H0DNB6|PG144_MONPV" → accession = "A0A7H0DNB6"
    accession = record.id.split("|")[1]

    # Step 2.2: Create subdirectory for this protein
    subdir = Path(output_root) / accession
    subdir.mkdir(parents=True, exist_ok=True)

    # Step 2.3: Save FASTA file
    fa_path = subdir / f"{accession}_protein.fa"
    SeqIO.write(record, fa_path, "fasta")

    # Step 2.4: Save Chai input file (.txt)
    txt_path = subdir / f"{accession}_input.txt"
    with open(txt_path, "w") as fout:
        fout.write(f">protein|{accession}\n")
        fout.write(str(record.seq) + "\n")

print(f"[INFO] Successfully processed {len(records)} protein sequences into {output_root}")
