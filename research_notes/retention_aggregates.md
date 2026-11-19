# Holding the cells back without a membrane: aggregates and carriers

> Repinned 2026-11-19 (scenario restructure): every kind of cell weighs 2 ng, so the best case's (Engineered cells, all favourable) cells are no longer Humbird's 3 ng. Its figures: aggregates $8.52 (range $7.98–12.37), carriers $39.45 (range $12.25–315.89, the beads hold it to 26 g/L), oxygenated aggregate 281 um at 0.10 mmol/L (443 and 520 um at 0.21 and 0.28), uptake 0.165 mmol/g/h; its 300 um aggregates lose 0.04% of growth. The body below keeps the earlier best-case figures where it quotes them.

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

Research date: 2026-11-19. Code: `retention.py` (devices `aggregates` and `microcarriers`; `particle`, `particle_case`,
`critical_diameter`, `hypoxic_share`, `growth_penalty`, `oxygen_sizes`, `aggregate_scan`); inputs `rt_part_*`, `rt_agg_*`,
`rt_o2_*`, `rt_mc_*` in `inputs.py`; tests `tests/test_retention.py` (`check_particles`). Costs are 2025 dollars per kg of wet
cells, for a plant built to each design. No default of the model changes. Parent note: `retention_devices.md`.

Source tags: **FT** full text (or the relevant section) read; **SNIP** a search snippet or abstract only; **MEM** from memory,
not checked in this pass. No source on carrier price was read in full, and no price for an edible carrier was found.

## 1. The answer

The question was: can cells be held back without a membrane? A single cell settles too slowly for a settler at 18% cells by
volume (`retention_devices.md`). Cells in a particle settle far faster. Two ways to put them in one:

