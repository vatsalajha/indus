"""Breakthrough 1: register split by artifact genre (jar-terminal, SUF-
terminal, text lengths). Pilot prediction: pottery ~0% jar-terminal,
seals ~40%."""
from collections import defaultdict

from common import JAR_W, genre_of, load_features, load_fuls, save_result

# mayig SUF class mapped to Wells numbers (from features crosswalk)
def suf_wells():
    from common import SUF_P
    feats = load_features()
    out = set()
    for p in SUF_P:
        out |= set(feats.get(p, {}).get("wells", []))
    return out


def main():
    SUF_W = suf_wells()
    groups = defaultdict(list)
    for t, r in load_fuls():
        groups[genre_of(r["artifact_type"])].append(t)
    res = {}
    for g, ts in sorted(groups.items()):
        jar_t = sum(1 for t in ts if t[-1] == JAR_W)
        suf_t = sum(1 for t in ts if t[-1] in SUF_W)
        lens = sorted(len(t) for t in ts)
        res[g] = {"n": len(ts),
                  "jar_terminal": f"{jar_t}/{len(ts)}",
                  "suf_terminal": f"{suf_t}/{len(ts)}",
                  "median_len": lens[len(lens) // 2],
                  "len_range": [lens[0], lens[-1]]}
    save_result("genre_split", res)
    for g, v in res.items():
        print(f"[genre] {g:9} n={v['n']:3} jar-term {v['jar_terminal']:>6} "
              f"suf-term {v['suf_terminal']:>6} med-len {v['median_len']}")


if __name__ == "__main__":
    main()
