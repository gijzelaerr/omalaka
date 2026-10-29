"""translatewiki.net interface messages, English-Kwanyama, via OPUS.

Short software strings (MediaWiki and other projects), so few pairs and an
odd domain, but human-translated and openly licensed. There is no Ndonga.
"""
import zipfile
from pathlib import Path

from . import download, write_source
from ..common import write_jsonl

VERSION = "v2026-07-01"
URL = f"https://object.pouta.csc.fi/OPUS-translatewiki/{VERSION}/moses/en-kj.txt.zip"

INFO = {
    "name": "translatewiki",
    "title": f"translatewiki.net (OPUS {VERSION})",
    "kind": "human",
    "langs": ["kj"],
    "homepage": "https://opus.nlpl.eu/translatewiki/corpus/version/translatewiki",
    "licence": "CC-BY-3.0",
    "licence_note": "OPUS corpus page: 'License: CC BY 3.0'. Attribution: translatewiki.net contributors; "
                    "J. Tiedemann, Parallel Data, Tools and Interfaces in OPUS (LREC 2012).",
    "checked": "2026-10-29",
    "status": "verified",
    "size": "36 pairs (en-kj)",
}


def fetch(out: Path):
    files = []
    archive = download(URL, out / "raw" / "en-kj.txt.zip", files)
    with zipfile.ZipFile(archive) as z:
        en = z.read(f"translatewiki.en-kj.en").decode("utf-8").splitlines()
        kj = z.read(f"translatewiki.en-kj.kj").decode("utf-8").splitlines()
    rows = [{"src": s.strip(), "tgt": t.strip(), "lang": "kj", "origin": INFO["name"]}
            for s, t in zip(kj, en) if s.strip() and t.strip()]
    write_jsonl(out / "pairs.jsonl", rows)
    write_source(out, INFO, files)
    return len(rows)