| Route | Reference | Selected cells | Engineered cells, all favourable | Selected cells range | What limits it | What has been shown |
|---|---|---|---|---|---|---|
| TFF loop (the model's default) | $12.81 | $32.80 | $11.46 | $26.48-78.74 | membranes | 2.14e8 cells/mL for days in 4 L |
| **Cells grown as aggregates, gravity settler** | **$12.12** | **$20.39** | **$8.34** (held to 193 g/L) | $19.95-29.08 | whether the cells grow as aggregates at all, and keep their size for a month | 33-35e6 iPSC/mL (about 40 g/L) in 150 mL for 7 days; aggregates held back in 8 L |
| **Cells on edible carriers, gravity settler** | **$37.43** (held to 36 g/L) | **$84.39** (held to 26 g/L) | **$28.53** (held to 36 g/L) | $28.98-451.86 | the beads take the tank's volume | 8e6 Vero/mL (about 20 g/L) in 3 L |

- **Aggregates would do what the hoped-for device assumed.** If a meat cell line grows as clumps of 100-300 um and keeps that
  size, a plain settler of 22 m2 holds Central's culture back for $4k per m3 of tank. Central would cost $20.39 against $32.80
  with the filter loop, and against the $20.49 the old hoped-for device charged. The physics allows it. The biology has not been
  shown: the densest aggregate culture found is about a fifth of Central's density, for a week, in 150 mL.
- **Carriers solve retention but not density.** A layer of cells 3.5 um thick on a bead of 190 um is a tenth of the bead's
  volume. When the beads fill the quarter of the tank the model allows any suspension, the cells reach 26 g/L in Central. At
  that density the harvest carries all the medium out, so no device is needed at all, and the tank makes a seventh of the
  kilos. Even with every carrier input at its favourable end the cells reach 94 g/L, half of Central's 191. The product
  would be 86-90% bead by wet weight.
- **Oxygen does not bind at the default sizes.** At 0.10 mmol/L the middle of an aggregate of Central's cells stays above the
  level cells need to divide up to 307 um across. Aggregates are broken up at 300 um. Larger ones lose a little growth (section 4).

## 2. How each route is modelled

Both routes use the inclined settler of `retention_devices.md` ($3.5k per m2 of plate, 17 litres of culture held per m2,
designed to overflow at half the crowded settling speed), sized on the speed of the particle, not of a cell.

**What a particle is** (`retention.particle`).

- Aggregate: cells are 75% of its volume (`rt_agg_cell_share`, 0.60-0.85); the rest is liquid that moves with it. Spheroids
  hold about 15% extracellular space (arXiv 2011.01131, SNIP); random packing of spheres is 64%; iPSC aggregates hold cavities
  (Manstein 2021, FT). Its density excess over medium is 0.75 x 29 = 22 kg/m3.
- Carrier: a swollen bead of 190 um (Cytodex 1 median, Cytiva datasheet, SNIP), 1.03 g/mL, covered at 1.8e5 cells/cm2
  (`rt_mc_cells_cm2`, 1e5-3e5: El Wajgali 2011, FT, 3.9e6 Vero/mL on 5 g/L of Cytodex 1; Eppendorf note 414, SNIP, 8e6/mL on
  10 g/L of Cytodex 3). The cells, laid flat, make a film t = cells per cm2 x mass per cell / cell density thick, and are a share
  6t / (6t + d) of the loaded bead. Dry carrier per kg of cells = solids x d / (6 x cells per cm2 x mass per cell), with 0.07 g
  of dry carrier per mL of swollen bead (Cytodex 1's 4,400 cm2/g and 4.3e6 beads/g, SNIP).

**The thickness rule.** The model lets single cells take a quarter of the tank's volume (258 g/L, Humbird's viscosity limit).
The viscosity of a suspension follows the volume its particles take, not their size, so here the particles, with the liquid
inside them, may take the same 0.249 (`rt_part_phi_max`, 0.20-0.35). The densest culture is then 0.249 x the cells' share of a
particle x 1,036 g/L: 193 g/L for aggregates, 26 g/L for carriers of Central's 2 ng cells, 36 g/L for the 3 ng cells of the
reference and best cases. When a case's density is above this, the case is costed at the cap (an `explore` density cap).
Microcarrier cultures have run at 10 g/L of Cytodex 3, about 15% of the volume in beads (SNIP); no source gave a firm upper
limit.

**Settling.** Stokes' speed goes as diameter squared times density excess. Central's 2 ng cell (15.4 um) settles at 1.8 cm/h.
The smallest aggregate the settler must hold, a freshly broken one of 100 um (`rt_agg_d_min_um`), settles at 57 cm/h, 31 times
faster; one of 300 um, about 280 times. A loaded bead settles at 239 cm/h. Crowding slows them as (1 - particle fraction)^4.65. In Central the aggregates take 25% of the volume, so the design speed is 57 x 0.27 x 0.5 = 7.7 cm/h, the plates
need 22 m2, they hold 0.38 m3 of culture outside the tank (2.4% of it) and an aggregate spends about 16 minutes on them without
oxygen. A settler for single cells would need 488 m2 and hold 8.3 m3, half the culture.

**Cells lost.** 3% of the grown cells leave with the cleared liquid as single cells or small clumps (`rt_part_loss`, 1-8%). A
settling-tube patent for Cytodex 3 held every bead and over 95% of the cells (SNIP). Huang 2020 (FT) found that a plain dip-tube
settler let aggregates go, and ended with a spiral settler plus a 20 um filter back-flushed for 10 s every 7 minutes. The model
costs the settler only; a polishing screen of that kind is small next to 22 m2 of plate.

**Carriers in the product.** The carrier is taken to be edible and to stay in the product, as in Yen 2023 (FT), where whole
cell-coated chitosan-collagen beads went into the food. It is bought once at $10 a kg dry (`rt_mc_price`, 3-50; assumed, since
no price for an edible carrier was found: food gelatin, chitosan and plant protein trade at a few to tens of dollars a kg, MEM).
The cost per kg is charged per kg of cells; the carrier's own mass is not counted as product. Cytodex 1 sells at about EUR 7.6
a gram (Fisher, 500 g pack, SNIP), which at 0.62 kg a kilo of cells would be about $5,000 per kg.

## 3. The oxygen limit

Oxygen reaches the middle of an aggregate only by diffusion. With uptake Q per volume of aggregate (zero order) and dissolved
oxygen C in the liquid around it, the middle of a sphere of radius R sits at C - Q R^2 (1/(6D) + 2/(3 Sh D_w)). The first term is
diffusion inside (D = 2e-9 m2/s, `rt_o2_diff_tissue`, 1.5-2.5e-9; Grimes and Currell, bioRxiv 271890, FT). The second is the
liquid film around it (D_w = 3e-9 m2/s; Sherwood number 10, `rt_o2_sherwood`, 3-20, from mass transfer to a 200 um particle at
the Kolmogorov scale of a stirred tank at 0.01-0.1 W/kg; 2 in still liquid). Q is the model's own uptake: Cells.qo2 (0.137
mmol/g/h for Central's cells, 0.149 for the 3 ng cells) x 0.75 x 1,036 g/L, about 0.030 mol/m3/s.

Cells below 0.026 mmol/L (20 mmHg, `rt_o2_prolif`, 0.013-0.065) are taken not to divide. Gomes et al. 2016 (PLoS ONE, FT) put
the level that sustains proliferation in HCT116 spheroids at about 20 mmHg, with half of it lost below; hypoxia stains appear
below 10 mmHg (same, FT); necrosis began at a mean of 42-57 mmHg in tumour spheroids in air-saturated medium (Mueller-Klieser
1982, SNIP).

The largest aggregate whose middle stays at 0.026 mmol/L (`oxygen_sizes`):

| Cells | At the case's own setpoint | 0.10 mmol/L | 0.21 (air) | 0.28 (Humbird's tank) |
|---|---|---|---|---|
| Reference (3 ng, 24 h) | 543 um at 0.28 | 295 um | 466 um | 547 um |
| Selected cells (2 ng, 36 h) | 307 um at 0.10 | 307 um | 485 um | 570 um |
| Engineered cells, all favourable (3 ng, 24 h) | 295 um at 0.10 | 295 um | 466 um | 547 um |

