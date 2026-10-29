"""Shared helpers: data loading and batched translation for M2M-100 and MADLAD-400."""
import json
import os
import re
from pathlib import Path

import torch

DEVICE = os.environ.get("MT_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
AUTOCAST = DEVICE.split(":")[0]

# M2M-100 has no Oshiwambo code; Swahili, a Bantu language, stands in.
M2M_SOURCE = "sw"


def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def is_madlad(name: str) -> bool:
    return "madlad" in str(name).lower()


class Translator:
    """Batched beam search. TARGET is "en", or for MADLAD any language it has a tag for (kj)."""

    def __init__(self, model, tok, name, max_len=200, target="en"):
        self.model, self.tok, self.madlad, self.max_len = model, tok, is_madlad(name), max_len
        self.target = target
        if not self.madlad:
            if target != "en":
                raise ValueError("M2M-100 has no Oshiwambo code; only translation into English is supported")
            tok.src_lang = M2M_SOURCE
            tok.tgt_lang = "en"

    def source(self, text: str) -> str:
        return f"<2{self.target}> {text}" if self.madlad else text

    @torch.no_grad()
    def translate(self, texts, beams=4, batch=24, no_repeat=4):
        order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
        out = [None] * len(texts)
        extra = {} if self.madlad else {"forced_bos_token_id": self.tok.get_lang_id("en")}
        for i in range(0, len(order), batch):
            idx = order[i:i + batch]
            enc = self.tok([self.source(texts[j]) for j in idx], return_tensors="pt", padding=True,
                           truncation=True, max_length=256).to(self.model.device)
            with torch.autocast(AUTOCAST, dtype=torch.bfloat16):
                gen = self.model.generate(**enc, num_beams=beams, max_new_tokens=self.max_len,
                                          no_repeat_ngram_size=no_repeat, **extra)
            for j, text in zip(idx, self.tok.batch_decode(gen, skip_special_tokens=True)):
                out[j] = text.strip()
        return out


def sentences(paragraph: str):
    """Split a paragraph into sentences; the models were trained on single sentences."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", paragraph.strip())
    return [p for p in parts if p.strip()]


def derailed(src: str, hyp: str) -> bool:
    """Looping or runaway output: a 3-word phrase 3+ times, or far longer than the input."""
    words = hyp.lower().split()
    grams = [" ".join(words[i:i + 3]) for i in range(len(words) - 2)]
    looping = any(grams.count(g) >= 3 for g in set(grams))
    return looping or len(words) > 2.5 * max(5, len(src.split()))


RELIGIOUS = re.compile(r"\b(jehovah|god|bible|christian\w*|congregation\w*|witness(es)?|kingdom|scriptur\w*|"
                       r"apostle\w*|jesus|christ|prayer\w*|pray\w*|faith|sin|sins|sinners?|preach\w*|disciples?|"
                       r"satan|paradise|bethel|elders?|biblical)\b", re.I)


def religious_bleed(src: str, hyp: str, ref: str) -> bool:
    """Religious words in the translation that neither the source names nor the reference has.

    A diagnostic from the first experiments, whose training text was religious:
    the invented content a model trained on such text is most likely to add.
    """
    found = {m.group(0).lower() for m in RELIGIOUS.finditer(hyp)}
    allowed = {m.group(0).lower() for m in RELIGIOUS.finditer(ref)}
    # Names and words that keep their form across the languages (Jehova, Kristus, Bibeli).
    src_l = src.lower()
    allowed |= {w for w in found if w[:4] in src_l}
    return bool(found - allowed)
