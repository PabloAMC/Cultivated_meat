#!/usr/bin/env python3
"""
humbird_check.py — does the engine give Humbird's own numbers when it is run at Humbird's own conditions?

Why
---
The page starts from "Humbird's best estimate (2021)": his fed-batch design with enhanced cells on soy hydrolysate, $21.00 a kilo
of wet cells in 2018 dollars (Humbird 2021, Table 4.7, second column). Before the page can start there, the engine
(floor_physics.explore) has to reproduce that figure line by line when it is given his conditions, and the gaps that remain have
to be explained. This module holds his figures as data, the engine settings that are his conditions, and the comparison.

What is compared
----------------
Five designs: the four columns of his Table 4.7 (fed-batch in 24 tanks of 20 m3: enhanced cells on amino acids, enhanced cells on
hydrolysate, wild-type cells on amino acids, wild-type cells on hydrolysate) and his perfusion design (Table 4.13: 96 tanks of
2 m3, enhanced cells on amino acids). The enhanced fed-batch on amino acids is also his Table 4.6.

His conditions, as engine settings (`conditions`)
-------------------------------------------------
* his cells: the model's reference cell is his enhanced cell (3 ng, 24 h, Reaction 2.11); `waste=1` is his wild type (2.9);
* his tanks, plant, yearly charge (14.6% + 4% + 5% = 23.6% of the plant's cost) and limits (5 mmol/L ammonia, 50 lactate,
  100 mbar CO2, 6 mm/s of gas);
* his plant cost: the total capital of that column of his table over its production tanks;
* his nutrient cost per kilo, entered as the price of a litre of medium (cost per kilo / litres per kilo);
* growth factors at his price per litre (in the wild-type columns his price is 11 times lower, because 16 times more is bought:
  his Eq. 3.4);
* his sterile filter sets, replaced at each batch;
* everything he does not count switched off: cells killed by bubbles, cells lost at harvest, the least medium flow, the bubble
  protectant, the antifoam's effect on oxygen, the growth slowdown at the end of a batch, the extra medium-preparation
  equipment, lost runs, tank tricks;
* the end of a batch as he counts it: only the waste made by the cells grown in the production tank (pf_batch_end_x note).
Each is run in 2018 dollars (both escalation inputs set to 1) and in today's dollars.

The page's start (`page_start`, since 2026-11-20; the owner: "stick to Humbird design unless he missed something important") is
the hydrolysate design like for like in today's dollars, $27.09. Four of the model's additions are levers of the page that start
at his value (none) and can be switched on together (`page_with_additions`) or one at a time (`page_additions`). `start_kwargs`
and `start` are the same design as the model itself would price it (its own plant figure and supplies, every addition on), $36.21:
the page opened there until 2026-11-20.

Run
---
    python humbird_check.py            # the comparison, as text
"""
from __future__ import annotations

import floor_physics as fp
from inputs import value

SOURCE = "Humbird 2021, 'Scale-up economics for cultured meat: techno-economic analysis and due diligence' (the full report)"

# ----------------------------------------------------------------------------
# His figures (2018 dollars per kilo of wet cells unless said). Each with its table and the page of the report.
# ----------------------------------------------------------------------------
LINES = ("nutrients", "growth_factors", "consumables", "utilities", "labour", "capital")
LINE_NAMES = {"nutrients": "Nutrients (his macronutrients)", "growth_factors": "Growth factors (his micronutrients)",
              "consumables": "Consumables", "utilities": "Utilities", "labour": "Labour",
              "capital": "Plant (capital charge, maintenance, insurance)", "total": "Total"}

