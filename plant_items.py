#!/usr/bin/env python3
"""
plant_items.py — the plant's capital as a sum of switchable items.  (Side-study; NOT used in the
headline cost. Write-up: research_notes/cheap_plant_study.md.)

Why
---
floor_physics prices the plant by CLASS: Humbird's sterile animal-cell plant ($683k per m3 of
production tank, 2018 dollars), the same without its clean room ($611k), or a plant built like a
yeast plant ($190k). The class is worth about $5 per kg of cells, more than any other single item,
and "class" hides what the money buys. This module opens it up.

What it does
------------
1. Rebuilds Humbird's fed-batch plant (24 x 20 m3; Tables 3.2, 3.3, 4.1-4.3) line by line as nine
   items, each carried through to total investment, per m3 of production tank:

       hall      the building round the bioreactors (a Class 8 clean room in his design)
       labs      cell lab and quality-control lab (Class 6)
       support   office, shop, warehouse, compressor building, slab
       vessels   production bioreactors, installed
       seed      seed-train bioreactors, installed
       medium    fill tanks, heat sterilisers, makeup tanks, filter housings
       oxygen    oxygen plant and compressor
       harvest   centrifuges
       cleaning  clean-in-place tanks, boiler, chiller, cooling tower

   The nine sum to his $327.9M (checked in tests/test_plant_items.py).

2. Rebuilds his baker's-yeast plant with the same 20 m3 tanks (Appendix A, Table A.5: 27 x 20 m3,
   $70M) on the same nine items. He gives only the total for that plant, so it is rebuilt from the
   equipment list of his standard yeast plant (Table A.1): the non-vessel equipment is resized by the
   six-tenths rule and the vessel size exponent is solved so that the total is his $70M. The exponent
   that does it, about 0.49, is an ordinary one; with 0.6 for everything the rebuild gives $56M.

3. Gives each item a short list of options (Humbird's, the yeast plant's, and what lies between),
   so any plant is a choice per item: `capital(hall="shed", oxygen="bought", ...)`.

4. Names five plants and prices their cells with floor_physics.explore:
       humbird   every item as he designed it                      ($683k per m3)
       floor     the same in a sanitary hall, no clean room         ($611k; the model's floor plant)
       lean      everything plausibly unnecessary removed           ($340k)
       yeastplus his yeast plant plus what animal cells must have:
                 cell labs, all medium sterilised, oxygen (bought)  ($180k)
       yeast     every item as in his yeast plant with 20 m3 tanks  ($130k)
   The first, second and last reproduce published or already-used figures; the two in between are new.

Every figure is 2018 dollars, $k per m3 of production tank, total investment (equipment, installation,
buildings, engineering, construction, fees and contingency) unless stated. floor_physics escalates to
today's prices.

Run
---
    python plant_items.py
"""

from __future__ import annotations

from inputs import value

ITEMS = ("hall", "labs", "support", "vessels", "seed", "medium", "oxygen", "harvest", "cleaning")
ITEM_LABELS = {
    "hall": "Hall round the bioreactors", "labs": "Cell and quality labs", "support": "Office, shop, warehouse, slab",
    "vessels": "Production tanks, installed", "seed": "Seed train", "medium": "Medium preparation and sterilising",
    "oxygen": "Oxygen supply", "harvest": "Harvest (centrifuges, filters)", "cleaning": "Cleaning system and utilities",
}
# seeds of the constrained yeast plant, m3 (Humbird Fig. A.4b): 9 x F4, 3 x F3, F2, F1
YEAST20_SEED_M3 = [19.0] * 9 + [18.5] * 3 + [18.0, 6.0]


# ----------------------------------------------------------------------------
# Humbird's cost rules
# ----------------------------------------------------------------------------
def indirect() -> float:
    """Total investment over total direct cost: engineering and construction, then fees and contingency
    (Humbird Table 4.3): 1.6 x 1.15 = 1.84."""
    return (1.0 + value("pi_engineering")) * (1.0 + value("pi_fees"))


