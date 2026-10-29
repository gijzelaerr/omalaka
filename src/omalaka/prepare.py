"""Build train/dev/test splits from downloaded datasets.

usage: omalaka-prepare [--datasets translatewiki community ...] [--extra FILE.jsonl ...] [--out splits]
Human translations are cleaned, deduplicated and split; synthetic pairs only
go to train. Any pair whose Oshiwambo or English appears in a test set (this
split's or one named with --exclude) is kept out of train and dev, under
either dialect.
--extra takes your own JSONL pairs {src, tgt, lang}. They are treated as human
translations; whether a model trained on them can be shared is up to their
licence (see docs/data.md).
"""
import argparse
import random
import re
from pathlib import Path

from .common import load_jsonl, write_jsonl
from .datasets import registry


def detok(text: str) -> str:
    """Undo Moses-style spacing (``word ,`` -> ``word,``), which some corpora carry."""
    text = re.sub(r"\s+([.,;:!?)\]'\"])", r"\1", text)
    text = re.sub(r"([(\[])\s+", r"\1", text)
    text = re.sub(r"\s+'\s*s\b", "'s", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def usable(src: str, tgt: str, min_words: int) -> bool:
    ls, lt = len(src.split()), len(tgt.split())
    if not (min_words <= ls <= 80 and min_words <= lt <= 80):
        return False
    # Misaligned pairs show up as very different lengths. Oshiwambo runs
    # somewhat shorter in words than English (agglutinative).
    return 0.4 <= ls / lt <= 1.8 or max(ls, lt) <= 3


def main(argv=None):
    sets = registry()
    p = argparse.ArgumentParser()
    p.add_argument("--datasets", nargs="*", default=[n for n, m in sets.items() if m.INFO["kind"] == "human"],
                   help="downloaded datasets to use (default: every human-translated one)")
    p.add_argument("--extra", nargs="*", default=[], help="more JSONL pairs, treated as human translations")
    p.add_argument("--exclude", nargs="*", default=[], help="test sets whose sentences must stay out of training")
    p.add_argument("--data", default="data")
    p.add_argument("--out", default="splits")
    p.add_argument("--dev", type=int, default=1000, help="dev size, at most a tenth of the human pairs")
    p.add_argument("--test", type=int, default=1000, help="test size per run, at most a tenth of the human pairs")
    p.add_argument("--min-words", type=int, default=1)
    p.add_argument("--seed", type=int, default=13)
    args = p.parse_args(argv)
    rng = random.Random(args.seed)

    human, synthetic = [], []
    for name in args.datasets:
        kind = sets[name].INFO["kind"]
        if kind not in ("human", "synthetic"):
            p.error(f"{name} is {kind} data, not training pairs")
        path = Path(args.data) / name / "pairs.jsonl"
        if not path.exists():
            p.error(f"{path} is missing: run omalaka-download {name}")
        (human if kind == "human" else synthetic).extend(load_jsonl(path))
    for path in args.extra:
        human.extend({**r, "origin": r.get("origin", Path(path).stem)} for r in load_jsonl(path))

    def clean(rows):
        seen, out = set(), []
        for r in rows:
            r = {**r, "src": detok(str(r["src"])), "tgt": detok(str(r["tgt"]))}
            if usable(r["src"], r["tgt"], args.min_words) and r["src"] not in seen:
                seen.add(r["src"])
                out.append(r)
        rng.shuffle(out)
        return out

    human, synthetic = clean(human), clean(synthetic)
    # Pairs collected as test data (community split=test) are always test,
    # and only once a second speaker has reviewed them.
    fixed = [r for r in human if r.get("split") == "test"]
    human = [r for r in human if r.get("split") != "test"]
    n_test = min(args.test, len(human) // 10)
    n_dev = min(args.dev, len(human) // 10)
    test = [r for r in fixed if r.get("reviewed")] + human[:n_test]
    held = test + fixed + [r for path in args.exclude for r in load_jsonl(path)]
    # External test sets may be English-only (ongiini/sources.jsonl has just "english").
    held_src = {r.get("src") for r in held} - {None}
    held_en = {r.get("tgt") or r.get("ref") or r.get("english") for r in held} - {None}
    rest = [r for r in human[n_test:] + synthetic if r["src"] not in held_src and r["tgt"] not in held_en]
    human_ids = {id(r) for r in human}
    dev = [r for r in rest if id(r) in human_ids][:n_dev]
    dev_ids = {id(r) for r in dev}
    train = [r for r in rest if id(r) not in dev_ids]
    for split, rows in (("train", train), ("dev", dev), ("test", test)):
        write_jsonl(Path(args.out) / f"{split}.jsonl", rows)
        origins = {}
        for r in rows:
            origins[r["origin"]] = origins.get(r["origin"], 0) + 1
        print(split, len(rows), origins)


if __name__ == "__main__":
    main()
