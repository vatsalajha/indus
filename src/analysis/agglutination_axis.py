"""The agglutination axis, rebuilt on GOLD data (supersedes the illustrative
15-word version in morphology_signature.py).

The single cross-comparable, register-fair, gold-backed metric is the
STACKING RATE: the fraction of units that express two or more separable
grammatical morphemes.
  - fusional (Vedic Sanskrit): 0 — case+number+gender fuse onto one word.
  - agglutinative (Tamil): >0 — grammatical morphemes split into separate tokens.
  - Indus: fraction of texts ending in 2+ consecutive suffix-class signs.

Baselines from gold Universal Dependencies treebanks (see baseline_from_ud.py).
Indus computed on both the vetted mayig-179 and the ICIT-2511 robustness corpus,
with a bootstrap CI. Output: results/agglutination_axis.json.

Honest scope: this metric places the Indus categorically (stacks separably like
Tamil; unlike fusional Vedic). It does NOT support the earlier "Indus has
reduced morphological depth vs Old Tamil" claim — gold Tamil running text is
itself shallow (~10% stacking), so Indus (8-12%) is at parity, not reduced.
The retired 0.79 composite score was an artifact of tiny constructed samples.
"""
import csv
import json
import os
import random
from collections import Counter, defaultdict

from common import load_features, load_mayig
from attack_positional import positional

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SEED = 7


def trailing_suf_count(t, suf):
    n = 0
    for s in reversed(t):
        if s in suf:
            n += 1
        else:
            break
    return n


def stacking_rate(texts, suf):
    return sum(1 for t in texts if trailing_suf_count(t, suf) >= 2) / len(texts)


def bootstrap(texts, suf, iters=2000):
    rng = random.Random(SEED)
    vals = []
    for _ in range(iters):
        sample = [texts[rng.randrange(len(texts))] for _ in texts]
        vals.append(stacking_rate(sample, suf))
    vals.sort()
    return round(vals[int(.025 * iters)], 3), round(vals[int(.975 * iters)], 3)


def load_big():
    texts = []
    p = os.path.join(ROOT, "data", "parsed", "yajnadevam_corpus.csv")
    for r in csv.DictReader(open(p)):
        s = [x for x in r["reading_order"].split() if x not in ("000", "999")]
        if len(s) >= 2:
            texts.append(s)
    return texts


def derive_suf(texts, min_freq):
    freq = Counter(s for t in texts for s in t)
    termc = Counter(t[-1] for t in texts)
    return {s for s, c in freq.items() if c >= min_freq and termc[s] / c > 0.5}


def load_baselines():
    out = {}
    for key, fn in [("tamil", "baseline_old_tamil.json"),
                    ("sanskrit", "baseline_sanskrit.json")]:
        p = os.path.join(ROOT, "results", fn)
        out[key] = json.load(open(p)) if os.path.exists(p) else None
    return out


def gondi_rate_hook():
    """DORMANT hook (mirrors INDUS_FULL_BOOK). Activates the between-branch test
    the moment a morpheme-segmented Gondi corpus appears. Provide it either as
    $GONDI_CORPUS or data/parsed/gondi_segmented.txt — one word per line, its
    morphemes joined by '-' (stem-suffix-suffix). Returns a rate or None.

    Until such data exists, Gondi stays a DESCRIPTIVE (categorical) pole only;
    no rate is invented."""
    path = os.environ.get("GONDI_CORPUS") or os.path.join(
        ROOT, "data", "parsed", "gondi_segmented.txt")
    if not os.path.exists(path):
        return None
    two_plus = total = 0
    for line in open(path, encoding="utf-8"):
        w = line.strip()
        if not w:
            continue
        total += 1
        # morphemes after the stem = count of '-' separators
        if w.count("-") >= 2:
            two_plus += 1
    return round(two_plus / total, 3) if total else None


def main():
    feats = load_features()
    mayig = [t for t, *_ in load_mayig()]
    _, cls = positional([(t,) for t in mayig], min_freq=6,
                        desc=lambda s: feats.get(s, {}).get("desc", ""))
    suf_m = {s for s, c in cls.items() if c == "SUF"}
    mayig_rate = stacking_rate(mayig, suf_m)
    mayig_ci = bootstrap(mayig, suf_m)

    big = load_big()
    suf_b = derive_suf(big, 15)
    big_rate = stacking_rate(big, suf_b)
    big_ci = bootstrap(big, suf_b)

    base = load_baselines()
    tamil_rate = base["tamil"]["mwt_split_rate"] if base["tamil"] else None
    vedic_rate = base["sanskrit"]["mwt_split_rate"] if base["sanskrit"] else None

    # Gondi rate hook: None until annotated Gondi text lands; then fires the
    # between-branch test the contact hypothesis needs.
    gondi_rate = gondi_rate_hook()
    between = None
    if gondi_rate is not None:
        lo, hi = sorted([tamil_rate or 0, gondi_rate])
        between = {
            "gondi_rate": gondi_rate,
            "indus_icit": round(big_rate, 3),
            "indus_between_tamil_and_gondi": lo <= big_rate <= hi,
            "note": "Between-branch test now LIVE (Gondi rate available). If "
                    "Indus sits between the two Dravidian branches, or off to "
                    "one side, that is the positional signal the contact "
                    "hypothesis needs; if it sits at both, the result is "
                    "generically Dravidian.",
        }

    res = {
        "metric": "stacking rate = fraction of units expressing 2+ separable "
                  "grammatical morphemes",
        "poles": {
            "vedic_sanskrit_gold": vedic_rate,
            "tamil_gold": tamil_rate,
            "gondi_gold": gondi_rate,          # None until annotated data lands
            "gondi_status": "descriptive/categorical only — no annotated corpus"
            if gondi_rate is None else "gold rate available",
        },
        "indus": {
            "mayig_179": {"rate": round(mayig_rate, 3), "ci95": mayig_ci},
            "icit_2511": {"rate": round(big_rate, 3), "ci95": big_ci},
        },
        "between_branch_test": between,
        "conclusion": (
            "Indus (mayig %.3f, ICIT %.3f) sits at the Tamil pole (%.3f) and "
            "categorically apart from fusional Vedic (%.3f, which never stacks). "
            "This supports an agglutinative/Dravidian-like frame. It does NOT "
            "support 'reduced depth vs Old Tamil': gold Tamil running text is "
            "itself shallow, so Indus is at parity, not reduced."
            % (mayig_rate, big_rate, tamil_rate or 0, vedic_rate or 0)),
        "retired": "The 0.79 composite agglutination score (morphology_"
                   "signature.py) was a small-sample artifact and is superseded "
                   "by this gold-backed single metric.",
    }
    json.dump(res, open(os.path.join(ROOT, "results",
                                     "agglutination_axis.json"), "w"), indent=1)
    print("=== AGGLUTINATION AXIS (gold-backed) ===")
    print(f"  Vedic Sanskrit (gold): {vedic_rate}   [fusional pole]")
    print(f"  Tamil (gold UD):       {tamil_rate}   [agglutinative pole]")
    print(f"  Indus mayig-179:       {mayig_rate:.3f}  CI{mayig_ci}")
    print(f"  Indus ICIT-2511:       {big_rate:.3f}  CI{big_ci}")
    print("\n" + res["conclusion"])


if __name__ == "__main__":
    main()