HIS = {
    "fb_aa": dict(
        label="Fed-batch, enhanced cells, amino acids", reaction="2.11", table="Table 4.7, column 1 (and Table 4.6)", page=57,
        mode="fedbatch", waste=0.0, kta=6.8, tci_m=328.0, tank_m3=20.0, tanks=24, fte=95, bioreactor_m3=649,
        lines=dict(nutrients=19.08, growth_factors=3.13, consumables=0.85, utilities=0.94, labour=1.45),
        capital_parts=dict(bioreactors=3.60, buildings=3.08, rest=4.65), total=36.79,
        density=115.6, density_src="1,849 kg of wet cells in 16 m3 at the end of a batch (Sect. 4.1, p. 49; he rounds it to 120 g/L)"),
    "fb_hydro": dict(
        label="Fed-batch, enhanced cells, soy hydrolysate (his best estimate)", reaction="2.13", table="Table 4.7, column 2", page=57,
        mode="fedbatch", waste=0.0, kta=6.9, tci_m=330.0, tank_m3=20.0, tanks=24, fte=94, bioreactor_m3=644,
        lines=dict(nutrients=3.39, growth_factors=3.12, consumables=0.81, utilities=0.93, labour=1.42),
        capital_parts=dict(bioreactors=3.56, buildings=3.11, rest=4.66), total=21.00,
        density=115.6, density_src="as the amino-acid design: 1,849 kg in 16 m3 (Sect. 4.1, p. 49)"),
    "fb_wt_aa": dict(
        label="Fed-batch, wild-type cells, amino acids", reaction="2.9", table="Table 4.7, column 3", page=57,
        mode="fedbatch", waste=1.0, kta=0.41, tci_m=286.0, tank_m3=20.0, tanks=24, fte=81, bioreactor_m3=633,
        lines=dict(nutrients=18.24, growth_factors=4.60, consumables=12.56, utilities=14.52, labour=20.70),
        capital_parts=dict(bioreactors=55.09, buildings=43.37, rest=67.48), total=236.58,
        density=7.0, density_src="two doublings to 2.3 million cells per mL (Sect. 2.3, Fig. 2.7a, p. 26)"),
    "fb_wt_hydro": dict(
        label="Fed-batch, wild-type cells, soy hydrolysate", reaction="2.12", table="Table 4.7, column 4", page=57,
        mode="fedbatch", waste=1.0, kta=0.41, tci_m=288.0, tank_m3=20.0, tanks=24, fte=81, bioreactor_m3=637,
        lines=dict(nutrients=4.27, growth_factors=4.62, consumables=13.05, utilities=14.81, labour=20.86),
        capital_parts=dict(bioreactors=55.43, buildings=43.78, rest=68.22), total=225.03,
        density=7.0, density_src="as the amino-acid design (Sect. 2.3, Fig. 2.7a, p. 26)"),
    "pf_aa": dict(
        label="Perfusion in 2 m3 tanks, enhanced cells, amino acids", reaction="2.11", table="Table 4.13 (and Table 4.14, column 1)", page=64,
        mode="perfusion", waste=0.0, kta=6.9, tci_m=662.628, tank_m3=2.0, tanks=96, fte=132, bioreactor_m3=197,
        lines=dict(nutrients=18.39, growth_factors=2.78, consumables=4.56, utilities=0.98, labour=1.99),
        # Table 4.13: capital charge 13.97 + maintenance 3.84 + insurance 4.79; Table 4.14 splits the same 22.61 four ways
        capital_parts=dict(bioreactors=5.77, perfusion=5.56, buildings=4.11, rest=7.17), total=51.29,
        density=195.0, density_src="'the retained cell density rises to 195 g/L' (Sect. 4.2, p. 59)"),
}
BEST = "fb_hydro"
ORDER = ("fb_aa", "fb_hydro", "fb_wt_aa", "fb_wt_hydro", "pf_aa")
for _h in HIS.values():
    _h["lines"]["capital"] = round(sum(_h["capital_parts"].values()), 2)
    _h["output"] = _h["kta"] * 1000.0 / (_h["tanks"] * _h["tank_m3"])           # t per m3 of production tank a year
    _h["capex"] = _h["tci_m"] * 1000.0 / (_h["tanks"] * _h["tank_m3"])          # $k per m3 of production tank

# his fed-batch plant: batches a year and the litres a batch ends with (Sect. 4.1, p. 50: "3,600 batches per year"; 16 m3)
BATCHES_YR = 3600.0
BATCH_L = 16000.0
SEED_KG, BATCH_KG = 482.0, 1849.0            # the seed cells a production tank starts with and what it ends with (Fig. 4.3, p. 51)
# his perfusion design (Sect. 4.2, pp. 59-60): one tank volume a day through the filters, 9 kg of cells an hour from each tank,
# ten turnarounds a year, two ATF membranes of $16,300 a tank changed at each (Table 4.11, p. 63)
PERF_L_DAY, PERF_KG_H, PERF_TURNS = 1600.0, 9.0, 10.0
ATF_MEMBRANE, ATF_PER_TANK = 16300.0, 2.0
PERF_FILTERS_YR = 24320.0 + 60800.0 + 121600.0   # sterile and virus filter membranes a year, the whole plant (Table 4.11)
ATF_BARE_K = 38530.0                             # 192 ATF 10 units, bare (Table 4.8)

