# Data acquisition (D1–D3) — findings

Goal: get past the 179-seal (~5% of corpus) ceiling without buying the Fuls book.

## D1 — mine the Mahadevan 1977 PDF for sequences → NOT VIABLE (honest)

The archive.org Mahadevan PDF's "Texts" and "Concordance" sections print each
text as **glyph images**, with only the text-ID and a line/field code as
machine-readable numbers (e.g. `4371 · 210001` beside a glyph row). They do
**not** print M-number sign sequences. Recovering sequences would need
glyph-recognition CV — the same wall as Table I, worse (arbitrary glyphs, not
digits). Premise of "the concordance prints M-numbers" is false for this book.
No parser built; that would be spin. (The machine-readable M77 concordance
that Yadav/Rao used was digitized separately by hand and shared privately.)

## D2 — pull other open repos → MAJOR UNLOCK (14× corpus)

| repo | license | contents | usable? |
|---|---|---|---|
| **yajnadevam/indus-website** | GPL-3.0 | `population-script.sql`: relational corpus — `GLYPHSEQUENCE` (2,536 seals, 11,135 sign tokens, Wells numbering), `SEAL` (CISI/site), `INSCRIPTION` (direction) | **YES** |
| CharlesCNorton/harappan-verified | MIT | Coq formalization of Indus structure; no raw sequence corpus | reference only |

**The yajnadevam SQL is a genuine ICIT/CISI sequence corpus.** Verification:
- Seals 5–9 (`740-235`, `740-390-590`, `740-904-33-705-235`, …) are
  **identical** to the Fuls-preview Allahdino inscriptions we independently
  parsed — confirming it is real ICIT-derived data, not fabricated.
- Integrity check vs published ICIT values: jar (740) = **11.4%** (published
  10-12%); mean length **4.4** (published ~4.6); **591 signs** (ICIT ~592);
  top signs 740/002/400/220/032 match known high-frequency ICIT signs. PASS.
- We use ONLY the factual sequences. We adopt NONE of that project's Sanskrit
  decipherment claims (data and interpretation are separable).

Parser: `src/parse/parse_yajnadevam_sql.py` → `data/parsed/yajnadevam_corpus.csv`
(gitignored). Provenance caveat: it is an open third-party compilation,
integrity-checked but not authoritatively vetted seal-by-seal; treated as a
strong independent robustness corpus, not the primary vetted corpus.

### Structural findings REPLICATE at 14× scale
`src/analysis/validate_bigcorpus.py` → `results/bigcorpus_validation.json`.
Slot classes re-derived independently on the 2,511 Wells-numbered texts:

| metric | pilot (179) | big corpus (2,511) |
|---|---|---|
| **5-slot template vs shuffled** | 75% / 23%, p<0.001 | **71% / 27%, p=0.0** |
| jar frequency | 10.1% | 11.4% |
| SUF-class terminal rate | ~0.63–0.70 | 0.695 |
| terminal paradigm (blind) | jar,lance,tree,bearer… | re-emerges (740,520,407,400…) |
| hapax fraction | 42% | 33% (better rare-sign sampling) |
| distinct final signs | 33 | 225 (multi-genre) |

The five-slot grammar — the paper's crown result — holds on a corpus fourteen
times larger, independently numbered. This is the strongest robustness evidence
the project has.

## D3 — extend mayig ourselves → SCAFFOLDED (see src/parse/mayig_transcribe/)

The mayig corpus (MIT) stops at M-199 and transcribes from CISI Vol. 1, which
we hold as `cisi_vol1_joshi_parpola1987.pdf`. A transcription harness pairs each
CISI plate with the mayig JSON schema so M-200+ can be added in the same format
and contributed upstream. Lower priority now that D2 supplies 2,500 sequences,
but the route is real and legal. Given D2, the realistic corpus path is:
**use the yajnadevam sequences as the scale corpus; keep mayig as the
richly-annotated (P/Wells/M77 + descriptions) reference corpus.**
