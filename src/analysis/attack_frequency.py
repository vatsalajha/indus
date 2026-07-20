"""Attack 1: unigram frequencies, Zipf-Mandelbrot fit, hapax, coverage."""
import math
from collections import Counter

import numpy as np
from scipy.optimize import curve_fit

from common import load_fuls, load_mayig, save_result, write_table


def analyze(texts, label):
    counts = Counter(s for t, *_ in texts for s in t)
    total = sum(counts.values())
    ranked = counts.most_common()
    hapax = sum(1 for _, c in ranked if c == 1)
    cum, cov80 = 0, None
    for i, (_, c) in enumerate(ranked, 1):
        cum += c
        if cov80 is None and cum / total >= 0.8:
            cov80 = i
    # Zipf-Mandelbrot: f(r) = C / (r + beta)^alpha, fit on log f
    r = np.arange(1, len(ranked) + 1, dtype=float)
    fvals = np.array([c for _, c in ranked], dtype=float)

    def zm(r, logC, alpha, beta):
        return logC - alpha * np.log(r + beta)

    try:
        popt, _ = curve_fit(zm, r, np.log(fvals), p0=[math.log(fvals[0]), 1.0, 2.0],
                            maxfev=20000)
        logC, alpha, beta = float(popt[0]), float(popt[1]), float(popt[2])
        resid = np.log(fvals) - zm(r, *popt)
        r2 = 1 - float((resid ** 2).sum() / ((np.log(fvals) - np.log(fvals).mean()) ** 2).sum())
    except Exception:
        logC = alpha = beta = r2 = None
    out = {"tokens": total, "types": len(counts), "hapax": hapax,
           "hapax_frac_types": round(hapax / len(counts), 3),
           "signs_for_80pct": cov80, "zm_alpha": alpha, "zm_beta": beta,
           "zm_logC": logC,
           "zm_log_r2": r2,
           "top10": ranked[:10]}
    write_table(f"frequency_{label}.csv", ["rank", "sign", "count", "pct"],
                [(i, s, c, round(100 * c / total, 2))
                 for i, (s, c) in enumerate(ranked, 1)])
    return out


def main():
    res = {"fuls_preview": analyze(load_fuls(), "fuls"),
           "mayig_179": analyze(load_mayig(), "mayig")}
    save_result("attack_frequency", res)
    for k, v in res.items():
        print(f"[frequency] {k}: tokens={v['tokens']} types={v['types']} "
              f"hapax={v['hapax']} 80%@{v['signs_for_80pct']} "
              f"ZM alpha={v['zm_alpha'] and round(v['zm_alpha'],2)}")


if __name__ == "__main__":
    main()
