# F1/F2 — real morphological baselines, and what they change

Goal: replace the 15-word hand samples (chat) with real corpora so the
morphology claim is trustworthy. Both baselines are now GOLD.

## Sources (real, pulled this session)

- **F1 Old Tamil / Sangam** — 74,070 words pulled from Project Madurai
  (Kuṟuntokai, Puṟanāṉūṟu, Naṟṟiṇai). Rule-based suffix stripping on raw
  sandhi'd verse proved unreliable for absolute depth (an honest dead end,
  documented in `baseline_old_tamil.py` history). Superseded by gold data:
- **Gold morphology** — Universal Dependencies treebanks (GitHub):
  `UD_Tamil-TTB` (Tamil, gold morpheme annotation; modern register, caveat)
  and `UD_Sanskrit-Vedic` (Vedic, 158k lexical tokens, gold). Parser:
  `baseline_from_ud.py`.

## The gold discriminator

| corpus | MWT split rate | feats / token | reading |
|---|---|---|---|
| Vedic Sanskrit (gold) | **0.000** | 3.02 | fusional: case+number+gender on one word, never split |
| Tamil (gold UD) | **0.097** | 3.60 | agglutinative: grammatical morphemes split into separate tokens |

`feats/token` is similar (~3) in both — both bundle features — so it does **not**
discriminate. The clean discriminator is **morpheme separability** (MWT rate):
Vedic never separates, Tamil does.

## The axis, rebuilt on gold data (`agglutination_axis.py`)

Cross-comparable, register-fair metric = **stacking rate** (fraction of units
expressing 2+ separable grammatical morphemes):

| corpus | stacking rate | 95% CI |
|---|---|---|
| Vedic Sanskrit (gold) | 0.000 | — |
| Tamil (gold UD) | 0.097 | — |
| **Indus mayig-179** | **0.080** | [0.040, 0.126] |
| **Indus ICIT-2511** | **0.125** | [0.112, 0.139] |

**Both Indus corpora sit at the Tamil rate and exclude the Vedic pole (0).**

## Two honest corrections this forces

1. **The 0.79 composite "agglutination score" is retired.** It was an artifact
   of tiny constructed samples (every word chosen to carry suffixes). On gold
   data the defensible statement is categorical (Indus stacks separably like
   Tamil; Vedic never does), not a single calibrated number.
2. **"Indus has reduced morphology vs Old Tamil" is NOT supported.** Gold Tamil
   *running text* stacks only ~10% of the time — Tamil itself is shallow in
   running text; the "deep Tamil" image came from constructed maximal forms.
   The Indus (8–13%) is at **parity** with attested agglutinative running text,
   not reduced. This weakens the "simplified/contact" depth argument the chat
   leaned on.

## What survives for the language question

- Indus expresses grammatical morphemes as **separable, stackable units** (like
  Tamil), categorically **unlike fusional Vedic** → excludes a fusional
  Indo-Aryan reading of the seal corpus; consistent with the Dravidian frame.
- The suffix-**order** result (jar→man) remains seal-construction-specific
  (fails M77 aggregate) — do not use it as morphological-order evidence.
- The **contact/Prakrit hypothesis (E)** must therefore rest on the *survivors*
  (separable stacking at the Tamil rate, terminal-set closure, jar suffix
  behaviour), NOT on a depth shortfall — because the depth shortfall does not
  exist against gold Tamil. E is still runnable but its center of gravity moves.
