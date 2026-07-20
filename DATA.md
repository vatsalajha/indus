# Reproducing the corpus data

This repository ships **code, aggregate statistics, and figures only**. No
row-level corpus data is included — the corpora derive from copyrighted
publications and one third-party compilation, none of which are redistributed
here. Each analysis script reads from a local `data/` directory you regenerate
from the original sources, as documented below. A correct regeneration
reproduces the shipped `results/` exactly (deterministic, seed = 7).

## 1. Primary corpus — 179 CISI unicorn seals (openly licensed)

MIT-licensed digitization of *Corpus of Indus Seals and Inscriptions* Vol. 1
(Joshi & Parpola 1987), seals M-1…M-199:

```
git clone https://github.com/mayig/indus-valley-script-corpus  mayig
```

`src/analysis/common.py` reads `mayig/corpus/**/*.json` and
`mayig/features/*.json`. This is the only freely redistributable corpus; do not
re-host it here — clone it.

## 2. Transfer corpus — Fuls, *Corpus of Indus Inscriptions*

Parse the inscription tables from a legally obtained copy of Fuls's *Corpus of
Indus Inscriptions* (Mathematica Epigraphica 3) into `data/parsed/corpus.csv`
and `corpus_reading.csv`. The PDF has a text layer; the parser regex-matches the
`+NNN-NNN+` sign codes. The free "view inside" preview yields 53 texts.

## 3. Ground truth — Mahadevan 1977 Table I (417 signs × positions)

`data/parsed/m77_table1.csv` (SOL/INI/MED/FIN/TOT per sign) is a transcription
of Table I of Mahadevan, *The Indus Script* (ASI Memoir 77, 1977). Because that
table is copyrighted expression, it is **not redistributed here**. To reproduce
it from the archive.org scan: render book pp. 717-723, transcribe each
half-page's five numeric columns in sign order, and validate that every row
satisfies `TOT = SOL+INI+MED+FIN` and that the five column sums equal the
printed grand totals `(190, 3010, 7196, 2976, 13372)` — two checks over 2,085
values that catch any transcription error.

## 4. Robustness corpus — ~2,511 ICIT seal sequences (third party)

An independent machine-readable compilation of seal sequences in Wells/ICIT
numbering exists in a public third-party database. Parse only the raw
`GLYPHSEQUENCE` rows into `data/parsed/yajnadevam_corpus.csv`. Use ONLY the
factual sequences; adopt none of that source's interpretive claims. Integrity
was verified against the Fuls transcription (27/27 shared seals agree) and
against published ICIT frequencies. This corpus is treated as SECONDARY
throughout and is never redistributed here.

## 5. Language baselines — Universal Dependencies treebanks (gold)

For the morphological placement, clone the gold treebanks into `data/external/`:

```
git clone https://github.com/UniversalDependencies/UD_Tamil-TTB      data/external/UD_Tamil-TTB
git clone https://github.com/UniversalDependencies/UD_Sanskrit-Vedic data/external/UD_Sanskrit-Vedic
```

`src/analysis/baseline_from_ud.py` reads these (override the location with the
`$UD_DATA` environment variable).

## 6. Rebus lexicon — DEDR (Burrow & Emeneau)

The rebus gauntlet reads the Dravidian Etymological Dictionary. Scrape it from
the Digital South Asia Library into `data/parsed/dedr.csv` (entry_no, headword,
gloss, languages). ~5,548 entries; spot-check that the *mīn* fish (DEDR 4885)
and shine/glitter (DEDR 4876) entries are present.

## Layout after regeneration

```
data/raw/        original PDFs (never modified, never published)
data/parsed/     machine-readable corpus (gitignored, never published)
data/external/   UD treebanks (gitignored, never published)
mayig/           cloned CISI digitization (gitignored, never published)
```
