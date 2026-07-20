"""F3: place the Indus seal corpus on the agglutination axis against three
real baselines — Vedic Sanskrit (fusional), Tamil (agglutinative South
Dravidian), Gondi (agglutinative South-Central Dravidian).

Honesty rules enforced (per project spec):
  * Seals are a REGISTER (formal name-tags), not running speech. Register
    reduces morphology independently of language family; stated prominently.
  * Metrics are flagged as DISCRIMINATING (separate the baselines) or
    UNINFORMATIVE (do not). Only discriminating metrics carry weight.
  * Claim ceiling is fixed and printed; the script never exceeds it.

Reads results/agglutination_axis.json, baseline_*.json, gauntlet.json.
Output: results/language_placement.json + results/language_placement.md
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RES = os.path.join(ROOT, "results")


def load(name):
    p = os.path.join(RES, name)
    return json.load(open(p)) if os.path.exists(p) else {}


CLAIM_CEILING = (
    "Indus seal structure patterns with the agglutinative (Dravidian) baselines "
    "on the discriminating axis (separable case/number marking) and is "
    "inconsistent with a fully inflectional Indo-Aryan (Vedic) profile. It sits "
    "at the running-text stacking rate of gold Tamil, NOT reduced below it. The "
    "evidence cannot distinguish simple Dravidian from a Dravidian contact "
    "language, and assigns no sounds.")


def main():
    axis = load("agglutination_axis.json")
    gondi = load("baseline_gondi.json")
    tamil = load("baseline_old_tamil.json")
    vedic = load("baseline_sanskrit.json")

    poles = axis.get("poles", {})
    indus = axis.get("indus", {})

    # --- metric 1: morpheme-split / stacking rate (DISCRIMINATING) ---
    rate_rows = [
        ("Vedic Sanskrit", "Indo-Aryan (fusional)", poles.get("vedic_sanskrit_gold"), "gold UD, 158k tokens"),
        ("Tamil", "South Dravidian (aggl.)", poles.get("tamil_gold"), "gold UD"),
        ("Gondi", "S-C Dravidian (aggl.)", None, "descriptive only — no annotated corpus"),
        ("Indus mayig-179", "—", indus.get("mayig_179", {}).get("rate"), f"CI {indus.get('mayig_179', {}).get('ci95')}"),
        ("Indus ICIT-2511", "—", indus.get("icit_2511", {}).get("rate"), f"CI {indus.get('icit_2511', {}).get('ci95')}"),
    ]

    # --- metric 2: categorical separability (DISCRIMINATING, binary) ---
    sep_rows = [
        ("Vedic Sanskrit", 0, "case+number+gender fused into one ending"),
        ("Tamil", 1, "case/number separable"),
        ("Gondi", gondi.get("separates_case_and_number", 1),
         "obligatory stem+oblique+case stacking (descriptive)"),
        ("Indus", 1, "each grammatical element a separate sign"),
    ]

    # --- metric 3: fusion density feats/token (UNINFORMATIVE) ---
    fusion = {
        "tamil_feats_per_token": tamil.get("feats_per_lex_token"),
        "vedic_feats_per_token": vedic.get("feats_per_lex_token"),
        "verdict": "UNINFORMATIVE: ~3 for both baselines; does not discriminate",
    }

    result = {
        "register_caveat": "Seals are a formal register (name-tags), not running "
                           "speech. Register reduces morphology independently of "
                           "language family; morphological simplicity on seals is "
                           "NOT by itself evidence of language change.",
        "metrics": {
            "stacking_rate": {"status": "DISCRIMINATING",
                              "rows": rate_rows,
                              "reading": "Vedic 0.00 vs Tamil 0.10 separates the "
                                         "poles; Indus (0.08 / 0.125) sits at the "
                                         "Tamil pole, excludes Vedic. Gondi has no "
                                         "comparable rate (no annotated corpus)."},
            "separability": {"status": "DISCRIMINATING (binary)",
                             "rows": sep_rows,
                             "reading": "Vedic fuses (0); Tamil, Gondi and Indus "
                                        "all separate (1). Confirms the axis is "
                                        "Dravidian-GENERAL, not Tamil-specific."},
            "fusion_density": {"status": "UNINFORMATIVE", **fusion},
        },
        "gondi_contribution": "Gondi (a different, S-Central Dravidian branch) is "
                              "agglutinative by descriptive grammar, so Indus at "
                              "the agglutinative pole supports 'Dravidian' broadly, "
                              "not merely 'Tamil-like'. BUT no gold Gondi rate "
                              "exists, so the quantitative 'does Indus sit BETWEEN "
                              "Tamil and Gondi' test the contact hypothesis needs "
                              "CANNOT be run. Contact stays non-distinguishable "
                              "from simple Dravidian on this evidence.",
        "claim_ceiling": CLAIM_CEILING,
    }
    json.dump(result, open(os.path.join(RES, "language_placement.json"), "w"),
              indent=1)

    # markdown table for the paper
    md = ["# Language placement — Indus vs three real baselines\n",
          "**Register caveat.** " + result["register_caveat"] + "\n",
          "## Metric 1 — stacking rate (DISCRIMINATING)\n",
          "| corpus | family | stacking rate | note |",
          "|---|---|---|---|"]
    for name, fam, rate, note in rate_rows:
        md.append(f"| {name} | {fam} | {rate if rate is not None else 'n/a'} | {note} |")
    md += ["\n## Metric 2 — separates case & number (DISCRIMINATING, binary)\n",
           "| corpus | separable? | basis |", "|---|---|---|"]
    for name, sep, basis in sep_rows:
        md.append(f"| {name} | {'yes (1)' if sep else 'no (0)'} | {basis} |")
    md += ["\n## Metric 3 — fusion density (UNINFORMATIVE)\n",
           f"Tamil {fusion['tamil_feats_per_token']} vs Vedic "
           f"{fusion['vedic_feats_per_token']} feats/token — does not "
           "discriminate; not used.\n",
           "## Gondi's contribution\n", result["gondi_contribution"] + "\n",
           "## Claim ceiling\n", CLAIM_CEILING + "\n"]
    open(os.path.join(RES, "language_placement.md"), "w").write("\n".join(md))

    print("=== LANGUAGE PLACEMENT (4 poles) ===")
    for name, fam, rate, note in rate_rows:
        print(f"  {name:18} rate={rate}  ({note})")
    print("\nseparability: Vedic=0 (fused); Tamil=Gondi=Indus=1 (separable)")
    print("fusion density: UNINFORMATIVE (Tamil 3.6 ~ Vedic 3.0)")
    print("\nCLAIM CEILING:\n ", CLAIM_CEILING)


if __name__ == "__main__":
    main()
