"""Validation gates for the extraction layer.

Rule (PROJECT_RULES.md #6): tests that cannot run at current data scale are SKIPPED
with a stated reason, never weakened to pass. Runs standalone
(`python3 tests/test_extraction.py`) or under pytest.
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PARSED = os.path.join(ROOT, "data", "parsed")
RESULTS = os.path.join(ROOT, "results")

VALID_DIRECTIONS = {"R/L", "L/R", "NR", "SYM", "BT", "-", "?"}
FULL_BOOK = os.environ.get("INDUS_FULL_BOOK") == "1"   # flip when full PDF lands


def load(name):
    with open(os.path.join(PARSED, name)) as f:
        return list(csv.DictReader(f))


def test_corpus_row_count():
    rows = load("corpus.csv")
    assert len(rows) >= 50, f"only {len(rows)} corpus rows"


def test_no_parse_failures():
    log = os.path.join(RESULTS, "parse_failures.log")
    with open(log) as f:
        failures = [ln for ln in f if ln.strip()]
    assert not failures, f"{len(failures)} parse failures — inspect {log}"


def test_sign_codes_in_valid_range():
    for r in load("corpus.csv"):
        for s in re.findall(r"\d{3}", r["code_printed"]):
            n = int(s)
            assert n == 0 or n == 999 or 1 <= n <= 958, \
                f"sign {s} out of range in {r['icit_id']}"


def test_jar_share_about_ten_percent():
    toks = [s for r in load("corpus_reading.csv")
            for s in r["reading_order"].split() if s not in ("000", "999")]
    jar = sum(1 for s in toks if s == "740")
    share = jar / len(toks)
    assert 0.07 <= share <= 0.13, \
        f"jar 740 = {100*share:.1f}% of legible tokens (expect ~10%)"


def test_directions_valid():
    dirs = {r["direction"] for r in load("corpus.csv")}
    assert dirs <= VALID_DIRECTIONS, f"unexpected directions: {dirs - VALID_DIRECTIONS}"


def test_reading_order_is_reversed_code():
    for r in load("corpus_reading.csv"):
        signs = re.findall(r"\d{3}", r["code_printed"])
        assert r["reading_order"].split() == list(reversed(signs)), \
            f"reading_order mismatch in {r['icit_id']}"


def test_m77_concordance():
    rows = load("m77_concordance.csv")
    assert len(rows) >= 90, f"only {len(rows)} m77 rows"
    nums = [r["m77_text_no"] for r in rows]
    assert len(nums) == len(set(nums)), "duplicate m77 text numbers"
    for r in rows:
        int(r["icit_id"]), int(r["book_page"])   # must be integers


def test_catalog_internal_consistency():
    """Sign-list freq == positional-stats total == artifact-table freq."""
    freqs = {int(r["wells_no"]): int(r["freq_book"]) for r in load("signs.csv")}
    for r in load("sign_stats.csv"):
        n = int(r["wells_no"])
        if n in freqs:
            assert freqs[n] == int(r["total"]), \
                f"sign {n}: list freq {freqs[n]} != stats total {r['total']}"
    for r in load("sign_by_artifact.csv"):
        n = int(r["wells_no"])
        if n in freqs:
            assert freqs[n] == int(r["freq"]), \
                f"sign {n}: list freq {freqs[n]} != artifact-table freq {r['freq']}"


def test_book_totals_match_published():
    """Fuls's own 'all' row vs the published ICIT figure (17,957 legible,
    v2.8 May 2022). The book prints 17,991 — accept ≤1% version drift."""
    with open(os.path.join(RESULTS, "book_totals.json")) as f:
        t = json.load(f)
    assert abs(t["legible_tokens"] - 17957) / 17957 < 0.01, t
    assert t["legible_tokens"] == sum(
        t[k] for k in ("seals", "tablets", "pottery", "tags", "other")), \
        "artifact-class totals do not sum to legible total"


# ---- full-book-only gates (SKIPPED on preview data) ----------------------

def test_full_book_totals():
    if not FULL_BOOK:
        print("SKIP full-book totals (reason: preview PDF only — "
              "expect ~5,644 texts / ~4,660 artifacts / R/L ≈ 4,235 "
              "once the complete Corpus PDF is in data/raw/)")
        return
    rows = load("corpus.csv")
    artifacts = {r["icit_id"] for r in rows}
    assert abs(len(rows) - 5644) / 5644 < 0.01
    assert abs(len(artifacts) - 4660) / 4660 < 0.01
    rl = sum(1 for r in rows if r["direction"] == "R/L")
    assert abs(rl - 4235) / 4235 < 0.02




# ---- M77 Table I gates (visual transcription, 2026-07-17) ----------------

def test_m77_table1_complete():
    rows = load("m77_table1.csv")
    assert len(rows) == 417, f"{len(rows)} rows, expect 417"
    for r in rows:
        vals = [int(r[k]) for k in ("sol", "ini", "med", "fin", "tot")]
        assert sum(vals[:4]) == vals[4], f"checksum fail at sign {r['m77_sign_no']}"


def test_m77_table1_totals_match_printed():
    rows = load("m77_table1.csv")
    sums = tuple(sum(int(r[k]) for r in rows)
                 for k in ("sol", "ini", "med", "fin", "tot"))
    assert sums == (190, 3010, 7196, 2976, 13372), sums


def test_m77_jar_and_fish_anchors():
    rows = {int(r["m77_sign_no"]): r for r in load("m77_table1.csv")}
    jar = rows[342]
    assert int(jar["tot"]) == 1395 and int(jar["fin"]) == 971
    assert max(int(r["tot"]) for r in rows.values()) == 1395
    fish = rows[59]
    assert int(fish["tot"]) == 381


def main():
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {name}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed, "
          f"{'full-book gates ACTIVE' if FULL_BOOK else 'full-book gates skipped (preview)'}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
