"""Attack 4: Kober-style context vectors, cosine pairs, greedy clusters.
Blind check: does the terminal paradigm {jar, lance, tree, bearer...}
re-emerge without supervision?"""
import math
from collections import Counter, defaultdict

from common import SUF_P, load_features, load_mayig, save_result, write_table


def context_vectors(texts):
    ctx = defaultdict(Counter)
    freq = Counter(s for t, *_ in texts for s in t)
    for t, *_ in texts:
        for i, s in enumerate(t):
            ctx[s]["L:" + (t[i - 1] if i else "<S>")] += 1
            ctx[s]["R:" + (t[i + 1] if i < len(t) - 1 else "<E>")] += 1
    return ctx, freq


def cos(a, b):
    num = sum(a[k] * b[k] for k in set(a) | set(b))
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da * db else 0.0


def main():
    feats = load_features()
    texts = load_mayig()
    ctx, freq = context_vectors(texts)
    cands = sorted([s for s, c in freq.items() if c >= 6],
                   key=lambda s: -freq[s])
    pairs = []
    for i, a in enumerate(cands):
        for b in cands[i + 1:]:
            pairs.append((round(cos(ctx[a], ctx[b]), 3), a, b))
    pairs.sort(reverse=True)

    # greedy agglomerative clusters at 0.65
    parent = {s: s for s in cands}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for sim, a, b in pairs:
        if sim >= 0.65:
            parent[find(a)] = find(b)
    clusters = defaultdict(list)
    for s in cands:
        clusters[find(s)].append(s)
    clusters = [sorted(v) for v in clusters.values() if len(v) > 1]

    # blind terminal-paradigm check
    jar_cluster = next((c for c in clusters if "P324" in c), [])
    recovered = sorted(set(jar_cluster) & set(SUF_P))
    jar_lance = next((sim for sim, a, b in pairs
                      if {a, b} == {"P324", "P217"}), None)

    write_table("substitution_pairs.csv", ["cosine", "sign_a", "sign_b",
                                           "desc_a", "desc_b"],
                [(sim, a, b, feats.get(a, {}).get("desc", "")[:40],
                  feats.get(b, {}).get("desc", "")[:40])
                 for sim, a, b in pairs[:30]])
    save_result("attack_substitution", {
        "n_candidate_signs": len(cands),
        "top10_pairs": pairs[:10],
        "clusters_at_0.65": clusters,
        "jar_cluster": jar_cluster,
        "suf_class_members_recovered_blind": recovered,
        "jar_lance_cosine": jar_lance,
    })
    print(f"[substitution] jar~lance cosine={jar_lance} (pilot: 0.83)")
    print(f"[substitution] jar cluster (blind): {jar_cluster}")


if __name__ == "__main__":
    main()
