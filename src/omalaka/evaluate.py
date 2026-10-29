"""Score a model on sentence test sets and, optionally, document test sets.

usage: omalaka-evaluate NAME MODEL_OR_DIR [--base BASE] [--test FILE ...] [--docs FILE ...] [--keep-text]
Writes results/NAME.json. A sentence test set is JSONL with src, tgt and lang;
a document set has src and ref, paragraphs separated by blank lines, and is
translated sentence by sentence.
Translations are only stored with --keep-text: leave it off for any test set
that is not openly licensed, so the results file can be shared.
"""
import argparse
import json
import time
from pathlib import Path

import sacrebleu
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from .common import DEVICE, Translator, derailed, load_jsonl, religious_bleed, sentences


def score_sentences(translator, rows, keep_text):
    if not rows:
        return {"all": {"n": 0}}
    hyps = translator.translate([r["src"] for r in rows])
    scores = {}
    for lang in sorted({r.get("lang", "all") for r in rows}) + ["all"]:
        pick = [i for i, r in enumerate(rows) if lang == "all" or r.get("lang", "all") == lang]
        h, ref = [hyps[i] for i in pick], [[rows[i]["tgt"] for i in pick]]
        scores[lang] = {"n": len(pick), "bleu": round(sacrebleu.corpus_bleu(h, ref).score, 1),
                        "chrf": round(sacrebleu.corpus_chrf(h, ref, word_order=2).score, 1)}
    scores["derailed_pct"] = round(100 * sum(derailed(r["src"], h) for r, h in zip(rows, hyps)) / len(rows), 1)
    if keep_text:
        scores["samples"] = [{"src": r["src"], "ref": r["tgt"], "hyp": h} for r, h in zip(rows, hyps)]
    return scores


def score_documents(translator, docs, keep_text):
    if not docs:
        return {"documents": 0}
    units = []  # (document index, paragraph index, sentence)
    for a, doc in enumerate(docs):
        for q, para in enumerate(p for p in doc["src"].split("\n\n") if p.strip()):
            units += [(a, q, s) for s in sentences(para)]
    out = translator.translate([u[2] for u in units])
    # Looping is measured without the repeat guard, which hides it as other garbage.
    raw = translator.translate([u[2] for u in units], no_repeat=0)
    hyps = []
    for a in range(len(docs)):
        paras = {}
        for (ua, q, _), h in zip(units, out):
            if ua == a:
                paras.setdefault(q, []).append(h)
        hyps.append("\n\n".join(" ".join(v) for _, v in sorted(paras.items())))
    n = max(1, len(units))
    scores = {
        "chrf": round(sacrebleu.corpus_chrf(hyps, [[d["ref"] for d in docs]], word_order=2).score, 1),
        "documents": len(docs),
        "sentences": len(units),
        "derailed_pct": round(100 * sum(derailed(u[2], h) for u, h in zip(units, raw)) / n, 1),
        "derailed_guarded_pct": round(100 * sum(derailed(u[2], h) for u, h in zip(units, out)) / n, 1),
        "religious_bleed_documents": sum(religious_bleed(d["src"], h, d["ref"]) for d, h in zip(docs, hyps)),
    }
    if keep_text:
        scores["samples"] = [{**d, "hyp": h} for d, h in zip(docs, hyps)]
    return scores


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("model")
    p.add_argument("--base", help="base model when MODEL is a LoRA adapter")
    p.add_argument("--test", nargs="*", default=["splits/test.jsonl"], help="sentence test sets (JSONL)")
    p.add_argument("--docs", nargs="*", default=[], help="document test sets (JSONL)")
    p.add_argument("--limit", type=int, help="score only the first N rows of each set")
    p.add_argument("--keep-text", action="store_true", help="store every translation (open test sets only)")
    p.add_argument("--out", default="results")
    args = p.parse_args(argv)

    tok = AutoTokenizer.from_pretrained(args.model)
    if args.base:
        from peft import PeftModel
        model = AutoModelForSeq2SeqLM.from_pretrained(args.base, dtype=torch.bfloat16).to(DEVICE)
        model = PeftModel.from_pretrained(model, args.model).merge_and_unload()
    else:
        model = AutoModelForSeq2SeqLM.from_pretrained(args.model, dtype=torch.bfloat16).to(DEVICE)
    model.eval()
    translator = Translator(model, tok, args.base or args.model)
    started = time.time()

    result = {"name": args.name, "model": args.model, "base": args.base, "test": {}, "docs": {}}
    for path in args.test:
        rows = load_jsonl(path)[:args.limit]
        result["test"][Path(path).stem] = score_sentences(translator, rows, args.keep_text)
        print(args.name, path, {k: v for k, v in result["test"][Path(path).stem].items() if k != "samples"},
              flush=True)
    for path in args.docs:
        docs = load_jsonl(path)[:args.limit]
        result["docs"][Path(path).stem] = score_documents(translator, docs, args.keep_text)
        print(args.name, path, {k: v for k, v in result["docs"][Path(path).stem].items() if k != "samples"},
              flush=True)
    result["seconds"] = round(time.time() - started)
    Path(args.out).mkdir(parents=True, exist_ok=True)
    with open(Path(args.out) / f"{args.name}.json", "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
