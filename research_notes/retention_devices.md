# Holding the cells back in a 20 m3 perfusion tank

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> **Current figures (2026-11-21, second batch; `python retention.py`).** After the engine fixes of the second batch (the building's
> power by floor and class, part of the crew per tank) and the thinner designs in the design search, the scenarios run the
> recycled-oxygen column held thinner: the low-lactate example at 168 g/L (16% cells by volume, 1.47 m³ of permeate an hour,
> $48.68 with the TFF loop, membranes $22.71 a kilo), the all-favourable example at 219 g/L ($6.97), Humbird's optimistic design
> at 120 g/L ($15.72). With each device, Humbird's optimistic design / the low-lactate example / the all-favourable example:
> hoped-for device $14.59 / $26.63 / $7.14; ATF $17.32 / $66.29 / $14.59; reused pharma modules $14.22 / $30.54 / $7.76;
> dialyser-grade fibres $13.86 / $26.28 / $6.97; ceramic $14.01 / $27.75 / $7.29; inclined settler $13.85 / $26.37 (not
> possible) / $6.99; acoustic $14.13 / $29.20 / $7.53; disc stack $14.92 / $33.53 (20% of the cells lost) / $7.64;
> hydrocyclone $14.19 / $35.81 / $7.62. The ATF is the dearest real device, $17.61 a kilo above the loop in the low-lactate
> example. The body below gives the figures of the morning of 2026-11-21 (the low-lactate example at 154 g/L, $49.50); its
> conclusions stand.

> Figures recomputed 2026-11-21 on the model of 2026-11-20: lactate tolerated 35 mmol/L, cells killed by bursting bubbles, a 2%
> harvest loss, twice the fed-batch crew in perfusion, membrane life 2,415 L/m2 in place of 3,960, medium-preparation capital,
> utilities in four parts, plant items charged per tank, thick cultures taking up oxygen more slowly (the low-lactate example's
> tank now holds 154 g/L, not 191), the bleed carrying the cells grown, the ATF priced with Humbird's accounting for bought
> equipment, and the all-favourable example redefined as `scenarios.all_favourable()` (3 ng cells, a 16-hour doubling,
> dialyser-grade fibres, a 42 m3 tank). Earlier repins: 2026-11-19 (nutrient floor $2.00, growth factors inside complete media
> prices; audit batch: ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance), 2026-11-16
> (bubble protectant, antifoam, dissolved oxygen at half of air saturation).

Research date: 2026-11-15. Code: `retention.py`; inputs `rt_*` in `inputs.py`; tests `tests/test_retention.py`. Costs are 2025
dollars per kg of wet cells harvested, for a plant built to each design.

Two research passes sit behind this note. Each has its own file with every source, its URL and how much of it was read:

- `retention_devices_sources/membrane_filters.md`: ATF and TFF hollow-fibre filters, TFDF, spin filters, rotating and
  vibrating filters, the viscosity of thick cultures, and filtration at 100-200 million cells per mL.
- `retention_devices_sources/settlers_centrifuges.md`: inclined settlers, acoustic settlers, centrifuges built for animal
  cells, disc-stack separators from the yeast and dairy industries, hydrocyclones, and separators on the whole outflow.