def eq31(v_m3: float) -> float:
    """Installed cost of one sterile bioreactor, $k (Humbird Eq. 3.1)."""
    if v_m3 >= 0.33:
        return value("pi_eq31_slope") * v_m3 + value("pi_eq31_fixed")
    return value("pi_eq31_small_slope") * v_m3 + value("pi_eq31_small_fixed")


def bare(v_m3: float) -> float:
    """Bare cost of one sterile bioreactor (vessel and agitator), $k (Humbird note 127)."""
    return value("pi_bare_coef") * v_m3 ** value("pi_bare_exp")


def _allowance() -> float:
    """The 10% for minor equipment, as a multiplier on listed cost: 1 / 0.9."""
    return 1.0 / (1.0 - value("pi_missing"))


def _bioreactor_direct(installed_k: float) -> float:
    """Direct cost of bioreactors bought installed: the installed price, plus the minor-equipment
    allowance on it, which is itself installed at 1.3x (how Table 4.1's ISBL adds up)."""
    return installed_k * (1.0 + (_allowance() - 1.0) * (1.0 + value("pi_install")))


def _equipment_direct(bare_k: float) -> float:
    """Direct cost of other equipment: bare cost, the allowance, and installation at 1.3x on top."""
    return bare_k * _allowance() * (1.0 + value("pi_install"))


def _volume() -> float:
    return value("pi_n_tanks") * value("pi_tank_m3")


def _per_m3(direct_k: float) -> float:
    return direct_k * indirect() / _volume()


# ----------------------------------------------------------------------------
# The seed train
# ----------------------------------------------------------------------------
def seed_chain_k() -> float:
    """Installed cost, $k, of one chain of small seed vessels (150 L, 550 L, 2.1 m3, 8.1 m3)."""
    return sum(eq31(value(k)) for k in ("pi_seed_f0_m3", "pi_seed_f1_m3", "pi_seed_f2_m3", "pi_seed_f3_m3"))


def seed_installed_k(chains: float, f4: float) -> float:
    """Installed cost, $k, of a seed train with `chains` chains of small vessels and `f4` final seed
    vessels (15.6 m3). Humbird's fed-batch plant has 4 chains and 8 final seeds."""
    return chains * seed_chain_k() + f4 * eq31(value("pi_seed_f4_m3"))


def seed_starts_per_day(f4: float) -> float:
    """Production tanks a seed train can start per day: each final seed vessel fills three tanks every
    57 hours (Humbird Fig. 4.3 and Sect. 4.1)."""
    return f4 * value("pi_seed_tanks_per_f4") / (value("pi_stage_h") / 24.0)


def starts_needed_per_day(run_days: float, restart_days: float, hazard: float = 0.0,
                          n_tanks: float | None = None) -> float:
    """Tank starts per day a plant needs: each tank restarts after every run, and a run lasts its planned
    length or until it is lost (a constant chance `hazard` per day)."""
    import math
    n = value("pi_n_tanks") if n_tanks is None else n_tanks
    t = run_days if hazard <= 0 else (1.0 - math.exp(-hazard * run_days)) / hazard
    return n / (t + restart_days)


def final_seeds_needed(run_days: float, restart_days: float, hazard: float = 0.0) -> float:
    """Final seed vessels the 24-tank plant needs to keep up with its restarts (not rounded)."""
    return starts_needed_per_day(run_days, restart_days, hazard) / seed_starts_per_day(1.0)


def restart_queue_days(tanks_lost: float, f4: float) -> float:
    """Average extra wait, days, when `tanks_lost` tanks must be restarted at once and the seed train
    can start only so many a day: the tanks queue, and the average one waits half the queue."""
    return max(0.0, tanks_lost - 1.0) / (2.0 * seed_starts_per_day(f4))


