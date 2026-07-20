"""Phase 2.3: publication figures (matplotlib, serif, grayscale-safe,
300 dpi PNG + PDF). Identity is never carried by color alone: markers,
direct labels, and lightness-ordered grays do the work, so the figures
survive grayscale printing and all CVD types by construction.
"""
import csv
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "analysis"))
RESULTS = os.path.join(ROOT, "results")
TABLES = os.path.join(RESULTS, "tables")
FIGS = os.path.join(RESULTS, "figures")
os.makedirs(FIGS, exist_ok=True)

R = json.load(open(os.path.join(RESULTS, "results.json")))

plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": "#dddddd",
    "grid.linewidth": 0.5, "axes.axisbelow": True, "figure.dpi": 300,
})
GRAYS = ["#111111", "#555555", "#999999", "#bbbbbb"]


def save(fig, name):
    fig.savefig(os.path.join(FIGS, f"{name}.png"), dpi=300,
                bbox_inches="tight")
    fig.savefig(os.path.join(FIGS, f"{name}.pdf"), bbox_inches="tight")
    plt.close(fig)
    print(f"  {name}.png/.pdf")


def load_table(name):
    with open(os.path.join(TABLES, name)) as f:
        return list(csv.DictReader(f))


# ---- fig1: rank-frequency with Zipf-Mandelbrot fit -----------------------
def fig1():
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    for tab, label, marker, color in [
            ("frequency_mayig.csv", "CISI 179-seal corpus (this study)", "o", GRAYS[0]),
            ("frequency_fuls.csv", "ICIT preview corpus (53 texts)", "s", GRAYS[2])]:
        rows = load_table(tab)
        r = np.array([int(x["rank"]) for x in rows])
        f = np.array([int(x["count"]) for x in rows])
        ax.loglog(r, f, marker, ms=2.5, ls="none", color=color, label=label)
    zm = R["attack_frequency"]["mayig_179"]
    if zm["zm_alpha"]:
        rows = load_table("frequency_mayig.csv")
        r = np.array([int(x["rank"]) for x in rows], dtype=float)
        fit = np.exp(zm["zm_logC"]) / (r + zm["zm_beta"]) ** zm["zm_alpha"]
        ax.loglog(r, fit, "-", lw=1, color=GRAYS[1],
                  label=f"Zipf–Mandelbrot fit (α={zm['zm_alpha']:.2f})")
    ax.set_xlabel("sign rank")
    ax.set_ylabel("frequency")
    ax.legend(frameon=False, fontsize=7)
    save(fig, "fig1_zipf")


# ---- fig2: positional scatter, mayig ------------------------------------
def fig2():
    rows = load_table("positional_mayig.csv")
    MARKERS = {"SUF": "v", "OPEN": "^", "NUM": "s", "BODY": "o",
               "PRESUF": "D", "EARLY": "<"}
    LABELS = {"P324": "jar", "P217": "lance", "P086": "tree", "P385": "diamond",
              "P378": "wheel", "P050": "fish", "P122": "2-stroke",
              "P004": "bearer", "P013": "man"}
    fig, ax = plt.subplots(figsize=(4.4, 3.4))
    for cls, mk in MARKERS.items():
        xs = [float(r["mean_pos"]) for r in rows if r["class"] == cls]
        ys = [float(r["term_share"]) for r in rows if r["class"] == cls]
        ss = [10 + 2.2 * int(r["freq"]) for r in rows if r["class"] == cls]
        ax.scatter(xs, ys, s=ss, marker=mk, facecolors="white",
                   edgecolors=GRAYS[0], linewidths=0.8, label=cls)
    OFFS = {"P013": (-26, -3), "P004": (5, -3), "P324": (7, -1),
            "P217": (-32, 6), "P086": (6, 3), "P385": (6, 3),
            "P378": (6, 3), "P050": (5, -10), "P122": (-14, 8)}
    for r in rows:
        if r["sign"] in LABELS:
            ax.annotate(LABELS[r["sign"]],
                        (float(r["mean_pos"]), float(r["term_share"])),
                        textcoords="offset points",
                        xytext=OFFS.get(r["sign"], (4, 4)), fontsize=7)
    ax.set_xlabel("mean normalized position in text (0 = start, 1 = end)")
    ax.set_ylabel("share of occurrences in terminal slot")
    ax.legend(frameon=False, fontsize=7, title="slot class", title_fontsize=7)
    save(fig, "fig2_positional")


