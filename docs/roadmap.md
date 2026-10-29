# Roadmap

## Now: Oshikwanyama and Oshindonga → English

1. Grow open training data: community translations, permission requests
   (Constitution translations, publishers), and the public-domain Rautanen
   Oshindonga Bible. See [data.md](data.md).
2. Train on open data only, plus synthetic Kwanyama pairs from base MADLAD-400,
   with and without them.
3. Report on Ongiini-Eval-OW once its references are out, and on the omalaka
   community test set once it has 500 reviewed pairs per dialect.
4. Publish the first model on the Hugging Face Hub when it beats the
   untrained base models on an open test set, with a model card listing every
   source and the derailment rate. Nothing is published before then.
5. English → Oshiwambo. Ongiini scores that direction, and it is what most
   users of a public service need.

## Next languages

All four have even less open data than Oshiwambo, and none has a language tag
in MADLAD-400 or M2M-100 (checked in the MADLAD tokenizer). So each one
starts with data collection, not training.

| Language | Codes | Family | What we know | First step |
|---|---|---|---|---|
| Otjiherero | `hz` / `her` | Bantu | Closed Wikipedia (8 kB); an 1849 public-domain selection of Bible stories and hymns on archive.org | Community translations; ask the Konrad-Adenauer-Stiftung about its planned Otjiherero Constitution |
| Khoekhoegowab (Damara/Nama) | `naq` | Khoe (not Bantu; click consonants) | No open parallel data found. Proxy tags from Bantu languages won't help much | Community translations; involve University of Namibia linguists for orthography |
| Rukwangali | `kwn` | Bantu | 1987 Genesis portion (probably in copyright) | Community translations; the Legal Assistance Centre's Rukwangali law guides (ask permission) |
| Silozi | `loz` | Bantu (Sotho-Tswana group) | Also a national language in Zambia, so Zambian sources may exist; a UDHR translation (licence to check, see data.md) | Search Zambian government and education material; the LAC Silozi law guides (ask permission) |

For each language: add a `community/LANG.tsv`, add its code to the
prepare/train path (a stand-in M2M source tag from the closest supported
language), and record every source in [data.md](data.md).

## Working with Masakhane and others

[Masakhane](https://www.masakhane.io/) is a grassroots research community for
NLP in African languages. It publishes openly and works in a participatory
way: native speakers are researchers, not just annotators. That fits this
project, and its members wrote the earlier Oshindonga work
(Nekoto et al., *Participatory Translations of Oshiwambo*, AfricaNLP 2022).

Concrete steps, each for the maintainer to take, not automated:

1. **Introduce omalaka** in the Masakhane community channels once the
   repository is public. Ask for Namibian speakers and reviewers.
2. **Ask the WON corpus authors** whether their roughly 5.5k Oshindonga
   sentences can be released under an open licence, or used with credit.
3. **Share results openly**: the open test set, the derailment metric and
   negative results (religious text bleeding into news) are useful to
   others working on low-resource languages.
4. **Ongiini-Eval-OW**: submit systems to its leaderboard, and coordinate so
   the omalaka test set and Ongiini complement each other (Ongiini is
   translated from English; omalaka's is written in Oshiwambo).
5. **Local partners**: University of Namibia and Namibia University of
   Science and Technology language departments, the Legal Assistance Centre
   and the Konrad-Adenauer-Stiftung for translations already made, and
   Namibian newspapers that publish in Oshiwambo, for permission to use
   their text.
6. **Funding for paid translation**: a few thousand news-domain sentences
   per language is the single most useful dataset. Grant programmes for
   African language data (for example Lacuna Fund) are a natural fit.
