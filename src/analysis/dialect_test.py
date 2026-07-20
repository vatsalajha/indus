"""Breakthrough 2: per-site template coverage + top bigrams, bootstrap CIs.
Pilot-scale honesty: only Mohenjo-daro (n=27) and Allahdino (n=12) have
enough texts; others reported with n only."""
import random
from collections import Counter, defaultdict

from common import SEED, load_fuls, save_result
from attack_positional import positional
from attack_template import coverage, monotone
from common import NUM_WELLS


def bootstrap_ci(texts, classes, iters=2000):
    rng = random.Random(SEED)
    covs = []
    for _ in range(iters):
        sample = [texts[rng.randrange(len(texts))] for _ in texts]
        covs.append(coverage(sample, classes))
    covs.sort()
    return covs[int(0.025 * iters)], covs[int(0.975 * iters)]


def main():
    fuls = load_fuls()
    _, classes = positional(fuls, min_freq=4, num_set=NUM_WELLS)
    overall = coverage(fuls, classes)
    lo, hi = bootstrap_ci(fuls, classes)
    res = {"overall": {"n": len(fuls), "coverage": round(overall, 3),
                       "ci95": [round(lo, 3), round(hi, 3)]}}
    groups = defaultdict(list)
    for t, r in fuls:
        groups[r["site"]].append((t, r))
    flagged = []
    for site, ts in sorted(groups.items()):
        entry = {"n": len(ts)}
        if len(ts) >= 8:
            c = coverage(ts, classes)
            slo, shi = bootstrap_ci(ts, classes)
            entry.update({"coverage": round(c, 3),
                          "ci95": [round(slo, 3), round(shi, 3)]})
            if shi < lo or slo > hi:
                flagged.append(site)
            bi = Counter()
            for t, _ in ts:
                for a, b in zip(t, t[1:]):
                    bi[f"{a}->{b}"] += 1
            entry["top_bigrams"] = bi.most_common(10)
        res[site] = entry
    res["sites_outside_overall_ci"] = flagged
    save_result("dialect_test", res)
    print(f"[dialect] overall {overall:.2f} CI [{lo:.2f},{hi:.2f}]; "
          f"flagged: {flagged or 'none'}")
    for s, v in res.items():
        if isinstance(v, dict) and "coverage" in v and s != "overall":
            print(f"  {s:14} n={v['n']:3} cov={v['coverage']} CI={v['ci95']}")


if __name__ == "__main__":
    main()