# ----------------------------------------------------------------------------
# Humbird's two plants on the same item list
# ----------------------------------------------------------------------------
def humbird() -> dict:
    """Humbird's fed-batch animal-cell plant by item, $k per m3 of production tank (total investment)."""
    v = value
    return {
        "hall": _per_m3(v("pi_bldg_hall")),
        "labs": _per_m3(v("pi_bldg_cell_lab") + v("pi_bldg_qc_lab")),
        "support": _per_m3(v("pi_bldg_office") + v("pi_bldg_compressor") + v("pi_bldg_shop")
                           + v("pi_bldg_warehouse") + v("pi_bldg_slab")),
        "vessels": _per_m3(_bioreactor_direct(v("pi_prod_installed"))),
        "seed": _per_m3(_bioreactor_direct(v("pi_seed_installed"))),
        "medium": _per_m3(_equipment_direct(v("pi_fill_tanks") + v("pi_htst") + v("pi_makeup_tanks")
                                            + v("pi_filter_housings"))),
        "oxygen": _per_m3(_equipment_direct(v("pi_vpsa") + v("pi_o2_compressor"))),
        "harvest": _per_m3(_equipment_direct(v("pi_centrifuge"))),
        "cleaning": _per_m3(_equipment_direct(v("pi_cip_tanks") + v("pi_boiler") + v("pi_chiller")
                                              + v("pi_cooling_tower"))),
    }


def _yeast20_listed(vessel_exp: float) -> dict:
    """Bare equipment of the constrained yeast plant, $k by item, for a given vessel size exponent."""
    v = value
    e = v("pi_scale_exp")
    tank = lambda m3: v("pi_yeast_bcr_200") * (m3 / 200.0) ** vessel_exp
    return {
        "vessels": v("pi_yeast20_tanks") * tank(v("pi_tank_m3")),
        "seed": sum(tank(m3) for m3 in YEAST20_SEED_M3),
        "medium": (v("pi_yeast_pasteurizer") + v("pi_yeast_prep_tank")) * v("pi_yeast_feed_ratio") ** e,
        "oxygen": v("pi_yeast_compressors") * v("pi_yeast_oxygen_ratio") ** e,
        "harvest": (v("pi_yeast_centrifuges") * v("pi_yeast_broth_ratio") ** e
                    + v("pi_yeast_rvf") * v("pi_yeast_output_ratio") ** e),
    }


def yeast20_total_k(vessel_exp: float) -> float:
    """Total investment, $k, of the rebuilt constrained yeast plant: listed equipment, 20% for minor
    items, and Humbird's overall factor of 4.5."""
    listed = sum(_yeast20_listed(vessel_exp).values())
    return listed / (1.0 - value("pi_yeast_missing")) * value("pi_yeast_lang")


def yeast_standard_total_k() -> float:
    """Total investment, $k, of Humbird's standard yeast plant (6 x 200 m3) from his Table A.1: a check
    that the allowance and the overall factor are applied as he applies them ($68,742k)."""
    v = value
    listed = (6.0 * v("pi_yeast_bcr_200") + v("pi_yeast_seed") + v("pi_yeast_pasteurizer") + v("pi_yeast_prep_tank")
              + v("pi_yeast_compressors") + v("pi_yeast_centrifuges") + v("pi_yeast_rvf"))
    return listed / (1.0 - v("pi_yeast_missing")) * v("pi_yeast_lang")


def yeast20_vessel_exp() -> float:
    """The vessel size exponent at which the rebuilt plant costs Humbird's $70M (bisection)."""
    lo, hi = 0.2, 1.0                      # cost falls as the exponent rises (20 m3 is below 200 m3)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if yeast20_total_k(mid) > value("pi_yeast20_capex"):
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def yeast20(vessel_exp: float | None = None) -> dict:
    """Humbird's yeast plant with 20 m3 tanks by item, $k per m3 of production tank. The overall factor
    of 4.5 is split the way Table 3.1's lysine column splits it (installation, buildings and site,
    auxiliary facilities), scaled down from that column's 4.7. Buildings and site go to `hall`,
    auxiliary facilities to `cleaning`; the plant has no separate labs or support buildings."""
    v = value
    n = yeast20_vessel_exp() if vessel_exp is None else vessel_exp
    listed = _yeast20_listed(n)
    gross = 1.0 / (1.0 - v("pi_yeast_missing"))
    tpec = sum(listed.values()) * gross
    direct = v("pi_yeast_lang") / indirect()                                  # 2.45 x equipment
    k = (direct - 1.0) / (v("pi_lys_install") + v("pi_lys_buildings") + v("pi_lys_aux"))
    vol = v("pi_yeast20_tanks") * v("pi_tank_m3")
    out = {item: bare_k * gross * (1.0 + k * v("pi_lys_install")) * indirect() / vol
           for item, bare_k in listed.items()}
    out["hall"] = k * v("pi_lys_buildings") * tpec * indirect() / vol
    out["cleaning"] = k * v("pi_lys_aux") * tpec * indirect() / vol
    out["labs"] = 0.0
    out["support"] = 0.0
    return {item: out[item] for item in ITEMS}


