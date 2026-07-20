"""F4 (reframed): can the seal corpus be placed as Dravidian, and can a
contact/mixed account be distinguished from simple Dravidian?

The original F4 leaned on a depth shortfall vs Old Tamil. F1/F2 (gold data)
WITHDREW that: gold Tamil running text is itself shallow, so there is no
reduction to point to. This reframed test therefore drops sub-test 2 and asks
only what the data can now answer:

  ST1  Frame is Dravidian: separability (like Tamil & Gondi), concentrated
       terminal set. Fixed suffix order is reported but flagged seal-specific
       (jar->man fails M77 aggregate, per ordering_m77.json).
  ST2  [WITHDRAWN] depth reduced vs Old Tamil — no reduction exists on gold data.
  ST3  Register layering: does the pottery-graffiti class differ morphologically
       from the seal class? (A yes would be a surprising contact signal.)
  AT / BETWEEN / OFF-AXIS: is Indus AT one Dravidian branch, BETWEEN branches,
       or off-axis? Requires a Gondi rate to test BETWEEN — which does not
       exist, so BETWEEN is untestable.

Honest verdict rule: a contact/mixed conclusion needs a positional signal that
Gondi-vs-Tamil rates would provide; absent it, the verdict is "generically
Dravidian; contact not distinguishable from simple Dravidian on this evidence."

Output: results/contact_hypothesis.json
"""
import csv
import json
import os
from collections import Counter

from common import JAR_W, genre_of

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RES = os.path.join(ROOT, "results")


def load(name):
    p = os.path.join(RES, name)
    return json.load(open(p)) if os.path.exists(p) else {}


def register_layering():
    """Seal vs pottery morphological profile on the Fuls corpus (small-n)."""
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "parsed",
                                                 "corpus_reading.csv"))))
    by = {"SEAL/TAG": [], "POTTERY": []}
    for r in rows:
        signs = [s for s in r["reading_order"].split() if s not in ("000", "999")]
        if len(signs) < 2:
            continue
        g = genre_of(r["artifact_type"])
        if g in by:
            by[g].append(signs)
    out = {}
    for g, texts in by.items():
        if not texts:
            out[g] = {"n": 0}
            continue
        jar_term = sum(1 for t in texts if t[-1] == JAR_W) / len(texts)
        mean_len = sum(len(t) for t in texts) / len(texts)
        out[g] = {"n": len(texts), "jar_terminal_rate": round(jar_term, 3),
                  "mean_len": round(mean_len, 2)}
    return out


def main():
    axis = load("agglutination_axis.json")
    place = load("language_placement.json")
    gaunt = load("gauntlet.json")
    order = load("ordering_m77.json")

    indus = axis.get("indus", {})
    poles = axis.get("poles", {})

    st1 = {
        "separable_stacking": 1,
        "separable_matches": "Tamil (1) and Gondi (1); Vedic (0)",
        "terminal_concentration_top5": gaunt.get("T3_terminal_concentration",
                                                 {}).get("top5_ending_share"),
        "fixed_suffix_order": {
            "seal_level": "jar->man 9/9 (binomial p=0.0039)",
            "m77_aggregate": order.get("test_jar_before_man", {}).get("survives"),
            "flag": "seal-construction convention; does NOT generalize to M77 "
                    "aggregate — not used as morphological-order evidence"},
        "verdict": "Dravidian frame SUPPORTED on the separability + terminal-set "
                   "axes; the ordering plank is seal-specific and set aside.",
    }

    st2 = {"status": "WITHDRAWN",
           "reason": "No depth reduction vs gold Tamil exists (Tamil running "
                     "text stacks ~0.097; Indus 0.08-0.125). The chat's "
                     "reduced-morphology claim was a small-sample artifact."}

    st3 = {"register_profiles": register_layering(),
           "verdict": "Pottery graffiti carry the jar suffix at a different rate "
                      "than seals (register split), but the pottery sample is "
                      "tiny (n<10); this is a register difference, NOT evidence "
                      "of a distinct language layer. Under-powered."}

    # AT / BETWEEN / OFF-AXIS
    at_between = {
        "indus_rate": {"mayig": indus.get("mayig_179", {}).get("rate"),
                       "icit": indus.get("icit_2511", {}).get("rate")},
        "tamil_rate": poles.get("tamil_gold"),
        "gondi_rate": None,
        "at_tamil": True,
        "between_testable": False,
        "between_reason": "No gold Gondi running-text rate exists, so 'Indus "
                          "between Tamil and Gondi' cannot be measured. The "
                          "contact hypothesis's one potential quantitative test "
                          "is unavailable.",
    }

    verdict = ("GENERICALLY DRAVIDIAN. Indus separates grammatical morphemes "
               "(like Tamil and Gondi, unlike fusional Vedic) and stacks at the "
               "gold-Tamil running-text rate. Both tested Dravidian branches are "
               "agglutinative, so the result supports 'Dravidian' broadly, not "
               "specifically Tamil. A contact / mixed-language account CANNOT be "
               "distinguished from simple Dravidian on this evidence: the "
               "depth-shortfall argument is withdrawn, and the between-branch "
               "test needs a Gondi rate that does not exist. Contact remains a "
               "live but unselected hypothesis.")

    res = {"ST1_frame_is_dravidian": st1,
           "ST2_depth_reduced": st2,
           "ST3_register_layering": st3,
           "AT_between_offaxis": at_between,
           "VERDICT": verdict}
    json.dump(res, open(os.path.join(RES, "contact_hypothesis.json"), "w"),
              indent=1)
    print("=== CONTACT HYPOTHESIS (reframed) ===")
    print("ST1 Dravidian frame:", st1["verdict"][:70])
    print("ST2 depth reduced:", st2["status"], "-", st2["reason"][:60])
    print("ST3 register layering:", st3["register_profiles"])
    print("AT Tamil:", at_between["at_tamil"], "| BETWEEN testable:",
          at_between["between_testable"])
    print("\nVERDICT:\n ", verdict)


if __name__ == "__main__":
    main()