# what he does not count, as inputs of the datasheet
NOT_COUNTED = {
    "pf_harvest_recovery": 1.0,       # no cells lost at harvest
    "pf_protectant_dose": 0.0,        # no bubble protectant in the medium
    "pf_antifoam_otr": 1.0,           # no antifoam effect on oxygen transfer
    "pf_medium_prep_exp": 0.0,        # no extra medium-preparation equipment for more medium
    "pf_batch_half_x": 1e9,           # growth at full speed to the end of the batch
    "pf_consumables_low": 0.0,        # his own filter sets are entered per batch instead
}
IN_2018 = {"pf_capex_escalation": 1.0, "pf_opex_escalation": 1.0}


def his_batch_end() -> float:
    """pf_batch_end_x as Humbird counts the end of a batch: his simulation starts a tank from fresh medium and seed cells and
    counts only the waste made by the cells grown in that tank (1,849 - 482 kg of 1,849), so by the engine's count (all the
    waste a kilo made is in the litres it leaves with) his batch ends at 1 / (1 - 482/1,849) = 1.35 times the limit."""
    return 1.0 / (1.0 - SEED_KG / BATCH_KG)


def _fedbatch_vm(filters_k_m3_run: float) -> dict:
    return {"kind": "cyclic", "n_doublings": value("pf_fedbatch_doublings"), "turnaround_h": value("pf_turnaround_h"),
            "restart_days": value("vm_restart_cycle_days"), "washed": False, "cons_run": filters_k_m3_run}


def atf_capex_2018() -> float:
    """His ATF units as capital per m3 of his 2 m3 perfusion tanks, $k (2018), in his own accounting: $38,530k bare for 192 units
    (Table 4.8), times 2.5556 for minor equipment and installation, times 1.84 (plant_items): retention.atf_factor in 2018
    dollars, the same factor the retention module prices its ATF units with (since 2026-11-20; it took only rt_install = 1.84
    before), so the two cannot drift apart."""
    import retention
    return ATF_BARE_K / (HIS["pf_aa"]["tanks"] * HIS["pf_aa"]["tank_m3"]) * retention.atf_factor(escalate=False)


def conditions(case: str, dollars: str = "2018") -> tuple:
    """(explore arguments, input overrides) that are Humbird's conditions for a design, like for like, without the price of the
    medium (see `reproduce`, which sets it from his nutrient cost per kilo). dollars: "2018" or "today". The plant is the
    engine's own (2026-11-20: his plant with clean rooms, sized for his tanks and way of running by floor_physics.tank_items);
    in perfusion his ATF units are added in his own accounting (`atf_capex_2018`), in place of the engine's filter loop."""
    h = HIS[case]
    over = dict(NOT_COUNTED)
    if dollars == "2018":
        over.update(IN_2018)
    ox = 1.0 if dollars == "2018" else value("pf_opex_escalation")
    cx = 1.0 if dollars == "2018" else value("pf_capex_escalation")
    kw = dict(doubling_h=24.0, mass_pg=3000.0, vessel_m3=h["tank_m3"], waste=h["waste"], charge=value("humbird_plant_charge"),
              nh3_limit=5.0, lac_limit=50.0, pco2_mbar=100.0, gas_velocity=0.006,
              kill=0.0, min_perfusion=1e-9, hazard=0.0, plant="pharma", viscous_kla=False)
    # growth factors at his price per litre in this column (the engine's is his fed-batch's: pf_growth_factors over 8.7 L/kg)
    gf_l_engine = value("pf_growth_factors") / value("pf_medium_prep_l_kg")
    if h["mode"] == "fedbatch":
        over["pf_batch_end_x"] = his_batch_end()
        filters = h["lines"]["consumables"] * h["output"] / (BATCHES_YR / h["tanks"])       # $k per m3 of tank per batch
        kw.update(mode="filldraw", vm=_fedbatch_vm(filters * ox))
        kw["growth_factors"] = 1.0 if h["waste"] == 0.0 else h["lines"]["growth_factors"] * h["density"] / 1000.0 / gf_l_engine
    else:
        kg_day = PERF_KG_H * 24.0
        kw["medium_l"] = PERF_L_DAY / kg_day + 1000.0 / h["density"]       # through the filters, plus what leaves with the cells
        kw["growth_factors"] = 1.0
        filters = PERF_FILTERS_YR / 1000.0 / (h["tanks"] * h["tank_m3"]) / PERF_TURNS        # $k per m3 per turnaround
        atf = ATF_MEMBRANE * ATF_PER_TANK / 1000.0 / h["tank_m3"]                           # $k per m3 per turnaround
        # the engine's plant for 2 m3 tanks in perfusion, his ATF units as a flat charge in place of the engine's filter loop
        kw.update(mode="perfusion", retention=atf_capex_2018() * cx, vm={"washed": True, "cons_run": (filters + atf) * ox})
    return kw, over


