"""Shared loaders and helpers for Phase 2 analysis modules.

Two corpora, one numbering crosswalk, deterministic everywhere:
- FULS: data/parsed/corpus_reading.csv (Wells/ICIT numbers, 53 texts, pilot)
- MAYIG: mayig/ CISI digitization (P-numbers, 179 seals) with P->Wells/M77
  crosswalk from mayig/features/*.json
- M77: data/parsed/m77_table1.csv (417 signs, SOL/INI/MED/FIN/TOT)

All results funnel into results/results.json via save_result(section, obj).
"""
import csv
import glob
import json
import os

SEED = 7
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
PARSED = os.path.join(ROOT, "data", "parsed")
RESULTS = os.path.join(ROOT, "results")
TABLES = os.path.join(RESULTS, "tables")
RESULTS_JSON = os.path.join(RESULTS, "results.json")
os.makedirs(TABLES, exist_ok=True)

# slot classes learned unsupervised on the mayig pilot (decipher.py Attack 2)
SUF_P = ["P004", "P013", "P086", "P217", "P301", "P324"]
OPEN_P = ["P011", "P076", "P256", "P378", "P385"]
PRESUF_P = ["P175", "P332"]
JAR_P, JAR_W, JAR_M = "P324", "740", 342

# In Wells's scheme, Set 01 (codes 001-059) is the stroke/numeral set
# (fuls2023 catalog preview, sign list p.25). Documented assumption.
NUM_WELLS = {f"{n:03d}" for n in range(1, 60)}


def genre_of(artifact_type):
    t = artifact_type.upper()
    if t.startswith(("SEAL", "TAG")):
        return "SEAL/TAG"
    if t.startswith("TAB"):
        return "TABLET"
    if t.startswith("POT"):
        return "POTTERY"
    return "OTHER"


def load_fuls(min_len=2):
    """[(signs_reading_order_legible, row)] from corpus_reading.csv."""
    out = []
    with open(os.path.join(PARSED, "corpus_reading.csv")) as f:
        for r in csv.DictReader(f):
            signs = [s for s in r["reading_order"].split()
                     if s not in ("000", "999")]
            if len(signs) >= min_len:
                out.append((signs, r))
    return out


def load_mayig(min_len=2):
    """[(P-sign list in reading order, artifact_id)] plus feature crosswalk."""
    texts = []
    for f in sorted(glob.glob(os.path.join(ROOT, "mayig", "corpus",
                                           "**", "*.json"), recursive=True)):
        for side in json.load(open(f)):
            gs = [g["id"] for g in side.get("graphemes", [])
                  if g["id"] != "P000"]
            if len(gs) >= min_len:
                texts.append((list(reversed(gs)), side.get("id", "")))
    return texts


def load_features():
    """P-number -> {desc, wells:[..], m77:[..], parpola:[..]}"""
    feats = {}
    for f in glob.glob(os.path.join(ROOT, "mayig", "features", "*.json")):
        d = json.load(open(f))
        feats[d["id"]] = {
            "desc": d.get("description", ""),
            "wells": [w.lstrip("W") for w in d.get("wells_graphemes", [])],
            "m77": [int(m.lstrip("M")) for m in d.get("mahadevan_graphemes", [])],
            "parpola": d.get("parpola_graphemes", []),
        }
    return feats


def load_m77_table1():
    rows = {}
    with open(os.path.join(PARSED, "m77_table1.csv")) as f:
        for r in csv.DictReader(f):
            rows[int(r["m77_sign_no"])] = {k: int(r[k]) for k in
                                           ("sol", "ini", "med", "fin", "tot")}
    return rows


def save_result(section, obj):
    data = {}
    if os.path.exists(RESULTS_JSON):
        data = json.load(open(RESULTS_JSON))
    data[section] = obj
    with open(RESULTS_JSON, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)


def write_table(name, header, rows):
    with open(os.path.join(TABLES, name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
