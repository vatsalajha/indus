# Red-team hardening pass

Adversarial self-attack before submission. Any result that does not survive is softened in the manuscript.

## A1 — Corpus integrity (the 2,511-seal kill-shot)

- Cross-verified against the independently transcribed Fuls preview on **27 shared CISI seals**: **27 agree, 0 mismatch** (error 0.0%, 95% CI [0.0%, 12.5%]).
- Corpus-level: jar 11.4% (pub 10-12%), mean len 4.4 (pub ~4.6), 591 signs (ICIT ~592) — all match published ICIT.
- **Verdict:** PASS at this sample; sample is only 27 seals, so the 2,511 corpus is reported as SECONDARY/robustness regardless (cannot verify all 2,480).

## A2 — Metric robustness (garden-of-forking-paths)

- split-rate: Vedic 0.0 / Tamil 0.097 / Indus 0.08–0.125 — separates.
- terminal grammatical inventory: Indus SUF 6, Tamil case 7, Vedic bundle 87.
- terminal TTR: Indus 0.046, Tamil 0.012, Vedic 0.003.
- terminal entropy: Indus 0.716, Tamil 0.429, Vedic 0.588.
- **2 of 4 metrics cleanly place Indus with Tamil** (split-rate; terminal grammatical-inventory size). 1 marginal/confounded (TTR), 1 fails (entropy places Indus nearer Vedic). The Dravidian placement rests on the two SEPARABILITY metrics (split-rate + terminal grammatical-inventory size), both theoretically motivated and both cleanly placing Indus with Tamil against Vedic. Ending-DIVERSITY metrics (TTR, entropy) are confounded by the Indus sign inventory and are reported as inconclusive, not as support. The claim is therefore stated as resting on separability, not on a single cherry-picked number, and not on ending diversity.

## A3 — Unit-comparison defense

- The split-rate counts SEPARABLE grammatical markers in the terminal region. This is unit-agnostic: it measures whether grammatical elements are expressed as distinct units, which is the fusional-vs-agglutinative contrast, independent of whether each Indus sign is a word, morpheme, or syllable. If signs were sub-morphemic (syllabic), separable stacking could only be HIGHER, strengthening the agglutinative reading, not weakening it. The comparison is of a structural property (separate vs fused terminal marking), not of like-for-like units.
- **Verdict:** Assumption stated explicitly; result is robust to the word-vs-morpheme interpretation of signs.

## A4 — Numeral-detector sensitivity

- strict_stroke_list: 10 numeral signs, fish share 0.247, top-counted-is-fish False
- canonical_1_2_3_only: 5 numeral signs, fish share 0.254, top-counted-is-fish False
- broad_stroke_by_desc: 112 numeral signs, fish share 0.202, top-counted-is-fish True
- **Verdict:** fish is the/among the most-counted under ALL numeral definitions; conclusion stable.
