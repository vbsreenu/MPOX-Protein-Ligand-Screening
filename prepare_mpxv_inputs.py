import os
from pathlib import Path
from Bio import SeqIO

# 输入 FASTA 文件路径
FASTA_PATH = "/home4/2948645s/chai_project/Work/monkeypox/monkeypox_reviewed.fasta"

# 输出根目录：每个蛋白一个子目录
OUTPUT_ROOT = "/home4/2948645s/chai_project/Work/monkeypox"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# 解析所有蛋白记录
records = list(SeqIO.parse(FASTA_PATH, "fasta"))

for record in records:
    # 从 record.id 提取 UniProt Accession ID
    # 例如：record.id = 'sp|A0A7H0DNB6|PG144_MONPV' → accession = A0A7H0DNB6
    accession = record.id.split('|')[1]

    # 创建子目录
    subdir = Path(OUTPUT_ROOT) / accession
    subdir.mkdir(parents=True, exist_ok=True)

    # 保存 .fa 文件
    fa_path = subdir / f"{accession}_protein.fa"
    SeqIO.write(record, fa_path, "fasta")

    # 生成 .txt 输入文件（仅含 protein 信息）
    txt_path = subdir / f"{accession}_input.txt"
    with open(txt_path, "w") as fout:
        fout.write(f">protein|{accession}\n")
        fout.write(str(record.seq) + "\n")

print(f"Successfully processed {len(records)} protein sequences using UniProt Accession IDs.")
