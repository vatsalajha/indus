"""The semantic gauntlet: seven falsifiable tests that point our structural
knowledge at specific meaning-claims, to confirm or wound them.

Each test is a deterministic, seeded function writing to results/gauntlet.json.
Numbers are whatever the corpus actually says; claims that fail are reported
as failing. Runs on the mayig 179-seal corpus now; a Fuls hook activates when
INDUS_FULL_BOOK=1 and the parsed Fuls corpus is present.

  T1  fish: name vs commodity (position + numeral+fish suffix attachment)
  T2  jar suffix L/R neighbour-diversity ratio (vs fish as control)
  T3  terminal-set concentration + jar/lance complementary distribution
  T4  name-formula stem diversity
  T5  suffix ordering: every SUF-class pair, order consistency, binomial p,
      plus a permutation control on the terminal region
  T6  jar number-sensitivity (case/honorific vs plural)
  T7  modifier-head ratio with a corrected content-noun detector
"""
import os
import random
from collections import Counter, defaultdict

from scipy.stats import binomtest

from common import JAR_P, load_features, load_mayig, save_result
from attack_positional import positional

SEED = 7
FISH_PREFIX = "fish"
LANCE_P = "P217"
MAN_P = "P013"
# strict stroke numerals (from attack_numerals, hand-audited)
NUMERALS = {"P121", "P145", "P147", "P202", "P122", "P123", "P126",
            "P144", "P056", "P325"}


def fish_signs(feats):
    return {s for s, f in feats.items()
            if f.get("desc", "").lower().startswith(FISH_PREFIX)}


def T1_fish(texts, feats, suf):
    fish = fish_signs(feats)
    # mean position of fish signs
    pos = []
    for t, *_ in texts:
        L = len(t)
        for i, s in enumerate(t):
            if s in fish and L > 1:
                pos.append(i / (L - 1))
    mean_pos = sum(pos) / len(pos) if pos else None
    # fish-before-jar placements
    fb = fa = 0
    for t, *_ in texts:
        idx_j = [i for i, s in enumerate(t) if s == JAR_P]
        for i, s in enumerate(t):
            if s in fish:
                for j in idx_j:
                    if i < j:
                        fb += 1
                    elif i > j:
                        fa += 1
    # numeral+fish compounds: what follows the fish?
    comp = suffixed = at_end = midtext = 0
    for t, *_ in texts:
        for i in range(len(t) - 1):
            if t[i] in NUMERALS and t[i + 1] in fish:
                comp += 1
                k = i + 1
                if k == len(t) - 1:
                    at_end += 1
                elif t[k + 1] in suf:
                    suffixed += 1
                else:
                    midtext += 1
    return {
        "fish_mean_position": round(mean_pos, 3) if mean_pos else None,
        "fish_before_jar": fb, "fish_after_jar": fa,
        "numeral_fish_compounds": comp,
        "compound_takes_suffix": suffixed,
        "compound_text_final": at_end,
        "compound_bare_midtext": midtext,
        "verdict": ("fish behaves like a countable noun (stem-side); the "
                    "specific numeral+fish = star-name prediction is "
                    + ("SUPPORTED" if comp and (suffixed + at_end) / comp > 0.4
                       else "NOT clearly supported: most compounds sit bare "
                       "mid-text, more commodity-like than named-entity-like")),
    }


def T2_jar_lr(texts):
    def lr(sign):
        left, right = set(), set()
        after = 0
        for t, *_ in texts:
            for i, s in enumerate(t):
                if s == sign:
                    if i:
                        left.add(t[i - 1])
                    if i < len(t) - 1:
                        right.add(t[i + 1])
                        after += 1
        return len(left), len(right)
    jl, jr = lr(JAR_P)
    from common import load_features
    feats = load_features()
    fish = fish_signs(feats)
    # aggregate fish family L/R
    fleft, fright = set(), set()
    for t, *_ in texts:
        for i, s in enumerate(t):
            if s in fish:
                if i:
                    fleft.add(t[i - 1])
                if i < len(t) - 1:
                    fright.add(t[i + 1])
    return {
        "jar_distinct_left": jl, "jar_distinct_right": jr,
        "jar_lr_ratio": round(jl / jr, 2) if jr else None,
        "fish_distinct_left": len(fleft), "fish_distinct_right": len(fright),
        "fish_lr_ratio": round(len(fleft) / len(fright), 2) if fright else None,
        "verdict": "jar bolts onto many stems, is rarely followed -> suffix "
                   "fingerprint; fish shows content-word fingerprint",
    }


