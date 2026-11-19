#!/usr/bin/env python3
"""test_market_size_loop.py — cost falling with market size, solved with the share (market_size_loop.py).

Checks that with no learning the module returns each scenario's own cost, that cost falls with volume and never below the cost at the
floors, that a resting point is one (its cost buys the share its volume is), and the conclusions the note draws since shoppers'
liking became a Student's t spread (2026-11-19, second round): Selected cells' whole sales need four to six times the membrane switch; its
premium products alone reach it, but only with premium fillets and shrimp counted; premium products are about a quarter of its first
sales and cuts most of them; with slow learning it has one resting point; published cells never start on their own; about a quarter
of Selected cells' gain comes from later rounds; and the premium products respond to price more than twice as strongly as farmed salmon did
along its demand curve, inside history's totals. Also that the note and RESULTS.md carry the module's tables and the figures their
prose quotes. Runs as a script or under pytest.
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
    # 2026-11-19 second round (Student's t spread of liking; first sales doubled by the heavier tail). Selected cells sells 0.55 Mt a year
    # at its own cost (0.26 with the audit batch's normal spread, 1.78 before the batch), needing 4.86 million m2 of membrane: 4.9
    # times the switch (was 2.3 times; ten before the batch). Premium products alone reach the switch (1.31 million m2) only because
    # the new row of premium fillets and shrimp counts as premium; the four small premium markets alone fall short (0.62). Without
    # any premium product its other sales still cross (3.55). The Engineered cells, all favourable case's cells cross on premium products alone (5.13);
    # published cells do not (0.12 million m2 for all their sales).
    W = value("ms_world_meat")
    for k in L.SCEN:
        st = s["start"][(k, "central")]
        if abs(st["whole_mt"] - s["model_share"][k] / 100.0 * W) > 1e-6 + 1e-6 * st["whole_mt"]:
            fails.append(f"{k}: the volumes by tier at its own cost do not add to the model's share")
        if st["crosses"] != (k != "today") or st["whole_crosses"] != (k != "today"):
            fails.append(f"{k}: premium products alone, or the whole sales, now stand differently against the membrane switch; rewrite the note")
    st = s["start"][("central", "central")]
    if not (st["switch_m2"] < st["area_m2"] < 1.5 * st["switch_m2"] and not st["small_crosses"]):
        fails.append("Selected cells' premium products alone no longer reach the switch by under half, and only with premium fillets and "
                     "shrimp; rewrite the note")
    if not 4.0 * st["switch_m2"] < st["whole_area_m2"] < 6.0 * st["switch_m2"]:
        fails.append("Selected cells' whole sales no longer need four to six times the switch's membrane area; rewrite the note")
    if not st["whole_area_m2"] - st["area_m2"] > _case("slow learning")["ms_switch_area"]:
        fails.append("without premium products Selected cells' other sales no longer pass even a 3 million m2 switch; rewrite the note")
    if not s["start"][("best", "central")]["small_crosses"]:
        fails.append("the Engineered cells, all favourable case's four small premium markets alone no longer cross the switch; rewrite the note")
    # 2026-11-19 second round: a switch at 3 million m2 is again below what Selected cells' sales need (4.86 million), so with slow
    # learning it crosses on its own and has ONE resting point, $21.91 and 0.59%. (With the audit batch's normal spread: two,
    # $32.48 left alone and $22.07 if pushed. After the cut-cost repin: one, $18.69.) With everything else central a 3 million m2
    # switch costs it 21 cents (was: stopped it at $31.66).
    lo, hi = s["solved"][("central", "slow learning", "below")], s["solved"][("central", "slow learning", "above")]
    own, slow_switch = s["base"]["central"]["cost"], _case("slow learning")["ms_switch_area"]
    if not (abs(hi["volume_mt"] - lo["volume_mt"]) < 1e-3 * hi["volume_mt"] and lo["area_m2"] > slow_switch and lo["cost"] < 0.8 * own):
        fails.append("Selected cells with slow learning no longer crosses the switch on its own to one resting point; rewrite the note's section 3")
    sw = s["sens"]["central"][0]["cost"]
    if not (sw[1] < 0.6 * own and sw[1] - sw[0] < 0.5):
        fails.append("the switch's level now moves Selected cells' resting cost by 50 cents or more; the note says it matters little")
    # 2026-11-19 second round: published cells cost $111.89 and sell 0.002% of world meat (about 6,000 t a year). Left alone they
    # stay within $2 of their own cost in every case; only fast learning has an upper resting point ($75.43), which needs a push.
    # (With the normal spread they sold nothing and had one resting point everywhere.)
    t0 = s["base"]["today"]["cost"]
    if not all(s["solved"][("today", case, "below")]["cost"] > t0 - 2.0 for case in L.CASES) or not all(
            s["solved"][("today", case, start)]["share"] < 0.01 for case in L.CASES for start in ("below", "above")):
        fails.append("published cells now leave their own cost unaided, or reach 0.01% of world meat; the note says they never start on their own")
    up = s["solved"][("today", "fast learning", "above")]
    if not (up["cost"] < 0.8 * t0 and all(abs(s["solved"][("today", case, "above")]["cost"] - s["solved"][("today", case, "below")]["cost"]) < 0.01
                                          for case in L.CASES if case != "fast learning")):
        fails.append("published cells no longer have an upper resting point with fast learning only; rewrite the note's section 3")
    # 2026-11-19 second round: premium products are about a quarter of Selected cells' first sales (27%; 13% without premium fillets and
    # shrimp) and ordinary cuts most of them (62%). (With the normal spread: premium 47%, beef steaks the other half. Before the
    # audit batch: premium 11%.)
    c0 = s["comp"][("central", "no learning")]
    if not (0.2 < c0["premium_of_sales"] < 0.35 and 0.08 < c0["premium_small_of_sales"] < 0.2 and c0["cut"] > 0.5 * c0["total"]):
        fails.append("premium products are no longer about a quarter of Selected cells' sales at its own cost, or cuts no longer most of them; "
                     "rewrite the note")
    # 2026-11-19 second round: all five premium products respond to price at 3.3-3.7, whether cultivated meat stays dearer or ends
    # cheaper: more than twice the top of farmed salmon's range along the demand curve (1-1.5), so the check still fails, but inside
    # history's totals (1.3-4.1). (With the normal spread: 5.2-7.5 where dearer, above the totals; 2.6 and 3.3 where cheaper.)
    resp = s["response"]["products"]
    if sorted(resp) != ["beef (prime/wagyu)", "chicken (organic)", "pork (heritage)", "seafood (premium fillet, shrimp)", "seafood (sushi)"]:
        fails.append("the model's premium products are no longer the five the note lists; rewrite the note")
    for n, v in resp.items():
        if not 2.0 * L.HISTORY_ALONG_CURVE[1] < v["response"] < L.HISTORY_TOTAL[1]:
            fails.append(f"{n}: the response to price is no longer more than twice salmon's range along the curve and inside history's "
                         "totals; rewrite the note")

    # 2026-11-19 second round: Selected cells' own volume is 4.9 times the switch, so the first pass buys most of the learning: later
    # rounds give 25% of its share gain (35% with the normal spread; 19% before the audit batch). The Engineered cells, all favourable case's cells: 5%.
    if not 0.15 < s["passes"]["central"]["later_rounds"] < 0.35:
        fails.append("later rounds no longer give about a quarter of Selected cells' share gain; rewrite the note's section 5")
    if not s["passes"]["best"]["later_rounds"] < 0.15:
        fails.append("best: later rounds now give 15% or more of the share gain; the note says it is one step")
    # 2026-11-19 second round: at Selected cells' own cost the model now gives more than the curve fitted to premium meats (0.16% against 0.10%)
    if not s["anchored"]["central"]["own"] < s["model_share"]["central"]:
        fails.append("at Selected cells' own cost the demand anchored on premium meats is no longer below the model's; rewrite the note")
    if not s["anchored"]["best"]["share"] < 0.7 * s["passes"]["best"]["rest"][1]:
        fails.append("the Engineered cells, all favourable case's share with demand anchored on premium meats is no longer well below the main model's; rewrite the note")

    sv = s["solved"]
    quoted = []
    for k in L.SCEN:
        for case in L.CASES:
            r = sv[(k, case, "below")]
            quoted += [f"${r['cost']:.2f}", L._pct(r["share"])]       # 2026-11-19 audit batch: shares under 0.01% are written so
        quoted.append(f"${s['floor'][k]['cost']:.2f}")
    # 2026-11-19 audit batch: every share in this study uses the model's ordinary demand (13% at equal price). The note also gives
    # the Engineered cells, all favourable case's cells with the Engineered cells, all favourable case's own demand (55%): they rest at the floors.
    own_demand = lambda cost: S.shares(cost, regions=("global",), eqs="best_equal_price_share")["global"]
    r = L.solve(S.SCENARIOS["best"].choice, share=own_demand)
    if abs(r["cost"] - s["floor"]["best"]["cost"]) > 0.01:
        fails.append("with its own demand the Engineered cells, all favourable case's cells no longer rest at the floors; rewrite the note")
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
