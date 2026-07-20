# indus-engine

Reproducible, decipherment-agnostic structural analysis of the Indus script.

An unsupervised distributional method, given only raw sign sequences from 179
CISI unicorn seals, recovers the functional sign classes of the Indus script —
the terminal "suffix" paradigm known since Mahadevan (1977), an opener paradigm,
dual numeral series, and a pre-suffix class. Those classes are then validated
against the complete positional statistics of Mahadevan's concordance (13,372
sign occurrences) that the method never saw, replicated on an independent
2,511-seal corpus, and placed on a morphological axis calibrated against
gold-annotated Tamil and Vedic Sanskrit.

**No claim of phonetic decipherment is made.** This is a structural benchmark:
it shows the grammar-bearing architecture of the script is objectively,
reproducibly present, and it exports as a test any future decipherment claim
should be required to beat.

> Accompanying manuscript: *Unsupervised Recovery of Functional Sign Classes in
> the Indus Script, Validated Against Mahadevan's Positional Concordance.*
> Preprint DOI: **[to be added on OSF deposit]**. Please cite the preprint.

## Headline results (all in `results/`, reproducible from code)

| finding | value |
|---|---|
| jar sign frequency | 10.1% / 10.3% / 10.4% (CISI / ICIT / M77) |
| terminal paradigm recovered blind | 6/6 signs in one cluster; jar~lance cosine 0.83 |
| 5-slot template vs shuffled | 75% vs 23% (primary); 71% vs 27% at 14× scale; p<0.001 |
| suffix class text-final (M77 ground truth) | 0.63 vs 0.22 baseline, frequency-matched p<0.0001 |
| morphological placement | agglutinative (Dravidian) rate; fusional Indo-Aryan excluded |
| fish = countable noun / fish = star | survives / **wounded** by our own test |
| phonetic rebus survivals under null model | **0 of 13** identifiable signs |

Honest nulls, wounds, withdrawals and the red-team pass are all reported — see
`results/DASHBOARD.md`, `results/REBUS_FINDINGS.md`, and `results/REDTEAM.md`.
The integrity scorecard is `results/figures/figD_scorecard.png`.

## Reproduce

Corpus data is **not** included (copyright + third-party provenance).
Regenerate it from the original sources per **[DATA.md](DATA.md)**, then:

```
pip install -r requirements.txt
python3 src/analysis/agglutination_axis.py    # the language-placement result
python3 src/analysis/m77_validation.py         # the ground-truth validation
python3 src/analysis/redteam.py                # the adversarial hardening pass
python3 src/figures/make_figures.py            # figures 1-6
python3 src/figures/make_figures2.py           # figures A-D
```

Everything is deterministic (seed = 7); the shipped `results/` are the
reference outputs.

## License

Code in this repository is released under the **MIT License** (see `LICENSE`).

**The underlying corpus data is NOT included and is NOT covered by that
license.** It derives from copyrighted publications (Joshi & Parpola 1987;
Fuls 2022; Mahadevan 1977) and a third-party compilation, and remains under its
original sources' terms. This repository redistributes no inscription data —
only code, aggregate statistics, and figures. `DATA.md` documents how to obtain
and regenerate the corpora from their original sources.
