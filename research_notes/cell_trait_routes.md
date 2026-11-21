# Cell traits and the routes that have shown them

Date: 2026-11-19; updated 2026-11-20 (the all-favourable example's traits, section 4) and 2026-11-21 (the appendix of odds deleted). Code: `cell_traits.py` (`routes`, `routes_needed`, `combination`); inputs `cr_*` in `inputs.py`; tests in
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
- Selected meat cells: `ammonia_tolerance_and_filter_life.md` section 10 gives the model's rough judgement (made while building the
  model with an AI assistant, not measured) of about 20% that selection reaches 0.055 in a meat cell; no meat cell has shown it.

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
- **The low-lactate example** (0.14, 0.42, 36 h, 2 ng): a lactate of 0.42 has been shown only in CHO; low ammonia with a 36-hour
  doubling has not yet been shown together in one meat cell.
- **The all-favourable example** (since 2026-11-20 one case, `scenarios.all_favourable`: 0.054, 0.279, 16 h, 3 ng; before, 0.055,
  0.279, 24 h, 2 ng): it takes Humbird's enhanced cell where that is more favourable. Its ammonia and lactate have been shown only in
  CHO (the ammonia at a plateau); a doubling near 16 hours only in immortalised bovine satellite cells grown with serum (15-17 h); a
  3 ng cell is near the 3.3 ng measured in chicken cells. None of these has been shown together with the others. This note does not
  say how such cells would be obtained.

## 5. Not found

- A lactate yield below 1.05 for any meat cell, by any route.
- A meat cell selected for low ammonia, with a figure.
- Doubling time, density, ammonia and lactate for the eight SciFi Foods bovine lines released through the Tufts open cell bank
  (October 2025): the first single public line that could anchor "Published cells" (TODO.md).

## Appendix: judged odds by 2035 (deleted 2026-11-21)

Until 2026-11-21 this appendix kept a table of odds by 2035 for each switch, a rough judgement made on 2026-11-19 while building
the model with an AI assistant, left over from a forecast that was built and dropped the same day. It was deleted: nothing in the
model read it, it was a forecast in all but name, and its retention row was set for a density (191 g/L) the low-lactate example no
longer runs at (168 g/L since 2026-11-21). The git history keeps it.