def _lines(r: dict) -> dict:
    return {"nutrients": r["feedstock"], "growth_factors": r["growth_factors"],
            "consumables": float(r["consumables"]) + r["extra_opex"], "utilities": r["utilities"], "labour": r["labour"],
            "capital": r["capital"], "total": r["total"], "density": r["density"], "output": r["output"], "capex": r["capex"],
            "medium_l": r["medium_l"], "limit": r["limit"]}


def reproduce(case: str, dollars: str = "2018") -> dict:
    """The engine at Humbird's conditions for one design: its cost lines, density (g/L), output (t per m3 of tank a year) and
    plant cost ($k per m3 of tank). His nutrient cost per kilo is entered as a price per litre: cost / the litres a kilo
    leaves with (two passes: the litres first)."""
    h = HIS[case]
    kw, over = conditions(case, dollars)
    ox = 1.0 if dollars == "2018" else value("pf_opex_escalation")
    with fp._inputs_set(over):
        litres = fp.explore(medium_price=0.0, **kw)["medium_l"]
        r = fp.explore(medium_price=h["lines"]["nutrients"] * ox / litres, **kw)
    return _lines(r)


# ----------------------------------------------------------------------------
# His best estimate as the model itself would price it today, every addition on (the page's start until 2026-11-20; the page
# now starts like for like: see "The page's start" below)
# ----------------------------------------------------------------------------
START_TRAITS = {"nh3_kg": value("pf_nh3_efficient"), "lac_yield": 0.279, "doubling_h": 24.0, "mass_pg": 3000.0}
START_FINANCE = {"rate": 7.5, "life": 10.0, "upkeep": 9.0}       # his 7.5% over 10 years, 4% maintenance + 5% insurance


def start_charge() -> float:
    """His yearly charge from its three parts, as the page's finance levers compute it: 7.5% over 10 years is 14.57% (he
    rounds it to 14.6%), plus 9%."""
    i, n = START_FINANCE["rate"] / 100.0, START_FINANCE["life"]
    return i / (1.0 - (1.0 + i) ** -n) + START_FINANCE["upkeep"] / 100.0


def his_today(case: str = BEST) -> dict:
    """His own lines in today's dollars: capital by the plant-cost index, everything else by consumer prices."""
    h, cx, ox = HIS[case], value("pf_capex_escalation"), value("pf_opex_escalation")
    out = {k: v * (cx if k == "capital" else ox) for k, v in h["lines"].items()}
    out["total"] = sum(out.values())
    out.update(density=h["density"], output=h["output"], capex=h["capex"] * cx)
    return out


def start_base() -> dict:
    """The explore arguments of the start that do not depend on the way the tank is run or the class of plant (the page keeps
    those two as its own selects): his cell as the four traits, his yearly charge, his tank size, growth factors bought. The
    medium's price is added by `start_kwargs`."""
    return dict(doubling_h=START_TRAITS["doubling_h"], mass_pg=START_TRAITS["mass_pg"], nh3_kg=START_TRAITS["nh3_kg"],
                lac_yield=START_TRAITS["lac_yield"], glc_balance=True, vessel_m3=20.0, charge=start_charge(),
                growth_factors=1.0)


