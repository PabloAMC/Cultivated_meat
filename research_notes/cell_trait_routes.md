# Cell traits and the routes that have shown them

Date: 2026-11-19. Code: `cell_traits.py` (`routes`, `routes_needed`, `combination`); inputs `cr_*` in `inputs.py`; tests in
`tests/test_scenarios.py` (section 12d). Nothing here is a forecast or a probability: it records what has been shown, by which route.

## 1. Why traits, not routes

The cost model uses four traits of the cells: the ammonia a kilo of cells makes as it grows, the lactate made per glucose taken up,
the doubling time and the mass of a cell. Until 2026-11-19 the scenarios offered them as named kinds of cell ("selected",
"engineered"), which tied each level to a route and made genetic engineering look necessary for the cheaper cases. The author: "The
problem with the current framing is that makes GMO look necessary, but I am not sure." So the traits are inputs in their own right,
and `routes_needed` says, for any set of values, the least intrusive route that has shown each level so far.

The routes, least intrusive first: a feed change in meat cells; selection or adaptation in meat cells, without engineering
(spontaneous immortalisation counts here); no engineering, in other cells only (CHO and the like: selection, adaptation or a process
change); genetic engineering, in any cells. A level better than every route has shown is "not shown by any route".

## 2. The table (generated)

| trait | a feed change, in meat cells | selection or adaptation, in meat cells | no engineering, other cells only | genetic engineering, any cells | not shown by any route |
|---|---|---|---|---|---|
| ammonia made per kilo of cells grown (mol/kg wet) | 0.14 | nothing better | 0.054 | 0 | nothing: zero has been shown |
| lactate made per glucose taken up (mol/mol) | 1.05 | nothing better | 0 | 0 | nothing: zero has been shown |
| doubling time (h) | 25.7 | 20 | nothing better | 15 | below 15 |
| mass of a cell (pg wet) | 3300 | nothing better | nothing better | nothing better | above 3300 |

The verdict for a set of traits: "No genetic engineering needed: each trait has been shown without it" (in meat cells, or with the
traits shown only in other cells named), "These traits have so far been shown only with genetic engineering: ..." or "Not yet
shown by any route: ...". Each trait is judged alone; `combination` adds what has not been shown together (low ammonia with a
doubling under 42.9 hours). The verdict never says engineering is necessary.

## 3. The evidence, both ways

**Ammonia** (mol per kilo of wet cells grown; lower is better).
- *Feed change, meat cells: 0.14.* Bovine fibro-adipogenic progenitors with glutamine replaced by alpha-ketoglutarate, pyruvate or
  glutamate, spinner flasks (Hubalek et al. 2023, full text): "more than 5-fold" below the 0.70 with glutamine, so an upper bound.
  Against a lower reading: it is the only stirred culture of growing meat-relevant cells. For a lower one: the same paper's
  orbital-shaker runs found no ammonia from the replacement substrates (a tenfold disagreement, unexplained). The model uses the
  stirred figure.
- *No engineering, other cells only: 0.054.* CHO perfused with a glucose-limited feed at about 130 million cells/mL held about 0.5
  fmol a cell an hour (Mayrhofer et al. 2020), the figure behind Humbird's enhanced cell; the cells were at a plateau, not growing.
  CHO-K1 adapted to glutamine-free medium by FACS-assisted selection grew with "greatly decreased" ammonia (no figure found).
