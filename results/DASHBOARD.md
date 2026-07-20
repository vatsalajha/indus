# indus-engine results dashboard (pilot mode, 2026-07-17)

Data scale: 179-seal mayig/CISI corpus + 53-text Fuls preview corpus + M77 Table I (417 signs / 13,372 tokens). Full Fuls corpus not yet on disk; full-book gates skipped (see data/raw/MANIFEST.md).

| test | pilot prediction | this run | verdict | note |
|---|---|---|---|---|
| jar share (mayig) | 9.9% | 10.1% | **PASS** | P324 top-ranked |
| jar share (Fuls preview) | ~10% | 10.3% | **PASS** | W740 top-ranked |
| jar share (M77 Table I) | ~10% | 10.4% (1395/13372) | **PASS** | row 342 = table max |
| slot template, mayig | 75% vs 22% shuffled | 75% vs 23%, p=0.000 | **PASS** | 1000-iter permutation |
| slot template, Fuls | transfers | 89% vs 52%, p=0.000 | **PASS*** | high shuffled baseline: only 10 signs classifiable at n=53 — many texts trivially monotone; treat as weak evidence |
| jar~lance cosine | 0.83 | 0.831 | **PASS** |  |
| terminal paradigm recovered blind | {jar,lance,tree,bearer,man,box} | 6/6 in one cluster | **PASS** | cluster: P004, P013, P086, P217, P301, P324 |
| fish = most-counted noun | fish dominates numeral phrases | fish share of counted = 25% | **PASS** | strict stroke-numeral list, no keyword contamination |
| X-jar-person name formula | recurs (9x) | 9 texts | **PASS** |  |
| pottery register split | pottery ~0% jar-terminal, seals ~40% | pottery 0/7, seals 13/34 | **PASS** | pottery also shorter (median 2 vs 4) |
| motif independence | text content ~ animal: no dependence | chi2 p=0.8136 | **PASS** | small-n caveat; jar-terminal similar across motifs |
| dialect differences | unknown (exploratory) | no site outside overall CI | **NULL** | only Mohenjo-daro (n=27) & Allahdino (n=10) testable |
| ligature decomposition | coverage change? | PARKED | **PARKED** | compound tables absent from Catalog preview |

## M77 Table I ground-truth validation (the headline)

- corpus baselines: FIN share 0.223, INI share 0.225
- **Test A** — unsupervised SUF class (M77 signs [1, 15, 161, 162, 167, 168, 169, 211, 254, 342]): mean FIN share **0.632** vs 0.223 baseline, frequency-matched p = **0.0** (10k permutations)
- **Test B** — unsupervised OPEN class (M77 signs [17, 54, 55, 150, 267, 391]): mean INI share **0.573** vs 0.225 baseline, p = **0.0041**
- Interpretation: classes learned with zero positional supervision on 179 seals are strongly FIN/INI-dominant across Mahadevan's full 3,573-line corpus — independent replication across corpora, numbering systems, and 45 years.

## Honest failures / limitations
- Fuls-preview template test is weak (10 classifiable signs).
- Dialect test underpowered below n≈30/site.
- All 'reading' claims remain hypothesis-tier; these results are structural only.

## Class membership & crosswalk reconciliation (for the Methods section)

Exact SUF class (learned on mayig P-numbers) with ALL retained M77 mappings
and per-sign FIN shares (n = occurrences in Table I):

| P-sign | description | M77 mapping(s) → FIN share (n) |
|---|---|---|
| P004 | burden-bearer | M15 → .730 (126) |
| P013 | man | M1 → .642 (134) |
| P086 | tree | M161 → .500 (4); M162 → .425 (212); M167 → .143 (7); M168 → 1.0 (1); M169 → .542 (240) |
| P217 | lance | M211 → .811 (227) |
| P301 | hatched box | M254 → .836 (73) |
| P324 | jar | M342 → .696 (1395) |

OPEN class: P011→M150, P076→M54+M55, P256→M17, P378→M391, P385→M267.

**Variant sensitivity (explains chat-vs-script 0.676 vs 0.632):** unweighted
mean over all 10 M-mappings = **0.632** (the reproducible script's number,
quoted in the manuscript); token-weighted mean = 0.669; first-mapping-only
(6 signs) = 0.702. The spread is entirely driven by the tree sign's
one-to-five crosswalk fan-out (M162/M167 dilute the unweighted mean). All
variants sit 2.8–3.1× above the 0.223 corpus baseline; the conclusion does
not depend on the variant. The script's convention (retain all mappings,
unweighted) is the most conservative and is the one reported.
