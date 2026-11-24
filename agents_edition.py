#!/usr/bin/env python3
"""
agents_edition.py — the model written for AI agents: AGENTS.md, llms.txt and inputs.json, generated from the live model.

Why
---
The page (interactive.html) is written for people. An agent that wants to understand this model, check it or extend it needs
something else: plain text it can read whole, the labels and assumptions before the results, every input with its source, the
checks and which of them miss, what was tried and withdrawn, and the functions of the causal chain with real inputs and outputs.
Every number in the three files is computed here, from the model, when this script runs, so the files cannot drift from the
code: tests/test_agents_edition.py fails when a committed file differs from a fresh run.

What it writes
--------------
AGENTS.md    at the repository root: the whole edition, in seven sections ("tell, then show").
llms.txt     beside interactive.html (served by GitHub Pages): a short index in the llms.txt form (llmstxt.org) with the answer in
             ten lines and links to the rest.
inputs.json  every input of inputs.py's REGISTRY: value, unit, range, source, note, evidence class, and how much it moves the
             cost and the share where answer_rests_on.py finds that it does.

Run
---
    python agents_edition.py            # write the three files
    python agents_edition.py --check    # exit 1, naming the files, if a committed file differs from a fresh run

    python agents_edition.py --scan     # first run answer_rests_on.py's scan again and store it (agents_edition_scan.json)

The inputs that move the answer come from answer_rests_on.py's scan (every ranged input moved to each end of its range), which
takes about 28 minutes in one process. It is stored in agents_edition_scan.json, with a fingerprint of the inputs and the two
examples' costs; the test fails when they no longer match the model, and `--scan` runs it again, split over the machine's cores.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

AGENTS_MD = os.path.join(ROOT, "AGENTS.md")
LLMS_TXT = os.path.join(ROOT, "llms.txt")
INPUTS_JSON = os.path.join(ROOT, "inputs.json")
PAGE_URL = "https://pabloamc.github.io/Cultivated_meat/"
REPO_URL = "https://github.com/PabloAMC/Cultivated_meat"
RAW_URL = "https://raw.githubusercontent.com/PabloAMC/Cultivated_meat/main/"


# ----------------------------------------------------------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------------------------------------------------------
def money(x: float, nd: int = 2) -> str:
    return f"${x:,.{nd}f}"


def pct(x: float) -> str:
    """A share in percent: one decimal from 10%, two significant figures below (0.26%, 0.0010%)."""
    if abs(x) >= 10:
        return f"{x:.1f}%"
    if x == 0:
        return "0%"
    import math
    nd = max(0, 1 - int(math.floor(math.log10(abs(x)))))
    return f"{x:.{nd}f}%"


def cell(s) -> str:
    """Text safe inside a markdown table cell."""
    return str(s).replace("|", "/").replace("\n", " ").strip()


def num(x) -> str:
    if isinstance(x, (int, float)):
        return f"{x:g}"
    return str(x)


class Repl:
    """Runs lines as Python's interactive prompt does and records them with their output: an expression's value is printed
    with repr, a statement prints nothing. One namespace for a whole example, so later lines see earlier names."""

    def __init__(self):
        self.ns: dict = {}

    def run(self, lines: list) -> str:
        out = []
        for src in lines:
            out.append(">>> " + src)
            try:
                code = compile(src, "<agents_edition>", "eval")
            except SyntaxError:
                exec(compile(src, "<agents_edition>", "exec"), self.ns)
                continue
            val = eval(code, self.ns)
            if val is not None:
                out.append(repr(val))
        return "```python\n" + "\n".join(out) + "\n```"


# ----------------------------------------------------------------------------------------------------------------------------
# Evidence class of an input, read mechanically from its source tag
# ----------------------------------------------------------------------------------------------------------------------------
EVIDENCE_CLASSES = (
    ("setting", "a setting of the model or a design choice, not an estimate"),
    ("judgement", "a judgement or assumption of the model, not measured"),
    ("fitted", "fitted to data: the model solves it so that it reproduces an observed figure"),
    ("derived", "derived by arithmetic from published figures"),
    ("company", "a company's or a vendor's figure, not peer reviewed"),
    ("published_partly", "a published figure, read only in part (a snippet, an abstract or a second-hand citation)"),
    ("published", "a published or observed figure (a paper, a report read in full, a market price, official statistics)"),
    ("untagged", "no source tag"),
)
_KEYS = {
    "setting": ("design choice", "model choice", "setting", "position"),
    "judgement": ("assumed", "judgement", "typical", "scenario", "behavioural", "dial", "premise", "from memory", "assumption"),
    "fitted": ("calibration", "solved", "fitted", "fit,"),
    "derived": ("derived", "converted", "restated"),
    "company": ("supermeat", "believer", "gfi", "vendor", "brochure", "data sheet", "datasheet", "product page", "nectar",
                "application note", "launch", "isccm", "industry"),
    "published_partly": ("snippet", "abstract", "secondary", "second-hand", "search result", "via ", "read part", "read in part",
                         "not read"),
}


def evidence_class(inp) -> str:
    """The first class whose keywords appear in the input's source tag (the text in its first square brackets). This is a
    mechanical reading of the tag, not a review of the evidence: answer_rests_on.EVIDENCE describes the inputs that matter."""
    m = re.match(r"\s*\[([^\]]+)\]", inp.source or "")
    if not m:
        return "untagged"
    tag = m.group(1).lower()
    for cls, words in _KEYS.items():
        if any(w in tag for w in words):
            return cls
    return "published"


# ----------------------------------------------------------------------------------------------------------------------------
# What a measurement would settle, for the inputs the answer rests on (answer_rests_on.py). An input that enters those tables
# without an entry here is listed with "no measurement named yet"; add one.
# ----------------------------------------------------------------------------------------------------------------------------
SETTLE = {
    "equal_price_share": "a repeated-purchase study (a market test or a panel) of a cultivated product sold at the price of the meat "
                         "it copies, after the first purchase: the share of meat buyers who keep choosing it",
    "best_equal_price_share": "the same repeated-purchase study, read for the best product it offers",
    "cult_sub_mult": "a price-variation test of cultivated meat on sale (a discount or a premium at random stores or weeks): its own "
                     "price elasticity against that of the meat it copies",
    "eps_own": "already measured (scanner meta-analyses); a test on cultivated meat itself would replace it",
    "liking_sd": "a random-parameter choice experiment on cultivated meat with real purchases, which estimates the spread of "
                 "willingness to pay across shoppers",
    "liking_tail": "the same experiment with enough respondents to see the top 5% of willingness to pay",
    "price_insensitive_share": "a latent-class analysis of purchase data (not stated choices) for a premium or novel meat",
    "price_insensitive_response": "the same latent-class analysis: the ratio of the two classes' price coefficients",
    "price_insensitive_liking": "the same analysis: the two classes' liking for cultivated meat, in utils",
    "markup_add": "the cost from harvested cells to the shelf (forming, packing, cold chain) reported by a producer selling at volume",
    "retail_margin": "retailers' gross margin on a cultivated product once it is stocked at volume",
    "premium_resistance": "a choice experiment or a sales test of cultivated premium products (wagyu, sushi-grade fish) against the "
                          "conventional premium product",
    "scaffold_frac": "the cell share of cuts that reach the texture of meat in a blind sensory test",
    "process_cost": "the cost of assembling a cut at a pilot line, per kilo",
    "sc_nh3_limit": "growth rate of meat cells at 2, 4, 8 and 16 mmol/L of ammonia, at production density in perfusion",
    "pf_nh3_limit": "as sc_nh3_limit: growth of meat cells against ammonia at density",
    "sc_lac_limit": "growth rate of meat cells at 20, 40 and 80 mmol/L of lactate, at density",
    "pf_lac_limit": "as sc_lac_limit",
    "sc_nh3_selected": "ammonia made per kilo of meat cells grown, measured in perfusion at density on a glutamine-free feed",
    "sc_lac_selected": "mol of lactate made per mol of glucose by meat cells at density, in perfusion",
    "sc_nh3_engineered": "ammonia made per kilo by the lowest-waste meat cells published, at density",
    "sc_lac_engineered": "lactate per glucose made by the lowest-waste meat cells published, at density",
    "sc_mass_selected_pg": "dry and wet mass per cell of meat cells at harvest (a cell count against a weighed, drained pellet)",
    "ge_kill_protected": "the share of meat cells killed per litre of gas sparged, with the bubble protectant, in a stirred tank",
    "pf_harvest_recovery": "the kilos of cells recovered after harvest and dewatering, against the kilos grown, at pilot scale",
    "pf_labour_perfusion_x": "staff per tank in a perfusion plant against a fed-batch plant of the same output",
    "pf_medium_prep_exp": "quotes for medium-preparation equipment at two or more flows",
    "tc_kla_exp": "oxygen transfer (kLa) measured in a meat-cell culture at 50, 100 and 200 g/L in a stirred tank",
    "tc_thin": "the viscosity of a dense meat-cell culture at the shear rates of a large tank",
    "pf_otr_cap": "oxygen transfer rate held in a 10 m³ or larger animal-cell tank at the gas flow the cells tolerate",
    "ge_col_pout": "the CO₂ level a stripping column on a cell-culture loop reaches at its design flow",
    "sc_do_setpoint": "the growth rate of meat cells against dissolved oxygen, at density",
    "pi_vessel_food_k": "an installed quote for a food-grade 20 m³ tank with its controls",
    "sc_p_top": "a culture of meat cells run at 1 bar or more of top pressure: growth and CO₂ removal",
    "rt_membrane_life": "the litres a square metre of cell filter passes before it is replaced, in a long meat-cell perfusion run",
    "rt_membrane_price": "a volume quote for hollow-fibre membrane, per m²",
    "pf_protectant_price": "a bulk (tonne) quote for food-grade poloxamer 188",
    "pf_protectant_dose": "the least dose of protectant that keeps meat cells alive under sparging",
    "pf_min_perfusion": "the least medium flow per cell at which meat cells keep growing when ammonia and lactate are removed",
    "plant_charge_mature": "the financing terms (rate and years) lenders give a food-grade cell-culture plant",
    "pf_antifoam_otr": "oxygen transfer with and without the antifoam the process needs, in the same tank",
    "pf_gas_velocity": "the gas flow (superficial velocity) a meat-cell culture tolerates with the protectant",
    "pf_maintenance_share": "oxygen uptake of meat cells growing and not growing, at the same density",
    "pf_glc_kg": "glucose taken up per kilo of meat cells grown, at density",
    "aa_intensity": "the amino acids taken up per kilo of meat cells grown, from a mass balance on the medium",
    "aa_bulk_price": "food-grade bulk quotes for the amino acids of a defined medium, at tonne scale",
    "pf_capex_escalation": "the construction cost index for the year the plant is priced",
    "pf_x_unperfused": "the density a meat-cell fed-batch reaches at production scale",
    "pf_osm_limit": "the growth of meat cells against osmolality (salt strength), at density",
    "neophobia_x": "the share of first-time buyers who buy again, months after launch",
    "health_x": "a choice experiment that varies health information on cultivated meat",
    "income_gradient": "price elasticities of meat by income group (already measured for conventional meat)",
    "loss_aversion": "a test of whether shoppers respond more to a price above meat's than to one below it",
    "p_conv": "observed; not open",
    "w_ratio": "a choice experiment that varies the absolute price and the price relative to meat separately",
    "theta_free_M": "a choice experiment that states the no-slaughter attribute and measures its value to mainstream buyers",
    "accept_x": "a blind sensory test of cultivated meat against the meat it copies",
}


# ----------------------------------------------------------------------------------------------------------------------------
# Dead ends and corrections, dated: assumptions tried and withdrawn, and why. History, not model output, so it is data here; the
# test checks that every file named exists. Order: oldest first.
# ----------------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------------
# The numbers
# ----------------------------------------------------------------------------------------------------------------------------
_N: dict = {}


def headline() -> dict:
    """Every headline figure, computed once."""
    if _N:
        return _N
    import floor_physics as fp
    import humbird_check as HC
    import price_ratio as PR
    import scenarios as S
    from inputs import value, REGISTRY

    def case(key):
        c = S.run(S.SCENARIOS[key].choice)["total"]
        eqs = S.eqs_of(key)
        return {"cost": c, "share": S.shares(c, regions=("global",), eqs=eqs)["global"],
                "share_ordinary": S.shares(c, regions=("global",))["global"]}

    his = HC.HIS[HC.BEST]
    af = S.all_favourable()
    eqs = REGISTRY["equal_price_share"]
    _N.update(
        his_2018=his["total"], his_label=his["label"],
        page_start=HC.page_start()["total"], page_add=HC.page_with_additions()["total"],
        optimistic=fp.explore()["total"],
        published=case("today"), low_lactate=case("central"), all_fav=case("best"),
        af_kw=af["kw"], af_density=af["result"]["density"],
        floor=fp.feedstock(fp.GOOD_CELLS),
        parity=PR.parity_cost(value("markup_add"), value("p_conv"), value("retail_margin")),
        p_conv=value("p_conv"),
        eqs_all=eqs.value, eqs_lo=eqs.lo, eqs_hi=eqs.hi,
        buyers=S.meat_buyers_at_equal_price(),
        buyers_best=S.meat_buyers_at_equal_price(value("best_equal_price_share")),
        cost_1=S.cost_for_share(1.0), cost_10=S.cost_for_share(10.0),
    )
    return _N


# ----------------------------------------------------------------------------------------------------------------------------
# Section 1: the question and the answer in ten lines
# ----------------------------------------------------------------------------------------------------------------------------
def ten_lines() -> list:
    n = headline()
    pub, low, af = n["published"], n["low_lactate"], n["all_fav"]
    k = n["af_kw"]
    return [
        "Units: every cost is US dollars of 2025 per kilo of wet cells (about 70% water) leaving the tank, at most likely values; "
        "every share is cultivated meat's long-run share of world meat and seafood sold, by weight.",
        f"Humbird's best estimate (2021), his fed-batch design with enhanced cells on soy hydrolysate in 20 m³ tanks: "
        f"{money(n['his_2018'])} a kilo in 2018 dollars; this model's engine "
        f"at his conditions gives {money(n['page_start'])} in 2025 dollars, and {money(n['page_add'])} with what this model counts "
        "and he does not (cells killed by bubbles, cells lost at harvest, a least medium flow, the bubble protectant, slower oxygen "
        "uptake in a thick culture). From `humbird_check.page_start()` and `page_with_additions()`.",
        f"Humbird's optimistic design (his enhanced cells in a 20 m³ perfusion tank): {money(n['optimistic'])}. "
        "From `floor_physics.explore()` with no arguments.",
        f"Published cells (the best value of each trait in the published record, grown in 20 m³ batches): "
        f"{money(pub['cost'], 1)}, and a share of {pct(pub['share'])}. From `scenarios.SCENARIOS['today']`.",
        f"The low-lactate example (0.14 mol of ammonia a kilo, 0.42 mol of lactate per mol of glucose, a doubling every 36 hours, "
        f"2 ng a cell, perfusion in a 20 m³ tank): {money(low['cost'])}, and a share of {pct(low['share'])}. From "
        "`scenarios.SCENARIOS['central']`.",
        f"The all-favourable example (every lever at its most favourable value among this model's favourable end, Humbird's "
        f"design and the published cost studies, inside the model's limits; cells of {k['mass_pg'] / 1000:g} ng doubling every "
        f"{k['doubling_h']:g} hours): {money(af['cost'])}, and a share of {pct(af['share'])} if {n['buyers_best'] * 100:.1f}% of "
        f"meat buyers pick it at equal price, {pct(af['share_ordinary'])} at the model's ordinary {n['buyers'] * 100:.1f}%. "
        "From `scenarios.all_favourable()`.",
        f"The nutrient floor (what a kilo of cells must eat: amino acids at feed grade and the most efficient published need, "
        f"glucose and other nutrients): {money(n['floor'])}; the medium is never charged less. From "
        "`floor_physics.feedstock(floor_physics.GOOD_CELLS)`, `nutrient_floor.py`.",
        f"Price parity with a {money(n['p_conv'], 0)} kilo of US minced beef or pork cuts needs cells at {money(n['parity'])} or "
        "less (shelf price = (cost + per-kilo costs to the shelf) / (1 - retail margin)). From `price_ratio.parity_cost`.",
        f"Long-run share at equal price, once familiar: {n['eqs_all'] * 100:g}% of all choices "
        f"(range {n['eqs_lo'] * 100:g}% to {n['eqs_hi'] * 100:g}%), which is {n['buyers'] * 100:.1f}% of meat buyers. A judgement "
        "from the literature on first-contact aversion fading, not a measurement: the input `equal_price_share`, "
        "`scenarios.meat_buyers_at_equal_price()`.",
        f"A 1% long-run share of world meat needs cells at {money(n['cost_1'], 1)} a kilo or less; 10% needs "
        f"{money(n['cost_10'], 1)}, below every set of traits tried. From `scenarios.cost_for_share`.",
    ]


# ----------------------------------------------------------------------------------------------------------------------------
# Section 2: the causal chain as functions
# ----------------------------------------------------------------------------------------------------------------------------
def chain() -> str:
    R = Repl()
    parts = []
    parts.append(
        "Each step is one function. The examples were run when this file was generated; the outputs are real. Run them from the "
        "repository root with the repository on `PYTHONPATH`. Costs are $ per kilo of wet cells in 2025 dollars, unless said.\n")

    parts.append("### Step 0. Inputs: `inputs.value(name)`, `inputs.prior(name)`, `inputs.REGISTRY`\n\n"
                 "Every number lives once in `inputs.py` as an `Input(value, unit, source, lo, hi, mode, kind, note)`. `value` gives "
                 "the point value; `prior` gives the Monte Carlo prior as (kind, lo, hi, mode, note). Swap a REGISTRY entry with "
                 "`dataclasses.replace` to move an input (answer_rests_on.py does this); restore it after.\n")
    parts.append(R.run(['import inputs', 'inputs.value("media_price"), inputs.REGISTRY["media_price"].unit',
                        'inputs.prior("media_price")[:4]', 'len(inputs.REGISTRY)']))

    parts.append("\n### Step 1. Traits of the cells, the tank and the plant, to the settings of the engine: "
                 "`scenarios.explore_kwargs(choice)`\n\n"
                 "A reference point is a `choice`: a dict of eleven switches (mode, cells, growth, plant, gas, tricks, shape, losses, "
                 "restart, gf, medium) plus extras. `explore_kwargs` turns it into the keyword arguments of the engine: doubling time "
                 "in hours (`doubling_h`), cell mass in pg (`mass_pg`), ammonia in mol per kilo (`nh3_kg`), lactate in mol per mol of "
                 "glucose (`lac_yield`), tank size in m³ (`vessel_m3`, 20 when not given), medium price in $ a litre (`medium_price`), and so on.\n")
    parts.append(R.run(['import scenarios as S', 'choice = S.SCENARIOS["central"].choice',
                        'kw = S.explore_kwargs(choice)',
                        '{k: kw[k] for k in ("doubling_h", "mass_pg", "nh3_kg", "lac_yield", "mode", "plant", "medium_price", "nh3_limit", "lac_limit")}']))

    parts.append("\n### Step 2. Settings to the cost of a kilo of cells: `floor_physics.explore(**kw)`\n\n"
                 "The engine. Oxygen and CO₂ transfer, waste build-up, salt strength and the cell filter set the density the tank "
                 "holds (`density`, g/L) and what limits it (`limit`); density and growth rate set the output; the output spreads "
                 "the plant's yearly charge, labour and utilities; the waste the cells make sets the litres of medium. It returns a "
                 "dict; `total` is the cost, and the lines below add up to it with the smaller items (filters, protectant, gas). "
                 "With no arguments it is Humbird's optimistic design.\n")
    parts.append(R.run(['import floor_physics as fp', 'r = fp.explore(**kw)',
                        'round(r["total"], 2), round(r["density"]), r["limit"], round(r["medium_l"], 1)',
                        '{k: round(float(r[k]), 2) for k in ("feedstock", "growth_factors", "consumables", "utilities", "labour", "capital")}',
                        'round(fp.explore()["total"], 2)']))

    parts.append("\n### Step 3. Cost to shelf price and price ratio: `price_ratio.shelf_price`, `ratio`, `parity_cost`\n\n"
                 "shelf price = (cost + markup_add) / (1 - retail_margin); R = shelf price / price of the conventional meat it "
                 "copies. Cuts (fillets, steaks) are part plant protein: `price_ratio.structured_cost(cells)`.\n")
    parts.append(R.run(['import price_ratio as PR', 'cost = r["total"]', 'round(PR.shelf_price(cost), 2)',
                        'round(PR.ratio(cost, inputs.value("markup_add"), inputs.value("p_conv")), 2)',
                        'round(PR.parity_cost(inputs.value("markup_add"), inputs.value("p_conv")), 2)']))

    parts.append("\n### Step 4. Price ratio to choice: `market_share.share(R, DemandParams(), which=\"x_meat\")`\n\n"
                 "A two-segment (mainstream and ethical) flat logit over four products (conventional meat, plant-based meat, "
                 "cultivated meat, a whole-food option), with shoppers differing in how much they like cultivated meat (a Student's t "
                 "spread) and a price-insensitive minority. Calibrated so that plant-based meat takes its observed 0.4% of meat by "
                 "volume. `which=\"x_meat\"` returns cultivated meat's share of the meat sold, x / (x + c), long run, at the "
                 "reference (US) income and a $12 meat.\n")
    parts.append(R.run(['from market_share import DemandParams, share', 'pr = DemandParams()',
                        '[round(share(R, pr, which="x_meat") * 100, 3) for R in (1.0, 1.5, 2.0, 3.0)]']))

    parts.append("\n### Step 5. Every meat type and region: `meat_market.penetration(market, cost, income=..., pr=...)`\n\n"
                 "Repeats step 4 for each meat type at its own local price and the region's income, turns cells into cuts, lowers "
                 "conventional meat's price as it loses sales, gives closed markets none, and adds up by volume and by value. It "
                 "returns (rows, share by volume, share by value) as fractions. `scenarios.shares(cost)` wraps it for three "
                 "regions, in percent.\n")
    parts.append(R.run(['import meat_market as mm',
                        'rows, vol, val = mm.penetration(mm.MARKETS["global"], cost, income=mm.REGION_INCOME["global"], pr=pr)',
                        'round(vol * 100, 3), round(val * 100, 3)',
                        '{k: round(v, 3) for k, v in S.shares(cost).items()}']))

    parts.append("\n### Step 6. Over time: `adoption_timing.years_for_cost(cost)`\n\n"
                 "Bass diffusion for the rollout and first-contact wariness fading towards the long-run attitude. Years to 90% of the "
                 "long-run share, at the point value of the fading rate and at the fast and slow ends of its range.\n")
    parts.append(R.run(['import adoption_timing as AT', 'AT.years_for_cost(cost)']))

    parts.append("\n### Shortcuts\n\n"
                 "- `scenarios.run(choice)`: steps 1 and 2, with the tank design chosen; `scenarios.SCENARIOS` holds the reference "
                 "points, `scenarios.LADDER` their order.\n"
                 "- `scenarios.bands(choice)`: the Monte Carlo band over the unmeasured estimates (cost and share).\n"
                 "- `scenarios.cost_for_share(target_percent)`: the cost of cells that gives a long-run world share.\n"
                 "- `answer_rests_on.cost_drivers()`, `demand_drivers()`: every ranged input moved to each end, one at a time.\n")
    return "\n".join(parts)


# ----------------------------------------------------------------------------------------------------------------------------
# Section 3: every input
# ----------------------------------------------------------------------------------------------------------------------------
_DRV: dict = {}


def _cost_rows(keys: list) -> list:
    """answer_rests_on.cost_drivers() over these inputs only (one worker's share of the scan)."""
    sys.path.insert(0, ROOT)
    import answer_rests_on as AR
    keep = set(keys)
    full = AR._ranged
    AR._ranged = lambda: [(k, v) for k, v in full() if k in keep]
    return AR.cost_drivers()


def cost_drivers_side_by_side() -> list:
    """answer_rests_on.cost_drivers(), the inputs split over worker processes. Each input is moved alone, so the rows are the
    same as one process gives; they are put back in the scan's order and sorted as cost_drivers sorts them. One process when
    workers cannot be started, or with AGENTS_EDITION_JOBS=1."""
    import answer_rests_on as AR
    if "cost" in AR._CACHE:
        return AR._CACHE["cost"]
    keys = [k for k, _v in AR._ranged()]
    jobs = int(os.environ.get("AGENTS_EDITION_JOBS", os.cpu_count() or 1))
    rows = None
    if jobs > 1:
        try:
            import multiprocessing as mp
            from concurrent.futures import ProcessPoolExecutor
            chunks = [keys[i::jobs] for i in range(jobs)]
            with ProcessPoolExecutor(max_workers=jobs, mp_context=mp.get_context("spawn")) as ex:
                got = [r for part in ex.map(_cost_rows, chunks) for r in part]
            order = {k: i for i, k in enumerate(keys)}
            got.sort(key=lambda r: order[r["key"]])
            got.sort(key=lambda r: -abs(r["central"][1] - r["central"][0]))
            rows = got
        except Exception as e:                      # no worker processes here: one process gives the same rows
            print(f"agents_edition: workers failed ({e!r}); scanning in one process", file=sys.stderr)
    if rows is None:
        rows = AR.cost_drivers()
    AR._CACHE["cost"] = rows
    return rows


SCAN_JSON = os.path.join(ROOT, "agents_edition_scan.json")


def fingerprint() -> str:
    """A hash of every input's value and range: the scan is stale when it changes."""
    import hashlib
    from inputs import REGISTRY
    rows = [[k, repr(v.value), repr(v.lo), repr(v.hi), repr(v.mode), v.kind, repr(v.clip)] for k, v in REGISTRY.items()]
    return hashlib.sha256(json.dumps(rows).encode("utf-8")).hexdigest()


def scan() -> dict:
    """Run answer_rests_on's two scans (the cost one side by side) and return what the edition needs from them."""
    import answer_rests_on as AR
    cost = cost_drivers_side_by_side()
    demand = AR.demand_drivers()
    return {"about": "answer_rests_on.py's scans, stored so the edition and its test need not run them (about 28 minutes in one "
                     "process). Written by `python agents_edition.py --scan`; tests/test_agents_edition.py fails when the inputs' "
                     "fingerprint or the two examples' costs no longer match the model.",
            "fingerprint": fingerprint(), "central_cost": AR._cost("central"), "best_cost": AR._cost("best"),
            "central_share": AR.S.shares(AR._cost("central"))["global"], "best_share": AR.S.shares(AR._cost("best"))["global"],
            "cost_rows": cost, "demand_rows": demand, "excluded_reasons": AR.excluded_reasons()}


def load_scan() -> dict:
    with open(SCAN_JSON, encoding="utf-8") as f:
        return json.load(f)


def drivers() -> dict:
    """answer_rests_on's two scans, keyed by input, from the stored scan (agents_edition_scan.json). Its rows are put into
    answer_rests_on's cache, so its own markdown tables are written from them."""
    if not _DRV:
        import answer_rests_on as AR
        sc = load_scan()
        tup = lambda r: {k: (tuple(v) if isinstance(v, list) else v) for k, v in r.items()}
        AR._CACHE["cost"] = [tup(r) for r in sc["cost_rows"]]
        AR._CACHE["demand"] = [tup(r) for r in sc["demand_rows"]]
        AR._CACHE["excl"] = list(sc["excluded_reasons"])
        _DRV["cost"] = {r["key"]: r for r in AR._CACHE["cost"]}
        _DRV["demand"] = {r["key"]: r for r in AR._CACHE["demand"]}
        _DRV["AR"] = AR
    return _DRV


def inputs_records() -> list:
    from inputs import REGISTRY
    d = drivers()
    out = []
    for name, inp in REGISTRY.items():
        rec = {"name": name, "value": inp.value, "unit": inp.unit, "source": inp.source, "note": inp.note,
               "evidence_class": evidence_class(inp)}
        if inp.has_prior:
            rec["range"] = {"kind": inp.kind, "lo": inp.lo, "mode": inp.prior_mode, "hi": inp.hi}
            if inp.clip is not None:
                rec["range"]["clip"] = list(inp.clip)
        else:
            rec["range"] = None
        if name in d["cost"]:
            r = d["cost"][name]
            rec["moves_cost"] = {"low_lactate_example_usd_per_kg_at_lo_hi": [round(x, 4) for x in r["central"]],
                                 "all_favourable_example_usd_per_kg_at_lo_hi": [round(x, 4) for x in r["best"]],
                                 "low_lactate_example_world_share_pct_at_lo_hi": [round(x, 6) for x in r["share"]]}
        if name in d["demand"]:
            r = d["demand"][name]
            rec["moves_share"] = {"world_share_pct_at_low_lactate_cost_at_lo_hi": [round(x, 6) for x in r["central"]],
                                  "world_share_pct_at_all_favourable_cost_at_lo_hi": [round(x, 6) for x in r["best"]]}
        out.append(rec)
    return out


def inputs_json() -> str:
    from inputs import REGISTRY
    doc = {
        "about": "Every input of the cultivated-meat model (inputs.py REGISTRY), generated by agents_edition.py. value is the point "
                 "value the model uses; range is the Monte Carlo prior (triangular: lo, mode, hi; lognormal: median mode, lo and hi "
                 "the 5th and 95th percentiles; null: fixed). evidence_class is read mechanically from the source tag. moves_cost "
                 "and moves_share appear for the inputs answer_rests_on.py finds move the cost by $1 a kilo or the share by its "
                 "thresholds when set to each end of their range.",
        "evidence_classes": dict(EVIDENCE_CLASSES),
        "count": len(REGISTRY),
        "inputs": inputs_records(),
    }
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n"


def inputs_section() -> str:
    AR = drivers()["AR"]
    d = drivers()
    recs = inputs_records()
    counts = {}
    for r in recs:
        counts[r["evidence_class"]] = counts.get(r["evidence_class"], 0) + 1
    out = [f"There are {len(recs)} inputs, each defined once in `inputs.py` and listed in full, with its whole source and note, "
           "in `inputs.json`. The evidence class is read mechanically from the source tag (the text in its first square brackets); "
           "it is not a review of the evidence. The inputs that matter are described by hand in `answer_rests_on.EVIDENCE` (the "
           "column \"where the value comes from\" below).\n",
           "| evidence class | what it means | inputs |", "|---|---|---|"]
    for cls, what in EVIDENCE_CLASSES:
        out.append(f"| {cls} | {what} | {counts.get(cls, 0)} |")
    out.append("")
    out.append("### The inputs that move the cost most\n")
    out.append(f"Every input with a range moved to each end, one at a time (`answer_rests_on.cost_drivers()`); kept when it moves the "
               f"low-lactate example's or the all-favourable example's cost by ${AR.COST_MIN:g} a kilo or more. Largest swing in "
               "the low-lactate example first. Marked **[cost]** in the full list below.\n")
    out.append(AR.markdown_cost())
    out.append("")
    out.append("### The inputs that move the share most\n")
    out.append(f"The demand inputs moved the same way (`answer_rests_on.demand_drivers()`); kept when they move the share by "
               f"{AR.SHARE_MIN[0]:g} points at the low-lactate example's cost or {AR.SHARE_MIN[1]:g} at the all-favourable "
               "example's. Largest at the all-favourable example first. Marked **[share]** below.\n")
    out.append(AR.markdown_demand())
    out.append("")
    out.append("### All inputs\n")
    out.append("Value, unit, Monte Carlo range (triangular lo, mode, hi unless marked lognormal: median, 5th and 95th percentiles), "
               "evidence class and source tag. Full sources and notes are in `inputs.json`.\n")
    out.append("| input | value | unit | range | evidence | moves | source tag |")
    out.append("|---|---|---|---|---|---|---|")
    for r in recs:
        rg = r["range"]
        rng = "fixed" if rg is None else (f"{num(rg['lo'])}, {num(rg['mode'])}, {num(rg['hi'])}" +
                                          (" (lognormal)" if rg["kind"] == "lognormal" else (" (uniform)" if rg["kind"] == "uniform" else "")))
        moves = " ".join(m for m, key in (("**[cost]**", "moves_cost"), ("**[share]**", "moves_share")) if key in r)
        m = re.match(r"\s*\[([^\]]+)\]", r["source"] or "")
        tag = m.group(1) if m else cell((r["source"] or "")[:60])
        out.append(f"| `{r['name']}` | {cell(num(r['value']))} | {cell(r['unit'])} | {rng} | {r['evidence_class']} | {moves} | {cell(tag)} |")
    del d
    return "\n".join(out)


# ----------------------------------------------------------------------------------------------------------------------------
# Section 4: the checks
# ----------------------------------------------------------------------------------------------------------------------------
def checks_section() -> str:
    import demand_checks as D
    import humbird_check as HC
    import scenarios as S
    import study_assumptions as SA
    out = ["### 4.1 The back-test against Humbird's own tables (`humbird_check.py`)\n",
           "The engine run at Humbird's own conditions (his cells, tanks, plant cost, yearly charge, nutrient cost and limits; "
           "everything he does not count switched off), in his 2018 dollars, against his Tables 4.7 and 4.13. The line-by-line "
           "tables are in `research_notes/humbird_backtest.md`; `tests/test_humbird_check.py` holds each line within its "
           f"tolerance ({HC.LINE_TOL:.0%} a line, {HC.TOTAL_TOL_DEFAULT:.0%} on the total, unless a residual below is named).\n",
           "| design | Humbird, 2018 $ | engine at his conditions, 2018 $ | gap | engine, 2025 $ | tolerance on the total | within it |",
           "|---|---:|---:|---:|---:|---:|---|"]
    for case in HC.ORDER:
        rows = {k: (his, eng, gap, today) for k, his, eng, gap, today in HC.compare(case)}
        his, eng, gap, today = rows["total"]
        tol = HC.tolerance(case, "total")
        out.append(f"| {HC.HIS[case]['label']} | {his:.2f} | {eng:.2f} | {gap:+.1%} | {today:.2f} | {tol:.0%} | "
                   f"{'yes' if abs(gap) <= tol else 'NO'} |")
    out.append("\nThe residuals that could not be closed from his report, each with its reason:\n")
    for (case, line), (tol, why) in HC.RESIDUALS.items():
        h, e, gap = next((h, e, g) for k, h, e, g, _t in HC.compare(case) if k == line)
        out.append(f"- {HC.HIS[case]['label']}, {HC.LINE_NAMES.get(line, line)}: gap {gap:+.1%} (tolerance {tol:.0%}). {why}")
    out.append("\nWhat this model adds to his best estimate, one lever at a time from the page's start "
               f"({money(HC.page_start()['total'])}, 2025 dollars):\n")
    out.append("| lever switched on alone | adds, $ a kilo |")
    out.append("|---|---:|")
    for _key, name, d in HC.page_additions():
        out.append(f"| {name} | {d:+.2f} |")
    out.append(f"| all of them together | {HC.page_with_additions()['total'] - HC.page_start()['total']:+.2f} |")

    # --- the demand checks
    s = D.summary()
    v = s["variants"][0]
    i3 = D.R_GRID.index(3.0)
    import market_size_loop as L
    resp = L.summary()["response"]["products"]
    still = [n for n, x in resp.items() if x["R"][0] > 1.5]
    pick = [resp[n]["response"] for n in still]
    m = D.menu_summary()
    cold_ok = D.VANLOO_ARMS[1] >= v["cold"] >= D.VANLOO_ARMS[0]
    p3, p3m = v["curve"][i3], s["premium_3x"]
    p3_ok = 1 / 1.3 <= p3 / p3m <= 1.3
    salmon_ok = all(D.SALMON_ALONG_CURVE[0] <= x <= D.SALMON_ALONG_CURVE[1] for x in pick)
    pb = s["pb"]["elasticity"]
    pb_ok = D.PB_CATEGORY_RANGE[0] <= pb <= D.PB_CATEGORY_RANGE[1]
    yes = lambda b: "passes" if b else "**misses**"
    out += ["\n### 4.2 Five checks on the response to price (`demand_checks.py`)\n",
            "The demand model has never seen cultivated meat on sale, so its response to price is checked against five measurements "
            "of novel or premium foods. Details in `research_notes/demand_checks.md`; `tests/test_demand_checks.py` pins each "
            "result. The pass rule for each is stated in the row.\n",
            "| check | measured | the model | rule | result |", "|---|---|---|---|---|",
            f"| 1. Cultivated meat at first contact and equal price: own-price elasticity (Van Loo, Caputo and Lusk 2020, simulated "
            f"from the paper's fitted model) | about {D.VANLOO_AT_PARITY:g} ({D.VANLOO_ARMS[1]:g} to {D.VANLOO_ARMS[0]:g} across its "
            f"arms) | {v['cold']:.2f} | inside the arms' range | {yes(cold_ok)} |",
            f"| 2. Share of a meat at 3 times the ordinary one's price (sixteen premium real meats, fitted; `premium_curve.py`) | "
            f"{p3m:.1f}% | {S.pct_num(p3)}% | within a factor of 1.3 | {yes(p3_ok)} |",
            f"| 3. A premium product getting cheaper: % more volume per % lower price (farmed salmon while it was premium) | "
            f"{D.SALMON_ALONG_CURVE[0]:g} to {D.SALMON_ALONG_CURVE[1]:g} | {min(pick):.1f} to {max(pick):.1f} (the model's premium "
            f"products still dearer than their meat at the low-lactate example's cost) | every product inside the range | "
            f"{yes(salmon_ok)} |",
            f"| 4. Plant-based meat's own-price elasticity (US retail; GFI/NielsenIQ) | {D.PB_ELASTICITY_MEASURED:.2f} (category "
            f"{D.PB_CATEGORY_RANGE[0]:g} to {D.PB_CATEGORY_RANGE[1]:g}) | {pb:.2f} | inside the category's range | {yes(pb_ok)} |",
            f"| 5a. Adding plant-based meat priced like meat to a menu: fall in meat's share, points (Hope 2026, US) | "
            f"{D.HOPE_FALL:g} (95% interval {D.HOPE_CI[0]:g} to {D.HOPE_CI[1]:g}; {D.HOPE_RULED_OUT:g} or more ruled out) | "
            f"{m['fall']:.2f} | inside the interval, under the ruled-out size | {yes(m['size_passes'])} |",
            f"| 5b. The same menu: share of the new option's orders taken from meat | about {D.HOPE_FROM_MEAT * 100:.0f}% | "
            f"{m['from_meat'] * 100:.0f}% | under 50% | {yes(m['source_passes'])} |"]
    misses = [n for n, ok in (("3 (farmed salmon)", salmon_ok), ("5b (where the menu's new orders come from)", m["source_passes"]),
                              ("1", cold_ok), ("2", p3_ok), ("4", pb_ok), ("5a", m["size_passes"])) if not ok]
    out.append(f"\nMisses: {', '.join(misses) if misses else 'none'}. In the model a flat logit within each group of shoppers "
               "takes a new option's sales from each product in proportion to its share, so most of plant-based meat's orders come "
               "from meat, the largest product; the menu experiment found most came from the vegetarian option. The salmon check "
               "says the model's premium products respond more strongly to price than farmed salmon did.\n")

    # --- the study comparison
    out += ["### 4.3 The published cost studies (`study_assumptions.py`, `research_notes/study_comparison.md` section 13)\n",
            "Each study's design as a set of modifications on Humbird's best estimate, with its assumptions made reasonable but "
            "ambitious long-term estimates and corrected where they break a limit of this model (every assumption, what the "
            "study says and where, what the set uses and why: section 13 of the note; `tests/test_study_assumptions.py` checks "
            "that every lever a set moves has a row). Plant is every cost that scales with what the plant cost to build; running "
            "is the rest.\n",
            "| set | the study's own figure | this engine, $ a kilo of cells | plant | running |", "|---|---|---:|---:|---:|"]
    for e in SA.sets():
        sp = SA.split(e["settings"])
        out.append(f"| {cell(e['name'])} | {cell(e['own'])} | {sp['total']:.2f} | {sp['plant']:.2f} | {sp['running']:.2f} |")
    c = SA.comparison()
    out.append(f"\nEach study's own most favourable estimate, in 2025 dollars a kilo of wet cells, against the all-favourable "
               f"example ({money(c['all_favourable'])}):\n")
    out.append("| study | its estimate as published | as a kilo of wet cells, 2025 $ | below the all-favourable example |")
    out.append("|---|---|---:|---|")
    for r in c["rows"]:
        today = "not compared: " + cell(r["not_compared"] or "no figure") if r["today"] is None else f"{r['today']:.2f}"
        out.append(f"| {cell(r['name'])} | {cell(r['published'] or 'no cost published')} | {today} | {'yes' if r['below'] else ''} |")
    for b in c["below"]:
        lims = "; ".join(f"{a['assumption']} (breaks: {a['limit_name']})" for a in b["assumptions"])
        inside = f" Inside the limits its design costs {money(b['inside'])}." if b["inside"] is not None else ""
        out.append(f"\n- {b['name']} is below it because of assumptions beyond this model's limits: {lims}.{inside}")
    return "\n".join(out)


# ----------------------------------------------------------------------------------------------------------------------------
# Section 6: open questions
# ----------------------------------------------------------------------------------------------------------------------------
def open_questions() -> str:
    d = drivers()
    AR = d["AR"]
    rows = []
    for k, r in d["cost"].items():
        rows.append((abs(r["share"][1] - r["share"][0]), k, "cost", r))
    for k, r in d["demand"].items():
        rows.append((abs(r["central"][1] - r["central"][0]), k, "share", r))
    rows.sort(key=lambda t: (-t[0], t[1]))
    out = ["Ranked by how far the input, moved across its range, moves the low-lactate example's long-run share of world meat "
           "(a cost input moves the share through the cost). Each comes with the measurement that would settle it, and the "
           "current evidence (`answer_rests_on.EVIDENCE`). Inputs whose evidence is an observed price or a measured elasticity "
           "are listed for completeness: the ranking is by leverage, not by weakness of evidence.\n",
           "| rank | input | moves the low-lactate example's share | moves the cost | evidence now | the measurement that would settle it |",
           "|---:|---|---|---|---|---|"]
    for i, (_sw, k, kind, r) in enumerate(rows, 1):
        if kind == "cost":
            sh = f"{pct(r['share'][0])} to {pct(r['share'][1])}"
            co = f"{money(r['central'][0], 1)} to {money(r['central'][1], 1)} (all-favourable {money(r['best'][0], 1)} to {money(r['best'][1], 1)})"
        else:
            sh = f"{pct(r['central'][0])} to {pct(r['central'][1])} (all-favourable {r['best'][0]:.1f}% to {r['best'][1]:.1f}%)"
            co = "no"
        out.append(f"| {i} | {cell(AR.PLAIN.get(k, k))} (`{k}`) | {sh} | {co} | {cell(AR.EVIDENCE.get(k, AR._tag(k)))} | "
                   f"{cell(SETTLE.get(k, 'no measurement named yet: add one to SETTLE in agents_edition.py'))} |")
    return "\n".join(out)


# ----------------------------------------------------------------------------------------------------------------------------
# Section 5: dead ends
# ----------------------------------------------------------------------------------------------------------------------------
def dead_ends_section() -> str:
    out = ["Assumptions, anchors and structures tried in this model and withdrawn or corrected, oldest first, so they are not "
           "tried again without new evidence. Each names the file where it is recorded.\n",
           "| date | what was tried | why it was withdrawn, and what replaced it | recorded in |", "|---|---|---|---|"]
    for date, what, why, where in DEAD_ENDS_DATA:
        out.append(f"| {date} | {cell(what)} | {cell(why)} | {cell(where)} |")
    out.append("\nStill open (decisions, not withdrawn):\n")
    out += [f"- {x}" for x in STILL_OPEN]
    return "\n".join(out)


# ----------------------------------------------------------------------------------------------------------------------------
# Section 7: how to extend
# ----------------------------------------------------------------------------------------------------------------------------
def test_list() -> list:
    txt = open(os.path.join(ROOT, "run_tests.sh"), encoding="utf-8").read()
    return re.findall(r'^\s*"([^"|]+)\|([^"]+)"', txt, flags=re.M)


def extend_section() -> str:
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    import test_easy_view as EV
    tests = test_list()
    out = ["### Run the model\n",
           "```bash\n"
           "pip install -r requirements.txt        # numpy and matplotlib; Node.js 18+ for the parity test\n"
           "python inputs.py                       # the datasheet: every input, its source and range\n"
           "python scenarios.py                    # the reference points: cost, density, limit, share\n"
           "python humbird_check.py                # the back-test\n"
           "python answer_rests_on.py              # what the answer rests on (several minutes)\n"
           "python build_interactive.py            # rebuild interactive.html from the Python\n"
           "./run_tests.sh                         # rebuild the page, then every test in parallel (15 to 20 minutes)\n"
           "python agents_edition.py               # rewrite AGENTS.md, llms.txt and inputs.json\n"
           "```\n",
           "Run from the repository root. The scripts import each other by module name, so the root must be on `PYTHONPATH` "
           "(`PYTHONPATH=. python ...` if it is not).\n",
           "### The tests (`run_tests.sh`)\n"]
    out += [f"- `{path}`: {label}" for label, path in tests]
    out += ["\n### Rules a change must keep\n",
            "1. **Python is the source of truth.** Never hand-edit `interactive.html`: `build_interactive.py` writes it, ports the "
            "model to JavaScript and fills every number in its text. Change the Python, rebuild, then run `./run_tests.sh`. "
            "`tests/run_parity.py` checks the JavaScript against the Python to 1e-4.",
            "2. **One source for every number.** A new number goes into `inputs.py` as an `Input` with its unit, a source tag in "
            "square brackets, a range if it is uncertain, and a note. Never type a model number into prose: the page's text uses "
            "build-time tokens and `tests/test_golden.py` checks the numbers quoted in RESULTS.md and METHODS.md.",
            "3. **Golden values move only on purpose.** If a change moves a headline output, update `GOLDEN` in "
            "`tests/test_golden.py` in the same commit, and say in CHANGELOG.md what moved and why.",
            "4. **This file is generated.** After any change, run `python agents_edition.py`; "
            "`tests/test_agents_edition.py` fails if AGENTS.md, llms.txt or inputs.json differ from a fresh run. The scan of what "
            "the answer rests on is stored in `agents_edition_scan.json`; when an input or the engine changes, the test asks for "
            "`python agents_edition.py --scan`, which runs it again split over the machine's cores.",
            "5. **Wording rules** (enforced on the page by `tests/test_easy_view.py`, and on this file by "
            "`tests/test_agents_edition.py`):",
            f"   - retired names, never used: {', '.join(repr(x) for x in EV.RETIRED)};",
            "   - no judgement or odds attributed to the owner or the author (the pattern `OWNER_JUDGED` in the test): a judgement "
            "is the model's, labelled as such, with its range;",
            "   - a converted cost names the year of its dollars (\"2025 dollars\"), never the present (the pattern `TODAY_COST`);",
            "   - no em dash in visible text;",
            "   - cells are described by their traits (ammonia, lactate, doubling time, mass), never by how cells would come to "
            "have them: no route words (the pattern `ROUTE_WORDS`); never imply that a trait needs one method;",
            "   - no forecast in the summary; literal section titles, not figurative ones; explanatory names are kept long.",
            "6. **Calibrated claims.** A value nobody has measured is called a judgement or an assumption, with its range, and "
            "the answer's dependence on it is shown (answer_rests_on.py). Evidence is searched in both directions.",
            "\n### Add a published cost study as a starting set (with its audit)\n",
            "1. Put the study's PDF in `Cultivated_meat_TEAs/` (outside this repository) and add an entry to "
            "`study_assumptions.STUDIES`: name, year, citation, the system it models in one plain sentence, its own reported cost "
            "and basis, and each assumption as (what, value as the source gives it, reference with the PDF page). Record only "
            "values read in the source; a value worked out from them says \"derived\" and shows the arithmetic.",
            "2. Add what it assumes on each lever of the all-favourable example to `STUDY_LEVERS`. A value that breaks a limit of "
            "the model (`LIMITS`) goes into `REJECTED` with the limit and its source, and is never a source for "
            "`scenarios.all_favourable()`.",
            "3. Add its most favourable estimate to `ESTIMATES` (basis, year of its dollars) so `estimates()` brings it to a kilo of "
            "wet cells in 2025 dollars.",
            "4. Express its design in the page's levers as modifications over Humbird's best estimate (`_mods()`: traits, held, "
            "plant, vm, device); an assumption the levers cannot say carries `not_representable` and the reason.",
            "5. Add a `SETS` entry with `audit`: one row per assumption, (assumption, the setting it moves or None, what the study "
            "says and where, one of the reasons in `AUDIT_WHY`, what the set uses when it is not the study's value). The reasons: "
            + "; ".join(f"{cell(v)}" for v in __import__('study_assumptions').AUDIT_WHY.values()) + ".",
            "6. If it publishes a plant and running split, add it to `SPLITS`.",
            "7. Regenerate section 13 of `research_notes/study_comparison.md` from `study_assumptions.markdown()`, rebuild the page, "
            "run `./run_tests.sh` (`tests/test_study_assumptions.py` checks that every lever a set moves has an audit row and that "
            "the page gives the same cost), then `python agents_edition.py`.",
            "\n### Where things are\n",
            "- `RESULTS.md`: the findings, with Monte Carlo bands. `METHODS.md`: the methods and sources at code level. "
            "`CHANGELOG.md`: what changed, dated. `TODO.md`: open work and decisions waiting.",
            "- `research_notes/`: one note per question, with the evidence read and the reasoning; the module docstrings name "
            "their notes.",
            f"- The page: {PAGE_URL}interactive.html. The repository: {REPO_URL}."]
    return "\n".join(out)


# ----------------------------------------------------------------------------------------------------------------------------
# The documents
# ----------------------------------------------------------------------------------------------------------------------------
INTRO = ("This is the cultivated-meat cost and demand model written for AI agents: what it answers, how, on what inputs, how it "
         "is checked, what was tried and withdrawn, what is open, and how to change it. It is generated from the code by "
         "`agents_edition.py`; do not edit it by hand. Every number below was computed by the model when the file was written. "
         "The model asks two questions: how cheap can a kilo of cultivated meat cells plausibly get, and at that cost, how much "
         "conventional meat would cultivated meat displace? The first is a cost built from tank physics and published plant "
         "designs (fairly solid where it rests on measurements). The second depends on how people will treat a product nobody can "
         "buy yet, so it is always a band. The model makes no forecast of when any cost is reached.")


def agents_md() -> str:
    parts = ["# Cultivated meat: cost and market share. The edition for AI agents", "", INTRO, "",
             "Contents: 1. The question and the answer in ten lines. 2. The causal chain as functions. 3. Every input. "
             "4. The checks. 5. Dead ends and corrections. 6. Open questions, ranked. 7. How to extend.", "",
             "## 1. The question and the answer in ten lines", ""]
    parts += [f"{i}. {line}" for i, line in enumerate(ten_lines(), 1)]
    parts += ["", "## 2. The causal chain as functions", "", chain(), "",
              "## 3. Every input", "", inputs_section(), "",
              "## 4. The checks", "", checks_section(), "",
              "## 5. Dead ends and corrections, dated", "", dead_ends_section(), "",
              "## 6. Open questions, ranked by how much they would move the answer", "", open_questions(), "",
              "## 7. How to extend", "", extend_section(), ""]
    return "\n".join(parts)


def llms_txt() -> str:
    lines = ["# Cultivated meat: cost and market share", "",
             "> A cost and demand model of cultivated meat: how cheap a kilo of cells can plausibly get, from tank physics and "
             "published plant designs, and how much of the world's meat it would take at that cost. Python is the source of truth; "
             "the interactive page is generated from it. Every number below is computed by the model (agents_edition.py).", "",
             "The answer in ten lines:", ""]
    lines += [f"- {line}" for line in ten_lines()]
    lines += ["", "## For agents", "",
              f"- [AGENTS.md]({RAW_URL}AGENTS.md): the whole edition for agents: the causal chain as functions with real inputs "
              "and outputs, every input, the checks and which miss, dead ends, open questions ranked, how to extend",
              f"- [inputs.json]({PAGE_URL}inputs.json): every input with value, unit, range, source, note and evidence class",
              f"- [Repository]({REPO_URL}): the Python model and its tests", "",
              "## For people", "",
              f"- [Interactive explorer]({PAGE_URL}interactive.html): the findings, every assumption as a lever, the method in "
              "plain language",
              f"- [RESULTS.md]({RAW_URL}RESULTS.md): the findings with their uncertainty bands",
              f"- [METHODS.md]({RAW_URL}METHODS.md): the methods and sources at code level", "",
              "## Optional", "",
              f"- [CHANGELOG.md]({RAW_URL}CHANGELOG.md): what changed and when",
              f"- [research_notes]({REPO_URL}/tree/main/research_notes): one note per question, with the evidence read", ""]
    return "\n".join(lines)


def outputs() -> dict:
    return {AGENTS_MD: agents_md(), LLMS_TXT: llms_txt(), INPUTS_JSON: inputs_json()}


def main() -> int:
    if "--scan" in sys.argv:
        with open(SCAN_JSON, "w", encoding="utf-8") as f:
            json.dump(scan(), f, indent=1, ensure_ascii=False)
            f.write("\n")
        print("wrote", os.path.relpath(SCAN_JSON, ROOT))
    out = outputs()
    if "--check" in sys.argv:
        stale = []
        for path, text in out.items():
            old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if old != text:
                stale.append(os.path.basename(path))
        if stale:
            print("out of date (run `python agents_edition.py` and commit): " + ", ".join(stale))
            return 1
        print("AGENTS.md, llms.txt and inputs.json match a fresh run")
        return 0
    for path, text in out.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote", os.path.relpath(path, ROOT))
    return 0


DEAD_ENDS_DATA = [
    ("2026-11-13", "The note said the loss-aversion parameter lambda leaves the regional roll-up unchanged.", "Corrected: absorbing lambda pushes the price weight beta positive (+0.051 at 2.25), so poorer shoppers become less price-sensitive and the world share rises from 2.5% to 6.3%. The default stays 1.0, the range is capped at 2.25, and results with lambda above about 1.65 are flagged as not meaningful.", "inputs.py, the loss_aversion note (corrected 2026-11-13)"),
    ("2026-11-14", "Pasitka et al. 2024 was the model's cost anchor.", "Dropped as the anchor because its kilogram is a wet pellet that is mostly liquid and its cost leaves out capital. The default was re-anchored on SuperMeat 2024's reported process, with a floor from physics.", "CHANGELOG.md 2026-11-14; METHODS.md, \"Why Pasitka is not the anchor\"; inputs.py, \"RE-ANCHORED 2026-11-14\""),
    ("2026-11-14", "One number, cult_sub_mult, set the price weight beta that every product shares.", "Raising it made shoppers more sensitive to every price, beans and plant-based meat included, and strained the calibration (at 9 a solved weight fell to zero). It was split: kappa_base (4) sets beta, and cult_sub_mult / kappa_base scales only cultivated meat's price difference from conventional meat.", "inputs.py, the kappa_base note (ADDED 2026-11-14)"),
    ("2026-11-15", "$11.5 a kilo from floor_physics.explore() at its defaults was presented as the floor.", "The name was retired: it was neither the most favourable case nor a typical one (20 m³ perfusion, 120 g/L, no tank tricks, no lost runs). It is kept as a labelled reference, Humbird's optimistic design, and the scenarios are built from switches.", "CHANGELOG.md 2026-11-15, \"Cost scenarios in place of the floor\""),
    ("2026-11-15", "Perfusion used a hoped-for cell-retention device with a flat capital and no membrane cost.", "Replaced as the default by a priced hollow-fibre filter loop (membranes about $0.37 a litre filtered). The most favourable scenario went from $6.57 to $8.95 and no scenario reached price parity. The old device stays behind rt_tff_default = 0.", "CHANGELOG.md 2026-11-15, \"The filter loop is the model's default\""),
    ("2026-11-15", "Antifoam took nothing off oxygen transfer, and the bubble protectant (poloxamer 188) was not charged.", "Antifoam's central value became 0.75 (the middle of the reported 0 to 50% cut), so oxygen now limits the low-lactate example. The protectant is charged at 2 g/L at an assumed bulk price below the $230 to 260 catalogue price, pending a supplier quote.", "CHANGELOG.md 2026-11-15, \"Three costs counted\"; TODO.md"),
    ("2026-11-16", "The protectant price prior ran from $10 to $260 a kg, with the catalogue price as its top.", "At that top the median tonne price drawn was $87, above what the catalogue-to-bulk gap suggests. The range was cut to $10 to 120, and later to $5 to 100 (2026-11-21).", "CHANGELOG.md 2026-11-16, \"Wider bands\"; research_notes/evidence_poloxamer_price.md"),
    ("2026-11-16", "The dollar channel's price coefficient in _derive_beta was left uncapped.", "Loss aversion above about 1.6 drove it positive, so paying more raised utility and the share rose with loss aversion (0.4% to 1.4%). It is capped at zero in Python and on the page. The split between dollars and ratios is still open.", "CHANGELOG.md 2026-11-16, \"Demand flaw\"; TODO.md"),
    ("2026-11-16", "The sorbent lever lowered the litres through the cell filter along with the fresh medium.", "Corrected: the liquid a device on the permeate cleans has already passed the cell filter. A sorbent taking half the ammonia gives $28.22, not $22.97. Cleaning the permeate saves $2 to 4 a kilo, not more.", "CHANGELOG.md 2026-11-16; research_notes/medium_reuse.md"),
    ("2026-11-16", "The scenarios held dissolved oxygen at Humbird's implied 0.28 mmol/L (130% of air saturation).", "Pharma holds 30 to 50%, so the scenarios hold 0.10 mmol/L (sc_do_setpoint). Humbird's optimistic design keeps his level.", "CHANGELOG.md 2026-11-16"),
    ("2026-11-18", "The step from a kilo of cells to the shelf was a flat $5 a kilo (range $3 to 8.7).", "Shop prices move about dollar for dollar with wholesale prices, but shops set a percentage margin (USDA ERS). The rule is now (cost + $2.5) / (1 - 28%). Parity moved from $7.00 to $6.14 a kilo of cells. A claim that margins rise with the quality tier was unsourced, and the one comparison found runs the other way.", "CHANGELOG.md 2026-11-18; research_notes/retail_markup_form.md"),
    ("2026-11-18", "The premium rows of the market tables (sushi-grade seafood 5.4 Mt, prime beef, heritage pork and organic chicken 1.35 Mt each) were used without a source.", "They were several times too large (about 1.2, 0.5, 0.4 and 0.4 Mt). Resizing cut the low-lactate example's share from 0.16% to 0.04%. An earlier agreement with the premium-meat anchoring was a coincidence of the oversized rows.", "CHANGELOG.md 2026-11-18; research_notes/premium_market_sizes.md"),
    ("2026-11-18", "A recalibration treated buyers of organic and welfare-labelled meat as cultivated meat's price-insensitive buyers.", "Not merged. In the two studies that split shoppers into groups, the price-insensitive organic buyers are the most hostile to cultivated meat. It was replaced by a spread of liking across all shoppers.", "research_notes/premium_buyers.md; research_notes/liking_spread.md section 1; TODO.md"),
    ("2026-11-18", "The demand check used -0.84 to -3.4 as the choice experiment's measured elasticity.", "That range is a formula on two of the experiment's coefficients, not a reported elasticity. The experiment's fitted model simulates to about -1.5, which the check now uses.", "CHANGELOG.md 2026-11-18; research_notes/demand_heterogeneity_evidence.md"),
    ("2026-11-19", "Shoppers' liking was a normal spread of 5 utils integrated on 15 points.", "Fifteen points were too few (integrated properly it gave -1.34, not -1.53, and missed the experiment), and a normal tail fell too fast above parity (0.1% at 4 times the price against premium meats' 0.6%). Replaced by a Student's t, refitted on 2026-11-22 to 3.55 utils and tail 7.", "CHANGELOG.md 2026-11-19; research_notes/liking_spread.md section 2"),
    ("2026-11-19", "A tier rule made buyers of cuts and premium products less price-sensitive (x0.8, x0.3), and a product became premium at 2.5 times its species' cheapest form.", "It worked backwards above about 1.5 times the price: more resistance gave cultivated meat a higher share (it added 41% to the low-lactate example). Removed. A cut now carries a penalty for its non-cell part, and premium products an offset that rises smoothly from 2 to 4 times the cheapest form.", "research_notes/audit_2026-11-19.md finding D3; CHANGELOG.md 2026-11-19"),
    ("2026-11-19", "The bands drew the equal-price share from a triangular 5/13/49% distribution.", "Its median was 21%, well above the 13% point it was meant to surround. It is now lognormal around 13%.", "research_notes/audit_2026-11-19.md finding D1"),
    ("2026-11-19", "Every scenario took an ammonia tolerance of 5 mmol/L.", "The model's own evidence note gives a median of 3.5 to 4. Set to 4 mmol/L (sc_nh3_limit, range 2 to 8); Humbird's optimistic design keeps 5.", "research_notes/audit_2026-11-19.md finding C2"),
    ("2026-11-19", "Published cells were given 0.84 mol of glucose a kilo, a figure drawn partly from CHO data and Pasitka's per-kilo-of-biomass figure.", "0.84 could not supply their own oxygen use. Glucose now comes from the cells' own balance (about 4.5 mol a kilo), so lactate sets their medium at about 95 litres a kilo, not 28.", "research_notes/audit_2026-11-19.md finding C5"),
    ("2026-11-19", "A kilo of cut was charged a full kilo of cells plus a $6 scaffold.", "The scaffold sat on top of the cells it replaces, and companies dropped scaffold-grown tissue. A kilo of cut is now 0.8 kg of cells, 0.2 kg of plant-protein matrix and an assembly cost.", "CHANGELOG.md 2026-11-19; research_notes/structuring_cost.md"),
    ("2026-11-19", "The nutrient floor was $1.70 a kilo on soy hydrolysate, medium settings at $0.05 and $0.15 a litre were offered, and growth factors were bought on top of announced medium prices.", "Hydrolysate cannot supply glutamine, arginine, asparagine, cystine or serine. The floor became $2.00 (232 g of feed-grade amino acids at $6.36, GFI December 2025). The two cheap settings were dropped. Announced prices are treated as complete media with growth factors inside; without that rule a culture under about 20 L a kilo got its growth factors free.", "research_notes/nutrient_floor.md section 6; research_notes/growth_factors_in_medium_price.md"),
    ("2026-11-19", "The density of a tank that is not perfused was Humbird's 120 g/L scaled by the waste the cells make.", "This broke the waste mass balance. The density is now end factor x level allowed / waste per kilo. The low-lactate example's batch fell from 56 to 37 g/L.", "CHANGELOG.md 2026-11-19; TODO.md"),
    ("2026-11-19", "A forecast for 2035 (a Monte Carlo over the switches, with odds for each way of reaching a trait) was built.", "Dropped the same day: the model gives no forecasts. The record of its odds was deleted on 2026-11-21.", "CHANGELOG.md 2026-11-19 and 2026-11-21"),
    ("2026-11-19", "Hypothetical sets of cells were given names, with tags saying how the cells would be obtained.", "All named kinds of cell were retired the same day. Cells are described only by their traits (the low-lactate example, the all-favourable example), each trait is set against the best value measured in meat cells, and no claim is made about how cells would come to have a trait.", "CHANGELOG.md 2026-11-19, \"Names\""),
    ("2026-11-19", "The share reported was cultivated meat's share of all four choices.", "A flat market at 50% of meat buyers showed 46.5%. The share is now x / (x + c), the share of the meat sold. Shares rose about a quarter at the low-lactate example's cost.", "CHANGELOG.md 2026-11-19 and 2026-11-21"),
    ("2026-11-19", "The headline share was the median of the Monte Carlo band, and the page led with the median cost and an 8-in-10 range.", "The all-favourable example's point sat below the 10th percentile of its own draws, and a median mixed cost and demand draws. The page shows the cost at the settings shown, with the draws in their own section.", "CHANGELOG.md 2026-11-19 and 2026-11-21"),
    ("2026-11-19", "A source text said a protectant cuts bubble deaths at least 100-fold.", "Jöbses 1991, the model's own input, gives about 20-fold at 1 g/L.", "CHANGELOG.md 2026-11-19, \"Two source texts corrected\""),
    ("2026-11-20", "The scenarios' cells tolerated 50 mmol/L of lactate with no range.", "That value decided the fed-batch cost ($209 at 50, $298 at 35). It is now 35 (sc_lac_limit, 20 to 50, drawn). Humbird's design keeps 50.", "research_notes/full_review_2026-11-19.md section 7; CHANGELOG.md 2026-11-20"),
    ("2026-11-20", "Filter membranes were given a life of 3,960 L/m² at the pharma price.", "That was the generous end (CHO membranes fouled after 450 to 1,200 L/m²; the evidence median is about 1,500). It is now Humbird's own replacement schedule at his price, 2,415 L/m².", "research_notes/filter_flux.md; CHANGELOG.md 2026-11-20"),
    ("2026-11-20", "Plant-based meat's anchor was 1.2% of meat by volume, and regional incomes were at purchasing-power parity with an income gradient of 0.5.", "The 1.2% contradicted its own note (under 1% by volume) and became 0.4%. Incomes became nominal GDP per head, with the gradient solved again (0.32).", "CHANGELOG.md 2026-11-20; inputs.py, the pb_share_target note"),
    ("2026-11-20", "The all-favourable example took 5.3 ng a cell from Risner 2021 (and CE Delft 2021's 5.2 and 3.6 ng).", "Those are assumptions of the analyses, not measurements, and no meat cell in suspension has been measured above about 2.3 ng. Rejected; the bound is Humbird's 3 ng. Pasitka's 3.3 and 9.8 ng are wet-pellet weights and are not used.", "research_notes/study_comparison.md sections 5 and 12"),
    ("2026-11-20", "Consumer-price factors for other years' dollars were typed from memory, and Humbird's yeast benchmark was read as support for cheaper financing.", "The factors are BLS CPI-U annual averages stored in inputs.py. The benchmark is 10% over 20 years, a higher rate than his 7.5%. CE Delft states payback years with no interest rate.", "research_notes/study_comparison.md sections 10 and 12"),
    ("2026-11-20", "The engine priced Humbird's growth factors over 11.2 L a kilo and charged his utilities as a flat $0.94 a kilo.", "Both misread his tables. Growth factors are over his fed-batch's 8.65 L a kilo, and utilities have four parts (by time, run, litre and kilo).", "research_notes/humbird_backtest.md, \"Gaps found\""),
    ("2026-11-21", "In a tank that is not perfused, the least medium flow capped the density, held to 1.0 times the perfusion level.", "A counting error: the by-products it stands for may end a batch 1.3 times above the level, as ammonia and lactate do. It no longer binds Humbird's design; the page's start with the additions went from $37.38 to $30.49.", "research_notes/humbird_backtest.md item 11; CHANGELOG.md 2026-11-21"),
    ("2026-11-21", "Fed-batch at 100 m³ was compared with perfusion at 20 m³, which made the batch look cheaper.", "Like for like, perfusion is cheaper at every size up to 100 m³ in every rung. Only cells making almost no ammonia or lactate at 200 m³ favour fed-batch.", "CHANGELOG.md 2026-11-21; TODO.md"),
    ("2026-11-24", "Published estimates that write the plant off with no interest (Ark Biotech 2023, Cellular Agriculture Ltd 2024, CE Delft 2021, Pasitka 2024 with no plant payment) were candidates for the favourable end.", "Rejected: a long-run price must repay the plant at a market rate. Pasitka's own Table S4 charge, with the plant included, gives a higher cost than its headline.", "research_notes/study_comparison.md sections 5 and 12; research_notes/evidence_pasitka_supplement.md"),
]

STILL_OPEN = [
    "Whether the range of the long-run share at equal price for the ordinary demand (`equal_price_share`) should reach about 60%, now that the all-favourable example assumes about that share of meat buyers (TODO.md).",
    "How much the price-insensitive shoppers like cultivated meat: most of the low-lactate example's sales go to them (research_notes/demand_checks.md section 7; TODO.md).",
    "Whether to add a nest for meat-free options, since the flat logit takes most of plant-based meat's choices from meat against about 30% measured on a menu (research_notes/demand_checks.md section 8; TODO.md).",
    "Membrane life and price are drawn separately in the bands; drawing price over life as one quantity would change every band (TODO.md).",
    "How the price response splits between dollars and the ratio to meat's price, which no data pin (`w_ratio`; TODO.md).",
]


if __name__ == "__main__":
    sys.exit(main())