def start_kwargs() -> dict:
    """The page's start, "Humbird's best estimate (2021)": his fed-batch design on hydrolysate in today's dollars, as the
    engine prices it with the levers at his values and the model's own additions on (cells killed by bubbles, cells lost at
    harvest, the least medium flow the cells need, the bubble protectant, the growth slowdown at the end of a batch).

    The medium: his own nutrient cost ($3.39 a kilo of cells in 2018 dollars, $4.34 today) is more than the model's price of
    the same cells' ingredients ($2.00: feed-grade amino acids, glucose, salts), so the start keeps his. It is entered as the
    page's medium lever takes it, a price per litre: his cost per kilo over the litres a kilo of cells grown takes at the start."""
    import scenarios as sc
    kw = dict(start_base())
    kw.update(sc.setting("mode", "fedbatch").kw)
    kw.update(sc.setting("plant", "pharma").kw)
    litres = fp.explore(medium_price=0.0, **kw)
    grown_l = litres["medium_l"] * litres["harvested_share"]
    kw["medium_price"] = round(HIS[BEST]["lines"]["nutrients"] * value("pf_opex_escalation") / grown_l, 3)
    return kw


def start() -> dict:
    return fp.explore(**start_kwargs())


def additions() -> list:
    """What the model adds to his design, one at a time on top of the like-for-like reproduction in today's dollars: rows of
    (what, cost with it, change). The last row is the page's start. His nutrient cost per kilo of cells grown is kept at every
    step (the price per litre is set again from the litres)."""
    h = HIS[BEST]
    kw, over = conditions(BEST, "today")
    nutrients = h["lines"]["nutrients"] * value("pf_opex_escalation")
    rows = []

    def run(label):
        with fp._inputs_set(over):
            r0 = fp.explore(medium_price=0.0, **kw)
            t = fp.explore(medium_price=nutrients / (r0["medium_l"] * r0["harvested_share"]), **kw)["total"]
        rows.append((label, t, t - (rows[-1][1] if rows else t)))
    run("His design, like for like")
    kw["charge"] = start_charge()
    kw["vm"] = dict(kw["vm"]); kw["vm"].pop("cons_run"); over.pop("pf_consumables_low"); over.pop("pf_medium_prep_exp")
    run("The model's flat $0.30 of supplies in place of his filter sets, and his yearly charge unrounded")
    kw.pop("viscous_kla")
    run("A thick culture takes up oxygen more slowly (kLa falls with the viscosity)")
    kw.pop("min_perfusion")
    run("The least medium flow the cells need (other by-products build up): it caps the density at 92 g/L")
    over.pop("pf_batch_end_x"); over.pop("pf_batch_half_x")
    run("All the waste a kilo made counted at the end of a batch, which may end 1.3 times above the limit")
    kw.pop("kill")
    run("Cells killed by bursting bubbles")
    over.pop("pf_harvest_recovery")
    run("Cells lost at harvest (2%)")
    over.pop("pf_protectant_dose"); over.pop("pf_antifoam_otr")
    run("Bubble protectant in the medium")
    assert not over, over
    s = start()["total"]
    assert abs(s - rows[-1][1]) < 0.02 * s, (s, rows[-1][1])      # the same case: the start writes the cell as its four traits
    rows[-1] = (rows[-1][0] + ": the model's own version of his design", s, s - rows[-2][1])
    return rows


def with_additions(case: str) -> dict:
    """One of his designs in today's dollars with the model's own additions on (the least medium flow, all waste counted at the
    end of a batch, cells killed by bubbles, cells lost at harvest, the protectant, the antifoam's effect on oxygen, the extra
    medium-preparation equipment), keeping his plant cost, his yearly charge, his filter sets and his nutrient cost per kilo of
    cells grown. For his best estimate the page's start (`start`) differs a little: it takes the model's own plant figure and
    its flat supplies in place of his filter sets."""
    kw, over = conditions(case, "today")
    over = {k: v for k, v in over.items() if k == "pf_consumables_low"}
    for k in ("kill", "min_perfusion", "medium_l", "viscous_kla"):
        kw.pop(k, None)
    nutrients = HIS[case]["lines"]["nutrients"] * value("pf_opex_escalation")
    with fp._inputs_set(over):
        r0 = fp.explore(medium_price=0.0, **kw)
        r = fp.explore(medium_price=nutrients / (r0["medium_l"] * r0["harvested_share"]), **kw)
    return _lines(r)