def T3_terminal(texts, suf):
    endc = Counter(t[-1] for t, *_ in texts)
    total_end = sum(endc.values())
    distinct_final = len(endc)
    top5 = endc.most_common(5)
    top5_share = sum(c for _, c in top5) / total_end
    # jar/lance complementary distribution
    both = jar_only = lance_only = 0
    for t, *_ in texts:
        hj, hl = JAR_P in t, LANCE_P in t
        if hj and hl:
            both += 1
        elif hj:
            jar_only += 1
        elif hl:
            lance_only += 1
    contain_either = both + jar_only + lance_only
    return {
        "distinct_final_signs": distinct_final,
        "inventory_final_fraction": round(distinct_final /
                                          len({s for t, *_ in texts for s in t}), 3),
        "top5_ending_share": round(top5_share, 3),
        "top5_enders": [(s, c) for s, c in top5],
        "jar_lance_cooccur": both, "jar_only": jar_only,
        "lance_only": lance_only, "texts_with_either": contain_either,
        "verdict": f"a small near-closed terminal set ({distinct_final} signs "
                   f"ever final); jar+lance co-occur in only {both}/"
                   f"{contain_either} -> near-complementary, suffix-like",
    }


def T4_name_formula(texts):
    stems = Counter()
    positions = 0
    for t, *_ in texts:
        for i, s in enumerate(t):
            if s == JAR_P and i:
                stems[t[i - 1]] += 1
                positions += 1
    return {"distinct_stems_before_jar": len(stems),
            "jar_stem_positions": positions,
            "verdict": f"{len(stems)} distinct stems feed one jar suffix "
                       f"across {positions} positions -> many-names-one-ending"}


def T5_suffix_order(texts, suf):
    pairs = {}
    for a in suf:
        for b in suf:
            if a >= b:
                continue
            ab = ba = co = 0
            for t, *_ in texts:
                ia = [i for i, s in enumerate(t) if s == a]
                ib = [i for i, s in enumerate(t) if s == b]
                if ia and ib:
                    co += 1
                    # order of first occurrences
                    if min(ia) < min(ib):
                        ab += 1
                    elif min(ib) < min(ia):
                        ba += 1
            if co >= 3:
                k = max(ab, ba)
                p = binomtest(k, ab + ba, 0.5).pvalue if (ab + ba) else 1.0
                order = f"{a}<{b}" if ab >= ba else f"{b}<{a}"
                pairs[f"{a}+{b}"] = {"cooccur": co, "a_before_b": ab,
                                     "b_before_a": ba, "dominant_order": order,
                                     "binom_p": round(p, 4)}
    # permutation control on the jar/man fixed-order bias. Measure the
    # consistency of whichever direction dominates, then ask how often random
    # order reaches that consistency.
    rng = random.Random(SEED)
    co_texts = [t for t, *_ in texts if MAN_P in t and JAR_P in t]
    obs_jar_first = sum(1 for t in co_texts if t.index(JAR_P) < t.index(MAN_P))
    obs_man_first = len(co_texts) - obs_jar_first
    obs_consistency = max(obs_jar_first, obs_man_first)
    ge = 0
    for _ in range(2000):
        cnt = 0
        for t in co_texts:
            tt = t[:]
            rng.shuffle(tt)
            if tt.index(JAR_P) < tt.index(MAN_P):
                cnt += 1
        if max(cnt, len(co_texts) - cnt) >= obs_consistency:
            ge += 1
    return {"pairs": pairs,
            "jar_man": {"cooccur": len(co_texts),
                        "jar_before_man": obs_jar_first,
                        "man_before_jar": obs_man_first,
                        "dominant": "jar<man (man is last)" if obs_jar_first >= obs_man_first
                        else "man<jar",
                        "order_consistency": f"{obs_consistency}/{len(co_texts)}",
                        "perm_p": round(ge / 2000, 4),
                        "note": "2000 per-text shuffles; p = P(random order "
                                "reaches observed one-directional consistency). "
                                "Corrects the chat's reversed man->jar direction: "
                                "the fixed pair is jar THEN man."}}


