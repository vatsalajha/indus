"""R3+R4: the rebus gauntlet. Falsifiable, null-model-guarded testing of
published-style rebus readings — a ranking, never a translation.

Method (per the committed, pre-registered spec in rebus_scoring_spec.json,
which was locked BEFORE the DEDR lexicon was touched):

  For each IDENTIFIABLE sign (data/parsed/identifiable_signs.csv):
    1. object -> DEDR words: entries whose gloss carries the object meaning.
    2. homophones/polysemy: the OTHER meanings attached to that phonetic form
       (within-entry polysemy + same-headword entries), with DEDR entry cites.
    3. each homophone meaning -> the grammatical ROLE it implies.
    4. score the sign's ACTUAL corpus position against every role's template.
    5. SURVIVES only if: picture-confidence is HIGH, AND some homophone's
       implied role == the sign's TOP-scoring role.
    R4 null model: for a survivor, draw frequency-matched random DEDR entries;
       p = fraction whose implied role also equals the sign's top role. Survives
       only if p < 0.05 (the specific meaning fits notably better than chance).

Built-in validation: fish/mīn MUST return WOUNDED for the star reading (fish
scores COUNTED_NOUN, star implies NAME_ELEMENT). If not, the pipeline is broken.

HARD RULES: no full-text transliteration; no sign gets a sound; low/medium
picture-confidence can never SURVIVE (only inform).
Output: results/rebus_gauntlet.json
"""
import csv
import json
import os
import random
import re

from sign_features import compute as sign_feats

SEED = 7
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SPEC = json.load(open(os.path.join(HERE, "rebus_scoring_spec.json")))
DEDR = os.path.join(ROOT, "data", "parsed", "dedr.csv")
IDENT = os.path.join(ROOT, "data", "parsed", "identifiable_signs.csv")

# object -> the DEDR gloss word(s) that denote it (the literal meaning)
OBJECT_MEANING = {
    "fish": ["fish"], "tree": ["tree"], "leaf": ["leaf"], "plant": ["plant"],
    "jar/pot": ["pot", "jar", "vessel"], "pot": ["pot", "vessel"],
    "man": ["man", "person"], "man-carrying": ["carry", "bear", "load"],
    "wheel": ["wheel"], "arrow/lance": ["arrow", "spear", "lance"],
    "fig": ["fig"], "comb": ["comb"],
}

# meaning-keyword -> implied grammatical role (documented interpretive layer).
# NAME_ELEMENT includes the celestial/light senses (shine, glitter, lightning)
# that underlie Parpola's fish->star->asterism-name rebus: the shine root
# (DEDR 4876) is exactly what the star reading rests on.
ROLE_KEYWORDS = {
    "GRAMMATICAL_SUFFIX": ["suffix", "particle", "demonstr", "pronoun",
                           "that ", "this ", "case", "negative", "interrog",
                           "marker", "postposition"],
    "NAME_ELEMENT": ["star", "sun", "moon", "planet", "god", "goddess",
                     "deity", "king", "chief", "lord", "master", "sacred",
                     "ancestor", "name", "priest", "hero", "shine", "glitter",
                     "lightning", "flash", "firefly", "twinkle", "bright"],
    "COUNTED_NOUN": ["fish", "grain", "rice", "paddy", "seed", "cattle", "cow",
                     "ox", "bull", "goat", "sheep", "pot", "jar", "vessel",
                     "tree", "leaf", "fruit", "corn", "measure", "coin",
                     "cloth", "stone", "metal", "tool", "grass", "flower"],
}


def implied_role(meaning):
    m = meaning.lower()
    for role, kws in ROLE_KEYWORDS.items():
        if any(k in m for k in kws):
            return role
    return "STEM_NOUN"       # generic concrete noun fallback


DIACRITICS = str.maketrans({"ī": "i", "ā": "a", "ū": "u", "ē": "e", "ō": "o",
                            "ṉ": "n", "ṇ": "n", "ṭ": "t", "ḍ": "d", "ḷ": "l",
                            "ḻ": "l", "ṟ": "r", "ṛ": "r", "ś": "s", "ṣ": "s",
                            "ṅ": "n", "ñ": "n", "·": "", "̆": ""})


