# What the FDA pre-market consultation memos say about process scale, density, medium and harvest

Research date: 2026-11-21. Evidence pass only; no input changed. TODO item: "Upside Foods' FDA memo, when published: the
operating mode, density and waste levels of a 20 m³ process."

## Short answer

- **Upside's first memo has been public since November 2022** (CCC 000002), but it is about the earlier tissue product
  (suspension expansion, then adherent differentiation into sheets). It gives **no** vessel size, density, run length or
  waste level.
- **Upside's second product** (a cultivated-chicken-plus-plant blend made in a "single vessel") got an FDA "no questions"
  letter in **September 2026** and USDA label approval in November 2026. Press reports of 17 November 2026 say "details of
  the cell lines and process will be published in a scientific memo on the FDA website shortly". **That memo was not in
  FDA's public inventory when checked today** (the inventory lists five files, the latest Believer, July 2025).
- **None of the five published memos discloses scale, density, perfusion rate or ammonia/lactate levels.** FDA states that
  firms gave equipment details as "supporting, corroborative information in the supplemental, confidential material".
  A memo for the 20 m³ process is unlikely to carry these numbers either (rough judgement: about 15% that the coming Upside
  memo states a density or a waste level).

## The five published files

| CCC | firm, cells | mode stated | harvest | medium notes | scale / density stated? |
|---|---|---|---|---|---|
| 000001 (memo 2023-03-17) | GOOD Meat, chicken, suspension | suspension proliferation, single-use or CIP/SIP stainless bioreactors | centrifugation, NaCl wash | basal medium, "anti-clumping agents", **fetal bovine serum**, **Pluronic F-68** (not detected in product; ≤10 mg/100 g bound) | no |
| 000002 (memo 2022-11-14) | Upside, chicken, fibroblast- and muscle-like | suspension seed train, then **adherent differentiation and maturation** forming tissue | sheets removed from vessel surface, PBS wash, dewatered | serum used in cell-line establishment | no |
| 000005 (memo 2025-05-29) | Wildtype, coho salmon, mesenchymal | "proliferation phase using **suspension fed-batch culture**", stainless bioreactors; contamination flag if pH leaves 7.1–7.8 | bowl centrifuge, three water-sugar washes, blast chill | no differentiation step | no |
| 000008 (memo 2025-03-07) | Mission Barns, pork fat cells | **adherent** proliferation and fattening in "proprietary ... cultivators", single-use seed train | dissociation solution, wash | serum-free production medium; product 5.85% fat | no |
| 000039 (memo 2025-07-24; supplement 2025-09-24) | Believer, chicken fibroblasts, spontaneously immortalised, suspension | "suspension culture proliferation", seed train to bioreactor | "**filtration** followed by washing with saline ... within a continuous closed system" | animal-component-free and growth-factor-free in production (insulin and FGF2 used only to set up the cell bank); a soy-derived enzyme removed in 2025; stable doubling over 800 days | no |

Useful facts for the model, all qualitative:
- **Two of three suspension-chicken processes and the salmon process are batch-type harvests** (GOOD Meat centrifuges a
  batch; Wildtype says fed-batch). Believer's "continuous closed system" for washing and its filtration harvest fit its
  published perfusion work (Pasitka 2024), but the memo does not say perfusion.
- **No maturation step** in GOOD Meat, Wildtype and Believer (supports `pf_mature_h` = 0 for bulk cell mass).
- **Poloxamer is in use** (GOOD Meat) and is accepted with a residue bound.
- **Growth-factor-free production medium** is claimed for Believer's line.

## Upside's 2026 scale-up (press, company claims)

- "Multiple vessels of 20,000+ liter bioreactors" at its Emeryville facility; validated "at 20,000-L scale consistently over
  the past 18 months"; next generation 50,000–100,000 L (AgFunderNews, 2026-11-17). Green Queen (2026-11-17, updated
  2026-11-21) says instead "combined capacity of over 20,000 litres"; the two disagree on whether one vessel is 20 m³.
- Capacity "more than 1 million pounds" (≈454 t) of product a year; cells "at least 25%" of the product (Green Queen
  update quoting the CEO); about three weeks per production cycle; serum-free; cost cut "by over 10-fold compared to the
  prior production method". No mode, density, medium cost or waste figure.
- Implied density, for orientation only: 25% of 454 t = ≥113 t of cells a year. In 20 m³ total at about 17 three-week cycles
  a year that would need about 330 g/L (implausible); in 80 m³ (four 20 m³ vessels) about 85 g/L. So the claims are
  consistent with several 20 m³ tanks at densities like the model's fed-batch case, and not with one tank. This is my
  arithmetic on company claims, not data.

## Recommendation for the parent session (not applied)

- No input change. Update the TODO item: Upside's first memo is public and silent on scale; the September 2026 memo is
  pending on FDA's site. Re-check the FDA inventory in December 2026.
- METHODS could cite Wildtype's "suspension fed-batch" and GOOD Meat's centrifuged batch harvest as evidence that cleared
  products are made in batch-type modes, and Believer's filtration harvest as the one consistent with perfusion.
- The AgFunder/Green Queen figures are the only public anchor for a 20 m³ meat-cell process; they support "several 20 m³
  tanks exist and run repeatedly", not any density or waste level.

## Sources

- FDA, Inventory of completed pre-market consultations, https://www.fda.gov/food/human-food-made-cultured-animal-cells/inventory-completed-pre-market-consultations-human-food-made-cultured-animal-cells
  and database https://www.hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=AnimalCellCultureFoods (both read 2026-11-21).
- Scientific memos (read in full as text): CCC 000002 https://www.fda.gov/media/163261/download ; CCC 000001
  https://www.fda.gov/media/166348/download ; CCC 000008 https://www.fda.gov/media/185744/download ; CCC 000005
  https://www.fda.gov/media/186753/download ; CCC 000039 https://www.fda.gov/media/188065/download and supplement letter
  https://www.fda.gov/media/189007/download . Regulatory documents summarising firm submissions: strong for what firms state,
  silent on numbers.
- AgFunderNews, "Cultivated meat's comeback moment? UPSIDE Foods unveils dramatic scale-up, eyes fresh funding", 2026-11-17,
  https://agfundernews.com/cultivated-meats-comeback-moment-upside-foods-unveils-dramatic-scale-up-eyes-fresh-funding (company claims).
- Green Queen, "Upside Foods Launches New Cultivated Chicken at 'Everyday Pricing' with Second US Approval & 10,000x Scale-Up",
  2026-11-17 (updated 2026-11-21), https://www.greenqueen.com.hk/?p=89983 (company claims).
