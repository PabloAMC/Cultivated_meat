#!/usr/bin/env python3
"""
gf_doubling_bounds.py — two bounds on the cost: what growth factors must cost, and how fast an animal cell can double.

A. Growth factors. Humbird's medium holds four proteins (insulin, transferrin, FGF, TGF-beta) at fixed concentrations (g/L).
   The cost per kg of cells is litres of medium per kg x sum(concentration x price per gram). `required_prices` turns a target
   ($1, $2, $3 per kg) into a price per gram for each protein, in each scenario. `reuse` prices what a filter that returns the
   proteins saves: the permeate carries none out, so only the bleed does.
B. Doubling time. `energy_limit` asks how fast a cell can double if it burns more oxygen than West's law gives at 24 h, and
   spends all the extra on growth. `biosynthesis_atp` builds the ATP cost of a gram of cells from Humbird's composition.
   `translation_limit` asks the same of the ribosomes. `scan_doubling` prices each scenario at other doubling times with
   floor_physics.explore (the scenario's tank design held fixed).

Everything calls floor_physics.explore, floor_physics.Cells and retention.duty; nothing in them changes. Numbers: inputs.py (`gb_*`).
Evidence and probabilities: research_notes/gf_and_doubling_bounds.md.

Run
---
    python gf_doubling_bounds.py
"""
from __future__ import annotations

import math

import floor_physics as fp
import retention as R
import scenarios as S
from inputs import value, REGISTRY

SCENARIOS = ("best", "central", "cautious")
TARGETS = (1.0, 2.0, 3.0)                         # $ of growth factors per kg of cells
FACTORS = ("insulin", "transferrin", "fgf", "tgfb")
NAMES = {"insulin": "Insulin", "transferrin": "Transferrin", "fgf": "FGF", "tgfb": "TGF-beta"}
HOURS = (16.0, 20.0, 24.0, 30.0, 36.0, 43.0)       # doubling times asked for
BEYOND = (12.0, 8.0)                               # faster than any meat cell has been shown to double, for reference
LN2 = math.log(2.0)


# ----------------------------------------------------------------------------
# A. Growth factors
# ----------------------------------------------------------------------------
def conc(f: str) -> float:
    """g/L of medium."""
    return value(f"gb_conc_{f}")


def humbird_price(f: str) -> float:
    """$/g in Humbird's 2018 dollars."""
    return value(f"gb_price_{f}")


def humbird_per_litre(escalate: bool = True) -> float:
    """$/L of medium at Humbird's four prices and concentrations (2025 dollars if `escalate`)."""
    s = sum(conc(f) * humbird_price(f) for f in FACTORS)
    return s * (value("pf_opex_escalation") if escalate else 1.0)


def model_per_litre() -> float:
    """$/L the model charges for all four proteins (growth_factors = 1): pf_growth_factors over the 8.7 L/kg of Humbird's
    fed-batch (pf_medium_prep_l_kg), in 2025 dollars. The same as `humbird_per_litre()` since the back-test of 2026-11-20;
    before, the model divided by the 11.2 L/kg of his cells in perfusion and came out a quarter below."""
    return value("pf_growth_factors") * value("pf_opex_escalation") / value("pf_medium_prep_l_kg")


def shares() -> dict:
    """Each protein's share of the cost at Humbird's prices."""
    tot = sum(conc(f) * humbird_price(f) for f in FACTORS)
    return {f: conc(f) * humbird_price(f) / tot for f in FACTORS}


def scenario_litres(key: str) -> float:
    """L of medium per kg of cells in a scenario (explore's own)."""
    return S.run(S.SCENARIOS[key].choice)["medium_l"]


def required_prices(litres: float, target: float) -> dict:
    """What each protein must cost ($/g, 2025 dollars) for growth factors to cost `target` $/kg of cells at `litres` L/kg.
    'alone': this protein carries the whole budget, the other three are free.
    'shared': the budget is split as at Humbird's prices, so all four prices fall by the same factor `x_humbird` (the
    fraction of Humbird's 2025 price each must reach)."""
    allowed = target / litres                                                   # $/L of medium
    out = {"allowed_per_litre": allowed, "x_humbird": allowed / humbird_per_litre(True)}
    sh = shares()
    for f in FACTORS:
        out[f] = {"alone": allowed / conc(f), "shared": sh[f] * allowed / conc(f),
                  "humbird_2025": humbird_price(f) * value("pf_opex_escalation")}
    return out


