# Brishti Guha's Indus work — location and comparison

## What was found (honest)

Brishti Guha is an economist (game theory / mechanism design; e.g. *J. Economic
Behavior & Organization* 2014). A targeted search (Crossref, Semantic Scholar,
web) did **not** locate a peer-reviewed *computational/statistical* Indus-script
paper authored by her. The two arXiv "Harappan seal" statistics papers that
surface are by others (Rao, arXiv:1812.00049; Mahesh T C, arXiv:2604.23582),
not Guha.

Her documented Indus engagement is as a **public commentator advocating the
Sanskrit reading** of the script:
- a *Times of India* article endorsing **Yajnadevam's cryptanalytic
  decipherment** of the Indus script as Sanskrit;
- a public lecture, "Indus Script Decoded: Sanskrit Origin Proves No Aryan
  Invasion" (Sangam Talks).

So the located position is advocacy, not an independent method paper. Stated
plainly to avoid overclaiming what she has published.

## Does it agree or conflict with our findings? — CONFLICTS

Her advocated position (Indus encodes **Sanskrit**, via Yajnadevam's method)
runs against our results on two axes:

1. **Result.** Our gold-baseline morphology test (against UD Vedic Sanskrit and
   Tamil) places the Indus seal corpus at the **agglutinative (Dravidian)**
   pole on the discriminating axis and **excludes a fully inflectional
   Indo-Aryan (Vedic/Sanskrit) profile** for the seal corpus. That is evidence
   against a Sanskrit identification of these texts.
2. **Method.** Yajnadevam's approach (fitting the corpus to grammatically valid
   Sanskrit via regex / set-intersection cryptogram search) is the **overfitting
   failure mode** this project is explicitly built to avoid — short texts +
   allograph freedom + "best-fit-any-Sanskrit" almost guarantees a fit. Our
   method assigns **no sounds**, uses shuffle controls and frequency-matched
   permutation, and validates against independent ground truth (Mahadevan
   Table I) and gold cross-linguistic baselines.

## Handling in the project

- We do **not** adopt or rebut her phonetic claims in the manuscript (out of
  scope; the paper is decipherment-agnostic).
- Where relevant, the Sanskrit-origin position is the Indo-Aryan hypothesis our
  morphology result speaks against — and we state that as an exclusion of a
  *fully inflectional Indo-Aryan* profile for the seal corpus, nothing stronger.
- No rebus / phonetic-substitution "translation pass" is implemented anywhere
  (the Yajnadevam failure mode; violates the project's claim ceiling).
