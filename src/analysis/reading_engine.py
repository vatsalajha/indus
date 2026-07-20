"""G1: STRUCTURAL glosses for every text — what a text IS, never how it sounds.

Applies only gauntlet-survived structural facts as a labelled parse. No sign is
given a sound. The output says a text is "a titled personal name" or "a
counted-commodity record", which the structure licenses, without any phonetics.

Per-sign tags:
  jar (P324)            -> [SUFFIX:case/honorific]   (survived T2, T6)
  man (P013) after jar  -> [PERSON-classifier]        (T5 fixed jar->man order)
  stroke numeral        -> [NUM]                       (consensus)
  sign right after NUM   -> [COUNTED]                  (T? counted-noun)
  sign right before jar  -> [STEM/name-candidate]      (T4 name-formula)
  OPEN-class sign        -> [OPENER]
  SUF-class (non-jar)    -> [SUFFIX]
  else                   -> [CONTENT]

Text-level structural reading (mutually-informed, conservative):
  ends in jar (+ optional man)         -> titled personal name / admin label
  numeral+counted present, no jar      -> counted-commodity / tally record
  opener + body, no jar/num            -> non-name administrative string
Output: results/structural_readings.csv (all mayig texts)
"""
import csv
import os

from common import load_features, load_mayig
from attack_positional import positional

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
JAR, MAN = "P324", "P013"
NUMERALS = {"P121", "P145", "P147", "P202", "P122", "P123", "P126",
            "P144", "P056", "P325"}


def tag_text(signs, cls):
    tags = []
    for i, s in enumerate(signs):
        after_num = i > 0 and signs[i - 1] in NUMERALS
        before_jar = i < len(signs) - 1 and signs[i + 1] == JAR
        if s == JAR:
            tags.append("SUFFIX:jar/case-honorific")
        elif s == MAN and i > 0 and signs[i - 1] == JAR:
            tags.append("PERSON-classifier")
        elif s in NUMERALS:
            tags.append("NUM")
        elif after_num:
            tags.append("COUNTED")
        elif before_jar:
            tags.append("STEM/name-candidate")
        elif cls.get(s) == "OPEN":
            tags.append("OPENER")
        elif cls.get(s) == "SUF":
            tags.append("SUFFIX")
        else:
            tags.append("CONTENT")
    return tags


def structural_reading(signs, tags):
    has_jar = JAR in signs
    ends_jarish = tags and (tags[-1].startswith("SUFFIX:jar")
                            or tags[-1] == "PERSON-classifier")
    has_count = "COUNTED" in tags or "NUM" in tags
    if ends_jarish or has_jar:
        base = "titled personal name / administrative label"
        if "PERSON-classifier" in tags:
            base += " (with person classifier)"
        return base
    if has_count:
        return "counted-commodity / tally record"
    if "OPENER" in tags:
        return "administrative string (opener-headed, no name-suffix)"
    return "short label (structure underdetermined)"


def main():
    feats = load_features()
    texts = load_mayig()
    _, cls = positional(texts, min_freq=6,
                        desc=lambda s: feats.get(s, {}).get("desc", ""))
    rows = []
    for signs, tid in texts:
        tags = tag_text(signs, cls)
        gloss = " ".join(f"[{t}:{s}]" for s, t in zip(signs, tags))
        rows.append({
            "text_id": tid,
            "signs_reading_order": " ".join(signs),
            "structural_gloss": gloss,
            "structural_reading": structural_reading(signs, tags),
        })
    out = os.path.join(ROOT, "results", "structural_readings.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["text_id", "signs_reading_order",
                                          "structural_gloss", "structural_reading"])
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    kinds = Counter(r["structural_reading"] for r in rows)
    print(f"structural readings for {len(rows)} texts -> {out}")
    for k, c in kinds.most_common():
        print(f"  {c:4}  {k}")
    print("\nsample glosses:")
    for r in rows[:6]:
        print(f"  {r['text_id']}: {r['structural_reading']}")
        print(f"       {r['structural_gloss']}")


if __name__ == "__main__":
    main()