def price_table(keys=SCENARIOS, targets=TARGETS) -> dict:
    """{scenario: {'litres', target: required_prices(...)}} using the scenario's litres."""
    out = {}
    for k in keys:
        L = scenario_litres(k)
        out[k] = {"litres": L, **{t: required_prices(L, t) for t in targets}}
    return out


def gfi_table(targets=TARGETS) -> dict:
    """The same at GFI's three medium uses (8, 13, 42 L/kg)."""
    return {L: {t: required_prices(L, t) for t in targets}
            for L in (value("gb_gfi_litres_low"), value("gb_gfi_litres_mid"), value("gb_gfi_litres_high"))}


def cost_at(litres: float, prices: dict) -> dict:
    """$/kg of cells from each protein at the given prices ($/g), and the total."""
    out = {f: litres * conc(f) * prices[f] for f in FACTORS}
    out["total"] = sum(out.values())
    return out


def market_prices() -> dict:
    """What the proteins are sold for, $/g: insulin's export price, transferrin's bulk catalogue price, FGF2 and TGF-beta
    at the research or specialist prices found."""
    return {"insulin": value("gb_mkt_insulin"), "transferrin": value("gb_mkt_transferrin"),
            "fgf": value("gb_mkt_fgf2"), "tgfb": value("gb_mkt_tgfb")}


def gaps(litres: float, target: float) -> dict:
    """Market price over the required 'shared' price, per protein: how many times too dear each is."""
    req, mkt = required_prices(litres, target), market_prices()
    return {f: mkt[f] / req[f]["shared"] for f in FACTORS}


def meat_volume_for_price(price_per_g: float, f: str, litres: float) -> dict:
    """Humbird's price-volume line (Eq. 3.4, 2018 dollars) turned round: the annual volume of protein `f` at which it falls to
    `price_per_g` (2025 dollars), and the cultivated meat that volume feeds at `litres` L/kg. {'protein_t_y', 'meat_Mt_y'}."""
    p18 = price_per_g / value("pf_opex_escalation")
    v_t = 10.0 ** ((value("gb_pv_intercept") - math.log10(p18 * 1000.0)) / value("gb_pv_slope"))            # MT/y
    meat_mt = v_t * 1e6 / (conc(f) * litres) / 1e9                                                           # Mt of cells a year
    return {"protein_t_y": v_t, "meat_Mt_y": meat_mt}


def price_at_volume(meat_mt: float, f: str, litres: float) -> float:
    """$/g (2025 dollars) of protein `f` from Eq. 3.4 when `meat_mt` Mt of cells a year are made at `litres` L/kg."""
    v_t = meat_mt * 1e9 * conc(f) * litres / 1e6
    return (10.0 ** (value("gb_pv_intercept") - value("gb_pv_slope") * math.log10(v_t)) / 1000.0
            * value("pf_opex_escalation"))


def cost_on_volume_line(meat_mt: float, litres: float) -> float:
    """$/kg of cells for all four proteins if each is priced on Humbird's volume line at `meat_mt` Mt of cells a year."""
    return sum(litres * conc(f) * price_at_volume(meat_mt, f, litres) for f in FACTORS)


def meat_volume_for_total(total: float, litres: float) -> float:
    """Mt of cells a year at which `cost_on_volume_line` falls to `total` $/kg (bisection on a log scale)."""
    lo, hi = 1e-4, 1e4
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        if cost_on_volume_line(mid, litres) > total:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


def volume_line_saving(litres_full: float, litres_kept: float) -> float:
    """Share of the growth-factor cost saved by using `litres_kept` L/kg in place of `litres_full` if prices follow the volume
    line: less protein is sold, so each gram costs more, and cost per kg goes as litres^(1 - slope)."""
    return 1.0 - (litres_kept / litres_full) ** (1.0 - value("gb_pv_slope"))


