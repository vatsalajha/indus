"""Attack 3: 5-slot monotone template with one-shuffle control AND a proper
1000-iteration permutation p-value; coverage split by genre and site."""
import random
from collections import defaultdict

from common import (SEED, genre_of, load_features, load_fuls, load_mayig,
                    save_result)
from attack_positional import positional
from common import NUM_WELLS

ORDER = {"OPEN": 0, "EARLY": 1, "NUM": 1, "BODY": 2, "RARE": 2,
         "PRESUF": 3, "SUF": 4}


def monotone(t, classes):
    cs = [ORDER[classes.get(s, "RARE")] for s in t]
    return all(cs[i] <= cs[i + 1] or {cs[i], cs[i + 1]} <= {1, 2}
               for i in range(len(cs) - 1))


def coverage(texts, classes):
    seqs = [t for t, *_ in texts]
    return sum(1 for t in seqs if monotone(t, classes)) / len(seqs)


def perm_test(texts, classes, iters=1000):
    rng = random.Random(SEED)
    seqs = [t for t, *_ in texts]
    real = coverage(texts, classes)
    ge = 0
    shuf_covs = []
    for _ in range(iters):
        cov = 0
        for t in seqs:
            tt = t[:]
            rng.shuffle(tt)
            if monotone(tt, classes):
                cov += 1
        cov /= len(seqs)
        shuf_covs.append(cov)
        if cov >= real:
            ge += 1
    mean_shuf = sum(shuf_covs) / len(shuf_covs)
    return real, mean_shuf, ge / iters


def main():
    feats = load_features()
    res = {}

    mayig = load_mayig()
    _, mayig_cls = positional(mayig, min_freq=6,
                              desc=lambda s: feats.get(s, {}).get("desc", ""))
    real, shuf, p = perm_test(mayig, mayig_cls)
    res["mayig_179"] = {"n_texts": len(mayig), "coverage": round(real, 3),
                        "shuffled_mean": round(shuf, 3), "p_value": p}

    fuls = load_fuls()
    _, fuls_cls = positional(fuls, min_freq=4, num_set=NUM_WELLS)
    real, shuf, p = perm_test(fuls, fuls_cls)
    res["fuls_preview"] = {"n_texts": len(fuls), "coverage": round(real, 3),
                           "shuffled_mean": round(shuf, 3), "p_value": p}

    # splits on the Fuls corpus (genre / site) — small-n, report counts
    for split_name, keyf in [("by_genre", lambda r: genre_of(r["artifact_type"])),
                             ("by_site", lambda r: r["site"])]:
        groups = defaultdict(list)
        for t, r in fuls:
            groups[keyf(r)].append((t, r))
        out = {}
        for g, ts in sorted(groups.items()):
            if len(ts) >= 3:
                out[g] = {"n": len(ts),
                          "coverage": round(coverage(ts, fuls_cls), 3)}
            else:
                out[g] = {"n": len(ts), "coverage": None}
        res[split_name] = out

    save_result("attack_template", res)
    print(f"[template] mayig: {res['mayig_179']}")
    print(f"[template] fuls:  {res['fuls_preview']}")
    print(f"[template] genre: {res['by_genre']}")


if __name__ == "__main__":
    main()
