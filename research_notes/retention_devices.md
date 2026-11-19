# Holding the cells back in a 20 m3 perfusion tank

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.

> Recomputed 2026-11-16 on the current model (bubble protectant, antifoam's cost to oxygen transfer, bought oxygen in a yeast-style plant, dissolved oxygen held at half of air saturation, medium at least the culture that leaves with the cells).

Research date: 2026-11-15. Code: `retention.py`; inputs `rt_*` in `inputs.py`; tests `tests/test_retention.py`. Costs are 2025
dollars per kg of wet cells, for a plant built to each design.

Two research passes sit behind this note. Each has its own file with every source, its URL and how much of it was read:

- `retention_devices_sources/membrane_filters.md`: ATF and TFF hollow-fibre filters, TFDF, spin filters, rotating and
  vibrating filters, the viscosity of thick cultures, and filtration at 100-200 million cells per mL.
- `retention_devices_sources/settlers_centrifuges.md`: inclined settlers, acoustic settlers, centrifuges built for animal
  cells, disc-stack separators from the yeast and dairy industries, hydrocyclones, and separators on the whole outflow.

Access levels: **full** (read in full), **part** (read in part, or through a fetch tool's extract), **abstract**, **snippet**
(a search result only), **secondary** (another document quotes it). No source on price was read in full: the prices are the
weakest numbers here.

## 1. The question

Every cost scenario uses a 20 m3 stirred tank (16 m3 of liquid) in perfusion. Fresh medium flows through. A device holds the
cells back. The harvest is a steady bleed of whole culture. Nobody has run animal cells in perfusion above about 4 m3. The model
charges a hoped-for device at `pf_capex_retention`: $89k per m3 of tank, from one design study (Pasitka 2024) that does not say
what the device is. This note asks which real devices can do the job, and what they would cost.

## 2. The duty

`retention.duty()` works it out from `floor_physics.explore()`:

- harvest H = output per tank-year / (8,760 h x uptime), in kg of wet cells an hour;
- medium in Q = litres of medium per kg x H;
- bleed B = H / density (the bleed is the product: whole culture);
- permeate P = Q - B (the cell-free liquid the device must clear).

| case | density | cells by volume | harvest | medium in | bleed | permeate | permeate a day |
|---|---|---|---|---|---|---|---|
| Reference | 120 g/L | 12% | 55.5 kg/h | 0.62 m3/h (0.93 tank volumes a day) | 0.46 m3/h | **0.16 m3/h** | 0.24 tank volumes |
| Central | 191 g/L | 18% | 57.5 kg/h | 2.01 m3/h (3.0) | 0.30 m3/h | **1.71 m3/h** | 2.6 tank volumes |
| Best case | 258 g/L | 25% | 118 kg/h | 1.63 m3/h (2.4) | 0.46 m3/h | **1.17 m3/h** | 1.8 tank volumes |

Two things follow.

- **The reference duty is light.** The product is the cells, so the bleed carries most of the liquid out. The device only clears
  2.8 litres of permeate per kg.
- **The central duty is ten times heavier.** The central cells make more ammonia and are held to 4 mmol/L of it, so each kg needs
  35 litres of medium (28 before the 2026-11-19 audit, at 5 mmol/L). At 191 g/L the bleed carries only 5.2 of them. The device
  must clear 30 litres per kg at 18% cells by volume.

Viscosity: a culture that is 12% cells is about 1.4 times as viscous as medium. At 25% it is about 2.2 to 2.3 times. Cell
suspensions turn elastic from about 40% (Iordan et al. 2007, part; Thomas's and Krieger's formulas).

## 3. The devices

| Device | Densest culture and largest scale shown | Central: what it takes | Central: capital per m3 of tank | Central: cost per kg (range) | Verdict |
|---|---|---|---|---|---|
| Hoped-for device (the old default) | nothing: the device is not named | - | $89k | **$20.49** ($19.74-23.61) | Not a real device |
| ATF hollow-fibre filter | 50 days on 50 L at volume fraction 0.13 (Ott 2024, full); 1.3e8 cells/mL for days in 4 L, where its vacuum failed (Clincke 2013, full); units rated to 5,000 L | 32 ATF 10s, 352 m2 | $589k | **$37.48** ($27.61-104.70) | Possible at the edge; costly |
| TFF hollow-fibre loop | 2.14e8 cells/mL (half the volume) for days in 4 L; one fibre lasted 30 days (Clincke 2013, full); nothing published above pilot scale | 343 m2 of membrane | $32k | **$32.80** ($26.48-78.74) | Possible at the edge; membranes set the cost |
| Inclined (lamella) settler | 5e7 cells/mL (Coronel 2020); a 2,000 L tank (Romann 2023) | 488 m2 of plate; 8.3 m3 of culture outside the tank | $85k | - | **Not possible**: half of the culture would sit without oxygen |
| Acoustic settler | 200-400 L/day tested; 1,000 L/day the largest sold | 42 units | $386k | ($21.07-62.99) | Beyond what is shown; heat limits larger units |
| Disc-stack separator on the outflow | CHO feed at 28% packed volume; yeast recycled 2-3 times a day for 250-280 days (not animal cells) | 2 running + 1 spare; the culture passes 3.5 times a day | $120k | **$27.49** ($23.32-47.61) | Possible; burst cells set the cost |
| Hydrocyclone | 5e7 cells/mL in a 40 L bag (Bettinardi 2020, abstract) | feed 3.4 m3/h | $9k | ($24.58-61.99) | Beyond what is shown; loses a third of the cells |
| Spin filter | about 1e7 cells/mL | - | - | - | Not possible: its screen does not grow with the tank's volume, and it clogs |
| Fluidized-bed centrifuge (kSep) | cell harvests | about 86 cycles an hour | - | - | Not possible: one cycle holds 2.9 kg of cells |
| Cells grown as aggregates, gravity settler (added 2026-11-19) | 33-35e6 iPSC/mL (about 40 g/L) in 150 mL for 7 days (Manstein 2021, full); aggregates held back in 8 L (Huang 2020, full) | 22 m2 of plate; 0.38 m3 outside the tank | $4k | **$20.39** ($19.95-29.08) | Beyond what is shown; the cells must grow as aggregates and keep their size for a month |
| Cells on edible carriers, gravity settler (added 2026-11-19) | 8e6 Vero/mL (about 20 g/L) in 3 L (Eppendorf, snippet); carriers at up to 6,000 L | the beads hold the tank to 26 g/L, where the harvest carries all the medium out | $0k | **$84.39** ($28.98-451.86) | Not a route to Central: beads take the volume |

The ranges move each device's own inputs to their favourable and unfavourable ends together (`retention.scenario_range`). Every
other part of the scenario stays as it is.

Cells grown as aggregates or on edible carriers, held back by a plain settler, are worked out in `retention_aggregates.md`:
what limits them, the oxygen inside an aggregate, the evidence and the probabilities.

The same devices in the other two cases:

| Device | Reference ($12.45 with the hoped-for device) | Best case ($7.74 with the hoped-for device) |
|---|---|---|
| ATF | $13.22 (3 units) | $12.96 (22 units) |
| TFF | $12.81 | $11.46 |
| Settler | $11.79 (23 m2, 0.4 m3 outside the tank) | not possible (40% of the culture outside the tank) |
| Acoustic | $12.04 (4 units) | $8.43, beyond what is shown |
| Disc stack | $12.74 (1.6% of cells lost) | $9.01 (14% lost) |
| Hydrocyclone | $12.08 (2.6% lost) | $8.92, beyond what is shown |
| Aggregates | $12.12, beyond what is shown | $8.34, held to 193 g/L, beyond what is shown |
| Carriers | $37.43, held to 36 g/L | $28.53, held to 36 g/L |

## 4. How each device is costed

- **ATF**: units = permeate / (flux x 11 m2), rounded up. Flux 5 L/m2/h (`rt_flux_lmh`, 2-8.3). Each unit costs $200k (Humbird's
  $38.5M for 192 units; Pasitka implies $350k), times 1.84 to install. Membranes as below.
- **TFF**: membrane area = permeate / flux. Pumps, housings and skids at $1k per m2 (assumed; it gave Pasitka's $35k per m3 at
  the central duty when that case ran at 258 g/L, and gives $32k now), times 1.84.
- **Membranes** (ATF and TFF): litres of permeate per kg x $1,450 per m2 / 3,960 litres per m2 over a membrane's life, about
  $0.37 per litre of permeate. The life spans 900 litres per m2 (fouled in 4.5 days at 8.3 L/m2/h, Veje 2024, full) to 5,500
  (one TFF fibre for 30 days, Clincke 2013). **Membranes, not hardware, set the cost of filtering a thick, fast-fed culture.**
- **Membranes of lost runs** (since the 2026-11-19 audit; ATF, TFF, reused modules and dialysers). A run lost to contamination
  throws its membranes away before they have filtered the litres they were bought for. `explore()` and `retention.sizing` multiply
  the membrane's life by the share of a planned run an average start completes: 85% in the central case (1% of runs lost a day,
  33-day runs), 91% in the best case, 100% in the reference case. So the central case pays $0.43 per litre of permeate, $12.80 per
  kg (it was $8.33: 23 litres at $0.37). That is more than twice the $0.20 a litre it pays for medium. The ATF filter pays the same
  membranes as the TFF loop, so its extra cost is its hardware: $4.68 a kilo in the central case. Ceramic elements are cleaned in
  place and kept, so a lost run does not shorten their life.
- **Inclined settler**: one cell settles at Stokes' speed, slowed by crowding as (1 - fraction)^4.65. The plates are designed for
  half that speed. Plate area = permeate / design speed, at $3.5k per m2 installed (assumed). A settler holds 17 litres of culture
  per m2 (Romann's 2,000 L settler). It is marked not possible when it would hold more than 5% of the tank's culture outside the
  tank (Romann's held 1.5%), because that culture has no oxygen supply. At 258 g/L its oxygen lasts seconds.
- **Acoustic settler**: units = permeate per day / 1,000 litres, at $100k each (assumed; no price found), times 1.84.
- **Disc-stack separator on the outflow**: it takes the permeate plus enough culture to send the cells back as a concentrate at
  70% packed volume (Hundley and Konigsson 2020, part). Feed = permeate x (1 + fraction / (0.70 - fraction)). Each pass bursts
  4% of the cells it carries (2-12.5% measured on CHO by the vendor's staff). The share of grown cells lost is lysis x passes a day
  / (bleed a day + lysis x passes a day). In the central case the culture passes 3.5 times a day and 24% of the grown cells are
  lost. Units at 2 m3/h each, one spare, $800k each installed (assumed; no sterile price found), 10 kW each, maintenance 4% a year.
- **Hydrocyclone**: feed = permeate / 0.5 (half leaves as overflow). It returns 96% of the cells; the rest are lost. $50k per m3/h
  of feed (assumed).
- **Cost of a scenario with a device**: `explore()` with the device's capital in place of `pf_capex_retention` and its running
  cost as `extra_opex`. Then every cost per kg is divided by the share of grown cells that survive the device. No default
  changes; the hoped-for device reproduces every scenario's cost exactly (`tests/test_retention.py`).

## 5. Probabilities (judgement, from the two research passes)

| Statement | Probability |
|---|---|
| ATF or TFF holds 120 g/L at 20 m3 for a month at the reference duty, module swaps allowed | 75% |
| The reference duty is met at $89k per m3 or less and $2 a kg of membranes or less | 45% |
| A filter holds 258 g/L at 20 m3 for a month at the central duty, at any cost | 35% |
| The same, at $89k per m3 or less and $3 a kg of membranes or less | 8% |
| An inclined settler holds 120 g/L at 20 m3 for a month | 35% |
| An inclined settler holds 258 g/L (central duty) | 5% |
| Any acoustic device meets the central duty | 3% |
| A disc-stack separator on the whole outflow keeps the culture above 90% alive for a month: reference / central | 60% / 25% |
| Extra lysis per pass in a hermetic separator is 2% or less for these cells | 30% |
| A sterile hermetic separator runs closed for 33 days without contamination or seal failure | 55% |
| The model's assumption (a $89k per m3 device that loses no cells) is right for the central case | 20% |

These were judged when the central case ran at 258 g/L. Oxygen supply now limits its tank to 191 g/L (18% cells by volume), so the
rows that name 258 g/L describe the best case's density, not today's central duty.

## 6. What this means for the model

1. **The reference case is safe.** Several devices meet its light duty. With any of them the reference case costs $11.79 to
   $13.22 against $12.45.
2. **The central case is not.** Its 191 g/L and 35 litres of medium a kilo ask a device to clear 1.71 m3 an hour of permeate from
   a culture that is 18% cells. The devices shown at that density cost $27.49 to $37.48 a kilo in place of $20.49. The
   range is $23 to $105. The gap between a real device and the hoped-for one grew from $4.5–11.3 to $7.0–17.0 a kilo with the
   2026-11-19 audit: more litres to clear, and membranes for lost runs. The hoped-for device hides this, because it charges only capital, and the real cost is membranes or burst
   cells.
3. **Applied as the model's default on 2026-11-15, at Pablo's request:** retention is priced as a TFF hollow-fibre loop: capital of about $1k per m2 of membrane,
   times 1.84, plus $0.37 per litre of permeate for membranes ($0.43 in the central case once lost runs are counted). The scenarios would become:

   | scenario | before | with TFF (now the default) | with a disc stack |
   |---|---|---|---|
   | Best case | $7.74 | $11.46 | $9.01 |
   | Central | $20.49 | $32.80 | $27.49 |
   | Central, food-grade plant with shared medium | $17.63 | $29.94 | $23.75 |
   | Cautious (published cells) | $55.37 | $92.17 | $84.76 |
   | Reference | $12.45 | $12.81 | $12.74 |

   ("before" is the hoped-for device on the model of 2026-11-19 after the audit batch, not the figures of 2026-11-15.) The
   cautious case filters 87 of its 95 litres a kilo, so membranes alone are $37.48 of its $92.17. Its disc stack would lose a third
   of the cells.

   The scenarios' tank designs are chosen again under the new cost (`scenarios.design` runs on the model's default), and they
   come out the same. A thinner culture does not pay (`retention.density_scan`). Held at 180 g/L in place of the 191 g/L its tank
   allows, the central case filters 1.1% fewer litres a kilo and saves $0.1 of membranes, but the plant's capital per kilo
   rises by $0.4, because each tank makes fewer kilos: $33.18 against $32.80. At the worst membrane life (900 L/m2) the cost
   is $74.7 to $76.3 at any density from 100 to 258 g/L; there the thinnest culture (100 g/L) is the cheapest, by $1.58.
   Membrane life matters far more than density: it moves the central case by about $43. In the cautious case a thinner
   culture costs more too ($94.77 at 100 g/L against $92.17 at the 120 g/L its tank allows), and at 180 g/L none of its
   designs with all three tank tricks passes the loop's checks (`thick_culture.md`, section 7). The model has no density
   setpoint switch in any case.
4. **What would lower it.** Cells that need less medium per kg (less ammonia), so less permeate: the "kind of cells" switch now
   also decides the retention cost. Membranes that last longer at this density. A separator that bursts under 1% of the cells per
   pass: at 1% the central case costs $22.63. None is shown. Cells that grow as aggregates and keep their size for a month: a plain settler would
   then hold Central's culture back for $20.39 a kilo (`retention_aggregates.md`; judged 8% likely at Central's density by 2035).

## 7. What was not found

- Any price for a sterile disc-stack separator, an inclined settler, an acoustic device or a TFF skid at this scale.
- Membrane life at 2-5 L/m2/h and a quarter cells by volume over a month.
- Cells lost through a filter into the permeate.
- Any non-membrane perfusion of animal cells above 3,000 L or above about 5e7 cells/mL for a month.
- Mayrhofer 2020, Wolf 2019 and the Xu/Chen high-density papers were not read.
- Retention without a membrane by growing the cells in particles (aggregates, edible carriers) was researched on 2026-11-19:
  `retention_aggregates.md`.
