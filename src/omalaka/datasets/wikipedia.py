"""Monolingual text from the Ndonga and Kwanyama Wikipedias (both closed, read-only wikis).

Tiny (a few hundred kB of text between them), so only a seed for
back-translation or language identification, not training data on its own.
Text is CC BY-SA 4.0: anything derived from it that is shared must carry the
same licence and attribute Wikipedia.
"""
import bz2
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from . import download, write_source

WIKIS = {"ng": "ngwiki", "kj": "kjwiki"}

INFO = {
    "name": "wikipedia",
    "title": "Wikipedia ng/kj article dumps",
    "kind": "mono",
    "langs": ["kj", "ng"],
    "homepage": "https://dumps.wikimedia.org/",
    "licence": "CC-BY-SA-4.0",
    "licence_note": "Wikipedia text is CC BY-SA 4.0 (https://dumps.wikimedia.org/legal.html). Share-alike.",
    "checked": "2026-10-29",
    "status": "verified",
    "size": "ngwiki 85 kB, kjwiki 8 kB compressed (Oct 2026)",
}


def plain(wikitext: str) -> str:
    """Rough wikitext to plain text: good enough for monolingual sentences."""
    t = re.sub(r"<ref[^>]*/>|<ref.*?</ref>|<!--.*?-->|<gallery.*?</gallery>", "", wikitext, flags=re.S)
    for _ in range(3):
        t = re.sub(r"\{\{[^{}]*\}\}|\{\|.*?\|\}", "", t, flags=re.S)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", t)
    t = re.sub(r"^\s*[\w-]+:\S.*$", "", t, flags=re.M)  # File:, Category: and interwiki lines
    t = re.sub(r"'{2,}|<[^>]+>|^[=*#:;|!].*$", "", t, flags=re.M)
    return "\n".join(line.strip() for line in t.splitlines() if len(line.split()) >= 4)


def fetch(out: Path):
    files, total = [], 0
    for lang, wiki in WIKIS.items():
        url = f"https://dumps.wikimedia.org/{wiki}/latest/{wiki}-latest-pages-articles.xml.bz2"
        dump = download(url, out / "raw" / f"{wiki}.xml.bz2", files)
        lines = []
        for _, el in ET.iterparse(bz2.open(dump)):
            if el.tag.endswith("}page"):
                ns = el.find("{*}ns")
                text = el.find("{*}revision/{*}text")
                if ns is not None and ns.text == "0" and text is not None and text.text \
                        and not text.text.lstrip().lower().startswith("#redirect"):
                    lines += plain(text.text).splitlines()
                el.clear()
        (out / f"{lang}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        total += len(lines)
    write_source(out, INFO, files)
    return total
