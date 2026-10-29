# Community translations

Sentence pairs contributed to omalaka by speakers of Oshikwanyama (`kj.tsv`)
and Oshindonga (`ng.tsv`). Other languages get their own file as they are
added (see [docs/roadmap.md](../docs/roadmap.md)).

## Format

Tab-separated, UTF-8, one pair per line, with this header:

| column | meaning |
|---|---|
| `id` | `kj-000001`, `ng-000001`, ...: next free number in the file |
| `lang` | `kj` or `ng` |
| `oshiwambo` | the sentence in Oshikwanyama or Oshindonga |
| `english` | its English translation |
| `domain` | `news`, `health`, `government`, `farming`, `education`, `daily`, `other` |
| `split` | `train`, or `test` for the open test set (see below) |
| `translator` | your name or GitHub handle, as you want to be credited |
| `reviewed_by` | a second speaker who checked the pair; empty until then |
| `note` | optional: anything a reviewer should know |

## What to contribute

- **Write the sentence yourself**, in your own words, and translate it
  yourself. Sentences about everyday life, news events, health, school,
  farming and dealing with government offices are the most useful.
- **Don't copy** sentences from newspapers, books, websites, the Bible,
  religious publications or apps, even if you translate them yourself: the
  original wording belongs to someone else.
- **Don't use machine translation** (Google Translate, ChatGPT, Gemini or any
  other model) for either side.
- Write the language as you would for a reader from your region; note
  dialect features in `note` if they are unusual.

## Test sentences

Pairs with `split=test` form the open test set, so they must never be used
for training anywhere. They need a `reviewed_by` before they count. Aim for
sentences as varied as possible, written first in Oshiwambo, not
translated from English.

## Licence

By opening a pull request that adds or changes rows here, you confirm that
you wrote both sentences yourself (or have the right to contribute them),
and you agree to license them under the
[Creative Commons Attribution 4.0 International licence](https://creativecommons.org/licenses/by/4.0/)
(CC BY 4.0). You will be credited by the name in `translator`.