# ----------------------------------------------------------------------------
# The page's start (2026-11-20): his best estimate like for like in today's dollars, the model's additions as levers at his value
# ----------------------------------------------------------------------------
# The five additions that are levers of the page: the lever (build_interactive.PAGE_PARAMS), what it is, and where `conditions`
# switches it off (an explore argument or an input of the datasheet). At the start each lever is at 0; the button "Add what this
# model counts and he does not" sets each to the model's own value.
PAGE_ADDITIONS = (
    ("kla_exp", "Thick cultures take up oxygen more slowly", "kw", "viscous_kla"),
    ("min_perfusion", "A least flow of medium the cells need", "kw", "min_perfusion"),
    ("killx", "Cells killed by bursting bubbles", "kw", "kill"),
    ("harvest_loss", "Cells lost at harvest", "over", "pf_harvest_recovery"),
    ("protect_dose", "A bubble protectant in the medium", "over", "pf_protectant_dose"),
)
# What `conditions` also sets to his value and the page has no lever for. They stay at his value while the tank is run his way (a
# stirred tank in fed-batch), with the additions on as well: his sterile filter sets in place of the model's flat supplies, no
# antifoam effect on oxygen, no extra medium-preparation equipment, growth at full speed to the end of the batch, and the end of a
# batch as he counts it.
PAGE_NO_LEVER = ("pf_consumables_low", "pf_antifoam_otr", "pf_medium_prep_exp", "pf_batch_half_x", "pf_batch_end_x")


def page_finance() -> dict:
    """What the page's three finance levers show at the start: 7.5% over 10 years, and the rest of his 23.6% a year (he rounds
    the payment of 14.57% to 14.6% and adds 4% maintenance and 5% insurance, so the rest is 9.03%)."""
    i, n = START_FINANCE["rate"] / 100.0, START_FINANCE["life"]
    return {"rate": START_FINANCE["rate"], "life": n, "upkeep": (value("humbird_plant_charge") - i / (1.0 - (1.0 + i) ** -n)) * 100.0}


def page_traits() -> dict:
    """His enhanced cell as the page's four traits, giving exactly the ammonia and lactate of the engine's reference cell
    (waste=0): the lactate per mol of glucose is his lactate per kilo over the glucose balance at that yield, 0.279."""
    cells = fp.Cells(mass_pg=START_TRAITS["mass_pg"], doubling_h=START_TRAITS["doubling_h"], maintenance_share=value("pf_maintenance_share"))
    nh3, lac = value("pf_nh3_efficient"), value("pf_lac_efficient")
    g0 = fp.glucose_balance(cells.o2_per_kg * 1000.0 / 32.0, nh3, 0.0)            # glucose a kilo with no lactate made
    y = lac / (g0 + lac / 2.0)                                                     # y x g0 / (1 - y/2) = lac
    assert abs(y - START_TRAITS["lac_yield"]) < 5e-4, y
    return {"nh3_kg": nh3, "lac_yield": y, "doubling_h": START_TRAITS["doubling_h"], "mass_pg": START_TRAITS["mass_pg"]}


def page_nutrients_kg() -> float:
    """His nutrient cost for a kilo of cells grown, in today's dollars: the page prices the medium at this, whatever the litres."""
    return HIS[BEST]["lines"]["nutrients"] * value("pf_opex_escalation")


def page_run(on: tuple = ()) -> dict:
    """The engine at his best estimate's conditions in today's dollars with the additions named in `on` (keys of PAGE_ADDITIONS)
    at the model's own values: explore's result. His nutrient cost per kilo of cells grown is kept (two passes: the litres first)."""
    kw, over = conditions(BEST, "today")
    for key, _name, where, arg in PAGE_ADDITIONS:
        if key in on:
            (kw if where == "kw" else over).pop(arg)
    with fp._inputs_set(over):
        r0 = fp.explore(medium_price=0.0, **kw)
        r = fp.explore(medium_price=page_nutrients_kg() / (r0["medium_l"] * r0["harvested_share"]), **kw)
    r["medium_price"] = page_nutrients_kg() / (r0["medium_l"] * r0["harvested_share"])
    return r


def page_start() -> dict:
    """The page's start: his best estimate like for like in today's dollars (`reproduce(BEST, "today")`, $27.09)."""
    return page_run(())


def page_with_additions() -> dict:
    """The page after "Add what this model counts and he does not": the five levers at the model's own values ($37.38). His
    plant cost, yearly charge, filter sets and count of the end of a batch are kept, which is why it is not `start()`."""
    return page_run(tuple(a[0] for a in PAGE_ADDITIONS))


