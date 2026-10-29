"""Open datasets: one module per source, each with INFO (licence and provenance) and fetch(out_dir).

fetch writes to data/NAME/ (gitignored):
  pairs.jsonl   parallel rows {"src": Oshiwambo, "tgt": English, "lang": "kj"|"ng", "origin": NAME}
  LANG.txt      monolingual text, one sentence or paragraph per line
  test.jsonl    test rows, same fields as pairs.jsonl
  SOURCE.json   INFO plus the URL, sha256 and date of every file downloaded

INFO["kind"] says how prepare may use the data:
  human      human translations: train, dev and test
  synthetic  machine-made source side: train only, never dev or test
  mono       monolingual: back-translation input only
  test       evaluation only, never training
docs/data.md has the full table, including sources checked and rejected.
"""
import datetime
import hashlib
import json
import urllib.request
from pathlib import Path

USER_AGENT = "omalaka-data/0.1 (https://github.com/gijzelaerr/omalaka)"


def download(url: str, path: Path, log: list) -> Path:
    """Fetch URL to PATH unless it is there already; record its sha256 in LOG."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req) as resp, open(path.with_suffix(path.suffix + ".part"), "wb") as fh:
            while chunk := resp.read(1 << 20):
                fh.write(chunk)
        path.with_suffix(path.suffix + ".part").rename(path)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    log.append({"url": url, "file": path.name, "sha256": sha,
                "retrieved": datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()})
    return path


def write_source(out: Path, info: dict, files: list):
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "SOURCE.json", "w", encoding="utf-8") as fh:
        json.dump({**info, "files": files}, fh, ensure_ascii=False, indent=1)


def registry():
    from . import community, ongiini, synthetic_madlad, translatewiki, wikipedia
    return {m.INFO["name"]: m for m in (translatewiki, community, ongiini, wikipedia, synthetic_madlad)}
