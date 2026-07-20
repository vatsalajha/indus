"""F1+F2: morphological baselines from GOLD Universal Dependencies treebanks —
Vedic Sanskrit (UD_Sanskrit-Vedic) and Tamil (UD_Tamil-TTB) — replacing the
hand-built samples with gold morpheme annotation.

The typological signature is directly visible in the annotation:
  - agglutinative (Tamil): orthographic words split into multiple syntactic
    tokens (multi-word tokens / MWT); grammatical morphemes are separable.
  - fusional (Sanskrit): one token carries fused Case+Number+Gender FEATS;
    no MWT splitting.

Metrics (comparable across both):
  mwt_split_rate      fraction of orthographic words that split into 2+ tokens
  mean_tokens_per_word  mean syntactic tokens per orthographic word
  feats_per_lex_token   mean morphological features on NOUN/VERB/ADJ/PRON (fusion density)
  case_number_cofused   of case-bearing tokens, fraction that ALSO carry Number
                        on the SAME token (the fusion fingerprint)

Honest note on comparability to the Indus: these gold metrics measure
morphology within an ORTHOGRAPHIC word system; the Indus writes each morpheme
as a separate sign (a script property), so the Indus is NOT placed on the MWT
axis directly. What the gold baselines establish is the reliable POLES and
which metrics discriminate; the Indus placement then rests on the register-fair
metrics (terminal-set closure, suffix-order), reported separately.

Output: results/baseline_old_tamil.json, results/baseline_sanskrit.json
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
# Universal Dependencies treebanks; see DATA.md. Override with $UD_DATA.
UD = os.environ.get("UD_DATA", os.path.join(ROOT, "data", "external"))
LEX = {"NOUN", "VERB", "ADJ", "PRON", "PROPN"}
MORPH_FEATS = {"Case", "Number", "Gender", "Person", "Tense", "Mood",
               "Voice", "VerbForm"}


def parse_conllu(paths):
    words = 0            # ALL orthographic words (MWT headers + free singletons)
    mwt_words = 0        # those that split into >1 token
    token_spans = []     # tokens per orthographic word
    feats_counts = []    # morph feats per lexical token
    case_tokens = 0
    case_and_number = 0
    for path in paths:
        covered_until = 0                  # last token id covered by an MWT span
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                if not line:
                    covered_until = 0      # reset at sentence boundary
                continue
            cols = line.split("\t")
            if len(cols) < 6:
                continue
            idx = cols[0]
            if "-" in idx:                 # MWT header = one orthographic word
                a, b = idx.split("-")
                span = int(b) - int(a) + 1
                words += 1
                token_spans.append(span)
                covered_until = int(b)
                if span > 1:
                    mwt_words += 1
                continue
            if "." in idx:                 # empty node
                continue
            # a plain integer token: a free orthographic word only if it is not
            # inside the current MWT span
            if int(idx) > covered_until:
                words += 1
                token_spans.append(1)
            upos = cols[3]
            feats = cols[5]
            fdict = {}
            if feats != "_":
                for kv in feats.split("|"):
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        fdict[k] = v
            if upos in LEX:
                feats_counts.append(sum(1 for k in fdict if k in MORPH_FEATS))
                if "Case" in fdict:
                    case_tokens += 1
                    if "Number" in fdict:
                        case_and_number += 1
    return {"lex_tokens": len(feats_counts),
            "orthographic_words_with_mwt_header": words,
            "mwt_split_rate": round(mwt_words / words, 3) if words else 0.0,
            "mean_tokens_per_mwt_word": round(sum(token_spans) / len(token_spans), 3)
            if token_spans else 1.0,
            "feats_per_lex_token": round(sum(feats_counts) / len(feats_counts), 3)
            if feats_counts else 0.0,
            "case_bearing_tokens": case_tokens,
            "case_number_cofused_rate": round(case_and_number / case_tokens, 3)
            if case_tokens else None}


def main():
    tamil = parse_conllu(glob.glob(os.path.join(UD, "UD_Tamil-TTB", "*.conllu")))
    tamil["corpus"] = "Tamil (UD_Tamil-TTB, gold; modern register — caveat)"
    tamil["note"] = ("Agglutinative pole. MWT splitting present: grammatical "
                     "morphemes separable. Register is modern Tamil, not Old "
                     "Tamil — used because it carries gold morpheme annotation "
                     "Sangam verse lacks.")
    json.dump(tamil, open(os.path.join(ROOT, "results",
                                       "baseline_old_tamil.json"), "w"), indent=1)

    vedic = parse_conllu(glob.glob(os.path.join(UD, "UD_Sanskrit-Vedic",
                                                "*.conllu")))
    vedic["corpus"] = "Vedic Sanskrit (UD_Sanskrit-Vedic, gold)"
    vedic["note"] = ("Fusional pole. Zero MWT splitting; Case+Number+Gender "
                     "fused onto single tokens.")
    json.dump(vedic, open(os.path.join(ROOT, "results",
                                       "baseline_sanskrit.json"), "w"), indent=1)

    print("=== GOLD UD morphological baselines ===")
    for name, r in [("Tamil (agglutinative)", tamil),
                    ("Vedic Sanskrit (fusional)", vedic)]:
        print(f"\n{name}: {r['lex_tokens']} lexical tokens")
        print(f"  MWT split rate:        {r['mwt_split_rate']}  "
              f"(fraction of words splitting into 2+ grammatical tokens)")
        print(f"  mean tokens/MWT word:  {r['mean_tokens_per_mwt_word']}")
        print(f"  feats per lex token:   {r['feats_per_lex_token']}  "
              f"(fusion density)")
        print(f"  case+number co-fused:  {r['case_number_cofused_rate']}")
    print("\nDISCRIMINATOR: Tamil splits grammatical morphemes into separate "
          "tokens (MWT rate {:.2f}); Vedic never does ({:.2f}), fusing "
          "case+number onto one word.".format(tamil['mwt_split_rate'],
                                              vedic['mwt_split_rate']))


if __name__ == "__main__":
    main()
