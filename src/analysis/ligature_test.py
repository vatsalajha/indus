"""Breakthrough 3: ligature decomposition — PARKED.

The compound/component tables live in the full *Catalog of Indus Signs*;
the 35-page preview on disk carries none of them (verified: signs.csv has
no component data). Recording the parked status so DASHBOARD.md is honest
rather than silently omitting the test.
"""
from common import save_result


def main():
    save_result("ligature_test", {
        "status": "PARKED",
        "reason": "compound/component tables absent from the Catalog preview; "
                  "requires the full book (or ICIT access) to run",
        "planned": "decompose compounds into components, rerun template test, "
                   "compare coverage",
    })
    print("[ligature] PARKED — needs full Catalog compound tables")


if __name__ == "__main__":
    main()
