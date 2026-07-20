"""Second figure set (figA-D), reproducible from results/*.json. Same house
style as make_figures.py: serif, grayscale-safe, 300 dpi PNG+PDF.

figA  language placement — Indus on the agglutination axis vs Tamil/Vedic (+Gondi)
figB  rebus null — the 13 identifiable signs and their verdicts (0 survive)
figC  template replication — primary corpus vs the 2,511-seal robustness corpus
figD  integrity scorecard — every claim by whether it survived falsification
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
RES = os.path.join(ROOT, "results")
FIGS = os.path.join(RES, "figures")
os.makedirs(FIGS, exist_ok=True)


def R(name):
    return json.load(open(os.path.join(RES, name)))


plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": "#dddddd",
    "grid.linewidth": 0.5, "axes.axisbelow": True, "figure.dpi": 300,
})
GRAYS = ["#111111", "#555555", "#999999", "#bbbbbb"]


def save(fig, name):
    fig.savefig(os.path.join(FIGS, f"{name}.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(FIGS, f"{name}.pdf"), bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}.png/.pdf")


# ---- figA: language placement --------------------------------------------
def figA():
    ax_ = R("agglutination_axis.json")
    poles, indus = ax_["poles"], ax_["indus"]
    fig, ax = plt.subplots(figsize=(5.2, 2.4))
    pts = [
        ("Vedic Sanskrit\n(fusional)", poles["vedic_sanskrit_gold"], None, "s", GRAYS[2]),
        ("Tamil (gold)", poles["tamil_gold"], None, "^", GRAYS[1]),
        ("Indus — CISI 179", indus["mayig_179"]["rate"], indus["mayig_179"]["ci95"], "o", GRAYS[0]),
        ("Indus — ICIT 2,511", indus["icit_2511"]["rate"], indus["icit_2511"]["ci95"], "o", GRAYS[0]),
    ]
    for y, (lab, val, ci, mk, col) in enumerate(pts):
        if ci:
            ax.plot(ci, [y, y], "-", color=col, lw=1.4, zorder=1)
        ax.plot(val, y, mk, ms=8, color=col, zorder=2)
        ax.annotate(f"{val:.3f}", (val, y), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=7.5)
    ax.axvspan(-0.004, 0.004, color="#eeeeee", zorder=0)
    ax.set_yticks(range(len(pts)), [p[0] for p in pts])
    ax.set_ylim(-0.6, len(pts) - 0.4)
    ax.set_xlabel("separable-stacking rate  (0 = fully fused,  higher = agglutinative)")
    ax.annotate("fusional pole", (0.0, -0.5), fontsize=7, color=GRAYS[1], ha="left")
    ax.annotate("Gondi (S-C Dravidian): agglutinative by descriptive grammar; "
                "no annotated rate", (0.5, 1.02), xycoords="axes fraction",
                ha="center", fontsize=6.5, color=GRAYS[1])
    save(fig, "figA_language_placement")


# ---- figB: rebus null -----------------------------------------------------
def figB():
    g = R("rebus_gauntlet.json")
    rows = sorted(g["results"], key=lambda r: (r["picture_confidence"] != "high",
                                               r["sign"]))
    conf_x = {"high": 2, "medium": 1, "low": 0}
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    for y, r in enumerate(rows):
        x = conf_x[r["picture_confidence"]]
        lit = r["verdict"] == "LITERAL-CONSISTENT"
        mk = "o" if lit else "x"
        ax.plot(x, y, mk, ms=8, mfc="white" if lit else GRAYS[0],
                mec=GRAYS[0], color=GRAYS[0], mew=1.3)
        ax.annotate(f"{r['sign']} {r['object']}", (x, y),
                    textcoords="offset points", xytext=(10, 0), fontsize=7,
                    va="center")
    ax.set_yticks([])
    ax.set_xticks([0, 1, 2], ["low", "medium", "high"])
    ax.set_xlim(-0.5, 3.4)
    ax.set_ylim(-2.2, len(rows) + 0.5)
    ax.set_xlabel("pictogram identification confidence")
    ax.set_title("0 of 13 signs earn a surviving rebus reading\n"
                 "(o = literal-consistent; x = no reading)", fontsize=8.5)
    ax.annotate("the 3 high-confidence fish signs are used as literal\n"
                "counted nouns; fish = star is wounded (the mīn homophone\n"
                "is real in DEDR 4885~4876, but the position is wrong)",
                (2, 1.6), textcoords="offset points", xytext=(-90, 26),
                fontsize=6.3, color=GRAYS[1], ha="left",
                arrowprops=dict(arrowstyle="->", color=GRAYS[2], lw=0.7))
    save(fig, "figB_rebus_null")


# ---- figC: template replication ------------------------------------------
def figC():
    t = R("results.json")["attack_template"]
    big = R("bigcorpus_validation.json")
    groups = ["CISI 179\n(n=175)", "ICIT 2,511\n(n=2,511)"]
    real = [t["mayig_179"]["coverage"], big["template_coverage"]]
    shuf = [t["mayig_179"]["shuffled_mean"], big["template_shuffled"]]
    x = np.arange(2)
    fig, ax = plt.subplots(figsize=(3.8, 3.0))
    b1 = ax.bar(x - 0.19, real, 0.34, color=GRAYS[0], label="observed order")
    b2 = ax.bar(x + 0.19, shuf, 0.34, color="white", edgecolor=GRAYS[0],
                hatch="///", label="shuffled control")
    for b in list(b1) + list(b2):
        ax.annotate(f"{b.get_height():.0%}", (b.get_x() + b.get_width() / 2,
                    b.get_height()), ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x, groups)
    ax.set_ylabel("texts conforming to 5-slot template")
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0, .25, .5, .75, 1.0])
    ax.legend(frameon=False, fontsize=7.5, loc="upper right")
    ax.set_title("The grammar replicates at 14x scale (p < 0.001 both)", fontsize=8.5)
    save(fig, "figC_template_replication")


# ---- figD: integrity scorecard -------------------------------------------
def figD():
    # (claim, status) — status in {survive, wounded, null, withdrawn, secondary}
    items = [
        ("Jar = grammatical suffix (L/R 4.2, number-independent)", "survive"),
        ("Terminal paradigm recovered blind (6/6)", "survive"),
        ("5-slot grammar vs shuffled (75/23; replicates 71/27)", "survive"),
        ("Suffix class text-final on M77 (p<1e-4)", "survive"),
        ("Opener class text-initial on M77 (p=0.004)", "survive"),
        ("Agglutinative/Dravidian placement (2 clean metrics)", "survive"),
        ("Fish = countable noun", "survive"),
        ("Fish = star / asterism name", "wounded"),
        ("Any phonetic rebus survives null model (0/13)", "wounded"),
        ("Modifier-before-head word order", "null"),
        ("Regional dialects", "null"),
        ("Reduced morphology vs Old Tamil", "withdrawn"),
        ("Contact vs simple Dravidian distinguishable", "withdrawn"),
        ("2,511 corpus verified seal-by-seal (27/27 shared)", "secondary"),
    ]
    # (marker, markerfacecolor, edgecolor, label) — no unicode glyphs
    style = {
        "survive":  ("o", GRAYS[0], GRAYS[0], "survives falsification"),
        "wounded":  ("X", "#a8452e", "#a8452e", "wounded by our own test"),
        "null":     ("o", "white", GRAYS[2], "null / underpowered"),
        "withdrawn":("P", "#888888", "#888888", "withdrawn on gold data"),
        "secondary":(">", "#3f7c86", "#3f7c86", "secondary / partially verified"),
    }
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    for i, (claim, st) in enumerate(reversed(items)):
        mk, mfc, mec, _ = style[st]
        ax.plot(0, i, marker=mk, mfc=mfc, mec=mec, ms=9, mew=1.4,
                color=mec, linestyle="none")
        ax.text(0.4, i, claim, fontsize=8, va="center")
    ax.set_xlim(-0.5, 9)
    ax.set_ylim(-1.5, len(items))
    ax.axis("off")
    handles = [plt.Line2D([0], [0], marker=m, color="w", markerfacecolor=fc,
               markeredgecolor=ec, label=d, markersize=8)
               for m, fc, ec, d in style.values()]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=7,
              handletextpad=0.3, ncol=1)
    ax.set_title("Integrity scorecard: every claim by whether it survived our "
                 "own falsification", fontsize=9, loc="left")
    save(fig, "figD_scorecard")


if __name__ == "__main__":
    print("rendering figA-D ->", FIGS)
    figA(); figB(); figC(); figD()
