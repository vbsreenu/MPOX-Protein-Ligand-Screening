import os
import time
import glob
import requests
import tarfile
import io

# Define input and output directories
QUERY_DIR = "/home4/2948645s/chai_project/Work/monkeypox/mpox_best_models_pdb"
OUT_DIR = "/home4/2948645s/chai_project/Work/monkeypox/foldseek_results"
os.makedirs(OUT_DIR, exist_ok=True)

# Set polling timeout and retry limit
MAX_WAIT = 180  # max waiting time in seconds
NO_PROGRESS_LIMIT = 5  # stop if no status change after 5 polls

# List of FoldSeek databases to search
FOLDSEEK_DATABASES = [
    "afdb50",
    "afdb-swissprot",
    "afdb-proteome",
    "cath50",
    "mgnify_esm30",
    "pdb100",
    "gmgcl_id"
]

def submit_foldseek(file_path):
    """Submit a PDB structure to FoldSeek API and return the ticket info."""
    url = "https://search.foldseek.com/api/ticket"
    with open(file_path, "rb") as f:
        files = { "q": (os.path.basename(file_path), f, "application/octet-stream") }
        data = [("mode", "3diaa")] + [("database[]", db) for db in FOLDSEEK_DATABASES]
        res = requests.post(url, files=files, data=data)
        res.raise_for_status()
        return res.json()

def poll_until_ready(ticket, file_path):
    """Poll FoldSeek server until the job is complete, or raise error/timeout."""
    url = f"https://search.foldseek.com/api/ticket/{ticket}"
    start = time.time()
    last_status = ""
    same_count = 0

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
        elif time.time() - start > MAX_WAIT:
            raise TimeoutError(f"Timeout while waiting for {file_path}")
        elif status == last_status:
            same_count += 1
            if same_count >= NO_PROGRESS_LIMIT:
                raise RuntimeError(f"No progress for {file_path}, ticket {ticket}")
        else:
            same_count = 0
            last_status = status

def download_and_extract(result_url, out_dir, file_path):
    """Download and extract FoldSeek result archive to the specified folder."""
    r = requests.get(result_url)
    r.raise_for_status()
    os.makedirs(out_dir, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(r.content)) as tar:
        tar.extractall(out_dir)
    print(f"Saved to {out_dir}\n")

def process_structure(pdb_path):
    """Submit a PDB file to FoldSeek and process the returned results."""
    if not pdb_path.endswith(".pdb"):
        print(f"Skipping non-pdb file: {pdb_path}")
        return

    uniprot = os.path.basename(pdb_path).replace(".pdb", "")
    result_folder = os.path.join(OUT_DIR, uniprot)
    if os.path.exists(os.path.join(result_folder, "aln.tsv")):
        print(f"Skipping {uniprot} (already done)")
        return

    try:
        print(f"\nSubmitting {pdb_path}")
        res_json = submit_foldseek(pdb_path)
        ticket = res_json.get("ticket") or res_json.get("id")
        if not ticket:
            raise ValueError(f"No ticket returned: {res_json}")

        print(f"Ticket: {ticket} | Status: {res_json.get('status')}")
        result_url = poll_until_ready(ticket, pdb_path)
        print(f"Download from: {result_url}")
        download_and_extract(result_url, result_folder, pdb_path)
        time.sleep(10)  # slight delay to avoid overloading the server
    except Exception as e:
        print(f" Error: {e}")
        with open("foldseek_failures.txt", "a") as f:
            f.write(f"{pdb_path}\n")

if __name__ == "__main__":
    # Find all PDB files in the input directory
    all_pdbs = sorted(glob.glob(os.path.join(QUERY_DIR, "*.pdb")))
    print(f"\nFound {len(all_pdbs)} PDB files.\n")
    for path in all_pdbs:
        process_structure(path)
