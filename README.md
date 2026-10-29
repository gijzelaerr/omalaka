# omalaka

Open machine translation for Namibian languages. *Omalaka* is Oshiwambo for
"languages".

None of the widely used translation services or open models translates
Oshikwanyama or Oshindonga well. omalaka fine-tunes open models
(M2M-100, MADLAD-400) on openly licensed data, starting with
**Oshikwanyama → English** and **Oshindonga → English**. Otjiherero,
Khoekhoegowab, Rukwangali and Silozi come later; see the
[roadmap](docs/roadmap.md).

**Status: early.** The pipeline works. What's missing is open training data.
The first experiments used corpora that are not openly licensed, so
no model has been released (see [Data](#data-and-licences)). Help with data
is the most useful contribution right now: see
[CONTRIBUTING.md](CONTRIBUTING.md) and [TODO.md](TODO.md).

## Quick start

Needs [uv](https://docs.astral.sh/uv/) and, for training, an NVIDIA GPU
(12 GB is enough for M2M-100 1.2B with LoRA). On Windows and Linux,
`pyproject.toml` installs PyTorch with CUDA 12.8.

```bash
uv sync
uv run omalaka-download --list              # datasets, licences, status
uv run omalaka-download                     # fetch every open dataset into data/
uv run omalaka-prepare                      # build splits/ from the human translations
uv run omalaka-train facebook/m2m100_1.2B runs/m2m1200 --lora --batch 16 --accum 2 --save-every 500
uv run omalaka-evaluate m2m1200 runs/m2m1200/best --base facebook/m2m100_1.2B --keep-text
```

Models come from the Hugging Face Hub and are cached wherever `HF_HOME`
points. Set `MT_DEVICE=cpu` to run without a GPU (only practical for smoke
tests).

On a shared GPU, wrap long jobs with `scripts/gpu.sh`. It books the GPU
through a tool named in `OMALAKA_GPU_RUN` if you have one, and otherwise
just runs the job:

```bash
scripts/gpu.sh --hours 2 --vram 12 -- uv run omalaka-train ...
```

[docs/pipeline.md](docs/pipeline.md) explains each step, the data formats
and the options.

## Data and licences

The code is under the [Apache License 2.0](LICENSE). **Each dataset keeps its
own licence**, recorded in its download module and in
[docs/data.md](docs/data.md). `omalaka-download` writes the licence, URL,
date and checksum of every file it fetches to `data/NAME/SOURCE.json`.

Ground rules for this repository:

- Only openly licensed data goes into training sets that lead to a released
  model, and every release will list its sources in the model card.
- No data, splits, checkpoints or scores are committed. They stay in
  gitignored folders (`data/`, `splits/`, `runs/`, `results/`).
- Synthetic data comes only from openly licensed base models (MADLAD-400,
  Apache-2.0), never from a model fine-tuned on closed data, and never from
  services whose terms restrict training on their output. It is used for
  training only, never for testing.
- Test sets are human translations, with their provenance documented
  (see [docs/data.md](docs/data.md#the-open-test-set)).

The first experiments used the MT560 corpus, which is Jehovah's Witnesses
literature (OPUS withdrew its source, JW300, over copyright). They also used a
news test set that is not openly licensed. Models trained on that data are
not released, and the data is not distributed here.
[docs/experiments.md](docs/experiments.md) reports their aggregate scores, and
[experiments/](experiments/) has the script for anyone who already has a copy.

## Project layout

```
src/omalaka/          pipeline: download, prepare, train, evaluate
src/omalaka/datasets/ one module per open dataset, with its licence
community/            translations contributed to this project (CC BY 4.0)
docs/                 pipeline, data sources, roadmap, experiment results
experiments/          scripts for the earlier non-open experiments
scripts/gpu.sh        optional GPU booking wrapper
```

## Related work and partners

- [Masakhane](https://www.masakhane.io/), the grassroots NLP community for
  African languages. Its 2022 participatory Oshindonga corpus (Nekoto et al.,
  AfricaNLP 2022) set the first M2M-100 baseline (24.2 BLEU).
- [Ongiini-Eval-OW](https://github.com/sebkuepers/Ongiini), an open
  (CC BY 4.0) benchmark for English ↔ Oshindonga and Oshikwanyama. omalaka
  will report results on it once its references are released.

## Licence

Code: Apache-2.0, see [LICENSE](LICENSE). Datasets: their own licences, see
[docs/data.md](docs/data.md). Community translations: CC BY 4.0.