Without the film Central's size would be 346 um; with a film of Sherwood number 2 (still liquid), 227 um. At the unfavourable
end of the proliferation level (0.065 mmol/L) it is 211 um; at the favourable end, 333 um.

**What the model does with it** (`growth_penalty`): a growth penalty, not a flag. Aggregates grow from 100 um to the size at
which they are broken up (`rt_agg_d_max_um`, 300 um, 200-450; Huang 2020, FT, held the mean below 300 um and passaged every
5 days; Manstein 2021, FT, 250-280 um at 80 rpm). In steady state the cells are spread evenly over the logarithm of aggregate
size, because each aggregate spends the same time in each doubling of its mass. The share of cells below 0.026 mmol/L,
averaged that way, is taken not to grow, and the case's doubling time is divided by one minus that share. It is worked out
once with the case's cells as they are. Inside the starved core the uptake is set to zero, so the core does not deepen the drop.

At the default sizes nothing is lost: Central's aggregates stop at 300 um against 307 um. The best case's 3 ng cells reach
295 um, so its largest aggregates lose 2e-6 of their growth. **The model keeps the scenarios' 0.10 mmol/L.** A higher setpoint
raises the size that stays oxygenated but costs oxygen transfer (`aggregate_scan`, Central):

| Largest aggregate | At 0.10 mmol/L: growth lost, density, cost | At 0.28 mmol/L |
|---|---|---|
| 300 um | 0%, 191 g/L, $20.39 | 0%, 172 g/L, $21.34 |
| 400 um | 0.9%, 192 g/L, $20.45 | 0%, 172 g/L, $21.34 |
| 500 um | 3.5%, 193 g/L, $20.62 | 0%, 172 g/L, $21.34 |
| 600 um | 6.5%, 193 g/L, $20.95 | 0%, 172 g/L, $21.34 |

At 0.28 mmol/L the tank's oxygen transfer falls and so does its density, which costs more than oxygen starvation at any size up
to 600 um. Oxygen is not what limits this route. A layer of cells 3.5-5 um thick on a solid bead is far too thin for it to
matter for carriers.

## 4. What moves each route (Selected cells)

Each input alone at the ends of its range:

- **Aggregates:** the cells' share of an aggregate (0.60: the cap falls to 155 g/L, $22.44) and the volume the particles may
  take (0.20: also 155 g/L, $22.38) matter most; cells lost with the cleared liquid ($19.98 at 1%, $21.50 at 8%); the size at
  break-up (450 um: 2.1% of growth lost, $20.52) and the proliferation level (0.065 mmol/L: $20.54) matter little. All
  unfavourable together: $29.08 at 124 g/L, still below the filter loop's $32.80.
- **Carriers:** cells per cm2 ($144.44 at 1e5, $57.07 at 3e5), bead size ($52.26 at 100 um, $108.09 at 250 um), the volume
  the beads may take ($64.33 at 0.35) and the carrier's price ($79.95 at $3 a kg, $109.78 at $50). All favourable together:
  $28.98 at 94 g/L.

## 5. Evidence

**That it can work.**
- Aggregates settle fast enough to be held by settling: a spiral settler with a back-flushed 20 um filter held aggregates in
  8 L, over 1e10 cells a run (Huang 2020, Cell & Gene Therapy Insights, FT). Patents describe angled settling chambers and
  perfusion rates set so that aggregates of 100-800 um settle out (US10100277B2 and others, SNIP).
- Perfused aggregate culture reached 33-35e6 iPSC/mL in 150 mL in 7 days, with a 20-40 um outflow filter, at 40% of air
  saturation (Manstein 2021, Stem Cells Transl Med, FT). iPSC aggregates have been grown at 0.1-80 L in vertical-wheel
  vessels, at about 1.5e6 cells/mL (PBS Biotech poster, SNIP).
