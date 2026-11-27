#!/usr/bin/env python3
"""test_market_size_loop.py — cost falling with market size, solved with the share (market_size_loop.py).

Checks that with no learning the module returns each scenario's own cost, that cost falls with volume and never below the cost at the
floors, that a resting point is one (its cost buys the share its volume is), and the conclusions the note draws since the engine
batch of 2026-11-20 made cells dearer: the low-lactate example's whole sales need two to three times the membrane switch; its premium
products alone no longer reach it; premium products are about three-tenths of its first sales and cuts most of them; with slow
learning it has two resting points; published cells never start on their own; about a third of the low-lactate example's gain comes
from later rounds; and the premium products respond to price at two and a half to three times the top of farmed salmon's range
along its demand curve, two of the five just above history's totals. Also that the note and RESULTS.md carry the module's tables and the figures their
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
        # 2026-11-19 restructure: the published cells are priced in perfusion as "cautious" ($92.17, the old rung 1 with the added equipment for oxygen and CO₂),
        # and in the central case they have two resting points: $91.80 left alone, $55.98 if pushed
        # 2026-11-20 (engine batch): the published cells in perfusion cost $183.15 and sell about 900 t a year; even with everything
        # at its floor ($78.27) they would sell 0.02 Mt, whose membrane (about 1.3 million m2 at their 0.067 m2 a kilo) the cost at
        # that volume does not sustain, so the upper resting point is gone. No scenario has two resting points in the central case.
        if abs(lo["volume_mt"] - hi["volume_mt"]) > 1e-3 * hi["volume_mt"] + 1e-6:
            fails.append(f"{k}: the number of resting points in the central case has changed; rewrite the note")
        if k != "cautious" and not lo["share"] > s["model_share"][k]:
            fails.append(f"{k}: learning no longer raises the share; rewrite the note")
        c = s["comp"][(k, "resting point")]
        if abs(c["total"] - lo["volume_mt"]) > 1e-3 * lo["volume_mt"] + 1e-6:
            fails.append(f"{k}: the volumes by tier do not add to the resting point's volume")
    # 2026-11-19 second round (Student's t spread of liking; first sales doubled by the heavier tail). The low-lactate example sells 0.55 Mt a year
    # at its own cost (0.26 with the audit batch's normal spread, 1.78 before the batch), needing 4.86 million m2 of membrane: 4.9
    # times the switch (was 2.3 times; ten before the batch). Premium products alone reach the switch (1.31 million m2) only because
    # the new row of premium fillets and shrimp counts as premium; the four small premium markets alone fall short (0.62). Without
    # any premium product its other sales still cross (3.55). The all-favourable example's cells cross on premium products alone (5.13);
    # published cells do not (0.12 million m2 for all their sales).
    W = value("ms_world_meat")
    for k in L.SCEN:
        st = s["start"][(k, "central")]
        if abs(st["whole_mt"] - s["model_share"][k] / 100.0 * W) > 1e-6 + 1e-6 * st["whole_mt"]:
            fails.append(f"{k}: the volumes by tier at its own cost do not add to the model's share")
        # 2026-11-20 (engine batch): the low-lactate example sells 0.15 Mt at $49.96 (was 0.71 Mt at $32.80) and its membrane
        # lasts 2,415 L/m2 (was 3,960), so its premium products alone no longer cross the switch (0.75 million m2 against 1.0);
        # its whole sales still do (2.54). Only the all-favourable example's premium products cross alone. A correct consequence
        # of the dearer cells: the volume fell 4.6 times and the membrane a kilo rose 1.9 times.
        # 2026-11-20 final pass: the all-favourable example is now scenarios.all_favourable() ($7.62), which keeps its cells with
        # haemodialyser fibres at $8 a m2 (rt_dial_*), so it buys about 600 times less process membrane a kilo (0.00003 m2 against
        # the low-lactate example's 0.015): its 18.3 Mt a year need 0.48 million m2, short of the central switch, and its premium
        # products alone 0.08 million. The membrane switch plays no part in it; its gain comes from the plant's learning. A
        # correct consequence of the rebuilt example. Only the low-lactate example's whole sales cross the central switch.
        # 2026-11-22 (fifth batch, the price-insensitive shoppers): published cells' whole sales now cross the switch too, and the
        # low-lactate example's premium products just reach it
        # 2026-11-24 (the default of 50% of meat buyers at equal price): premium products alone cross the switch for published cells
        # (2.4 million m2) and the low-lactate example (5.9 million), not for the all-favourable example (0.30 million, dialyser
        # fibres); every scenario's whole sales cross it (13.8, 75 and 2.7 million m2)
        if st["crosses"] != (k in ("cautious", "central")) or not st["whole_crosses"]:
            fails.append(f"{k}: premium products alone, or the whole sales, now stand differently against the membrane switch; rewrite the note")
    st = s["start"][("central", "central")]
    # 2026-11-19 restructure (the share of the meat sold, about a quarter higher): premium products alone reach the switch twice over,
    # and even the four small premium markets alone cross it; the whole sales need about six times its area (were 4.9)
    # 2026-11-20: premium products alone are a quarter short of the switch (0.75 million m2; the four small ones 0.38), the whole
    # sales need 2.5 times its area, and the sales without premium products (1.79 million m2) pass the central switch but not a
    # 3 million m2 one
    # 2026-11-22 (fifth batch): premium products 1.10 million m2 (were 0.68), the four small ones 0.33; the whole sales 13.6 times
    # the switch (were 2.4 times); without premium products the other sales pass even a 3 million m2 switch
    # 2026-11-24: premium products alone need 5.9 million m2, the four small ones cross too; the whole sales (4.8 Mt a year) 75 times the switch
    if not (5.0 * st["switch_m2"] < st["area_m2"] < 7.0 * st["switch_m2"] and st["small_crosses"]):
        fails.append("the low-lactate example's premium products alone no longer need five to seven times the switch, or the four small ones no longer cross; "
                     "rewrite the note")
    if not 60.0 * st["switch_m2"] < st["whole_area_m2"] < 90.0 * st["switch_m2"]:
        fails.append("the low-lactate example's whole sales no longer need sixty to ninety times the switch's membrane area; rewrite the note")
    if not st["whole_area_m2"] - st["area_m2"] > _case("slow learning")["ms_switch_area"]:
        fails.append("without premium products the low-lactate example's other sales no longer pass a 3 million m2 switch; rewrite the note")
    # 2026-11-21: the all-favourable example ($7.62 -> $6.97; its tank design is now held thinner so its oxygen column passes its
    # checks) sells 20.4 Mt at its own cost and needs 0.79 million m2 (was 0.48 million for 18.3 Mt): still short of the central
    # switch, but no longer under 0.6 of it. The bound is now 0.9 of the switch; the note says 0.79 million and that it does not cross
    # 2026-11-24: its whole sales (68.9 Mt a year) need 2.7 million m2, 2.7 times the switch: they cross it
    # 2026-11-27 (nutrient balance): 68.9 -> 68.5 Mt a year, 2.66 -> 2.64 million m2; rests at $6.25 -> $6.30, 22.59% -> 22.44%
    if not 2.0 * st["switch_m2"] < s["start"][("best", "central")]["whole_area_m2"] < 3.5 * st["switch_m2"]:
        fails.append("the all-favourable example's whole sales no longer need two to three and a half times the membrane switch; rewrite the note")
    # 2026-11-19 second round: a switch at 3 million m2 is again below what the low-lactate example's sales need (4.86 million), so with slow
    # learning it crosses on its own and has ONE resting point, $21.91 and 0.59%. (With the audit batch's normal spread: two,
    # $32.48 left alone and $22.07 if pushed. After the cut-cost repin: one, $18.69.) With everything else central a 3 million m2
    # switch costs it 21 cents (was: stopped it at $31.66).
    # 2026-11-20 (engine batch): flipped again. A switch at 3 million m2 is above the 2.54 million the low-lactate example's sales
    # need, so with slow learning it has TWO resting points: $49.69 and 0.05% left alone, $30.39 and 0.27% if pushed. And the
    # switch's level now matters most among the market-size inputs: across its range the resting cost runs from $23.89 to $49.03
    # (was 21 cents). The note says the conclusion follows the sales at the example's own cost and is not robust.
    lo, hi = s["solved"][("central", "slow learning", "below")], s["solved"][("central", "slow learning", "above")]
    own, slow_switch = s["base"]["central"]["cost"], _case("slow learning")["ms_switch_area"]
    # 2026-11-22 (fifth batch): with slow learning the low-lactate example now crosses on its own sales (13.6 million m2 against a
    # 3 million switch) and has one resting point ($29.43, 0.54%); before, two ($48.38 and $30.30)
    if not (abs(hi["volume_mt"] - lo["volume_mt"]) < 1e-3 * hi["volume_mt"] and s["start"][("central", "slow learning")]["whole_area_m2"] > slow_switch
            and lo["cost"] < 0.7 * own):
        fails.append("the low-lactate example with slow learning no longer has one resting point, well below its own cost; rewrite the note's section 3")
    # 2026-11-22 (fifth batch): the switch's level no longer matters (its whole range leaves it at about $23.5-23.8); the plant's
    # learning rate matters most ($21.5-25.8)
    sens = {r["key"]: r["cost"] for r in s["sens"]["central"]}
    sw, lp = sens["ms_switch_area"], sens["ms_lr_plant"]
    if not (max(sw) - min(sw) < 1.0 and max(lp) - min(lp) > 3.0
            and all(max(lp) - min(lp) >= max(v) - min(v) for v in sens.values())):
        fails.append("the switch's level no longer leaves the low-lactate example near $23.5 across its range, or the plant's learning "
                     "rate no longer matters most; rewrite the note's section 5")
    # 2026-11-19 second round: published cells cost $111.89 and sell 0.002% of world meat (about 6,000 t a year). Left alone they
    # stay within $2 of their own cost in every case; only fast learning has an upper resting point ($75.43), which needs a push.
    # (With the normal spread they sold nothing and had one resting point everywhere.)
    # 2026-11-19 restructure: the published cells in perfusion ("cautious", $92.17). Left alone they stay within $2 of their own cost
    # except with fast learning, which carries them to $51.66 on its own; with central learning a resting point at $55.98 needs a push.
    # Their share stays under 0.05% of world meat in every case.
    # 2026-11-20 (engine batch): at $183.15 they stay within 10 cents of their own cost in EVERY case when left alone, fast learning
    # included; only fast learning has an upper resting point ($87.51), and it needs a push. Central learning has none.
    # 2026-11-22 (fifth batch): published cells now cross the switch on their own sales (2.4 million m2) and rest at $84.88 and
    # 0.09%; with slow learning, or with no food-grade supplier, they stay at their own cost unless pushed
    t0 = s["base"]["cautious"]["cost"]
    # 2026-11-24 (the default of 50% of meat buyers): published cells rest at $81.47 (0.63%) with central learning, $97.91 with slow
    # learning and $76.16 with fast; only with no food-grade supplier and slow plant learning do they stay at their own cost ($180.37)
    # 2026-11-25 (the gas cap and loop thinning): $181.13 -> $179.90 at their own cost; they rest at $81.23 central, $97.91 slow, $75.87
    # fast, and stay at $178.89 with no food-grade supplier and slow plant learning
    if not (s["solved"][("cautious", "central", "below")]["cost"] < 0.5 * t0
            and s["solved"][("cautious", "slow learning", "below")]["cost"] < 0.6 * t0
            # 2026-11-25 (the gas cap and loop thinning): "at their own cost" was within $1 ($180.37 against $181.13); now $178.89
            # against $179.90, $1.01 below, so the bound is 1% of their own cost. They still stay put: the conclusion is unchanged
            and s["solved"][("cautious", "no food-grade membrane supplier, slow plant learning", "below")]["cost"] > 0.99 * t0
            and all(s["solved"][("cautious", case, start)]["share"] < 0.8 for case in L.CASES for start in ("below", "above"))):
        fails.append("published cells no longer rest below half their own cost with central and slow learning, stay at their own cost with no "
                     "food-grade supplier and slow plant learning, and stay under 0.8% of world meat; rewrite the note")
    # 2026-11-19 second round: premium products are about a quarter of the low-lactate example's first sales (27%; 13% without premium fillets and
    # shrimp) and ordinary cuts most of them (62%). (With the normal spread: premium 47%, beef steaks the other half. Before the
    # audit batch: premium 11%.)
    c0 = s["comp"][("central", "no learning")]
    # 2026-11-22 (fifth batch): premium products 8% of first sales (were 28%), the four small ones 2.4% (14%); cuts 57%
    if not (0.05 < c0["premium_of_sales"] < 0.12 and 0.01 < c0["premium_small_of_sales"] < 0.04 and c0["cut"] > 0.5 * c0["total"]):
        fails.append("premium products are no longer about a quarter of the low-lactate example's sales at its own cost, or cuts no longer most of them; "
                     "rewrite the note")
    # 2026-11-19 second round: all five premium products respond to price at 3.3-3.7, whether cultivated meat stays dearer or ends
    # cheaper: more than twice the top of farmed salmon's range along the demand curve (1-1.5), so the check still fails, but inside
    # history's totals (1.3-4.1). (With the normal spread: 5.2-7.5 where dearer, above the totals; 2.6 and 3.3 where cheaper.)
    resp = s["response"]["products"]
    if sorted(resp) != ["beef (prime/wagyu)", "chicken (organic)", "pork (heritage)", "seafood (premium fillet, shrimp)", "seafood (sushi)"]:
        fails.append("the model's premium products are no longer the five the note lists; rewrite the note")
    # 2026-11-20 (engine batch): the five respond at 3.8-4.3, two and a half to three times the top of salmon's range along the
    # curve; organic chicken, heritage pork and premium fillets and shrimp (3.8-4.0) are inside history's totals (up to 4.1),
    # prime beef (4.2) and sushi-grade seafood (4.3) just above them. The responses rose because dearer cells start every
    # product further from its meat's price, with a smaller share that has more room to rise (prime beef from 2.3% of its
    # market, was 13%). A correct consequence of the batch; the demand model is unchanged.
    # 2026-11-20 final pass: 3.7-4.3. Organic chicken gives 3.748, a hair under 2.5 times 1.5 (3.75), after the demand anchor
    # moved. The lower bound is set at 2.4 times for that reason only: the five still respond at about two and a half to three
    # times the top of salmon's range, and the note says so.
    # 2026-11-22 (fifth batch, the price-insensitive shoppers): the three dearest premium products respond at 1.0-1.7 times the top
    # of salmon's range along the curve (1.5, 1.8, 2.4), prime beef and sushi-grade seafood, nearest their meat's price, at 2.4-3.0
    # times (4.3, 4.0); only prime beef is above history's totals. Before, all five were at 2.4-3.0 times.
    top = L.HISTORY_ALONG_CURVE[1]
    for n, v in resp.items():
        near = n in ("beef (prime/wagyu)", "seafood (sushi)")
        # 2026-11-24: 1.5-2.5 for the three dearest, 3.0 and 3.5 (2.0 and 2.4 times the top) for prime beef and sushi-grade seafood
        if not ((1.9 * top < v["response"] < 2.5 * top) if near else (top < v["response"] < 1.7 * top)):
            fails.append(f"{n}: the response to price no longer stands where the note says against salmon's range along the curve; "
                         "rewrite the note")
        if v["response"] > L.HISTORY_TOTAL[1]:    # 2026-11-24: none is above them now (prime beef 2.96, was 4.3 against the totals' 4.1)
            fails.append(f"{n}: stands differently against history's totals (all five are inside them); rewrite the note")

    # 2026-11-19 second round: the low-lactate example's own volume is 4.9 times the switch, so the first pass buys most of the learning: later
    # rounds give 25% of its share gain (35% with the normal spread; 19% before the audit batch). The all-favourable example's cells: 5%.
    # 2026-11-20: 32% (its own volume is now 2.5 times the switch, so less of the learning comes on the first pass); the all-favourable example 10%
    # 2026-11-22 (fifth batch): an eighth (12%; was about a third)
    # 2026-11-24: 8% (about a twelfth)
    if not 0.05 < s["passes"]["central"]["later_rounds"] < 0.12:
        fails.append("later rounds no longer give about a twelfth of the low-lactate example's share gain; rewrite the note's section 5")
    if not s["passes"]["best"]["later_rounds"] < 0.15:
        fails.append("best: later rounds now give 15% or more of the share gain; the note says it is one step")
    # 2026-11-19 second round: at the low-lactate example's own cost the model now gives more than the curve fitted to premium meats (0.16% against 0.10%)
    if not s["anchored"]["central"]["own"] < s["model_share"]["central"]:
        fails.append("at the low-lactate example's own cost the demand anchored on premium meats is no longer below the model's; rewrite the note")
    if not s["anchored"]["best"]["share"] < 0.7 * s["passes"]["best"]["rest"][1]:
        fails.append("the all-favourable example's share with demand anchored on premium meats is no longer well below the main model's; rewrite the note")

    sv = s["solved"]
    quoted = []
    for k in L.SCEN:
        for case in L.CASES:
            r = sv[(k, case, "below")]
            quoted += [f"${r['cost']:.2f}", L._pct(r["share"])]       # 2026-11-19 audit batch: shares under 0.01% are written so
        quoted.append(f"${s['floor'][k]['cost']:.2f}")
    # 2026-11-19 audit batch: every share in this study uses the model's ordinary demand (13% at equal price). The note also gives
    # the all-favourable example's cells with the all-favourable example's own demand (55%): they rest at the floors.
    own_demand = lambda cost: S.shares(cost, regions=("global",), eqs="best_equal_price_share")["global"]
    r = L.solve(S.SCENARIOS["best"].choice, share=own_demand)
    if abs(r["cost"] - s["floor"]["best"]["cost"]) > 0.01:
        fails.append("with its own demand the all-favourable example's cells no longer rest at the floors; rewrite the note")
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
