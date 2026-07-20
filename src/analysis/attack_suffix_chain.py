"""Attack 6: the jar's neighborhood — pre/post context, two-deep ending
chains, and the [X]-jar-[person] name formula, on both corpora."""
from collections import Counter

from common import (JAR_P, JAR_W, load_features, load_fuls, load_mayig,
                    save_result)

PERSON_P = {"P013", "P004", "P009", "P194"}    # person-like signs (mayig)


def neighborhood(texts, jar):
    pre, post = Counter(), Counter()
    after_jar = 0
    for t, *_ in texts:
        for i, s in enumerate(t):
            if s == jar:
                if i:
                    pre[t[i - 1]] += 1
                if i < len(t) - 1:
                    post[t[i + 1]] += 1
                    after_jar += 1
    return pre, post, after_jar


def main():
    feats = load_features()
    res = {}

    mayig = load_mayig()
    pre, post, after = neighborhood(mayig, JAR_P)
    formula = 0
    for t, *_ in mayig:
        for i in range(1, len(t) - 1):
            if t[i] == JAR_P and t[i + 1] in PERSON_P:
                formula += 1
                break
    res["mayig_179"] = {
        "jar_pre_top8": [(s, c, feats.get(s, {}).get("desc", "")[:36])
                         for s, c in pre.most_common(8)],
        "jar_post_top5": [(s, c, feats.get(s, {}).get("desc", "")[:36])
                          for s, c in post.most_common(5)],
        "jar_nonfinal_occurrences": after,
        "x_jar_person_formula_texts": formula,
    }

    fuls = load_fuls()
    pre, post, after = neighborhood(fuls, JAR_W)
    res["fuls_preview"] = {
        "jar_pre_top8": pre.most_common(8),
        "jar_post_top5": post.most_common(5),
        "jar_nonfinal_occurrences": after,
    }

    save_result("attack_suffix_chain", res)
    print(f"[suffix_chain] mayig X-jar-person formula: "
          f"{res['mayig_179']['x_jar_person_formula_texts']} texts (pilot: 9x jar->man)")
    print(f"[suffix_chain] fuls jar-pre top3: {res['fuls_preview']['jar_pre_top8'][:3]}")


if __name__ == "__main__":
    main()