- *Engineering: zero.* Knocking out glutaminases and asparaginase eliminated ammonia during growth (ISCCM11 poster, 2025; not peer
  reviewed). An Upside Foods patent describes glutamine-synthetase lines (GFI's deep dive cites about 20% less ammonia).
- Selected meat cells: `ammonia_tolerance_and_filter_life.md` section 10 puts about 20% on selection reaching 0.055 in a meat cell.

**Lactate** (mol per mol of all glucose taken up; lower is better).
- *Meat cells: 1.05,* chicken fibroblasts in TFF perfusion (Pasitka et al. 2024, snippet). No lower figure was found for a meat cell
  by any route.
- *No engineering, other cells only: zero.* Feeding glucose only as the pH rises (HIPDOG) eliminated lactate build-up in CHO fed-batch
  up to 2,500 L (Gagnon et al. 2011, abstract); glucose-limited CHO perfusion turned the cells to consuming lactate (Mayrhofer 2020);
  lactate-adapted CHO reached 0.39 (Freund and Croughan 2018). These are process changes and adaptation, in CHO.
- *Engineering: zero.* Ldha and Pdk knockouts in CHO and HEK293 (Hefzi et al. 2024, preprint).

**Doubling time** (hours; lower is better).
- *Meat cells, standard feed: 25.7 h* (bovine fibro-adipogenic progenitors with glutamine, Hubalek 2023). With the low-ammonia feed
  the same cells took 42.9 to 54.2 h: fast and low-ammonia have not been shown together.
- *Meat cells, selection without engineering: 20 h,* spontaneously immortalised chicken fibroblasts on a surface (Pasitka et al.
  2023, snippet of figure text); Atlantic mackerel Mack1, 24 h with 20% serum (Saad et al. 2023).
- *Engineering: 15–17 h,* immortalised bovine satellite cells with serum (Stout et al. 2023).
- Below 15 h nothing is shown; physics allows about 8–9 h (`gf_and_doubling_bounds.md`).

**Mass of a cell** (pg wet; larger cells respire less per gram and cost less).
- Chicken cells: about 3.3 ng from a density of 108 million cells/mL at 36% w/v (Pasitka et al. 2024, abstract, converted); SuperMeat
  reports 1.0–1.75 ng. No bovine figure. The model uses 2 ng for every kind of cell (range 1–3 ng, drawn in the bands); Humbird's
  optimistic design keeps his 3 ng. A cell's mass is measured, not chosen by a route.

## 4. What it does to the reference points

- **Published cells** (0.14, 1.05, 43 h, 2 ng): each trait shown in meat cells.
- **The low-lactate example** (0.14, 0.42, 36 h, 2 ng): no genetic engineering needed, but a lactate of 0.42 only in CHO; low ammonia with a
  36-hour doubling not yet together in one meat cell.
- **The all-favourable example** (0.055, 0.279, 24 h, 2 ng): no genetic engineering needed by this table, but its ammonia and
  lactate only in CHO (the ammonia at a plateau) and not together with fast growth. The name says how such cells would most likely be
  made, not that they must be.

## 5. Not found

- A lactate yield below 1.05 for any meat cell, by any route.
- A meat cell selected for low ammonia, with a figure.
- Doubling time, density, ammonia and lactate for the eight SciFi Foods bovine lines released through the Tufts open cell bank
  (October 2025): the first single public line that could anchor "Published cells" (TODO.md).

## Appendix: judged odds by 2035 (not a forecast; not used by the model)

On 2026-11-19 a forecast drawn from these odds was built and then dropped at the author's direction ("I like the idea of clouds,
but I do not like the idea of forecasts"). The odds are kept as a record of how far each route has got, as judged that day. Nothing
in the model reads them.

| switch | settings, favourable first, with the author's odds for 2035 | median | where the odds come from |
|---|---|---|---|
| Kind of cells | engineered 25%, selected on low-waste feed 40%, best measured 30%, ordinary 5% | selected on low-waste feed | judgement: engineering has no meat-cell result yet; selection and the feed change are shown in flasks |
| Growth speed | 24 h 10%, 30 h 15%, 36 h 20%, 43 h 55% | 43 h | `cost_scenarios.md`: 24 h 10%, 30 h or faster 25%, 36 h or faster 45%, 43 h or faster 70% (slower is put at 43 h) |
| The plant | food-grade, shared medium 65%, food-grade plant 30%, pharma-style plant 5% | food-grade, shared medium | `cheap_plant_study.md`: about 65% for a plant at or below the shared-medium plant's cost |
| Gas the cells tolerate | 6 mm/s 45%, 4 mm/s 35%, 2 mm/s 20% | 4 mm/s | `gas_exchange_study.md`: 6 mm/s tolerable at 20 m³ about 50% |
| Tank tricks that work | all three 25%, column and pressure 25%, column only 10%, none 40% | column and pressure | `gas_exchange_study.md`: a column 60%, then 1 bar 85%, then recycled oxygen 50% (judgement) |
| Runs lost | 0.2% a day 10%, 0.6% a day 45%, 1% a day 30%, 2% a day 15% | 0.6% a day | makers report 0.6–2.2% a day (Powell 2025); judgement for 2035 |
| Restart after a loss | 4 days (neighbour) 20%, 14 days 55%, 21 days 15%, 30 days 10% | 14 days | judgement; reseeding from a neighbour has not been reported |
| Growth factors | none 25%, 30% 45%, 60% 20%, all 10% | 30% | judgement; tied to the kind of cells |
| Price of the medium | nutrient floor 10%, $0.20/L 50%, $0.30/L 25%, $0.50/L 15% | $0.20/L | `medium_cost_gfi.md`: $0.20 announced for 2025, $0.07 the lowest report, $0.50 reported |
| Tank size, if run in fed-batch | 100 m³ 7%, 50 m³ 13%, 20 m³ 80% | 20 m³ | `tank_size.md` section 7: 50 m³ about 12% and 100 m³ about 5% by the end of 2035 |
| Cells held back at 20 m³ for a month (perfusion) | at 120 g/L: filter 34%, aggregates 15%, either 44%, 191 g/L: filter 20%, aggregates 8%, either 27%, 258 g/L: filter 16%, aggregates 5%, either 20% | fed-batch | a filter possible at 75% / 45% / 35% (`retention_devices.md`; 191 g/L re-judged), times 45% that it runs in production by 2035; aggregates by 2035 (`retention_aggregates.md`) |