def page_additions() -> list:
    """Rows of (lever, what it is, what it adds switched on alone at the page's start, $ a kilo)."""
    base = page_start()["total"]
    return [(key, name, page_run((key,))["total"] - base) for key, name, _w, _a in PAGE_ADDITIONS]


def page_table() -> list:
    """The page's table for his best estimate: rows of (line, his 2018, his in today's dollars, the engine like for like in
    today's dollars = the page's start, the engine with the five additions on)."""
    t, like, s = his_today(), _lines(page_start()), _lines(page_with_additions())
    rows = [(k, HIS[BEST]["lines"][k], t[k], like[k], s[k]) for k in LINES]
    rows.append(("total", HIS[BEST]["total"], t["total"], like["total"], s["total"]))
    return rows


# ----------------------------------------------------------------------------
# The comparison
# ----------------------------------------------------------------------------
# Residuals that could not be closed from his report, as (case, line): (tolerance as a share of his figure, why)
RESIDUALS = {
    ("pf_aa", "growth_factors"): (0.75, "He counts the growth factors lost in the 7 litres a kilo that pass the filters; the engine "
                                        "doses every litre that leaves, the 5 litres that go out with the cells included."),
    ("pf_aa", "utilities"): (0.60, "His plant of 2 m3 tanks has 2.9 times the clean-room floor per m3 of tank of his fed-batch "
                                   "plant, and uses 26 litres of water a kilo; the engine's utilities are his fed-batch plant's."),
    ("pf_aa", "labour"): (0.50, "His 96 small tanks take 0.69 staff per m3 of tank; the engine gives a tank in perfusion twice "
                                "his fed-batch crew (0.40 per m3), a figure for 20 m3 tanks (pf_labour_perfusion_x)."),
    ("fb_wt_aa", "labour"): (0.20, "His wild-type plant has 81 staff where the enhanced one has 95; the engine keeps the crew "
                                   "per m3 of tank."),
    ("fb_wt_hydro", "labour"): (0.20, "As the amino-acid column: 81 staff against 95."),
    # the engine's own plant (2026-11-20): his wild-type plants are smaller than his enhanced one for the same tanks (less oxygen
    # plant, utilities and medium equipment for 6% of the output); the engine's plant scales with tanks, not with output
    ("fb_wt_aa", "capital"): (0.16, "His wild-type plant costs $286M against $328M for the same 24 tanks: the oxygen plant, the "
                                    "utilities and the medium equipment are sized for 6% of the output. The engine's plant is the "
                                    "enhanced one's, scaled with tanks."),
    ("fb_wt_aa", "capex"): (0.16, "As its plant line."),
    ("fb_wt_hydro", "capital"): (0.16, "As the amino-acid column: $288M against $330M."),
    ("fb_wt_hydro", "capex"): (0.16, "As its plant line."),
    ("pf_aa", "capital"): (0.07, "The engine prices his 2 m3 plant 6% under his: its seed train, sterilisers, centrifuges and "
                                 "outside utilities stay at the fed-batch plant's cost per m3 of tank ($286k), where his 2 m3 plant "
                                 "spends $493k per m3 on them."),
    ("pf_aa", "capex"): (0.07, "As its plant line."),
}
TOTAL_TOL = {"pf_aa": 0.05, "fb_wt_aa": 0.12, "fb_wt_hydro": 0.12}   # perfusion: residuals partly cancel; wild type: the plant
LINE_TOL, LINE_ABS, TOTAL_TOL_DEFAULT = 0.05, 0.30, 0.03


def tolerance(case: str, line: str) -> float:
    if line == "total":
        return TOTAL_TOL.get(case, TOTAL_TOL_DEFAULT)
    return RESIDUALS.get((case, line), (LINE_TOL, ""))[0]


def compare(case: str) -> list:
    """Rows of (line, his 2018 figure, engine like for like in 2018 dollars, relative gap, engine in today's dollars)."""
    h, a, b = HIS[case], reproduce(case, "2018"), reproduce(case, "today")
    rows = [(k, h["lines"][k], a[k], a[k] / h["lines"][k] - 1.0, b[k]) for k in LINES]
    rows.append(("total", h["total"], a["total"], a["total"] / h["total"] - 1.0, b["total"]))
    for k in ("density", "output", "capex"):
        rows.append((k, h[k], a[k], a[k] / h[k] - 1.0, b[k]))
    return rows


