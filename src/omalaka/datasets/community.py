"""Translations contributed to this repository (community/*.tsv), under CC BY 4.0.

Nothing is downloaded: the TSV files in the repository are the source. Each
row says who translated it and whether a second speaker checked it; see
community/README.md for the format and the contribution terms.
"""
import csv
from pathlib import Path

from . import write_source
from ..common import write_jsonl

ROOT = Path(__file__).resolve().parents[3] / "community"

INFO = {
    "name": "community",
    "title": "omalaka community translations",
    "kind": "human",
    "langs": ["kj", "ng"],
    "homepage": "https://github.com/gijzelaerr/omalaka/tree/main/community",
    "licence": "CC-BY-4.0",
    "licence_note": "Contributors agree to CC BY 4.0 when they submit (community/README.md).",
    "checked": "2026-10-29",
    "status": "verified",
    "size": "grows with contributions",
}


def read(root: Path = ROOT):
    rows = []
    for path in sorted(root.glob("*.tsv")):
        with open(path, encoding="utf-8", newline="") as fh:
            for rec in csv.DictReader(fh, delimiter="\t"):
                if rec.get("oshiwambo", "").strip() and rec.get("english", "").strip():
                    rows.append({"src": rec["oshiwambo"].strip(), "tgt": rec["english"].strip(),
                                 "lang": rec["lang"].strip(), "origin": INFO["name"],
                                 "split": rec.get("split", "").strip() or "train",
                                 "reviewed": bool(rec.get("reviewed_by", "").strip())})
    return rows


def fetch(out: Path):
    rows = read()
    write_jsonl(out / "pairs.jsonl", rows)
    write_source(out, INFO, [])
    return len(rows)
