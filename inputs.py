#!/usr/bin/env python3
"""
inputs.py — the ONE place every concrete number in the model lives, with its
source and (where it is uncertain) its Monte-Carlo range.

Why this file exists
--------------------
The model's whole credibility rests on every number being honest and sourced.
Before this file, a number like the medium price lived as a point default in
cost_model (`media_price = 0.50`) AND as an independent prior in uncertainty.py
(`("triangular", 0.20, 1.00, 0.50, ...)`) — two unconnected facts that could
silently drift apart. Here each input is a SINGLE record carrying both facets:

    Input(value=0.50, unit="$/L", source="SuperMeat 2024: '<$0.5 per liter'",
          lo=0.20, hi=1.00, mode=0.50, note="company figures; none verified at scale")

  * `value`            -> the point/base-case default the dataclasses use.
  * `lo, mode, hi`     -> the triangular Monte-Carlo prior uncertainty.py samples.
  * `unit, source, note` -> provenance, so the datasheet is self-documenting.

So the point estimate and the uncertainty band can never diverge: change the
number here and every rung follows.

Reference it
------------
    python inputs.py            # prints the full datasheet (every number + source)

    from inputs import value, prior, REGISTRY
    value("media_price")        # -> 0.50
    prior("media_price")        # -> ("triangular", 0.20, 1.00, 0.50, "<note>")

Every number here is real and sourced. The model has no placeholder mechanism
that a later rung substitutes, so there are no "fake" values to keep out — the
price_ratio module takes a cost as input rather than inventing a cost curve.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Input:
    """One concrete model input: its base value, optional MC prior, and source."""
    value: float                  # point / base-case default
    unit: str
    source: str                   # short provenance tag
    lo: float | None = None       # MC prior low  (None -> not sampled / fixed)
    hi: float | None = None       # MC prior high
    mode: float | None = None     # MC prior mode (defaults to `value` if omitted)
    kind: str = "triangular"      # MC prior distribution
    note: str = ""                # one-line justification / caveat

    @property
    def has_prior(self) -> bool:
        return self.lo is not None and self.hi is not None

    @property
    def prior_mode(self) -> float:
        return self.value if self.mode is None else self.mode


# ----------------------------------------------------------------------------
# THE REGISTRY  (grouped by where in the ladder the number is used)
# Tags: [Pasitka] empirical TEA (Nature Food 5, 693-702, 2024) · [Believer] company announcements, read 2026-11-03 · [Humbird] TEA
#       (Biotechnol. Bioeng. 118, 3239-3250, 2021) · [GFI] GFI 2025 State-of-the-
#       Industry / medium-cost analysis (company self-reports) · [GFI25] GFI & Hawkwood
#       2025 fermentation cost report (glucose price) · [Gu25-qual] Gu et al.
#       2025 scaffolds review (Compr. Rev. Food Sci. Food Saf. 24, e70221) — materials
#       only, NO cost figure · [market] observed retail price · [scanner] meat/plant-
#       based own-price elasticity (Andreyeva 2010; Gallet 2010/2012) · [assumed] our
#       judgement · [calibration] fixes a model coefficient
#
# Sourcing discipline (2026-11-14): costs are per kg of real wet cells. The default stack is what a
# company reports for its own process ([SuperMeat] 2024, not peer reviewed). The floor comes from
# physics and published plant costs (floor_physics.py: Humbird's long report for cell physics and
# plant capital, pf-tea for built fermentation plants). Pasitka et al. 2024 is NOT an anchor: its
# kilogram is a wet pellet that is mostly liquid and its cost leaves out capital (METHODS.md).
# ----------------------------------------------------------------------------
REGISTRY: dict[str, Input] = {

    # --- shared across rungs ------------------------------------------------
    "markup_add": Input(5.0, "$/kg", "[assumed] additive biomass->retail spread, roughly "
        "fixed $/kg (does NOT shrink as biomass falls). Anchored to conventional meat's "
        "farm-to-retail margin: USDA price-spread data put ground-beef processing+retail at "
        "very roughly $3-6/kg.",
        lo=2.0, hi=7.0, mode=5.0,
        note="PIVOTAL: with p_conv this sets the parity threshold (p_conv - markup_add). The lower "
             "bound is $2 (not the conventional ~$4) because cultivated SKIPS slaughter / evisceration "
             "/ carcass breakdown — a real chunk of conventional's farm-to-retail wedge — so its retail "
             "markup can sit slightly BELOW conventional's; mode stays $5 (typical), $7 = markup-heavy. "
             "The most leverage of any single number; at the $2 floor parity becomes reachable in the "
             "optimistic cost corner."),
    "p_conv": Input(12.0, "$/kg", "[market] conventional commodity meat price (~$10-15/kg)",
        lo=10.0, hi=14.0, mode=12.0,
        note="PIVOTAL: co-sets the parity threshold with markup_add (a meat tax enters here)."),
    "years": Input(30, "years", "[assumed] analysis horizon"),

    # --- Rung 2: cost model ----------------------------------------------------
    # ALL COSTS ARE PER KG OF REAL WET CELLS (about 70% water, 20% protein: comparable with meat).
    # RE-ANCHORED 2026-11-14. The default used to be Pasitka et al. 2024. That paper's kilogram is a wet
    # pellet that is mostly liquid and its cost leaves out capital (METHODS.md, "Why Pasitka is not the
    # anchor"), so it is no longer used. The default is now what a company reports for its own process
    # (SuperMeat 2024: 100% cell mass, cell wet weight 1.0-1.75 ng, 10 L runs scaled on paper to 25 m3);
    # the floor comes from physics (floor_physics.py). [SuperMeat] = "Cultivating the Future: A Deep Dive
    # Into Cost-Effective Cultivated Meat Production" (Nov 2024, company report, not peer reviewed), read
    # 2026-11-14.
    "media_intensity": Input(30.5, "L/kg wet", "[SuperMeat] 'Media Usage: 92,772K liters per year' for 6.7 million "
        "lb (3,039 t) of 100% cultivated chicken: 92.77e6 L / 3.039e6 kg",
        note="fixed; the efficiency multiplier carries the uncertainty. For scale: Humbird's efficient-cell "
             "designs need about 8 L/kg"),
    "media_price": Input(0.50, "$/L", "[SuperMeat] 'Media Cost and Usage: <$0.5 per liter', chemically defined "
        "medium",
        lo=0.20, hi=1.00, mode=0.50,
        note="lo=0.20: [GFI26] 'several companies announced media costs at $0.20/L or below in 2025' (p.8), "
             "the amino-acid portion supported by GFI/MG Consulting (p.30), full medium cost unverified. "
             "hi=1.00: a process that has not reached these prices; Pasitka et al. 2024 measured $0.63/L for "
             "an animal-free medium and $3.31/L before removing albumin. All are company or single-lab "
             "figures; none is verified at production scale"),
    "efficiency": Input(1.0, "x media-use", "[SuperMeat] cells as reported (1.0)",
        lo=0.25, hi=1.00, mode=1.00,
        note="media-VOLUME multiplier; centred on the reported process (mode=1.0). 0.25 = about 8 L/kg, the "
             "medium use of Humbird's efficient-cell designs: an OPTIMISTIC tail, not demonstrated for meat "
             "cells, so better efficiency is upside, never assumed."),
    "overhead": Input(19.1, "$/kg", "[SuperMeat, capital restated] everything except medium. Running costs as the "
        "company reports them, $10.8/kg ($11.8/lb 'without depreciation' = $26.0/kg, less 30.5 L x $0.50 of "
        "medium), plus a full yearly charge on the plant, $8.3/kg",
        lo=9.8, hi=34.0, mode=19.1,
        note="THE PLANT knob. CAPITAL: the report gives depreciation of $1.6/lb ($3.5/kg) but neither the plant's "
             "cost nor the depreciation period. Assuming straight-line over 10 years (Humbird's plant life), the "
             "plant costs $35 per kg of yearly output, and at the 23.6%-a-year charge used for every other case "
             "(humbird_plant_charge) that is $8.3/kg. Over 20 years it would be $16.7/kg. The company's own "
             "figure with depreciation only is $29.5/kg in all; this default is $34.3. CAUTION: the report's "
             "stated tank volumes, densities and bleed rate reproduce about half its stated output, so its "
             "plant cost per kg cannot be checked. lo=9.8 = the plant floor (floor_physics: no clean rooms, "
             "perfusion, efficient cells). hi=34 = the cautious case with cells at half the density "
             "(floor_physics: pharma-style plant, tanks drained and refilled, 60 g/L). PIVOTAL: with the "
             "medium price, the top driver of R."),

    # --- Rung 2: the irreducible FLOOR --------------------------------------
    "aa_intensity": Input(0.337, "kg hydrolysate/kg wet", "[Humbird] Table 3.5: soy hydrolysate "
        "needed to supply Reaction 2.11's amino acids (0.26 kg/kg of pure amino acids, Table 3.4; "
        "more hydrolysate because its amino-acid profile does not match the cells')",
        note="stoichiometric -> does NOT scale with media efficiency. Humbird adds free glutamine "
             "(0.044 kg/kg, $1.74) and tyrosine (0.009 kg/kg, $0.88) supplements; the floor leaves "
             "them out, assuming cells that make their own glutamine (glutamine-synthetase lines, "
             "as in CHO) and tyrosine covered by the hydrolysate"),
    "aa_bulk_price": Input(2.0, "$/kg", "[Humbird] bulk plant hydrolysate (cuts $15-16/kg)"),
    "glucose_intensity": Input(0.32, "kg/kg wet", "[Humbird] glucose at full respiration: Table "
        "2.3 gives 0.13 mol per mol DCMa (vs 0.147 for Reaction 2.11 = 0.362 kg/kg wet, Table 3.4), "
        "so 0.13/0.147 x 0.362 = 0.32",
        note="anabolic glucose (lipid, carbohydrate, nucleotides: 0.065 mol, Reaction 2.6) + glucose "
             "respired to pay the cell's metabolic power over its growth (mu = 0.029/h). No lactate; "
             "faster growth lowers it, toward 0.16 kg/kg (anabolic only)"),
    "glucose_price": Input(0.40, "$/kg", "[GFI25] US Midwest DE95 glucose, GFI & Hawkwood 2025 "
        "(Driving down costs of fermentation-derived ingredients, Table 6: $0.35-0.56)",
        note="Humbird quotes ~$0.25-0.26/kg contract prices"),
    "other_nutrients_floor": Input(0.9, "$/kg", "[assumed] mineral salts, buffer, vitamins and "
        "trace elements at the floor",
        note="the remainder of the earlier $1 'glucose and other nutrients' assumption. Humbird "
             "leaves buffers and mineral salts out of his medium cost as low-cost (his footnote 26), "
             "so this leans conservative"),
    "plant_floor": Input(9.8, "$/kg", "[floor_physics] plant cost per kg of real cells if everything that has "
        "been costed for animal cells works together, financed like a mature food industry: a sterile plant "
        "without clean rooms ($810k per m3 in 2025 prices) plus a hoped-for device to hold cells back ($89k per "
        "m3), 20 m3 tanks in perfusion at the density CO2 removal allows (120 g/L), efficient 3 ng cells, 91% "
        "uptime: capital, maintenance and insurance $7.1 + labour $1.2 + utilities and consumables $1.5",
        note="THE FLOOR'S PLANT TERM (2026-11-14). Each element is allowed by physics and claimed or shown "
             "somewhere, never together: food-grade 20 m3 tanks run today (Vow); perfusion above 100 g/L is "
             "shown at 10 L (SuperMeat, Pasitka); a way to hold cells back at 20 m3 is not shown; efficient "
             "cells are not shown; 91% uptime is Humbird's figure, which he calls 'rather aggressive'. "
             "FINANCING: the yearly charge is plant_charge_mature (17.3%), because the floor is a long-run "
             "case compared with meat, a mature industry; at the first-plant rate (23.6%) this term is $12.4. "
             "tests/test_floor_physics.py ties this value to the module"),
    "plant_floor_lo": Input(4.9, "$/kg", "[floor_physics] THE FRONTIER: the same case in a plant that costs what "
        "microbial fermentation plants cost today ($190k per m3: Liberation Labs, Quorn), at the same financing",
        note="such plants exist, for microbes, with 150 m3 vessels. Nobody has costed or built one for "
             "animal cells, whose cultures are far easier to contaminate. $5.7 at the first-plant rate"),
    "plant_floor_hi": Input(17.7, "$/kg", "[floor_physics] the cautious case: Humbird's sterile pharma-style plant "
        "($908k per m3), tanks half-drained and refilled with no cell retention, 85% uptime, at his first-plant "
        "financing (23.6% a year)"),
    "plant_charge_mature": Input(0.173, "of TCI per yr", "[Humbird-R, derived] the yearly charge on a plant financed "
        "like a mature food industry: capital recovery at i = 5.4% over n = 20 years (8.3%) plus his 4% "
        "maintenance and 5% insurance",
        lo=0.123, hi=0.236, mode=0.173,
        note="GROUNDING, all from Humbird's report: Sect. 3.1 gives the 2019 cost of capital of the food "
             "processing sector as 5.4% (against 8.5% for pharma and biotech, and the 7.5% of Beyond Meat that "
             "he adopts); his baker's-yeast benchmark (Appendix A) uses a 20-year plant life, where his "
             "cultivated-meat plants use 10. CCF = i / (1 - (1 + i)^-n) = 0.083. Maintenance and insurance are "
             "kept at his 4% and 5%, which he also applies to the yeast plant. Used for the floor and the "
             "frontier, which are long-run cases set against meat; the default and the cautious cases keep the "
             "first-plant rate (humbird_plant_charge). lo: CE Delft 2021's 30-year payback with no return "
             "(3.3% + 9%). hi: the first-plant rate"),
    "humbird_plant_cost": Input(14.5, "$/kg", "[Humbird] Table 4.7, fed-batch on hydrolysate (enhanced "
        "metabolism): consumables 0.81 + utilities 0.93 + labour 1.42 + bioreactor, building and rest-of-plant "
        "capital 3.56 + 3.11 + 4.66 = $14.5/kg wet",
        note="CROSS-CHECK ONLY, not used in the cost: Humbird's independent estimate of the non-nutrient cost "
             "of his most favourable design, in 2018 prices ($18.9 in 2025 prices). The default overhead "
             "(19.1) is about the same; the floor (9.8) assumes a plant without clean rooms run in perfusion"),
    # --- cost cross-checks (shown on the page's reality checks; NOT used in the cost) -----------
    # Read in Humbird 2021's journal version (Biotechnol Bioeng 118:3239; Europe PMC PMC8362201) on 2026-11-03.
    "humbird_tci_fedbatch": Input(328e6, "$", "[Humbird] Table 2: 'Total capital investment | $328M' (fed-batch, "
        "649 m3 of bioreactors)", note="CROSS-CHECK ONLY"),
    "humbird_output_fedbatch": Input(6.8e6, "kg wet/yr", "[Humbird] Table 2: 'Production rate (kTA) | 6.8' (fed-batch)",
        note="CROSS-CHECK ONLY"),
    "humbird_plant_charge": Input(0.236, "of TCI per yr", "[Humbird] Tables 4.3 and 4.10: 'Annual capital charge "
        "14.6% TCI/y' (i = 7.5%, n = 10 yr; his text rounds it to 15%); Sect. 2.5: '4% TCI/y for maintenance "
        "(including CIP) and 5% TCI/y for insurance'. 0.146 + 0.04 + 0.05 = 0.236 (derived)",
        note="Used by floor_physics for every plant case and for the default's capital. Humbird's 'CAPEX' lines "
             "in Table 2 ($4 + $3 + $5 = $12/kg fed-batch) are this 23.6%/yr of TCI per kg (0.236 x 328M / "
             "6.8M kg = $11.4/kg)"),
    "believer_capex": Input(123.35e6, "$", "[Believer] 'initial planned investment of $123.35m' for the Wilson, NC "
        "plant (FoodNavigator, 8 Dec 2022); 'an initial investment of more than $123 million' (NC Governor's office, "
        "7 Dec 2022)", note="CROSS-CHECK ONLY. An initial figure, announced at groundbreaking; the final cost of the "
        "plant (completed 2025) is not public"),
    "believer_capacity": Input(10e6, "kg/yr", "[Believer] 'the capacity to produce at least 10,000 metric tons of "
        "cultivated meat (around 22 million lbs) per year' (FoodNavigator, 8 Dec 2022)",
        note="CROSS-CHECK ONLY. A company claim (Believer Meats, whose scientists co-authored Pasitka 2024). The plant "
             "was completed in 2025, but the company became defunct before producing at scale and its assets went "
             "to sale (Just Food, 2026: 'defunct peer Believer Meats', BDO Consulting managing the sale)"),
    "eff_best": Input(0.25, "x media-use", "[assumed] efficient-cell media-volume multiplier "
        "(~4x less medium than reported: about 8 L/kg, as in Humbird's designs)",
        note="drives the efficient-cell SCENARIO, not the floor"),
    "cleanroom_cost": Input(1.6, "$/kg", "[Humbird-R, derived] the clean-room premium in his fed-batch design: the "
        "cell-culture hall as a Class 8 clean room ($39.6M) against a sanitary hall ($20.9M), x 1.84 to total "
        "investment, x 23.6% a year over 6.8 kt, in 2025 prices",
        note="OPTIONAL adder, OFF by default. An earlier value ($3.0) was Humbird's whole buildings line (Table "
             "4.7), not the premium. The default's source does not say what class of building it assumes"),

    # --- Rung 2 side-study: doubling-time envelope (growth_rate.py; NOT used in the cost) ------
    # Every number here is OUR JUDGEMENT, not a measurement: no public series gives these rates for
    # meat cells. They bound a what-if (does growing slower ever pay?), they do not feed the headline.
    "gr_tau_ref": Input(24.0, "h", "[assumed] doubling time of the base process",
        note="fixed; the envelope depends only on the RATIO tau/tau_ref, so this sets the axis, not the result"),
    "gr_time_share": Input(0.8, "of overhead", "[assumed] share of the non-medium cost that scales with "
        "vessel-time per kg (capital, labour, utilities, maintenance)",
        lo=0.5, hi=1.0, mode=0.8,
        note="a fixed plant makes kg in proportion to growth rate, so its fixed costs per kg scale with "
             "doubling time. Cross-check: in Humbird's Table 4.7 only consumables ($0.81 of $14.5/kg) do "
             "not; lo=0.5 allows a fed-batch cycle with a large turnaround share"),
    "gr_tau_star": Input(48.0, "h", "[assumed] doubling time at which overflow (lactate) production stops, "
        "threshold case", lo=30.0, hi=96.0, mode=48.0,
        note="unknown for meat cells. The CHO chemostat series the proposal cites were read as abstracts only"),
    "gr_bp_time_share": Input(0.2, "of by-product", "[assumed] share of the binding by-product at tau_ref that "
        "is made per unit TIME, not per unit growth", lo=0.0, hi=0.5, mode=0.2,
        note="glutamine breaks down to ammonia in warm medium whether or not cells grow; maintenance "
             "metabolism also makes lactate. This part rises per kg when growth slows"),
    "gr_next_level": Input(0.6, "x volume", "[assumed] the volume the NEXT limit would demand at tau_ref, "
        "as a share of the volume the binding limit demands", lo=0.25, hi=1.0, mode=0.6,
        note="relieving the binding limit cannot cut volume below the next one. lo=0.25 is eff_best "
             "(CHO-grade); hi=1.0 means two limits bind together. growth_rate.py's rough check puts "
             "lactate, ammonia and amino-acid supply within a factor of a few"),
    "gr_nut_time_share": Input(0.3, "of nutrient need", "[assumed] share of the nutrient-supply need at "
        "tau_ref that scales with time (maintenance energy, growth-factor decay)",
        lo=0.1, hi=0.6, mode=0.3,
        note="Humbird's glucose is about half maintenance (see glucose_intensity); amino acids are mostly "
             "built into biomass; growth factors decay with time alone"),
    "gr_death_rate": Input(0.002, "1/h", "[assumed] cell death rate, constant", lo=0.0, hi=0.005, mode=0.002,
        note="dead cells must be regrown, so growth-coupled needs per NET kg rise as growth slows. A constant "
             "rate understates Hayter 1993's finding that death rises at low growth rate (abstract only)"),

    # --- Rung 2 side-study: physics-based floor (floor_physics.py; NOT used in the headline cost) -----
    # Per kg of REAL wet cells (70% water, ~21% protein: Humbird's basis). [Humbird-R] = Humbird's long report
    # (engrXiv, rev. 3, Oct 2021), read 2026-11-14. [pf-tea] = evidence recorded in the pf-tea repository
    # (data/evidence/*.yaml, docs/VALIDATION.md), taken as recorded there and not re-read at source.
    "pf_capex_escalation": Input(1.33, "x", "[pf-tea] CEPCI 2024 (~800, an estimate) over 2018 (603.1): plant "
        "construction costs since Humbird's price basis", lo=1.17, hi=1.40, mode=1.33,
        note="Humbird's costs are in 2018 dollars (his Table 3.2 and equipment captions say '2018$'). lo: CEPCI "
             "2021 over 2018 (708.8 / 603.1); hi: a further 5% for 2025-26. Applied to the Humbird-based capital "
             "per m3 in floor_physics, not to figures that are already recent"),
    "pf_opex_escalation": Input(1.28, "x", "[pf-tea] US CPI-U 2025 (321.9) over 2018 (251.1): labour, utilities, "
        "consumables and growth factors since Humbird's price basis"),
    "pf_cell_mass_pg": Input(3000.0, "pg wet", "[Humbird-R] Sect. 2.1 model cell: 3,000 pg hydrated, 17.7 um"),
    "pf_cell_mass_small_pg": Input(550.0, "pg wet", "[Pasitka, derived] 10 um measured diameter (Extended Data "
        "Fig. 4b) as a sphere at 1.05 g/mL", note="Pasitka's own biomass figures use 10 ng per cell; see METHODS "
        "'Wet mass per cell'"),
    "pf_doubling_h": Input(24.0, "h", "[Humbird-R] mu_max = 0.029/h"),
    "pf_doubling_slow_h": Input(61.0, "h", "[Pasitka] 'Culture doubling time was relatively stable at 61 h' in "
        "the animal-free 20-day run"),
    "pf_power_coef": Input(0.148, "pW/pg^0.75", "[Humbird-R] Eq. 2.8 (West et al.): metabolic power per cell = "
        "0.148 x M^0.75; 60 pW at 3,000 pg"),
    "pf_heat_per_o2": Input(483.0, "kJ/mol O2", "[Humbird-R] Reaction 2.10 (enhanced catabolism): 2,225 kJ per "
        "4.61 mol O2", note="full respiration of glucose gives 467; wild-type Reaction 2.7 gives 532"),
    "pf_x_visc": Input(258.0, "g wet/L", "[Humbird-R] Table 2.2: density at volume fraction 0.25, the viscosity limit"),
    "pf_x_unperfused": Input(120.0, "g wet/L", "[Humbird-R] Fig. 2.8b: fed-batch limit at 20 m3 with 90% O2 and "
        "enhanced metabolism (ammonia and CO2 bind together)", lo=50.0, hi=150.0, mode=120.0,
        note="applies to any culture whose waste is not washed out: fed-batch, fill-and-draw, chemostat"),
    "pf_x_co2_20m3": Input(120.0, "g wet/L", "[Humbird-R] Sect. 2.3: at 20 m3 the CO2 limit falls at about 120 g/L "
        "(40e6 cells/mL); 'At larger volume, the pCO2 limit is incurred'",
        note="the density a 20 m3 tank can hold even when waste is washed out by perfusion. Small tanks are "
             "oxygen-limited instead (195 g/L at 2 m3)"),
    "pf_otr_cap": Input(29.0, "mmol O2/L/h", "[Humbird-R] oxygen-limited density of 195 g/L in perfusion with 90% "
        "O2 x the model cell's uptake", lo=13.0, hi=50.0, mode=29.0,
        note="lo: Negulescu 2023's designs (12.8-13.5); Humbird: '<~25' with air under cell-culture sparging "
             "limits; hi: '<50' for animal cells [pf-tea, engineering.yaml, citing Humbird 2021]. Microbial "
             "fermenters reach 150-200, but bursting bubbles kill animal cells"),
    "pf_working_volume": Input(0.8, "of vessel", "[Humbird-R] 80% maximum working volume"),
    "pf_uptime": Input(0.91, "of year", "[Humbird-R] Sect. 4.2: 'average annual uptime ... ~91%' for perfusion"),
    "pf_uptime_realistic": Input(0.85, "of year", "[assumed] share of the year a continuously run tank produces, "
        "with restarts and failed runs", lo=0.75, hi=0.91, mode=0.85,
        note="Humbird's 0.91 assumes 33-day runs, a 3-day restart and no failures. Our research pass (reports/"
             "'Continuous harvest bioreactor progress', 2026-11-14) puts 0.75-0.80 on today's failure rates "
             "(about 11% of batches lost in cultivated meat, about 3% in pharma); 0.85 is a floor-case judgement"),
    "pf_draw_fraction": Input(0.5, "of tank", "[assumed] share of the tank drained at each harvest in fill-and-draw",
        lo=0.3, hi=0.8, mode=0.5,
        note="output relative to (density cap x maximum growth rate) is f / ln(1/(1-f)): 0.84 at 0.3, 0.72 at 0.5, "
             "0.50 at 0.8, because the culture spends each cycle climbing back to the cap. Patents describe draws "
             "of up to 80%"),
    "pf_turnaround_h": Input(10.0, "h", "[Humbird-R] Sect. 4.2: 10 h offline per turnaround for cleaning and refill"),
    "pf_fedbatch_doublings": Input(2.0, "doublings", "[Humbird-R] Fig. 4.3: production batch grows 482 -> 1,849 kg "
        "(1.9 doublings); seed splits of 2-3 doublings are the recommended range"),
    "pf_capex_aseptic_fedbatch": Input(683.0, "$k/m3", "[Humbird-R] Tables 4.1 and 4.3: TCI $327.9M for 24 x 20 m3 "
        "production vessels (480 m3), seed train, buildings and utilities included"),
    "pf_capex_aseptic_perfusion": Input(3450.0, "$k/m3", "[Humbird-R] Tables 4.8 and 4.10: TCI $662.6M for 96 x 2 m3 "
        "production vessels (192 m3) with 192 ATF units"),
    "pf_capex_pasitka_large": Input(810.0, "$k/m3", "[Pasitka] SI Tables S1 and S4: TCI $40.3M for 2 x 25 m3",
        note="perfusion with an unspecified retention device at a scale nobody has run; see METHODS "
             "'Reactor type and mode'"),
    "pf_capex_no_cleanroom": Input(611.0, "$k/m3", "[Humbird-R, derived] his fed-batch plant with the clean room "
        "replaced by a sanitary hall: Table 4.2 prices the cell-culture hall (5,268 m2 on 2 levels) at $39.6M as a "
        "Class 8 clean room, $3,760 per m2-level (Table 3.2); at the 'Sanitary' rate of $1,980 it is $20.9M. Total "
        "direct cost $178.2M -> $159.5M, so TCI x 0.895 = $293M for 480 m3. 2018 prices; about $810k in 2025 prices",
        note="GROUNDING: Humbird's vessels are already priced without pharma compliance (Eq. 3.1 takes 25% off "
             "for 'the elimination of cGMP'), so the saving from dropping clean rooms is the building alone, "
             "about 10%. Other costed animal-cell plants agree in scale: Pasitka's designs are $0.8-2.5M per "
             "m3 and a 2025 company-commissioned design (ADL for Gourmey, six 5 m3 vessels) is about $1.3M "
             "per m3. An earlier version of this model assumed $300k; nothing published supports that for "
             "animal cells"),
    "pf_capex_retention": Input(89.0, "$k/m3", "[Pasitka SI Tables S1 and S4, derived] a hoped-for filter-free device "
        "to hold cells back in large tanks: '2 x Large-Scale PD' at $1.21M each for 2 x 25 m3, x 1.84 for "
        "engineering, construction, fees and contingency",
        lo=0.0, hi=460.0, mode=89.0,
        note="A HYPOTHETICAL DEVICE: the paper does not say what it is, and nothing holds cells back at 20 m3 "
             "today. Added to the capital of the large-tank perfusion cases. hi: Humbird's ATF filters cost "
             "$38.5M for 192 m3 before installation, about $460k per m3 of total investment (and $4.6/kg of "
             "membranes besides), which is why his perfusion design stops at 2 m3. 2024 prices; not escalated"),
    "pf_x_half": Input(60.0, "g wet/L", "[assumed] half the efficient-cell density cap, for the cautious case",
        note="Vow's largest reported harvest from a 20,000 L tank implies about 27 g/L (our research pass, one "
             "trade-press source), so 60 g/L is still about twice what has been reported"),
    "pf_capex_fermentation": Input(190.0, "$k/m3", "[pf-tea] what microbial fermentation plants cost when built: "
        "Liberation Labs (4 x 150 m3, announced $115M) $192k/m3; Quorn's third fermenter about GBP 190k/m3",
        lo=70.0, hi=300.0, mode=190.0,
        note="THE FRONTIER CLASS: sanitary plants with very large vessels, built for microbes. lo=70: pf-tea's "
             "model plant at 7,200 m3. Not demonstrated or costed for animal cells; contaminants double in "
             "20 minutes, animal cells in a day or two. Company figures are announcements (grade C/D in "
             "pf-tea)"),
    "pf_bioreactor_capex_share": Input(0.32, "of direct cost", "[Humbird-R] Table 4.3: bioreactors $56.6M of "
        "$178.2M total direct cost", note="the share of plant cost that scales with vessel size (Eq. 3.1)"),
    "pf_labour": Input(1.45, "$/kg", "[Humbird-R] Table 4.6, fed-batch: burdened labour",
        note="scaled with vessel-time per kg in floor_physics"),
    "pf_utilities": Input(0.94, "$/kg", "[Humbird-R] Table 4.6, fed-batch: water, power, gas"),
    "pf_consumables_fedbatch": Input(0.85, "$/kg", "[Humbird-R] Table 4.4: sterile and virus filters per batch"),
    "pf_consumables_perfusion": Input(4.56, "$/kg", "[Humbird-R] Table 4.14: filters plus ATF membranes"),
    "pf_labour_perfusion": Input(1.99, "$/kg", "[Humbird-R] Table 4.13, perfusion: burdened labour (132 staff for "
        "96 small tanks, against 95 for the fed-batch plant)"),
    "pf_bound_capex": Input(70.0, "$k/m3", "[pf-tea] the model fermentation plant at 7,200 m3, used only for the "
        "rough lower bound"),
    "pf_bound_otr": Input(50.0, "mmol O2/L/h", "[pf-tea, citing Humbird 2021] '<50' for animal cells, used only "
        "for the rough lower bound"),
    "pf_consumables_low": Input(0.3, "$/kg", "[assumed] continuous or food-grade operation with few filter changes"),
    "pf_growth_factors": Input(3.1, "$/kg", "[Humbird-R] Table 4.4: insulin, transferrin, FGF, TGF-beta at a "
        "100 kTA industry", note="Humbird: 'At much larger scale, their contribution vanishes entirely'. The "
        "model's floor leaves them out; cells that make their own growth factors would do the same"),
    "pf_aa_price_cheap": Input(1.0, "$/kg hydrolysate", "[assumed] a cheaper amino-acid source than the $2/kg "
        "hydrolysate", note="soybean meal is roughly $0.4/kg at ~47% protein, so ~$0.85 per kg of protein before "
        "hydrolysis and clean-up; microbial or gas-fermentation protein would have to beat that"),
    "pf_other_nutrients_cheap": Input(0.3, "$/kg", "[assumed] salts, buffer, vitamins at feed-grade prices",
        note="against the 0.9 assumed in other_nutrients_floor"),

    # --- Rung 3: demand / price-sensitivity inputs ----------------------------
    # Rung 3 is a two-segment, four-product latent-class logit (market_share.py), NOT a
    # willingness-to-pay reservation curve. Price enters via the BLP income term
    # alpha*ln(income-price); the shared price coefficient beta is DERIVED, not set here:
    # the behavioural primitive is cultivated's own-price elasticity
    # eps_x = eps_own*cult_sub_mult, and beta is solved so the logit reproduces it at
    # a FIXED calibration price (`elasticity_anchor_price` below) and cultivated's share there
    # (see market_share._derive_beta). The two inputs below are the
    # factors of that target; beta tracks them and the cost model automatically.
    "elasticity_anchor_price": Input(29.012, "$/kg", "[calibration] the retail price at which the own-price "
        "elasticity target (eps_own x cult_sub_mult = -3.6) is imposed when the price coefficient beta is solved",
        note="A CALIBRATION DEVICE, NOT A COST. What it pins down is how sharply shoppers respond to price. The "
             "evidence for that is at EQUAL price: Van Loo, Caputo & Lusk (2020) put cultivated meat's own-price "
             "elasticity there between -0.84 and -3.4, and with this anchor the model gives -1.54 at first "
             "contact (golden-guarded, test_golden.py). So the anchor is to be read as 'the price coefficient "
             "that puts the at-parity elasticity at -1.54', which no cost input changes. HISTORY: it used to be "
             "derived from the cost defaults (it was cultivated's retail price when the demand side was first "
             "calibrated), so every cost correction silently re-solved beta; it has been fixed since "
             "2026-11-14. Changing it re-solves beta and every calibrated weight; the kappa range (3-9) is "
             "how the model carries the width of the measured bracket"),
    "eps_own": Input(-0.9, "elasticity", "[scanner] own-price elasticity of meat demand. "
        "Andreyeva, Long & Brownell 2010 (AJPH 100:216) meta-analysis: beef -0.75, pork -0.72, "
        "poultry -0.68; Gallet 2010/2012 meta-analysis: -0.7..-1.0 by species/region; plant-based "
        "scanner data sits in the same -0.5..-1.4 envelope. -0.9 is the mid-range central.",
        lo=-1.4, hi=-0.5, mode=-0.9,
        note="ONE factor of cultivated's own-price-elasticity TARGET eps_x = eps_own*cult_sub_mult; "
             "the shared logit coefficient beta is DERIVED to hit that target at cultivated's own modeled "
             "price & share (market_share._derive_beta), so beta moves automatically when this moves. "
             "Premium tiers are made LESS elastic in meat_market (cuts x0.8, luxury x0.3): premium buyers "
             "are less price-sensitive (Lusk & Tonsor 2016: demand more inelastic at high price)."),
    "cult_sub_mult": Input(4.0, "x", "[data-bracketed] kappa: HOW MANY TIMES more own-price-elastic CULTIVATED "
        "meat is than meat as a CATEGORY. Plain meaning: a 1% rise in cultivated's price loses kappa x 0.9% of its "
        "buyers, versus 0.9% for meat-in-general. WHY > 1: the measured -0.9 is the elasticity of the meat "
        "CATEGORY, which is inelastic precisely because the category has no close substitute; but a single "
        "cultivated product DOES have a near-perfect substitute right next to it (conventional meat, the SAME "
        "tissue), so its OWN price matters far more -- a price cut wins buyers fast, a price rise loses them to "
        "conventional. kappa therefore sets HOW STEEPLY cultivated's share falls as it gets pricier than "
        "conventional (above parity); it does NOT change the at-parity share (where prices are equal).",
        lo=3.0, hi=9.0, mode=4.0,
        note="RANGE WIDENED 2026-11-13 (hi 6 -> 9): the organic-chicken check (market_share.organic_premium_check) "
             "shows the model gives a real-meat product at a premium far more share than organic chicken's ~2.4%; "
             "a higher kappa is the in-model direction of that evidence, so the band now reaches kappa=9, where the "
             "implied at-parity elasticity (about -3.2) is still inside the Lusk bracket. The mode stays 4. "
             "DATA ANCHOR (the one direct measurement): Van Loo, Caputo & Lusk 2020 (Food Policy 95:101931) "
             "priced lab-grown across SIX levels ($2.99-$10.49/lb) in a US choice experiment, identifying its "
             "OWN-PRICE ELASTICITY AT PARITY. Their two models bracket it: the conditional logit (price coeff "
             "-0.178/$) implies eps_lab ~ -0.84 at $5/lb; the random-parameter logit (mean -0.72/$, with a lab "
             "random-coeff SD ~3-4.6 LARGER than its mean -> ~half the population positive, half negative) implies "
             "eps_lab ~ -3.4. So the data bracket is eps_lab(at parity, cold) in [-3.4, -0.84]. kappa is the "
             "flat-logit STAND-IN for exactly that real_tissue heterogeneity (= a nested-logit dissimilarity "
             "parameter), so this is the moment that grounds it: at the central kappa=4 the model's implied "
             "at-parity cold elasticity is -1.5, INSIDE the bracket (self-check [4b]; golden-guarded at -1.53827). "
             "CORROBORATION: a single "
             "product's own-price elasticity is typically ~3-5x its category's (the standard brand-vs-category "
             "gap), and cultivated is a closer substitute (same tissue) -> the upper half is apt. RANGE 3-6 spans "
             "the bracket's interior (note kappa=3 dips just under the MNL -0.84 end; the floor could tighten to "
             "~3.5, kept at 3 as a mild dovish margin). RESIDUAL CAVEAT (functional form, not fixable by kappa): "
             "Lusk measures the elasticity AT PARITY, but the realized headline target eps_x = eps_own*kappa = "
             "-0.9*4 = -3.6 is at cultivated's OPERATING POINT R~2.4, where the BLP+kink elasticity is steeper -- "
             "matching the at-parity bracket grounds the SHAPE near parity, but the -3.6 at R~2.4 is an "
             "EXTRAPOLATION (no DCE has priced cultivated at ~2.4x conventional). The OTHER factor of eps_x, so it "
             "moves the DERIVED beta directly; swept lo-hi in self-check [6]."),
    "loss_aversion": Input(1.0, "ratio", "REFERENCE-DEPENDENT price asymmetry lambda (OFF by default). Consumers "
        "may compare each product to the conventional price and feel a premium as a 'loss': a DISCOUNT (below "
        "conventional) rewarded at the UNIT rate (+1), a PREMIUM penalised at -lambda, so "
        "V_loss_j = -lambda*max(0, price_ratio_j - 1) + 1*max(0, 1 - price_ratio_j). lambda=1 (the DEFAULT) is "
        "SYMMETRIC -- the term collapses to a smooth linear (1 - price_ratio) with NO kink, i.e. no loss "
        "aversion; lambda>1 adds an asymmetric premium penalty (Tversky-Kahneman 1992 put the loss/gain ratio "
        "~2.25). Applied uniformly to every product (plant-based at 1.77x and cultivated at R), never a "
        "cultivated-only cliff.",
        lo=1.0, hi=2.25, mode=1.0,
        note="WHY DEFAULT 1.0 (symmetric, no kink) rather than the TK 2.25: (1) it is NEAR-INERT on the headline "
             "anyway -- the beta-derivation absorbs lambda's price slope, so lambda only reshapes the parity KINK, "
             "not the elasticity level at the US anchor (lambda 1->2.25 moves the at-parity share <2pp). It does NOT "
             "leave the regional roll-up unchanged (corrected 2026-11-13): absorbing lambda pushes beta positive "
             "(+0.051 at 2.25), which reverses the income channel so poorer shoppers become LESS price-sensitive; "
             "the world share rises from 2.5% to 6.3% and Nigeria's from 0.09% to 1.4%. Regional results at "
             "lambda above ~1.65 (where beta crosses zero) are therefore not meaningful. RANGE CAPPED AT 2.25 (the TK median) for a principled reason: the "
             "beta-derivation absorbs lambda's price slope only up to lambda~2.6, where beta saturates at its "
             "monotonicity cap (beta_cap = 1/p_conv - 1e-3); beyond that the realised own-price elasticity would "
             "drift off the eps_own*kappa target (e.g. ~-7 at lambda=4) -- a broken microfoundation, not a "
             "meaningful scenario -- so the slider/prior stops at the literature anchor, where the 'only reshapes "
             "the kink, not the level' property still holds. (A subtler point: the BLP sub-term's coefficient flips "
             "sign around lambda~1.65; above that the price response is carried by the kink rather than the income "
             "log, though the HEADLINE elasticity stays on target throughout the capped range.) (2) Bell & Lattin "
             "2000 (Marketing Sci 19:185) show estimated loss "
             "aversion in aggregate choice data is largely CONFOUNDED by unmodeled price-response heterogeneity -- "
             "and this model already carries that heterogeneity in kappa (cult_sub_mult, the real_tissue "
             "random-coefficient stand-in), so a separate asymmetric kink risks DOUBLE-COUNTING it; (3) the model's "
             "reference is CONTEXTUAL (the competitor's current price), a cross-sectional comparison that does NOT "
             "fade -- distinct from a TEMPORAL reference anchored to a product's own price history, which adapts "
             "and is transient (the genuinely time-varying novelty effect lives in the neophobia fade, not here). "
             "BONUS: at lambda=1 the model's at-parity own-price elasticity is -0.82, CLOSER to Lusk 2020's "
             "measured MNL -0.84 than the kinked lambda=2.25 (-0.50) was. So lambda is now an OFF-by-default "
             "exploratory dial (range 1-2.25) for anyone who wants to test reference-dependent asymmetry, not a "
             "baked-in behavioral assumption. Its slope still feeds the beta calibration when moved."),
    "w_ratio": Input(1.0, "utils per unit ratio", "[judgement] WEIGHT of the ratio-based price term "
        "w_ratio*(-lambda*max(0, R-1) + max(0, 1-R)): the part of the price response that compares each product "
        "with the conventional price and carries NO income scaling. The rest of the price response is the BLP "
        "income log, which is income-scaled. beta is re-derived for any w_ratio, so the TOTAL own-price "
        "elasticity at the US anchor stays on its target (eps_own*kappa) and US results do not move; what "
        "w_ratio sets is the SPLIT between the two channels, which decides how much less price-sensitive "
        "richer shoppers are than poorer ones, and so the low-income regions and the world roll-up.",
        lo=0.5, hi=1.5, mode=1.0,
        note="No study measures this split for meat; 1.0 (one util per unit of price ratio) is the model's "
             "original, previously hard-coded value, kept as the default so published results are unchanged. "
             "Range 0.5-1.5 is a judgement band around it. Effect (2026-11-13): world share 1.6% at 0.5, "
             "2.5% at 1.0 and 4.0% at 1.5, with the US everyday share unchanged (8.8%); at 0 (all price response "
             "income-scaled) the world share is 1.1%. It is in the tornado (sensitivity.py) rather than the Monte "
             "Carlo, because every value needs beta and the calibration re-solved; that tornado is at the US "
             "reference income, where its bar is zero by construction, so its effect is the world figure above."),

    # --- cultivated's STANDING dials (NO baked-in stance; the reader sets them) -
    #     Cultivated's standing vs conventional is TWO interpretable scenario dials,
    #     both with a NEUTRAL default (not fitted — reported as a band): taste-
    #     acceptance accept_x is the FRICTION half (enters utility as w_taste*(accept_x
    #     -1)); slaughter-free value theta_free_M is the UPSIDE half (the mainstream
    #     weight on the slaughter-free attribute). See market_share.py.
    "theta_free_M": Input(0.0, "utils", "[NEUTRAL DIAL] MAINSTREAM utility weight on the slaughter-free "
        "attribute — THE headline UPSIDE dial. In the rebuilt MNL it is w_slaughter[M], applied to "
        "EVERY slaughter-free product (cultivated, plant-based, whole-food). 0 = mainstream indifferent "
        "to no-slaughter (cultivated ties conventional at parity); positive = mainstream values cleaner "
        "/ no-slaughter, so cultivated (and, more weakly, plant-based) gain.",
        lo=0.0, hi=1.0, mode=0.0,
        note="The ethical UPSIDE half of cultivated's standing. ~89% of real PB-meat buyers are "
             "non-veg/vegan (GFI 2024) — that flexitarian pull lives HERE (mainstream), not in the 5% "
             "ethical core (w_eth). MC prior 0..1: neutral to 'values no-slaughter'."),
    "accept_x": Input(1.0, "fraction", "[DIAL] how fully the mainstream credits cultivated's taste / "
        "real-meat attribute. In the rebuilt MNL it sets cultivated's taste_quality = (accept_x - 1), "
        "weighted by w_taste utils. 1 = tastes as real as conventional (neutral); <1 = a taste deficit.",
        lo=0.6, hi=1.0, mode=1.0,
        note="The taste-FRICTION half of cultivated's standing. In the MNL the utility offset is "
             "w_taste*(accept_x-1) utils, weighted by the shared taste coefficient w_taste."),
    "premium_resistance": Input(1.0, "x", "[assumed] JUDGEMENT DIAL scaling how much premium/cut meat "
        "resists cultivated, relative to everyday mince. It multiplies BOTH per-tier demand levers in "
        "meat_market together (they encode one belief): the authenticity offset tau_type "
        "(basic +0.2, cut -0.4, premium -1.5 utils) AND the deviation of the elasticity multiplier from 1 "
        "(cut 0.8, premium 0.3). At 1.0 = the central ladder; 0 = no tier effect (cultivated penetrates "
        "premium as easily as mince); 2 = doubly resistant premium.",
        lo=0.5, hi=1.5, mode=1.0,
        note="The model's most JUDGEMENT-TO-TARGET demand assumption: the tier offsets have NO external "
             "data source — they encode the belief that premium stays demand-capped even at a deep price "
             "discount. (With the current calibration, premium still has the highest within-category share at "
             "today's cost; cuts lead only near the cost floor.) Exposed and SWEPT (prior 0.5-1.5) so that judgement's "
             "leverage is visible rather than hidden. Scales (tau_type) and (eps_mult - 1) about their "
             "neutral points, so resistance=0 removes the tier effect entirely."),
    "real_tissue_x": Input(1.0, "0/1", "[IDENTIFYING PREMISE, now a DIAL] whether CULTIVATED meat counts as "
        "'real animal tissue' (1) or not (0). =1 is the model's load-bearing premise: cultivated, being "
        "actual cells, INHERITS conventional meat's real-tissue standing and so escapes the plant-based "
        "'not real meat' penalty — the structural reason it can succeed where plant-based stalled. Exposed "
        "as a 0/1 dial (default 1) so a SKEPTIC can set it to 0 ('consumers won't credit lab-grown as real "
        "meat') and watch cultivated collapse toward the plant-based outcome. Weighted by w_realtissue_M "
        "(mainstream) in V_x.",
        note="The single most important ASSUMPTION in the model, deliberately made adjustable rather than "
             "hardwired. At 1 cultivated > plant-based at parity (the headline ordering); at 0 cultivated "
             "becomes a second plant-based product. NOT swept in the MC (it is a scenario axis, like the "
             "acceptance dials), but a primary what-if."),
    "real_tissue_p": Input(0.0, "0/1", "[product position] whether PLANT-BASED meat counts as 'real animal "
        "tissue' (1) or not (0). =0 by definition (plant-based is not animal tissue) — this is the penalty "
        "that, with its price premium and taste deficit, keeps plant-based meat at ~1.2%. Exposed for "
        "SYMMETRY with real_tissue_x (equal footing): set it to 1 to ask the counterfactual 'what if "
        "consumers treated plant-based as equivalent to real meat?' (it would rise sharply). Default 0.",
        note="Plant-based gets the SAME machinery as cultivated; the only a-priori difference between the "
             "two novel meats is this attribute (and price/taste, which are observed). Equal footing means "
             "the asymmetry is a visible DIAL, not a hidden constant."),
    # --- HEALTH-PERCEPTION ATTRIBUTE (positions per product; the WEIGHT is segment-specific & SOLVED) ---
    # Health is a named attribute b_health on every product, weighted by a calibrated, segment-specific
    # health weight (w_health_M / w_health_E). The whole-food health premium is the principled
    # replacement for the old free whole-food intercept xi_w: it is WHY ethical/health-minded eaters
    # default to beans over a processed veggie burger. Positions below; weights are solved.
    "health_x": Input(0.0, "norm", "[SCENARIO, unidentified] HEALTH-PERCEPTION POSITION of CULTIVATED meat "
        "(on the same scale as the other products' health positions, weighted by the segment health weight). "
        "POSITIVE = perceived HEALTHIER (a draw: 'clean, no antibiotics, no faecal contamination, controlled "
        "fat'); NEGATIVE = perceived LESS healthy ('lab-grown, unnatural, ultra-processed'); 0 = at the "
        "conventional reference. Default 0 because the evidence is genuinely TWO-SIDED with no point estimate. "
        "A scenario dial like novelty/authenticity: inert at 0 relative to conventional, never re-pins.",
        lo=-0.5, hi=0.5, mode=0.0,
        note="Distinct from taste (a_x, sensory) and slaughter-free (theta, ethics). Equal footing with the "
             "plant-based health dial. Swept +-0.5 in the MC band."),
    "health_p": Input(0.0, "norm", "[SCENARIO, unidentified] HEALTH-PERCEPTION POSITION of PLANT-BASED meat — "
        "the SAME dial as health_x, for equal footing. POSITIVE = the 'plant-based = good for you' health-halo; "
        "NEGATIVE = the 'ultra-processed fake meat' backlash. 0 = at the conventional reference. Default 0 and "
        "UNIDENTIFIED, like health_x: an exploratory deviation from plant-based's calibrated ~1.2%, not a re-pin.",
        lo=-0.5, hi=0.5, mode=0.0,
        note="The term for 'how much of plant-based's plateau is a health-perception problem?'. Swept in MC."),
    "health_w": Input(2.0, "norm", "[position] HEALTH-PERCEPTION POSITION of the WHOLE-FOOD outside option "
        "(beans/tofu/lentils): POSITIVE — whole plant foods are widely seen as 'the healthy choice' (dietary "
        "guidance ranks legumes above red meat; ~17% name healthfulness the top protein driver, and 'good "
        "source of protein' is the #1 healthy-food definer). This positive position, times the SOLVED segment "
        "health weight, is what replaces the old free whole-food intercept. Default +2 (a judgement scale set "
        "with the weight; only the product depends on data, not the split)."),
    "health_c": Input(-0.1, "norm", "[position] HEALTH-PERCEPTION POSITION of CONVENTIONAL meat: slightly "
        "NEGATIVE — red/processed meat carries a mild 'less healthy' standing (saturated fat, processed-meat "
        "guidance) relative to whole plant foods, though it remains a high-quality protein. Small by design; it "
        "sets conventional's health standing that the other positions are measured against. Default -0.1, so "
        "cultivated (health_x=0, i.e. no antibiotics/contamination, controlled fat) carries a mild +0.1 health "
        "edge over conventional — a small, defensible lift to the at-parity share (~47% -> ~49%)."),
    "neophobia_p0": Input(-1.0, "utils", "[behavioural] plant-based meat's INITIAL (cold-start) novelty "
        "attitude — the analogue of neophobia_x0 for cultivated. Plant-based is already MATURE (~1.2%), so "
        "its observed position is the calibration target and this cold-start is mostly HISTORICAL / "
        "exploratory: it sets where plant-based's own diffusion curve STARTED. Crucially, plant-based's "
        "novelty never fully faded into success because it never reached sensory parity (the taste deficit "
        "a_p<1 is permanent) — so in the timing chart plant-based is the STALLED counterfactual to "
        "cultivated. Default -1.0; fades toward the long-run neophobia_p (default 0) at accept_rate.",
        lo=-2.0, hi=0.5, mode=-1.0,
        note="Mirrors neophobia_x0 so plant-based has the SAME timing apparatus. PB's stall in the chart is "
             "driven by its permanent taste deficit (a_p) + price premium (R_p), not by novelty — novelty "
             "fades for both; taste does not. Exploratory (PB is calibrated to its mature share)."),

    # === Rung 3, REBUILT: two-segment, FOUR-product latent-class MNL ==========
    # Demand is an explicit discrete choice over FOUR products by TWO segments:
    #   products  c = conventional meat, p = plant-based meat, x = cultivated,
    #             w = whole-food / non-meat outside option (beans/tofu/lentils)
    #   segments  M = mainstream (taste/price-driven), E = ethical (slaughter-free)
    # Each product carries {price, taste_quality, slaughter_free, real_tissue};
    # each segment weights those attributes differently. Total share_j =
    # w_eth*P_E(j) + (1-w_eth)*P_M(j). NO nested logit: cultivated cannibalises
    # CONVENTIONAL (not the veggie burger) because the shared real_tissue attribute
    # makes conventional dominate the large mainstream segment. See market_share.py.
    "price_pb_mult": Input(1.77, "x p_conv", "[GFI] plant-based meat retail PRICE premium vs "
        "conventional: GFI/NIQ 2024 put PB meat at +77% per lb (up from +65% in 2022); the gap WIDENED, "
        "and 2025 narrowing is an artifact of beef inflation, not PB cost-down",
        lo=1.5, hi=2.2, mode=1.77,
        note="PB meat is a genuine, persistent price PREMIUM — a load-bearing reason its share is small."),
    "price_wf_mult": Input(0.25, "x p_conv", "[BLS] whole-food plant protein staple (dried beans/lentils) "
        "$/kg vs commodity meat: US dried beans $3.40/kg (BLS Aug 2025), representative $2-3.5/kg, vs "
        "~$12/kg meat -> ~0.25x. Beans are also ~3-5x cheaper per kg of PROTEIN than beef (VRG 2024).",
        note="the outside option is CHEAP; with taste_quality_w and the whole-food HEALTH premium "
             "(health_w x the solved segment health weight) it absorbs most ethical demand -> PB stays ~1%."),
    "taste_quality_w": Input(-0.7, "norm", "[assumed] whole-food (beans/tofu/lentils) taste/utility AS A "
        "MEAT SUBSTITUTE: nutritious and cheap, but quite far from a meat-eating experience. Normalised "
        "like (accept_x-1): 0 = as satisfying as real meat, negative = a worse stand-in for meat (-0.7 ≈ "
        "a_w 0.3 on the 1=real-meat scale)",
        lo=-1.0, hi=-0.3, mode=-0.7,
        note="NOT load-bearing: the whole-food HEALTH weight (w_health) is SOLVED to hit the meatless / "
             "PB-share targets, so it absorbs whatever this taste does not — lowering taste_quality_w just "
             "raises the solved health weight, leaving cultivated and plant-based shares unchanged. Set to a plausible "
             "'beans aren't a burger' value; the split between taste and the solved ASC is not identified."),

    # --- Rung 3: income-dependent price sensitivity (BLP log form) -----------
    # Price enters utility as alpha*ln(income_eff - price) (Berry-Levinsohn-Pakes 1995):
    # richer consumers are LESS price-sensitive. alpha is derived in market_share from
    # beta_price so the US-reference behaviour is unchanged; income_eff = income_ref *
    # (income/income_ref)**income_gradient damps the cross-region gradient. See market_share.py.
    "income_ref": Input(85810, "$/yr", "[World Bank] US GDP per capita PPP 2023 ($85,810) — the "
        "REFERENCE income at which the price coefficient is anchored (so the US/commodity case is "
        "unchanged). Only income RATIOS across regions matter, so the absolute level is absorbed by alpha."),
    "income_gradient": Input(0.5, "exponent", "[Muhammad/ERS] phi: the DAMPING exponent on the BLP income "
        "term. Income enters the price utility as genuine Berry-Levinsohn-Pakes V_price = alpha*ln(y_eff - "
        "price_j), with the EFFECTIVE income y_eff = income_ref*(income/income_ref)**phi. phi controls how "
        "strongly the BLP curvature is expressed across regions: phi=1 = raw BLP (y_eff = actual income); "
        "phi=0 = no income effect (y_eff = income_ref everywhere); 0<phi<1 damps it.",
        lo=0.0, hi=1.0, mode=0.5,
        note="phi=0.5 (DEFAULT) gives a Nigeria/US own-price-elasticity ratio ~2.2x (India ~1.8x), matching "
             "the empirical food-price-elasticity gradient (poor countries ~2-3x more responsive for meat; "
             "Muhammad et al. 2011 USDA ERS, food income-elasticity 0.78 low- vs 0.50 high-income). WHY DAMP: "
             "RAW BLP (phi=1) is TOO STEEP for food — it implies a ~6.4x rich->poor elasticity ratio, far "
             "above the data; phi damps the EFFECTIVE income inside the log so the BLP curvature matches the "
             "empirical gradient. This is GENUINE BLP (income inside the log, a single constant alpha = "
             "-beta*(income_ref - anchor_price); the diminishing-marginal-utility-of-income curvature is the "
             "mechanism), NOT the earlier f-multiplier form (which froze income in the log and re-added it "
             "outside — that was not BLP). The US anchor and every at-parity number are invariant to phi "
             "(y_eff = income_ref at the US reference). Cultivated (a premium at R>1) penetrates LESS where "
             "income is lower; the effect saturates above ~US incomes (a $30 product is negligible to a high "
             "earner). phi=0 removes it; phi=1 is raw, over-steep BLP."),
    "taste_quality_p": Input(-0.2, "norm", "[Nectar] plant-based meat AVERAGE blind-taste deficit vs "
        "real meat. Nectar 'Taste of the Industry' 2025: only ~16% (20/122) of PB SKUs reach blind "
        "sensory parity, so the category average is BELOW parity. Normalised like (accept_x-1): "
        "0 = parity, negative = deficit",
        lo=-0.4, hi=0.0, mode=-0.2,
        note="taste is the binding constraint on PB meat (Nectar); the best ~16% reach parity, the "
             "average lags -> a modest negative, weighted by w_taste in utils."),
    "w_taste": Input(5.0, "utils", "[calibration] taste-utility weight: converts a normalised taste "
        "gap (0=parity, -1=very poor) into utils. Large => the flavour-first mainstream punishes a "
        "taste deficit heavily; it is the single shared taste coefficient for all products. It also sets "
        "the SCALE the other perception weights are read against: taste is the #1 food-choice driver "
        "(IFIC 2025; Malone & Lusk 2017 find taste WTP ~2x health and ~3x safety), so w_taste is the "
        "largest non-price weight and health (w_health_M ~0.17x w_taste) sits well below it."),
    "w_eth": Input(0.05, "fraction", "[Gallup] ethics-driven CORE = vegetarian (4%) + vegan (1%), "
        "Gallup 2023",
        lo=0.04, hi=0.10, mode=0.05,
        note="5% is the ethics core and is KEPT. Plant-based lands at ~1% (not ~5%) because the cheap, "
             "HEALTHY whole-food outside option (the health premium w_health_E x health_w) absorbs most "
             "ethical eaters — NOT because the segment is smaller. The flexitarian PB buyer base (~89% of "
             "buyers, GFI 2024) lives in the MAINSTREAM via theta_free_M, not here."),
    "w_realtissue_M": Input(2.0, "utils", "[calibration, SOLVED] MAINSTREAM utility weight on REAL TISSUE "
        "(=1 conventional & cultivated, =0 plant-based & whole-food). SOLVED at runtime so the mainstream "
        "carries pb_mainstream_frac (~89%) of plant-based buyers (GFI/Morning Consult 2024). The stored "
        "value is a seed.",
        note="A REDUCED-FORM bundle: the mainstream non-price standing of non-real-meat products (genuine "
             "'I want real meat' preference + processed/habit residual). Cross-sectionally it is NOT "
             "separately identifiable from habit (we only observe plant-based, which lacks both), so we do "
             "not split it (Heckman state-dependence-vs-heterogeneity). HABIT proper lives in the diffusion "
             "rung (adoption_timing) + the long-run acceptance dials accept_x/theta_free_M. real_tissue is the "
             "IDENTIFYING ASSUMPTION that cultivated, being real tissue, ESCAPES this penalty (inherits "
             "conventional's standing) — the load-bearing premise, giving conventional > cultivated > "
             "plant-based at parity as a structural PREDICTION, not a fitted result."),
    "pb_mainstream_frac": Input(0.89, "fraction", "[GFI] share of plant-based-meat BUYERS who are NOT "
        "vegetarian/vegan (mainstream flexitarians/omnivores): GFI/Morning Consult 2024 (~89%: 57% "
        "omnivore + 15% flexitarian + ~17% other; only ~11% veg/vegan)",
        lo=0.82, hi=0.93, mode=0.89,
        note="pins w_realtissue_M: PB's ~1.2% must be carried mostly by the MAINSTREAM (flexitarians), not "
             "the 5% ethical core. Solved jointly with the segment-specific whole-food intercepts."),
    "wf_mainstream_target": Input(0.06, "share", "[assumed, SOFT] mainstream 'meatless-by-choice' share: "
        "the fraction of mainstream meat-occasions where a whole-food plant protein is chosen over meat",
        lo=0.04, hi=0.14, mode=0.06,
        note="pins w_health_M (the mainstream health weight) so the cheap, healthy outside option does not "
             "spill unrealistically into the mainstream. SOFT (no clean source); mostly moves the whole-food "
             "line, NOT the cultivated headline (self-check [6]: <=0.2pp). Lowered 0.10->0.06 so total "
             "whole-food (~ethical core 5pp + this) sits ~10%, not ~14%; the irreducible part is the ethical "
             "segment eating beans (w_eth * ~96% ~= 5pp), which IS the model's premise, not a free knob."),
    "w_health_M": Input(1.2, "utils", "[calibration, SOLVED] MAINSTREAM weight on the HEALTH attribute — "
        "SOLVED so mainstream whole-food == wf_mainstream_target. Seed only. Times the whole-food health "
        "position (health_w), this is the mainstream's pull toward beans; it REPLACES the old free whole-food "
        "intercept K_wholefood_M.",
        note="SEGMENT-SPECIFIC (vs w_health_E for the ethical segment): mainstream meat-eaters weight health "
             "less / substitute beans for a meat occasion rarely, so this weight is much smaller than the "
             "ethical one. Splitting the health weight by segment is what lets w_realtissue_M be pinned to the "
             "buyer split without the cheap bean option leaking into the mainstream. LITERATURE CHECK: Malone "
             "& Lusk (2017, J. Agric. Appl. Econ. 49:139), a US discrete-choice experiment with taste, health "
             "and safety perceptions on a common -5..+5 scale, find WTP of $0.60/$0.31/$0.21 per unit -> "
             "mainstream HEALTH is ~0.52x TASTE (and the IFIC 2025 'very important' ratio ~0.78x brackets the "
             "soft end). The solved w_health_M lands at ~0.17x w_taste — i.e. health is weighted BELOW taste "
             "and price for the mainstream, well below the ~0.5x discrete-choice anchor."),
    "w_realtissue_E": Input(0.0, "utils", "[assumed] ethical-segment weight on real tissue ~ 0: ethical "
        "eaters choose on slaughter-free, not on 'real meat'"),
    "w_slaughter_E": Input(4.0, "utils", "[assumed] ETHICAL-segment utility weight on the SLAUGHTER-FREE "
        "attribute (=1 for p, x, w; =0 for conventional). Large => segment E strongly avoids conventional "
        "and is drawn to no-slaughter options; this is what lets cultivated win an early beachhead at R>1"),
    "pb_share_target": Input(0.012, "share", "[GFI] plant-based meat's mature share of TOTAL meat "
        "(~0.8% of all meat by $, ~1.7% of packaged, <1% by volume; ~13% household penetration; declining "
        "since the ~2020-21 peak), SPINS/Circana via GFI 2024",
        lo=0.008, hi=0.017, mode=0.012,
        note="the calibration ANCHOR: the whole-food health weight w_health is solved at runtime so the model reproduces this with "
             "cultivated absent (market_share.solve_calibration) — a solved calibration target, not a static floor."),
    "w_health_E": Input(2.3, "utils", "[calibration, SOLVED] ETHICAL-segment weight on the HEALTH attribute — "
        "SOLVED so the ethical-segment plant-based rate hits its target (the residual ~11% of PB buyers / the "
        "non-mainstream part of pb_share_target). Times the whole-food health position (health_w), this is the "
        "ethical segment's strong pull toward whole foods; it REPLACES the old free intercept K_wholefood. Seed.",
        note="this (a large health weight on the healthy whole-food option), not a smaller w_eth, is why a 5% "
             "ethical core yields only ~0.1pp of PB: the healthy whole-food option (beans/tofu) absorbs most "
             "ethical eaters. Diffusion ruled out (PB is mature/declining). Mainstream uses the smaller "
             "w_health_M. The health-minded and the ethical overlap, so the ethical segment weights health "
             "heavily — the principled reason it defaults to whole foods over a processed veggie burger."),
    # === FOOD NEOPHOBIA — an adjustable +/- attitude to a NOVEL food, on BOTH non-
    #     conventional meats. SIGN CONVENTION: the value is a UTILITY OFFSET in utils,
    #     NEGATIVE = neophobia (the novel product is shunned, a penalty), POSITIVE =
    #     neophilia (novelty is a draw, a bonus), 0 = neutral. Named & theory-grounded
    #     (Pliner & Hobden 1992, the Food Neophobia Scale) — NOT a generic cultivated-only
    #     "standing" catch-all: it applies SYMMETRICALLY to plant-based AND cultivated, the
    #     two novel meats (conventional & whole-food beans are familiar -> 0). Default 0 =
    #     neutral, so it does not move the central headline; it is an exploration dial.
    "neophobia_x": Input(0.0, "utils", "[behavioural] CULTIVATED's long-run NOVELTY attitude (utility offset): "
        "NEGATIVE = food neophobia (wary of a novel/unfamiliar food — a penalty), POSITIVE = neophilia (drawn "
        "to the new — a bonus), 0 = neutral (treated like conventional on novelty). Adjustable +/-. This is the "
        "PERMANENT (long-run) part — where novelty attitude LANDS after the product is familiar; the INITIAL "
        "cold-start value neophobia_x0 fades toward THIS with exposure.",
        lo=-2.0, hi=1.0, mode=0.0,
        note="Default 0 is neutral and non-load-bearing. Dial NEGATIVE if a residual 'lab-grown is unnatural' "
             "aversion persists even after the product is familiar (distinct from a TASTE deficit, which is "
             "accept_x); POSITIVE if novelty / cleaner-tech is itself a draw. An exploration dial alongside "
             "accept_x and theta_free_M (Gate 2); held at 0 centrally."),
    "neophobia_p": Input(0.0, "utils", "[behavioural] PLANT-BASED's NOVELTY attitude (utility offset; same sign "
        "convention as neophobia_x: - = neophobia, + = neophilia). An EXPLORATORY override applied after "
        "calibration (like a_p, R_p): default 0 keeps PB at its calibrated ~1.2%; move it to ask 'what if PB "
        "faced more/less novelty resistance?'. PB's residual processed-food / 'fake meat' resistance is already "
        "baked into the calibrated w_realtissue_M, so this term is a DEVIATION from that, not a double-count.",
        lo=-2.0, hi=1.0, mode=0.0,
        note="Lets plant-based be explored as a first-class product (with a_p, R_p). Default 0 = the observed, "
             "calibrated position; it is not in the headline band."),
    "neophobia_x0": Input(-2.8, "utils", "[DATA-ANCHORED] cultivated's INITIAL (cold-start, today) novelty "
        "attitude — the value of neophobia_x at the launch of diffusion (t=0), before any familiarity builds. "
        "It FADES with cumulative exposure (mere-exposure effect) at rate accept_rate, relaxing toward the "
        "long-run neophobia_x. DEFAULT -2.8 is anchored to data: at price+taste parity (R=1, accept_x=1) it "
        "reproduces cultivated's observed COLD at-parity share of ~5% (Van Loo, Caputo & Lusk 2020, US "
        "choice experiment: lab-grown 5% at price parity with beef). The RANGE [-3.5, +1.5] spans the full "
        "survey FRAMING band: -3.5 -> ~3% (coldest), -2.8 -> ~6% (Lusk choice exp ~5%), 0 -> ~49% (neutral), "
        "~+0.5 -> ~60% (Perdue 2024 'cultivated chicken in a restaurant', the warmest framing), +1.5 -> ~80% "
        "(beyond the surveys). The legacy "
        "'launch wariness' is now DERIVED = neophobia_x0 - neophobia_x (the transient part that fades).",
        lo=-3.5, hi=1.5, mode=-2.8,
        note="Replaces the old neophobia_launch (which was the delta x0 - x_long); setting the two ENDPOINTS "
             "(initial x0, final neophobia_x) directly is more intuitive than setting the delta. Cold-start "
             "default -2.8 = 'today's unfamiliar consumer'; it sets the START of the diffusion S-curve, not "
             "the equilibrium (which is neophobia_x). With accept_x it captures the plant-based lesson: "
             "exposure cures the NOVELTY penalty (this fades), but a TASTE deficit (accept_x<1) is permanent. "
             "SWEPT in the Monte Carlo so the 5-60% framing uncertainty enters the band."),

    # --- Rung 4: timing -----------------------------------------------------
    "p_innov": Input(0.02, "1/yr", "[literature] Bass innovation coeff.; near the cross-study "
        "norm (~0.03 avg in Bass-model meta-analyses) — independent adopters",
        lo=0.005, hi=0.05, mode=0.02,
        note="Bass meta-analyses (Sultan/Farley/Lehmann 1990; Van den Bulte 2002) center p~0.01-0.03; "
             "range spans slow (0.005) to fast (0.05) early uptake."),
    "q_imit": Input(0.40, "1/yr", "[literature] Bass imitation coeff.; near the cross-study "
        "norm (~0.38 avg) — word-of-mouth/contagion",
        lo=0.20, hi=0.60, mode=0.40,
        note="Bass meta-analytic norm q~0.3-0.5; range 0.20-0.60 spans weak to strong contagion."),
    # NOTE: there is deliberately NO long-run cultivated "standing" input. Neophobia
    # (neophobia_M/E) fades to ZERO with exposure, and the PERMANENT at-parity standing
    # is the interpretable pair accept_x (sensory parity) + theta_free_M (cleaner-meat
    # upside) — the headline at-parity scenario axis (see RESULTS Gate 2). Removing the
    # old xi_x_floor_M dial is the "no symmetry-breaking garbage collector" fix.
    "accept_rate": Input(0.15, "1/exposure", "[assumed] how fast the INITIAL neophobia (neophobia_x0) decays "
        "toward the long-run neophobia_x, per unit cumulative AVAILABILITY (rollout F, not the small consumed "
        "share)",
        lo=0.05, hi=0.50, mode=0.15,
        note="UNGROUNDED (sets WHEN novelty fades, not the long-run ceiling — that is neophobia_x / accept_x / "
             "theta_free_M). ~0.15 -> ~90% faded by yr~23; range 0.05 (novelty barely resolves within 30yr) to "
             "0.50 (fast, ~90% by yr~13). Driving it by consumed share would never ignite once shares are "
             "realistically ~1%, hence availability (F). SWEPT in the MC (time-to-stabilize uncertainty)."),
    "milestone_year_breakthrough": Input(10, "year", "[assumed] year a scale-up / cheaper-media "
        "breakthrough lands, stepping R down (Rung 4 cost-path coupling)",
        lo=5, hi=20, mode=10,
        note="The WHEN of the cost step (the declared unknown), not the whether. The R endpoints of "
             "each cost path are DERIVED from the cost model (adoption_timing.COST_PATHS), not "
             "hand-typed here, so they cannot drift from Rung 2."),

    # --- Rung 6: scaffold / structured product (most speculative) -----------
    "biomass_cost_nearterm": Input(25.2, "$/kg", "[derived] near-term achievable biomass: the default "
        "with medium at $0.20/L (30.5 x 0.20 + 19.1)"),
    "scaffold_frac": Input(0.2, "kg/kg", "[Gu25-qual/assumed] scaffold material per kg product "
        "(minority mass); Gu et al. 2025 gives the materials picture but no mass fraction",
        lo=0.1, hi=0.3, mode=0.2),
    "material_price": Input(5.0, "$/kg", "[assumed/round] synthetic PLA/PCL <$10/kg, plant "
        "cheaper, gels higher (Gu et al. 2025 ranks materials but gives no $/kg); Gelatex vendor claim "
        "~<$1/kg of meat. Centred so the structured-scaffold mode 0.2*5 + process 5 = $6/kg == SCAF (the "
        "round datasheet scaffold cost) — the decomposition is illustrative, pinned to that one number.",
        lo=2.0, hi=20.0, mode=5.0),
    "process_cost": Input(5.0, "$/kg", "[UNGROUNDED] seed+maturation+removal bioprocess; no TEA",
        lo=1.0, hi=15.0, mode=5.0,
        note="widest, most speculative input; dominates the structured-product spread"),

    # --- premium comparators (Rung 5 targets / Rung 6) ----------------------
    "p_conv_premium_fish": Input(25.0, "$/kg", "[market] premium fish / BlueNalu target",
        lo=20.0, hi=30.0, mode=25.0),
    "p_conv_sushi_salmon": Input(40.0, "$/kg", "[market] sushi-grade salmon / Wildtype target",
        lo=32.0, hi=48.0, mode=40.0),
}


# ----------------------------------------------------------------------------
# Derived constants (computed from the registry — never hand-typed twice)
# ----------------------------------------------------------------------------
# Irreducible feedstock: what the cells must physically eat. Media cost can never fall below
# AA_FLOOR + GLUCOSE_OTHER_FLOOR (cost_model.FEEDSTOCK_FLOOR).
AA_FLOOR: float = REGISTRY["aa_intensity"].value * REGISTRY["aa_bulk_price"].value  # 0.337*2 = 0.67
GLUCOSE_FLOOR: float = REGISTRY["glucose_intensity"].value * REGISTRY["glucose_price"].value  # 0.32*0.40 = 0.13
GLUCOSE_OTHER_FLOOR: float = GLUCOSE_FLOOR + REGISTRY["other_nutrients_floor"].value          # 0.13 + 0.9

# Three plant COSTS for the cost chart and the scenario tables, as (label -> everything-but-medium $/kg).
# They are combined with the reported medium use, so the outer two are not the floor_physics cases
# themselves (those assume efficient cells and floor-price medium); they show the plant lever alone.
# The middle one is the default (`overhead`); the ends are the plant floor and the cautious case with
# cells at half the density, both from floor_physics.py. These are the ends of the `overhead` prior.
PLANT_CONFIGS: dict[str, float] = {
    "cautious plant cost (pharma-style, half the density)":    REGISTRY["overhead"].hi,
    "as reported, with a return on capital (default)":         REGISTRY["overhead"].value,
    "floor plant cost":                                        REGISTRY["plant_floor"].value,
}

# ----------------------------------------------------------------------------
# Demand-model tier ladder & scaffold (model constants, not sliders).
# These are scaled live by the `premium_resistance` slider in meat_market; they are
# defined HERE so the datasheet is the single source of truth (meat_market and
# market_share read them rather than redefining), and so the methods text can quote
# the same numbers it documents. NOT swept individually (premium_resistance sweeps
# the whole ladder); judgement-to-target, no external per-tier data exists.
# ----------------------------------------------------------------------------
SCAF: float = 6.0            # scaffold cost $/kg for a STRUCTURED cut (ASSUMED; no published TEA)
# The cost rung (cuts, §1, the JS) uses the round scalar SCAF; the foothold/uncertainty rungs build
# the SAME scaffold cost from a 3-input decomposition so they can sample a band. The two MUST agree on
# the central (mode) value or the foothold R silently drifts from the rest of the model — guard it here.
_SCAF_DECOMP = (REGISTRY["scaffold_frac"].value * REGISTRY["material_price"].value
                + REGISTRY["process_cost"].value)
assert abs(SCAF - _SCAF_DECOMP) < 1e-9, (
    f"scaffold cost out of sync: SCAF={SCAF} but the decomposition mode "
    f"(scaffold_frac*material_price + process_cost) = {_SCAF_DECOMP}. Re-centre one so they match.")
PREMIUM_RATIO: float = 2.5   # a structured product priced >= this x its species' base form is "premium"
AUTH_BASIC: float = +0.2     # per-tier authenticity offset (utils): everyday staple — cleaner-meat pull, no hang-up
AUTH_CUT: float = -0.4       #   cut (steak/fillet): some "want the real cut" attachment
AUTH_PREMIUM: float = -1.5   #   luxury (wagyu/sushi): strong authenticity, weak welfare pull
EPS_MULT_CUT: float = 0.8    # per-tier elasticity multiplier: cuts a bit less price-sensitive
EPS_MULT_PREMIUM: float = 0.3  #   premium buyers barely price-sensitive -> caps premium share

# Loss-aversion asymmetry constant (Tversky-Kahneman 1992 median ~2.25). The LIVE loss-aversion
# coefficient is the `loss_aversion` slider (canonical form, lambda IS the coefficient); this
# constant is the literature anchor surfaced for the methods text / interactive `const`.
LOSS_AVERSION_RATIO: float = 2.25

# ----------------------------------------------------------------------------
# Which inputs the Monte-Carlo bands sample. ONE list for every band — the Python roll-ups
# (uncertainty.py, meat_market.py), the tornado (sensitivity.py) and the page's JS (injected by
# build_interactive.py) — so they cannot sample different uncertainty sets. (They once did: the
# page swept health_x but not neophobia_x and the Python roll-up the reverse, so the page's band
# and the one quoted in RESULTS.md disagreed.) Everything not listed is held at its slider value.
# ----------------------------------------------------------------------------
MC_COST_INPUTS = ("media_price", "efficiency", "overhead", "markup_add")
# cult_sub_mult (kappa) is sampled since 2026-11-13: a kappa draw enters as the price-sensitivity override
# eps_own*kappa_draw/kappa, which scales both price channels (market_share ratio_scale).
MC_DEMAND_INPUTS = ("eps_own", "cult_sub_mult", "theta_free_M", "accept_x", "neophobia_x", "health_x")
MC_TIER_INPUTS = ("premium_resistance",)   # only where meat types are rolled up by tier
# The adoption-over-time band holds the price ratio fixed and samples what shapes the PATH:
# the cold start, how fast novelty fades, the Bass rollout speed, and the long-run acceptance dials.
MC_TIMING_INPUTS = ("neophobia_x0", "accept_rate", "p_innov", "q_imit",
                    "accept_x", "theta_free_M", "neophobia_x", "health_x")


# ----------------------------------------------------------------------------
# Accessors
# ----------------------------------------------------------------------------
def value(name: str) -> float:
    """The point / base-case value of an input (used as dataclass defaults)."""
    return REGISTRY[name].value


def prior(name: str) -> tuple:
    """The Monte-Carlo prior as (kind, lo, hi, mode, note). Raises if the input
    has no prior (i.e. it is treated as fixed)."""
    inp = REGISTRY[name]
    if not inp.has_prior:
        raise KeyError(f"input '{name}' has no MC prior (it is fixed at {inp.value})")
    return (inp.kind, inp.lo, inp.hi, inp.prior_mode, inp.source if not inp.note else inp.note)


# ----------------------------------------------------------------------------
# Datasheet  (python inputs.py)
# ----------------------------------------------------------------------------
def datasheet() -> str:
    lines = ["Cultivated-meat model — input datasheet", "=" * 78]
    hdr = f"{'input':<22}{'value':>8}  {'unit':<13}{'MC range (lo..hi)':<18}source"
    lines += [hdr, "-" * 78]
    for name, inp in REGISTRY.items():
        rng = f"{inp.lo:g}..{inp.hi:g}" if inp.has_prior else "(fixed)"
        src = inp.source if not inp.note else f"{inp.source}  [{inp.note}]"
        lines.append(f"{name:<22}{inp.value:>8g}  {inp.unit:<13}{rng:<18}{src}")
    lines += ["-" * 78,
              f"derived  AA_FLOOR = aa_intensity x aa_bulk_price = {AA_FLOOR:g} $/kg",
              f"derived  GLUCOSE_FLOOR = glucose_intensity x glucose_price = {GLUCOSE_FLOOR:g} $/kg",
              f"derived  GLUCOSE_OTHER_FLOOR = GLUCOSE_FLOOR + other_nutrients_floor = {GLUCOSE_OTHER_FLOOR:g} $/kg"]
    return "\n".join(lines)


if __name__ == "__main__":
    print(datasheet())