def best_table() -> list:
    """The page's table for his best estimate: rows of (line, his 2018, his in today's dollars, engine like for like in
    today's dollars, engine with the model's additions = the page's start)."""
    t, like, s = his_today(), reproduce(BEST, "today"), _lines(start())
    rows = [(k, HIS[BEST]["lines"][k], t[k], like[k], s[k]) for k in LINES]
    rows.append(("total", HIS[BEST]["total"], t["total"], like["total"], s["total"]))
    return rows


_EXTRA_NAMES = {"density": "Density at harvest, g/L", "output": "Output, t per m3 of tank a year", "capex": "Plant, $k per m3 of tank"}


def markdown() -> str:
    out = []
    for case in ORDER:
        h = HIS[case]
        out.append(f"### {h['label']} ({h['table']}, p. {h['page']})\n")
        out.append("| Line | Humbird, 2018 $ | Engine at his conditions, 2018 $ | Gap | Engine, today's $ |")
        out.append("|---|---:|---:|---:|---:|")
        for k, his, eng, gap, today in compare(case):
            name = LINE_NAMES.get(k) or _EXTRA_NAMES[k]
            f = (lambda v: f"{v:,.0f}") if k == "capex" else ((lambda v: f"{v:.1f}") if k in ("density", "output") else (lambda v: f"{v:.2f}"))
            out.append(f"| {name} | {f(his)} | {f(eng)} | {gap:+.1%} | {f(today)} |")
        out.append("")
    out.append("### His best estimate against the model's own version of his design (today's dollars)\n")
    out.append("| Line | Humbird, 2018 $ | Humbird, today's $ | Engine like for like | Engine with the model's additions |")
    out.append("|---|---:|---:|---:|---:|")
    for k, his, t, like, s in best_table():
        out.append(f"| {LINE_NAMES[k]} | {his:.2f} | {t:.2f} | {like:.2f} | {s:.2f} |")
    out.append("")
    out.append("### All five designs: totals\n")
    out.append("| Design | Humbird, 2018 $ | Engine like for like, 2018 $ | Engine like for like, today's $ | Engine with the model's additions, today's $ | Density with the additions, g/L |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for case in ORDER:
        a, b, c = reproduce(case, "2018"), reproduce(case, "today"), with_additions(case)
        out.append(f"| {HIS[case]['label']} | {HIS[case]['total']:.2f} | {a['total']:.2f} | {b['total']:.2f} | {c['total']:.2f} | {c['density']:.0f} |")
    out.append("")
    out.append("### What the model adds to his best estimate, one at a time\n")
    out.append("| Step | $ a kilo | Change |")
    out.append("|---|---:|---:|")
    for label, t, d in additions():
        out.append(f"| {label} | {t:.2f} | {d:+.2f} |")
    out.append("")
    out.append("### The page's start, and what the page's five levers add (today's dollars)\n")
    out.append("| Setting | $ a kilo | Change |")
    out.append("|---|---:|---:|")
    p0 = page_start()["total"]
    out.append(f"| The page's start: his design, like for like | {p0:.2f} | |")
    for _key, name, d in page_additions():
        out.append(f"| {name}, switched on alone | {p0 + d:.2f} | {d:+.2f} |")
    pa = page_with_additions()["total"]
    out.append(f"| All five switched on (his yearly charge and filter sets kept) | {pa:.2f} | {pa - p0:+.2f} |")
    return "\n".join(out) + "\n"


def main():
    print(markdown())
    for case in ORDER:
        r = reproduce(case, "2018")
        print(f"{case}: the engine's own plant ${r['capex']:,.0f}k per m3 against his ${HIS[case]['capex']:,.0f}k ({r['capex'] / HIS[case]['capex'] - 1:+.1%})")
    s = start()
    print(f"the model's own version of his best estimate: ${s['total']:.2f} a kilo; density {s['density']:.0f} g/L ({s['limit']}); "
          f"medium ${start_kwargs()['medium_price']:.3f} a litre")
    p = page_start()
    print(f"the page's start: ${p['total']:.2f} a kilo; density {p['density']:.0f} g/L ({p['limit']}); medium ${p['medium_price']:.3f} a litre; "
          f"with the five additions on ${page_with_additions()['total']:.2f}")


if __name__ == "__main__":
    main()