- Bovine adipose-derived stem cells grew as spheroids above 400 um for 14 days with no hypoxia or cell-death markers, in
  air-saturated wells, and turned into fat cells well (PMC11496621, FT). Porcine muscle cells and C2C12 formed spheroids in a
  stirred bioreactor and kept their ability to form muscle (Cells 2022, 11:1453, SNIP).
- Carriers have run at up to 6,000 L in vaccine plants (Engineering Conferences abstract, SNIP), and settling tubes held
  every bead that was measured (El Wajgali 2011, FT).

**That it fails or is limited.**
- No aggregate culture comes near 191 g/L. The best is about 40 g/L, at 150 mL, for 7 days (Manstein 2021). Growth there slowed
  from day 4, and the aggregates held cavities below 300 um, which the authors put down to glucose, not oxygen.
- Size is not held in continuous culture. Aggregates grow 32-48 um a day in diameter and neither split nor merge on their own
  (Huang 2020; Manstein 2021, FT); merging gets worse at larger scale (PBS poster, SNIP). Every pluripotent process found runs
  5-8 day batches with a dissociation step between them. A 33-day run would need about 7-11 break-ups (one each 3 doublings,
  from 150 to 300 um), in line and sterile. Nobody has shown that.
- Retention at scale is not shown. A plain dip-tube settler lost aggregates; an ATF filter was too harsh; an acoustic settler
  trapped them (Huang 2020, FT). Every retention device found ends in a 20-40 um filter; no 50-100 um screen used with
  aggregates was found.
- Myogenic aggregate cultures doubled in over 150 h (Bodiou 2020 review, Front. Nutr., FT); C2C12 on Cytodex 3 formed large
  clumps (npj Sci. Food 2024, SNIP).
- No cultivated-meat company has published aggregate or carrier culture data at density. Believer's 130e6 cells/mL (Pasitka
  2024, SNIP) was held back by tangential-flow filtration.
- Carriers: the densest perfused culture found is 8e6 cells/mL (Eppendorf, SNIP), and a patent claims 1-2e7 (SNIP). Macroporous
  carriers reached 1-2.3e7 CHO cells/mL (Xiao 1999 and others, SNIP). A patent says carrier cultures "lack the capacity" for
  densities above 1e8 cells/mL (SNIP).
- No measured settling speed of a cell aggregate against its diameter was found. Stokes' law was off by more than 30% for live
  cells in long perfusion runs (Cleveland State, SNIP).

## 6. Probabilities (judgement)

| Statement | Probability |
|---|---|
| A meat cell line grows as 100-300 um aggregates at 80% or more of its single-cell growth rate | 45% |
| Aggregate size is held for 33 days by in-line break-up or shear, losing under 5% of the cells | 25% |
| A gravity settler, with a back-flushed screen, holds 97% or more of the cells of an aggregate culture at 20 m3 | 50% |
| By 2035, aggregates of a meat cell line are held at the reference's 120 g/L in a 20 m3 perfusion tank for a month | 15% |
| By 2035, the same at Selected cells' 191 g/L (aggregates taking a quarter of the volume) | 8% |
| By 2035, carriers of any kind hold 100 g/L of meat cells in perfusion | 4% |
| By 2035, carriers hold Selected cells' 191 g/L | under 1% |

The 8% for aggregates at Central is above the 5% given to a settler for single cells at that density, and below the 35% for a
filter, because the physics works but every step past 40 g/L and a week is unshown. Most of the risk is biology (growth in
aggregates, size held for a month), not engineering.

## 7. What this means for the model

1. **Aggregates are the only membrane-free route with a cost near the hoped-for device.** If they work, Central costs $20.39
   (range $19.95-29.08) in place of $32.80, the best case $8.34 (held to 193 g/L) in place of $11.46, and the reference $12.12
   in place of $12.81. No default changes: the route rests on an 8% chance at Central's density.
2. **Microcarriers are not a route to Central.** They cost $84.39 in Central because the beads hold the tank to 26 g/L. The
   cells' share of a loaded bead, not the device, sets the cost.
3. **The experiment that would settle it:** grow a meat cell line (chicken fibroblasts or bovine satellite cells) as aggregates
   in a 2-10 L perfused stirred tank for 30 days, with a settler and an in-line break-up step. Measure density reached, growth
   rate against aggregate size, cells lost over the settler, and whether size holds. This is a pilot experiment, not a plant.

## 8. Not found

- A measured settling speed of cell aggregates against diameter, and their effective density.
- Any aggregate or carrier culture of meat cells in perfusion, at any density, for more than a week.
- A price for an edible carrier, or a techno-economic study that prices carriers.
- Cell density inside macroporous carriers (Cytopore, CultiSpher) in cells per mL of carrier.
- The oxygen level at which meat cells stop dividing.
