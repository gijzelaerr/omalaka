"""Synthetic Kwanyama-English pairs: open English sentences translated into Kwanyama by base MADLAD-400.

Back-translation: the English side is real (Tatoeba, everyday sentences), and
only the Kwanyama side is machine-made, which is the usual way to add data for
translation into English. MADLAD-400 has a Kwanyama tag but none for Ndonga,
so this is Kwanyama only.
Always the published base model (Apache-2.0), never a model fine-tuned here:
a fine-tune on closed data would launder that data into this set. Base
MADLAD-400 scored 7.6 BLEU Kwanyama/Ndonga -> English in our first test, so
treat these pairs as experimental: train only, never dev or test, and compare
runs with and without them.
Needs a GPU: book it first (scripts/gpu.sh). Run with --limit for a trial.
"""
import argparse
import bz2
import csv
import random
import re
from pathlib import Path

from . import download, write_source
from ..common import derailed, load_jsonl, write_jsonl

MODEL = "google/madlad400-3b-mt"
TATOEBA = "https://downloads.tatoeba.org/exports/per_language/eng/eng_sentences.tsv.bz2"

INFO = {
    "name": "synthetic-madlad",
    "title": "Tatoeba English back-translated into Kwanyama with MADLAD-400 3B",
    "kind": "synthetic",
    "langs": ["kj"],
    "homepage": "https://tatoeba.org/",
    "licence": "CC-BY-2.0-FR",
    "licence_note": "English: Tatoeba sentences, CC BY 2.0 FR (https://tatoeba.org/en/terms_of_use), "
                    "attribute Tatoeba and its contributors. Kwanyama: output of google/madlad400-3b-mt "
                    "(Apache-2.0), which places no restriction on its output.",
    "checked": "2026-10-29",
    "status": "verified licence; experimental quality",
    "size": "as many as generated (--limit)",
}


def english(out: Path, files: list, limit: int, seed: int = 13):
    """Distinct Tatoeba English sentences of 4-30 words, in a fixed random order.

    Leaves out the Ongiini test sentences, when downloaded: reversed, they are a test target.
    """
    path = download(TATOEBA, out / "raw" / "eng_sentences.tsv.bz2", files)
    test = out.parent / "ongiini" / "sources.jsonl"
    seen = {r["english"].strip().lower() for r in load_jsonl(test)} if test.exists() else set()
    rows = []
    with bz2.open(path, "rt", encoding="utf-8") as fh:
        for rec in csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
            text = rec[2].strip() if len(rec) >= 3 else ""
            if 4 <= len(text.split()) <= 30 and text.lower() not in seen:
                seen.add(text.lower())
                rows.append({"id": rec[0], "text": text})
    random.Random(seed).shuffle(rows)
    return rows[:limit]


def invented_name(english: str, kwanyama: str) -> bool:
    """A capitalised word, past the first, that the English doesn't have.

    MADLAD likes to add "Namibia" and other names to sentences that never mention them.
    """
    words = re.findall(r"[^\W\d_]+", kwanyama)[1:]
    return any(w[0].isupper() and w.lower() not in english.lower() for w in words)


def fetch(out: Path, limit: int = 1000, batch: int = 32):
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    from ..common import DEVICE, Translator

    files = []
    todo = english(out, files, limit)
    done = load_jsonl(out / "pairs.jsonl") if (out / "pairs.jsonl").exists() else []
    rejected = load_jsonl(out / "rejected.jsonl") if (out / "rejected.jsonl").exists() else []
    have = {r["tgt"] for r in done + rejected}
    todo = [r for r in todo if r["text"] not in have]
    if todo:
        tok = AutoTokenizer.from_pretrained(MODEL)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL, dtype=torch.bfloat16).to(DEVICE).eval()
        translator = Translator(model, tok, MODEL, target="kj")
        for i in range(0, len(todo), 512):
            chunk = todo[i:i + 512]
            hyps = translator.translate([r["text"] for r in chunk], batch=batch)
            for r, h in zip(chunk, hyps):
                row = {"src": h, "tgt": r["text"], "lang": "kj", "origin": INFO["name"], "tatoeba_id": r["id"]}
                ratio = len(h.split()) / max(1, len(r["text"].split()))
                # Copies of the English, loops, runaway output and invented names are the usual failures.
                bad = h.strip().lower() == r["text"].lower() or derailed(r["text"], h) \
                    or not 0.4 <= ratio <= 1.8 or invented_name(r["text"], h)
                (rejected if bad else done).append(row)
            write_jsonl(out / "pairs.jsonl", done)
            write_jsonl(out / "rejected.jsonl", rejected)
            print(f"{len(done)} kept, {len(rejected)} rejected", flush=True)
    write_source(out, {**INFO, "model": MODEL}, files)
    return len(done)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--out", default="data/synthetic-madlad")
    p.add_argument("--limit", type=int, default=1000, help="English sentences to translate (resumes)")
    p.add_argument("--batch", type=int, default=32)
    args = p.parse_args(argv)
    print(fetch(Path(args.out), args.limit, args.batch))


if __name__ == "__main__":
    main()
