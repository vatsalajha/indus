"""Breakthrough 4: does text content depend on the animal motif?
Chi-square over sign distributions across motif classes + jar-terminal
rate per motif. Pilot prediction: no dependence (the animal is not the
text's subject)."""
from collections import Counter, defaultdict

from scipy.stats import chi2_contingency

from common import JAR_W, load_fuls, save_result


def motif_class(motif):
    m = motif.lower()
    if m.startswith("bull"):
        return "bull"
    if m.startswith(("unicorn",)):
        return "unicorn"
    if m.startswith(("elep", "rhin", "goat", "gaur", "mult")):
        return "other_animal"
    if m in ("none", "-"):
        return "none"
    return "other"


def main():
    groups = defaultdict(list)
    for t, r in load_fuls():
        groups[motif_class(r["motif"])].append(t)
    res = {}
    # jar-terminal per motif
    for g, ts in sorted(groups.items()):
        jt = sum(1 for t in ts if t[-1] == JAR_W)
        res[g] = {"n": len(ts), "jar_terminal": f"{jt}/{len(ts)}"}
    # chi-square over top-sign distributions (motifs with n>=5 texts)
    big = {g: ts for g, ts in groups.items() if len(ts) >= 5}
    all_counts = Counter(s for ts in big.values() for t in ts for s in t)
    top_signs = [s for s, _ in all_counts.most_common(8)]
    table = []
    for g, ts in big.items():
        c = Counter(s for t in ts for s in t)
        table.append([c[s] for s in top_signs])
    if len(table) >= 2:
        chi2, p, dof, _ = chi2_contingency(table)
        res["chi_square"] = {"groups": list(big), "top_signs": top_signs,
                             "chi2": round(float(chi2), 2), "dof": int(dof),
                             "p": round(float(p), 4),
                             "caveat": "small-n pilot; expected counts low"}
    save_result("motif_test", res)
    print(f"[motif] jar-terminal by motif: "
          f"{ {g: v['jar_terminal'] for g, v in res.items() if isinstance(v, dict) and 'jar_terminal' in v} }")
    if "chi_square" in res:
        print(f"[motif] chi2={res['chi_square']['chi2']} p={res['chi_square']['p']}")


if __name__ == "__main__":
    main()
