"""M77 Table I ground-truth validation of the unsupervised slot classes.

The SUF and OPEN classes were learned with no positional supervision from
179 CISI seals (P-numbers). Mahadevan's Table I gives independent, corpus-
wide positional ground truth (417 signs, 13,372 tokens, 3,573 lines).

Test A (SUF vs FIN): mean FIN share of the SUF-class signs vs the corpus.
Test B (OPEN vs INI): mean INI share of the OPEN-class signs vs the corpus.
Test C (frequency-matched permutation): for each class, 10,000 random sign
sets drawn from frequency-matched bins (same size), p = fraction of random
sets whose mean share >= the class's. Frequency matching kills the "your
classes are just the common signs" objection.
"""
import random

from common import OPEN_P, SEED, SUF_P, load_features, load_m77_table1, save_result


def m77_of(pset, feats):
    out = []
    for p in pset:
        out += feats.get(p, {}).get("m77", [])
    return sorted(set(out))


def share(row, k):
    return row[k] / row["tot"] if row["tot"] else 0.0


def freq_matched_p(class_signs, table, key, iters=10000):
    rng = random.Random(SEED)
    # frequency bins: log2 bins over TOT
    import math
    bins = {}
    for m, row in table.items():
        b = int(math.log2(row["tot"])) if row["tot"] > 0 else 0
        bins.setdefault(b, []).append(m)
    obs = sum(share(table[m], key) for m in class_signs) / len(class_signs)
    ge = 0
    for _ in range(iters):
        pick = []
        for m in class_signs:
            b = int(math.log2(table[m]["tot"]))
            pick.append(rng.choice(bins[b]))
        val = sum(share(table[m], key) for m in pick) / len(pick)
        if val >= obs:
            ge += 1
    return obs, ge / iters


def main():
    feats = load_features()
    table = load_m77_table1()
    corpus_fin = sum(r["fin"] for r in table.values()) / sum(r["tot"] for r in table.values())
    corpus_ini = sum(r["ini"] for r in table.values()) / sum(r["tot"] for r in table.values())

    suf_m = [m for m in m77_of(SUF_P, feats) if m in table]
    open_m = [m for m in m77_of(OPEN_P, feats) if m in table]

    a_obs, a_p = freq_matched_p(suf_m, table, "fin")
    b_obs, b_p = freq_matched_p(open_m, table, "ini")

    res = {
        "corpus_baseline": {"fin_share": round(corpus_fin, 3),
                            "ini_share": round(corpus_ini, 3)},
        "test_A_suf_vs_fin": {
            "class_m77_signs": suf_m,
            "mean_fin_share": round(a_obs, 3),
            "p_freq_matched": a_p,
            "per_sign": {m: round(share(table[m], "fin"), 3) for m in suf_m}},
        "test_B_open_vs_ini": {
            "class_m77_signs": open_m,
            "mean_ini_share": round(b_obs, 3),
            "p_freq_matched": b_p,
            "per_sign": {m: round(share(table[m], "ini"), 3) for m in open_m}},
        "method": "test C machinery: 10k permutations, log2-frequency-matched "
                  "bins, seed=7",
    }
    save_result("m77_validation", res)
    print(f"[m77] corpus FIN share {corpus_fin:.3f}; SUF-class mean FIN "
          f"{a_obs:.3f} (p={a_p})")
    print(f"[m77] corpus INI share {corpus_ini:.3f}; OPEN-class mean INI "
          f"{b_obs:.3f} (p={b_p})")


if __name__ == "__main__":
    main()