# ----------------------------------------------------------------------------
# Options per item
# ----------------------------------------------------------------------------
def options() -> dict:
    """{item: {option: (capital $k per m3, description)}}. The first option of each item is Humbird's;
    the last is the yeast plant's."""
    v = value
    h, y = humbird(), yeast20()
    hall = v("pi_bldg_hall")
    tank_ratio = v("pi_vessel_food_k") / eq31(v("pi_tank_m3"))
    seed = lambda chains, f4: _per_m3(_bioreactor_direct(seed_installed_k(chains, f4)))
    return {
        "hall": {
            "class8": (h["hall"], "Class 8 clean room (Humbird)"),
            "sanitary": (_per_m3(hall * v("pi_rate_sanitary") / v("pi_rate_class8")), "sanitary hall, as in a food plant"),
            "shed": (_per_m3(hall * v("pi_rate_warehouse") / v("pi_rate_class8")), "plain industrial building"),
            "yeast": (y["hall"], "as in a yeast plant: mostly outdoors"),
        },
        "labs": {
            "class6": (h["labs"], "Class 6 cell and quality labs (Humbird)"),
            "yeast": (y["labs"], "none costed separately"),
        },
        "support": {
            "humbird": (h["support"], "office, shop, warehouse, slab (Humbird)"),
            "yeast": (y["support"], "none costed separately"),
        },
        "vessels": {
            "sterile": (h["vessels"], "sterile packaged stirred tanks, $1.41M each installed (Humbird)"),
            "food": (h["vessels"] * tank_ratio, "sterilisable food-grade stirred tanks at $1M each installed"),
            "yeast": (y["vessels"], "bubble columns as in a yeast plant"),
        },
        "seed": {
            "full": (h["seed"], "four trains, eight final seed tanks: a tank restarts every 57 hours (Humbird)"),
            "two": (seed(2.0, 2.0), "two small trains: enough for runs of ten days or more"),
            "one": (seed(1.0, 1.0), "one small train, no spare"),
            "yeast": (y["seed"], "as in a yeast plant"),
        },
        "medium": {
            "dedicated": (h["medium"], "a makeup tank and filters for every bioreactor (Humbird)"),
            "shared": (_per_m3(_equipment_direct(v("pi_fill_tanks") + v("pi_htst") + v("pi_filter_housings"))),
                       "shared tanks, heat sterilisers and filters; no makeup tank per bioreactor"),
            "yeast": (y["medium"], "one pasteuriser and one tank"),
        },
        "oxygen": {
            "owned": (h["oxygen"], "the plant owns an oxygen plant (Humbird)"),
            "bought": (0.0, "oxygen bought from a gas supplier"),
            "air": (y["oxygen"], "air compressors only"),
        },
        "harvest": {
            "humbird": (h["harvest"], "disk-stack centrifuges (Humbird)"),
            "yeast": (y["harvest"], "centrifuges and vacuum filters as in a yeast plant"),
        },
        "cleaning": {
            "humbird": (h["cleaning"], "clean-in-place tanks, boiler, chiller (Humbird)"),
            "yeast": (y["cleaning"], "utilities as in a yeast plant"),
        },
    }


