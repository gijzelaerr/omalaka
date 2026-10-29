# Data sources

Every source that was checked, with what was found, so nobody has to check
twice. **Scripted** datasets have a module in `src/omalaka/datasets/` and are
fetched with `omalaka-download NAME`. Last checked 2026-10-29 unless noted.

Status values: **verified**: licence read at the source and open; **candidate**:
looks open but needs work or a closer check; **rejected**: not open, or
nothing there.

Codes: `kj` Oshikwanyama (ISO 639-3 `kua`), `ng` Oshindonga (`ndo`).

## Scripted

| Name | Kind | Langs | Size | Licence | Status |
|---|---|---|---|---|---|
| `translatewiki` | human | kj | 36 pairs | CC BY 3.0 (stated on the OPUS corpus page) | verified |
| `community` | human | kj, ng | contributions in `community/` | CC BY 4.0 | verified, empty so far |
| `ongiini` | test | kj, ng | 600 items | CC BY 4.0 (`data/oshiwambo_eval/LICENSE` upstream) | verified; English sources only until v1.0 (planned end 2026) |
| `wikipedia` | mono | ng, kj | ngwiki 85 kB, kjwiki 8 kB (bz2); a few hundred lines of text | CC BY-SA 4.0, share-alike | verified; quality poor (see below) |
| `synthetic-madlad` | synthetic | kj | as generated | English: Tatoeba, CC BY 2.0 FR. Kwanyama: MADLAD-400 output (Apache-2.0 model) | verified licence, experimental quality |

Both Wikipedias are closed, read-only wikis. After extraction, much of the
Ndonga text is a copy of the Universal Declaration of Human Rights, plus
English boilerplate and some lines that don't read as Oshindonga. Have a
speaker look before using it for anything.

In short: openly licensed human-translated parallel data for Oshiwambo is
almost non-existent. That is the problem this project has to solve, mostly
through community translation and public-domain texts.

## Candidates

### Namibian legislation and the Government Gazette

- **Law:** Namibia's Copyright and Neighbouring Rights Protection Act 6 of 1994
  says copyright does not subsist in "the official text of any work of a
  legislative, administrative or legal nature, or an official translation" of
  one. Source: Wikimedia Commons' summary of the Act
  ([COM:NOP Namibia](https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Namibia)).
  The primary text on NamibLII returned HTTP 403 to scripts. Quote the section
  from the gazetted Act (Government Gazette 845, 5 May 1994) before relying on
  it.
- **The catch:** laws and gazettes are published in English. The exemption
  covers *official* translations only. Translations made by NGOs, such as the
  Konrad-Adenauer-Stiftung's Oshiwambo Constitution or the Legal Assistance
  Centre's guides to laws in Oshikwanyama, are probably their own copyrighted
  works. They need the publisher's permission, which is worth asking for: the
  Constitution would give 1-2k aligned sentences.
