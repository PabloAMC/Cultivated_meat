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
    "markup_add": Input(5.0, "$/kg", "[USDA ERS, judgement] additive biomass->retail spread, roughly "
        "fixed $/kg (does NOT shrink as biomass falls). Anchored to conventional meat's wholesale-to-retail "
        "spread (USDA ERS Meat Price Spreads, per kg of retail weight): broilers $3.0-3.3 (2026), pork "
        "$6.6-6.9 (2023-25), Choice beef $7.6-8.7 (2023-25).",
        lo=3.0, hi=8.7, mode=5.0,
        note="RANGE RE-GROUNDED 2026-11-14 (was 2-7): the wholesale-to-retail spread starts AFTER the packing "
             "plant, so it already leaves out slaughter and carcass breakdown; the cheapest species (broilers) "
             "is $3.0, the dearest (beef) $8.7. No per-kg cost of forming, packaging or cold chain for a "
             "cultivated product has been published (research_notes/post_harvest_costs.md), and the spread is "
             "closer to proportional than flat across species (42-65% of retail). EARLIER NOTE: "
             "PIVOTAL: with p_conv this sets the parity threshold (p_conv - markup_add). The lower "
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
        lo=10.8, hi=34.0, mode=19.1,
        note="THE PLANT knob. CAPITAL: the report gives depreciation of $1.6/lb ($3.5/kg) but neither the plant's "
             "cost nor the depreciation period. Assuming straight-line over 10 years (Humbird's plant life), the "
             "plant costs $35 per kg of yearly output, and at the 23.6%-a-year charge used for every other case "
             "(humbird_plant_charge) that is $8.3/kg. Over 20 years it would be $16.7/kg. The company's own "
             "figure with depreciation only is $29.5/kg in all; this default is $34.3. CAUTION: the report's "
             "stated tank volumes, densities and bleed rate reproduce about half its stated output, so its "
             "plant cost per kg cannot be checked. lo=10.8 = the plant floor (floor_physics: no clean rooms, "
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
    "plant_floor": Input(10.8, "$/kg", "[floor_physics] plant cost per kg of real cells if everything that has "
        "been costed for animal cells works together, financed like a mature food industry: a food-grade plant "
        "without clean rooms ($810k per m3 in 2025 prices) plus a hollow-fibre filter loop to hold cells back "
        "(retention.py), 20 m3 tanks in perfusion at the density CO2 removal allows (120 g/L), efficient 3 ng cells, "
        "91% uptime: capital, maintenance and insurance $6.4 + labour $1.2 + utilities $1.2 + consumables $2.0 (of "
        "which filter membranes $1.0 and bubble protectant $0.7). Until 2026-11-15 (late) it was $9.8, with a "
        "hoped-for device at $89k per m3 and no protectant",
        note="THE FLOOR'S PLANT TERM (2026-11-14). Each element is allowed by physics and claimed or shown "
             "somewhere, never together: food-grade 20 m3 tanks run today (Vow); perfusion above 100 g/L is "
             "shown at 10 L (SuperMeat, Pasitka); a way to hold cells back at 20 m3 is not shown; efficient "
             "cells are not shown; 91% uptime is Humbird's figure, which he calls 'rather aggressive'. "
             "FINANCING: the yearly charge is plant_charge_mature (17.3%), because the floor is a long-run "
             "case compared with meat, a mature industry; at the first-plant rate (23.6%) this term is $13.1. "
             "tests/test_floor_physics.py ties this value to the module"),
    "plant_floor_lo": Input(6.3, "$/kg", "[floor_physics] THE FRONTIER: the same case in a plant that costs what "
        "microbial fermentation plants cost today ($190k per m3: Liberation Labs, Quorn), at the same financing, "
        "buying its oxygen (such plants have no oxygen unit). $4.9 before 2026-11-15 (late): no filter membranes, "
        "no protectant, no oxygen",
        note="such plants exist, for microbes, with 150 m3 vessels. Nobody has costed or built one for "
             "animal cells, whose cultures are far easier to contaminate. $6.8 at the first-plant rate. "
             "CROSS-CHECK (research_notes/plant_capital_crosscheck.md): the price holds at small tanks. "
             "Humbird's own baker's-yeast plant costs $57k per m3 with 200 m3 fermentors and $130k with "
             "27 x 20 m3 (his Table A.5; about $175k in 2025 prices). And two published designs FOR ANIMAL "
             "CELLS assume this level: CE Delft 2021 $167-277k per m3 (food-grade, no clean rooms) and "
             "Negulescu 2023 $209k (42 m3 tanks). Humbird's animal-cell plant is 5x his yeast plant at the "
             "same tank size: sterile seed train, media handling, oxygen supply, a higher installation factor "
             "and clean rooms. Whether animal cells need all of that is the open question"),
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
    "pf_run_days": Input(33.0, "days", "[Humbird-R] Sect. 4.2: perfusion runs of about 33 days; with his 91% uptime "
        "that leaves 3.3 days to clean, restart and regrow",
        note="Used by the page's 'build your own case' controls: a run ends at this length or when it is "
             "contaminated, whichever comes first. The restart time is derived from pf_uptime (perfusion) and "
             "pf_uptime_realistic (drained and refilled), so a run with no losses reproduces those uptimes"),
    "pf_hazard_pharma": Input(0.002, "per day", "[research pass, derived] chance per day of losing a run to "
        "contamination in large biopharma plants: about 2% of batches (Humbird's report) over runs of about two weeks",
        note="REFERENCE POINTS shown beside the lever, not used in the floor (which assumes none): 0.2% a day "
             "for biopharma contamination, 0.7% for biopharma losses from all causes (7.6% of batches), and "
             "1-2% a day for cultivated meat today, from a survey in which makers lost 11.2% of batches (19.5% "
             "beyond flask scale; Compr. Rev. Food Sci. Food Saf. 2025) if those batches ran 10-20 days, which "
             "the survey does not state. See reports/'Continuous harvest bioreactor progress.md'"),
    "pf_blend_filler_price": Input(3.0, "$/kg", "[Pasitka] the plant ingredients blended with cells in its hybrid "
        "product, at the price that paper uses", note="for the page's blend lever only"),
    "pf_medium_l_floor": Input(8.0, "L/kg", "[Humbird-R, derived] the least liquid a kg of cells needs to carry its "
        "nutrients in: the medium use of his efficient-cell designs, about a quarter of the 30.5 L/kg a company reports",
        note="a lower bound on litres per kg in the page's 'build your own case' controls; the waste the "
             "cells make usually needs more (pf_nh3_*, pf_lac_*)"),
    "pf_nh3_efficient": Input(0.054, "mol/kg wet", "[Humbird-R, derived] ammonia made per kg of cells grown by his "
        "enhanced cells: Reaction 2.11, 0.004 mol per mol of dry cell mass, x 13.6 mol per kg wet",
        note="13.6 mol/kg = 300 g dry matter per kg wet over 22.06 g/mol for CH1.68 O0.34 N0.21 (his Table 2.1). "
             "All of it comes from catabolism, so per kg it scales with the upkeep burned (slower cells make more)"),
    "pf_nh3_wild": Input(0.952, "mol/kg wet", "[Humbird-R, derived] the same for ordinary (wild-type) cells: "
        "Reaction 2.9, 0.070 mol per mol of dry cell mass"),
    "pf_lac_efficient": Input(0.558, "mol/kg wet", "[Humbird-R, derived] lactate, enhanced cells: Reaction 2.11, 0.041 "
        "mol per mol of dry cell mass"),
    "pf_lac_wild": Input(6.45, "mol/kg wet", "[Humbird-R, derived] lactate, ordinary cells: Reaction 2.9, 0.474 mol "
        "per mol of dry cell mass"),
    "pf_glc_kg": Input(1.116, "mol glucose/kg wet", "[Humbird-R, derived] glucose used per kg of cells grown by his "
        "enhanced cells: 0.558 mol lactate at his stated lactate:glucose of 0.50", lo=0.67, hi=3.6, mode=1.116,
        note="used only when the lactate yield is set explicitly (explore lac_yield). lo-1.0 = 0.4-0.6 kg glucose "
             "per kg dry x 0.30 dry/wet (waste_tricks_sizing.md, consistent with CHO at a yield of 1.41); hi = "
             "Humbird's wild-type cell (6.4 mol lactate at 1.77). Which applies to a meat cell is unmeasured"),
    "pf_sorbent_q": Input(0.15, "mmol/g = mol/kg", "[derived, not measured; waste_tricks_sizing.md A2] ammonium a "
        "sorbent holds at 3-5 mM against 140 mM sodium", lo=0.10, hi=0.25, mode=0.15,
        note="mass-action exchange with selectivities of 0.6-3 for clinoptilolite, zirconium phosphate and cation "
             "resin; pure-solution capacities (0.9-5.5) do not apply in medium. No capacity has been measured in "
             "medium"),
    "pf_sorbent_price": Input(5.0, "$/kg", "[assumed] a graded, sterilised exchanger fit for medium",
        lo=0.05, hi=20.0, mode=5.0,
        note="bulk natural zeolite is $0.05-0.30/kg (USGS Mineral Commodity Summaries 2026, read in full); no price "
             "was found for a sterile medium-grade zeolite, resin or zirconium phosphate; 5-20 is an assumption"),
    "pf_sorbent_cycles": Input(1.0, "uses", "[assumed] times the sorbent is used before it is thrown away (1 = "
        "single use)", lo=1.0, hi=50.0, mode=1.0,
        note="no regeneration count in medium was found; 50 is a hope, not a number (waste_tricks_sizing.md)"),
    "pf_nh3_limit": Input(5.0, "mmol/L", "[Humbird-R] Sect. 2.3: 'consider the limits of 5 mmol/L NH3 and 50 mmol/L "
        "lactate'; he cites 2-10 mmol/L reported for mammalian cells", lo=2.0, hi=10.0, mode=5.0),
    "pf_lac_limit": Input(50.0, "mmol/L", "[Humbird-R] Sect. 2.3, as above"),
    "pf_maintenance_share": Input(0.5, "of O2 uptake", "[GFI 2025 / Miller 1987, judgement] share of a cell's oxygen "
        "uptake at a 24 h doubling time that is upkeep (it runs whether or not the cell grows); the rest rises "
        "in proportion to the growth rate",
        lo=0.31, hi=1.0, mode=0.5,
        note="qO2(mu) = qO2(24 h) x [share + (1 - share) x mu / mu(24 h)]. lo=0.31: GFI's 2025 growth-modelling "
             "review, Fig. 3.5b, from Wagner et al. 2011 (cells at zero growth took up 12-67% of their "
             "exponential-phase oxygen, mean 31%; the fit gives a true yield of 2.9 g dry cells per g O2). "
             "Miller et al. 1987 put upkeep at 62% of ATP use in hybridoma at 0.66 per day. hi=1.0: Humbird's "
             "assumption (upkeep only). 0.5 sits between the two measurements. At 24 h the uptake is West's "
             "law whatever the share, so Humbird's designs are unaffected; it matters for faster and slower "
             "cells. The review calls this 'a gap for CM-relevant cell lines'"),
    "pf_mix_ratio_20m3": Input(0.97, "-", "[Humbird-R, derived] oxygen transfer the mixing rule allows in a 20 m3 "
        "stirred tank, relative to the oxygen-transfer limit",
        note="Humbird's rule (Sect. 2.3, after his ref. 127): mixing time t_m must stay below 1/kLa. His Eq. "
             "2.18 gives t_m = 6 T^(2/3) (P/V rho)^(-1/3) (D/T)^(-1/3) (H_L/T)^2.5 = 141 s at 20 m3 (liquid "
             "height 1.6 T from his Fig. 2.5, D = T/3, and 43 W/m3, the power at which the smallest eddies are "
             "20 um: his Eq. 2.17 with 50x peak dissipation and water at 37 C). His Eq. 2.16 gives kLa = "
             "0.075 (P/V)^0.47 u_s^0.8 = 26.4 per hour at 0.006 m/s, so 1/kLa = 137 s. 137/141 = 0.97: the two "
             "limits coincide at 20 m3, as his text says. At fixed shape and power t_m grows as V^(2/9), so "
             "the mixing-limited density falls as (V / 20)^(-2/9). Hydrostatic pressure, which helps oxygen "
             "in tall tanks, is left out. Used by the page's 'build your own case' controls"),
    # --- salt strength (osmolality) and the least medium flow a cell needs (floor_physics.explore) ---
    "pf_osm_base": Input(300.0, "mOsm/kg", "[typical] osmolality of fresh culture medium for mammalian cells"),
    "pf_osm_limit": Input(415.0, "mOsm/kg", "[Humbird-R, derived; Zhu 2005] the salt strength at which growth is taken to "
        "stop: the level that Humbird's own two limits imply together (100 mbar of CO2 and 50 mmol/L of lactate, "
        "each with its sodium, in a 300 mOsm medium at pH 7.2 come to 413)",
        lo=350.0, hi=450.0, mode=415.0,
        note="Holding the pH against dissolved CO2 takes bicarbonate, and neutralising lactate takes base; both "
             "add salt. CHO cells showed no obvious change at 400-450 mOsm/kg from salt alone and a 20% drop at "
             "400-450 combined with 190-210 mbar of CO2 (Zhu et al. 2005, via research_notes/"
             "co2_sparging_settling.md); hybridoma growth fell 63% at 415 with 260 mbar. Across four sources "
             "(research_notes/perfusion_rate_osmolality.md) growth starts to fall at about 320-400 mOsm/kg "
             "and is halved at about 430-465, so 415 sits where growth is clearly slowed but not stopped: a "
             "single limit stands in for a gradual decline. Applied in perfusion only"),
    "pf_ph": Input(7.2, "pH", "[typical] the pH the tank is held at (setpoints near 7.0 are common; 6.85-7.8 has been "
        "tested)", lo=6.9, hi=7.4, mode=7.2,
        note="sets how much bicarbonate a given CO2 level needs: [HCO3-] = dissolved CO2 x 10^(pH - pK1)"),
    "pf_pk1": Input(6.1, "pK", "[textbook] apparent first dissociation constant of carbonic acid in medium at 37 C"),
    "pf_co2_henry": Input(0.0246, "mmol/L per mbar", "[textbook] solubility of CO2 in water at 37 C (2.46 mmol/L at 100 mbar)"),
    "pf_hco3_base": Input(24.6, "mmol/L", "[derived] bicarbonate already in fresh medium: equilibrium with 50 mbar of "
        "CO2 at pH 7.4, the usual incubator condition; only bicarbonate above this adds to the salt strength"),
    "pf_min_perfusion": Input(7.5, "mL per g wet cells per day", "[judgement within a measured range] the least medium "
        "flow a cell needs for everything other than ammonia and lactate: other by-products that build up, and "
        "nutrients that run out",
        lo=3.7, hi=18.5, mode=7.5,
        note="The bioprocess measure is the cell-specific perfusion rate. Measured for CHO cells "
             "(research_notes/perfusion_rate_osmolality.md): 50 pL per cell per day sustained 2.1 x 10^8 cells "
             "per mL with more giving no benefit (Clincke et al. 2013, full text); 14-30 sustained 2.2-2.4 x "
             "10^8 at slow growth and 8-10 only held the culture without growth (Mayrhofer et al. 2020); "
             "unoptimised processes run at 50-300. For a 17 um cell (2.7 ng) 10 / 25 / 50 pL is 3.7 / 9.3 / "
             "18.5 mL per gram per day; cell size was not reported for the low figures, so they could be up "
             "to 1.8 times higher. The default 7.5 is the value at which this stops binding for the floor's "
             "efficient cells (10.8 L/kg at a 24 h doubling time, against 11.2 from lactate), so the floor "
             "assumes cells better than typical pharma practice (9.3) and within what has been reached. "
             "Litres per kg = this / growth rate per day, so slow cells need more. One company's chicken "
             "process (30.5 L/kg at half a doubling a day) works out to 10.6"),
    # --- gravity settling (floor_physics.settler_spec): can a settler hold cells back at 20 m3? ---
    "pf_cell_density": Input(1.036, "g/mL", "[calibrated; research_notes/co2_sparging_settling.md] density of an animal "
        "cell, set so that a 14 um CHO cell settles at its measured 1.45 cm/h", lo=1.03, hi=1.06, mode=1.036,
        note="measured single-cell settling: CHO 1.45 cm/h, hybridoma 2.9; working settlers are sized at 0.7-1.0"),
    "pf_medium_density": Input(1.007, "g/mL", "[typical] density of culture medium at 37 C"),
    "pf_medium_viscosity": Input(0.75, "mPa s", "[typical] viscosity of culture medium at 37 C (water is 0.69)"),
    "pf_plate_gap": Input(1.0, "cm", "[typical] spacing of the plates of an inclined (lamella) settler; they stand at 60 degrees"),
    "pf_anoxia_min": Input(60.0, "min", "[research_notes/co2_sparging_settling.md] time cells spend in working inclined "
        "settlers (60-90 minutes), taken as what they tolerate without oxygen", lo=10.0, hi=90.0, mode=60.0,
        note="at 120 g/L the cells use up the dissolved oxygen in seconds, so the whole stay in a settler is "
             "without oxygen unless the settler is cooled"),
    "pf_clump_packing": Input(0.6, "-", "[assumed] share of a clump's volume that is cells (random packing)"),
    # --- CO2 balance (floor_physics.co2_limited_density): the tank's CO2 limit from first principles ---
    "pf_pco2_limit": Input(100.0, "mbar", "[Humbird-R] Sect. 2.3: dissolved CO2 kept below a partial pressure of 100 "
        "mbar ('productivity is maximized when pCO2 is maintained in' a range below it)",
        lo=80.0, hi=250.0, mode=100.0,
        note="The level animal cells tolerate while GROWING. Evidence (research_notes/co2_sparging_settling.md): "
             "CHO lost 9% of its growth rate at 150 mmHg (200 mbar) with osmolality controlled (Zhu 2005) and "
             "about half near 260 mbar with osmolality raised; a defensible range is 100 / 160 / 200 mbar. "
             "CHO and hybridoma only: nothing is published for muscle, fibroblast or fish cells"),
    "pf_gas_velocity": Input(0.006, "m/s", "[Humbird-R] Sect. 2.3: 'Sparging is limited to a superficial velocity of "
        "0.006 m/s at the top of the vessel' (0.1 vvm in a 20 m3 tank); his recasting of guidance that the maximum "
        "sparge rate 'is usually <0.1 vvm' (he cites Ozturk 1996 and Poertner 2015, neither readable by us)",
        lo=0.002, hi=0.009, mode=0.005,
        note="NOT A MEASURED LIMIT (research_notes/gas_flow_cap.md). A 1990s rule of thumb, reportedly for 'cell "
             "lysis and foaming', turned into a velocity for one tank. Nienow 2006 (read in full): large tanks use "
             "0.1-2 mm/s and the upper limit with protectant 'is not established'. What we found: (1) damage from "
             "bursting bubbles scales with gas per litre (vvm), as CO2 removal does, so it does not worsen with "
             "tank size; with 2 g/L poloxamer and drilled-hole spargers 0.2 vvm did no harm at 60-80 million "
             "cells/mL up to 200 L (abstract), without protectant 0.1 vvm kills cells ten times faster than they "
             "grow; (2) foam scales with velocity, is unmeasured against it, and is the likeliest cap; (3) no "
             "published culture at 6 mm/s at any scale, and none above 200 L combines 50 million cells/mL with "
             "0.05 vvm; tanks of 1-25 m3 are reported at 0.002-0.02 vvm. Defensible range 2 / 5 / 9 mm/s; our "
             "probability that 6 mm/s is usable at 20 m3 and 120 g/L is about 45%. The floor keeps 6 because it "
             "takes the favourable end of each range. The exhaust gas leaves tall tanks close to saturated with "
             "CO2 (four sources), which is what the balance assumes"),
    "pf_aspect": Input(1.6, "H/T", "[Humbird-R] Fig. 2.5: a tank built twice as tall as wide, filled to 80%, so the "
        "liquid is 1.6 times as deep as the tank is wide", lo=0.8, hi=2.5, mode=1.6),
    "pf_rq": Input(1.204, "mol CO2/mol O2", "[Humbird-R, derived] Reaction 2.11: 0.455 mol CO2 made per 0.378 mol O2 used"),
    "pf_rq_lipid": Input(0.2381, "mol CO2/mol O2", "[Humbird-R, derived] CO2 released by making the cells' lipid "
        "from glucose, per oxygen used: Reaction 2.2 (0.049 glucose -> 0.205 lipid + 0.090 CO2 per mol of dry cell "
        "mass, no oxygen) over Reaction 2.11's 0.378 mol O2. Feeding all the lipid takes RQ from 1.204 to 0.966",
        note="Carbon and electron balance check: lipid (CH2 O0.13) carries 1.74 more electrons per carbon than "
             "glucose; 0.205 C-mol x 1.74 / 4 = 0.089 mol CO2. Humbird's lipid is 15% of dry mass (Table 2.1)"),
    "pf_fat_kg": Input(0.045, "kg/kg wet", "[Humbird-R, derived] lipid in a kg of wet cells: 15% of the 300 g of dry "
        "mass (Table 2.1)"),
    "pf_fat_price": Input(1.5, "$/kg", "[assumed] fatty acids fed to the culture, at about a vegetable-oil price",
        lo=1.0, hi=20.0, mode=1.5,
        note="the oil itself is cheap; delivering it to cells in serum-free medium needs a carrier (albumin, "
             "cyclodextrin) or an emulsion, which is not priced here; hi stands for a chemically defined concentrate"),
    "ge_atp_per_o2": Input(5.0, "mol ATP/mol O2", "[textbook] oxidative phosphorylation at a P/O ratio of about 2.5"),
    "pf_protectant_dose": Input(2.0, "g/L", "[gas_flow_cap.md] poloxamer 188 in the medium: the dose with which dense pharma "
        "cultures took 0.1-0.2 vvm without extra cell death, which the model's 6 mm/s relies on",
        lo=1.0, hi=5.0, mode=2.0,
        note="Humbird recommends more than 0.5 g/L for vigorously sparged cultures (Sect. 2.3); dense high-gas runs used 2-5 g/L "
             "(research_notes/gas_flow_cap.md). It passes the filter and leaves with the medium."),
    "pf_protectant_price": Input(30.0, "$/kg", "[assumed] poloxamer 188 bought by the tonne: no bulk price found; catalogue "
        "prices are $230-260/kg in 10-25 kg packs (Sigma-Aldrich, search summary), tonne-scale excipients sell at a fraction",
        lo=10.0, hi=260.0, mode=30.0,
        note="hi = the catalogue price. At 2 g/L and $30/kg it is $0.06 a litre of medium: $0.67/kg of cells at 11 L/kg, "
             "$1.7 at 28 L/kg. A supplier quote would replace the assumption (TODO.md)."),
    "pf_o2_microbial": Input(1.0, "switch", "[model choice, 2026-11-15] 1: the yeast-style plant class buys its oxygen "
        "(pi_o2_feed x pi_o2_price), as plants built item by item do; 0: no oxygen cost (earlier versions)"),
    "pf_antifoam_otr": Input(0.75, "-", "[judgement, effect reported] oxygen transfer from the sparger with antifoam "
        "present, relative to without: the middle of the reported 0-50% cut",
        lo=0.5, hi=1.0, mode=0.75,
        note="research_notes/gas_flow_cap.md (follow-up 2): antifoams cut kLa by 0 to about 50% depending on type and dose "
             "(snippet- and abstract-level sources there). 1 keeps Humbird's oxygen transfer; at 0.5 the oxygen limit of the "
             "reference tank falls from 195 to about 97 g/L and binds before CO2. Applied to the sparger only."),
    "pf_co2_strip_eff": Input(0.9605, "-", "[calibrated] how close the exhaust gas comes to equilibrium with the liquid",
        note="THE CO2 BALANCE. CO2 leaves a sparged tank only in the exhaust gas. Gas passes at u_s / H_L tank "
             "volumes per second (superficial velocity over liquid depth) and can carry at most pCO2 / RT of CO2, "
             "so the most the tank can remove is (u_s / H_L) x pCO2 / RT. The cells make RQ x qO2 per gram. "
             "With Humbird's limits that gives 125 g/L at 20 m3 and 58 g/L at 200 m3, against his 120-150 and "
             "70 (Fig. 2.8b): the balance reproduces his curve, and its (V)^(-1/3) fall with size is geometry "
             "(liquid depth). This factor, 0.96, sets the 20 m3 value to the 120 g/L the floor uses "
             "(pf_x_co2_20m3). Perfusion does not help: at 11 L/kg the liquid carries off about 4% of the CO2"),
    # --- gas supply (floor_physics.oxygen_fed): what the sparge gas costs per kg ---
    "pf_o2_purity": Input(0.90, "mol/mol", "[Humbird-R] Sect. 2.3: the tanks are sparged with 90% O2 made on site by "
        "vacuum pressure-swing adsorption (VPSA)"),
    "pf_back_pressure": Input(1.33, "bar", "[Humbird-R] Sect. 4.1: '1.33 bar (5 psig) back pressure at the top'; his gas "
        "velocity limit is defined at the top of the vessel"),
    "pf_o2_price": Input(0.15, "$/kg O2", "[Humbird-R] Sect. 2.3: on-site VPSA oxygen at 'a size-dependent effective cost "
        "of $0.10-0.20/kg O2' (2018 prices; escalated with running costs)", lo=0.10, hi=0.33, mode=0.15,
        note="hi: Humbird's own plant tables imply more. His Table 4.1 lists a 25,000 t/y VPSA at $8.84M bare for "
             "480 m3 of tanks (about 13% of direct plant cost once installed), which at his 23.6% yearly charge "
             "plus Table 4.4's power is about $0.25-0.33 per kg O2 [derived]. The oxygen plant is sized by the gas "
             "flow, not by what the cells use: his design feeds about 3.7 kg O2 per kg of cells (25,000 t/y for "
             "6,800 t/y of cells) and the cells use 0.2, so about 95% is vented"),
    # --- gas-exchange side study (gas_exchange.py; research_notes/gas_exchange_study.md). NOT used in the
    #     headline cost or on the page. Access levels of the sources are in the note's source list ---
    "ge_d_co2": Input(2.5e-9, "m2/s", "[textbook, scaled] diffusivity of CO2 in water: 1.92e-9 at 25 C, scaled to "
        "37 C by temperature over viscosity (x1.34)", note="not corrected for the cells in the way; +-20%"),
    "ge_d_o2": Input(2.8e-9, "m2/s", "[textbook, scaled] diffusivity of O2 in water: 2.1e-9 at 25 C, scaled as above"),
    "ge_o2_henry": Input(0.0010, "mmol/L per mbar", "[textbook] solubility of O2 in culture medium at 37 C: about "
        "1.0 mmol/L against pure oxygen at 1 bar (water is 1.05), 0.2 against air"),
    "ge_do_setpoint": Input(0.05, "mmol/L", "[typical] dissolved oxygen a culture is held at, about a quarter of "
        "saturation with air"),
    "ge_o2_bar": Input(1.0, "bar", "[assumed] pressure of pure oxygen inside the fibres", lo=1.0, hi=2.0, mode=1.0,
        note="a dense (non-porous) wall can hold more than 1 bar without bubbling; the liquid then returns to the "
             "tank far above air saturation, which may harm cells"),
    "ge_buffer": Input(0.0, "mmol/L per pH unit", "[assumed] buffering of the culture other than bicarbonate",
        lo=0.0, hi=5.0, mode=0.0,
        note="Bicarbonate can only turn into CO2 if something supplies the acid. Blood has haemoglobin (about 30 "
             "mmol/L per pH); fresh medium has about 0.5 (1 mmol/L phosphate). The cells' own contents might "
             "add 3-6 at 12-18% of the volume, if CO2 crossing their membranes brings it into play within "
             "seconds [inference, not measured]. In phosphate-buffered saline, carbonic anhydrase on the fibres "
             "doubled CO2 removal (Kimmel 2013, Arazawa 2015, read in full); in medium with no buffer it "
             "would do little"),
    "ge_buffer_medium": Input(0.47, "mmol/L per pH unit", "[textbook arithmetic] buffer of 1 mmol/L phosphate "
        "(DMEM/F12 level, memory) at pH 7.2 with pK 6.8: 2.303 x 1 x 0.715 x 0.285",
        note="HEPES (pK about 7.3, 10-25 mmol/L in lab media) would add 6-14, but is 'no longer essential' at "
             "large scale and adds salt (patent snippets)"),
    "ge_beta_i": Input(15.0, "mmol/L per pH unit of cell water", "[search snippet and memory] buffer inside "
        "cultured cells other than bicarbonate: '10-50' across cell types (a physiology review); about 10 in a "
        "muscle-like line (BC3H-1)", lo=10.0, hi=30.0, mode=15.0,
        note="no figure found for CHO, fibroblasts or myoblasts; whether it acts within a 6 s pass depends on "
             "carbonic anhydrase inside the cells, also not found for these cells"),
    "ge_cell_water": Input(0.70, "of cell mass", "[Humbird-R] wet cells are about 70% water"),
    "ge_ed_volt": Input(2.0, "V per proton", "[memory, unverified] voltage of a bipolar-membrane electrodialysis "
        "cell pair splitting water, with losses (1.2-3 V)"),
    "ge_filtrate_flux": Input(3.8, "L per m2 per h", "[Humbird-R; vendor size guide, snippet] what a perfusion "
        "hollow-fibre filter passes: an ATF-10 serves up to about 1,000 L a day through 11 m2"),
    "ge_atf_area": Input(11.0, "m2", "[vendor size guide, snippet] filter area of one ATF-10"),
    # --- packed (falling-film) column on the loop, headspace pressure (gas_exchange.column_design) ---
    "ge_pk_area": Input(250.0, "m2/m3", "[vendor designation] Mellapak 250Y: about 250 m2 of sheet per m3"),
    "ge_pk_angle": Input(45.0, "degrees", "[vendor designation] the 'Y' channels run at 45 degrees from horizontal"),
    "ge_pk_side": Input(0.0187, "m", "[Wang 2015 thesis, Table 5.1, full text; derived] corrugation side of Mellapak "
        "250Y from its measured channel base (30.2 mm) and crimp height (11.1 mm): sqrt(15.1^2 + 11.1^2)"),
    "ge_pk_ce": Input(0.9, "-", "[Rocha, Bravo and Fair 1996; form read in Wang 2015, value from memory] surface-renewal factor C_E"),
    "ge_pk_load": Input(40.0, "m3/m2/h", "[design choice] liquid load on the packing; Mellapak runs from about 0.2 "
        "to over 200 m3/m2/h (Sulzer brochure, vendor); Tsai's area correlation was fitted over 2.5-75", lo=10.0, hi=80.0, mode=40.0),
    "ge_surface_tension": Input(0.05, "N/m", "[assumed] surface tension of culture medium with protectant "
        "(water 0.070; Pluronic lowers it)"),
    "ge_col_pout": Input(55.0, "mbar", "[design choice] CO2 the culture leaves the column at (in from the tank "
        "at 100)", lo=20.0, hi=70.0, mode=55.0,
        note="55 keeps the pH rise in the loop to 0.26; stripping to 20 (pH +0.70) gave an alkaline exposure 1.6 "
             "times the one that cut CHO density 18-52% (Paul 2020; research_notes/gas_exchange_study.md section 8)"),
    "ge_loop_transit": Input(8.0, "s", "[assumed] time the culture spends outside the tank besides the packing: "
        "pump, sump and return pipe (about 20 m of pipe at 3 m/s)", lo=4.0, hi=20.0, mode=8.0),
    "ge_passes_tested": Input(15.0, "tank volumes per hour", "[Clincke et al. 2013, read in full] the highest "
        "recirculation dense CHO cultures took for weeks through hollow fibres: 1 L/min on 4 L, about 360 passes a "
        "day, 48 days", lo=15.0, hi=24.0, mode=15.0,
        note="hi: a vendor note ran a 1-2 L CHO culture at 12-24 volumes an hour for three weeks with a levitated "
             "pump. Both at bench scale and through filter fibres, not a packed column"),
    "ge_col_gas_out": Input(20.0, "mbar", "[design choice] CO2 in the sweep gas where it leaves the top of the "
        "column, against culture entering at 100 (counter-current)"),
    "ge_col_gas_in": Input(0.4, "mbar", "[textbook] CO2 in fresh air entering the bottom of the column (about 400 ppm)"),
    "ge_loop_volume": Input(0.5, "m3", "[design choice] liquid in the loop outside the tank: packing hold-up (about "
        "0.1-0.4 m3), a small sump and the return pipe", lo=0.2, hi=2.0, mode=0.5),
    "ge_paul_dph": Input(0.37, "pH units", "[Paul et al. 2020, PMC7401239, full text via a summary] mean alkaline "
        "pulse (+0.36 to +0.39) in a two-compartment CHO culture, 35-44 s per pass, that cut peak cell density by "
        "18-52%"),
    "ge_paul_share": Input(0.075, "of volume", "[Paul et al. 2020, as above] share of the culture in the alkaline zone"),
    "ge_col_head_extra": Input(4.0, "m", "[assumed] pumping head beyond the packing height: lift to the top, "
        "distributor, pipes"),
    "ge_col_extra_height": Input(2.5, "m", "[assumed] shell height beyond the packing: distributor, gas inlet, sump"),
    "ge_col_wall": Input(0.006, "m", "[textbook rule] minimum wall of a 1.5-4 m vessel, about 6 mm (Seider, as coded in "
        "BioSTEAM: 1/4-5/16 inch below 6 ft)"),
    "ge_cepci_2014": Input(1.39, "x", "[pf-tea basis] plant-cost index about 800 in 2024 over 576 in 2014"),
    "ge_o2_sweep_purity": Input(0.9, "mol/mol", "[Humbird-R] Sect. 2.3: on-site oxygen is about 90% pure"),
    "ge_o2_price": Input(0.15, "$/kg O2", "[Humbird-R] Sect. 2.3: on-site oxygen at $0.10-0.20 per kg (as quoted "
        "by the gas-flow session)"),
    "ge_lime_price": Input(0.24, "$/kg", "[USGS Mineral Commodity Summaries 2025, lime, search snippet] hydrated lime at "
        "the plant, about $240 per tonne (2024)"),
    "ge_lime_use": Input(0.7, "-", "[assumed] share of the lime that reacts in the scrubber"),
    "ge_p_top_base": Input(0.33, "bar gauge", "[Humbird-R] Sect. 4.1: '1.33 bar (5 psig) back pressure at the "
        "top' (as quoted by the gas-flow session); his gas velocity limit is set at the top of the vessel"),
    "ge_sparge_o2": Input(0.9, "mol/mol", "[Humbird-R] Sect. 2.3: the tanks are sparged with 90% oxygen"),
    "ge_kla_20m3": Input(26.4, "1/h", "[Humbird-R, derived] his Eq. 2.16 at 43 W/m3 and 6 mm/s (see pf_mix_ratio_20m3)"),
    "ge_mix_time_20m3": Input(141.0, "s", "[Humbird-R, derived] his Eq. 2.18 at 20 m3 (see pf_mix_ratio_20m3)"),
    "ge_stir_power": Input(43.0, "W/m3", "[Humbird-R, derived] the stirring power behind the mixing time (see "
        "pf_mix_ratio_20m3)"),
    "ge_nozzle_velocity": Input(3.0, "m/s", "[assumed] speed of the loop's return flow entering the tank"),
    "ge_co2_frac": Input(0.5, "-", "[design choice] how far one pass takes the liquid's CO2 towards the sweep gas",
        lo=0.3, hi=0.8, mode=0.5, note="more per pass: fewer passes, longer fibres, a larger pH swing in the loop"),
    "ge_sweep_pco2": Input(10.0, "mbar", "[design choice] average CO2 pressure in the sweep gas (air swept at "
        "about ten times the flow a sparger would use, or less in counter-current)"),
    "ge_bore_mm": Input(0.5, "mm", "[Clincke et al. 2013, read in full] bore of the hollow fibres CHO cells were "
        "pumped through at over 10^8 cells/mL: 1 mm (microfiltration) and 0.5 mm (ultrafiltration)",
        lo=0.5, hi=1.0, mode=0.5, note="those were filters, not gas-exchange fibres; area scales with the bore"),
    "ge_shear": Input(1000.0, "1/s", "[Clincke et al. 2013, read in full] wall shear rate in the fibres: 1,000 to "
        "3,400 per second had 'no impact ... on CHO cell growth, viability, and metabolism' in 4-litre runs of "
        "up to 48 days at 15 tank volumes an hour", lo=500.0, hi=3400.0, mode=1000.0,
        note="CHO only; nothing for muscle, fibroblast or fish cells"),
    "ge_wall_um": Input(100.0, "um", "[assumed] wall of a dense silicone (PDMS) fibre; 0 would be a microporous "
        "wall with no resistance", note="silicone is the material that survives steam; microporous polypropylene "
        "contactors are limited to 85 C hot water and no surfactants (3M Liqui-Cel cleaning guide, read in full)"),
    "ge_pdms_co2": Input(3250.0, "Barrer", "[memory; search results give 3,190-3,970] CO2 permeability of PDMS",
        note="1 Barrer = 3.35e-16 mol m / (m2 s Pa). Not read in a primary source"),
    "ge_pdms_o2": Input(600.0, "Barrer", "[vendor data sheet, search result] O2 permeability of PDMS"),
    "ge_headloss_x": Input(2.0, "x", "[assumed] pressure drop of the whole loop over that of the fibres alone"),
    "ge_pump_eff": Input(0.6, "-", "[assumed] pump efficiency"),
    "ge_power_price": Input(0.08, "$/kWh", "[assumed] industrial electricity"),
    "ge_cost_m2": Input(200.0, "$/m2", "[distributor listings, Nov 2026] large polypropylene gas-exchange "
        "contactors list at about $160-265 per m2 (Liqui-Cel EXF 8x20 and 10x28 complete units; areas from memory); "
        "CO2-capture studies assume $50-200 (search results)", lo=80.0, hi=1480.0, mode=200.0,
        note="AN OPTIMISTIC ASSUMPTION: it is the price of modules that cannot be steamed (polypropylene, hot water "
             "to 85 C only). The one priced silicone module, which the design uses, is $704 per m2 at 2.1 m2 "
             "(PermSelect web store, Nov 2026) and may be steamed once only. No module both survives repeated "
             "steaming and has a published price. hi = the pharma ATF-10 filter (Humbird: $16,300 for 11 m2)"),
    "ge_life_y": Input(2.0, "years", "[judgement] life of the membranes in a culture that fouls them and is "
        "sterilised between runs", lo=0.1, hi=5.0, mode=2.0,
        note="lo = one 33-day run, which is the life of a module that may be steamed only once (PermSelect "
             "silicone). Silicone and PMP lungs last about 2-4 weeks in blood (search results); microporous "
             "polypropylene leaks within hours to days in protein-rich liquid. 3-5 years in gas-separation service"),
    "ge_install_x": Input(3.0, "x", "[CE Delft 2021, via research_notes/plant_capital_crosscheck.md] installed and "
        "engineered cost over purchased cost for food-grade equipment (an overall Lang factor of about 3)"),
    "ge_pump_cost": Input(30.0e3, "$", "[assumed] a low-shear sanitary pump for ge_pump_flow; no price was found",
        note="a 7.5-15 HP sanitary centrifugal pump lists at about $10k (search result)"),
    "ge_pump_flow": Input(300.0, "m3/h", "[assumed] the flow ge_pump_cost refers to; cost scales as flow^0.6"),
    "ge_k_submerged": Input(2.0e-5, "m/s", "[assumed order of magnitude] liquid-film coefficient at a membrane "
        "hung in a stirred tank", note="for comparison, unmodified fibres in saline at 67 mbar of CO2 removed 75-92 "
        "mL/min per m2 (Kimmel 2013, Arazawa 2015), which is 3.4-4.1e-5 m/s with buffer helping"),
    "ge_tubing_od_mm": Input(3.0, "mm", "[Frahm et al. 2009, read in full] outer diameter of the silicone tubing "
        "used for bubble-free aeration up to 200 L, at 30-68 m2 of tubing per m3"),
    "ge_head_area": Input(1.084, "x D^2", "[textbook] surface of a 2:1 elliptical vessel head"),
    "ge_vessel_cost_exp": Input(0.6, "-", "[Seider et al. 2017, read as code in BioSTEAM] exponent of vessel cost "
        "on shell weight: Cv = exp(7.139 + 0.18255 ln W + 0.02297 (ln W)^2) for vertical vessels, W in lb, whose "
        "slope at the 8,000 lb of a 20 m3 tank is 0.60",
        note="the same source prices a horizontal vessel a third below a vertical one of equal weight"),
    "ge_hall_share": Input(0.131, "of direct cost", "[Humbird-R, derived] the sanitary cell-culture hall's share of "
        "the plant: $20.9M of $159.5M (see pf_capex_no_cleanroom)"),
    "ge_clearance_m": Input(2.0, "m", "[assumed] floor taken per tank is (width + this)^2"),
    "ge_kill_protected": Input(4.0e-4, "L of culture per L of gas", "[Jobses, Martens, Tramper 1991, read in full] "
        "volume of culture whose cells die per volume of gas sparged, hybridoma with 1 g/L Pluronic F68: death "
        "rate 0.05 per hour at 10 L/h of gas through 80 mL", lo=4.0e-4, hi=3.2e-3, mode=4.0e-4,
        note="death rate = this x gas flow per litre of culture ('the cell death rate is linearly proportional to "
             "the gas flow rate per unit volume'); independent of sparger and, in Tramper 1988, of bubble size. "
             "hi = the same at 0.1 g/L (0.4 per hour). 3 cm columns, 4-6 mm bubbles, 2.0-12 cm deep: a long "
             "extrapolation to 20 m3"),
    "ge_kill_unprotected": Input(8.8e-3, "L of culture per L of gas", "[Jobses et al. 1991, read in full] the same "
        "with no protectant: 1.1 per hour", note="Tramper et al. 1988 give 4e-3 for insect cells"),
    "ge_alr_volume": Input(261.754, "m3", "[Negulescu et al. 2023, read in full] 'the ALR is 261,754 L with a "
        "working volume of 209,404 L'"),
    "ge_alr_our": Input(10.3, "mmol O2/L/h", "[Negulescu et al. 2023, read in full] oxygen uptake 'of about 10.3 "
        "mmol O2/L/hr ... based on the maximum cell concentration of 100 g FW/L'; CO2:O2 set to 1.2",
        note="0.103 mmol per g per hour, 31% below the model cell's 0.149 for the same 3 ng cell"),
    "ge_alr_li_height": Input(13.75, "m", "[Negulescu et al. 2023, read in full, describing Li et al. 2020] 'a 300 "
        "m3, 13.75 m tall airlift reactor'; Negulescu gives no dimensions for its own"),
    "ge_alr_li_volume": Input(300.0, "m3", "[as above]"),
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

    # --- plant capital by item (plant_items.py; research_notes/cheap_plant_study.md) -------------------
    # Humbird's fed-batch plant (24 x 20 m3) transcribed line by line, his yeast plant, and the options each
    # item can be switched to. 2018 dollars, $k, unless stated. [Humbird-R] = the long report, read in full text.
    "pi_n_tanks": Input(24.0, "tanks", "[Humbird-R] Table 4.1: 24 x 20 m3 production bioreactors"),
    "pi_tank_m3": Input(20.0, "m3", "[Humbird-R] Table 4.1: production bioreactor volume"),
    "pi_prod_installed": Input(33922.0, "$k", "[Humbird-R] Table 4.1: production bioreactors (F5), installed; "
        "= 24 x Eq. 3.1 (30.7 x 20 + 800 = $1,414k each)"),
    "pi_seed_installed": Input(22673.0, "$k", "[Humbird-R] Table 4.1: seed bioreactors, '24 x 16 m3 and smaller', "
        "installed", note="24 vessels = 4 trains x (150 L, 550 L, 2.1, 8.1 and 2 x 15.6 m3) (Fig. 4.3 and text); "
        "Eq. 3.1 on these gives $22.72M, 0.2% above the table"),
    "pi_bioreactor_bare": Input(13794.0, "$k", "[Humbird-R] Table 4.1 note a: bare equipment cost of all 48 "
        "bioreactors; reproduced by his note 127, $k = 51 x V^0.69"),
    "pi_fill_tanks": Input(1660.0, "$k", "[Humbird-R] Table 4.1: initial fill tanks, 14 x 20 m3 and smaller, bare"),
    "pi_htst": Input(702.0, "$k", "[Humbird-R] Table 4.1: HTST sterilisers, 14 x 4,950 L/h and smaller, bare"),
    "pi_makeup_tanks": Input(3370.0, "$k", "[Humbird-R] Table 4.1: makeup tanks, 72 x 2.8 m3 and smaller (one per "
        "bioreactor, production and seed), bare"),
    "pi_filter_housings": Input(1481.0, "$k", "[Humbird-R] Table 4.1: filter housings, 216 x 0.7 m2 and smaller, bare"),
    "pi_centrifuge": Input(1744.0, "$k", "[Humbird-R] Table 4.1: disk-stack centrifuges, 4 x 35 gpm, bare"),
    "pi_vpsa": Input(8840.0, "$k", "[Humbird-R] Table 4.1: oxygen plant (vacuum pressure-swing adsorption), 25 kt "
        "of oxygen a year, bare", note="Pasitka 2024 (SI Table S2) prices a 15 kt/yr unit at $1,991k: 4.4 times "
        "less for 60% of the capacity"),
    "pi_o2_compressor": Input(295.0, "$k", "[Humbird-R] Table 4.1: oxygen compressor, bare"),
    "pi_boiler": Input(154.0, "$k", "[Humbird-R] Table 4.1: natural-gas boiler, bare"),
    "pi_cip_tanks": Input(4136.0, "$k", "[Humbird-R] Table 4.1: clean-in-place tanks, 12 x 42 m3, bare"),
    "pi_chiller": Input(551.0, "$k", "[Humbird-R] Table 4.1: chiller, bare"),
    "pi_cooling_tower": Input(24.0, "$k", "[Humbird-R] Table 4.1: cooling tower, bare"),
    "pi_missing": Input(0.10, "share", "[Humbird-R] Sect. 3.1 and Table 4.1: 10% of equipment cost for minor items "
        "not listed (pumps and the like)", note="taken on the total including itself: allowance = listed / 0.9 - "
        "listed. In the ISBL the listed base includes the installed bioreactors; both reproduce Table 4.1"),
    "pi_install": Input(1.3, "x bare", "[Humbird-R] Sect. 3.1: installation of equipment other than bioreactors, "
        "added on top of the bare cost (so installed = 2.3 x bare)"),
    "pi_engineering": Input(0.6, "x direct", "[Humbird-R] Table 4.3: engineering and construction, 0.6 x total "
        "direct cost"),
    "pi_fees": Input(0.15, "x plant cost", "[Humbird-R] Table 4.3: contractor's fee and contingency, 0.15 x total "
        "plant cost"),
    "pi_bldg_hall": Input(39607.0, "$k", "[Humbird-R] Table 4.2: cell-culture hall, Class 8 clean room, 5,268 m2 on "
        "2 levels ('15% occupied by major equipment')"),
    "pi_bldg_cell_lab": Input(2575.0, "$k", "[Humbird-R] Table 4.2: cell lab, Class 6, 294 m2"),
    "pi_bldg_qc_lab": Input(1287.0, "$k", "[Humbird-R] Table 4.2: quality-control lab, Class 6, 147 m2"),
    "pi_bldg_office": Input(527.0, "$k", "[Humbird-R] Table 4.2: office, 318 m2"),
    "pi_bldg_compressor": Input(162.0, "$k", "[Humbird-R] Table 4.2: compressor building, 63 m2 on 2 levels"),
    "pi_bldg_shop": Input(1648.0, "$k", "[Humbird-R] Table 4.2: maintenance shop, 1,317 m2 (25% of the hall)"),
    "pi_bldg_warehouse": Input(1491.0, "$k", "[Humbird-R] Table 4.2: warehouse, 1,317 m2 (25% of the hall)"),
    "pi_bldg_slab": Input(1185.0, "$k", "[Humbird-R] Table 4.2: slab under the whole developed area, 8,724 m2"),
    "pi_rate_class8": Input(3760.0, "$/m2-level", "[Humbird-R] Table 3.2: Class 8 clean room"),
    "pi_rate_sanitary": Input(1980.0, "$/m2-level", "[Humbird-R] Table 3.2: sanitary building"),
    "pi_rate_warehouse": Input(1130.0, "$/m2-level", "[Humbird-R] Table 3.2: warehouse"),
    "pi_eq31_slope": Input(30.7, "$k/m3", "[Humbird-R] Eq. 3.1: installed cost of a sterile bioreactor, $k = 30.7 V "
        "+ 800 for V >= 0.33 m3"),
    "pi_eq31_fixed": Input(800.0, "$k", "[Humbird-R] Eq. 3.1: the fixed part (piping, instruments), per vessel"),
    "pi_eq31_small_slope": Input(2285.0, "$k/m3", "[Humbird-R] Eq. 3.1 below 0.33 m3: $k = 2285 V + 49.5"),
    "pi_eq31_small_fixed": Input(49.5, "$k", "[Humbird-R] Eq. 3.1 below 0.33 m3"),
    "pi_bare_coef": Input(51.0, "$k", "[Humbird-R] note 127: bare bioreactor cost $k = 51 x V^0.69"),
    "pi_bare_exp": Input(0.69, "exponent", "[Humbird-R] note 127"),
    # Table 3.3: what the installed cost of one sterile 20 m3 bioreactor is made of
    "pi_t33_vessel": Input(330.0, "$k", "[Humbird-R] Table 3.3, 20 m3: vessel and agitator"),
    "pi_t33_piping": Input(360.0, "$k", "[Humbird-R] Table 3.3, 20 m3: piping (sterile feeds, steam, CIP)"),
    "pi_t33_instr": Input(476.0, "$k", "[Humbird-R] Table 3.3, 20 m3: instruments and electrical; probes are "
        "three times redundant (his note 92)"),
    "pi_t33_other": Input(22.0, "$k", "[Humbird-R] Table 3.3, 20 m3: other direct cost"),
    "pi_t33_internals": Input(164.0, "$k", "[Humbird-R] Table 3.3, 20 m3: sparger, spray balls, exhaust heater, "
        "double mechanical seal"),
    "pi_t33_surface": Input(132.0, "$k", "[Humbird-R] Table 3.3, 20 m3: electropolishing and acid passivation"),
    # the seed train of the fed-batch plant: vessel sizes (m3), per train (Fig. 4.3)
    "pi_seed_trains": Input(4.0, "trains", "[Humbird-R] Sect. 4.1: 'four identical trains ending with 6 x F5'"),
    "pi_seed_f0_m3": Input(0.15, "m3", "[Humbird-R] Sect. 4.1: 'F0, a single 150 L seed bioreactor inoculated with "
        "3 kg of cells prepared in the lab'"),
    "pi_seed_f1_m3": Input(0.55, "m3", "[Humbird-R] Fig. 4.3: F1"),
    "pi_seed_f2_m3": Input(2.1, "m3", "[Humbird-R] Fig. 4.3: F2"),
    "pi_seed_f3_m3": Input(8.1, "m3", "[Humbird-R] Fig. 4.3: F3"),
    "pi_seed_f4_m3": Input(15.6, "m3", "[Humbird-R] Fig. 4.3: F4, two per train; each fills three production tanks"),
    "pi_seed_tanks_per_f4": Input(3.0, "tanks", "[Humbird-R] Fig. 4.3: an F4 batch of 1,445 kg seeds three "
        "production tanks at 482 kg (36.5 g/L)"),
    "pi_stage_h": Input(57.0, "h", "[Humbird-R] Sect. 4.1: a stage takes 48 h of growth (two doublings) plus 2 h to "
        "drain, 4 h to clean and sterilise and 4 h to refill; seeds are assumed to run the same cycle"),
    # Humbird's baker's-yeast plant (Appendix A)
    "pi_yeast_bcr_200": Input(818.0, "$k", "[Humbird-R] Table A.1: one 200 m3 jacketed bubble column in 316L steel, "
        "bare"),
    "pi_yeast_seed": Input(1369.0, "$k", "[Humbird-R] Table A.1: seed train of the standard plant (0.5, 3.4, 24 and "
        "2 x 85 m3, Fig. A.4a), bare; not itemised"),
    "pi_yeast_pasteurizer": Input(221.0, "$k", "[Humbird-R] Table A.1: pasteuriser for the molasses feed, bare"),
    "pi_yeast_prep_tank": Input(593.0, "$k", "[Humbird-R] Table A.1: preparation tank, bare"),
    "pi_yeast_compressors": Input(2750.0, "$k", "[Humbird-R] Table A.1: two air compressors, bare"),
    "pi_yeast_centrifuges": Input(1728.0, "$k", "[Humbird-R] Table A.1: two centrifuges, bare"),
    "pi_yeast_rvf": Input(652.0, "$k", "[Humbird-R] Table A.1: two rotary vacuum filters, bare"),
    "pi_yeast_missing": Input(0.20, "x listed", "[Humbird-R] Table A.1: minor items, 20% of purchased equipment "
        "($3,055k of $15,276k), so purchased = listed / 0.8"),
    "pi_yeast_lang": Input(4.5, "x equipment", "[Humbird-R] Table A.1: overall factor from purchased equipment to "
        "total investment", note="Table 3.1's 'non-sterile outdoors (lysine)' column sums to 4.7; he uses 4.5"),
    "pi_yeast20_capex": Input(70000.0, "$k", "[Humbird-R] Table A.5: the yeast process held to animal-cell limits "
        "(growth rate 0.03/h, oxygen transfer 25 mol/m3/h): 27 x 20 m3 fermentors, 'Total CAPEX $70M'",
        note="NOT ITEMISED by Humbird, and the column is headed 'equal CAPEX' (the standard plant is $68.7M), so "
             "the figure is rounded and partly set by construction. plant_items rebuilds it from Table A.1"),
    "pi_yeast20_tanks": Input(27.0, "tanks", "[Humbird-R] Table A.5 and Fig. A.4b: 27 x 20 m3 production fermentors; "
        "seeds of 9 x 19, 3 x 18.5, 18 and 6 m3 (the list is in plant_items.YEAST20_SEED_M3)"),
    "pi_yeast_output_ratio": Input(1.7 / 17.3, "ratio", "[Humbird-R] Table A.5: yeast made, constrained over "
        "standard plant (1.7 against 17.3 kt a year)"),
    "pi_yeast_oxygen_ratio": Input(25.0 * 540.0 / (150.0 * 1200.0), "ratio", "[Humbird-R] Table A.5: oxygen "
        "transferred, constrained over standard: 25 against 150 mol/m3/h, in 540 against 1,200 m3"),
    "pi_yeast_broth_ratio": Input((1.7 / 25.0) / (17.3 / 69.0), "ratio", "[Humbird-R] Table A.5: broth to dewater, "
        "constrained over standard: yeast made / cell density (25 against 69 g/L)"),
    "pi_yeast_feed_ratio": Input(1.7 * 0.89 / (17.3 * 0.72), "ratio", "[Humbird-R] Table A.5: molasses handled, "
        "constrained over standard: yeast made x carbon cost per kg ($0.89 against $0.72)"),
    "pi_scale_exp": Input(0.6, "exponent", "[assumed] the six-tenths rule for scaling equipment cost with capacity, "
        "the standard default in process cost estimating (Negulescu 2023 uses it for bioreactors)",
        lo=0.5, hi=0.7, mode=0.6,
        note="used to resize the yeast plant's compressors, centrifuges, filters and feed equipment from the "
             "standard to the constrained plant. The vessel exponent is not assumed: it is solved so that the "
             "rebuilt plant costs Humbird's $70M (about 0.49)"),
    # Table 3.1, 'non-sterile outdoors (lysine)': what the yeast plant's overall factor is made of
    "pi_lys_install": Input(0.29 + 0.38 + 0.40, "x equipment", "[Humbird-R] Table 3.1, lysine column: installation "
        "0.29 + process piping 0.38 + instruments and electrical 0.40"),
    "pi_lys_buildings": Input(0.10 + 0.10, "x equipment", "[Humbird-R] Table 3.1, lysine column: buildings 0.10 + "
        "site improvement 0.10"),
    "pi_lys_aux": Input(0.30, "x equipment", "[Humbird-R] Table 3.1, lysine column: auxiliary facilities "
        "(utilities)"),
    # options for animal cells that are neither Humbird's nor the yeast plant's
    "pi_vessel_food_k": Input(1000.0, "$k per 20 m3 tank", "[company claim, trade press] Vow: its 20,000 L "
        "food-grade tank cost 'well under $1 million' (AgFunder 2025, full text; Lever VC 2025 reads it as 80% "
        "below a pharma-specification system)", lo=450.0, hi=1414.0, mode=1000.0,
        note="taken as an UPPER bound for a sterilisable food-grade stirred tank, installed, against Humbird's "
             "$1,414k. Cross-checks: Humbird's Table 3.3 without electropolishing and with single probes is about "
             "$1,190k; CE Delft 2021 prices a 12.5 m3 tank at $325k purchased; Negulescu 2023 starts from $300k "
             "for a 20 m3 tank in 304 steel. lo: about the yeast-plant vessel with its installation. Whether "
             "'under $1 million' includes piping and installation is not stated"),
    "pi_o2_feed": Input(3.3, "kg O2/kg wet cells", "[Humbird-R, derived] Table 4.4: the oxygen plant draws 2,139 "
        "kWh per batch of 1,849 kg; at about 0.35 kWh per kg of oxygen [assumed, typical for the technology] that "
        "is 6.1 t of oxygen fed per batch, consistent with a 25 kt/yr plant serving 3,600 batches",
        note="most of the oxygen fed leaves unused: the cells burn about 0.3 kg per kg"),
    "pi_o2_price": Input(0.10, "$/kg", "[assumed] oxygen bought over the fence or as bulk liquid; not sourced "
        "(industrial gas prices are contract prices and rarely published)", lo=0.05, hi=0.20, mode=0.10,
        note="at 3.3 kg per kg of cells this is $0.33 per kg of cells, against about $1.5 per kg for owning "
             "Humbird's oxygen plant at his capital loading. A judgement, flagged as such in the note"),

    # --- contamination as dynamics (contamination.py; research_notes/cheap_plant_study.md) ----------------
    "ct_doubling_fast_min": Input(20.0, "min", "[BioNumbers 103514, search result] E. coli in rich broth at 37 C",
        note="the fast end. Doubling times of contaminants in cell-culture medium were looked for and not found"),
    "ct_doubling_slow_min": Input(60.0, "min", "[assumed] a slower common contaminant (many environmental bacteria "
        "and yeasts double in 40 to 90 minutes in rich medium)"),
    "ct_doubling_cryptic_h": Input(6.0, "h", "[Fratz-Berilla et al. 2019, Biotechnol. Bioeng., full text] "
        "Mycoplasma arginini in a CHO perfusion culture: doubling 'about 6 h or more'; from 15-300 CFU/mL it "
        "reached about 1e7 CFU/mL in 2-3 days, and oxygen and CO2 readings moved 1-5 days after the spike"),
    "ct_bact_qo2": Input(15.0, "mmol O2/g dry/h", "[from memory, textbook range 10-20 for E. coli growing fast; "
        "not verified at source]", lo=5.0, hi=20.0, mode=15.0),
    "ct_bact_dry_pg": Input(0.3, "pg dry per cell", "[from memory, BioNumbers: an E. coli cell is about 0.3 pg dry "
        "(1 pg wet); not verified at source]", lo=0.15, hi=1.0, mode=0.3),
    "ct_detect_shift": Input(0.05, "share", "[assumed] the change in a tank's oxygen uptake that its oxygen "
        "control or off-gas reading shows clearly above noise", lo=0.01, hi=0.10, mode=0.05,
        note="sets the contaminant density at which ordinary sensors see it; a factor of 5 either way moves "
             "the time to detection by only about 2 doublings out of about 50"),
    "ct_inoculum_cfu": Input(1.0, "cells", "[assumed] a contamination starts from a single cell; a hundred cells "
        "would show under 7 doublings sooner"),
    "ct_food_limit_cfu": Input(1e4, "CFU/g", "[FSANZ A1269 risk assessment, April 2025, full text] Vow's harvest "
        "specification: standard plate count under 1e4 per gram",
        note="UPSIDE's is under 100 and GOOD Meat's under 1,000 (FDA memos, full text). Raw meat at the end of "
             "its shelf life carries 1e6 to 1e7. These are company-proposed limits, not law"),
    "ct_start_detect_days": Input(1.0, "days", "[Linderholm et al. 2025, Anal. Bioanal. Chem., search result] "
        "'gross contamination' is detected after 18-24 h at the earliest; contamination.time_to_detect_h gives "
        "0.7 to 2 days for doubling times of 20 to 60 minutes", lo=0.7, hi=5.0, mode=1.0,
        note="how long a tank started from a contaminated seed runs before it shows. hi: slow organisms"),
    "ct_seed_share": Input(36.5 / 120.0, "of a tankful", "[Humbird-R] Sect. 4.1: a tank is started at 36.5 g/L and "
        "harvested at 120, so a start that fails loses about 0.3 of a tankful of cells"),
    "ct_batch_loss_pharma": Input(0.023, "of batches", "[Langer 2008, BioProcess Int., full text] BioPlan survey of "
        "145 organisations: 2.3% of batches lost to contamination in plants above 1,000 L (7.6% from all causes); "
        "3.2% in the 2022 survey as quoted by GFI",
        note="over a 10-14 day production batch [typical length, from memory] this is 0.15-0.3% a day, the "
             "basis of pf_hazard_pharma"),
    "ct_batch_loss_cm": Input(0.112, "of batches", "[Powell et al. 2025, Compr. Rev. Food Sci. Food Saf., full "
        "text] survey of cultivated-meat makers, May-July 2023: mean 11.2% of batches lost to contamination in the "
        "past year (range 0-52%, 11 companies)", lo=0.0, hi=0.52, mode=0.112,
        note="19.5% for the 6 companies beyond flask scale (ct_batch_loss_cm_scaled). Run lengths and tank sizes "
             "are not reported, so no rate per day follows without assuming them"),
    "ct_batch_loss_cm_scaled": Input(0.195, "of batches", "[Powell et al. 2025, full text] the same survey without "
        "the four companies working only in flasks: mean 19.5% (6 companies)"),
    "ct_hazard_frontier": Input(0.015, "per day", "[derived, with an assumed run length] the survey's 11.2-19.5% of "
        "batches, if those ran 10-20 days: about 0.6 to 2.2% a day; 1.5% is the round middle",
        lo=0.006, hi=0.022, mode=0.015),

    # --- Cost scenarios (scenarios.py): the settings of each switch -------------------------------------
    # Each switch on the page's "what decides it" panel has a few settings; every number a setting fixes is
    # registered here with its source and plausible range. The scenarios are presets of these switches
    # (scenarios.py), so no scenario carries a number of its own. Evidence: research_notes/cost_scenarios.md.
    "sc_nh3_engineered": Input(0.055, "mol/kg wet", "[Humbird-R, derived; waste_tricks_sizing.md] ammonia made by "
        "engineered cells: his enhanced cell, 0.054, rounded; seen only in engineered (glutamine-synthetase) CHO",
        lo=0.054, hi=0.14, mode=0.055,
        note="GENETIC ENGINEERING. The CHO plateau rate that clears this (0.54 fmol/cell/h) is an upper bound "
             "from cells that were not net-growing; nothing at a 24 h doubling"),
    "sc_nh3_selected": Input(0.14, "mol/kg wet", "[Hubalek et al. 2023, full text; waste_tricks_sizing.md] ammonia "
        "made by bovine fibro-adipogenic cells when glutamine is replaced by alpha-ketoglutarate, pyruvate or "
        "glutamate: 'more than 5-fold' below the 0.70 with glutamine, so under 0.14",
        lo=0.07, hi=0.25, mode=0.14,
        note="FEED CHANGE, then SELECTION. Measured once, in one cell type, in spinner flasks; the same paper's "
             "shaker value for ordinary cells is ten times lower than its spinner value, cause unexplained"),
    "sc_nh3_ordinary": Input(0.70, "mol/kg wet", "[Hubalek et al. 2023, full text] the same cells with glutamine: "
        "56.3 fmol/cell/h at a 25.7 h doubling", lo=0.09, hi=0.95, mode=0.70,
        note="0.09 is the same paper's shaker value; 0.95 is Humbird's ordinary wild-type cell"),
    "sc_lac_engineered": Input(0.5, "mol lactate / mol glucose", "[Humbird-R] his stated lactate:glucose ratio for "
        "enhanced cells", lo=0.1, hi=0.5, mode=0.5,
        note="GENETIC ENGINEERING for values near 0 (knocked-out genes); 0.5 is his assumption"),
    "sc_lac_selected": Input(0.42, "mol lactate / mol glucose", "[waste_tricks_sizing.md] 0.39 was reached by "
        "adapting CHO to low-lactate culture; 0.42 allows a little for meat cells, for which nothing is measured",
        lo=0.39, hi=0.6, mode=0.42,
        note="SELECTION OR ADAPTATION. No value for muscle, fat or fish cells has been published"),
    "sc_lac_measured": Input(1.05, "mol lactate / mol glucose", "[Pasitka et al. 2024, snippet; "
        "waste_tricks_sizing.md] chicken cells in perfusion; bovine cells similar", lo=0.8, hi=1.4, mode=1.05,
        note="ordinary pharma cells make about 1.4"),
    "sc_glc_measured": Input(0.84, "mol glucose/kg wet", "[waste_tricks_sizing.md, from Hubalek 2023 and the "
        "chicken data] glucose used per kg of meat cells grown", lo=0.67, hi=1.2, mode=0.84,
        note="Humbird's efficient cell uses 1.116 (pf_glc_kg); measured pharma cells 0.67-1.0. Unmeasured for "
             "meat cells at density"),
    "sc_mass_selected_pg": Input(2000.0, "pg wet per cell", "[judgement] between the 1.0-1.75 ng reported for "
        "chicken cells (SuperMeat 2024) and Humbird's 3 ng; no mass was found for the bovine cells",
        lo=1000.0, hi=3000.0, mode=2000.0,
        note="smaller cells respire more per gram (West's law), so the tank holds fewer of them. Used for every "
             "cell setting except the engineered one, which is Humbird's cell"),
    "sc_td_central": Input(36.0, "h", "[Hubalek et al. 2023; judgement] the speed taken for cells that make this "
        "little waste by selection and feed alone: cells with glutamine replaced doubled in 42.9-54.2 h "
        "(38 h unchanged, 25.7 h in the spinner), never 24 h", lo=26.0, hi=43.0, mode=36.0,
        note="MY ODDS (labelled judgement): 24 h together with ammonia at or below 0.14 about 10%; 30 h or "
             "faster about 25%; 36 h or faster about 45%; 43 h or faster about 70%. Selection acts most directly "
             "on growth rate, so the central value sits nearer the ordinary cells' speed than the measured one"),
    "sc_td_fast": Input(30.0, "h", "[judgement] a third setting between the engineered 24 h and the central 36 h",
        lo=26.0, hi=36.0, mode=30.0),
    "sc_td_measured": Input(43.0, "h", "[Hubalek et al. 2023, full text] 42.9 h: the best low-ammonia culture "
        "measured in meat cells (bovine, alpha-ketoglutarate)", lo=38.0, hi=54.0, mode=43.0,
        note="DTs 42.9 / 47.6 / 48.8 / 54.2 h with glutamine replaced; difference from 38.0 h not significant, n = 5"),
    "sc_gas_mid": Input(0.004, "m/s", "[research_notes/gas_flow_cap.md] a middle setting for the gas the cells "
        "tolerate: twice the 2 mm/s run in 8-20 m3 tanks (Nienow 2006), two thirds of Humbird's 6", lo=0.002, hi=0.006,
        mode=0.004, note="needs a protectant and foam control; nobody has run dense cells at this gas flow at 20 m3"),
    "sc_gas_low": Input(0.002, "m/s", "[Nienow 2006, full text; gas_flow_cap.md] about the most gas that has been "
        "run with cells in 8-20 m3 tanks", lo=0.001, hi=0.004, mode=0.002),
    "sc_hazard_mid": Input(0.006, "per day", "[Powell et al. 2025; ct_hazard_frontier] the low end of the loss "
        "rate the survey of makers implies (0.6-2.2% a day if batches ran 10-20 days)", lo=0.002, hi=0.015, mode=0.006),
    "sc_hazard_cm": Input(0.01, "per day", "[Powell et al. 2025, full text; assumed run length] 11.2-19.5% of "
        "batches lost, about 1% a day if runs last 10-20 days", lo=0.006, hi=0.022, mode=0.01),
    "sc_hazard_high": Input(0.02, "per day", "[Powell et al. 2025] the upper end of what makers report",
        lo=0.015, hi=0.022, mode=0.02),
    # --- a stirred tank with the sparger inside a fine-mesh inner cylinder (vessels.py "caged"; Pablo's design, 2026-11-16) ---
    "vm_cage_exchange": Input(0.8, "-", "[judgement] how much of the gas exchange inside the cage reaches the cells' ring: oxygen "
        "and CO2 move between the two only with the medium that crosses the mesh",
        lo=0.5, hi=1.0, mode=0.8,
        note="caged aeration surrounds the sparger with a fine mesh so cells never meet bubbles (bench and pilot microcarrier "
             "cultures, with mesh of about 85 um; a BioProcess International review, search summary). Single cells of 10-20 um "
             "need mesh finer than that, which fouls. No exchange rate between cage and bulk was found; 1 = as if the "
             "whole tank were sparged."),
    "vm_cage_gas": Input(0.006, "m/s", "[judgement, gas_flow_cap.md] gas bubbled inside the cage, as a velocity over the whole tank's "
        "cross-section; bubbles there never touch cells, so only foam and gas handling cap it. Added, after the mesh discount, to "
        "the soft bubbling in the cells' ring", lo=0.003, hi=0.012, mode=0.006),
    "vm_cage_capex_ratio": Input(1.15, "x stirred tank", "[judgement] a stirred tank plus the mesh cylinder: a patent "
        "notes that large fine-mesh parts for gas exchange could be very costly to make", lo=1.05, hi=1.4, mode=1.15),
    "sc_restart_neighbour": Input(4.0, "days", "[arithmetic, judgement] a lost tank reseeded with half the culture of a healthy "
        "neighbouring tank, in place of a new seed train: about 2 days to empty, clean and steam the tank, about 1 doubling to regrow "
        "both tanks to working density, and the neighbour's lost output counted as about 1 more day of the lost tank's time",
        lo=3.0, hi=7.0, mode=4.0,
        note="Pablo's question (2026-11-16): why 14 days and not 1? Regrowing from a seed at about 1 g/L to 120 g/L is about 7 doublings, "
             "7-10 days at 24-36 h, plus cleaning and checks; a neighbour's dense culture skips most of that. The risk is a donor carrying "
             "a contaminant not yet detected (a fast contaminant shows on oxygen readings only after 17-51 h, cheap_plant_study.md), so the "
             "donor must test clean first. Needs several tanks running; nobody has reported doing it with animal cells at scale."),
    "sc_restart_base": Input(14.0, "days", "[contamination.py; Humbird-R Sect. 4.1 seed train] two weeks to clean, "
        "re-sterilise and regrow the seed after a lost run", lo=7.0, hi=30.0, mode=14.0),
    "sc_restart_slow": Input(21.0, "days", "[plant_items.py, contamination.py] a plant that loses its seed trains "
        "needs three weeks to sterilise and regrow", lo=14.0, hi=30.0, mode=21.0),
    "sc_restart_long": Input(30.0, "days", "[contamination.common_mode_restart_days] a month: one failure that "
        "reaches every tank", lo=21.0, hi=60.0, mode=30.0),
    "sc_gf_part": Input(0.3, "of Humbird's growth-factor cost", "[judgement; Humbird-R, Sect. 3.1 price of "
        "large-scale growth factors] cheaper factors or cells that need fewer: 30% of his price per litre",
        lo=0.0, hi=1.0, mode=0.3,
        note="his price assumes an industry far larger than today's; cells that make their own were shown in "
             "cattle cells by genetic engineering"),
    "sc_gf_most": Input(0.6, "of Humbird's growth-factor cost", "[judgement] most of his price", lo=0.0, hi=1.0,
        mode=0.6),
    "sc_medium_aspire": Input(0.05, "$/L", "[Pablo's aspiration, 2026-11-15; GFI Dec 2025] a medium at $0.05 a litre: GFI puts "
        "amino acids alone at $0.02-0.17 a litre and the lowest company report at $0.07 (Clever Carnivore, unaudited)",
        lo=0.03, hi=0.10, mode=0.05,
        note="an aspiration, not a figure anyone has reported. Below about $0.06 the model's nutrient floor ($1.70 a kilo) binds, "
             "so this setting prices medium at the floor; nutrient_floor.py shows the floor is probably higher"),
    "sc_medium_mid": Input(0.20, "$/L", "[GFI 2026 industry report, p.8] several companies announced media costs at "
        "$0.20/L or below in 2025", lo=0.15, hi=0.5, mode=0.20,
        note="company announcements, not verified at scale. GFI's amino acid analysis (Dec 2025, read in full) puts amino acids at "
             "$0.02-0.17/L and cites Meatly and Gourmey at about $0.20, Clever Carnivore at $0.07 and Believer's measured "
             "$0.63; see research_notes/medium_cost_gfi.md"),
    "sc_medium_high": Input(0.30, "$/L", "[judgement] between the announced $0.20 and the $0.50 SuperMeat reports",
        lo=0.2, hi=0.5, mode=0.30),
    "sc_aspect_flat": Input(0.5, "depth/width", "[gas_exchange.cheapest_tricks] the squattest shape its search "
        "considers: liquid half as deep as wide (a horizontal or wide, shallow vessel)", lo=0.5, hi=0.75, mode=0.5,
        note="gives the most gas per litre; steel and floor counted; no cost data on tank shape"),
    "sc_aspect_squat": Input(0.75, "depth/width", "[gas_exchange_study.md] a squat tank: liquid 0.75 times as deep as "
        "wide, the cheapest shape the search finds when the gas cap is high", lo=0.5, hi=1.0, mode=0.75,
        note="its extra steel and floor are counted (gas_exchange.shape_capex_factor); no cost data on tank shape"),
    "sc_aspect_mid": Input(1.0, "depth/width", "[judgement] a squarer tank than Humbird's 1.6", lo=0.75, hi=1.6,
        mode=1.0),
    "sc_p_top": Input(1.0, "bar gauge", "[gas_exchange_study.md; vendor data sheets] pressure at the top of the tank "
        "when the pressure trick is used: steaming already takes 1 bar, steel culture vessels are rated to 3-4",
        lo=0.33, hi=2.0, mode=1.0, note="no culture has been run at 1 bar gauge"),

    # --- Vessel types and operating modes (vessels.py; research_notes/vessels_and_modes.md) ---------------
    # Each vessel is priced at the largest unit it has been built or designed at, up to 20 m3. Sizes are working
    # volumes where `wv` is 1, else vessel volumes. Everything not listed is the model's stirred tank.
    "vm_str_m3": Input(20.0, "m3", "[Humbird-R] the model's tank; animal cells have been grown in stirred tanks of "
        "up to about 25 m3 (pharma; Vow's 20 m3 for food)"),
    "vm_perf_max_m3": Input(4.0, "m3", "[research pass, read part] the largest animal-cell perfusion run found: Genzyme's "
        "4,000 L tanks at Geel; Humbird's perfusion design stops at 2 m3",
        note="our probability that anyone has run animal cells in perfusion at 20 m3 for a month: 2-3%"),
    "vm_x_meat_shown": Input(27.0, "g wet/L", "[research_notes/Continuous harvest bioreactor progress/"
        "cultivated_meat_reactor_progress.md, company and press reports] the densest culture of meat cells reported in a vessel "
        "of 1 m3 or more: Vow's record 538 kg harvest from its 20,000 L tank is about 27 g/L if the tank was full",
        lo=27.0, hi=68.0, mode=27.0,
        note="hi: 1,500 kg from 22,000 L, about 68 g/L, poorly sourced. Bench perfusion has gone far higher (SuperMeat, 10 L, "
             "about 112 g/L), but not at this size. vessels.py flags any cell tagged 'done at this size' whose density is above "
             "this: the vessel, mode and size have been run, but not at that density with meat cells"),
    "vm_labour_exp": Input(0.54, "-", "[Humbird-R, derived] labour per m3 of tank against tanks per m3: his fed-batch "
        "plant has 95 staff for 24 x 20 m3 tanks, his perfusion plant 132 for 96 x 2 m3 (Tables 4.6, 4.13): 3.5 "
        "times the staff per m3 for 10 times the tanks per m3, so the exponent is log 3.5 / log 10",
        lo=0.3, hi=1.0, mode=0.54,
        note="applied to vessels whose largest unit is below 20 m3. lo: automated single-use units; hi: crew in "
             "proportion to the number of units"),
    "vm_restart_cycle_days": Input(2.0, "days", "[assumed] time a lost batch or bed cycle adds, beyond the cycle "
        "itself: clean, sterilise and start again from the next seed, which is ready because the seed train cycles "
        "anyway", lo=1.0, hi=14.0, mode=2.0,
        note="hi: the seed train must be regrown too. Continuous runs keep the scenarios' restart (14-30 days), "
             "because a lost continuous tank must be regrown to its density from a seed"),
    "vm_batch_x": Input(25.0, "g wet/L", "[assumed from pharma] density a plain batch reaches when all the food is in "
        "the first fill: CHO batch cultures peak at about 1e7 cells/mL, against 1.5-2.2e7 in fed-batch (Clincke et "
        "al. 2013 Part II, read part; Merck application note, snippet), i.e. 25 g/L at 2.5 ng a cell",
        lo=12.0, hi=45.0, mode=25.0,
        note="the CHO batch peak is a textbook figure, not found in a primary source in this pass. Vow's reported "
             "harvests imply about 27 g/L at 20 m3"),
    "vm_chemostat_dil": Input(0.6, "of mu_max", "[HeLa chemostat, Korean J. Biotechnol. 1989, abstract only] cell output "
        "peaked at a dilution rate of 0.030 per hour against washout at 0.050, about 0.6 of washout; mouse LS cells "
        "held their highest density at 0.30-0.35 per day (J. Gen. Virol. 1973-74, snippet)", lo=0.4, hi=0.9, mode=0.6,
        note="a chemostat must run below the maximum growth rate, or the culture washes out. Lab scale only: no "
             "animal-cell chemostat above about 1 litre has been reported"),
    # airlift (draft-tube bubble column) and single-use stirred bag
    "vm_alr_aspect": Input(3.0, "depth/width", "[assumed] liquid depth over width of a 20 m3 airlift: Li et al. 2020's "
        "300 m3 design is 13.75 m tall (about 2.6 times its width, the proportions the model's airlift check uses); "
        "airlifts are built tall to drive the circulation, and Quorn's loops are 30 m or more",
        lo=2.0, hi=8.0, mode=3.0,
        note="a taller airlift passes less gas per litre at the same gas speed, so it clears less CO2"),
    "vm_alr_otr_mult": Input(1.0, "x stirred", "[Hubbard 2024 preprint, read in full, quoting Negulescu 2023's "
        "correlation] kLa = 0.32 x (gas speed in m/s)^0.7 per second for an airlift: 32 per hour at 6 mm/s, against "
        "26 per hour for Humbird's stirred tank at the same speed (ge_kla_20m3)",
        lo=0.7, hi=1.2, mode=1.0,
        note="central 1.0, not 1.2: the correlation is for air and water, and no oxygen transfer has been measured in "
             "an animal-cell airlift above 1 m3. In air the airlift transfers 7-13 mmol/L/h at 6-16 mm/s; Humbird's 29 "
             "is with 90% oxygen"),
    "vm_alr_capex_ratio": Input(0.8, "x a stirred vessel", "[assumed, research pass] no stirrer, drive or seal, but a "
        "taller, thicker shell, a compressor and a bigger gas train. Scaling Humbird's aseptic plant to 155 m3 gives "
        "$270k per m3, the same as a Quorn airlift cost model's $271k: a like-for-like ratio near 1",
        lo=0.5, hi=1.0, mode=0.8,
        note="Negulescu 2023's 0.15 comes from a price list for a non-aseptic airlift, not from a property of airlifts"),
    "vm_bag_m3": Input(5.0, "m3", "[Thermo Fisher launch, 2021, secondary; Patheon white paper, read in full] the "
        "largest single-use stirred bags are 5,000 L (WuXi has installed them); 2,000 L is the common size",
        note="the gamma-sterilised bag and its film weight cap the size near 4-6 m3. Rocking bags stop at 500 L "
             "(CHO perfusion, 2004) and transfer 0.6-4 mmol O2/L/h in air"),
    "vm_bag_capex_ratio": Input(0.5, "x a stirred vessel", "[vendor claim, secondary] single-use hardware costs 40-50% "
        "less than stainless: no jacket, no cleaning or steaming in place", lo=0.4, hi=1.0, mode=0.5),
    "vm_bag_cost_run": Input(20.0, "$k/m3 per run", "[assumed] the bag thrown away after each run, $15-30 per litre "
        "(no vendor or published price found; one unsourced figure of about $30k for a 1,000 L bag)",
        lo=5.0, hi=30.0, mode=20.0,
        note="a bag would have to cost about $3-5 a litre for single-use to match stainless (research pass)"),
    # fixed bed: the iCELLis 500 (Pall/Cytiva), the largest commercial fixed bed
    "vm_bed_m3": Input(0.065, "m3 working", "[Pall application note, read in full] iCELLis 500: 500 m2 of PET "
        "carriers in a 25 L bed, 59-71 L working volume; 660 m2 is the largest run",
        note="scale-up is by number of units: the bed is kept at 10 cm or less to limit gradients"),
    "vm_bed_x": Input(113.0, "g wet/L", "[Pall application note, read in full; converted] 490,000 Vero cells per cm2 "
        "after 6.9 days on 200 m2; on a full 500 m2 bed at 3 ng a cell that is 7.35 kg in 59-71 L of working volume",
        lo=60.0, hi=275.0, mode=113.0,
        note="hi: a vendor's 1.2e6 cells per cm2, which 3 ng cells could hardly fit. Oxygen along the bed allows "
             "about this density only with enriched gas (research pass, calculated)"),
    "vm_bed_doublings": Input(6.6, "doublings", "[Pall application note, read in full] seeded at 5,000 cells per cm2, "
        "harvested at 490,000: 6.6 doublings per run", lo=4.0, hi=7.0, mode=6.6,
        note="a fixed bed is seeded thin because the seed is spread over the whole carrier surface"),
    "vm_bed_turnaround_h": Input(72.0, "h", "[assumed, research pass] set up a new single-use bed, equilibrate, "
        "detach the cells and harvest: about 3 days, giving 33-35 runs a year with Vero cells",
        lo=24.0, hi=120.0, mode=72.0),
    "vm_bed_recovery": Input(0.9, "of cells", "[assumed] share of the grown cells that detaching gives back: no "
        "fixed-bed figure was found; microcarrier harvests give 88-98%, a mesh bed 96% (snippets)",
        lo=0.7, hi=0.96, mode=0.9,
        note="a patent on fixed-bed detachment says enzyme alone detaches the cells poorly in a dense bed"),
    "vm_bed_capex_ratio": Input(1.0, "x a stirred vessel", "[assumed] a fixed-bed unit with its controller costs "
        "about what Humbird's formula gives for a packaged vessel of that size ($0.8M a unit): no price was found",
        lo=0.3, hi=1.5, mode=1.0,
        note="applies to the bioreactor share of the plant only; the rest of the plant is priced per m3 as for "
             "20 m3 tanks, which flatters many small units"),
    "vm_bed_cost_run": Input(154.0, "$k/m3 per run", "[assumed] a new single-use bed and bag each run at about "
        "$10,000 for a 500 m2 bed (no price found; the research pass puts 80% on $5,000-50,000), over 65 L",
        lo=31.0, hi=460.0, mode=154.0,
        note="an edible carrier that becomes part of the product (Ever After Foods' claim) would remove this, "
             "but it is unpublished"),
    # hollow fibre: the Terumo Quantum, the largest hollow-fibre unit with published cell yields
    "vm_hf_m3": Input(0.00048, "m3 working", "[HEK293T paper, PMC10504471, read part; Terumo papers, snippet] "
        "Quantum: 2.1 m2 of fibre, 175 mL inside the fibres and 305 mL outside",
        note="a 1 L cartridge has been proposed, never run; scale-up is by number of cartridges"),
    "vm_hf_x": Input(13.0, "g wet/L", "[PMC10504471, read part; converted] 2.14e9 HEK293T cells in 0.48 L of circuit "
        "after about 100 h, at 3 ng a cell", lo=9.0, hi=150.0, mode=13.0,
        note="hi: vendors' 1-2e8 cells per mL of bare cartridge, counted over a system 2-5 times its volume"),
    "vm_hf_doublings": Input(3.1, "doublings", "[PMC10504471, read part] 2.5e8 cells seeded, 2.14e9 harvested",
        lo=3.0, hi=7.0, mode=3.1),
    "vm_hf_turnaround_h": Input(96.0, "h", "[assumed, research pass] about 2 days of lag after seeding and 2 days to "
        "harvest, clean and set up", lo=48.0, hi=144.0, mode=96.0),
    "vm_hf_recovery": Input(0.9, "of cells", "[Terumo, snippet] 90-95% expected when the cells are flushed out with "
        "an enzyme", lo=0.7, hi=0.95, mode=0.9, note="a vendor's expectation, not a measurement"),
    "vm_hf_capex_ratio": Input(0.035, "x a stirred vessel", "[reseller listing, snippet] a Quantum instrument "
        "lists at about EUR 25,000, against $0.8M that Humbird's formula gives for a packaged vessel",
        lo=0.02, hi=0.1, mode=0.035),
    "vm_hf_cost_run": Input(6250.0, "$k/m3 per run", "[assumed] a single-use set of about $3,000 a run (no price "
        "found) over 0.48 L", lo=2000.0, hi=20000.0, mode=6250.0),

    # --- Cell retention for a 20 m3 perfusion tank (retention.py; research_notes/retention_devices.md) ---------------
    # Not used by any default: retention.py reprices the cases with each device through explore(retention=, extra_opex=).
    "rt_tff_default": Input(1.0, "switch", "[model choice, 2026-11-15] 1: perfusion is priced with the TFF hollow-fibre "
        "loop (retention.py; floor_physics.explore's default); 0: with the old hoped-for device, pf_capex_retention and no "
        "membranes",
        note="the side studies written before this change (research_notes/gas_exchange_study.md, cheap_plant_study.md) quote "
             "figures at 0; their tests check them at 0"),
    "rt_install": Input(1.84, "x", "[Pasitka SI Tables S1 and S4, as for pf_capex_retention] engineering, construction, "
        "fees and contingency on bought retention equipment", lo=1.5, hi=2.5, mode=1.84),
    "rt_flux_lmh": Input(5.0, "L/m2/h", "[Repligen design guidance, snippet; Ott 2024, Veje 2024, read in full] permeate "
        "flux a hollow-fibre filter holds for weeks: vendors design at 4-6; one ATF 6 ran 50 days unchanged at 0.68 (50 L, "
        "volume fraction 0.13); membranes fouled in 3-6 days at 8.3", lo=2.0, hi=8.3, mode=5.0,
        note="no month-long data at a volume fraction of 0.25"),
    "rt_atf_area": Input(11.0, "m2", "[Repligen XCell ATF 10 brochure, read in full] membrane area of the largest ATF unit",
        note="rated for 200-5,000 L tanks; 'up to 1,000 L/d' of permeate each (Humbird 2021)"),
    "rt_atf_price": Input(200.0, "$k per unit", "[Humbird 2021, read in part, derived] $38.5M for 192 ATF 10 units before "
        "installation", lo=100.0, hi=350.0, mode=200.0, note="hi: Pasitka's SI, $17.5M for 50 units"),
    "rt_atf_phi_max": Input(0.31, "volume fraction", "[Clincke et al. 2013, read in full] the ATF's vacuum could no longer "
        "pull the thick broth at 1.3e8 CHO cells/mL (about 2.4 pL a cell), in a 4 L bag",
        lo=0.25, hi=0.35, mode=0.31),
    "rt_tff_hw": Input(1.0, "$k per m2", "[assumed, research pass] pumps, housings and skid per m2 of hollow-fibre membrane "
        "for a recirculating TFF loop; at the central duty this gives $35k per m3 of tank, Pasitka's own TFF figure",
        lo=0.5, hi=3.0, mode=1.0),
    "rt_tff_phi_max": Input(0.5, "volume fraction", "[Clincke et al. 2013, read in full] a TFF loop with a positive-pressure "
        "pump reached 2.14e8 CHO cells/mL (about half the volume) for days in a 4 L bag, at about 1 bar at the inlet",
        lo=0.3, hi=0.5, mode=0.5),
    "rt_membrane_price": Input(1450.0, "$/m2", "[Humbird 2021, read in part, derived] $16,000 per ATF membrane of 11 m2; a "
        "retail 0.2 um module lists at $1,050-1,260 per m2 (snippet)", lo=1050.0, hi=1450.0, mode=1450.0),
    "rt_membrane_life": Input(3960.0, "L/m2", "[research pass, derived] litres of permeate a m2 of membrane filters before it "
        "is replaced: 5 L/m2/h for a 33-day run", lo=900.0, hi=5500.0, mode=3960.0,
        note="lo: fouled in about 4.5 days at 8.3 L/m2/h (Veje 2024); hi: one TFF hollow fibre lasted 30 days at 7.6 (Clincke "
             "2013). Membranes, not hardware, set the cost of filtering a thick, fast-fed culture"),
    # alternatives to the pharma membrane: research_notes/retention_alternatives.md, retention_alternatives_sources/
    "rt_reuse_life": Input(12000.0, "L/m2", "[Cobetter and Sartorius reuse guidance, snippets; patent US 6,261,457, snippet] "
        "litres a reusable pharma hollow-fibre module filters over a first run and four reuses: 3,960 x (1 + 4 x 0.3 to 0.8), "
        "after cleaning with sodium hydroxide; flux recovers 70-80% and a patent saw reuse life fall to 30-40% of the first",
        lo=8700.0, hi=16600.0, mode=12000.0,
        note="the same polymer, price and sterility as the model's membrane. No reuse data with animal-cell fouling; steam "
             "limits a module to about 10 cycles"),
    "rt_dial_price": Input(8.0, "$/m2", "[market reports and a retailer, snippets] a haemodialyser sells for $6-25 and holds "
        "1.8 m2 of hollow fibre", lo=3.0, hi=14.0, mode=8.0,
        note="made in the hundreds of millions, steam- or gamma-sterilised. Plasma separators have wider fibre but no price "
             "was found"),
    "rt_dial_flux": Input(2.5, "L/m2/h", "[Fresenius FX 80 data sheet, snippet; haemodiafiltration study, snippet] filtering "
        "whole blood at 30-40% cells by volume: 17-27 litres in a 4-hour session over about 2 m2", lo=2.0, hi=3.4, mode=2.5,
        note="blood cells are 8 um and deformable; meat cells are 17 um and stiffer. Sessions last hours, not weeks"),
    "rt_dial_life": Input(1000.0, "L/m2", "[assumed, between the two cases the research pass worked] litres a dialyser fibre "
        "filters before it is replaced: 240 if it fouls in 4 days as CHO membranes did (Veje 2024), 2,000 if it lasts a "
        "33-day run at 2.5 L/m2/h", lo=240.0, hi=2000.0, mode=1000.0,
        note="no animal-cell run on dialyser fibres was found"),
    "rt_dial_hw": Input(0.5, "$k per m2", "[assumed] manifolds, sterile connections and pumps per m2 of dialyser fibre, "
        "about $900 for each 1.8 m2 dialyser; none could be priced", lo=0.2, hi=1.0, mode=0.5,
        note="a central-case plant needs about 420 dialysers in parallel, so hardware, not fibre, sets the cost"),
    "rt_dial_phi_max": Input(0.35, "volume fraction", "[Fresenius FX 80 data sheet, snippet] the densest fluid dialysers "
        "routinely filter: whole blood at a haematocrit of 32-40%, for hours", lo=0.3, hi=0.4, mode=0.35),
    "rt_ceramic_price": Input(1500.0, "$/m2", "[research pass, snippets] ceramic microfiltration elements for dairy and "
        "beverages cost about $500-3,000 per m2", lo=500.0, hi=3000.0, mode=1500.0),
    "rt_ceramic_life": Input(40000.0, "L/m2", "[assumed] litres of permeate a ceramic element filters before it is replaced: "
        "ten runs of 33 days at 5 L/m2/h, if cleaning in place restores the flux each time", lo=15000.0, hi=200000.0,
        mode=40000.0,
        note="elements last years in dairies, but nobody has shown cleaning restores flux after animal cells foul them"),
    "rt_ceramic_hw": Input(3.0, "$k per m2", "[assumed] stainless housings, a cleaning skid and a spare bank, per m2 of "
        "ceramic membrane; no price found", lo=1.0, hi=6.0, mode=3.0),
    "rt_ceramic_phi_max": Input(0.12, "volume fraction", "[assumed] no animal-cell run on ceramic membranes was found; the "
        "lowest density any filter-based device has held", lo=0.05, hi=0.25, mode=0.12),
    "rt_settle_price": Input(3.5, "$k per m2", "[assumed, research pass] a steam-rated inclined settler per m2 of projected "
        "plate area, installed; no price found", lo=2.0, hi=5.0, mode=3.5),
    "rt_settle_holdup": Input(17.0, "L per m2", "[Romann et al. 2023, read in full, via the repo notes] a 2,000 L "
        "bleed-recycling settler: 30.4 L inside for 1.78 m2 of projected area", lo=10.0, hi=25.0, mode=17.0,
        note="culture in the settler has no oxygen supply; at 1e8 cells/mL its oxygen lasts seconds"),
    "rt_settle_v_frac": Input(0.5, "of hindered velocity", "[research notes, practice] settlers are designed to overflow at "
        "about half the speed at which the crowded cells settle", lo=0.3, hi=0.7, mode=0.5),
    "rt_settle_holdup_max": Input(0.05, "of the tank's liquid", "[assumed] the most culture a settler may hold outside the "
        "tank, with no oxygen supply; Romann's 2,000 L settler held about 1.5% of its tank", lo=0.02, hi=0.10, mode=0.05,
        note="above this a settler is marked not possible: too much of the culture would sit without oxygen"),
    "rt_settle_phi_max": Input(0.12, "volume fraction", "[Coronel 2020; Romann 2023, via the repo notes] the densest cultures "
        "held by a settler: 5e7 avian cells/mL; all data at a volume fraction of about 0.1 or less", lo=0.1, hi=0.2, mode=0.12),
    "rt_acoustic_cap": Input(1.0, "m3/day per unit", "[Getinge BioSep product page, snippet] the largest acoustic separator: "
        "1,000 L/day (vendor); independent tests reached 200-400 L/day", lo=0.2, hi=1.0, mode=1.0,
        note="larger units are 'very difficult' because the sound heats the culture (Romann 2023 review)"),
    "rt_acoustic_price": Input(100.0, "$k per unit", "[assumed] no price found (vendor quotes on request)",
        lo=50.0, hi=200.0, mode=100.0),
    "rt_ds_cap": Input(2.0, "m3/h per unit", "[Alfa Laval Culturefuge 100, vendor, snippet] a hermetic, steam-sterilised "
        "disc-stack separator for cell culture: 0.2-2 m3/h", lo=1.0, hi=2.0, mode=2.0),
    "rt_ds_price": Input(800.0, "$k per unit installed", "[assumed, research pass] no sterile price found; a non-sterile "
        "154 m3/h separator cost $747.5k in 2013 (NREL 2016, read in part)", lo=400.0, hi=1500.0, mode=800.0),
    "rt_ds_spares": Input(1.0, "units", "[assumed] one spare separator, so a seal failure does not end a 33-day run"),
    "rt_ds_conc": Input(0.70, "volume fraction", "[Hundley and Konigsson 2020, BioProcess Int., read in part] a hermetic "
        "separator concentrated CHO cells to 70% packed volume", lo=0.6, hi=0.8, mode=0.70),
    "rt_ds_lysis": Input(0.04, "per pass", "[same, measured by the vendor's staff] extra cells burst per pass: 2-6% in a "
        "single-use prototype at low load, 12.5% in the Culturefuge 100", lo=0.02, hi=0.125, mode=0.04,
        note="CHO cells; meat cells are larger and may be more fragile. Yeast survives 2-3 passes a day for 250-280 days in "
             "Brazilian ethanol plants, but yeast has a cell wall"),
    "rt_ds_phi_max": Input(0.28, "volume fraction", "[Hundley and Konigsson 2020, read in part] the densest feed a hermetic "
        "separator was shown with: a synthetic analogue at 28% packed cell volume", lo=0.2, hi=0.3, mode=0.28),
    "rt_ds_power": Input(10.0, "kW per running unit", "[research pass, inference from vendor data] a 2 m3/h hermetic "
        "separator; power is cents a kilo", lo=5.0, hi=20.0, mode=10.0),
    "rt_maint": Input(0.04, "of capital a year", "[assumed] maintenance of a separator beyond the plant's own 4%",
        lo=0.02, hi=0.08, mode=0.04),
    "rt_hc_eff": Input(0.96, "of cells", "[Bettinardi et al. 2020, abstract; Pinto et al. 2008, snippet] share of cells a "
        "hydrocyclone returns to the tank: 96-97% at 2.3 bar, 89-95% in other tests", lo=0.89, hi=0.97, mode=0.96),
    "rt_hc_split": Input(0.5, "of feed", "[assumed] share of a hydrocyclone's feed that leaves in the overflow (the clarified "
        "stream); the rest returns", lo=0.3, hi=0.7, mode=0.5),
    "rt_hc_price": Input(50.0, "$k per m3/h of feed, installed", "[assumed] no price or flow per unit found", lo=20.0,
        hi=150.0, mode=50.0),
    "rt_hc_phi_max": Input(0.12, "volume fraction", "[Bettinardi et al. 2020, abstract] the densest hydrocyclone perfusion: "
        "5e7 cells/mL in a 40 L bag", lo=0.06, hi=0.2, mode=0.12),

    # --- The nutrient floor, bottom-up from GFI's amino-acid prices (nutrient_floor.py; research_notes/nutrient_floor.md) ---
    # Not used by any default: nutrient_floor.py reprices the scenarios through explore()'s own `aa_bulk_price`.
    "nf_aa_price_feed": Input(6.36, "$/kg AA", "[GFI amino acid analysis, Dec 2025, Table 1, read in full; unweighted mean of 22 "
        "amino acids] feed-grade price scenario, from aggregate supplier data", lo=3.0, hi=12.0, mode=6.36,
        note="the mean is unweighted: the amino acids a cell needs are not needed in equal amounts. Serine, arginine and "
             "glutamine are needed in the largest amounts. GFI reports its own weighted figures only in charts"),
    "nf_aa_price_low": Input(11.59, "$/kg AA", "[GFI Dec 2025, Table 1; unweighted mean] low food-grade scenario: 25% below the "
        "lowest quote for each amino acid", lo=7.0, hi=16.0, mode=11.59),
    "nf_aa_price_high": Input(23.18, "$/kg AA", "[GFI Dec 2025, Table 1; unweighted mean] high food-grade scenario: 25% above "
        "the highest quote", lo=15.0, hi=35.0, mode=23.18),
    "nf_aa_g_eff": Input(232.0, "g AA/kg wet cells", "[GFI Dec 2025, Fig. 9, read in full] the most efficient of eight "
        "bioconversion estimates (200-650); 232 is the figure from Humbird's stoichiometry", lo=200.0, hi=350.0, mode=232.0),
    "nf_aa_g_mid": Input(350.0, "g AA/kg wet cells", "[GFI Dec 2025, Fig. 9] the third most efficient of its estimates",
        lo=232.0, hi=500.0, mode=350.0),
    "nf_aa_g_low": Input(650.0, "g AA/kg wet cells", "[GFI Dec 2025, Fig. 9] the least efficient of its estimates",
        lo=500.0, hi=650.0, mode=650.0),

    # --- The model audit (audit.py; research_notes/model_audit.md) ----------------------------------------------------------
    "au_retail_share": Input(0.45, "of retail price", "[USDA ERS Meat Price Spreads, via research_notes/post_harvest_costs.md, full "
        "data read] the wholesale-to-retail spread is 42-43% of the retail price for beef, 60-65% for pork and about 61% for "
        "broilers", lo=0.42, hi=0.65, mode=0.45,
        note="used only to test the model's flat $5/kg markup against a proportional one; the model's default is the flat markup "
             "(markup_add)"),
    "au_processing": Input(1.0, "$/kg", "[assumed] dewatering, forming, packing and quality control of cell mass before it enters "
        "the retail chain; none is published for cultivated meat (post_harvest_costs.md section 4)", lo=0.3, hi=3.0, mode=1.0),
    # --- The filter's flux limit (filter_flux.py; research_notes/filter_flux.md) ---------------------------------------------
    "ff_phi_w": Input(0.6, "volume fraction", "[Kromkamp 2005 (Wageningen thesis, text extract read); Vyas 1999 (Massey thesis, "
        "full text read)] cell volume fraction in the layer at the membrane wall, the value both theses use for a packed layer",
        lo=0.5, hi=0.64, mode=0.6),
    "ff_coef_belfort": Input(0.078, "-", "[Vyas 1999 (Massey thesis), Eq. 2.18, full text read, page image checked, restating Belfort, "
        "Davis and Zydney 1994] constant in J = 0.078 x shear x (phi_w a^4 / (phi_b L))^(1/3) x ln(phi_w/phi_b)",
        note="the primary papers (Zydney and Colton 1986; Davis and Leighton 1987; Belfort et al. 1994) were not readable; "
             "the form is checked in two theses. It needs phi_w - phi_b much less than phi_w, which fails at phi_b = 0.25"),
    "ff_coef_ds": Input(0.072, "-", "[Kromkamp 2005, Eq. 5.2, text extract read, restating Davis and Sherwood 1990] constant in "
        "J = 0.072 x shear x (phi_w a^4 / (phi_b L))^(1/3), stated valid for a bulk fraction phi_b below 0.1"),
    "ff_yeast_shortfall": Input(4.0, "x", "[Redkar and Davis 1993, abstract only] measured steady-state fluxes of unwashed yeast "
        "were 2 to 4 times below the model; washed yeast 10-30% below", lo=1.3, hi=4.0, mode=4.0,
        note="used as the conservative cut to the back-transport ceiling"),
    "ff_shear": Input(2000.0, "1/s", "[Pinto et al. 2020, full text read; Mostafavi et al. 2025, full text read] wall shear rate "
        "commonly used with hollow-fibre perfusion filters: 1,250-3,000 (Pinto); 2,000 (Mostafavi); 5,500 in Veje 2024, "
        "who call it high", lo=1250.0, hi=5500.0, mode=2000.0),
    "ff_length": Input(0.3, "m", "[Pinto 2020 and Radoniqi 2018, full text read: 0.2 m; Veje 2024: 0.65 m] fibre length", lo=0.2,
        hi=1.0, mode=0.3),
    "ff_throughput_lo": Input(450.0, "L/m2", "[Pinto et al. 2020, full text read] litres filtered per m2 of a 0.65 um hollow fibre "
        "before the pressure rose (CHO, 75e6 cells/mL, 1-2 L/m2/h): 450-900", lo=450.0, hi=900.0, mode=450.0),
    "ff_throughput_hi": Input(1200.0, "L/m2", "[Pinto 2020; Veje 2024, full text read] the most a membrane filtered before fouling: "
        "900-1,200 for a 0.2 um fibre at 1-2 L/m2/h (Pinto); about 1,200 over 5.9 days at 8.3 L/m2/h (Veje, the authors' "
        "arithmetic as read by the research pass)", lo=900.0, hi=1200.0, mode=1200.0,
        note="CHO at 50-75e6 cells/mL, a volume fraction of about 0.13-0.16, with antifoam and cell debris. The model's "
             "default is 3,960 (rt_membrane_life), 3 to 9 times this"),
    "ff_flux_typical": Input(2.5, "L/m2/h", "[Veje 2024 (full text, citing the literature: 2-3); Radoniqi 2018 (full text: 2); "
        "Pinto 2020 (1-2)] the sustained permeate flux hollow-fibre perfusion filters are run at", lo=1.0, hi=3.0, mode=2.5,
        note="the model's rt_flux_lmh is 5"),

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
    "kappa_base": Input(4.0, "x", "[structural] how many times more own-price-elastic a single meat PRODUCT is than "
        "meat as a category; sets the price weight beta that every product shares",
        note="ADDED 2026-11-14 when kappa was split in two. Until then one number, cult_sub_mult, set the shared "
             "price weight beta, so raising it made shoppers more sensitive to EVERY price (beans and "
             "plant-based included) and the calibration strained (at 9 a solved weight fell to zero). Now "
             "kappa_base sets beta (unchanged at 4: a product's own-price elasticity is typically 3-5x its "
             "category's), and cult_sub_mult / kappa_base multiplies only cultivated's price DIFFERENCE from "
             "the conventional meat beside it. At cult_sub_mult = kappa_base the model is exactly the "
             "published one"),
    "cult_sub_mult": Input(8.5, "x", "[data-bracketed] kappa: HOW MANY TIMES more own-price-elastic CULTIVATED "
        "meat is than meat as a CATEGORY. Plain meaning: a 1% rise in cultivated's price loses kappa x 0.9% of its "
        "buyers, versus 0.9% for meat-in-general. WHY > 1: the measured -0.9 is the elasticity of the meat "
        "CATEGORY, which is inelastic precisely because the category has no close substitute; but a single "
        "cultivated product DOES have a near-perfect substitute right next to it (conventional meat, the SAME "
        "tissue), so its OWN price matters far more -- a price cut wins buyers fast, a price rise loses them to "
        "conventional. kappa therefore sets HOW STEEPLY cultivated's share falls as it gets pricier than "
        "conventional (above parity); it does NOT change the at-parity share (where prices are equal).",
        lo=4.0, hi=11.0, mode=8.5,
        note="DEFAULT 4 -> 8.5, 2026-11-14, on two kinds of evidence. (1) Six premium animal products with "
             "matched price premiums and volume shares (market_share.ANALOGUES: organic milk, cage-free, "
             "organic and omega-3 eggs, organic chicken, all organic meat) take 2-7% of volume at 1.5-2.2x "
             "the conventional price. The model's share for a product equal to conventional on everything but "
             "price misses them by a typical factor of six at kappa = 4 (log error 1.84), by 2.6 at 8.5 "
             "(0.97), and fits best at 10 (0.92). (2) The one choice experiment on cultivated meat (Lusk, "
             "below) brackets the at-parity elasticity at [-3.4, -0.84]; kappa = 8.5 gives -3.27 and 9 gives "
             "-3.46, just outside. So 8.5 is the best analogue fit that the experiment allows. Range 4 (the "
             "old default) to 11. THIS BECAME POSSIBLE when kappa was split (kappa_base): it now multiplies "
             "only cultivated's price difference from conventional, so the at-parity share, the plant-based "
             "calibration and every other dial are unchanged by it (the solved weights are those of the "
             "published model). EARLIER NOTE (2026-11-13, hi 6 -> 9): the organic-chicken check (market_share.organic_premium_check) "
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

    # --- Tank size scan (tank_size.py; research_notes/tank_size.md). Used only by the what-if rows of that scan; no
    #     scenario, default or page number uses them. -----------------------------------------------------------------
    "ts_ph_relaxed": Input(2.0, "x the safe dose", "[derived, research_notes/gas_exchange_study.md section 8] the "
        "alkaline dose a column loop may give the culture in the what-if that relaxes the pH check: the safe design "
        "(55 mbar out, 0.5 m3 of loop in a 20 m3 tank) is 0.29 of the dose that slowed CHO cells, so twice it is 0.58",
        lo=1.0, hi=3.4, mode=2.0,
        note="3.4 times the safe dose is the dose that slowed CHO cells (Paul et al. 2020, via a summary); one study, "
             "inferred measure of 'rise x share'"),
    "ts_loop_hw_exp": Input(0.3, "-", "[assumed] how fast the cost of the retention loop's hardware per m2 of membrane "
        "falls with tank size, in the what-if that gives it economies of scale: per m2 it scales as (V/20)^-0.3, so "
        "the hardware as a whole scales as V^0.7",
        lo=0.0, hi=0.4, mode=0.3,
        note="the base model prices every m2 alike (rt_tff_hw); pumps, housings and controls cost less per m2 in a "
             "bigger skid and more in a small one; the membranes themselves do not change. The usual exponent for "
             "process equipment is 0.6 to 0.7 (ge_vessel_cost_exp is 0.6)"),
    "ts_hazard_exp": Input(0.333, "-", "[assumed] how fast the chance of losing a run per tank-day grows with tank "
        "size, in the what-if that makes it grow: hazard x (V/20)^0.333",
        lo=0.0, hi=0.667, mode=0.333,
        note="the base model holds the chance per tank-day fixed. A bigger tank has more ports, seals and "
             "connections (surface goes as V^(2/3)) and a loss costs the whole tank, so the loss per kilo rises with "
             "the chance per tank-day. No source gives it by tank size; BioPlan's survey found larger facilities had "
             "about three times the contamination of smaller ones (facilities, not tanks)"),
    # --- how thick a culture can be (thick_culture.py, research_notes/thick_culture.md) ------------------
    "tc_phi_max": Input(0.65, "volume fraction", "[Iordan, Duperray and Verdier 2007, arXiv:0709.3671, read in full] the "
        "maximum packing in the Krieger-Dougherty fit to the viscosity of CHO suspensions at 1,000 per second (eta/eta0 = "
        "(1 - phi/phi0)^(-2.5 phi0))", lo=0.64, hi=0.74, mode=0.65,
        note="0.64 is random close packing of hard spheres, 0.74 the face-centred cubic limit. Their cells were spun down "
             "and re-diluted at 20 C and not growing"),
    "tc_thin": Input(1.33, "-", "[Tregidgo et al. 2023, Chem Eng Res Des 194:344, read in full] CHO at 1e8 cells/mL, 37 C: "
        "2.4 mPa s at 50 rpm in a 250 mL tank against 1.8 at a shear rate of 45 per second (the viscosity the Thomas "
        "equation gives for a quarter cells by volume): the excess viscosity is 1.33 times higher at the low shear a large "
        "tank has", lo=1.0, hi=3.0, mode=1.33,
        note="hi: the same paper, 'viscosities increase up to 3-fold ... at shear rates below 40 per second', with high "
             "scatter. Applied to the excess of the suspension over the medium"),
    "tc_kla_exp": Input(0.40, "-", "[Yagi and Yoshida 1975, as listed in a university course note, snippet] the oxygen "
        "transfer coefficient falls with the apparent viscosity to the power -0.40 in stirred tanks of Newtonian and "
        "non-Newtonian liquids", lo=0.0, hi=0.6, mode=0.40,
        note="lo: Amgen's CHO perfusion cultures at 1e5 to 35e5 cells/mL lost almost no kLa (AIChE 2017 abstract, 403 on "
             "fetch) and Pappenreiter saw none between cell-free and spent harvest medium (via Bioprocess Intl 2024). hi: a "
             "2025 Biotechnology Journal paper reports a 10-40% fall with culture rheology (snippet, not read). Humbird's "
             "kLa equation has no viscosity term"),
    "tc_np": Input(5.0, "-", "[Tregidgo et al. 2023, read in full] power number of the dual-impeller 250 mL tank, 4.9; "
        "elephant-ear and pitched-blade impellers in large tanks run at 1.3-1.5 (assumed)", lo=1.3, hi=5.0, mode=5.0,
        note="at a fixed power per volume a lower power number turns the stirrer faster and raises the Reynolds number, so 5 "
             "is the cautious end"),
    "tc_re_turb": Input(1.0e4, "-", "[Tregidgo et al. 2023, read in full] a mixing number (time x speed) that stays constant "
        "from Re 5,600 up; the usual boundary of fully turbulent flow is 10,000", lo=5600.0, hi=1.0e4, mode=1.0e4,
        note="above this Reynolds number, Humbird's mixing-time equation (which has no viscosity in it) holds"),
    "tc_bubble_mm": Input(3.5, "mm", "[research_notes/gas_flow_cap.md, section 3, citing a bubble-column measurement in "
        "synthetic medium with poloxamer] bubbles of 3-4 mm", lo=2.0, hi=5.0, mode=3.5),
    "tc_holdup": Input(0.04, "of the tank", "[research_notes/gas_flow_cap.md, section 3] gas hold-up at 6 mm/s: 3.5% at "
        "4.2 mm/s and 4.5% at 7.7 mm/s", lo=0.03, hi=0.06, mode=0.04,
        note="measured without cells, at the viscosity of the medium"),
    "tc_yield_sigma": Input(1.4, "Pa", "[Iordan, Duperray and Verdier 2007, read in full] the stress scale sigma* of the "
        "fractal-aggregate fit to their yield stresses", lo=0.5, hi=5.0, mode=1.4,
        note="their Figure 4a values were not extracted; the yield stress is taken as sigma* (phi/phi0)^m, with m below. "
             "They fitted CHO at 20 C, spun down and re-diluted"),
    "tc_yield_exp": Input(8.4, "-", "[Iordan, Duperray and Verdier 2007, read in full] yield stress grows as phi to the "
        "power 8.4", lo=6.0, hi=11.0, mode=8.4),
    "tc_peak_dissipation": Input(50.0, "-", "[Humbird 2021, Eq. 2.17 after Nienow 2010, read in part] the energy dissipation "
        "near the impeller against the tank average", lo=20.0, hi=100.0, mode=50.0),
    "tc_jacket_u": Input(400.0, "W/m2/K", "[assumed] heat transfer through the wall of a jacketed steel tank holding a thick "
        "culture, inside film included", lo=200.0, hi=700.0, mode=400.0,
        note="textbook range for a stirred jacketed vessel; nothing found for a 20 m3 animal-cell tank"),
    "tc_cool_dt": Input(10.0, "K", "[assumed] temperature difference between the culture (37 C) and the cooling water in the "
        "jacket", lo=5.0, hi=15.0, mode=10.0),
    # --- the least medium per kg of cells that physics allows (min_litres.py; research_notes/min_litres_per_kg.md) ---
    "ml_dry_mol_kg": Input(13.6, "mol/kg wet", "[Humbird-R, derived] moles of dry cell mass in a kg of wet cells",
        note="300 g dry matter per kg wet over 22.06 g/mol for CH1.68 O0.34 N0.21 (his Table 2.1); the figure that "
             "turns pf_nh3_efficient from per mole of dry mass into per kg"),
    "ml_n_per_dry": Input(0.21, "mol N/mol dry", "[Humbird-R] Table 2.1: nitrogen in the cell formula CH1.68 O0.34 N0.21",
        note="x 13.6 = 2.86 mol N per kg wet. A protein-only count gives about 2.2 (195 g protein per kg wet at 16% "
             "nitrogen); nucleic acids add about 0.2"),
    "ml_aa_pure_kg": Input(0.26, "kg/kg wet", "[Humbird-R] Table 3.4: pure amino acids the cells take up per kg of wet cells "
        "(Reaction 2.11); quoted in the aa_intensity note",
        note="free amino acids in the proportion the cell builds protein; the hydrolysate (0.337) carries more because "
             "its profile does not match"),
    "ml_aa_mw": Input(128.0, "g/mol", "[textbook] mean molar mass of a free amino acid: 110 for a protein residue plus 18 "
        "for water", lo=120.0, hi=140.0, mode=128.0),
    "ml_glc_mw": Input(180.16, "g/mol", "[textbook] glucose"),
    "ml_salts_osm": Input(250.0, "mOsm/kg", "[judgement; research_notes/min_litres_per_kg.md] osmolality of the salts and "
        "buffer in a conventional medium, without its glucose and amino acids",
        lo=150.0, hi=260.0, mode=250.0,
        note="about 100 mM NaCl (190), 25 mM bicarbonate (50) and the rest (10). Not sourced from a medium sheet. Lower "
             "values mean cells that tolerate less sodium; no source on how low the salts can go. Used only where the "
             "medium is what the cells sit in (min_litres.bounds, 'bath')"),
    "ml_feed_g_l": Input(100.0, "g/L", "[judgement; research_notes/min_litres_per_kg.md] strength of a concentrated feed of "
        "amino acids and glucose, as solids per litre, that is mixed into the tank and diluted there",
        lo=50.0, hi=200.0, mode=100.0,
        note="single-strength perfusion media carry roughly 10-30 g/L of these (unsourced); feeds of 5-10 times that "
             "are used in fed-batch (the search found papers on ultra-concentrated feeds, limited by tyrosine and "
             "cystine solubility, and no figure). No measurement in a 20 m3 perfusion tank"),
    "ml_nh3_chogs": Input(0.012, "mol/kg wet", "[Mayrhofer et al. 2020, via waste_tricks_sizing.md B2, derived] ammonia of a "
        "glutamine-synthetase CHO line in optimised perfusion, if its 0.54 fmol per cell per hour held at 0.35 per day",
        lo=0.0063, hi=0.029, mode=0.012,
        note="the lowest ammonia in any source read. Measured in cells that were not growing; the extrapolation to "
             "faster growth is an inference, and the cells are CHO, not meat cells"),
    "ml_atp_bio": Input(1.6e-11, "mol ATP/cell", "[Kilburn, Lilly and Webb 1969, J Cell Sci 4:645, via the BioNumbers page "
        "(ID 101985), read]: ATP to build a mouse fibroblast (LS cell)",
        note="cell size not given on that page; used only as a cross-check on the oxygen the model burns"),
    "ml_atp_maint": Input(2.9e-11, "mol ATP/cell", "[Kilburn et al. 1969, as above] ATP for upkeep per new cell at a "
        "1.15 day generation time"),
    "ml_kilburn_td_h": Input(27.6, "h", "[Kilburn et al. 1969] the 1.15 day generation time of that upkeep figure"),
    # --- growth-factor prices and the fastest doubling time (gf_doubling_bounds.py;
    #     research_notes/gf_and_doubling_bounds.md). Access levels: FT = full text read, ABS = abstract only,
    #     SNIP = search snippet, MEM = from memory (check before citing). ------------------------------------
    "gb_conc_insulin": Input(0.0194, "g/L", "[Humbird-R Sect. 3.1, FT; GFI 2023 footnote 4, FT; Chen et al. 2011 Essential 8] "
        "insulin in the medium: 19.4 mg/L"),
    "gb_conc_transferrin": Input(0.0107, "g/L", "[Humbird-R Sect. 3.1, FT; GFI 2023 footnote 4, FT] transferrin: 10.7 mg/L"),
    "gb_conc_fgf": Input(1.0e-4, "g/L", "[Humbird-R Sect. 3.1, FT; GFI 2023 footnote 4, FT] FGF: 0.1 mg/L"),
    "gb_conc_tgfb": Input(2.0e-6, "g/L", "[Humbird-R Sect. 3.1, FT; GFI 2023 footnote 4, FT] TGF-beta: 0.002 mg/L"),
    "gb_price_insulin": Input(7.0, "$/g", "[Humbird-R Table 4.4, FT] unit cost of insulin in his fed-batch plant, 2018 dollars, "
        "from his price-volume line at the world demand of 16,785 kg/y"),
    "gb_price_transferrin": Input(12.0, "$/g", "[Humbird-R Table 4.4, FT] transferrin, 2018 dollars, at 9,258 kg/y"),
    "gb_price_fgf": Input(649.0, "$/g", "[Humbird-R Table 4.4, FT] FGF, 2018 dollars, at 87 kg/y"),
    "gb_price_tgfb": Input(18837.0, "$/g", "[Humbird-R Table 4.4, FT] TGF-beta, 2018 dollars, at 1.7 kg/y",
        note="the four prices at the four concentrations cost $3.13 per kg of cells in his table (pf_growth_factors rounds "
             "this to 3.1). His batch holds about 115 g/L, so 8.65 L of medium per kg"),
    "gb_pv_intercept": Input(4.90, "log10 $/kg", "[Humbird-R Eq. 3.4, FT] log10(price in $/kg) = intercept - slope x "
        "log10(volume in MT/y), a regression of market prices of protein bioproducts (insulin, antibodies, industrial enzymes)"),
    "gb_pv_slope": Input(0.861, "-", "[Humbird-R Eq. 3.4, FT] price falls 0.861 decades for every decade of volume"),
    "gb_gfi_target_rp": Input(1.0, "$/g", "[GFI 2023 (Swartz et al.), Table 1, FT] production cost assumed for insulin and "
        "transferrin so growth factors and recombinant proteins are 10% of a $10/kg cost: $1,000/kg"),
    "gb_gfi_target_gf": Input(100.0, "$/g", "[GFI 2023, Table 1, FT] production cost assumed for growth factors: $100,000/kg"),
    "gb_gfi_litres_low": Input(8.0, "L/kg", "[GFI 2023, Box 2, FT; Sinke et al. 2021 Table 16] medium use, low scenario"),
    "gb_gfi_litres_mid": Input(13.0, "L/kg", "[GFI 2023, Box 2, FT] medium use, medium scenario"),
    "gb_gfi_litres_high": Input(42.0, "L/kg", "[GFI 2023, Box 2, FT] medium use, high scenario"),
    "gb_mkt_insulin": Input(24.75, "$/g", "[Gotham, Barber & Hill 2018, BMJ Global Health 3:e000850, full text via Europe PMC] "
        "regular human insulin API, a regression of Indian export prices in 2013-2016 without the USA shipments",
        note="a market price, not a production cost; fell about 18% a year; only 484-793 kg a year in the data. Humbird's "
             "footnote calls the same number a production cost. Pharmaoffer trade data average $36.4/g over 12 months to "
             "Aug 2026 (SNIP: the page returned 403)"),
    "gb_mkt_transferrin": Input(182.3, "$/g", "[Stout et al. 2022 Beefy-9 Supplementary Table 3, read in full by the pf-tea "
        "evidence file] InVitria recombinant human transferrin, 10 g for $1,823",
        note="InVitria Optiferrin: $351.7/g at 1 g and $217.7/g at 10 g (pf-tea evidence, vendor page)"),
    "gb_mkt_fgf2": Input(196000.0, "$/g", "[GFI growth-factor-cost page, FT] ORF Genetics human FGF2, $196/mg in September 2022",
        note="the same page: $7.47/mg (7,470 $/g) from Venkatesan et al. made in-house, and $2,005/mg in the 2018 analysis"),
    "gb_mkt_fgf2_inhouse": Input(7470.0, "$/g", "[GFI growth-factor-cost page, FT; Venkatesan et al. not read] FGF2 made in-house"),
    "gb_mkt_tgfb": Input(2.9e7, "$/g", "[Humbird-R footnote 111, FT] research quantities of human TGF-beta from the Sigma "
        "catalogue, about $29k/mg"),
    "gb_floor_enzyme_lo": Input(12.0, "$/kg", "[GFI 2023 footnote 8, FT, second-hand] Novozymes quotes for common food enzymes "
        "at 200-1,000 kg"),
    "gb_floor_enzyme_hi": Input(25.0, "$/kg", "[GFI 2023 footnote 8, FT, second-hand] the top of the same quotes"),
    "gb_floor_albumin_trade": Input(55.0, "$/kg", "[pf-tea evidence, grade C: GFI 2025 and trade data] bulk albumin traded at "
        "$40-70/kg", lo=40.0, hi=70.0, mode=55.0),
    "gb_floor_tf_model": Input(314.0, "$/kg", "[pf-tea model result, my own: results/analyses.json, case tf/100/humbird] "
        "recombinant transferrin on albumin's two-column route, 100 t/y, design-point titre",
        note="at the best published titre (Finnis 2010, 2.29 g/L, 10 L) the same plant gives $949/kg at 100 t/y and $1,939 at "
             "10 t/y. A bottom-up cost from patents and one fermentation paper, not a quote"),
    "gb_floor_tf_published": Input(949.0, "$/kg", "[pf-tea model result: tf_finnis2010/100/humbird] the same at the best "
        "published titre"),
    "gb_fgf2_half_life_h": Input(10.0, "h", "[vendor pages and a review, SNIP] wild-type FGF2 at 37 C in culture medium: "
        "under 10 h", lo=5.0, hi=10.0, mode=10.0),
    "gb_fgf2_g3_half_life_h": Input(168.0, "h", "[Qkine and Reprocell vendor pages, SNIP; Dvorak et al. preprint reports "
        ">20 days] engineered FGF2-G3 at 37 C: over 7 days", lo=168.0, hi=480.0, mode=168.0),
    # biosynthesis ATP budget, per gram of dry cell mass, from Humbird's composition (Table 2.1)
    "gb_f_protein": Input(0.70, "g/g dry", "[Humbird-R Table 2.1, FT] protein share of dry cell mass"),
    "gb_f_lipid": Input(0.15, "g/g dry", "[Humbird-R Table 2.1, FT] lipid"),
    "gb_f_carb": Input(0.10, "g/g dry", "[Humbird-R Table 2.1, FT] carbohydrate"),
    "gb_f_rna": Input(0.05, "g/g dry", "[Humbird-R Table 2.1, FT] RNA and DNA"),
    "gb_dry_per_wet": Input(0.30, "g/g wet", "[Humbird-R, via pf_fat_kg] dry mass in a gram of wet cells: 70% water"),
    "gb_aa_g_mol": Input(110.0, "g/mol", "[textbook, MEM] mean mass of an amino-acid residue in protein"),
    "gb_atp_peptide": Input(4.0, "ATP/bond", "[textbook, MEM] two to charge the tRNA, one to bring it in, one to move the "
        "ribosome; a minimum, leaves out making ribosomes and mRNA", lo=4.0, hi=6.0, mode=4.0),
    "gb_lipid_g_mol": Input(256.0, "g/mol", "[Humbird-R Table 2.1: lipid taken as palmitate] palmitate mass"),
    "gb_atp_fa16": Input(42.0, "ATP/palmitate", "[textbook, MEM] 7 ATP and 14 NADPH to build palmitate from acetyl-CoA, "
        "counting each NADPH as 2.5 ATP; carbon not counted", lo=30.0, hi=50.0, mode=42.0,
        note="Humbird's Reaction 2.2 makes all lipid from glucose. Fed fatty acids skip this cost (pf_fat_kg, pf_fat_price)"),
    "gb_nt_g_mol": Input(330.0, "g/mol", "[textbook, MEM] mean nucleotide mass"),
    "gb_atp_nt": Input(9.0, "ATP/nucleotide", "[textbook, MEM] about 7 to make a nucleotide from glucose and glutamine and 2 "
        "to join it to the chain", lo=6.0, hi=12.0, mode=9.0),
    "gb_glycosyl_g_mol": Input(162.0, "g/mol", "[textbook] one hexose unit in a polysaccharide"),
    "gb_atp_glycosyl": Input(2.0, "ATP/unit", "[textbook, MEM] to add one hexose to a chain through UDP-glucose",
        lo=1.0, hi=3.0, mode=2.0),
    "gb_biosyn_overhead": Input(1.0, "x", "[judgement] extra ATP over the bare synthesis for folding, amino-acid uptake, "
        "making ribosomes and mRNA; 1.0 counts none of it", lo=1.0, hi=1.6, mode=1.0),
    "gb_resp_scope": Input(2.0, "x", "[judgement; typical maximal-to-basal respiration of cultured cells under an uncoupler is "
        "about 2-4, MEM, not read in this pass] most oxygen a cell can burn per gram, relative to West's rate at a 24 h "
        "doubling", lo=1.5, hi=3.0, mode=2.0,
        note="more mitochondria per cell would raise it; heart muscle holds about 35% of its volume as mitochondria against "
             "10-20% in fast cell lines (MEM)"),
    "gb_elong_aa_s": Input(5.6, "aa/s", "[Ingolia et al. 2011, mouse embryonic stem cells; bionumbers snippet, SNIP] how fast a "
        "mammalian ribosome adds amino acids", lo=2.0, hi=6.0, mode=5.6,
        note="other studies in U2OS and HEK293 cells give 3.1-4.9 codons/s"),
    "gb_ribosome_kda": Input(4300.0, "kDa", "[textbook, MEM] mass of a mammalian 80S ribosome"),
    "gb_rrna_in_ribosome": Input(0.65, "of ribosome mass", "[textbook, MEM] 2.8 MDa of rRNA in 4.3 MDa"),
    "gb_rrna_in_rna": Input(0.80, "of RNA", "[textbook, MEM] ribosomal RNA is about 80% of a cell's RNA"),
    "gb_cho_mass_pg": Input(1167.0, "pg wet", "[Humbird-R footnote 41, FT] a CHO cell: 350 pg dry mass and 70% water"),
    "gb_cho_qo2_pmol_h": Input(0.227, "pmol O2/cell/h", "[Goudar et al. 2011, ABS, via species_cell_parameters.md] CHO "
        "perfusion at 36.5 C: 5.14-5.77 pmol/cell/day", lo=0.214, hi=0.240, mode=0.227),
    "gb_cho_doubling_h": Input(15.0, "h", "[species_cell_parameters.md] CHO doubling time, 14-16 h", lo=14.0, hi=16.0, mode=15.0,
        note="the 14-16 h comes from the research-note brief, not from a source read in this pass"),
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
    "reference plant cost (standard perfusion tank)":          REGISTRY["plant_floor"].value,
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