def reuse(key: str, fgf_half_life_h: float | None = None) -> dict:
    """What a filter that returns the growth factors saves in a scenario (all per kg of cells, 2025 dollars).

    The proteins are dosed per litre of fresh medium in the model. If the filter returns them, the permeate (retention.duty's
    flow) carries none out and only the bleed does: litres = 1000 / density per kilo grown (retention.duty's bleed, which since
    2026-11-20 carries the cells grown, not only those harvested) instead of all of `medium_l`. Every figure is per kilo harvested. A first fill of the tank
    adds a little. `fgf_half_life_h` lets one protein decay: FGF dosed per hour = c V (bleed rate + decay rate), so its litres
    rise to (bleed + 1000 V ln2 / (t_half x kg/h)), capped at the full medium (no saving left).
    Returns both the scenario's own growth-factor assumption and Humbird's full price."""
    ch = S.SCENARIOS[key].choice
    kw = S.explore_kwargs(ch)
    d = R.duty(kw)
    r = d["result"]
    L = r["medium_l"]
    per_l = model_per_litre()
    bleed_l = d["bleed_m3_h"] * 1000.0 / d["kg_h"]
    perm_l = d["permeate_m3_h"] * 1000.0 / d["kg_h"]
    fill_l = d["liquid_m3"] * 1000.0 / (d["kg_h"] * 24.0 * value("pf_run_days"))      # first fill, L per kg grown in a run
    sh = shares()
    if fgf_half_life_h is None:
        fgf_half_life_h = value("gb_fgf2_half_life_h")
    kd = LN2 / fgf_half_life_h
    fgf_l = min(L, bleed_l + 1000.0 * d["liquid_m3"] * kd / d["kg_h"])
    eq_l = {f: bleed_l for f in FACTORS}
    eq_l["fgf"] = fgf_l
    full = per_l * L                                                               # $/kg, all four bought, no reuse
    out = {"litres": L, "bleed_l": bleed_l, "permeate_l": perm_l, "permeate_share": perm_l / L, "fill_l": fill_l,
           "residence_h": d["liquid_m3"] / d["bleed_m3_h"], "vvd_permeate": d["vvd_permeate"], "gf_frac": kw["growth_factors"],
           "full_price": full,
           "full_reuse": per_l * (bleed_l + fill_l),
           "full_reuse_fgf_decay": per_l * (sum(sh[f] * eq_l[f] for f in FACTORS) + fill_l),
           "fgf_litres_with_decay": fgf_l}
    g = kw["growth_factors"]                                                       # the scenario's share of Humbird's price
    out["own"], out["own_reuse"], out["own_reuse_fgf_decay"] = (full * g, out["full_reuse"] * g, out["full_reuse_fgf_decay"] * g)
    out["own_saving"] = out["own"] - out["own_reuse"]
    out["full_saving"] = out["full_price"] - out["full_reuse"]
    return out


# ----------------------------------------------------------------------------
# B. How fast can an animal cell double?
# ----------------------------------------------------------------------------
def biosynthesis_atp(lipid_made: bool = True, overhead: float | None = None) -> dict:
    """ATP spent building a gram of cells from amino acids, glucose and the rest, from Humbird's composition (Table 2.1).
    mmol ATP per g of dry mass for protein, lipid, RNA/DNA and carbohydrate; the total; and per g of wet cells.
    `lipid_made`: lipid built from glucose (Humbird's Reaction 2.2); False means it is fed, and costs no ATP here."""
    ov = value("gb_biosyn_overhead") if overhead is None else overhead
    parts = {"protein": value("gb_f_protein") / value("gb_aa_g_mol") * value("gb_atp_peptide"),
             "lipid": (value("gb_f_lipid") / value("gb_lipid_g_mol") * value("gb_atp_fa16")) if lipid_made else 0.0,
             "rna_dna": value("gb_f_rna") / value("gb_nt_g_mol") * value("gb_atp_nt"),
             "carbohydrate": value("gb_f_carb") / value("gb_glycosyl_g_mol") * value("gb_atp_glycosyl")}
    parts = {k: v * 1000.0 * ov for k, v in parts.items()}                        # mmol per g dry
    dry = sum(parts.values())
    return {**parts, "dry": dry, "wet": dry * value("gb_dry_per_wet")}


def atp_supply_24h() -> float:
    """mmol ATP per g wet cells per hour at West's rate for a 24 h doubling (Cells.qo2 x ATP per O2)."""
    return fp.Cells().qo2 * value("ge_atp_per_o2")


def model_growth_atp() -> float:
    """mmol ATP per g wet cells that the model's respiration spends on growth: the (1 - upkeep share) of West's rate at 24 h,
    per gram of cells made (mu = ln2/24 h)."""
    c = fp.Cells()
    return (1.0 - c.maintenance_share) * atp_supply_24h() / c.mu


