# Holding the cells back in a 20 m3 perfusion tank

> **Note, 2026-11-15 (late).** The figures in this note were computed before three costs were counted: the bubble protectant
> (poloxamer 188), antifoam's quarter cut to the sparger's oxygen transfer, and the oxygen a yeast-style plant buys. Its test checks
> them with those three set back (`tests/_snapshot.py`, `floor_physics.BEFORE_PROTECTANT`). The comparisons hold; the levels are
> higher now. Current scenario costs (RESULTS.md): best case $9.71 (was $8.95), central $29.92 ($26.64), central with shared medium
> $26.81 ($24.34), cautious $43.79 ($38.97), reference $12.51 ($11.84). With antifoam counted, oxygen limits the central and
> cautious tanks, so levers that raise the CO₂ or thickness limits are worth less there than this note says.

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
| Central | 258 g/L | 25% | 77.8 kg/h | 2.18 m3/h (3.3) | 0.30 m3/h | **1.88 m3/h** | 2.8 tank volumes |
| Best case | 258 g/L | 25% | 118 kg/h | 1.32 m3/h (2.0) | 0.46 m3/h | **0.86 m3/h** | 1.3 tank volumes |

Two things follow.

- **The reference duty is light.** The product is the cells, so the bleed carries most of the liquid out. The device only clears
  2.9 litres of permeate per kg.
- **The central duty is twelve times heavier.** The central cells make more ammonia, so each kg needs 28 litres of medium. At 258
  g/L the bleed carries only 3.9 of them. The device must clear 24 litres per kg at a quarter cells by volume.

Viscosity: a culture that is 12% cells is about 1.4 times as viscous as medium. At 25% it is about 2.2 to 2.3 times. Cell
suspensions turn elastic from about 40% (Iordan et al. 2007, part; Thomas's and Krieger's formulas).

## 3. The devices

