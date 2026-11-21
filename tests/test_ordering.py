#!/usr/bin/env python3
"""test_ordering.py — the model's reference points stay in the order their assumptions imply, and there is ONE most favourable case.

Why (2026-11-20). The all-favourable example ($18.7) once cost more than Humbird's design ($16.0), because it did not take the
levers on which his design is the more favourable, and a second "every lever at its limit" figure ($7.86) lived in frontier.py.
Now `scenarios.all_favourable()` is the one most favourable case. This test fails, naming the lever, if a later change lets any
reference point or any single lever undercut it.

1. One number, one call: scenarios.all_favourable(), scenarios.run(SCENARIOS["best"].choice), frontier.ladder()[-1] and the
   page's "best level known" (TP.frontier in interactive.html, when the page has been built).
2. The order of the costs:
       the nutrient floor
    <= the all-favourable case
    <= Humbird's design as this model prices it, scenarios.reference()
    <= Humbird's best estimate as this model prices it with its own additions (humbird_check.start and page_with_additions)
    <= the low-lactate example
    <= Published cells in perfusion (the `cautious` scenario).
   (The task's wording put Humbird's best estimate with the additions BELOW scenarios.reference(). It is above: the best
   estimate is his fed-batch design in a pharma-style plant at his own yearly charge with growth factors bought, about $36;
   reference() is his cells in perfusion in a food-grade plant at the mature charge with none bought, about $16.)
3. Lever by lever, the all-favourable case is at least as favourable as Humbird's design and as every preset. The direction
   that is favourable is stated per lever in DIRECTION below. A lever without a direction (the plant, the device that holds the
   cells back, the way the tank is run, the gas flow, the tank design) must be at the setting that costs least.
4. No single lever, moved back to Humbird's value or to any preset's, makes the all-favourable case cheaper.
5. Published studies (study_assumptions.py; the owner, 2026-11-20: "It should not lose to Humbird nor to any newer TEA"):
   a. lever by lever, the all-favourable case is at least as favourable as every value a study states, unless that value is
      in study_assumptions.REJECTED, and every rejected value does break the limit it names;
   b. the all-favourable cost is no higher than each study's most favourable estimate, as a kilo of wet cells in today's
      dollars, unless the study is in study_assumptions.EXCEPTIONS with the assumptions that break a limit; where the study
      publishes enough, its design in this engine with those brought inside the limits is not below the all-favourable case;
   c. no study is silently missing: every entry of STUDIES is compared or listed in NOT_COMPARED with the reason;
   d. no published tank size makes the case cheaper with its tank design chosen again.

Run directly or under pytest.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import floor_physics as fp
import frontier as F
import humbird_check as HC
import retention as R
import scenarios as S
import study_assumptions as SA
from inputs import AA_FLOOR, GLUCOSE_OTHER_FLOOR, value

# The favourable direction of each lever with one: +1 = higher is favourable, -1 = lower is. Keys are explore() arguments.
DIRECTION = {
    "nh3_kg": -1,             # ammonia the cells make, mol a kilo: less waste to wash out
    "lac_yield": -1,          # lactate per mol of glucose: less waste, less glucose
    "mass_pg": +1,            # weight of a cell: a bigger cell uses less oxygen per gram
    "doubling_h": -1,         # doubling time: faster cells make more per m3 of tank
    "nh3_limit": +1,          # ammonia the cells tolerate, mmol/L: fewer litres of medium
    "lac_limit": +1,          # lactate the cells tolerate, mmol/L
    "hazard": -1,             # runs lost a day
    "restart_fail_days": -1,  # days a lost tank is out of use
    "growth_factors": -1,     # growth factors bought, as a share of Humbird's price (those inside a complete medium included)
    "medium_price": -1,       # $ a litre
    "do_mmol": -1,            # dissolved oxygen held, mmol/L: a lower level passes more oxygen
    "min_perfusion": -1,      # least medium flow the cells need
    "x_visc": +1,             # thickest culture the tank can stir, g/L
}


def _defaults() -> dict:
    """What explore() takes for a directional lever a case does not set (Humbird's design: scenarios.reference())."""
    from gas_exchange import headspace_pressure
    return {"nh3_kg": S.HUMBIRD_TRAITS["nh3_kg"], "lac_yield": S.HUMBIRD_TRAITS["lac_yield"], "mass_pg": 3000.0, "doubling_h": 24.0,
            "nh3_limit": value("pf_nh3_limit"), "lac_limit": value("pf_lac_limit"), "hazard": 0.0,
            "restart_fail_days": 0.0,          # no loss, so no restart after one
            "growth_factors": 0.0, "medium_price": 0.15, "do_mmol": headspace_pressure()["c_liquid"],
            "min_perfusion": value("pf_min_perfusion"), "x_visc": value("pf_x_visc")}


def _levers(kw: dict) -> dict:
    """A case's value of every directional lever, from its explore() arguments."""
    d = _defaults()
    out = {k: (kw[k] if kw.get(k) is not None else d[k]) for k in DIRECTION}
    out["growth_factors"] = kw.get("growth_factors", 0.0) + kw.get("gf_in_medium", 0.0)
    if kw.get("hazard", 0.0) <= 0:
        out["restart_fail_days"] = 0.0
    return out


def check() -> list:
    fails = []
    a = S.all_favourable()
    kw, cost = a["kw"], a["cost"]

    # --- 1. one number, one call ---------------------------------------------------------------------------------------
    same = {"scenarios.run(SCENARIOS['best'].choice)": S.run(S.SCENARIOS["best"].choice)["total"],
            "frontier.ladder()[-1]['cost']": F.ladder()[-1]["cost"],
            "explore(**all_favourable()['kw'])": fp.explore(**kw)["total"]}
    for name, v in same.items():
        if v != cost:
            fails.append(f"one case: {name} = {v!r} is not scenarios.all_favourable()['cost'] = {cost!r}")
    if F.ladder()[-1]["kw"] != kw or S.explore_kwargs(S.SCENARIOS["best"].choice) != kw:
        fails.append("one case: the ladder's last row, the `best` scenario and all_favourable() do not share their explore() arguments")
    page = os.path.join(ROOT, "interactive.html")
    if os.path.exists(page):
        html = open(page, encoding="utf-8").read()
        m = re.search(r'"frontier":\s*([0-9.eE+-]+)', html)
        b = re.search(r'"best_cost":\s*([0-9.eE+-]+)', html)
        if not m or abs(float(m.group(1)) - cost) > 1e-9:
            fails.append(f"one case: the page's 'best level known' (TP.frontier = {m.group(1) if m else 'missing'}) is not {cost!r}; rebuild the page")
        if not b or abs(float(b.group(1)) - cost) > 1e-9:
            fails.append(f"one case: the page's SC.best_cost ({b.group(1) if b else 'missing'}) is not {cost!r}; rebuild the page")
    # the dialyser as explore() arguments is retention.py's own dialyser
    if a["device"] == "dialyser":
        bare = {k: v for k, v in kw.items() if k not in ("flux", "membrane_life", "membrane_price", "membrane_hw")}
        via = R.scenario_cost("dialyser", bare)["total"]
        if abs(via - cost) > 1e-9 * cost:
            fails.append(f"device: the all-favourable case's dialyser (${cost:.6f}) is not retention.scenario_cost('dialyser') (${via:.6f})")

    # --- 2. the order of the costs --------------------------------------------------------------------------------------
    chain = [("the nutrient floor", AA_FLOOR + GLUCOSE_OTHER_FLOOR),
             ("the all-favourable case", cost),
             ("Humbird's design, scenarios.reference()", S.reference()["total"]),
             ("Humbird's best estimate with the model's additions (humbird_check.start)", HC.start()["total"]),
             ("Humbird's best estimate with the model's additions, his plant cost kept (humbird_check.page_with_additions)",
              HC.page_with_additions()["total"]),
             ("the low-lactate example", S.run(S.SCENARIOS["central"].choice)["total"]),
             ("Published cells in perfusion (cautious)", S.run(S.SCENARIOS["cautious"].choice)["total"])]
    for (n1, c1), (n2, c2) in zip(chain, chain[1:]):
        if not c1 <= c2 + 1e-9:
            fails.append(f"order: {n1} (${c1:.2f}) costs more than {n2} (${c2:.2f})")
    for key, sc in S.SCENARIOS.items():                      # and no preset undercuts it
        c = S.run(sc.choice)["total"]
        if c < cost - 1e-9:
            fails.append(f"order: the scenario '{key}' (${c:.2f}) costs less than the all-favourable case (${cost:.2f})")

    # --- 3. lever by lever: at least as favourable as Humbird's design and every preset ------------------------------------
    mine = _levers(kw)
    others = {"Humbird's design (scenarios.reference())": {},
              "Humbird's best estimate (humbird_check.start_kwargs)": HC.start_kwargs()}
    others.update({f"the scenario '{k}'": S.explore_kwargs(sc.choice) for k, sc in S.SCENARIOS.items() if k != "best"})
    for who, okw in others.items():
        theirs = _levers(okw)
        for lever, sign in DIRECTION.items():
            if who.startswith("Humbird's best estimate") and lever in ("medium_price", "do_mmol"):
                continue        # his nutrients are priced per kilo, turned into a price a litre; no setpoint in his kwargs (default)
            if sign * (mine[lever] - theirs[lever]) < -1e-12:
                fails.append(f"lever {lever}: the all-favourable case has {mine[lever]:g}, {who} has {theirs[lever]:g}, and "
                             f"{'higher' if sign > 0 else 'lower'} is favourable")
    # the table's own claim: each directional lever is the best of its sources
    for r in a["levers"]:
        if r["better"] == "cost":
            continue
        vals = [v for v, _w in r["sources"].values() if v is not None]
        best = max(vals) if r["better"] == "higher" else min(vals)
        if r["args"] == ("recovery",):         # held at the model's own: explore()'s default charge is this payment plus 9%
            if r["value"] != best or "charge" in kw or abs(best + 0.09 - value("plant_charge_mature")) > 5e-4:
                fails.append(f"lever {r['lever']}: the case should keep the model's own charge, the most favourable payment ({best:.4f}) plus 9%")
            continue
        if r["value"] != best or kw.get(r["args"][0]) != best:
            fails.append(f"lever {r['lever']}: the case takes {kw.get(r['args'][0])!r}, the most favourable of its sources is {best!r}")

    # --- 4. no single lever moved back makes it cheaper ------------------------------------------------------------------------
    d = _defaults()
    for lever in DIRECTION:
        for who, okw in others.items():
            v = okw.get(lever, None)
            if lever == "growth_factors":
                v = okw.get("growth_factors", 0.0)
            if v is None or v == kw.get(lever):
                continue
            c = fp.explore(**{**kw, lever: v})["total"]
            if c < cost - 1e-9:
                fails.append(f"lever {lever}: at {who}'s value ({v:g}) the all-favourable case costs ${c:.4f}, less than ${cost:.4f}")
    ch = a["choice"]
    for sw in ("plant", "mode", "gas", "losses", "restart", "gf", "medium", "cells", "growth"):       # every other setting of a switch
        for st in S.SW[sw].settings:
            if st.key == ch[sw]:
                continue
            c2 = {**ch, sw: st.key}
            if sw in ("plant", "mode", "gas"):               # a design choice: the tank design is chosen again for it
                c2 = S.design({k: v for k, v in c2.items() if k not in ("tricks", "shape")})
            c = S.run(c2)["total"]
            if c < cost - 1e-9:
                fails.append(f"lever {S.SW[sw].name}: at '{st.label}' the all-favourable case costs ${c:.4f}, less than ${cost:.4f}")
    for tk in S.SW["tricks"].settings:                       # the tank design: no pair that passes the loop's checks is cheaper
        for sh in S.SW["shape"].settings:
            r = S.run({**ch, "tricks": tk.key, "shape": sh.key})
            col = r["column"]
            ok = col is None or (col["ph_vs_safe"] <= 1.0 + 1e-9 and col["passes_tested"])
            if ok and r["total"] < cost - 1e-9:
                fails.append(f"lever tank design: '{tk.key}' with '{sh.key}' costs ${r['total']:.4f}, less than ${cost:.4f}")
    if a["device"] == "dialyser":                            # the device: the engine's own filter loop is not cheaper
        c = fp.explore(**{k: v for k, v in kw.items() if k not in ("flux", "membrane_life", "membrane_price", "membrane_hw")})["total"]
        if c < cost - 1e-9:
            fails.append(f"lever device: the engine's own filter loop costs ${c:.4f}, less than the dialyser's ${cost:.4f}")
    fails += check_studies(a)
    return fails


def check_studies(a: dict) -> list:
    """5. The all-favourable case against every published study (study_assumptions.py)."""
    fails = []
    kw, cost = a["kw"], a["cost"]
    rows = {r["args"][0]: r for r in a["levers"]}
    names = {k: s["name"] for k, s in SA.STUDIES.items()}
    # what the case has on each lever the studies state: the rows' values, and what a kilo of its cells is fed
    mine = {k: r["value"] for k, r in rows.items() if r["better"] != "cost"}
    mine["medium_kg"] = AA_FLOOR + GLUCOSE_OTHER_FLOOR
    mine["glucose_g"] = a["result"]["glucose_kg"] * 1000.0 if "glucose_kg" in a["result"] else value("glucose_intensity") * 1000.0
    better = {k: r["better"] for k, r in rows.items()}
    better.update(SA.EXTRA_DIRECTION)
    # --- a. lever by lever
    for lever, by_study in SA.STUDY_LEVERS.items():
        if lever not in better:
            fails.append(f"studies: the lever {lever} is not a row of favourable_levers() nor in EXTRA_DIRECTION")
            continue
        if better[lever] == "cost":
            continue
        sign = 1.0 if better[lever] == "higher" else -1.0
        for study, vals in by_study.items():
            if study not in SA.STUDIES:
                fails.append(f"studies: {study} is not in STUDIES")
            for v, where in vals:
                if not str(where).strip() or not any(w in where for w in ("PDF page", "Table", "Section", "Figure")):
                    fails.append(f"studies: {study} {lever} = {v:g} has no page or table reference")
                if sign * (v - mine[lever]) > 1e-9 and not SA.is_rejected(lever, study, v):
                    fails.append(f"studies: on {lever}, {names.get(study, study)} has {v:g} ({where}), more favourable than the all-favourable "
                                 f"case's {mine[lever]:g}, and it is not in REJECTED")
    for r in SA.rejected():
        lever, sign = r["lever"], (1.0 if better.get(r["lever"]) == "higher" else -1.0)
        if not any(abs(v - r["value"]) < 1e-9 for v, _w in SA.STUDY_LEVERS.get(lever, {}).get(r["study"], [])):
            fails.append(f"rejected: {r['study']} {lever} = {r['value']:g} is not a value recorded in STUDY_LEVERS")
        if not sign * (r["value"] - r["limit_value"]) > 0:
            fails.append(f"rejected: {r['study_name']}'s {lever} = {r['value']:g} does not break the limit it names ({r['limit_value']:g} {r['unit']})")
        for f in ("assumption", "ref", "why", "limit_name", "limit_source"):
            if not str(r.get(f, "")).strip():
                fails.append(f"rejected: {r['study']} {lever} has no {f}")
        if lever in rows and rows[lever]["sources"].get(r["study"], (None,))[0] == r["value"]:
            fails.append(f"rejected: {r['study']} {lever} = {r['value']:g} is still a source of the all-favourable case")
    # the limits the rejections name are the model's own numbers
    L = SA.limits()
    if L["thickness"][1] != value("pf_x_visc") or L["growth"][1] != value("cr_td_engineering") or \
            abs(L["nutrients_cost"][1] - (AA_FLOOR + GLUCOSE_OTHER_FLOOR)) > 1e-12:
        fails.append("limits: study_assumptions.limits() no longer reads the model's own inputs")
    if kw["doubling_h"] < L["growth"][1]:
        fails.append(f"limits: the all-favourable case doubles in {kw['doubling_h']:g} h, faster than the fastest measured ({L['growth'][1]:g} h)")
    # --- b. the cost against each study's most favourable estimate, and c. nobody missing
    c = SA.comparison()
    if abs(c["all_favourable"] - cost) > 1e-12:
        fails.append("studies: comparison() does not use scenarios.all_favourable()")
    if {r["key"] for r in c["rows"]} != set(SA.STUDIES):
        fails.append("studies: comparison() does not list every study")
    for r in c["rows"]:
        if r["today"] is None:
            if not (r["key"] in SA.NOT_COMPARED and SA.NOT_COMPARED[r["key"]].strip()):
                fails.append(f"studies: {r['name']} is not compared and NOT_COMPARED gives no reason")
            continue
        if r["key"] in SA.NOT_COMPARED:
            fails.append(f"studies: {r['name']} has an estimate and is also listed as not compared")
        if not (r["published"] and r["ref"] and r["how"] and r["year_how"] and r["year"] in SA.CPI):
            fails.append(f"studies: {r['name']}'s estimate lacks its figure, page, basis or the year of its dollars")
        if r["today"] < cost - 1e-9 and r["key"] not in SA.EXCEPTIONS:
            fails.append(f"studies: {r['name']}'s most favourable estimate (${r['today']:.2f} a kilo of wet cells in today's dollars) is below "
                         f"the all-favourable case (${cost:.2f}) and the study is not in EXCEPTIONS")
    for k, ex in SA.EXCEPTIONS.items():
        b = next((x for x in c["below"] if x["key"] == k), None)
        if b is None:
            fails.append(f"exceptions: {names[k]} is listed but its estimate is not below the all-favourable case")
            continue
        if len(b["assumptions"]) != len(ex["levers"]) or not b["assumptions"]:
            fails.append(f"exceptions: {names[k]} names assumptions that are not in REJECTED")
        if ex.get("inside") and not b["inside"] >= cost - 1e-9:
            fails.append(f"exceptions: {names[k]}'s design with its assumptions inside the limits costs ${b['inside']:.2f} in this engine, "
                         f"below the all-favourable case (${cost:.2f})")
    # Humbird's own estimate in today's dollars by the same rule as every study (BLS CPI-U since his 2018 dollars; 2026-11-20)
    hb = next(r for r in c["rows"] if r["key"] == "humbird2021")
    if abs(hb["today"] - HC.HIS[HC.BEST]["total"] * SA.cpi(2018)) > 1e-12 or abs(SA.cost({}) - HC.page_start()["total"]) > 1e-9:
        fails.append("studies: Humbird's estimate, or the base of the modifications, is not humbird_check's")
    # --- d. no published tank size is cheaper, the tank design chosen again
    ex0 = S.EXTRAS[S.ALL_FAVOURABLE]
    ch = {k: v for k, v in a["choice"].items() if k not in ("tricks", "shape")}
    try:
        for size in S.FAV_TANK_M3:
            S.EXTRAS[S.ALL_FAVOURABLE] = {"always": {**{k: v for k, v in ex0["always"].items() if k != "vessel_m3"}, "vessel_m3": size},
                                          "when": ex0["when"]}
            t = S.run(S.design(ch))["total"]
            if t < cost - 1e-9:
                fails.append(f"lever tank size: at {size:g} m³ the all-favourable case costs ${t:.4f}, less than ${cost:.4f}")
    finally:
        S.EXTRAS[S.ALL_FAVOURABLE] = ex0
    sizes = {v for by in SA.STUDY_LEVERS["vessel_m3"].values() for v, _w in by}
    if not sizes <= set(S.FAV_TANK_M3):
        fails.append(f"lever tank size: the studies' sizes {sorted(sizes - set(S.FAV_TANK_M3))} are not searched (scenarios.FAV_TANK_M3)")
    return fails


def test_ordering():
    assert not check()



def check_charge_parts() -> list:
    """The model's yearly charge on the plant (plant_charge_mature) is the most favourable repayment the all-favourable case takes
    plus 9% maintenance and insurance (Humbird). Moved here from an assert in scenarios.all_favourable (2026-11-20), which fired
    whenever a study perturbed plant_charge_mature on purpose."""
    import scenarios as S
    from inputs import value
    S.all_favourable()
    rows = {r["args"][0]: r for r in S.favourable_levers() if r.get("args")}
    rec = rows.get("recovery", {}).get("value")
    if rec is None:
        return []
    return [] if abs(rec + 0.09 - value("plant_charge_mature")) < 5e-4 else [
        f"the model's yearly charge {value('plant_charge_mature'):.4f} is no longer the most favourable repayment {rec:.4f} plus 9%"]

if __name__ == "__main__":
    fails = check() + check_charge_parts()
    for f in fails:
        print("FAIL:", f)
    a = S.all_favourable()
    print(f"PASS — one all-favourable case (${a['cost']:.2f}), below Humbird's design (${S.reference()['total']:.2f}), every lever "
          f"at least as favourable as his, as every preset's and as every published study's that respects the model's limits "
          f"({len(SA.REJECTED)} study values rejected, {len(SA.EXCEPTIONS)} study below it)." if not fails else f"{len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
