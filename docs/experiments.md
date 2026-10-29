# Experiments

The first two experiments, in October 2026, trained on data that is not
openly licensed. Experiments 3 and 4 trained on open data only, and were scored on
the same internal test sets because no open Oshiwambo → English test set
exists yet. All are reported here as aggregate scores, without any
translated text.

The first two experiments used data that is not openly
licensed. They are reported here as aggregate scores only, without any
translated text. The data, splits, models and per-sentence results are not
released. See [experiments/](../experiments/) for how they were run.

**Training data:** MT560 Kwanyama and Ndonga pairs (Jehovah's Witnesses
literature), 185k pairs after filtering. **Tests:** 1,000 held-out MT560
pairs, with their English kept out of training under both dialects. Also 60
Oshiwambo news articles (20 Kwanyama, 20 Ndonga, 20 untagged), scored
against machine-made English, so only a rough signal. Hardware: one
RTX 4070 Ti (12 GB).

## Experiment 1: three base models

| Model | Training | MT560 BLEU / chrF++ | News chrF++ | Looping, no guard | Articles with invented religious words |
|---|---|---|---|---|---|
| M2M-100 418M | none | 2.8 / 16.7 | 26.1 | 77% | 23 of 60 |
| MADLAD-400 3B | none | 7.6 / 23.3 | 38.1 | 4.6% | 6 of 60 |
| M2M-100 418M | full, 1 epoch, 27 min | 32.6 / 50.1 | 41.4 | 1.9% | 24 of 60 |
| M2M-100 1.2B | LoRA, 0.94 epoch, 45 min | **33.6 / 50.6** | **42.6** | 0.7% | 32 of 60 |
| MADLAD-400 3B | LoRA, 0.09 epoch, 90 min | 24.6 / 41.8 | 41.0 | 1.3% | 44 of 60 |

- On the training domain fine-tuning works: 33.6 BLEU on held-out MT560,
  against 24.2 reported by Masakhane on a different, harder (daily-life)
  test set.
- On news it doesn't. Names, numbers and who said what survive, but the rest
  is fluent invention, and the religious register of the training text leaks
  in. Fine-tuning raised the leak from 6 to 24-44 of 60 articles while it
  fixed the looping.
- MADLAD-400 3B trained at 0.1 steps a second (memory-bound on 12 GB), so it
  saw 9% of an epoch: not a fair comparison. M2M-100 1.2B with LoRA is the
  best trade-off (about 2 steps a second).

## Experiment 2: without religious pairs, early checkpoints

M2M-100 1.2B with LoRA on the 96,692 MT560 pairs whose English contains no
word from the religious word list, 2 epochs (6,044 steps, 56 min), scored
every 750 steps.

| Step | MT560 BLEU / chrF++ | News chrF++ | Looping | Articles with religious words |
|---|---|---|---|---|
| 750 | 20.2 / 37.1 | 37.6 | 4.0% | 7 of 60 |
| 1500 | 23.6 / 40.6 | 39.8 | 1.7% | 3 |
| 3000 | 25.9 / 43.2 | 42.2 | 0.9% | 0 |
| 6044 | 27.4 / 44.4 | 42.9 | 0.8% | 0 |
| Exp. 1, all pairs | 33.6 / 50.6 | 42.6 | 0.7% | 32 |

- The leak count drops to zero, but it uses the same word list as the
  filter, so it flatters. Read side by side, the register is still there.
- The invented content did not change, and news chrF++ stayed the same
  (42.9 vs 42.6). Removing religious text cost in-domain quality and bought
  nothing on news.
- MADLAD-400 3B with gradient checkpointing: 0.14-0.33 steps a second, so
  2.5-6 hours per epoch on 12 GB.

## Conclusion

Filtering and early stopping don't fix it: the model doesn't know
everyday and news vocabulary, and religious text won't teach it. The
missing piece is open, in-domain parallel data, which is what this
repository now sets out to build.

## Experiment 3 (2026-10-29): open data only, synthetic Kwanyama

The first model trained only on open data. 20,000 Tatoeba English sentences
were translated into Kwanyama by base MADLAD-400 3B (`omalaka-synthetic`).
The filters dropped 46%: mostly copies of the English (about half the
rejections) and invented names (about a third). That left 10,196 synthetic
pairs plus 30 translatewiki pairs. Sentences from the test sets below and
from Ongiini were excluded. Then M2M-100 1.2B with LoRA, 2 epochs (640 steps,
6 minutes). The open dev set has 3 pairs, too few to select a checkpoint,
so the final checkpoint is scored. Same internal test sets as above, scores
only.

| Model | Training | MT560 BLEU / chrF++ (kj / ng chrF++) | News chrF++ | Looping, no guard (news) | Articles with invented religious words |
|---|---|---|---|---|---|
| M2M-100 1.2B | none | 3.3 / 15.4 (14.8 / 15.9) | 24.3 | 53.3% | 13 of 60 |
| M2M-100 1.2B | LoRA, 10k synthetic kj | 5.9 / 19.2 (19.7 / 18.8) | 30.0 | 7.5% | 5 of 60 |
| MADLAD-400 3B (the teacher) | none (exp. 1) | 7.6 / 23.3 | 38.1 | 4.6% | 6 of 60 |

- Synthetic pairs help M2M-100 a lot: news chrF++ rose from 24.3 to 30.0,
  and looping fell from 53% to 7.5%. Ndonga improved as much as Kwanyama,
  though all the synthetic data is Kwanyama.
- The student is still well below its teacher (30.0 vs 38.1 on news). Back-
  translation from a weak model mostly transfers what MADLAD already knows.
  For an open system today, base MADLAD-400 is better than this fine-tune.
- Next: fine-tune MADLAD itself on these pairs (experiment 4), and collect
  human translations, the only thing that can raise the ceiling.

## Experiment 4 (2026-10-29): MADLAD-400 on its own back-translations

The same 10,226 open training pairs as experiment 3, now training MADLAD-400 3B
with LoRA (gradient checkpointing, batch 8 x 4, max length 96, 2 epochs,
640 steps, 41 minutes at 0.27 steps a second). Final checkpoint, same
internal test sets, scores only.

| Model | Training | MT560 BLEU / chrF++ (kj / ng chrF++) | News chrF++ | Looping, no guard (news) | Articles with invented religious words |
|---|---|---|---|---|---|
| MADLAD-400 3B | none (exp. 1) | 7.6 / 23.3 | **38.1** | 4.6% | 6 of 60 |
| MADLAD-400 3B | LoRA, 10k synthetic kj | **8.7** / 21.8 (22.3 / 21.2) | 33.6 | **2.6%** | 7 of 60 |
| M2M-100 1.2B | LoRA, 10k synthetic kj (exp. 3) | 5.9 / 19.2 | 30.0 | 7.5% | 5 of 60 |

- **Training on its own output made MADLAD worse on news** (38.1 to 33.6
  chrF++) and slightly worse on MT560 chrF++. It loops less, and BLEU on
  MT560 rose a little. The synthetic Kwanyama side is MADLAD's own noisy
  output, so the model learns to read its mistakes, and the short everyday
  Tatoeba sentences pull it away from longer news sentences.
- The base MADLAD-400 row comes from experiment 1's evaluation script; the
  metrics are computed the same way, but it predates the current
  `omalaka-evaluate`.

## Where this leaves us

Synthetic data from MADLAD-400 helps a weaker model (M2M-100), but it can't
take quality past MADLAD itself, and it hurts MADLAD. For now the best open
system for Oshiwambo → English is the untrained MADLAD-400 3B. Further gains
need human translations; see [TODO.md](../TODO.md).