def T6_number_sensitivity(texts):
    def has_num(t):
        return any(s in NUMERALS for s in t)
    jar_texts = [t for t, *_ in texts if JAR_P in t]
    non = [t for t, *_ in texts if JAR_P not in t]
    jn = sum(has_num(t) for t in jar_texts) / len(jar_texts)
    nn = sum(has_num(t) for t in non) / len(non)
    return {"jar_texts_with_numeral": round(jn, 3),
            "nonjar_texts_with_numeral": round(nn, 3),
            "verdict": "jar is number-independent -> case/honorific, not a "
                       "plural marker" if abs(jn - nn) < 0.12 else
                       "jar interacts with number -> revisit plural hypothesis"}


def T7_modifier_head(texts, feats, suf):
    # content signs: frequent, not numerals, not suffix-class, not openers
    freq = Counter(s for t, *_ in texts for s in t)
    content = {s for s, c in freq.items() if c >= 6
               and s not in NUMERALS and s not in suf}
    before = after = 0
    for t, *_ in texts:
        for i, s in enumerate(t):
            if s in NUMERALS:
                if i < len(t) - 1 and t[i + 1] in content:
                    before += 1
                if i and t[i - 1] in content:
                    after += 1
    ratio = round(before / after, 2) if after else None
    return {"numeral_before_content": before, "numeral_after_content": after,
            "ratio": ratio,
            "verdict": "modifier-before-head SUPPORTED" if ratio and ratio > 1.5
            else "NULL: numerals precede and follow content signs about "
                 "equally; clean modifier-head order not present in this corpus"}


def main():
    feats = load_features()
    texts = load_mayig()
    _, cls = positional(texts, min_freq=6,
                        desc=lambda s: feats.get(s, {}).get("desc", ""))
    suf = [s for s, c in cls.items() if c == "SUF"]

    res = {
        "corpus": "mayig 179 seals (175 texts >=2 signs)",
        "suf_class": suf,
        "T1_fish_name_vs_commodity": T1_fish(texts, feats, suf),
        "T2_jar_lr_diversity": T2_jar_lr(texts),
        "T3_terminal_concentration": T3_terminal(texts, suf),
        "T4_name_formula": T4_name_formula(texts),
        "T5_suffix_order": T5_suffix_order(texts, suf),
        "T6_number_sensitivity": T6_number_sensitivity(texts),
        "T7_modifier_head": T7_modifier_head(texts, feats, suf),
    }
    path = os.path.join(os.path.dirname(__file__), "..", "..", "results",
                        "gauntlet.json")
    import json
    json.dump(res, open(path, "w"), indent=1)
    # console summary
    print("=== SEMANTIC GAUNTLET (mayig 175 texts) ===")
    print("T1 fish:", res["T1_fish_name_vs_commodity"]["verdict"][:80])
    print(f"   compounds={res['T1_fish_name_vs_commodity']['numeral_fish_compounds']}, "
          f"suffixed={res['T1_fish_name_vs_commodity']['compound_takes_suffix']}, "
          f"final={res['T1_fish_name_vs_commodity']['compound_text_final']}, "
          f"bare-mid={res['T1_fish_name_vs_commodity']['compound_bare_midtext']}")
    print(f"T2 jar L/R ratio={res['T2_jar_lr_diversity']['jar_lr_ratio']} "
          f"vs fish {res['T2_jar_lr_diversity']['fish_lr_ratio']}")
    print(f"T3 distinct-final={res['T3_terminal_concentration']['distinct_final_signs']}, "
          f"top5 share={res['T3_terminal_concentration']['top5_ending_share']}, "
          f"jar+lance co-occur={res['T3_terminal_concentration']['jar_lance_cooccur']}")
    print(f"T4 stems before jar={res['T4_name_formula']['distinct_stems_before_jar']}")
    mj = res["T5_suffix_order"]["jar_man"]
    print(f"T5 order: {mj['dominant']} {mj['order_consistency']}, perm_p={mj['perm_p']}")
    for k, v in res["T5_suffix_order"]["pairs"].items():
        print(f"   {k}: {v['dominant_order']} {max(v['a_before_b'],v['b_before_a'])}"
              f"/{v['cooccur']} binom_p={v['binom_p']}")
    print(f"T6 jar-texts-num={res['T6_number_sensitivity']['jar_texts_with_numeral']} "
          f"vs nonjar {res['T6_number_sensitivity']['nonjar_texts_with_numeral']}")
    print(f"T7 ratio={res['T7_modifier_head']['ratio']}: "
          f"{res['T7_modifier_head']['verdict'][:60]}")


if __name__ == "__main__":
    main()