def implied_upkeep_share(growth_atp: float) -> float:
    """The upkeep share of West's 24 h respiration that leaves `growth_atp` mmol ATP per g wet for growth."""
    return min(1.0, max(0.0, 1.0 - growth_atp * fp.Cells().mu / atp_supply_24h()))


def energy_limit(scope: float | None = None, growth_atp: float | None = None) -> dict:
    """The fastest doubling the energy budget allows.
    A cell can burn `scope` times West's oxygen rate at 24 h (`gb_resp_scope`). Upkeep stays what it was; everything above it
    goes to growth at `growth_atp` mmol ATP per g wet (default: the bottom-up cost). So
        mu_max = mu_24 + (scope - 1) x P_24 / growth_atp.
    Returns the doubling time (h), the growth rate, the upkeep share this implies and the oxygen uptake at that speed."""
    k = value("gb_resp_scope") if scope is None else scope
    a = biosynthesis_atp()["wet"] if growth_atp is None else growth_atp
    c = fp.Cells()
    p24 = atp_supply_24h()
    mu = c.mu + (k - 1.0) * p24 / a
    return {"scope": k, "growth_atp": a, "upkeep_share": implied_upkeep_share(a), "mu": mu, "doubling_h": LN2 / mu,
            "qo2": k * c.qo2}


def model_energy_limit(scope: float | None = None) -> dict:
    """The same with the model's own growth cost (pf_maintenance_share), through Cells.qo2: the doubling time at which the
    oxygen uptake of floor_physics.Cells reaches `scope` x its 24 h value."""
    k = value("gb_resp_scope") if scope is None else scope
    c = fp.Cells()
    m = c.maintenance_share
    h = c.doubling_h * (1.0 - m) / (k - m)
    return {"scope": k, "growth_atp": model_growth_atp(), "upkeep_share": m, "doubling_h": h,
            "qo2": fp.Cells(doubling_h=h).qo2}


def cho_check() -> dict:
    """Does the model's oxygen uptake at a CHO cell's doubling time match what CHO cells burn? Measured: pmol/cell/h over the
    cell's wet mass, mmol/g/h. Model: Cells.qo2 at the same doubling time."""
    m = value("gb_cho_mass_pg") * 1e-3                                          # ng per cell; 1 pmol / 1 ng = 1 mmol / g
    reg = REGISTRY["gb_cho_qo2_pmol_h"]
    return {"measured": value("gb_cho_qo2_pmol_h") / m,
            "measured_lo": reg.lo / m, "measured_hi": reg.hi / m,
            "model": fp.Cells(doubling_h=value("gb_cho_doubling_h")).qo2}


def translation_limit(rna_share: float | None = None, elongation: float | None = None) -> dict:
    """The fastest doubling the ribosomes allow: each adds `elongation` amino acids a second, and the ribosomes' share of
    dry mass is set by the RNA content (rRNA is 80% of RNA and 65% of a ribosome's mass). Protein must double with the cell:
        mu = (aa/s x 3600 x aa mass / ribosome mass) x ribosome share of dry mass / protein share of dry mass."""
    rna = value("gb_f_rna") if rna_share is None else rna_share
    el = value("gb_elong_aa_s") if elongation is None else elongation
    f_r = rna * value("gb_rrna_in_rna") / value("gb_rrna_in_ribosome")
    per_h = el * 3600.0 * value("gb_aa_g_mol") / (value("gb_ribosome_kda") * 1000.0)       # protein made per ribosome mass, per hour
    mu = per_h * f_r / value("gb_f_protein")
    return {"rna_share": rna, "ribosome_share": f_r, "elongation": el, "mu": mu, "doubling_h": LN2 / mu}


def rna_share_for(doubling_h: float, elongation: float | None = None) -> float:
    """RNA share of dry mass the ribosomes need for a given doubling time (inverse of `translation_limit`)."""
    base = translation_limit(rna_share=1.0, elongation=elongation)["mu"]            # mu at an RNA share of 1.0
    return (LN2 / doubling_h) / base


