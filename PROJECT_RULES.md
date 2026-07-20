# indus-engine — project rules

Computational analysis of the Indus script. Python + pandas, no notebooks; scripts + saved outputs only.

## Data provenance & copyright (non-negotiable)
1. Corpus data derives from: Fuls, *Corpus of Indus Inscriptions* (2nd ed.), Fuls, *A Catalog of Indus Signs* (both received from the author by email — verify redistribution permission with him before ANY public release), Mahadevan 1977 (scanned, OCR-derived), and the MIT-licensed `mayig/indus-valley-script-corpus` (only openly redistributable source).
2. `data/` and `mayig/` are gitignored. Public outputs contain aggregate statistics and figures only, never row-level corpus data from copyrighted sources.

## Encoding invariants
3. Sign codes are 3-digit Wells/ICIT numbers 001–958 (not all used). `000` = illegible sign, `999` = blank space. Code strings print left-to-right but are READ right-to-left: `reading_order = reversed(printed list)`. The mayig corpus uses P-numbers; crosswalk to Wells/M77 lives in `mayig/features/*.json`.
4. Jar sign anchors: P324 = M342 = W740 ≈ 10% of legible tokens, dominant reading-order terminal. Any parse whose jar share is far off ~10% is broken — investigate before analyzing.

## Method rules
5. Every analysis script is deterministic (seeded RNG) and rerunnable end-to-end.
6. Every extraction validates against known published totals in `tests/` before analysis runs. Tests that cannot run at current data scale are SKIPPED with a stated reason, never weakened to pass.
7. Never fabricate, interpolate, or "fix" corpus data. Failed parses go to `results/parse_failures.log` with location; move on.
8. No mock/simulated corpora in this repo. (A fabricated `src/pipeline.py` with invented data was deleted 2026-07-17 — do not reintroduce that pattern.)

## Layout
- `data/raw/` originals (never modified) · `data/parsed/` machine-readable corpus (gitignored)
- `src/parse/` extraction · `src/analysis/` statistical attacks · `src/figures/` charts
- `results/` committed aggregates · `paper/` manuscript · `site/` website · `tests/` validation gates

## Commands
- Full run: `python3 run.py` (parses → tests → analyses)
- Tests only: `python3 -m pytest tests/ -v` (falls back to plain asserts if pytest absent)
