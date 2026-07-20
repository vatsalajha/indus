# The semantic gauntlet — ranking readings by structural survival

Reproducible: `python3 src/analysis/semantic_gauntlet.py` → `results/gauntlet.json`.
Corpus: mayig 175 texts (seals). These test meaning-claims, not just structure.
Every number is what the corpus says; failures are reported as failures.

## Survived (ranked by strength)

| # | Claim | Result | Verdict |
|---|---|---|---|
| T2 | **jar = grammatical suffix** | attaches to 55 distinct left-neighbours, only 13 right (L/R ratio **4.23**); fish is the mirror (0.65) | **STRONGEST** — pure suffix fingerprint |
| T3 | morphology is **agglutinative, small closed terminal set** | 33 signs ever final; top-5 enders = **71.4%** of all endings; jar+lance co-occur in only **1** text | strong Dravidian-leaning signal |
| T5 | **fixed suffix order** | jar→man consistent in **9/9** texts (binomial p=0.0039; permutation p=0.004) | significant; rigid agglutinative order |
| T6 | **jar = case/honorific, not plural** | 71% of jar-texts have a numeral vs 74% of non-jar — number-independent | survives |
| T4 | **name-and-title formula** | 55 distinct stems feed one jar suffix across 98 positions | survives (also consistent with any many-nouns-one-suffix system) |
| T1 | **fish = countable noun** | mean position 0.55; 67/70 fish placements are before the jar-suffix (stem side) | survives |

## Wounded / did not survive

| # | Claim | Result | Verdict |
|---|---|---|---|
| T1b | **fish = star-names specifically** (numeral+fish = asterisms) | of 44 numeral+fish compounds, only 4 take a following suffix and 3 sit at text-end; **37 sit bare mid-text** like counted goods | **NOT clearly supported** — distribution is commodity-like, not named-entity-like. Wounds the strong Parpola reading (which was always philological, not distributional). |
| T7 | **modifier-before-head word order** (numeral before noun) | numeral-before-content / after = **0.82** (essentially flat) | **NULL** — not spun as positive |

## Correction to the chat run (important)

The chat reported "**man → jar**, man first, 9/9," and inferred man was *not*
terminal. The reproducible script finds the **opposite direction**: the fixed
pair is **jar → man**, with man LAST (9/9, p=0.004). This *restores* the
original reading — man is a terminal person-classifier sitting after the jar
suffix. The real formula is **[stem] + jar + man** in locked order. The
fixed-order finding (the decipherment-relevant part) stands; only its direction
label was reversed in conversation. This is exactly why we harden chat results
into seeded scripts.

## Honest scope

Sequence tests (T1, T4, T5, T7) run on ~175 texts = **~5% of the ~3,573 that
exist**. Positional tests validated against M77 Table I (T2, T3 signatures) use
Mahadevan's **complete** 13,372-token counts. So "jar = suffix" is corpus-
complete on positional evidence; the ordering/sequence results await the full
corpus. The tree→jar pair (10/15, p=0.30) is the honest weak spot — tree was
always our shakiest SUF member (five-way M-number crosswalk).
