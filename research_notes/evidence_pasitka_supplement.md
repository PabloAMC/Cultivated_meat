# Pasitka et al. 2024 (Nature Food), supplementary tables: available, and what they say

Research date: 2026-11-21. Evidence pass only; no input changed.

**Yes, the Supplementary Information is openly available** (11 tables, author-formatted PDF):
https://static-content.springer.com/esm/art%3A10.1038%2Fs43016-024-01022-w/MediaObjects/43016_2024_1022_MOESM1_ESM.pdf
(downloaded and read in full as text, 2026-11-21). Some repo notes already used it (`plant_capital_crosscheck.md`,
`growth_factors_in_medium_price.md`), while `TODO.md` item "Pasitka 2024's supplementary tables were not available" and
`study_comparison.md` say it was not. This note settles the open point.

Paper: Pasitka L. et al., "Empirical economic analysis shows cost-effective continuous manufacturing of cultivated chicken
using animal-free medium", Nature Food 5, 693 (2024), doi:10.1038/s43016-024-01022-w. Strength: peer-reviewed design study by
company authors (Humbird's method plus vendor quotes); the cost lines are assumptions, not plant data.

## The cost lines (Tables S4, S5–S10), 2024 dollars, per kg of wet cell mass

Three designs, each about **1,070 t of wet cells a year** (S5: $15,104,086 of nutrients = $14.11/kg):

| line | ATF (25 × 2 m³, 50 ATF-10) | TFF (10 × 5 m³) | Large-scale perfusion (2 × 25 m³, a "large-scale PD" retention device) |
|---|---|---|---|
| TCI (S4) | $123.9 M | $63.1 M | $40.3 M |
| **Annual capital charge, 14.6% of TCI (S4)** | $18.09 M = **$16.90/kg** | $9.21 M = **$8.60/kg** | $5.89 M = **$5.50/kg** |
| Nutrients, animal-component-free (S5, S10) | 14.11 | 14.11 | 14.11 |
| Consumables (S6) | 9.21 (600 ATF membranes/yr at $16,300 = $9.14) | 0.43 (24 membranes/yr at $16,000) | 0.07 (sterile filters only) |
| Utilities (S7) | 2.18 | 2.18 | 2.18 |
| Labour, burdened (S8) | 2.61 | 2.03 | 1.73 |
| Maintenance + insurance (S9/S10) | 10.42 | 5.31 | 3.40 |
| **Total cost of wet biomass as published (S10)** | **38.54** | **24.06** | **21.49** |
| same, **with the S4 capital charge added** (my sum) | 55.44 | 32.66 | 26.99 |
| same, in 2025 dollars (×1.026, CPI-U) | 56.9 | 33.5 | 27.7 |

**Plant payment: confirmed excluded.** S4 computes an annual capital charge (14.6% of TCI a year), but S9 and S10 total only
variable OPEX plus labour, maintenance and insurance (e.g. large-scale: $17,513,635 + $5,484,690 = $22,998,325 = $21.49/kg).
The repo's reading from the chart legends (about 85% likely, `study_comparison.md`) is now certain. Adding Pasitka's own
14.6% charge raises the large-scale case by $5.50/kg (+26%). The model's 8.3% a year (5.4% over 20 years) on the same TCI
would add $3.13/kg instead.

The serum-free (with albumin) variant, S5/S9: nutrients $75.58/kg ($24.1 M of albumin alone), total $82.96–100.00/kg.

## Medium cost per litre

- The tables give $/kg and kg of each nutrient class, not litres. The **$0.63/L** is the paper's main-text figure; with $14.11
  of nutrients a kilo it implies **22.4 L of medium a kg** (the repo's existing derivation, `study_comparison.md`).
- Table S7 charges **61,006,667 kg of process water a year = 57 L a kg of cells**. That is all water (medium, cleaning, washing),
  so it bounds medium from above: if all of it were medium, the nutrients would be $0.25/L. The 22.4 L/kg vs 57 L/kg gap
  is consistent with roughly 35 L/kg of non-medium water, but the SI does not split it.
- Animal-component-free nutrients by class (S5): sugars $1.12, amino acids **$2.47** (86.7 t/yr: **81 g a kg of cells** at
  $30.6/kg), lipids $1.57, vitamins and minerals $2.92, growth factors **$0.17** (2 kg/yr), others $5.85.
  Note the amino acids: 81 g/kg of cells is a third of the model's 232 g floor (`aa_intensity`), at about five times its price.

## Filter life implied (ATF case)

600 membranes a year on 50 ATF-10s is one change per device a month. At 11 m² each that is 6,600 m² a year. If all 22.4 L/kg
of medium leaves as permeate: 24.0 M L / 6,600 m² = **3,640 L/m²**; if all 57 L/kg of water did: **9,240 L/m²**. This is a
company's cost assumption, not a measurement (same caveat as `ammonia_tolerance_and_filter_life.md` section 5).

## Recommendation for the parent session (not applied)

1. Close the TODO item: the SI is available; replace "read from chart legends" in `study_comparison.md` and the Pasitka
   rows with "Tables S4 and S10: capital charge computed (14.6% of TCI) but excluded from the total".
2. If the study-comparison table shows Pasitka with a capital charge, use either its own 14.6% ($26.99/kg large-scale,
   2024$; $27.7 in 2025$) or the model's 8.3% ($24.62; $25.3 in 2025$), and say which.
3. Note in METHODS that Pasitka's medium (81 g of amino acids a kg of cells) is far leaner than the model's floor (232 g);
   it is a recipe claim, not a measured uptake.

## Sources

- Pasitka et al. 2024, Nature Food 5:693, Supplementary Information (Tables S1–S11), URL above; reporting summary
  (`MOESM2`) checked, no data. Main text not re-read (paywalled redirect on nature.com).
- CPI-U 2025 over 2024 ×1.026, as used in `study_comparison.md`.
