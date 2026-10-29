"""Ongiini-Eval-OW: an open benchmark for English <-> Oshindonga and Oshikwanyama.

600 English source items, each to be translated by a human into both
dialects. The English is public now; the references come with v1.0, which
its authors plan for the end of 2026. Until then this writes the English
sources only (data/ongiini/sources.jsonl), so test.jsonl is empty.
Evaluation only: never train on it. The upstream TSV also carries columns for
model drafts; those are dropped here.
"""
import csv
import io
from pathlib import Path

from . import download, write_source
from ..common import write_jsonl

REPO = "https://raw.githubusercontent.com/sebkuepers/Ongiini/main"
SOURCES = f"{REPO}/data/oshiwambo_eval_v3.tsv"

INFO = {
    "name": "ongiini",
    "title": "Ongiini-Eval-OW benchmark (Küpers 2026)",
    "kind": "test",
    "langs": ["kj", "ng"],
    "homepage": "https://github.com/sebkuepers/Ongiini",
    "licence": "CC-BY-4.0",
    "licence_note": "data/oshiwambo_eval/LICENSE: 'Creative Commons Attribution 4.0 International License "
                    "(CC-BY-4.0)', Copyright (c) 2026 Common Intelligence Foundation.",
    "checked": "2026-10-29",
    "status": "verified (English sources); references not released yet",
    "size": "600 items (420 dev, 180 blind)",
}


def fetch(out: Path):
    files = []
    tsv = download(SOURCES, out / "raw" / "oshiwambo_eval_v3.tsv", files)
    download(f"{REPO}/data/oshiwambo_eval/LICENSE", out / "raw" / "LICENSE", files)
    reader = csv.DictReader(io.StringIO(tsv.read_text(encoding="utf-8")), delimiter="\t")
    # provenance: crafted and formal_drafted English was drafted with LLM help; score those apart.
    sources = [{"id": r["id"], "english": r["english"], "domain": r["domain"], "provenance": r["provenance"],
                "split": "blind" if r["in_blind_split"].strip().lower() == "true" else "dev"}
               for r in reader if r.get("english", "").strip()]
    write_jsonl(out / "sources.jsonl", sources)
    # References: add them here once v1.0 is out, as rows {src, tgt, lang, origin}.
    write_jsonl(out / "test.jsonl", [])
    write_source(out, INFO, files)
    return len(sources)
