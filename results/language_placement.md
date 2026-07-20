# Language placement — Indus vs three real baselines

**Register caveat.** Seals are a formal register (name-tags), not running speech. Register reduces morphology independently of language family; morphological simplicity on seals is NOT by itself evidence of language change.

## Metric 1 — stacking rate (DISCRIMINATING)

| corpus | family | stacking rate | note |
|---|---|---|---|
| Vedic Sanskrit | Indo-Aryan (fusional) | 0.0 | gold UD, 158k tokens |
| Tamil | South Dravidian (aggl.) | 0.097 | gold UD |
| Gondi | S-C Dravidian (aggl.) | n/a | descriptive only — no annotated corpus |
| Indus mayig-179 | — | 0.08 | CI [0.04, 0.126] |
| Indus ICIT-2511 | — | 0.125 | CI [0.112, 0.139] |

## Metric 2 — separates case & number (DISCRIMINATING, binary)

| corpus | separable? | basis |
|---|---|---|
| Vedic Sanskrit | no (0) | case+number+gender fused into one ending |
| Tamil | yes (1) | case/number separable |
| Gondi | yes (1) | obligatory stem+oblique+case stacking (descriptive) |
| Indus | yes (1) | each grammatical element a separate sign |

## Metric 3 — fusion density (UNINFORMATIVE)

Tamil 3.595 vs Vedic 3.021 feats/token — does not discriminate; not used.

## Gondi's contribution

Gondi (a different, S-Central Dravidian branch) is agglutinative by descriptive grammar, so Indus at the agglutinative pole supports 'Dravidian' broadly, not merely 'Tamil-like'. BUT no gold Gondi rate exists, so the quantitative 'does Indus sit BETWEEN Tamil and Gondi' test the contact hypothesis needs CANNOT be run. Contact stays non-distinguishable from simple Dravidian on this evidence.

## Claim ceiling

Indus seal structure patterns with the agglutinative (Dravidian) baselines on the discriminating axis (separable case/number marking) and is inconsistent with a fully inflectional Indo-Aryan (Vedic) profile. It sits at the running-text stacking rate of gold Tamil, NOT reduced below it. The evidence cannot distinguish simple Dravidian from a Dravidian contact language, and assigns no sounds.
