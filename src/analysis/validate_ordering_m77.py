"""Validate the T5 fixed-order pairs against Mahadevan's independent Table I.

The corrected seal-level construction is [stem] + jar + man (man LAST) and
tree + jar (tree earlier). A construction where element X precedes element Y
predicts, at the aggregate level, that X is LESS strictly text-final than Y
(the earlier element is less often the very last sign).

Predictions from the ordering:
  tree < jar  (tree earlier)  => tree FIN-share  <  jar FIN-share
  jar  < man  (man last)      => jar  FIN-share  <= man FIN-share

We check both against M77 FIN shares the sequence analysis never saw.
"""
import json
import os

from common import JAR_M, load_features, load_m77_table1


def fin_share(m77, m):
    r = m77.get(m)
    return round(r["fin"] / r["tot"], 3) if r and r["tot"] else None


def main():
    feats = load_features()
    m77 = load_m77_table1()

    jar_m = [342]
    man_m = feats.get("P013", {}).get("m77", [])       # man
    tree_m = feats.get("P086", {}).get("m77", [])       # tree
    lance_m = feats.get("P217", {}).get("m77", [])      # lance

    def shares(ms):
        return {m: fin_share(m77, m) for m in ms if m in m77}

    jar = shares(jar_m)
    man = shares(man_m)
    tree = shares(tree_m)
    lance = shares(lance_m)

    jar_fin = jar[342]
    # aggregate (token-weighted) FIN share for multi-mapped signs
    def wshare(ms):
        tot = sum(m77[m]["tot"] for m in ms if m in m77)
        fin = sum(m77[m]["fin"] for m in ms if m in m77)
        return round(fin / tot, 3) if tot else None
    man_w, tree_w, lance_w = wshare(man_m), wshare(tree_m), wshare(lance_m)

    tree_pred = tree_w < jar_fin
    man_pred = jar_fin <= man_w

    res = {
        "jar_fin_share": jar_fin,
        "man_fin_shares": man, "man_weighted": man_w,
        "tree_fin_shares": tree, "tree_weighted": tree_w,
        "lance_fin_shares": lance, "lance_weighted": lance_w,
        "test_tree_before_jar": {
            "prediction": "tree FIN < jar FIN",
            "tree_fin": tree_w, "jar_fin": jar_fin,
            "survives": bool(tree_pred),
            "note": "tree earlier than jar in seals (10/15) -> tree should be "
                    "less final. " + ("CONFIRMED by M77." if tree_pred else
                    "NOT confirmed.")},
        "test_jar_before_man": {
            "prediction": "jar FIN <= man FIN (man is last)",
            "jar_fin": jar_fin, "man_fin": man_w,
            "survives": bool(man_pred),
            "note": ("CONFIRMED: man is at least as text-final as jar."
                     if man_pred else
                     "NOT confirmed at aggregate level: man's overall FIN "
                     "share (%.3f) is below jar's (%.3f). The jar->man order is "
                     "a seal-construction fact; across all M77 contexts man "
                     "appears in many non-terminal roles, so aggregate finality "
                     "does not reflect the construction. Honest mixed result." %
                     (man_w, jar_fin))},
    }
    path = os.path.join(os.path.dirname(__file__), "..", "..", "results",
                        "ordering_m77.json")
    json.dump(res, open(path, "w"), indent=1)
    print("=== T5 ordering vs M77 Table I ===")
    print(f"jar (M342) FIN share: {jar_fin}")
    print(f"man (M1)   FIN share: {man_w}")
    print(f"tree (M161-9) weighted FIN: {tree_w}   lance (M211): {lance_w}")
    print(f"\ntree<jar : predicted tree<jar FIN -> {tree_w} < {jar_fin} = "
          f"{'SURVIVES' if tree_pred else 'FAILS'}")
    print(f"jar<man  : predicted jar<=man FIN -> {jar_fin} <= {man_w} = "
          f"{'SURVIVES' if man_pred else 'FAILS (honest mixed result)'}")


if __name__ == "__main__":
    main()
