#!/usr/bin/env python3
"""
File: p2_05_foldseek_batch.py
Description:
    Step 1: Submit predicted monkeypox protein structures (.pdb) to the FoldSeek web API.
    Step 2: Poll the server until results are ready or timeout.
    Step 3: Download and extract result archives into result subfolders.
    Step 4: Log failed cases for troubleshooting.

Usage:
    python scripts/phase2/p2_05_foldseek_batch.py \
        --query-dir results/phase2/mpox_best_models_pdb \
        --out-dir results/phase2/foldseek_results

Notes:
    - Requires internet access to query FoldSeek API.
    - Input directory must contain .pdb files.
    - Default FoldSeek databases: afdb50, afdb-swissprot, afdb-proteome, cath50,
      mgnify_esm30, pdb100, gmgcl_id.
"""

import os
import time
import glob
import tarfile
import io
import requests
import argparse

# === Step 1: Parse arguments ===
parser = argparse.ArgumentParser(description="Batch submit PDBs to FoldSeek API.")
parser.add_argument("--query-dir", type=str, default="results/phase2/mpox_best_models_pdb",
                    help="Directory containing input .pdb files (default: results/phase2/mpox_best_models_pdb)")
parser.add_argument("--out-dir", type=str, default="results/phase2/foldseek_results",
                    help="Directory to save FoldSeek results (default: results/phase2/foldseek_results)")
args = parser.parse_args()

query_dir = args.query_dir
out_dir = args.out_dir
os.makedirs(out_dir, exist_ok=True)

# === Config ===
max_wait = 600             # max waiting time (seconds)
no_progress_limit = 12     # stop if no status change after 12 polls
foldseek_databases = [
    "afdb50",
    "afdb-swissprot",
    "afdb-proteome",
    "cath50",
    "mgnify_esm30",
    "pdb100",
    "gmgcl_id"
]

# === Step 2: Define helper functions ===
def submit_foldseek(file_path):
    """Submit a PDB structure to FoldSeek API and return ticket info."""
    url = "https://search.foldseek.com/api/ticket"
    with open(file_path, "rb") as f:
        files = {"q": (os.path.basename(file_path), f, "application/octet-stream")}
        data = [("mode", "3diaa")] + [("database[]", db) for db in foldseek_databases]
        res = requests.post(url, files=files, data=data)
        res.raise_for_status()
        return res.json()

def poll_until_ready(ticket, file_path):
    """Poll FoldSeek server until COMPLETE/ERROR/timeout."""
    url = f"https://search.foldseek.com/api/ticket/{ticket}"
    start = time.time()
    last_status, same_count = "", 0

    while True:
        time.sleep(5)
        r = requests.get(url)
        r.raise_for_status()
        info = r.json()
        status = info["status"]

        if status == "COMPLETE":
            return f"https://search.foldseek.com/api/result/download/{ticket}"
        elif status == "ERROR":
            raise RuntimeError(f"Server returned error for {file_path}: {info}")
        elif time.time() - start > max_wait:
            raise TimeoutError(f"Timeout while waiting for {file_path}")
        elif status == last_status:
            same_count += 1
            if same_count >= no_progress_limit:
                raise RuntimeError(f"No progress for {file_path}, ticket {ticket}")
        else:
            same_count, last_status = 0, status

def download_and_extract(result_url, out_dir, file_path):
    """Download and extract FoldSeek result archive."""
    r = requests.get(result_url)
    r.raise_for_status()
    os.makedirs(out_dir, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(r.content)) as tar:
        tar.extractall(out_dir)
    print(f"[INFO] Results saved → {out_dir}")

def process_structure(pdb_path):
    """Submit one PDB file and process results."""
    if not pdb_path.endswith(".pdb"):
        return

    uniprot = os.path.basename(pdb_path).replace(".pdb", "")
    result_folder = os.path.join(out_dir, uniprot)
    if os.path.exists(os.path.join(result_folder, "aln.tsv")):
        print(f"[SKIP] {uniprot} (already done)")
        return

    try:
        print(f"[INFO] Submitting {pdb_path}")
        res_json = submit_foldseek(pdb_path)
        ticket = res_json.get("ticket") or res_json.get("id")
        if not ticket:
            raise ValueError(f"No ticket returned: {res_json}")

        print(f"[INFO] Ticket {ticket} | Status {res_json.get('status')}")
        result_url = poll_until_ready(ticket, pdb_path)
        print(f"[INFO] Download from {result_url}")
        download_and_extract(result_url, result_folder, pdb_path)
        time.sleep(10)  # avoid server overload
    except Exception as e:
        print(f"[ERROR] {pdb_path}: {e}")
        with open("foldseek_failures.txt", "a") as f:
            f.write(f"{pdb_path}\n")

# === Step 3: Main execution ===
if __name__ == "__main__":
    all_pdbs = sorted(glob.glob(os.path.join(query_dir, "*.pdb")))
    print(f"[INFO] Found {len(all_pdbs)} PDB files.")
    for path in all_pdbs:
        process_structure(path)