PLANTS = {
    "humbird": {},
    "floor": {"hall": "sanitary"},
    "lean": {"hall": "shed", "vessels": "food", "seed": "two", "medium": "shared", "oxygen": "bought"},
    "yeastplus": {"hall": "yeast", "support": "yeast", "vessels": "yeast", "seed": "yeast", "medium": "shared",
                  "oxygen": "bought", "harvest": "yeast", "cleaning": "yeast"},
    "yeast": {"hall": "yeast", "labs": "yeast", "support": "yeast", "vessels": "yeast", "seed": "yeast",
              "medium": "yeast", "oxygen": "air", "harvest": "yeast", "cleaning": "yeast"},
}
PLANT_LABELS = {
    "humbird": "Humbird's plant, with clean rooms",
    "floor": "The floor's plant: sanitary hall",
    "lean": "Lean: what is plausibly unnecessary removed",
    "yeastplus": "A yeast plant plus what animal cells must have",
    "yeast": "Built like a yeast plant",
}

# What animal cells need of each step from Humbird's plant towards the yeast plant. (item, option,
# verdict, reason). Verdicts: "not needed", "probably not needed", "needed", "unknown". The evidence and
# its sources are in research_notes/cheap_plant_study.md, section 3.
STATUS = [
    ("hall", "sanitary", "not needed",
     "The clean room. Pharma's own guidance lets closed, steam-sterilised tanks stand in unclassified space; "
     "Humbird calls it 'a risk-reduction measure'; Vow runs a 20 m3 tank without one."),
    ("hall", "shed", "probably not needed",
     "A food-grade finish round closed tanks. Open steps (starting cultures, sampling) need a small clean "
     "area, which the labs provide."),
    ("hall", "yeast", "unknown",
     "Tanks outdoors. Usual for amino-acid and yeast plants; nobody has run animal cells so."),
    ("labs", "yeast", "needed",
     "The cell bank and the first seed steps are open handling of a culture that cannot outgrow anything."),
    ("vessels", "food", "probably not needed",
     "Electropolish, triple probes, pharma documentation. The tank must still be a sealed, steam-sterilised "
     "pressure vessel with sterile gas and feed lines."),
    ("vessels", "yeast", "unknown",
     "A bubble column with a yeast plant's piping. Whether animal cells can do without a stirrer, and how "
     "much sterile piping they need, is the largest unknown left."),
    ("seed", "two", "not needed",
     "Seed capacity for a restart every 57 hours. Runs of ten days or more need a fifth of it."),
    ("seed", "one", "needed",
     "A spare train. With one train a contaminated seed stops every restart."),
    ("medium", "shared", "unknown",
     "A makeup tank and filters per bioreactor. Shared lines cost less but one failure reaches every tank."),
    ("medium", "yeast", "needed",
     "Animal-cell medium is rich and neutral, so all of it must be sterilised; a pasteuriser is not enough."),
    ("oxygen", "bought", "not needed",
     "Owning the oxygen plant. Gas suppliers sell oxygen over the fence; the cost moves to running cost."),
    ("oxygen", "air", "needed",
     "Oxygen itself, at the floor's density. Air may do at the 20 to 30 g/L of today's plants."),
    ("harvest", "yeast", "needed", "Cells must be separated from the broth either way."),
    ("cleaning", "yeast", "needed", "Tanks must be cleaned and steamed between runs either way."),
]


def choices_for(plant: str = "humbird", **override) -> dict:
    """The option chosen for every item: a named plant, with any item overridden."""
    opts = options()
    c = {item: next(iter(opts[item])) for item in ITEMS}
    c.update(PLANTS[plant])
    c.update(override)
    for item, opt in c.items():
        if opt not in opts[item]:
            raise ValueError(f"unknown option {opt!r} for {item!r}; choose from {list(opts[item])}")
    return c


def capital(plant: str = "humbird", **override) -> dict:
    """Capital of a plant, $k per m3 of production tank (2018 dollars), by item and in total, and the
    running cost its choices add ($ per kg of cells: oxygen, when it is bought and not made)."""
    opts = options()
    c = choices_for(plant, **override)
    items = {item: opts[item][c[item]][0] for item in ITEMS}
    o2 = value("pi_o2_feed") * value("pi_o2_price") if c["oxygen"] == "bought" else 0.0
    return {"choices": c, "items": items, "total": sum(items.values()), "extra_opex": o2}