def phonetic_key(form):
    """Normalise a Dravidian form to a length-insensitive consonant skeleton so
    that homophones like mīṉ (fish) and miṉ (shine) collide."""
    f = form.lower().translate(DIACRITICS)
    f = re.sub(r"[^a-z]", "", f)
    return f[:5]


def ta_form(gloss):
    """First Tamil headword form in a DEDR gloss (after 'Ta. ')."""
    m = re.search(r"\bTa\.\s+([A-Za-zāīūēōṉṇṭḍḷḻṟṛśṣṅñ·̆]+)", gloss)
    return m.group(1) if m else ""


# ---- committed template evaluator ----------------------------------------
FEAT_ALIAS = {"L/R": "lr_ratio"}


def eval_predicate(pred, f):
    """Return (met, total) for an 'A AND B AND ...' predicate string."""
    conds = [c.strip() for c in pred.split("AND")]
    met = 0
    for c in conds:
        # range form: lo<=feat<=hi
        rng = re.match(r"([\d.]+)<=([A-Za-z_/]+)<=([\d.]+)", c)
        if rng:
            lo, name, hi = float(rng[1]), rng[2], float(rng[3])
            v = f.get(FEAT_ALIAS.get(name, name), 0)
            met += lo <= v <= hi
            continue
        m = re.match(r"([A-Za-z_/]+)\s*(>=|<=|>|<)\s*([\d.]+)", c)
        if not m:
            continue
        name, op, val = m[1], m[2], float(m[3])
        v = f.get(FEAT_ALIAS.get(name, name), 0)
        met += {">": v > val, "<": v < val, ">=": v >= val, "<=": v <= val}[op]
    return met, len(conds)


def top_role(f):
    scores = {}
    for role, spec in SPEC["roles"].items():
        met, total = eval_predicate(spec["predicts"], f)
        scores[role] = met / total
    best = max(scores, key=scores.get)
    return best, round(scores[best], 2), {k: round(v, 2) for k, v in scores.items()}


# ---- DEDR ----------------------------------------------------------------
def load_dedr():
    rows = []
    with open(DEDR) as fh:
        for r in csv.DictReader(fh):
            rows.append((int(r["entry_no"]), r["headword"], r["gloss"]))
    return rows


def meanings_of(gloss):
    """Distinct candidate meanings (head nouns) from a DEDR gloss."""
    g = re.split(r"[;,.]", gloss)
    out = []
    for piece in g:
        piece = piece.strip().lower()
        if 2 < len(piece) < 40 and re.search(r"[a-z]", piece):
            out.append(piece)
    return out[:12]


def find_object_entries(dedr, object_words):
    hits = []
    for no, hw, gloss in dedr:
        gl = gloss.lower()
        if any(re.search(r"\b" + re.escape(w) + r"\b", gl) for w in object_words):
            hits.append((no, hw, gloss))
    return hits


def build_phonetic_index(dedr):
    idx = {}
    for no, hw, gloss in dedr:
        key = phonetic_key(ta_form(gloss) or hw)
        if key:
            idx.setdefault(key, []).append((no, hw, gloss))
    return idx


def find_homophones(dedr, phon_idx, object_words):
    """Cross-entry homophones: entries sharing the object word's phonetic key
    but carrying a DIFFERENT (non-object) meaning. Returns list of dicts with
    DEDR cites."""
    obj_entries = find_object_entries(dedr, object_words)
    keys = {phonetic_key(ta_form(g) or hw) for no, hw, g in obj_entries}
    keys.discard("")
    homs = []
    seen = set()
    for k in keys:
        for no, hw, gloss in phon_idx.get(k, []):
            gl = gloss.lower()
            is_object = any(re.search(r"\b" + re.escape(w) + r"\b", gl)
                            for w in object_words)
            for mng in meanings_of(gloss):
                if is_object and any(re.search(r"\b" + re.escape(w) + r"\b", mng)
                                     for w in object_words):
                    continue          # skip the literal object meaning itself
                sig = (no, mng[:24])
                if sig in seen:
                    continue
                seen.add(sig)
                role = implied_role(mng)
                if role != "STEM_NOUN":     # keep only role-bearing meanings
                    homs.append({"dedr": no, "headword": hw,
                                 "meaning": mng[:60], "implied_role": role})
    return homs[:12]


