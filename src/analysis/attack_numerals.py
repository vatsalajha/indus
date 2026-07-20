"""Attack 5: strict stroke-numeral phrases — what gets counted, and the
half-height vs full-height stroke series (mayig descriptions distinguish
them; strict list, no keyword contamination)."""
from collections import Counter

from common import load_features, load_mayig, save_result, write_table

# strict stroke numerals from mayig feature descriptions, hand-audited:
FULL = {"P121": 1, "P145": 2, "P147": 3, "P202": 4}          # full-height
HALF = {"P122": 2, "P123": 3, "P126": 4, "P144": 5, "P056": 6, "P325": 7}


def main():
    feats = load_features()
    texts = load_mayig()
    nums = set(FULL) | set(HALF)
    counted = Counter()
    series_next = {"full": Counter(), "half": Counter()}
    for t, *_ in texts:
        for i, s in enumerate(t):
            if s in nums and i < len(t) - 1:
                nxt = t[i + 1]
                counted[nxt] += 1
                series_next["full" if s in FULL else "half"][nxt] += 1
    top = counted.most_common(12)
    fish = [s for s in counted if feats.get(s, {}).get("desc", "").lower()
            .startswith("fish")]
    fish_total = sum(counted[s] for s in fish)
    write_table("numeral_counted.csv", ["sign", "count", "desc"],
                [(s, c, feats.get(s, {}).get("desc", "")[:50]) for s, c in
                 counted.most_common()])
    save_result("attack_numerals", {
        "strict_numeral_list": {"full_height": FULL, "half_height": HALF},
        "counted_top12": [(s, c, feats.get(s, {}).get("desc", "")[:40])
                          for s, c in top],
        "fish_signs_counted_total": fish_total,
        "fish_share_of_counted": round(fish_total / sum(counted.values()), 3),
        "full_series_top5": series_next["full"].most_common(5),
        "half_series_top5": series_next["half"].most_common(5),
    })
    print(f"[numerals] counted-noun top5: {top[:5]}")
    print(f"[numerals] fish share of counted objects: "
          f"{100 * fish_total / sum(counted.values()):.0f}%")


if __name__ == "__main__":
    main()