Access levels: **full** (read in full), **part** (read in part, or through a fetch tool's extract), **abstract**, **snippet**
(a search result only), **secondary** (another document quotes it). No source on price was read in full: the prices are the
weakest numbers here.

## 1. The question

Every cost scenario uses a stirred tank in perfusion (20 m3, 16 m3 of liquid, in the low-lactate example). Fresh medium flows
through. A device holds the cells back. The harvest is a steady bleed of whole culture. Nobody has run animal cells in perfusion
above about 4 m3. Until 2026-11-15 the model charged a hoped-for device at `pf_capex_retention`: $89k per m3 of tank, from one
design study (Pasitka 2024) that does not say what the device is. This note asks which real devices can do the job, and what
they would cost.

## 2. The duty

`retention.duty()` works it out from `floor_physics.explore()`:

- harvest H = output per tank-year / (8,760 h x uptime), in kg of wet cells harvested an hour;
- medium in Q = litres of medium per kg x H;
- bleed B = H / harvested share / density (the bleed is whole culture and carries the cells grown, of which the bubbles kill some
  and the harvest loses 2%);
- permeate P = Q - B (the cell-free liquid the device must clear).

| case | density | cells by volume | harvest | medium in | bleed | permeate | permeate a day |
|---|---|---|---|---|---|---|---|
| Humbird's optimistic design | 120 g/L | 12% | 50.0 kg/h | 0.62 m3/h (0.93 tank volumes a day) | 0.46 m3/h | **0.16 m3/h** (3.1 L/kg) | 0.24 tank volumes |
| Low-lactate example | 154 g/L | 15% | 41.7 kg/h | 1.62 m3/h (2.43) | 0.30 m3/h | **1.32 m3/h** (32 L/kg) | 1.98 tank volumes |
| All-favourable example (42 m3 tank) | 155 g/L | 15% | 209 kg/h | 2.44 m3/h (1.74) | 1.46 m3/h | **0.99 m3/h** (4.7 L/kg) | 0.71 tank volumes |

Two things follow.

- **The reference duty is light.** The product is the cells, so the bleed carries most of the liquid out. The device only clears
  3.1 litres of permeate per kg.
- **The low-lactate example's duty is ten times heavier per kilo.** Its cells make more ammonia and are held to 4 mmol/L of it,
  so each kg needs 39 litres of medium. At 154 g/L the bleed carries only 7.2 of them. The device must clear 32 litres per kg at
  15% cells by volume.

Viscosity: a culture that is 12% cells is about 1.4 times as viscous as medium. At 25% it is about 2.2 to 2.3 times. Cell
suspensions turn elastic from about 40% (Iordan et al. 2007, part; Thomas's and Krieger's formulas).

## 3. The devices

| Device | Densest culture and largest scale shown | Low-lactate example: what it takes | Low-lactate example: capital per m3 of tank | Low-lactate example: cost per kg (range) | Verdict |
|---|---|---|---|---|---|
| Hoped-for device (the old default) | nothing: the device is not named | - | $89k | **$27.97** ($26.94-32.27) | Not a real device |
| ATF hollow-fibre filter | 50 days on 50 L at volume fraction 0.13 (Ott 2024, full); 1.3e8 cells/mL for days in 4 L, where its vacuum failed (Clincke 2013, full); units rated to 5,000 L | 24 ATF 10s, 264 m2 | $1,501k | **$66.60** ($39.45-162.75) | Possible at the edge; the dearest real device |
| TFF hollow-fibre loop (the model's default) | 2.14e8 cells/mL (half the volume) for days in 4 L; one fibre lasted 30 days (Clincke 2013, full); nothing published above pilot scale | 264 m2 of membrane | $24k | **$49.50** ($34.09-89.58) | Possible at the edge; membranes set the cost |
| Inclined (lamella) settler | 5e7 cells/mL (Coronel 2020); a 2,000 L tank (Romann 2023) | 307 m2 of plate; 5.2 m3 of culture outside the tank | $54k | - | **Not possible**: a third of the culture would sit without oxygen |
| Acoustic settler | 200-400 L/day tested; 1,000 L/day the largest sold | 32 units | $294k | $30.35 ($28.33-72.96) | Beyond what is shown; heat limits larger units |
| Disc-stack separator on the outflow | CHO feed at 28% packed volume; yeast recycled 2-3 times a day for 250-280 days (not animal cells) | 2 running + 1 spare; the culture passes 2.5 times a day | $80k | **$34.34** ($30.42-53.22) | Possible; burst cells set the cost |
| Hydrocyclone | 5e7 cells/mL in a 40 L bag (Bettinardi 2020, abstract) | feed 2.6 m3/h | $7k | $36.47 ($32.02-71.16) | Beyond what is shown; loses a quarter of the cells |
| Spin filter | about 1e7 cells/mL | - | - | - | Not possible: its screen does not grow with the tank's volume, and it clogs |
| Fluidized-bed centrifuge (kSep) | cell harvests | about 86 cycles an hour | - | - | Not possible: one cycle holds 2.9 kg of cells |
| Cells grown as aggregates, gravity settler (added 2026-11-19) | 33-35e6 iPSC/mL (about 40 g/L) in 150 mL for 7 days (Manstein 2021, full); aggregates held back in 8 L (Huang 2020, full) | 13 m2 of plate; 0.22 m3 outside the tank | $2k | **$27.80** ($27.22-36.77) | Beyond what is shown; the cells must grow as aggregates and keep their size for a month |
| Cells on edible carriers, gravity settler (added 2026-11-19) | 8e6 Vero/mL (about 20 g/L) in 3 L (Eppendorf, snippet); carriers at up to 6,000 L | the beads hold the tank to 26 g/L, where the harvest carries all the medium out | $0k | **$96.46** ($36.02-491.52) | Not a route to the low-lactate example: beads take the volume |

The ranges move each device's own inputs to their favourable and unfavourable ends together (`retention.scenario_range`). Every
other part of the scenario stays as it is. Three membrane routes from other industries (reused pharma modules $31.70, dialyser-grade
fibres $27.52, ceramic membranes $28.97 in the low-lactate example) are in `retention_alternatives.md`.

Cells grown as aggregates or on edible carriers, held back by a plain settler, are worked out in `retention_aggregates.md`:
what limits them, the oxygen inside an aggregate, the evidence and the judgements.

The same devices in the other two cases:

| Device | Humbird's optimistic design ($15.93 with the TFF loop; $14.79 with the hoped-for device) | All-favourable example ($7.62 with its loop of dialyser-grade fibres; $7.93 with the hoped-for device) |
|---|---|---|
| ATF | $17.53 (3 units) | $12.72 (18 units) |
| TFF (the model's default) | $15.93 | $7.62 |
| Settler | $14.06 (23 m2, 0.4 m3 outside the tank) | not possible (9% of the culture outside the tank) |
| Acoustic | $14.34 (4 units) | $8.00 (24 units), beyond what is shown |
| Disc stack | $15.14 (1.6% of cells lost) | $8.02 (3.3% lost) |
| Hydrocyclone | $14.41 (2.6% lost) | $7.97 (5.1% lost), beyond what is shown |
| Aggregates | $14.46, beyond what is shown | $7.79, beyond what is shown |
| Carriers | $44.16, held to 36 g/L | $24.26, held to 36 g/L |

## 4. How each device is costed

- **ATF**: units = permeate / (flux x 11 m2), rounded up. Flux 5 L/m2/h (`rt_flux_lmh`, 2-8.3). Each unit's bare price is $200k
  (Humbird's $38.5M for 192 units; Pasitka implies $350k). Since 2026-11-20 it is charged as Humbird charges bought equipment
  (`retention.atf_factor`): x 1/0.9 for minor equipment, x 2.3 for installation, x 1.84 for engineering, construction, fees and
  contingency, and x 1.33 from his 2018 prices to 2025 dollars, 6.25 times the bare price in all. Until then it took only the
  1.84, 3.4 times less ($589k per m3 in the low-lactate example, against $1,501k now). Membranes as below.
- **TFF**: membrane area = permeate / flux. Pumps, housings and skids at $1k per m2 (`rt_tff_hw`, assumed; an installed cost),
  times 1.84: $24k per m3 of tank in the low-lactate example.
- **Membranes** (ATF and TFF): litres of permeate per kg x $1,450 per m2 / 2,415 litres per m2 over a membrane's life, about
  $0.60 per litre of permeate. The 2,415 is Humbird's own replacement schedule (1,920 membranes a year for 51 million litres of
  perfusate) at his price; it was 3,960 until 2026-11-20. The life spans 900 litres per m2 (fouled in 4.5 days at 8.3 L/m2/h,
  Veje 2024, full) to 5,500 (one TFF fibre for 30 days, Clincke 2013). **Membranes, not hardware, set the cost of filtering a
  thick, fast-fed culture.**
- **Membranes of lost runs** (since the 2026-11-19 audit; ATF, TFF, reused modules and dialysers). A run lost to contamination
  throws its membranes away before they have filtered the litres they were bought for. `explore()` and `retention.sizing` multiply
  the membrane's life by the share of a planned run an average start completes: 85% in the low-lactate example (1% of runs lost a
  day, 33-day runs), 100% in Humbird's optimistic design and the all-favourable example, which lose no runs. So the low-lactate example pays
  $0.70 per litre of permeate, $22.28 per kg of its $49.50. That is three and a half times the $0.20 a litre it pays for medium.
  The ATF filter pays the same membranes as the TFF loop, so its extra cost is its hardware: $17.10 a kilo in the low-lactate
  example. Ceramic elements are cleaned in place and kept, so a lost run does not shorten their life.
- **Inclined settler**: one cell settles at Stokes' speed, slowed by crowding as (1 - fraction)^4.65. The plates are designed for
  half that speed. Plate area = permeate / design speed, at $3.5k per m2 installed (assumed). A settler holds 17 litres of culture
  per m2 (Romann's 2,000 L settler). It is marked not possible when it would hold more than 5% of the tank's culture outside the
  tank (Romann's held 1.5%), because that culture has no oxygen supply. At 154 g/L its oxygen lasts seconds.
- **Acoustic settler**: units = permeate per day / 1,000 litres, at $100k each (assumed; no price found), times 1.84.
- **Disc-stack separator on the outflow**: it takes the permeate plus enough culture to send the cells back as a concentrate at
  70% packed volume (Hundley and Konigsson 2020, part). Feed = permeate x (1 + fraction / (0.70 - fraction)). Each pass bursts
  4% of the cells it carries (2-12.5% measured on CHO by the vendor's staff). The share of grown cells lost is lysis x passes a day
  / (bleed a day + lysis x passes a day). In the low-lactate example the culture passes 2.5 times a day and 18% of the grown cells
  are lost. Units at 2 m3/h each, one spare, $800k each installed (assumed; no sterile price found), 10 kW each, maintenance 4% a
  year.
- **Hydrocyclone**: feed = permeate / 0.5 (half leaves as overflow). It returns 96% of the cells per pass; the rest are lost
  (26% of the grown cells in the low-lactate example). $50k per m3/h of feed (assumed).
- **Cost of a scenario with a device**: `explore()` with the device's capital in place of the default loop's and its running
  cost per kilo grown as `extra_opex`. Then every cost per kg is divided by the share of grown cells that survive the device. The
  TFF loop priced here gives the same capital and membranes as `explore()` (`tests/test_retention.py`).

## 5. Judgements from the two research passes

Each figure below is a rough judgement made while building the model with an AI assistant from the two research passes; not
measured and not reviewed by an expert. The reasoning for each is in the source files named at the top.

| Statement | Probability (the model's rough judgement) |
|---|---|
| ATF or TFF holds 120 g/L at 20 m3 for a month at the reference duty, module swaps allowed | 75% |
| The reference duty is met at $89k per m3 or less and $2 a kg of membranes or less | 45% |
| A filter holds 258 g/L at 20 m3 for a month at a duty like the low-lactate example's, at any cost | 35% |
| The same, at $89k per m3 or less and $3 a kg of membranes or less | 8% |
| An inclined settler holds 120 g/L at 20 m3 for a month | 35% |
| An inclined settler holds 258 g/L at that duty | 5% |
| Any acoustic device meets the low-lactate example's duty | 3% |
| A disc-stack separator on the whole outflow keeps the culture above 90% alive for a month: reference / low-lactate example | 60% / 25% |
| Extra lysis per pass in a hermetic separator is 2% or less for these cells | 30% |
| A sterile hermetic separator runs closed for 33 days without contamination or seal failure | 55% |
| A $89k per m3 device that loses no cells is right for the low-lactate example | 20% |

A dated snapshot: these were judged when the low-lactate example ran at 258 g/L, and not re-judged since. Its tank held 154 g/L
from 2026-11-20 and holds 168 g/L (16% cells by volume) since the second batch of 2026-11-21, so the rows that name 258 g/L
describe a denser culture than the example now runs. Each row names its own density and duty, so it stays a checkable statement.

## 6. What this means for the model

1. **Humbird's optimistic design is safe.** Several devices meet its light duty. With any of them Humbird's optimistic design costs $14.06 to
   $17.53, against $15.93 with the default loop.
2. **The low-lactate example is not.** Its 154 g/L and 39 litres of medium a kilo ask a device to clear 1.32 m3 an hour of
   permeate from a culture that is 15% cells. The real devices shown at that density cost $34.34 (disc stack) to $66.60 (ATF) a
   kilo, against $27.97 with the hoped-for device; their ranges run from $30 to $163. The hoped-for device hides this, because it
   charges only capital, and the real cost is membranes or burst cells. The ATF is the dearest real device in every case, $17.10
   a kilo above the loop in the low-lactate example, since its hardware is priced as Humbird prices bought equipment.
3. **The model's default since 2026-11-15** is a TFF hollow-fibre loop: capital of about $1k per m2 of membrane, times 1.84, plus
   $0.60 per litre of permeate for membranes ($0.70 in the low-lactate example once lost runs are counted). The scenarios, with
   each device:

   | scenario | with the hoped-for device | with TFF (the default) | with a disc stack |
   |---|---|---|---|
   | All-favourable example (its loop uses dialyser-grade fibres) | $7.93 | $7.62 | $8.02 |
   | Low-lactate example | $27.97 | $49.50 | $34.34 |
   | Low-lactate example, food-grade plant with shared medium | $23.51 | $45.04 | $28.89 |
   | Cautious (published cells) | $90.49 | $185.59 | $147.48 |
   | Reference | $14.79 | $15.93 | $15.14 |

   The cautious case filters 136 of its 146 litres a kilo, so membranes alone are $95.71 of its $185.59. Its disc stack would
   lose 38% of the cells.

   A thinner culture does not pay (`retention.density_scan`). Held at 140 g/L in place of the 154 g/L its tank allows, the
   low-lactate example saves $0.5 of membranes, but the plant's capital per kilo rises by $0.9, because each tank makes fewer
   kilos: $50.28 against $49.50; at 100 g/L it is $53.72. At the worst membrane life (900 L/m2) the cost is $86.62 to $87.00
   at any density from 100 to 258 g/L; there the thinnest culture (100 g/L) is the cheapest, by $0.38. Membrane life matters far
   more than density: across its range it moves the low-lactate example from $34.09 to $89.58 with the loop's other inputs. The
   model has no density setpoint switch.
4. **What would lower it.** Cells that need less medium per kg (less ammonia), so less permeate: the "kind of cells" switch also
   decides the retention cost. Membranes that last longer at this density, or cost less (`retention_alternatives.md`). A
   separator that bursts under 1% of the cells per pass: at 1% the low-lactate example costs $29.66. None is shown. Cells that
   grow as aggregates and keep their size for a month: a plain settler would then hold the low-lactate example's culture back for
   $27.80 a kilo (`retention_aggregates.md`).

## 7. What was not found

- Any price for a sterile disc-stack separator, an inclined settler, an acoustic device or a TFF skid at this scale.
- Membrane life at 2-5 L/m2/h and 15-25% cells by volume over a month.
- Cells lost through a filter into the permeate.
- Any non-membrane perfusion of animal cells above 3,000 L or above about 5e7 cells/mL for a month.
- Mayrhofer 2020, Wolf 2019 and the Xu/Chen high-density papers were not read.
- Retention without a membrane by growing the cells in particles (aggregates, edible carriers) was researched on 2026-11-19:
  `retention_aggregates.md`.
