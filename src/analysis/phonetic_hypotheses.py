"""G2: a TIERED, SOURCED register of published phonetic proposals — a ranking,
never a reading. Only signs with a published rebus proposal are listed. For
each, our own structural tests are recorded as support / wound / neutral.

HARD RULES (enforced):
  * Nothing above tier B is ever presented as a reading.
  * Tier C items appear only as "disputed hypotheses".
  * NO full phonetic transliteration of any text is produced — that is the
    Yajnadevam failure mode and violates the project's claim ceiling.

Confidence tiers (from the project's master sign table):
  A = broad agreement on the descriptive fact (e.g. stroke = numeral)
  B = a plausible, best-supported reading (e.g. jar = suffix; fish = mīn)
  C = speculative / single-proponent (e.g. numeral+fish = star names)

Output: results/phonetic_hypotheses.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

HYPOTHESES = [
    {
        "sign": "stroke numerals (P121/P145/P147…)",
        "candidate": "numeral values 1–7",
        "structural_gloss": "NUM",
        "proponent": "consensus (Mahadevan 1977; Parpola 1994)",
        "tier": "A",
        "our_test": "support",
        "note": "Numeral status is a descriptive fact, not a sound; the values "
                "1–7 are near-universally accepted.",
    },
    {
        "sign": "jar (P324 / M342 / W740)",
        "candidate": "grammatical case / honorific suffix (Dravidian)",
        "structural_gloss": "SUFFIX:case/honorific",
        "proponent": "Mahadevan 1977; Parpola 1994",
        "tier": "B",
        "our_test": "support",
        "note": "Gauntlet T2 (L/R ratio 4.23, affix fingerprint) and T6 "
                "(number-independent) support a case/honorific suffix. No sound "
                "assigned.",
    },
    {
        "sign": "fish (P050 / M059)",
        "candidate": "mīn 'fish' (Dravidian rebus)",
        "structural_gloss": "COUNTED / content noun",
        "proponent": "Parpola 1994 (after Heras)",
        "tier": "B",
        "our_test": "support (as 'fish/countable noun')",
        "note": "Gauntlet T1 supports fish as a countable content noun "
                "(position 0.55, stem-side). Glossed 'fish/countable noun', "
                "NOT 'star'.",
    },
    {
        "sign": "numeral + fish compound",
        "candidate": "asterism / star names (e.g. Old Tamil aṟumīṉ 'six-star')",
        "structural_gloss": "NUM + COUNTED",
        "proponent": "Parpola 1994",
        "tier": "C",
        "our_test": "WOUND",
        "note": "DISPUTED. Gauntlet T1 discriminator: of 44 numeral+fish "
                "compounds, 37 sit bare mid-text like tallied commodities and "
                "only 7 behave like named entities. Distribution favours "
                "counted-commodity over star-name. Shown only as a disputed "
                "hypothesis.",
    },
    {
        "sign": "lance / arrow (P217 / M211)",
        "candidate": "ampu → non-masculine / case suffix",
        "structural_gloss": "SUFFIX",
        "proponent": "Mahadevan 1977",
        "tier": "C",
        "our_test": "neutral",
        "note": "Lance is in the recovered terminal (suffix) class structurally, "
                "but the specific sound is single-proponent and untested here.",
    },
    {
        "sign": "man (P013 / M001)",
        "candidate": "person / agent classifier",
        "structural_gloss": "PERSON-classifier",
        "proponent": "Mahadevan 1977 (positional)",
        "tier": "C",
        "our_test": "neutral (structural only)",
        "note": "Gauntlet T5 places man after jar in seals (fixed order), "
                "consistent with a terminal person classifier; no sound assigned.",
    },
]

REFUSAL = ("This project does NOT produce a phonetic transliteration of any "
           "text. Attaching sounds to sign sequences and reading them off as "
           "language is the overfitting failure mode (Yajnadevam) the project "
           "is built to avoid. We rank published hypotheses by tier and record "
           "whether our structural tests support or wound them; we do not read.")


def main():
    out = {
        "claim_ceiling": REFUSAL,
        "tiers": {"A": "descriptive fact", "B": "plausible best-supported",
                  "C": "speculative / disputed — never a reading"},
        "hypotheses": HYPOTHESES,
        "summary": {
            "tier_A": [h["sign"] for h in HYPOTHESES if h["tier"] == "A"],
            "tier_B": [h["sign"] for h in HYPOTHESES if h["tier"] == "B"],
            "tier_C_disputed": [h["sign"] for h in HYPOTHESES if h["tier"] == "C"],
            "wounded_by_our_tests": [h["sign"] for h in HYPOTHESES
                                     if h["our_test"] == "WOUND"],
        },
    }
    json.dump(out, open(os.path.join(ROOT, "results",
                                     "phonetic_hypotheses.json"), "w"), indent=1)
    print("=== PHONETIC HYPOTHESES (ranked, never read) ===")
    for h in HYPOTHESES:
        print(f"  [{h['tier']}] {h['sign']:28} -> {h['candidate'][:40]:40} "
              f"[{h['our_test']}]")
    print("\nHARD RULE:", REFUSAL[:90], "...")


if __name__ == "__main__":
    main()
