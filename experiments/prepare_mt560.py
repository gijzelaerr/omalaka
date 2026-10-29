"""Convert a local copy of MT560 (Kwanyama + Ndonga) to JSONL pairs for omalaka-prepare --extra.

usage: uv run --extra experiments python experiments/prepare_mt560.py MT560_DIR [--out data/local]
MT560_DIR holds oshiwambo.parquet and ndonga.parquet (Hugging Face
michsethowusu/english-{oshiwambo,ndonga}_sentence-pairs_mt560).

MT560 is Jehovah's Witnesses text (OPUS withdrew JW300 over copyright). This
reproduces the internal experiments in docs/experiments.md and nothing more:
do not publish the data, splits, results with text, or models trained on it.
Then:  omalaka-prepare --datasets --extra data/local/mt560.jsonl --out splits/mt560
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from omalaka.common import write_jsonl  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("mt560")
p.add_argument("--out", default="data/local")
args = p.parse_args()

rows = []
for name, col, lang in (("oshiwambo", "kua", "kj"), ("ndonga", "ndo", "ng")):
    df = pd.read_parquet(Path(args.mt560) / f"{name}.parquet")
    rows += [{"src": str(osh), "tgt": str(eng), "lang": lang, "origin": "mt560"}
             for eng, osh in zip(df["eng"], df[col])]
write_jsonl(Path(args.out) / "mt560.jsonl", rows)
print(len(rows), "pairs ->", Path(args.out) / "mt560.jsonl")
