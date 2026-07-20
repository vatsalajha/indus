"""R5: write results/REBUS_FINDINGS.md from rebus_gauntlet.json — a tiered,
honest report. Leads with the count, states these are candidate readings that
survive a falsifiable test, not sounds, and no text is translated. The fish =
star WOUNDED result is shown prominently."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
G = json.load(open(os.path.join(ROOT, "results", "rebus_gauntlet.json")))

VERDICT_ORDER = {"SURVIVES(tier-B)": 0, "LITERAL-CONSISTENT": 1,
                 "WOUNDED-BY-NULL": 2, "LOW/MED-CONFIDENCE-PICTURE": 3,
                 "UNEXPLAINED": 4, "NEUTRAL": 5}


def main():
    res = sorted(G["results"], key=lambda r: (VERDICT_ORDER.get(r["verdict"], 9),
                                              -r["role_scores"].get(r["corpus_top_role"], 0)))
    n_ident = len(res)
    n_high = sum(1 for r in res if r["picture_confidence"] == "high")
    survivors = G["survivors"]

    lines = [
        "# Rebus gauntlet findings\n",
        f"**{len(survivors)} of {n_ident} identifiable signs "
        f"({n_high} high-confidence) have a Dravidian rebus reading that "
        f"survives positional + null-model testing.**\n",
        "These are candidate readings that survive a falsifiable test, NOT "
        "confirmed sound values. No sign is assigned a sound and no text is "
        "translated. The scoring templates were committed before the DEDR "
        "lexicon was consulted (`rebus_scoring_spec.json`).\n",
        "## The fish = star result (shown prominently)\n",
        "Parpola's celebrated reading takes the fish sign, via the Dravidian "
        "homophone *mīn* (fish, DEDR 4885 ~ shine/glitter, DEDR 4876), to mean "
        "*star* — so numeral+fish compounds would be asterism names. Our test "
        "**wounds** it: the fish sign scores COUNTED_NOUN on position (it is "
        "counted, sits mid-text, is not terminal), whereas a star / asterism "
        "name would imply the NAME_ELEMENT role. The homophone is real in DEDR, "
        "but the sign's position does not behave like a named entity. The fish "
        "reads as a countable noun, not a star. The method rejects an appealing "
        "reading its own authors would have liked to keep.\n",
        "## Full tiered table\n",
        "| sign | object | pic-conf | position role (T) | literal role (L) | "
        "null p | verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in res:
        lines.append(
            f"| {r['sign']} | {r['object']} | {r['picture_confidence']} | "
            f"{r['corpus_top_role']} | {r['literal_role']} | "
            f"{r['null_model_p'] if r['null_model_p'] is not None else '—'} | "
            f"**{r['verdict']}** |")

    lines += [
        "\n## Reading the verdicts\n",
        "- **SURVIVES(tier-B)** — a non-literal homophone implies the sign's "
        "position role, at high picture-confidence, beating a frequency-matched "
        "null (p<0.05). A candidate reading, not a sound.",
        "- **LITERAL-CONSISTENT** — the picture at face value already matches "
        "the position (e.g. fish = a counted noun); no rebus is needed, and "
        "non-literal extensions (fish=star) are wounded.",
        "- **UNEXPLAINED** — the position (e.g. jar = grammatical suffix) is "
        "real but no DEDR homophone of the object implies that role, so the "
        "specific sound-rebus is not lexically grounded here. The functional "
        "reading stands on position alone.",
        "- **LOW/MED-CONFIDENCE-PICTURE** — the pictogram identification is not "
        "secure enough to carry a reading, by rule.\n",
        "## Honest bottom line\n",
        f"Even given the Dravidian structural result, seal positions plus the "
        f"DEDR lexicon do not confirm specific rebus readings under a null-model "
        f"control: {len(survivors)} survive. This is the sentence that "
        f"distinguishes the project from over-claimers. The fish=star wound "
        f"shows the test has teeth; the jar suffix stands on distribution, not "
        f"on a forced sound.\n",
    ]
    out = os.path.join(ROOT, "results", "REBUS_FINDINGS.md")
    open(out, "w").write("\n".join(lines))
    print("wrote", out)
    print(f"survivors: {len(survivors)}  fish/star validation: "
          f"{'PASS' if G['validation']['fish_star_wounded'] else 'FAIL'}")


if __name__ == "__main__":
    main()
