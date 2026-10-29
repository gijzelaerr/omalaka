# To do

Status (2026-10-29): the pipeline works end to end. The first two models
trained on open data only (experiments 3 and 4 in
[docs/experiments.md](docs/experiments.md)) show that synthetic data from
MADLAD-400 can't take quality past MADLAD itself: it helps M2M-100, and it
makes MADLAD worse on news (38.1 to 33.6 chrF++). **The bottleneck is human
translations, not GPU time.** Priorities follow from that.

## 1. Ask for permission to use existing translations (maintainer)

Each one is an email; drafts can be prepared on request. Record answers in
[docs/data.md](docs/data.md).

- [ ] WON corpus authors (Nekoto et al., AfricaNLP 2022, via Masakhane):
      about 5.5k Oshindonga-English sentences on daily life and culture.
      Open licence, or use with credit?
- [ ] Konrad-Adenauer-Stiftung Namibia: their Oshiwambo translation of the
      Constitution (1-2k aligned sentences), and the planned Otjiherero
      and Khoekhoegowab ones.
- [ ] Legal Assistance Centre: guides to laws in Oshikwanyama, Rukwangali
      and Silozi.
- [ ] OHCHR: reuse terms for the UDHR translations (Oshindonga and Silozi in
      the UDHR-in-XML project).
- [ ] Quote section 15(8) of the Copyright Act from the gazetted text (Gazette
      845, 1994); so far it's from a secondary source.

## 2. Make contributing translations easy

- [ ] A simple web form or shared sheet that feeds `community/*.tsv`, so
      speakers don't need GitHub.
- [ ] A short call for contributors, in English and Oshiwambo, explaining
      what to write (own sentences, no copying, no machine translation) and
      the CC BY 4.0 terms.
- [ ] A review flow: a second speaker checks each test-set pair.
- [ ] Target: 500 reviewed test sentences per dialect, then training data.

## 3. Open test set and evaluation

- [ ] Once Ongiini-Eval-OW v1.0 is released (planned end 2026): add its
      references to `datasets/ongiini.py`, score Oshiwambo → English on the
      blind split, and report the LLM-drafted English strata separately.
- [ ] Re-score base MADLAD-400 with the current `omalaka-evaluate`, so all
      rows in experiments.md come from the same code.
- [ ] Submit to the Ongiini leaderboard (English → Oshiwambo), which needs
      training in that direction too.

## 4. More data from public-domain text

- [ ] Rautanen's Oshindonga New Testament (1903): find scans, check the
      edition is his, OCR, align verses with the World English Bible.
      Normalise the old spelling. Use in small doses (religious domain).
- [ ] Look for an Oshikwanyama translation old enough to be public domain.

## 5. Modelling, once there is human data

- [ ] Fine-tune MADLAD-400 3B on human data plus synthetic pairs; compare
      with and without the synthetic pairs.
- [ ] Back-translate open monolingual Oshiwambo, once some exists, with the
      best open model.
- [ ] English → Oshiwambo direction.
- [ ] First release on the Hugging Face Hub, once a model beats base
      MADLAD-400 on an open test set, with a model card listing every source
      (maintainer decides; ask before uploading).

## 6. Community and more languages

- [ ] Introduce omalaka to Masakhane, and ask for Namibian speakers and
      reviewers.
- [ ] Contact University of Namibia and NUST language departments.
- [ ] Look into funding for a paid news-domain translation job (for example
      Lacuna Fund).
- [ ] Otjiherero, Khoekhoegowab, Rukwangali, Silozi: one `community/LANG.tsv`
      each, and the sources in [docs/roadmap.md](docs/roadmap.md).

## Housekeeping

- [ ] Silence the `max_new_tokens`/`max_length` warning in `Translator`.