def scan_doubling(key: str, hours=HOURS) -> dict:
    """explore() for a scenario at other doubling times, its tank design held fixed. {hours: result}.
    The tank, column and cells are held; since 2026-11-25 the engine picks the gas flow (up to the cap) and thins an overloaded
    column loop at each doubling time, as a plant would."""
    choice = S.SCENARIOS[key].choice
    return {h: S.run(choice, doubling_h=h) for h in hours}


# ----------------------------------------------------------------------------
def summarise() -> None:
    f = value
    print("A. Growth factors")
    print(f"   $/L at Humbird's prices (2025 $): {humbird_per_litre():.4f}   the model's own: {model_per_litre():.4f}   "
          f"ratio {model_per_litre() / humbird_per_litre():.2f}")
    print("   shares at Humbird's prices: " + ", ".join(f"{NAMES[x]} {s:.1%}" for x, s in shares().items()))
    for k, t in price_table().items():
        print(f"   {k}: {t['litres']:.2f} L/kg")
        for T in TARGETS:
            r = t[T]
            row = "  ".join(f"{NAMES[x]} {r[x]['shared']:>9.2f} ({r[x]['alone']:>9.2f})" for x in FACTORS)
            print(f"     ${T:.0f}/kg: {row}   x{r['x_humbird']:.3f} of Humbird's price")
    print("   GFI litres:")
    for L, t in gfi_table().items():
        print(f"     {L:.0f} L/kg  $1/kg: " + "  ".join(f"{NAMES[x]} {t[1.0][x]['shared']:.2f}" for x in FACTORS))
    for k in SCENARIOS:
        r = reuse(k)
        print(f"   reuse {k}: {r['litres']:.1f} L/kg, bleed {r['bleed_l']:.2f}, permeate {r['permeate_l']:.2f} "
              f"({r['permeate_share']:.0%}); full price ${r['full_price']:.2f} -> ${r['full_reuse']:.2f} "
              f"(FGF decays: ${r['full_reuse_fgf_decay']:.2f}); scenario's own ${r['own']:.2f} -> ${r['own_reuse']:.2f}")
    for k in ("central",):
        L = scenario_litres(k)
        r = reuse(k)
        print(f"   on Humbird's volume line ({k}, {L:.0f} L/kg): $1/kg at {meat_volume_for_total(1.0, L):.2f} Mt of cells a year, "
              f"$3/kg at {meat_volume_for_total(3.0, L):.2f}; the scenario's own ${r['own']:.2f} at {meat_volume_for_total(r['own'], L):.2f}; "
              f"reuse saves {volume_line_saving(L, r['bleed_l'] + r['fill_l']):.0%} on that line, "
              f"{1 - (r['bleed_l'] + r['fill_l']) / L:.0%} at a fixed price")
    print("B. Doubling time")
    b = biosynthesis_atp()
    print(f"   ATP to build 1 g: {b['dry']:.1f} mmol/g dry, {b['wet']:.1f} mmol/g wet "
          f"(protein {b['protein']:.1f}, lipid {b['lipid']:.1f}, RNA {b['rna_dna']:.1f}, carbohydrate {b['carbohydrate']:.1f}); "
          f"fed lipid: {biosynthesis_atp(lipid_made=False)['wet']:.1f}; model's own: {model_growth_atp():.1f}")
    print(f"   West's rate at 24 h: {atp_supply_24h():.3f} mmol ATP/g/h; implied upkeep share {implied_upkeep_share(b['wet']):.2f}")
    for k in (1.5, 2.0, 3.0):
        e, m = energy_limit(k), model_energy_limit(k)
        print(f"   {k:.1f}x respiration: {e['doubling_h']:.1f} h (bottom-up), {m['doubling_h']:.1f} h (model's split)")
    t = translation_limit()
    print(f"   ribosomes at {t['elongation']} aa/s and RNA {t['rna_share']:.0%}: {t['doubling_h']:.1f} h; "
          f"8 h needs RNA {rna_share_for(8.0):.1%}, 12 h {rna_share_for(12.0):.1%}")
    c = cho_check()
    print(f"   CHO oxygen: measured {c['measured_lo']:.2f}-{c['measured_hi']:.2f}, model at 15 h {c['model']:.2f} mmol/g/h")
    for k in SCENARIOS:
        sc = scan_doubling(k, HOURS + BEYOND)
        print(f"   {k}: " + "  ".join(f"{h:.0f}h ${r['total']:.2f}" for h, r in sc.items()))


if __name__ == "__main__":
    summarise()
