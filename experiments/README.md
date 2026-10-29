# Experiments on non-open data

[docs/experiments.md](../docs/experiments.md) describes the first two
experiments, which trained on MT560 (Jehovah's Witnesses literature). This
folder lets someone who already has a local copy reproduce them. **Nothing
derived from MT560 may be published:** not the data, the splits, the models,
nor result files that contain translations.

```bash
uv sync --extra experiments
uv run python experiments/prepare_mt560.py /path/to/mt560 --out data/local
uv run omalaka-prepare --datasets --extra data/local/mt560.jsonl --min-words 3 --out splits/mt560
# Experiment 2: M2M-100 1.2B LoRA without religious pairs, a checkpoint every 750 steps
scripts/gpu.sh --hours 2.5 --vram 12 -- uv run omalaka-train facebook/m2m100_1.2B runs/exp2 \
    --data splits/mt560 --lora --drop-religious --batch 16 --accum 2 --epochs 2 --save-every 750 --eval-every 750
uv run omalaka-evaluate exp2 runs/exp2/best --base facebook/m2m100_1.2B --test splits/mt560/test.jsonl
```

The original runs also scored a news document set that is not openly
licensed, with `--docs`. It is not included. `omalaka-evaluate` leaves
translations out of the results file unless you pass `--keep-text`.