def bridge() -> list:
    """The steps from Humbird's animal-cell plant to his yeast plant: rows (item, Humbird, lean, yeast,
    Humbird minus yeast), $k per m3, largest gap first."""
    h, l, y = capital("humbird")["items"], capital("lean")["items"], capital("yeast")["items"]
    return sorted(((i, h[i], l[i], y[i], h[i] - y[i]) for i in ITEMS), key=lambda r: -r[4])


def vessel_without_extras_k() -> float:
    """Humbird's installed 20 m3 bioreactor without electropolishing and with single, not triple,
    probes, $k: Table 3.3's parts less the surface treatment and two thirds of an assumed probe share
    (a third of instruments and electrical), scaled to Eq. 3.1's total. A cross-check on the
    food-grade tank price, not an input."""
    v = value
    parts = (v("pi_t33_vessel") + v("pi_t33_piping") + v("pi_t33_instr") + v("pi_t33_other")
             + v("pi_t33_internals") + v("pi_t33_surface"))
    less = v("pi_t33_surface") + v("pi_t33_instr") / 3.0 * 2.0 / 3.0
    return eq31(v("pi_tank_m3")) * (parts - less) / parts


def cost_per_kg(plant: str = "humbird", **kw) -> dict:
    """Cost of cells in a named plant, with everything else as in floor_physics.explore (keyword
    arguments pass through: mode, hazard, run_days, ...). Item overrides go in `items={...}`."""
    import floor_physics as fp
    items = kw.pop("items", {})
    cap = capital(plant, **items)
    r = fp.explore(capex_2018=cap["total"], extra_opex=cap["extra_opex"], **kw)
    return {**r, "capex_2018": cap["total"]}


def main() -> None:
    h, y = humbird(), yeast20()
    n = yeast20_vessel_exp()
    print("Plant capital by item, $k per m3 of production tank (2018 dollars, total investment)\n")
    yp = capital("yeastplus")
    print(f"  {'item':<38}{'Humbird':>9}{'lean':>9}{'yeast+':>9}{'yeast':>9}{'gap':>9}")
    for item, a, l, b, gap in bridge():
        print(f"  {ITEM_LABELS[item]:<38}{a:9.1f}{l:9.1f}{yp['items'][item]:9.1f}{b:9.1f}{gap:9.1f}")
    print(f"  {'total':<38}{sum(h.values()):9.1f}{capital('lean')['total']:9.1f}{yp['total']:9.1f}{sum(y.values()):9.1f}"
          f"{sum(h.values()) - sum(y.values()):9.1f}")
    print(f"\n  Humbird's plant: ${sum(h.values()) * _volume() / 1000:.1f}M (his Table 4.3: $327.9M)")
    print(f"  yeast plant with 20 m3 tanks: vessel exponent {n:.3f} reproduces his $70M; with 0.6 throughout "
          f"${yeast20_total_k(0.6) / 1000:.1f}M")
    print(f"  one yeast-plant 20 m3 column, bare: ${value('pi_yeast_bcr_200') * 0.1 ** n:.0f}k "
          f"(Humbird's sterile tank: ${bare(20.0):.0f}k by his note 127, $330k in Table 3.3)")
    print(f"  his sterile tank without electropolish and spare probes: ${vessel_without_extras_k():.0f}k installed "
          f"(as designed ${eq31(20.0):.0f}k)")
    print("\n  Named plants, cells at the floor's settings (perfusion, mature financing), and drained and refilled:")
    for p in PLANTS:
        a, b = cost_per_kg(p), cost_per_kg(p, mode="filldraw")
        print(f"    {PLANT_LABELS[p]:<46} ${a['capex_2018']:5.0f}k/m3   ${a['total']:5.2f}/kg   ${b['total']:5.2f}/kg")
    print("\n  Seed train: final seed tanks needed by 24 production tanks (Humbird has 8):")
    for L in (2.0, 5.0, 10.0, 20.0, 33.0, 60.0):
        r = 0.4 if L <= 2.0 else 3.3
        print(f"    runs of {L:4.0f} days: {final_seeds_needed(L, r):4.1f}")


if __name__ == "__main__":
    main()