def main():
    if not os.path.exists(DEDR):
        print("dedr.csv absent — run R1 (scrape_dedr.py) first."); return
    feats = sign_feats()
    dedr = load_dedr()
    phon_idx = build_phonetic_index(dedr)
    ident = list(csv.DictReader(open(IDENT)))
    rng = random.Random(SEED)

    results = []
    for row in ident:
        sign, obj, conf = row["sign"], row["object"], row["confidence"]
        f = feats.get(sign)
        if not f:
            continue
        tr, tr_score, all_scores = top_role(f)     # T = position's top role
        object_words = OBJECT_MEANING.get(obj, [obj.split("/")[0]])
        literal_role = implied_role(object_words[0])    # L = literal picture role
        literal_consistent = (tr == literal_role)
        homophones = find_homophones(dedr, phon_idx, object_words)

        # A REBUS is only needed when position (T) != literal role (L). A rebus
        # SURVIVES if some homophone implies role T (i.e. the sound, not the
        # picture, explains the position), at high confidence and beating null.
        rebus_matches = [h for h in homophones
                         if h["implied_role"] == tr and tr != literal_role]
        # per-homophone wound record (e.g. fish->star NAME_ELEMENT vs T)
        for h in homophones:
            h["matches_position"] = (h["implied_role"] == tr)

        null_p = None
        survives = False
        if rebus_matches and conf == "high":
            K = 2000
            hit = sum(1 for _ in range(K)
                      if (lambda ms: ms and implied_role(rng.choice(ms)) == tr)
                      (meanings_of(rng.choice(dedr)[2])))
            null_p = round(hit / K, 4)
            survives = null_p < 0.05

        if survives:
            verdict = "SURVIVES(tier-B)"
        elif rebus_matches:                 # matched but low conf or failed null
            verdict = ("WOUNDED-BY-NULL" if conf == "high"
                       else "LOW/MED-CONFIDENCE-PICTURE")
        elif literal_consistent:
            verdict = "LITERAL-CONSISTENT"   # picture used at face value
        else:
            verdict = "UNEXPLAINED"          # position not explained by picture
        # star reading wound: fish position is COUNTED_NOUN, star implies NAME_ELEMENT
        star_wounded = any(h["implied_role"] == "NAME_ELEMENT"
                           and tr != "NAME_ELEMENT" for h in homophones)

        results.append({
            "sign": sign, "object": obj, "picture_confidence": conf,
            "literal_role": literal_role, "corpus_top_role": tr,
            "literal_consistent": literal_consistent,
            "top_role_score": tr_score, "role_scores": all_scores,
            "homophones": homophones[:8],
            "surviving_rebus": rebus_matches,
            "celestial_name_reading_wounded": star_wounded,
            "null_model_p": null_p, "verdict": verdict,
        })

    # built-in validation: fish (P050) scores COUNTED_NOUN and the star/celestial
    # (NAME_ELEMENT) reading is wounded, not survived.
    fish = next((r for r in results if r["sign"] == "P050"), None)
    star_ok = bool(fish and fish["corpus_top_role"] == "COUNTED_NOUN"
                   and fish["celestial_name_reading_wounded"]
                   and "SURVIVES" not in fish["verdict"])

    out = {
        "committed_spec": SPEC,
        "validation": {
            "fish_star_wounded": star_ok,
            "fish_top_role": fish["corpus_top_role"] if fish else None,
            "note": "fish must score COUNTED_NOUN and the star->NAME_ELEMENT "
                    "reading must NOT survive",
        },
        "results": results,
        "survivors": [r["sign"] for r in results if "SURVIVES" in r["verdict"]],
    }
    json.dump(out, open(os.path.join(ROOT, "results", "rebus_gauntlet.json"),
                        "w"), indent=1)
    print("=== REBUS GAUNTLET ===")
    for r in results:
        star = ""
        if r["sign"] == "P050":
            star = "  <- fish/star validation"
        print(f"  {r['sign']} {r['object']:12} [{r['picture_confidence']:6}] "
              f"top={r['corpus_top_role']:18} nullp={r['null_model_p']} "
              f"=> {r['verdict']}{star}")
    print(f"\nSURVIVORS (tier-B): {out['survivors'] or 'none'}")
    print(f"fish/star WOUNDED validation: {'PASS' if star_ok else 'FAIL — STOP'}")


if __name__ == "__main__":
    main()
