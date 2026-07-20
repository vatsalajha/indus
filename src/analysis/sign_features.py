"""Positional feature vector per sign, shared by the rebus gauntlet. These are
the corpus signatures the committed scoring templates read. Computed on the
mayig corpus (P-numbers, has descriptions + crosswalk).

Features per sign:
  freq, terminal, initial, mean_pos, after_numeral, stem_before_jar, left_div
"""
import os
from collections import Counter, defaultdict

from common import JAR_P, load_features, load_mayig

NUMERALS = {"P121", "P145", "P147", "P202", "P122", "P123", "P126",
            "P144", "P056", "P325"}


def compute(min_freq=6):
    texts = load_mayig()
    freq = Counter(s for t, *_ in texts for s in t)
    initc, termc = Counter(), Counter()
    pos = defaultdict(list)
    after_num = Counter()
    before_jar = Counter()
    left = defaultdict(set)
    for t, *_ in texts:
        L = len(t)
        for i, s in enumerate(t):
            if L > 1:
                pos[s].append(i / (L - 1))
            if i:
                left[s].add(t[i - 1])
                if t[i - 1] in NUMERALS:
                    after_num[s] += 1
            if i < L - 1 and t[i + 1] == JAR_P:
                before_jar[s] += 1
        initc[t[0]] += 1
        termc[t[-1]] += 1
    feats = {}
    for s, c in freq.items():
        if c < min_freq:
            continue
        rl = (len(left[s]) / max(len({} ), 1)) if False else None
        feats[s] = {
            "freq": c,
            "terminal": round(termc[s] / c, 3),
            "initial": round(initc[s] / c, 3),
            "mean_pos": round(sum(pos[s]) / len(pos[s]), 3) if pos[s] else 0.5,
            "after_numeral": round(after_num[s] / c, 3),
            "stem_before_jar": round(before_jar[s] / c, 3),
            "left_div": len(left[s]),
        }
    # L/R diversity ratio (distinct left / distinct right)
    right = defaultdict(set)
    for t, *_ in texts:
        for i, s in enumerate(t):
            if i < len(t) - 1:
                right[s].add(t[i + 1])
    for s in feats:
        r = len(right[s])
        feats[s]["lr_ratio"] = round(feats[s]["left_div"] / r, 2) if r else 99.0
    return feats


if __name__ == "__main__":
    f = compute()
    for s in ("P324", "P050", "P385"):
        print(s, f.get(s))
