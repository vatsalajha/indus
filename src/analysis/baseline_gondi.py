"""Third morphological pole: Gondi (South-Central Dravidian), from REAL
descriptive linguistics — NOT hand-invented paradigm arrays.

No gold/annotated Gondi treebank exists (checked: absent from Universal
Dependencies). The CGNetSwara Hindi-Gondi parallel corpus (19k sentences)
exists but ships no morpheme segmentation and its download is JS-gated, so a
gold running-text stacking RATE comparable to the Tamil/Vedic UD numbers is not
obtainable. This is documented honestly rather than faked.

What IS available and citable is the descriptive morphology of Gondi, which
places it categorically on the fusional-vs-agglutinative axis:

Documented facts (sources below):
  - Gondi is classified as agglutinative (Krishnamurti 2003, who classifies all
    Dravidian as agglutinative; standard grammars: Grammar of Gondi 1919; Moss
    1950; Pagdi 1954; Subrahmanyam).
  - Nouns take a separable OBLIQUE stem-formant (-d-, -t-, -n-, -ṭ-, -ɸ) and
    THEN a case marker. Crucially, "when case markers are added, all nouns have
    an oblique marker" — i.e. an inflected noun obligatorily stacks
    stem + oblique + case as SEPARABLE morphemes (2+ bound morphemes).
  - Plural is a separate suffix (-r / -ir / -ur, gendered), stacked before case.
  - Word order is SOV, modifier-before-head (canonical Dravidian).

Therefore Gondi's morpheme-SEPARABILITY is high and obligatory: it separates
number and case into distinct stacked suffixes, exactly the agglutinative
signature, and the opposite of Vedic's fused portmanteau endings.

Metric reported: categorical `separates_case_and_number` (1 = separable/
agglutinative, 0 = fused/inflectional), the axis that gold Tamil (1) and gold
Vedic (0) anchor. Gondi = 1, from descriptive grammar. No numeric running-text
rate is asserted.

Output: results/baseline_gondi.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

GONDI = {
    "corpus": "Gondi (South-Central Dravidian) — descriptive placement",
    "branch": "South-Central Dravidian (distinct from Tamil's South Dravidian)",
    "gold_corpus_available": False,
    "reason_no_rate": "No UD/annotated Gondi treebank exists; CGNetSwara "
                      "parallel corpus has no morpheme segmentation. A "
                      "running-text stacking rate comparable to the Tamil/Vedic "
                      "gold numbers cannot be computed without fabrication.",
    "documented_morphology": {
        "type": "agglutinative",
        "oblique_markers": ["-d-", "-t-", "-n-", "-ṭ-", "-ɸ"],
        "case_stacking": "stem + OBLIGATORY oblique + case (>=2 separable "
                         "bound morphemes on every case-marked noun)",
        "plural_suffixes": ["-r", "-ir", "-ur"],
        "gender_suffixes": {"masc": ["-a:l", "-o:r"], "fem": ["-a:r"]},
        "word_order": "SOV, modifier-before-head",
    },
    "sources": [
        "Krishnamurti, B. 2003. The Dravidian Languages. Cambridge UP "
        "(classifies all Dravidian, incl. Gondi, as agglutinative).",
        "Grammar of Gondi as Spoken in the Betul District. Madras Govt Press, 1919.",
        "Moss, C.F. 1950. An Introduction to the Grammar of the Gondi Language.",
        "Pagdi, S.R. 1954. A Grammar of the Gondi Language.",
    ],
    # the categorical axis coordinate: separates case and number = agglutinative
    "separates_case_and_number": 1,
    "placement": "agglutinative pole (same side as Tamil, opposite Vedic), "
                 "established from descriptive grammar, not a running-text rate",
}


def main():
    json.dump(GONDI, open(os.path.join(ROOT, "results",
                                       "baseline_gondi.json"), "w"), indent=1)
    print("=== Gondi baseline (descriptive) ===")
    print("branch:", GONDI["branch"])
    print("gold corpus available:", GONDI["gold_corpus_available"])
    print("type:", GONDI["documented_morphology"]["type"])
    print("case stacking:", GONDI["documented_morphology"]["case_stacking"])
    print("categorical axis (separates case & number):",
          GONDI["separates_case_and_number"], "-> agglutinative pole")
    print("\nLIMITATION:", GONDI["reason_no_rate"])


if __name__ == "__main__":
    main()
