"""Do the pilot's structural findings replicate on the 14x-larger corpus?

Runs the terminal-paradigm and 5-slot template tests on the 2,536-seal
yajnadevam/ICIT corpus (Wells numbering), fully independently: slot classes
are re-derived on THIS corpus by the same unsupervised positional rules, not
imported from the pilot. Compares headline numbers to the 179-seal pilot.

Provenance caveat: yajnadevam_corpus.csv is an open third-party compilation
(GPL-v3), integrity-checked (jar 11.4%, mean len 4.4, 591 signs — all match
published ICIT values) but not authoritatively vetted seal-by-seal. Treated as
a strong independent corpus, reported with that caveat.
"""
import csv
import os
import random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "data", "parsed", "yajnadevam_corpus.csv")
SEED = 7
ORDER = {"OPEN": 0, "EARLY": 1, "NUM": 1, "BODY": 2, "RARE": 2,
         "PRESUF": 3, "SUF": 4}
# Wells stroke-numeral set (Set 01 low codes) — same convention as common.py
NUM_WELLS = {f"{n:03d}" for n in range(1, 60)}


def load():
    texts = []
    with open(SRC) as f:
        for r in csv.DictReader(f):
            signs = [s for s in r["reading_order"].split()
                     if s not in ("000", "999")]
            if len(signs) >= 2:
                texts.append(signs)
    return texts


def derive_slots(texts, min_freq=15):
    freq = Counter(s for t in texts for s in t)
    pos = defaultdict(list)
    initc, termc = Counter(), Counter()
    for t in texts:
        L = len(t)
        for i, s in enumerate(t):
            if L > 1:
                pos[s].append(i / (L - 1))
        initc[t[0]] += 1
        termc[t[-1]] += 1
    cls = {}
    for s, c in freq.items():
        if c < min_freq:
            continue
        mean = sum(pos[s]) / len(pos[s]) if pos[s] else 0.5
        ish, tsh = initc[s] / c, termc[s] / c
        if s in NUM_WELLS:
            cls[s] = "NUM"
        elif tsh > 0.5:
            cls[s] = "SUF"
        elif ish > 0.4:
            cls[s] = "OPEN"
        elif mean > 0.66:
            cls[s] = "PRESUF"
        elif mean < 0.33:
            cls[s] = "EARLY"
        else:
            cls[s] = "BODY"
    return cls, freq


def monotone(t, cls):
    cs = [ORDER[cls.get(s, "RARE")] for s in t]
    return all(cs[i] <= cs[i + 1] or {cs[i], cs[i + 1]} <= {1, 2}
               for i in range(len(cs) - 1))


def main():
    texts = load()
    cls, freq = derive_slots(texts)
    total = sum(freq.values())
    rng = random.Random(SEED)

    # jar-terminal
    jar_term = sum(1 for t in texts if t[-1] == "740") / len(texts)
    suf = {s for s, c in cls.items() if c == "SUF"}
    suf_term = sum(1 for t in texts if t[-1] in suf) / len(texts)

    # template vs shuffled (permutation)
    real = sum(1 for t in texts if monotone(t, cls)) / len(texts)
    shuf_scores = []
    for _ in range(300):
        c = 0
        for t in texts:
            tt = t[:]
            rng.shuffle(tt)
            if monotone(tt, cls):
                c += 1
        shuf_scores.append(c / len(texts))
    shuf = sum(shuf_scores) / len(shuf_scores)
    p = sum(1 for x in shuf_scores if x >= real) / len(shuf_scores)

    # terminal concentration
    endc = Counter(t[-1] for t in texts)
    top5 = sum(c for _, c in endc.most_common(5)) / sum(endc.values())
    hapax = sum(1 for _, c in freq.items() if c == 1)

    res = {
        "n_texts": len(texts), "n_tokens": total, "n_signs": len(freq),
        "mean_len": round(sum(len(t) for t in texts) / len(texts), 2),
        "hapax_frac": round(hapax / len(freq), 3),
        "jar_frequency_pct": round(100 * freq["740"] / total, 1),
        "jar_terminal_rate": round(jar_term, 3),
        "suf_class_wells": sorted(suf, key=int),
        "suf_terminal_rate": round(suf_term, 3),
        "template_coverage": round(real, 3),
        "template_shuffled": round(shuf, 3),
        "template_p": p,
        "distinct_final_signs": len(endc),
        "top5_ending_share": round(top5, 3),
        "pilot_comparison": {
            "jar_freq": "10.1% (pilot) -> " + str(round(100*freq['740']/total,1)) + "% (14x)",
            "template": "75%/23% (pilot) -> " + str(round(real*100)) + "%/" +
                        str(round(shuf*100)) + "% (14x)",
            "top5_enders": "71.4% (pilot) -> " + str(round(top5*100)) + "% (14x)",
        },
    }
    import json
    json.dump(res, open(os.path.join(ROOT, "results",
                                     "bigcorpus_validation.json"), "w"), indent=1)
    print("=== BIG-CORPUS REPLICATION (2,536 seals, Wells numbering) ===")
    for k in ("n_texts", "n_tokens", "n_signs", "mean_len", "hapax_frac",
              "jar_frequency_pct", "jar_terminal_rate", "suf_terminal_rate",
              "template_coverage", "template_shuffled", "template_p",
              "distinct_final_signs", "top5_ending_share"):
        print(f"  {k:22} {res[k]}")
    print("  SUF class (Wells):", res["suf_class_wells"])
    print("\n  vs pilot:")
    for k, v in res["pilot_comparison"].items():
        print("   ", k, ":", v)


if __name__ == "__main__":
    main()
