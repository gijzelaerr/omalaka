# Pipeline

```
omalaka-download  ->  data/NAME/{pairs.jsonl, LANG.txt, test.jsonl, SOURCE.json}
omalaka-synthetic ->  data/synthetic-madlad/pairs.jsonl        (optional, GPU)
omalaka-prepare   ->  splits/{train,dev,test}.jsonl
omalaka-train     ->  runs/NAME/{best, last, ckpt-STEP, train_log.jsonl}
omalaka-evaluate  ->  results/NAME.json
```

Every command takes `--help`. Run them with `uv run` from the repository root.
All paths are relative to the current directory, and every output folder is
gitignored.

## 1. Download

`omalaka-download --list` shows the registered datasets. With no names,
`omalaka-download` fetches all of them except the synthetic set. Each dataset
is one module in `src/omalaka/datasets/`, with an `INFO` dict (licence, where
the licence is stated, date checked, status, kind) and a `fetch(out_dir)`.
Downloads are skipped when the file is already there, and `SOURCE.json`
records the sha256 of what was used.

Kinds:

| kind | used for |
|---|---|
| `human` | train, dev and test |
| `synthetic` | train only |
| `mono` | input for back-translation or language ID; not used by prepare |
| `test` | evaluation only, never training |

To add a dataset, copy `translatewiki.py`, fill in `INFO` from the source's
own licence statement (quote it and give the date you checked), add it to
`registry()` in `datasets/__init__.py` and to [data.md](data.md).

## 2. Synthetic pairs (optional)

```bash
scripts/gpu.sh --hours 1 --vram 10 -- uv run omalaka-synthetic --limit 20000
```

Translates Tatoeba English sentences into Kwanyama with base MADLAD-400 3B.
It drops copies of the English, loops, pairs whose lengths don't match, and
outputs with names the English doesn't have: in a first trial MADLAD added
"Namibia" to two of four sentences. Kept pairs go to
`pairs.jsonl` and dropped ones to `rejected.jsonl`. Raise `--limit` to add more;
it resumes. MADLAD-400 has no Ndonga tag, so this is Kwanyama only. Base
MADLAD translates Oshiwambo poorly, so compare a run with and without these
pairs before relying on them.

## 3. Prepare

```bash
uv run omalaka-prepare --datasets translatewiki community synthetic-madlad
```

- Undoes Moses-style spacing, drops pairs with implausible length ratios,
  and removes duplicate sources.
- Test and dev come from human translations only (up to `--test` and `--dev`
  pairs, at most a tenth of the human data each). Synthetic pairs only go to
  train.
- A pair whose Oshiwambo or English is in the test set is kept out of train
  and dev, under either dialect, because both dialects often translate the
  same English sentence. Pass external test sets with `--exclude` to keep
  them out too.
- `--extra FILE.jsonl` adds your own pairs (`{"src", "tgt", "lang"}`). The
  licence of the result is yours to check.

Row format: `{"src": "<Oshiwambo>", "tgt": "<English>", "lang": "kj"|"ng", "origin": "<dataset>"}`.
Language codes are ISO 639-1: `kj` Oshikwanyama, `ng` Oshindonga.

## 4. Train

```bash
uv run omalaka-train facebook/m2m100_1.2B runs/m2m1200 --lora --batch 16 --accum 2 --epochs 2 --save-every 500
```

- Models: `facebook/m2m100_418M` (full fine-tune), `facebook/m2m100_1.2B`
  and `google/madlad400-3b-mt` (LoRA, `--lora`). M2M-100 has no Oshiwambo
  code, so Swahili (`sw`), another Bantu language, stands in as the source
  tag. MADLAD needs only the target tag `<2en>`.
- The best dev chrF++ checkpoint goes to `runs/NAME/best`.
- `--save-every N` makes the run resumable: the full state (weights, optimizer,
  scheduler, data position, RNG) goes to `runs/NAME/last`, and an adapter
  checkpoint to `runs/NAME/ckpt-STEP`. After a crash, run the same command
  again and it carries on.
- `--max-minutes` stops with a final evaluation, which suits a fixed GPU
  booking. `--max-steps` is for smoke tests.
- MADLAD 3B on 12 GB needs `--checkpointing --batch 8 --accum 4 --max-len 96`
  and is slow (about 0.3 steps a second on an RTX 4070 Ti).

## 5. Evaluate

```bash
uv run omalaka-evaluate m2m1200 runs/m2m1200/best --base facebook/m2m100_1.2B \
    --test splits/test.jsonl --keep-text
```

Reports BLEU and chrF++ (sacrebleu) per language, plus the share of
*derailed* outputs: looping, or far longer than the input, the typical
failure of a model that doesn't know the language. `--docs FILE` scores
whole documents (paragraphs split into sentences). It also counts documents
where the model added religious words the source doesn't have, a check from
the first experiments.

Leave out `--keep-text` when a test set isn't openly licensed. The results
file then holds only scores and can be shared.

## Smoke test without a GPU

```bash
MT_DEVICE=cpu uv run omalaka-train facebook/m2m100_418M runs/smoke --max-steps 2 --batch 4 --eval-every 1
MT_DEVICE=cpu uv run omalaka-evaluate smoke runs/smoke/best --limit 20
```
