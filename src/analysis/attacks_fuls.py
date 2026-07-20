"""The four attacks on the REAL parsed Fuls corpus (Wells/ICIT numbering).

Input: data/parsed/corpus_reading.csv (from src/parse/parse_fuls_corpus.py).
Small-n honesty: this is the 53-text preview subset until the full book is
parsed; every number below carries that caveat. Deterministic (seeded RNG).
"""
import csv
import math
import os
import random
from collections import Counter, defaultdict

random.seed(7)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "data", "parsed", "corpus_reading.csv")

rows = list(csv.DictReader(open(SRC)))
texts = []          # (reading_order signs legible-only, genre, direction)
for r in rows:
    signs = [s for s in r["reading_order"].split() if s not in ("000", "999")]
    if len(signs) >= 2:
        t = r["artifact_type"]
        genre = ("seal" if t.startswith(("SEAL", "TAG")) else
                 "pottery" if t.startswith("POT") else
                 "tablet" if t.startswith("TAB") else "other")
        texts.append((signs, genre, r["direction"]))
N = len(texts)
print(f"texts (>=2 legible signs): {N}\n")

# ---- Attack 3: Zipf / frequency structure --------------------------------
counts = Counter(s for t, _, _ in texts for s in t)
total = sum(counts.values())
ranked = counts.most_common()
print("=== ZIPF / FREQUENCY ===")
print(f"tokens {total}, types {len(counts)}, "
      f"hapax {sum(1 for _, c in ranked if c == 1)} "
      f"({100*sum(1 for _, c in ranked if c == 1)/len(counts):.0f}% of types)")
# log-log slope over ranks with count>1 (tiny corpus: report, don't overclaim)
pts = [(math.log(r), math.log(c)) for r, (_, c) in enumerate(ranked, 1) if c > 1]
n = len(pts)
sx = sum(x for x, _ in pts); sy = sum(y for _, y in pts)
sxx = sum(x * x for x, _ in pts); sxy = sum(x * y for x, y in pts)
slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
print(f"Zipf log-log slope (ranks with count>1): {slope:.2f} "
      f"(natural languages ≈ -1; small-n caveat applies)\n")

# ---- Attacks 1+2: terminal-class parse rate vs shuffled control ----------
# SUF class learned unsupervised on the mayig corpus, mapped to Wells numbers
SUF_WELLS = {"090", "153", "154", "155", "156", "158", "390", "392", "405",
             "406", "407", "408", "520", "526", "527", "740"}
print("=== TERMINAL PARADIGM vs SHUFFLED CONTROL ===")


def term_rate(ts):
    return sum(1 for t in ts if t[-1] in SUF_WELLS) / len(ts)


real = term_rate([t for t, _, _ in texts])
trials = []
for _ in range(1000):
    sh = []
    for t, _, _ in texts:
        tt = t[:]
        random.shuffle(tt)
        sh.append(tt)
    trials.append(term_rate(sh))
mean_sh = sum(trials) / len(trials)
p = sum(1 for x in trials if x >= real) / len(trials)
print(f"reading-terminal in learned SUF class: real {100*real:.0f}% "
      f"vs shuffled {100*mean_sh:.0f}% (p≈{p:.3f}, 1000 shuffles)\n")

# ---- Genre split (the register question) ---------------------------------
print("=== GENRE SPLIT (jar-terminal rate by artifact class) ===")
by_genre = defaultdict(list)
for t, g, _ in texts:
    by_genre[g].append(t)
for g, ts in sorted(by_genre.items()):
    jt = sum(1 for t in ts if t[-1] == "740")
    st = sum(1 for t in ts if t[-1] in SUF_WELLS)
    print(f"  {g:8} n={len(ts):3}  jar-terminal {jt}/{len(ts)}  "
          f"SUF-terminal {st}/{len(ts)}")

# ---- Attack 4: bigrams / Markov ------------------------------------------
print("\n=== TOP BIGRAMS (reading order) ===")
bi = Counter()
for t, _, _ in texts:
    for a, b in zip(t, t[1:]):
        bi[(a, b)] += 1
for (a, b), c in bi.most_common(8):
    print(f"  {a} -> {b}  ×{c}")