# ---- fig3: template coverage bars ---------------------------------------
def fig3():
    t = R["attack_template"]
    labels = ["CISI corpus\n(n=175)", "ICIT preview\n(n=46)"]
    real = [t["mayig_179"]["coverage"], t["fuls_preview"]["coverage"]]
    shuf = [t["mayig_179"]["shuffled_mean"], t["fuls_preview"]["shuffled_mean"]]
    x = np.arange(2)
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    b1 = ax.bar(x - 0.19, real, 0.34, color=GRAYS[0], label="observed order")
    b2 = ax.bar(x + 0.19, shuf, 0.34, color="white", edgecolor=GRAYS[0],
                hatch="///", label="shuffled control (mean of 1000)")
    for b in list(b1) + list(b2):
        ax.annotate(f"{b.get_height():.0%}", (b.get_x() + b.get_width() / 2,
                    b.get_height()), ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x, labels)
    ax.set_ylabel("texts conforming to 5-slot template")
    ax.set_ylim(0, 1.3)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.legend(frameon=False, fontsize=7, loc="upper left")
    save(fig, "fig3_template")


# ---- fig4: cosine similarity heatmap, top-25 mayig signs ----------------
def fig4():
    from attack_substitution import context_vectors, cos
    from common import load_mayig
    texts = load_mayig()
    ctx, freq = context_vectors(texts)
    top = [s for s, _ in freq.most_common(25)]
    M = np.array([[cos(ctx[a], ctx[b]) for b in top] for a in top])
    # order by average-linkage-ish: greedy chain from jar
    order = ["P324"] + [s for s in top if s != "P324"]
    idx = [top.index(s) for s in order]
    M = M[np.ix_(idx, idx)]
    fig, ax = plt.subplots(figsize=(4.6, 4.2))
    im = ax.imshow(M, cmap="Greys", vmin=0, vmax=1)
    ax.set_xticks(range(len(order)), order, rotation=90, fontsize=6)
    ax.set_yticks(range(len(order)), order, fontsize=6)
    ax.grid(False)
    fig.colorbar(im, ax=ax, shrink=0.7, label="context cosine similarity")
    save(fig, "fig4_cosine")


# ---- fig5: per-site coverage with bootstrap CIs -------------------------
def fig5():
    d = R["dialect_test"]
    entries = [("All sites", d["overall"])] + \
        [(s, v) for s, v in d.items()
         if isinstance(v, dict) and "coverage" in v and s != "overall"]
    fig, ax = plt.subplots(figsize=(3.8, 2.6))
    ys = np.arange(len(entries))
    for y, (site, v) in zip(ys, entries):
        lo, hi = v["ci95"]
        ax.plot([lo, hi], [y, y], "-", color=GRAYS[1], lw=1.5)
        ax.plot(v["coverage"], y, "o", color=GRAYS[0], ms=5)
        ax.annotate(f"n={v['n']}", (hi, y), textcoords="offset points",
                    xytext=(6, -2), fontsize=7, color=GRAYS[1])
    ax.set_yticks(ys, [e[0] for e in entries])
    ax.set_xlabel("template coverage (95% bootstrap CI)")
    ax.set_xlim(0, 1.05)
    save(fig, "fig5_sites")


# ---- fig6: what the numerals count --------------------------------------
def fig6():
    rows = load_table("numeral_counted.csv")[:10]
    rows = rows[::-1]
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    ys = np.arange(len(rows))
    counts = [int(r["count"]) for r in rows]
    names = [f"{r['sign']}  {r['desc'][:28]}" for r in rows]
    fish = ["fish" in r["desc"].lower() for r in rows]
    colors = [GRAYS[0] if f else "white" for f in fish]
    ax.barh(ys, counts, 0.62, color=colors, edgecolor=GRAYS[0])
    ax.set_yticks(ys, names, fontsize=7)
    ax.set_xlabel("times following a stroke numeral")
    ax.annotate("filled = fish signs", (0.97, 0.04), xycoords="axes fraction",
                ha="right", fontsize=7, color=GRAYS[1])
    save(fig, "fig6_numerals")


if __name__ == "__main__":
    print("rendering figures ->", FIGS)
    for f in (fig1, fig2, fig3, fig4, fig5, fig6):
        f()
