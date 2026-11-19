#!/usr/bin/env python3
"""test_market_size_loop.py — cost falling with market size, solved with the share (market_size_loop.py).

Checks that with no learning the module returns each scenario's own cost, that cost falls with volume and never below the cost at the
floors, that a resting point is one (its cost buys the share its volume is), and the conclusions the note draws since the audit batch
of 2026-11-19: Central's whole sales need two to three times the membrane switch; its premium products alone just reach it, and only
with premium fillets and shrimp counted; premium products are about half of its first sales; with slow learning it has two resting
points; published cells never start; about a third of Central's gain comes from later rounds; and the premium products respond to
price more strongly than history. Also that the note and RESULTS.md carry the module's tables and the figures their prose quotes.
Runs as a script or under pytest.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import market_size_loop as L  # noqa: E402
from market_size_loop import _case  # noqa: E402
import scenarios as S  # noqa: E402
from inputs import value  # noqa: E402


def check() -> list:
    fails = []
    s = L.summary()
    none = {"ms_switch_area": L.NEVER, "ms_lr_plant": 0.0}       # no food-grade supplier and no plant learning
    for k in L.SCEN:
        choice = S.SCENARIOS[k].choice
        own = S.run(choice)["total"]
        if abs(L.cost_at(choice, 5.0, none)["cost"] - own) > 1e-9 or abs(L.cost_at(choice, 0.0)["cost"] - own) > 1e-9:
            fails.append(f"{k}: with no learning, or no volume, the cost is not the scenario's own")
        costs = [r["cost"] for r in s["ladder"][k]]
        if costs != sorted(costs, reverse=True):
            fails.append(f"{k}: the cost should fall as the volume rises")
        if not s["floor"][k]["cost"] <= costs[-1] + 1e-9:
            fails.append(f"{k}: a cost on the ladder is below the cost at the floors")
        for case in L.CASES:
            for start in ("below", "above"):
                r = s["solved"][(k, case, start)]
                if abs(r["share"] - 100.0 * r["volume_mt"] / value("ms_world_meat")) > 1e-3:
                    fails.append(f"{k}, {case}, from {start}: the resting point's cost does not buy the share its volume is")
        lo, hi = s["solved"][(k, "central", "below")], s["solved"][(k, "central", "above")]
        if abs(lo["volume_mt"] - hi["volume_mt"]) > 1e-3 * hi["volume_mt"] + 1e-6:
            fails.append(f"{k}: two resting points in the central case now; the note says there is one")
        if k != "today" and not lo["share"] > s["model_share"][k]:
            fails.append(f"{k}: learning no longer raises the share; rewrite the note")
        c = s["comp"][(k, "resting point")]
        if abs(c["total"] - lo["volume_mt"]) > 1e-3 * lo["volume_mt"] + 1e-6:
            fails.append(f"{k}: the volumes by tier do not add to the resting point's volume")
    # 2026-11-19 audit batch: cells dearer (Central $32.80), seafood re-priced, the tier rule replaced. Central sells 0.26 Mt a year at
    # its own cost (was 1.78), needing 2.33 million m2 of membrane: 2.3 times the switch (was ten times). Premium products alone
    # just reach the switch (1.09 million m2) only because the new row of premium fillets and shrimp counts as premium; the four
    # small premium markets alone fall short (0.71). The best case's cells cross on premium products alone now (5.19 million m2);
    # published cells sell nothing. (Was: premium alone crosses for Central only, at 1.11 million m2.)
    W = value("ms_world_meat")
    for k in L.SCEN:
        st = s["start"][(k, "central")]
        if abs(st["whole_mt"] - s["model_share"][k] / 100.0 * W) > 1e-6 + 1e-6 * st["whole_mt"]:
            fails.append(f"{k}: the volumes by tier at its own cost do not add to the model's share")
        if st["crosses"] != (k != "today") or st["whole_crosses"] != (k != "today"):
            fails.append(f"{k}: premium products alone, or the whole sales, now stand differently against the membrane switch; rewrite the note")
    st = s["start"][("central", "central")]
    if not (st["area_m2"] < 1.25 * st["switch_m2"] and not st["small_crosses"]):
        fails.append("Central's premium products alone no longer just reach the switch, and only with premium fillets and shrimp; rewrite the note")
    if not 1.5 * st["switch_m2"] < st["whole_area_m2"] < 3.0 * st["switch_m2"]:
        fails.append("Central's whole sales no longer need two to three times the switch's membrane area; rewrite the note")
    if not s["start"][("best", "central")]["small_crosses"]:
        fails.append("the best case's four small premium markets alone no longer cross the switch; rewrite the note")
    # 2026-11-19 audit batch: a switch at 3 million m2 is now above what Central's sales need (2.33 million), so with slow learning
    # it has two resting points: left alone near its own cost ($32.48, 0.08%), pushed across at $22.07 and 0.47%. (Was: one resting
    # point at $18.69, crossing on its own sales.) With everything else central a 3 million m2 switch also stops it ($31.66); one
    # at 2.5 million does not.
    lo, hi = s["solved"][("central", "slow learning", "below")], s["solved"][("central", "slow learning", "above")]
    own, slow_switch = s["base"]["central"]["cost"], _case("slow learning")["ms_switch_area"]
    if not (hi["volume_mt"] > 3.0 * lo["volume_mt"] and lo["area_m2"] < slow_switch < hi["area_m2"]
            and lo["cost"] > 0.95 * own and hi["cost"] < 0.8 * own):
        fails.append("Central with slow learning no longer has two resting points, one near its own cost and one well below it; "
                     "rewrite the note's section 3")
    if not (s["sens"]["central"][0]["cost"][1] > 0.9 * own
            and L.solve(S.SCENARIOS["central"].choice, {"ms_switch_area": 2.5e6})["cost"] < 0.7 * own):
        fails.append("Central no longer crosses a 2.5 million m2 switch on its own and stops at a 3 million one; rewrite the note")
    # 2026-11-19 audit batch: published cells cost $111.89 and sell under 0.001%, so nothing starts in any case, fast learning
    # included. (Was: fast learning took them to $33.67.)
    if not all(abs(s["solved"][("today", case, start)]["cost"] - s["base"]["today"]["cost"]) < 0.01 and
               s["solved"][("today", case, start)]["share"] < 0.01 for case in L.CASES for start in ("below", "above")):
        fails.append("published cells now leave their own cost in some case; the note says they never start")
    # 2026-11-19 audit batch: premium products are about half of Central's first sales (47%; 30% without premium fillets and
    # shrimp) and cuts, nearly all beef steaks, the other half. (Was: premium 11%, ordinary cuts most of it.)
    c0 = s["comp"][("central", "no learning")]
    if not (0.35 < c0["premium_of_sales"] < 0.6 and 0.2 < c0["premium_small_of_sales"] < 0.4
            and 0.4 * c0["total"] < c0["cut"] < 0.65 * c0["total"]):
        fails.append("premium products are no longer about half of Central's sales at its own cost and cuts the other half; rewrite the note")
    # 2026-11-19 audit batch: with the tier rule gone the premium products respond to price MORE strongly than history, and the
    # note says this check fails. Where cultivated meat stays dearer than the product at both costs (organic chicken, heritage
    # pork, premium fillets and shrimp) the response is 5.2-7.5, above history's totals (1.3-4.1); where it ends cheaper (prime
    # beef 0.59x, sushi-grade seafood 0.76x at $17.75) it is 2.6 and 3.3, above salmon's range along the curve (1-1.5) and inside
    # the totals. (Was: 1.3-1.5 where dearer, inside history's range; 0.6-0.7 where it undercut, below it.)
    resp = s["response"]["products"]
    if sorted(resp) != ["beef (prime/wagyu)", "chicken (organic)", "pork (heritage)", "seafood (premium fillet, shrimp)", "seafood (sushi)"]:
        fails.append("the model's premium products are no longer the five the note lists; rewrite the note")
    for n, v in resp.items():
        dearer = v["R"][1] > 1.0
        if dearer and not v["response"] > L.HISTORY_TOTAL[1]:
            fails.append(f"{n}: the response to price where cultivated meat stays dearer is no longer above history's totals; rewrite the note")
        if not dearer and not L.HISTORY_ALONG_CURVE[1] < v["response"] < L.HISTORY_TOTAL[1]:
            fails.append(f"{n}: the response to price where cultivated meat ends cheaper is no longer above salmon's range and inside "
                         "history's totals; rewrite the note")

    # 2026-11-19 audit batch: Central's own volume is only 2.3 times the switch, so the first pass buys less learning: later
    # rounds give 35% of its share gain (was 19%, "mostly one step"). The best case's cells still gain in one step (5%).
    if not 0.25 < s["passes"]["central"]["later_rounds"] < 0.5:
        fails.append("later rounds no longer give about a third of Central's share gain; rewrite the note's section 5")
    if not s["passes"]["best"]["later_rounds"] < 0.15:
        fails.append("best: later rounds now give 15% or more of the share gain; the note says it is one step")
    if not s["anchored"]["best"]["share"] < 0.7 * s["passes"]["best"]["rest"][1]:
        fails.append("the best case's share with demand anchored on premium meats is no longer well below the main model's; rewrite the note")

    sv = s["solved"]
    quoted = []
    for k in L.SCEN:
        for case in L.CASES:
            r = sv[(k, case, "below")]
            quoted += [f"${r['cost']:.2f}", L._pct(r["share"])]       # 2026-11-19 audit batch: shares under 0.01% are written so
        quoted.append(f"${s['floor'][k]['cost']:.2f}")
    # 2026-11-19 audit batch: every share in this study uses the model's ordinary demand (13% at equal price). The note also gives
    # the best case's cells with the best case's own demand (55%): they rest at the floors.
    own_demand = lambda cost: S.shares(cost, regions=("global",), eqs="best_equal_price_share")["global"]
    r = L.solve(S.SCENARIOS["best"].choice, share=own_demand)
    if abs(r["cost"] - s["floor"]["best"]["cost"]) > 0.01:
        fails.append("with its own demand the best case's cells no longer rest at the floors; rewrite the note")
    quoted += [f"{own_demand(s['base']['best']['cost']):.1f}%", f"{r['share']:.1f}%"]
    for name, tables in (("research_notes/market_size_loop.md", [L.markdown_ladder(), L.markdown_solved(), L.markdown_composition(), L.markdown_start(), L.markdown_passes(),
                          L.markdown_sensitivity(), L.markdown_response()]), ("RESULTS.md", [])):
        text = open(os.path.join(ROOT, name), encoding="utf-8").read()
        for line in "\n".join(tables).splitlines():
            if line.strip() and line not in text:
                fails.append(f"{name} does not carry: {line[:90]}")
        up = sv[("central", "central", "above")]
        for q in (quoted if name.startswith("research") else
                  [f"${sv[('central', 'central', 'below')]['cost']:.2f}", f"${up['cost']:.2f}", L._pct(up["share"]),
                   f"${sv[('best', 'central', 'below')]['cost']:.2f}", L._pct(sv[("best", "central", "below")]["share"])]):
            if q not in text:
                fails.append(f"{name} does not quote {q}")
    return fails


def test_market_size_loop():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("market size loop: all checks passed")
