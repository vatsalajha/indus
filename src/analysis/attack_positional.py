"""Attack 2: positional stats + slot classes per sign (both corpora)."""
from collections import Counter, defaultdict

from common import (NUM_WELLS, load_features, load_fuls, load_mayig,
                    save_result, write_table)


def positional(texts, min_freq, num_set=None, desc=lambda s: ""):
    freq = Counter(s for t, *_ in texts for s in t)
    pos = defaultdict(list)
    init = Counter()
    term = Counter()
    for t, *_ in texts:
        L = len(t)
        for i, s in enumerate(t):
            if L > 1:
                pos[s].append(i / (L - 1))
        init[t[0]] += 1
        term[t[-1]] += 1
    rows = []
    classes = {}
    for s, c in freq.most_common():
        if c < min_freq:
            continue
        mean = sum(pos[s]) / len(pos[s]) if pos[s] else 0.5
        ish = init[s] / c
        tsh = term[s] / c
        if num_set and s in num_set:
            cls = "NUM"
        elif "stroke" in desc(s).lower() and "vertical" in desc(s).lower():
            cls = "NUM"
        elif tsh > 0.5:
            cls = "SUF"
        elif ish > 0.4:
            cls = "OPEN"
        elif mean > 0.66:
            cls = "PRESUF"
        elif mean < 0.33:
            cls = "EARLY"
        else:
            cls = "BODY"
        classes[s] = cls
        rows.append((s, c, round(mean, 3), round(ish, 3), round(tsh, 3), cls))
    return rows, classes


def main():
    feats = load_features()
    fuls_rows, fuls_cls = positional(load_fuls(), min_freq=4,
                                     num_set=NUM_WELLS)
    mayig_rows, mayig_cls = positional(load_mayig(), min_freq=6,
                                       desc=lambda s: feats.get(s, {}).get("desc", ""))
    write_table("positional_fuls.csv",
                ["sign", "freq", "mean_pos", "init_share", "term_share", "class"],
                fuls_rows)
    write_table("positional_mayig.csv",
                ["sign", "freq", "mean_pos", "init_share", "term_share", "class"],
                mayig_rows)
    by_class = defaultdict(list)
    for s, cls in mayig_cls.items():
        by_class[cls].append(s)
    save_result("attack_positional", {
        "fuls_n_classified": len(fuls_rows),
        "mayig_n_classified": len(mayig_rows),
        "mayig_classes": {k: sorted(v) for k, v in by_class.items()},
        "fuls_classes": {k: sorted(s for s, c in fuls_cls.items() if c == k)
                         for k in set(fuls_cls.values())},
    })
    print(f"[positional] mayig classes: "
          f"{ {k: len(v) for k, v in by_class.items()} }")
    print(f"[positional] fuls signs classified: {len(fuls_rows)} (min_freq=4; small-n)")


if __name__ == "__main__":
    main()
