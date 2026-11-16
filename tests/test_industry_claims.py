#!/usr/bin/env python3
"""test_industry_claims.py — the model against company claims (industry_claims.py).

Checks the split adds up, that it matches explore() and the scenarios, and that RESULTS.md carries the module's tables and
the figures its prose quotes, so a model change cannot leave the comparison stale. Run directly or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import industry_claims as IC  # noqa: E402
import scenarios as S  # noqa: E402


def check() -> list:
    fails = []
    s = IC.summary()
    for k, d in s["split"].items():
        if abs(d["capital"] + d["operating"] - d["total"]) > 1e-9:
            fails.append(f"{k}: plant charge + operating != total")
        if not 0 < d["capital"] < d["total"]:
            fails.append(f"{k}: plant charge out of range")
    for k in S.PAGE_ORDER:
        if abs(s["split"][k]["total"] - S.run(S.SCENARIOS[k].choice)["total"]) > 1e-9:
            fails.append(f"{k}: split total differs from the scenario")
    # drained and refilled: no filter, and cheaper plants lower only the plant charge
    vow = [d for _n, d in s["vow"]]
    if any(d["membranes"] != 0.0 for d in vow):
        fails.append("drained and refilled should need no filter membranes")
    if not vow[0]["capital"] > vow[1]["capital"] > vow[2]["capital"]:
        fails.append("cheaper plants should carry a smaller plant charge")
    if any(d27["total"] <= d["total"] for (_a, d), (_b, d27) in zip(s["vow"], s["vow27"])):
        fails.append("capping the density at 27 g/L should raise the cost")

    results = open(os.path.join(ROOT, "RESULTS.md"), encoding="utf-8").read()
    for line in IC.markdown().splitlines():
        if line.strip() and line not in results:
            fails.append(f"RESULTS.md does not carry: {line[:90]}")
    ops = [d["operating"] for d in vow]
    quoted = [f"${min(ops):.1f}–{max(ops):.1f}", f"${s['central_engineered']['operating']:.1f}",
              f"${s['split']['best']['operating']:.1f}",
              f"${min(d['capital'] for d in vow):.0f}–{max(d['capital'] for d in vow):.0f}",
              f"${vow[2]['total']:.1f}", f"${s['split']['central']['total']:.1f}", f"${vow[2]['capex_k_m3']:.0f}k",
              f"${min(d['total'] for _n, d in s['vow27']):.0f}–{max(d['total'] for _n, d in s['vow27']):.0f}"]
    for q in quoted:
        if q not in results:
            fails.append(f"RESULTS.md does not quote {q}")
    return fails


def main() -> None:
    fails = check()
    if fails:
        print("FAIL — industry claims:")
        for f in fails:
            print("  " + f)
        sys.exit(1)
    print("PASS — the comparison with company claims holds.")


if __name__ == "__main__":
    main()