| Device | Densest culture and largest scale shown | Central: what it takes | Central: capital per m3 of tank | Central: cost per kg (range) | Verdict |
|---|---|---|---|---|---|
| Hoped-for device (the model's default) | nothing: the device is not named | - | $89k | **$18.14** ($17.59-20.45) | Not a real device |
| ATF hollow-fibre filter | 50 days on 50 L at volume fraction 0.13 (Ott 2024, full); 1.3e8 cells/mL for days in 4 L, where its vacuum failed (Clincke 2013, full); units rated to 5,000 L | 35 ATF 10s, 385 m2 | $644k | **$30.43** ($23.17-79.84) | Possible at the edge; costly |
| TFF hollow-fibre loop | 2.14e8 cells/mL (half the volume) for days in 4 L; one fibre lasted 30 days (Clincke 2013, full); nothing published above pilot scale | 375 m2 of membrane | $35k | **$26.64** ($22.25-58.64) | Possible at the edge; membranes set the cost |
| Inclined (lamella) settler | 5e7 cells/mL (Coronel 2020); a 2,000 L tank (Romann 2023) | 785 m2 of plate; 13 m3 of culture outside the tank | $137k | - | **Not possible**: most of the culture would sit without oxygen |
| Acoustic settler | 200-400 L/day tested; 1,000 L/day the largest sold | 46 units | $423k | ($18.66-52.70) | Beyond what is shown; heat limits larger units |
| Disc-stack separator on the outflow | CHO feed at 28% packed volume; yeast recycled 2-3 times a day for 250-280 days (not animal cells) | 2 running + 1 spare; the culture passes 4.4 times a day | $120k | **$25.69** ($21.27-49.12) | Possible; burst cells set the cost |
| Hydrocyclone | 5e7 cells/mL in a 40 L bag (Bettinardi 2020, abstract) | feed 3.8 m3/h | $9k | ($22.30-58.69) | Beyond what is shown; loses a third of the cells |
| Spin filter | about 1e7 cells/mL | - | - | - | Not possible: its screen does not grow with the tank's volume, and it clogs |
| Fluidized-bed centrifuge (kSep) | cell harvests | about 170 cycles an hour | - | - | Not possible: one cycle holds 2.9 kg of cells |

The ranges move each device's own inputs to their favourable and unfavourable ends together (`retention.scenario_range`). Every
other part of the scenario stays as it is.

The same devices in the other two cases:

| Device | Reference ($11.48 now) | Best case ($6.57 now) |
|---|---|---|
| ATF | $12.25 (3 units) | $10.04 (16 units) |
| TFF | $11.84 | $8.95 |
| Settler | $10.82 (23 m2, 0.4 m3 outside the tank) | not possible (29% of the culture outside the tank) |
| Acoustic | $11.07 (4 units) | $6.98, beyond what is shown |
| Disc stack | $11.76 (1.6% of cells lost) | $7.38 (10% lost) |
| Hydrocyclone | $11.08 (2.6% lost) | $7.17, beyond what is shown |

## 4. How each device is costed

- **ATF**: units = permeate / (flux x 11 m2), rounded up. Flux 5 L/m2/h (`rt_flux_lmh`, 2-8.3). Each unit costs $200k (Humbird's
  $38.5M for 192 units; Pasitka implies $350k), times 1.84 to install. Membranes as below.
- **TFF**: membrane area = permeate / flux. Pumps, housings and skids at $1k per m2 (assumed; this gives Pasitka's $35k per m3 at
  the central duty), times 1.84.
- **Membranes** (ATF and TFF): litres of permeate per kg x $1,450 per m2 / 3,960 litres per m2 over a membrane's life, about
  $0.37 per litre of permeate. The life spans 900 litres per m2 (fouled in 4.5 days at 8.3 L/m2/h, Veje 2024, full) to 5,500
  (one TFF fibre for 30 days, Clincke 2013). In the central case this is $8.83 per kg. **Membranes, not hardware, set the cost of
  filtering a thick, fast-fed culture.** Filtering adds about $0.37 per litre of permeate, close to twice the $0.20 a litre the
  central case pays for medium.
- **Inclined settler**: one cell settles at Stokes' speed, slowed by crowding as (1 - fraction)^4.65. The plates are designed for
  half that speed. Plate area = permeate / design speed, at $3.5k per m2 installed (assumed). A settler holds 17 litres of culture
  per m2 (Romann's 2,000 L settler). It is marked not possible when it would hold more than 5% of the tank's culture outside the
  tank (Romann's held 1.5%), because that culture has no oxygen supply. At 258 g/L its oxygen lasts seconds.
- **Acoustic settler**: units = permeate per day / 1,000 litres, at $100k each (assumed; no price found), times 1.84.
- **Disc-stack separator on the outflow**: it takes the permeate plus enough culture to send the cells back as a concentrate at
  70% packed volume (Hundley and Konigsson 2020, part). Feed = permeate x (1 + fraction / (0.70 - fraction)). Each pass bursts
  4% of the cells it carries (2-12.5% measured on CHO by the vendor's staff). The share of grown cells lost is lysis x passes a day
  / (bleed a day + lysis x passes a day). In the central case the culture passes 4.4 times a day and 28% of the grown cells are
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

## 6. What this means for the model

1. **The reference case is safe.** Several devices meet its light duty. With any of them the reference case costs $10.82 to
   $12.25 against $11.48.
2. **The central case is not.** Its 258 g/L and 28 litres of medium a kilo ask a device to clear 1.88 m3 an hour of permeate from
   a culture that is a quarter cells. The devices shown at that density cost $25.69 to $30.43 a kilo in place of $18.14. The
   range is $21 to $80. The hoped-for device hides this, because it charges only capital, and the real cost is membranes or burst
   cells.
3. **Applied as the model's default on 2026-11-15, at Pablo's request:** retention is priced as a TFF hollow-fibre loop: capital of about $1k per m2 of membrane,
   times 1.84, plus $0.37 per litre of permeate for membranes. The scenarios would become:

   | scenario | before | with TFF (now the default) | with a disc stack |
   |---|---|---|---|
   | Best case | $6.57 | $8.95 | $7.38 |
   | Central | $18.14 | $26.64 | $25.69 |
   | Central, food-grade plant with shared medium | $15.84 | $24.34 | $22.50 |
   | Cautious | $32.29 | $38.97 | $37.41 |
   | Reference | $11.48 | $11.84 | $11.76 |

   The scenarios' tank designs are chosen again under the new cost (`scenarios.design` runs on the model's default), and they
   come out the same. A thinner culture does not pay (`retention.density_scan`). Held at 180 g/L in place of 258, the central
   case filters 15% fewer litres a kilo and saves $0.6 of membranes, but the plant's capital per kilo rises by $2.4, because
   each tank makes fewer kilos: $28.75 against $26.64. At the worst membrane life (900 L/m2) the cost is about $56.7 at any
   density from 180 to 258 g/L. Membrane life matters far more than density: it moves the central case by about $30. One
   exception: the cautious case could run all three tank tricks within the loop's checks if it held the culture at 180 g/L,
   which would cost $37.87 against $38.97. The model has no density setpoint switch, so this is not used.
4. **What would lower it.** Cells that need less medium per kg (less ammonia), so less permeate: the "kind of cells" switch now
   also decides the retention cost. Membranes that last longer at this density. A separator that bursts under 1% of the cells per
   pass: at 1% the central case costs $20.32. None is shown.

## 7. What was not found

- Any price for a sterile disc-stack separator, an inclined settler, an acoustic device or a TFF skid at this scale.
- Membrane life at 2-5 L/m2/h and a quarter cells by volume over a month.
- Cells lost through a filter into the permeate.
- Any non-membrane perfusion of animal cells above 3,000 L or above about 5e7 cells/mL for a month.
- Mayrhofer 2020, Wolf 2019 and the Xu/Chen high-density papers were not read.