- **Gazettes:** [Gazettes.Africa](https://gazettes.africa/gazettes/na/) hosts
  Namibian gazettes but states no reuse terms on its about page. They also
  include private notices (estates, companies), which are not "official
  texts". Expect little or no Oshiwambo. Low priority.

### Public-domain Bible translations

Not in the open [eBible](https://ebible.org/) corpus for any Namibian
language. (eBible's "Nama", `nmx`, is a language of Papua New Guinea.)

- **Oshindonga, Martti Rautanen:** New Testament 1903, whole Bible translated
  by about 1920. Rautanen died in 1926, so under Namibia's life + 50 years
  the editions he authored, such as the 1903 New Testament, are likely in the
  public domain. The complete Bible was printed later and may include other
  editors' work. Check the edition and the rules for posthumous publication
  before using it. Later revisions by others (the Bible Society of Namibia's
  current edition) are in copyright. To use
  it: find scans of an early printing (Finnish mission archives, the National
  Library of Finland), OCR them, and align verses with a public-domain
  English Bible (World English Bible, KJV). The orthography is older than
  today's Oshindonga, so normalize it or mark it as such. Religious domain:
  earlier experiments showed religious training text leaks into news
  translations, so mix it in sparingly.
- **Oshikwanyama:** No pre-1950s edition with a known translator and date
  found yet.
- **Otjiherero:** an 1849 selection of Bible stories and hymns on archive.org
  (`heroro-bible-stories-and-hymns-1849`, public domain mark). Old
  orthography, small.
- **Rukwangali:** a 1987 Genesis portion on archive.org
  (`rosettaproject_kwn_gen-1`); probably still in copyright. Not usable
  without permission.

### Universal Declaration of Human Rights

The [UDHR in XML](https://github.com/eric-muller/udhr) project has Oshindonga
(`udhr_ndo.xml`) and Silozi (`udhr_loz.xml`) with the English text: preamble
plus 30 articles, aligned by article, about 100 sentences each. No Kwanyama,
Otjiherero, Khoekhoegowab or Rukwangali there. The translations come from the
OHCHR translation project, which carries an OHCHR copyright notice
(© 1996-2009). The repository states no licence, and secondary sources
disagree on reuse terms. Ask OHCHR, or find its terms page, before
scripting it. Small but clean, formal and human-translated.

### Others

- **WON corpus** (Writing Our Narratives, Nekoto et al., AfricaNLP 2022): about 5.5k
  Oshindonga-English sentences on culture and daily life, the best fit
  there is. Its data and licence are not public anywhere we could find. Ask
  the authors through Masakhane; see [roadmap.md](roadmap.md).
- **meyabase/oshiwambo** (GitHub): an Oshiwambo-English corpus effort from
  dictionaries, Bibles and web articles. The repository's MIT licence appears
  to cover code, and its sources are mixed. Ask before using.
- **Dictionaries**, such as an English-Kwanyama dictionary (1954) and an
  Oshindonga/English dictionary (2004), both on archive.org: example sentences
  would help, but both are probably in copyright. Check case by case.

## Rejected

| Source | Why |
|---|---|
| MT560 / JW300 (`michsethowusu/english-{ndonga,oshiwambo}_sentence-pairs_mt560` on Hugging Face) | Jehovah's Witnesses publications; OPUS withdrew JW300 over copyright, so the re-upload's licence label can't be relied on. Used in the first internal experiments only. |
| News articles with machine-made English | The articles belong to their publisher, and the English came from a commercial LLM whose terms restrict training on its output. |
| Output of commercial LLM or translation APIs | Terms restrict training on the output. |
| OPUS QED (en-kj, 743 pairs) | "made public for RESEARCH purpose only ... All rights reserved" (Qatar Computing Research Institute). |
| Tatoeba (kj, ng) | No sentences in either language; Tatoeba rejects both codes. |
| FLORES+ | No Kwanyama or Ndonga (checked the `openlanguagedata/flores_plus` devtest files). |
| NLLB-200 as a synthetic data source | CC BY-NC 4.0 model; it also doesn't cover these languages. |
| Bible Society of Namibia editions | In copyright. |

## The open test set

There is no openly licensed Oshiwambo → English test set yet. Plan:

1. **Ongiini-Eval-OW v1.0** (CC BY 4.0), when its references are released:
   600 English items translated by a human into both dialects. Per its
   dataset card, the translator sees only the English, with no machine
   drafts, so the references are not post-edits. Its "crafted" and "formal"
   English sources (270 of 600) were drafted with LLM help, and for
   Oshiwambo → English that English is our reference. Report those strata
   separately from the "mined_paraphrased" and "v1_retained" items. It is a
   reversed (translationese) test set for us. Report on its 180-item blind
   split. Its English sources are already in `data/ongiini/sources.jsonl`.
   Pass its test file to `omalaka-prepare --exclude` so it never leaks into
   training.
2. **The omalaka test set:** sentences written *in* Oshikwanyama or
   Oshindonga by native speakers, then translated into English. That makes it
   the right direction, unlike a set translated from English. It is collected through
   `community/` with `split=test`, and every pair must be reviewed by a second
   speaker before it counts. Target: 500 sentences per dialect, spread over
   news, health, government services, farming and daily life.
3. Never: model output, LLM output, or any text from the rejected list
   above.
