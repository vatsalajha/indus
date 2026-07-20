"""Grapheme frequency table from the parsed Fuls corpus (Wells/ICIT numbering).

Reads data/parsed/corpus_reading.csv, writes results/grapheme_frequencies.csv:
rank, wells_no, count, pct, cum_pct — the input for the Zipf/coverage attacks.
000 (illegible) and 999 (blank) are excluded; they are not graphemes.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "data", "parsed", "corpus_reading.csv")
OUT = os.path.join(ROOT, "results", "grapheme_frequencies.csv")

from collections import Counter

counts = Counter()
n_rows = 0
with open(SRC) as f:
    for row in csv.DictReader(f):
        n_rows += 1
        for s in row["reading_order"].split():
            if s not in ("000", "999"):
                counts[s] += 1

total = sum(counts.values())
cum = 0
with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["rank", "wells_no", "count", "pct", "cum_pct"])
    for rank, (sign, c) in enumerate(counts.most_common(), 1):
        cum += c
        w.writerow([rank, sign, c, f"{100*c/total:.2f}", f"{100*cum/total:.2f}"])

print(f"texts: {n_rows}  legible tokens: {total}  unique graphemes: {len(counts)}")
print(f"wrote {OUT}")
top = counts.most_common(5)
print("top 5:", ", ".join(f"{s}×{c} ({100*c/total:.1f}%)" for s, c in top))
cov = 0
for i, (_, c) in enumerate(counts.most_common(), 1):
    cov += c
    if cov / total >= 0.8:
        print(f"signs covering 80% of tokens: {i} of {len(counts)}")
        break
