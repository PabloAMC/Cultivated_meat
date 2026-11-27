# Tank size: is 20 m³ the right size?

> Repinned 2026-11-27 (the nitrogen and carbon balance: each case's cells are charged the amino acids their ammonia takes and the glucose they ferment; a cleaning route's dialysate is floored at the case's own nutrients). The reference and the all-favourable example rise by about $0.05 at every size (reference at 20 m³ $15.72 -> $15.77, all-favourable at its own 42 m³ $6.97 -> $7.02, at 20 m³ $7.16 -> $7.22, its cheapest $6.94 -> $6.99); in fed-batch at 20 m³ the low-lactate example $69.90 -> $70.02 and the all-favourable $10.93 -> $10.97. The other scenarios' perfusion rows do not move. The conclusions are unchanged.

> **Updated 2026-11-25.** The model now chooses the gas flow up to the cap the cells tolerate, and holds a culture thinner
> by itself when its column loop fails its checks. The rows of section 1 and the fed-batch table of section 10 are recomputed.
> Two scenarios now bubble less gas and lose fewer cells: shared medium $44.53 -> $43.92 at 20 m³, cautious $181.13 -> $179.90.
> The low-lactate and all-favourable examples do not move. Three findings change. (1) The cautious 20 m³ design, held as it
> runs (109 g/L, 1 mm/s of gas), now passes its checks up to 27.8 m³; the low-lactate examples' designs still stop at 20.0 m³.
> (2) At 100 m³ a flatter tank (liquid 0.4 or 0.5 as deep as wide) now costs less than the 20 m³ price ($47.98 and $47.58
> against $48.68): flat tanks were dear because they bubbled the full cap. (3) The cells that make almost no ammonia or
> lactate are now cheaper in fed-batch at 100 m³ too ($24.94 against $25.26). The cautious case saves 3.4% at 200 m³ (was 3.7%).

> **Updated 2026-11-21.** Section 1's table and section 10's fed-batch table are recomputed; the other sections are the
> 2026-11-20 snapshot below. Three engine changes reach this note. (1) The tank design is chosen as `scenarios.design` now chooses
> it: a column loop that fails its checks at full density is run with the culture held thinner, at the densest density it passes.
> Every scenario's 20 m³ design is the recycled-oxygen column held thinner (low-lactate 168 g/L, cautious 134 g/L); at that
> density it sits exactly at the edge of its checks, so `design_limit` is 20.0 m³ (with the pH check relaxed to twice the safe
> dose: 42 m³ for the low-lactate examples, 107 m³ for the cautious case). (2) The building's power follows its floor and its
> class, so small tanks pay more for it and large ones less. (3) Part of the crew is counted per tank, as Humbird counts it.
> **Changed conclusions:** the low-lactate examples and the cautious case are now cheapest at the 200 m³ end of the range (3.7%
> to 6.8% below 20 m³), with a thinner culture in a larger tank; the all-favourable example is cheapest at 44 m³, next to its own
> 42 m³ (3.1% below its 20 m³ row); fed-batch with shared medium at 100 m³ or more costs less than perfusion at 20 m³
> ($43.62 at 100 m³ against $44.53), but not than perfusion at the same size ($41.97 at 100 m³); only the cells that make almost
> no ammonia or lactate, at 200 m³, are cheaper in fed-batch, by $0.31 ($24.63 against $24.94).
>
> **Updated 2026-11-20 (final pass).** Every table recomputed on the model as it now stands: per-tank plant items
> (`floor_physics.tank_items`, `capex_at_size`: the tank, its makeup tanks and filter housings and the buildings are charged per
> tank as well as per m³), thick cultures take up oxygen more slowly (`viscous_kla`), twice the fed-batch crew in perfusion,
> membrane life 2,415 L/m², cells killed by bursting bubbles, a 2% harvest loss, and the all-favourable example redefined
> (`scenarios.all_favourable()`, $7.62 at its own 42 m³ tank, membranes at $8 a m², no lost runs). **Changed conclusions:**
> (1) every scenario now saves 5.3% to 7.4% in a larger tank, and 20 m³ is outside the sizes within 3% of the cheapest for all
> four (on 2026-11-19 the saving was 0.5% to 2.1%; earlier on 2026-11-20 it was up to 5.1% for three of the four); the cause is
> the per-tank plant items. (2) The all-favourable example's cheapest tank keeps the column and 1 bar of pressure and its density
> (156 g/L at 90 m³); it was a thin culture with no added equipment for oxygen and CO₂ while membranes cost $1,450 a m². (3) Fed-batch costs more than
> perfusion at every size again (section 10). (4) A flatter tank no longer helps at any size (section 5). (5) The probabilities
> of section 7 are restated as ranges and the column that rested on the old designs is deleted.

Research date: 2026-11-15; updated 2026-11-20. Code: `tank_size.py` (`size_scan`, `summary`, `what_ifs`, `flatter`,
`fedbatch_markdown`), `tests/test_tank_size.py`. Run `python tank_size.py` for every table below. Costs are 2025 dollars per kg
of wet cells harvested. The scenarios use a stirred tank in perfusion with a TFF filter loop, 20 m³ except the all-favourable
example, which chooses its size among the published ones (42 m³). The scan runs each scenario's switches at each size through
`floor_physics.explore(vessel_m3=...)` and adds no physics.

## 1. The answer

**For cost, 20 m³ is not at the bottom of the curve (changed 2026-11-20).** Every scenario saves 5.3% to 7.4% in a larger tank
($0.60 to $9.88 a kilo), at 90 to 168 m³. The sizes within 3% of the cheapest run from 32 to 63 m³ up to 200 m³, so 20 m³ is
outside them for all four. On 2026-11-19 the saving was 0.5% to 2.1% and no scenario gained more than 3%. **For risk the answer
is unchanged: no animal cells have run above about 25 m³, and no animal-cell perfusion above about 4 m³ (section 7).**

| Scenario | Cost at 20 m³ | Cheapest size the model finds | Cost there | Saving | Sizes within 1% of the minimum |
|---|---|---|---|---|---|
| All-favourable example (its own tank is 42 m³, $7.02) | $7.22 | 44 m³ | $6.99 | $0.22 (3.1%) | 39 to 69 m³ |
| Low-lactate example | $48.68 | 200 m³ (the end of the range) | $45.53 | $3.15 (6.5%) | 90 to 200 m³ |
| Low-lactate example, food-grade plant with shared medium | $43.92 | 200 m³ (the end of the range) | $41.19 | $2.73 (6.2%) | 111 to 200 m³ |
| Cautious | $179.90 | 200 m³ (the end of the range) | $173.87 | $6.03 (3.4%) | 60 to 200 m³ |
| Reference (Humbird's tank, no added equipment for oxygen and CO₂) | $15.77 | 47 m³ | $14.98 | $0.79 (5.0%) | 37 to 50 m³ |
| Reference, tank design chosen again | $14.56 | 200 m³ (the end of the range) | $13.10 | $1.46 (10.0%) | 114 to 200 m³ |

- **Why larger tanks now save more.** Since 2026-11-20 the plant's capital per m³ of tank follows Humbird's own accounting item
  by item (`floor_physics.tank_items`): each tank brings its own installed vessel (his Eq. 3.1, $30.7k per m³ + $800k a tank),
  two makeup tanks and filter housings ($167k a tank in perfusion, bare), and buildings ($74.4k per m³ + $533k a tank, a fit to
  his two plants), all with his installation and indirect factors. Before, only the bioreactor share of the plant (32%) changed
  with size. The tank items cost $388k per m³ of tank at 20 m³, $226k at 200 m³ and $2,014k at 2 m³ (2018 dollars). The cautious
  scenario's capital falls from $23.37 a kilo at 20 m³ to $17.49 at 168 m³; the low-lactate example's from $11.29 to $10.10.
- **The low-lactate examples and the cautious one sit at 168 m³ for a stated reason.** 168 m³ is the largest size at which the
  low-lactate examples' cheapest design (the column alone, tall tank, 124 g/L) passes the pH check. Above it the cheapest passing
  design is a square tank at 118 g/L and the cost steps up by $1.59 a kilo. Their thinner culture at large sizes also needs less
  membrane per kilo ($20.18 against $22.28 at 20 m³).
- **The all-favourable example's cheapest tank keeps its added equipment for oxygen and CO₂.** Its membranes cost $0.04 a kilo at every size (it uses
  membranes at $8 a m²), so a thin culture saves nothing and the cheapest design at 90 m³ is the column + 1 bar in a squat tank at
  156 g/L, the 20 m³ density. The saving is all capital ($2.06 a kilo against $2.52). Against its own 42 m³ tank the saving is
  $0.12 (1.6%).
- **Smaller tanks cost much more, and the penalty grows fast below 10 m³.** At 10 m³ a kilo costs 4% to 8% more than at 20 m³
  (all-favourable $8.52, low-lactate $53.50, cautious $193.33). At 5 m³ it costs 12% to 23% more. At 2 m³ it costs 31% to 64% more.
  Before the per-tank items the figures were 3% to 7%, 8% to 12% and 22% to 35%.
- **The loop checks stop the densest designs.** Without them every scenario's cheapest size is 200 m³, the end of the range: the
  all-favourable example at 320 g/L (8.9% below 20 m³ without checks), the low-lactate example at 231 g/L (6.6%). The scenarios'
  own 20 m³ designs pass the checks up to 32 to 169 m³ (section 6).
- **Labour is the assumption that would move the answer most.** The model charges the same crew per m³ at every size. If staff
  per m³ fell with tank size as they do between Humbird's 2 m³ and 20 m³ plants, the saving would be 18.2% for the all-favourable
  example (at 200 m³), 12.0% for the low-lactate example (168 m³) and 7.5% for the cautious one (168 m³). Section 5 says why that
  is an upper bound.
- **A chance of losing a run that grows with size removes most of the gain** for the scenarios that lose runs: the low-lactate
  example's cheapest size falls to 32 m³ (1.6%), the cautious one's to 25 m³ (0.1%). The all-favourable example loses no runs, so
  this what-if does not change it.

## 2. How the scan works

For each case and size, the scan tries every pair of added equipment for oxygen and CO₂ (none; column; column and 1 bar extra pressure; column, pressure
and recycled oxygen) and tank shape (liquid 1.6, 1.0, 0.75 or 0.5 times as deep as wide). That is 16 designs, as
`scenarios.design` tries. It keeps the cheapest design whose column loop
- is pH-safe: its alkaline dose is at most 1.0 times that of the design judged safe (55 mbar out, 0.5 m³ of loop in a 20 m³ tank), and
- runs at a pass rate dense cultures have taken: at most `ge_passes_tested` (15) tank volumes an hour.

At 20 m³ the scan returns each scenario's own design, and its cost for the scenarios whose own tank is 20 m³; for the
all-favourable example the same design at its own 42 m³ gives the scenario's $7.62 (the test checks both). Everything else about
the scenario is held fixed. Humbird's optimistic design is shown twice: as defined (Humbird's tall tank, no added equipment for oxygen and CO₂) and with the design
chosen again.

Two things set what a design costs at a size. The plant's capital per m³ of tank falls with size through the per-tank items
(section 1; `capex_at_size`); seed trains, fill tanks, sterilisers, centrifuges and the utilities outside the process stay at
their cost per m³. And a deeper tank clears less CO₂ and mixes more slowly, so each trick has a size above which it no longer
lifts the limit.

## 3. Cost against size, and what binds

"Capital" is the tank, plant and column. "Loop" is the retention loop's hardware. "Medium" is feed plus growth factors. "Other" is
utilities, other consumables and bought oxygen. "Density limit" is the cap that sets the culture's density. "Loop checks cost" is
what the pH or pass check adds against the cheapest design that fails it. The all-favourable example's 20 m³ row is its switches
at 20 m³; its own tank is 42 m³.

#### The all-favourable example

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **13.30** | 7.42 | 0.04 | 1.46 | 0.04 | 2.30 | 2.04 | 150 | oxygen supply | $3.88 (pH) |
| 5 | column + 1 bar, tall 1.6 | **9.59** | 3.93 | 0.04 | 1.40 | 0.04 | 2.22 | 1.97 | 152 | oxygen supply | $2.24 (pH) |
| 10 | column + 1 bar, tall 1.6 | **8.52** | 2.98 | 0.04 | 1.35 | 0.04 | 2.18 | 1.93 | 154 | oxygen supply | $1.77 (pH) |
| 20 | column + 1 bar, square 1.0 | **8.10** | 2.52 | 0.04 | 1.37 | 0.04 | 2.19 | 1.94 | 153 | oxygen supply | $1.70 (pH) |
| 50 | column + 1 bar, square 1.0 | **7.54** | 2.09 | 0.04 | 1.32 | 0.04 | 2.15 | 1.90 | 156 | oxygen supply | $1.47 (pH) |
| 100 | column + 1 bar, flat 0.5 | **7.77** | 2.23 | 0.04 | 1.36 | 0.04 | 2.18 | 1.93 | 154 | oxygen supply | $1.85 (pH) |
| 200 | column + 1 bar, flat 0.5 | **7.56** | 2.11 | 0.04 | 1.32 | 0.04 | 2.15 | 1.90 | 156 | oxygen supply | $1.73 (pH) |

#### The low-lactate example

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **80.89** | 38.47 | 0.31 | 4.07 | 24.54 | 8.82 | 4.68 | 148 | oxygen supply | $13.46 (pH) |
| 5 | column + 1 bar, tall 1.6 | **60.76** | 20.53 | 0.29 | 3.81 | 23.33 | 8.36 | 4.43 | 150 | oxygen supply | $6.90 (pH) |
| 10 | column + 1 bar, tall 1.6 | **53.50** | 14.42 | 0.29 | 3.65 | 22.72 | 8.12 | 4.30 | 151 | oxygen supply | $4.50 (pH) |
| 20 | column + 1 bar, tall 1.6 | **49.50** | 11.29 | 0.28 | 3.52 | 22.28 | 7.94 | 4.20 | 154 | oxygen supply | $3.21 (pH) |
| 50 | column + 1 bar, square 1.0 | **48.34** | 10.10 | 0.28 | 3.52 | 22.29 | 7.94 | 4.20 | 154 | oxygen supply | $4.03 (pH) |
| 100 | column, tall 1.6 | **47.27** | 10.72 | 0.25 | 4.33 | 20.15 | 7.66 | 4.15 | 120 | oxygen supply | $3.85 (pH) |
| 200 | column, square 1.0 | **47.75** | 11.07 | 0.25 | 4.41 | 20.15 | 7.69 | 4.18 | 119 | oxygen supply | $4.53 (pH) |

#### The low-lactate example, food-grade plant with shared medium

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **63.69** | 20.87 | 0.31 | 4.07 | 24.54 | 8.82 | 5.08 | 148 | oxygen supply | $6.27 (pH) |
| 5 | column + 1 bar, tall 1.6 | **52.18** | 11.57 | 0.29 | 3.81 | 23.33 | 8.36 | 4.81 | 150 | oxygen supply | $3.44 (pH) |
| 10 | column + 1 bar, tall 1.6 | **47.67** | 8.22 | 0.29 | 3.65 | 22.72 | 8.12 | 4.67 | 151 | oxygen supply | $2.23 (pH) |
| 20 | column + 1 bar, tall 1.6 | **45.04** | 6.46 | 0.28 | 3.52 | 22.28 | 7.94 | 4.56 | 154 | oxygen supply | $1.53 (pH) |
| 50 | column, tall 1.6 | **44.13** | 6.81 | 0.25 | 4.55 | 20.17 | 7.76 | 4.58 | 116 | oxygen supply | $2.14 (pH) |
| 100 | column, tall 1.6 | **43.04** | 6.14 | 0.25 | 4.33 | 20.15 | 7.66 | 4.51 | 120 | oxygen supply | $1.78 (pH) |
| 200 | column, square 1.0 | **43.36** | 6.33 | 0.25 | 4.41 | 20.15 | 7.69 | 4.53 | 119 | oxygen supply | $2.42 (pH) |

#### Cautious

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **242.64** | 70.45 | 1.35 | 7.14 | 101.27 | 47.80 | 14.63 | 99 | oxygen supply | $38.40 (pH) |
| 5 | column + 1 bar, tall 1.6 | **207.04** | 39.90 | 1.31 | 6.84 | 98.40 | 46.40 | 14.20 | 100 | oxygen supply | $20.96 (pH) |
| 10 | column + 1 bar, tall 1.6 | **193.33** | 28.97 | 1.29 | 6.64 | 96.86 | 45.62 | 13.95 | 101 | oxygen supply | $14.41 (pH) |
| 20 | column + 1 bar, tall 1.6 | **185.59** | 23.37 | 1.28 | 6.45 | 95.71 | 45.03 | 13.76 | 103 | oxygen supply | $11.06 (pH) |
| 50 | column + 1 bar, tall 1.6 | **179.84** | 19.73 | 1.26 | 6.20 | 94.65 | 44.44 | 13.56 | 105 | oxygen supply | $8.84 (pH) |
| 100 | column + 1 bar, tall 1.6 | **177.19** | 18.26 | 1.26 | 6.00 | 94.12 | 44.11 | 13.45 | 108 | oxygen supply | $7.90 (pH) |
| 200 | column + 1 bar, square 1.0 | **178.01** | 18.69 | 1.26 | 6.07 | 94.29 | 44.22 | 13.49 | 107 | oxygen supply | $9.71 (pH) |

#### Reference, tank design chosen again

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **29.39** | 18.98 | 0.05 | 2.05 | 3.96 | 2.47 | 1.88 | 172 | oxygen supply | $4.60 (pH) |
| 5 | column + 1 bar, tall 1.6 | **19.63** | 9.76 | 0.05 | 1.94 | 3.75 | 2.34 | 1.78 | 172 | oxygen supply | $1.96 (pH) |
| 10 | column + 1 bar, tall 1.6 | **16.61** | 7.03 | 0.05 | 1.88 | 3.64 | 2.27 | 1.73 | 172 | oxygen supply | $1.33 (pH) |
| 20 | column + 1 bar, tall 1.6 | **14.89** | 5.52 | 0.05 | 1.84 | 3.56 | 2.22 | 1.70 | 172 | oxygen supply | $0.87 (pH) |
| 50 | column + 1 bar, square 1.0 | **14.28** | 4.90 | 0.05 | 1.84 | 3.56 | 2.22 | 1.70 | 172 | oxygen supply | $1.00 (pH) |
| 100 | column, tall 1.6 | **14.00** | 5.72 | 0.02 | 2.53 | 1.86 | 2.14 | 1.72 | 121 | oxygen supply | $0.88 (pH) |
| 200 | column, tall 1.6 | **13.81** | 5.80 | 0.02 | 2.67 | 1.48 | 2.12 | 1.72 | 113 | mixing | $0.90 (pH) |

#### Reference as defined (Humbird's tall tank, no added equipment for oxygen and CO₂)

| m³ | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 36.19 | 26.66 | 0.03 | 2.91 | 2.15 | 2.47 | 1.98 | 121 | oxygen supply |
| 5 | 22.60 | 13.57 | 0.03 | 2.76 | 2.03 | 2.34 | 1.87 | 121 | oxygen supply |
| 10 | 18.16 | 9.39 | 0.03 | 2.68 | 1.97 | 2.27 | 1.82 | 121 | oxygen supply |
| 20 | 15.93 | 7.38 | 0.03 | 2.64 | 1.88 | 2.22 | 1.78 | 120 | CO₂ removal |
| 50 | 15.57 | 8.04 | 0.00 | 3.50 | 0.00 | 2.17 | 1.85 | 88 | CO₂ removal |
| 100 | 18.23 | 9.39 | 0.00 | 4.36 | 0.00 | 2.29 | 2.20 | 70 | CO₂ removal |
| 200 | 22.25 | 11.32 | 0.00 | 5.43 | 0.00 | 2.85 | 2.64 | 56 | CO₂ removal |

### What binds at each size

- **2 to 10 m³: capital.** A small tank costs much more per m³: each tank brings its own makeup tanks, filter housings and
  building share. Capital per kilo falls from $7.42 at 2 m³ to $2.98 at 10 m³ in the all-favourable example, and from $38.47 to
  $14.42 in the low-lactate example. Oxygen supply sets the density in every scenario design: 150 to 156 g/L (all-favourable),
  148 to 154 g/L (low-lactate, up to 50 m³) and 99 to 108 g/L (cautious). The pH check costs $3.88 a kilo at 2 m³ in the
  all-favourable example and $13.46 in the low-lactate example: a cheaper design fails it.
- **20 m³: the pH check.** The check costs $1.70 (all-favourable), $3.21 (low-lactate), $1.53 (shared medium) and $11.06
  (cautious) a kilo: the cheaper design with recycled oxygen as well fails the pH check.
- **50 m³ and above: the pH check, then a thinner culture.** A deeper tank clears less CO₂ through the sparger, so the loop must
  make more passes, and the alkaline dose rises with the passes. The low-lactate example keeps column + 1 bar to 50 m³ (square),
  then drops the pressure and keeps the column alone at 100 and 200 m³, where the density falls to 119 to 120 g/L. The
  all-favourable and cautious examples keep column + 1 bar at every size and hold their density (153 to 156 g/L and 103 to 108 g/L).
- **Mixing binds in one chosen design**: the reference with its design chosen again, at 200 m³. In the reference as defined (tall
  tank, no added equipment for oxygen and CO₂), oxygen supply binds at 2 to 10 m³ and CO₂ removal from 20 m³ up, and the culture thins from 121 g/L to 56 g/L.
  That is why the reference's own cost curve turns up above 47 m³.
- **Heat is not modelled.** At 20 m³ the cells give off 3.8 kW per m³ of culture (all-favourable, 153 g/L), 2.8 kW/m³
  (low-lactate, 154 g/L) and 1.8 kW/m³ (cautious, 103 g/L). The wall of a 20 m³ tank has about 2.9 m² per m³ of culture; at 200
  m³ it has 1.3 (square, low-lactate and cautious) to 1.4 (flat, all-favourable) m² per m³. A jacket alone must take 0.6 to 1.4
  kW/m² at 20 m³ and 1.4 to 2.8 kW/m² at 200 m³. What a jacket removes, 1 to 5 kW/m², is a rough judgement made while building the model with an
  AI assistant; not measured and not reviewed by an expert. If it is near the low end, an external heat exchanger on the column
  loop would take the rest; its cost is not in the model.

## 4. The retention loop and size

The TFF loop is sized on permeate per m³ of tank (`floor_physics.explore`, `retention.py`): permeate per kilo is the medium per
kilo less what the bleed of cells carries out (1000 / density); membrane area per m³ is that permeate times the harvest rate per
m³, divided by the flux (5 L/m²/h); hardware is $1k per m² times 1.84 for installation; membranes cost $1,450 per m² and last
2,415 litres per m² (the all-favourable example uses $8 a m² and 1,000 litres). A lost run throws its membranes away early: the
life is multiplied by the share of a planned run an average start completes. That share does not depend on tank size unless the
chance of losing a run does.

**What this does at each size.** For the same density and medium the area per m³ of tank is the same at every size (the test
checks it on the reference at 2 and 10 m³), and the loop's capital and its membranes move in one proportion. A deeper tank kills
fewer cells with bubbles, so the cost per kilo harvested falls a little with depth. The loop is not what decides the size.

| | All-favourable example, 20 m³ | All-favourable example, 200 m³ | Low-lactate example, 20 m³ | Low-lactate example, 200 m³ |
|---|---|---|---|---|
| Membrane area | 91 m² | 949 m² | 264 m² | 1,904 m² |
| ATF-10 equivalents (11 m² each) | 8 | 86 | 24 | 173 |
| Loop hardware, $/kg | 0.04 | 0.04 | 0.28 | 0.25 |
| Membranes, $/kg | 0.04 | 0.04 | 22.28 | 20.15 |
| Membranes, share of the cost | 0.5% | 0.5% | 45% | 42% |

**Assumptions in the sizing that favour or penalise a size:**
1. *Hardware per m² does not fall with size.* A big skid costs less per m² than a small one. That penalises large tanks. The
   what-if (`ts_loop_hw_exp` = 0.3, hardware as V^0.7) changes the all-favourable example's saving from 7.4% to 7.6% and the
   low-lactate example's from 6.2% to 6.5%. The hardware is under 1% of the cost, so this barely matters.
2. *Membranes cost the same per litre at every size.* They are 42% to 53% of the cost in the low-lactate and cautious scenarios,
   and they set the loop's cost there. They fall at large sizes only because the thinner culture needs less permeate per kilo
   ($22.28 to $20.15 in the low-lactate example). The price per m² would fall with a bigger order, but that has nothing to do
   with tank size.
3. *Flux is 5 L/m²/h whatever the density.* A thinner culture at large size would hold a higher flux. That favours large tanks
   slightly, through hardware only, so the effect is under $0.05 a kilo.
4. *No unit rounding.* A 2 m³ tank needs 1 to 6 ATF-10 units' worth of membrane; the model charges the fraction. That flatters
   the smallest tanks by a few cents.
5. *Not charged at any size:* pumping power for the loop, labour and downtime to change membranes (173 ATF-10 equivalents at
   200 m³ in the low-lactate example, 622 in the cautious one), sterile connections, and the time culture spends in the loop
   outside the tank. The column loop has a pH and a pass check; the TFF loop pumps the whole culture through fibres and has none.
   All of these grow with area, so they would penalise large tanks, but nothing in the repo prices them.
6. *In Humbird's optimistic design as defined, the model charges no loop at 50 m³ and above.* The bleed at 88, 70 and 56 g/L carries out
   at least the medium the cells need, so permeate is zero. Since 2026-11-16 `explore` buys at least the liquid the bleed removes
   (the test checks it in every case).

## 5. Other assumptions that favour or penalise a size

The plant model scales the tank, its makeup tanks and filter housings and the buildings with size (`tank_items`). The rest (seed
trains, fill tanks, sterilisers, centrifuges, utilities outside the process) is priced per m³ at its 20 m³ value.

| Assumption | Effect | Direction |
|---|---|---|
| Labour: the same crew per m³ at every size | Humbird's two plants (95 staff for 24 × 20 m³, 132 for 96 × 2 m³) give crew per m³ ∝ (tank size)^-0.54. Extrapolated to 200 m³ it cuts labour by 71%. | Penalises large tanks, rewards small tanks. The exponent comes from two sizes at or below 20 m³; above 20 m³ it is an extrapolation. |
| Buildings: $74.4k per m³ + $533k per tank (direct cost) | A fit to Humbird's two plants, both at or below 20 m³ tanks. Above 20 m³ it is an extrapolation. | Rewards large tanks through the per-tank part. |
| The chance of losing a run per tank-day is the same at every size | A bigger tank has more ports and seals and loses a whole tankful. BioPlan's survey found larger facilities had about 3 times the contamination of smaller ones (facilities, not tanks). | Flatters large tanks. |
| Seed train and restart time are the same at every size | A 200 m³ tank needs about 3 more doublings of seed than a 20 m³ tank. | Flatters large tanks. |
| Shape: a squat tank mixes faster, by Humbird's Eq. 2.18 (t_m ∝ T^(2/3) (H/T)^2.5) | Used below its fitted range (H/T from 1.6). Wide flat tanks (7 m across at 200 m³) need several impellers. | Flatters large flat tanks. |
| Gas speed through the surface is fixed (the model's rule) | `gas_exchange_study.md` section 2.3 reads the bubble-damage evidence as gas per litre, not per surface: then a deeper tank can pass faster gas (up to 13 mm/s at 200 m³, a speed whose foam nobody has measured). | Penalises large tanks. |

The what-ifs below change one at a time and report the cheapest size and the saving against 20 m³ under the same rule. Each is
zero at 20 m³ by construction (the test checks it).

| What-if | All-favourable example | Low-lactate example | Low-lactate example, shared medium | Cautious | Reference, redesigned |
|---|---|---|---|---|---|
| As modelled | 90 m³, 7.4% | 168 m³, 6.2% | 168 m³, 5.8% | 168 m³, 5.3% | 96 m³, 7.5% |
| No loop checks (physics only) | 200 m³, 8.9% | 200 m³, 6.6% | 200 m³, 5.9% | 200 m³, 3.6% | 200 m³, 7.9% |
| pH check relaxed to twice the safe dose | 136 m³, 5.5% | 163 m³, 7.0% | 200 m³, 6.2% | 200 m³, 5.6% | 173 m³, 9.5% |
| Pass limit at the top of its range (24 an hour) | 90 m³, 7.4% | 168 m³, 6.2% | 168 m³, 5.8% | 168 m³, 5.3% | 96 m³, 7.5% |
| Labour follows Humbird's crew rule | 200 m³, 18.2% | 168 m³, 12.0% | 200 m³, 12.6% | 168 m³, 7.5% | 200 m³, 20.0% |
| Loop hardware has economies of scale | 90 m³, 7.6% | 168 m³, 6.5% | 168 m³, 6.0% | 168 m³, 5.6% | 96 m³, 7.6% |
| Chance of losing a run grows with size (V^0.33) | 90 m³, 7.4% | 32 m³, 1.6% | 32 m³, 0.8% | 25 m³, 0.1% | 96 m³, 7.5% |
| Gas per litre held at its 20 m³ value | 200 m³, 15.7% | 173 m³, 5.9% | 173 m³, 3.7% | 173 m³, 4.2% | 128 m³, 9.4% |
| Favourable to large tanks (pH check relaxed, crew rule, loop economies) | 136 m³, 16.4% | 200 m³, 12.9% | 200 m³, 12.9% | 200 m³, 8.1% | 200 m³, 20.1% |

- **The pass limit never binds first.** The pH check fails before the pass count reaches 15.
- **Removing a check can lower the per-cent saving**, because it lowers the 20 m³ cost as well (cautious: 3.6% without checks
  against 5.3% with them; all-favourable with the pH check relaxed: 5.5% against 7.4%). The costs reached are lower in both.
- **The crew rule is the largest single effect, and the least supported above 20 m³.** It would put the all-favourable example at
  200 m³ and 18.2% cheaper. It does not move the low-lactate example's size: 168 m³ is where its design changes (section 1), and
  the rule only deepens the saving there. No source gives crew against tank size above 20 m³.
- **A chance of loss that grows with size removes the large-tank gain for the scenarios that lose runs.** At V^0.33 the
  low-lactate example's optimum drops to 32 m³ and 1.6%, with shared medium 32 m³ and 0.8%, the cautious one 25 m³ and 0.1%. The
  all-favourable example and the reference lose no runs in the model, so their rows do not move.
- **Gas per litre moves the all-favourable example most** (15.7% at 200 m³): a deeper tank could pass faster gas and hold a
  denser culture.
- **A flatter tank than the scenarios offer does not help at any size (changed 2026-11-20).** A shallow tank passes more gas per
  litre of culture at the same surface speed, so it loses more cells to bursting bubbles: at 20 m³ the low-lactate example's flat
  0.5 tank kills 17% of its cells against 8% in the tall tank, and costs $56.96 against $49.50. At 100 m³ a tank with the liquid
  0.4 times as deep as wide (6.3 m across, 2.5 m deep) passes the check with column + 1 bar for $51.39, and 0.5 for $49.97; the
  scan's own choice there (column alone, tall) costs $47.27 (`tank_size.flatter`). Before 2026-11-20 the 0.4 tank cost about the
  20 m³ price. The scenarios do not offer these shapes, and nobody has built a tank this wide for cells.

## 6. The largest size at which each design passes

| Scenario | The 20 m³ design | Its limit with the model's checks | Limit with the pH check at twice the safe dose | Largest size that keeps the 20 m³ density, with the design chosen again |
|---|---|---|---|---|
| All-favourable example | column + 1 bar, square | 51.1 m³ | 77.3 m³ | 200 m³ (the end of the range) |
| Low-lactate example | column + 1 bar, tall | 32.1 m³ | 65.4 m³ | 32.1 m³ |
| Low-lactate example, food-grade plant with shared medium | column + 1 bar, tall | 32.1 m³ | 65.4 m³ | 32.1 m³ |
| Cautious | column + 1 bar, tall | 168.8 m³ | 793.4 m³ | 200 m³ (the end of the range) |

- **The limits rose on 2026-11-20** (they were 24 to 63 m³). A design fails when its pH dose passes 1.0 times the safe dose. At
  20 m³ the dose is 0.36 (all-favourable), 0.82 (low-lactate) and 0.64 (cautious) of the safe dose. Thick cultures now take up
  oxygen more slowly (`viscous_kla`), so the cultures are thinner (low-lactate 154 g/L, was 191; cautious 103 g/L, was 120) and
  the column has less CO₂ to strip. With `viscous_kla=False` the same 20 m³ designs would hold 196 and 120 g/L at 1.35 and 0.84 of
  the safe dose. The all-favourable example's 20 m³ design passes to 51.1 m³, above its own 42 m³ tank.
- **A re-chosen design holds the 20 m³ density to 200 m³ for the all-favourable and cautious examples.** The low-lactate
  examples hold 154 g/L to 32.1 m³ (and about 154 g/L in a square tank at 50 m³ for the low-lactate example), then drop to 116
  to 120 g/L.
- **The check is a judgement, not a physical limit.** The safe dose is 0.29 of the dose that slowed CHO cells (Paul et al. 2020,
  via a summary in `gas_exchange_study.md` section 8): one study, and a measure (rise × share) the study did not use. At 3.4
  times the safe dose the loop would reach that harm. Between 1.0 and 3.4 nothing is measured.

## 7. How likely is each size?

Every probability in this section is a rough judgement made while building the model with an AI assistant; not measured and not
reviewed by an expert. The model does not use them. The reasoning is given beside each.

**Sources of evidence.** Animal cells have run in a stirred tank at 25 m³ (pharma fed-batch, `Continuous harvest bioreactor
progress/biopharma_continuous_culture.md`), at 21 m³ (insect cells, `floor_physics.SPECIES_PRESETS`, Ashizawa 2022) and at 20 m³
for food (Vow; `Continuous harvest bioreactor progress/cultivated_meat_reactor_progress.md`). Perfusion with a retention device
has run at 4 m³ (Genzyme Geel). Vendor ratings stop at 5 m³. Nobody has run animal-cell perfusion above about 4 m³. For meat
cells, no perfusion above 10 L is reported, and besides Vow no vessel above 2 m³. Microbial tanks of 150 m³ and more exist
(Quorn's 155 m³ airlift runs continuously), so the steel is not the problem.

Two events, for a tank of each size. "Possible" means: with funding and a development programme of up to ten years, nothing in
the model's physics or the evidence stops it.

- **H**: the tank is built and run with animal cells for a production run of at least two weeks (any mode, any density).
- **R**: the tank is run in perfusion with a retention device for at least four weeks at 100 g/L or more.

| Size | H, possible | R, possible | R, shown by end of 2035 |
|---|---|---|---|
| 2 m³ | 95% to 100% | 90% to 100% | already shown |
| 5 m³ | 95% to 100% | 85% to 97% | already shown (4 m³) |
| 10 m³ | 95% to 99% | 75% to 90% | 15% to 35% |
| 20 m³ | 90% to 99% | 60% to 85% | 5% to 20% |
| 50 m³ | 75% to 95% | 40% to 70% | 2% to 8% |
| 100 m³ | 60% to 90% | 30% to 55% | 1% to 5% |
| 200 m³ | 45% to 75% | 20% to 40% | 0% to 3% |

How each column is built:
- **H.** Nothing in the physics stops a stirred tank above 25 m³. Large pharma tanks stop at 25 m³ for batch-size reasons, and
  the one report at 25 m³ found lower viability traced to CO₂ stripping. The range falls with the size of the step beyond 25 m³
  (shear, mixing time, pH and dissolved-gas zones). The largest vessels in use or planned for meat cells are 20 to 22 m³ (Vow,
  Meatly, Orbillion), and the 100,000 L and 250,000 L plans (UPSIDE Glenview, GOOD Meat, BlueNalu) were paused, abandoned or not
  started.
- **R.** The anchor is `retention_devices.md`: a filter holding 120 g/L at 20 m³ for a month. Above 20 m³ the range falls with
  each doubling of size, because the membrane area (and the number of parallel units, up to 173 in the low-lactate example at 200
  m³) grows with the tank, and a failure in one unit has more units to occur in. Below 20 m³ it rises toward the 2 m³ perfusion
  tanks that are standard in pharma.
- **The scenario's own design at each size.** An earlier column multiplied R by factors for density and for the added equipment, judged
  for designs the model no longer chooses (258 g/L); it is deleted. For a scenario's design to work at a size, R must hold at the
  design's density (153 to 156 g/L for the all-favourable example, 119 to 154 g/L for the low-lactate example, 103 to 108 g/L for
  the cautious one), and the column and 1 bar of pressure must work at that size for four weeks. Neither has been shown at any
  size in perfusion.

**What this says about size.** A larger tank saves 5.3% to 7.4% at 90 to 168 m³, sizes at which no animal-cell perfusion has run.
At 10 m³, where perfusion is closer to what has been shown, a kilo costs 4% to 8% more than at 20 m³.

## 8. What would change the answer

1. **A measured pH limit for the column loop.** The largest size depends on one check set at 0.29 of the dose that slowed CHO
   cells. If cells tolerate twice the safe dose, the 20 m³ designs pass to 77 m³ (all-favourable) and 65 m³ (low-lactate), and
   the low-lactate example saves 7.0% at 163 m³. The experiment is the bench test in `gas_exchange_study.md` section 8.
2. **Labour by tank size above 20 m³.** If crew falls as Humbird's plants suggest, the all-favourable example saves 18.2% at
   200 m³. A plant design with 100 m³ tanks and a crew count would settle it.
3. **Buildings and per-tank items above 20 m³.** The size answer now rests on Humbird's per-tank costs (makeup tanks, filter
   housings, $533k of building a tank), fitted to plants with tanks of 20 m³ and below. A priced plant design with 100 m³ tanks
   would test it.
4. **Whether bubbles hurt by surface speed or by gas per litre.** The second rule moves every scenario toward 128 to 200 m³ (3.7%
   to 15.7%). `gas_exchange_study.md` section 2.3 reads the evidence as favouring gas per litre, but foam at 13 mm/s is unmeasured.
5. **A retention device that scales with the tank.** A settler or disc-stack separator has fewer parallel units, which would make
   large tanks more likely.

## 9. Not done

- No size above 200 m³. Without the loop checks every scenario's cheapest size is the 200 m³ end of the range, and Humbird's
  vessel cost (`30.7 V + 800` $k) and the buildings fit are extrapolated above his range.
- No separate price for a tank built to a different shape beyond the model's steel and floor factor (`gas_exchange.shape_capex_factor`).
- No seed-train sizing, no heat exchanger, no impeller design, no run-length effect on membrane life with size.
- The search offers 16 designs per size. Intermediate pressures and a column outlet other than 55 mbar (`ge_col_pout`) are not
  searched; either could extend the sizes that pass the pH check.

## 10. Fed-batch and tank size (added 2026-11-19; recomputed 2026-11-20)

The scenarios can run the tank in fed-batch (`scenarios.SW["mode"]`), and the first three rungs of the ladder do. A batch is held
by its waste (the mass balance, `vessels_and_modes.md` section 10), not by gas exchange, so a deeper tank costs it no density.
Its handicap against perfusion is capital: the same plant makes a sixth to a half of the kilos. A bigger tank makes the capital
cheaper per m³, so size matters more to fed-batch than to perfusion. `tank_size.fedbatch_at` prices each scenario's switches in
fed-batch at each size, tank design chosen again (the low-lactate examples come out the tall tank with no added equipment for oxygen and CO₂; the
all-favourable example's the column and the pressure, a column of no size in fed-batch: an open point, see
`no_perfusion_downside.md`, section 2). Since 2026-11-21 each size also shows perfusion in a tank of that size, its design
chosen again (`tank_size.perfusion_at`); the first column is each scenario at its own tank:

| switches as in | perfusion in the scenario's own tank, $/kg | 20 m³: perfusion / fed-batch | 50 m³: perfusion / fed-batch | 100 m³: perfusion / fed-batch | 200 m³: perfusion / fed-batch |
|---|---|---|---|---|---|
| Low-lactate example | $48.68 | $48.68 (168 g/L) / $70.02 (37 g/L) | $46.60 (145 g/L) / $57.81 (37 g/L) | $45.89 (132 g/L) / $53.62 (37 g/L) | $45.53 (122 g/L) / $51.49 (37 g/L) |
| Low-lactate example, food-grade plant with shared medium | $43.92 | $43.92 (125 g/L) / $54.00 (37 g/L) | $42.29 (98 g/L) / $45.86 (37 g/L) | $41.67 (95 g/L) / $42.97 (37 g/L) | $41.19 (102 g/L) / $41.52 (37 g/L) |
| Cells that make almost no ammonia or lactate (rung 6) | $27.32 | $27.32 (168 g/L) / $31.17 (68 g/L) | $25.86 (145 g/L) / $26.58 (68 g/L) | $25.31 (132 g/L) / $24.99 (68 g/L) | $24.97 (102 g/L) / $24.17 (68 g/L) |
| All-favourable example | $7.02 | $7.22 (218 g/L) / $10.97 (120 g/L) | $7.01 (213 g/L) / $9.70 (120 g/L) | $7.15 (182 g/L) / $9.39 (117 g/L) | $7.34 (156 g/L) / $9.24 (120 g/L) |

- **A 100 m³ batch costs 7% to 15% less than a 20 m³ one** with the scenarios' switches ($71.76 to $60.71 in the low-lactate
  example, $11.28 to $10.44 with the all-favourable example's; for the all-favourable example 50 m³ is already as cheap). Beyond
  100 m³ the gain is 1% to 2.5%.
- **Compared at the same size, perfusion stays cheaper up to 100 m³ (2026-11-21).** In every row perfusion costs less than
  fed-batch at 20, 50 and 100 m³. At 200 m³ the cells that make almost no ammonia or lactate are $0.31 cheaper in fed-batch
  ($24.63 against $24.94), within the uncertainty; the others still favour perfusion. (2026-11-25: those cells are now cheaper in
  fed-batch at 100 m³ as well, $24.94 against $25.26, and at 200 m³ $24.12 against $24.91: their thin batch bubbles less gas.) A larger tank narrows the gap because it
  cuts fed-batch's handicap, the plant per kilo, while perfusion's culture must run thinner (168 g/L at 20 m³, 122 g/L at
  200 m³), held by what the column can strip safely.
- **No size closes the gap to perfusion (changed back 2026-11-20).** With the all-favourable example's switches fed-batch at
  200 m³ costs $10.22 against $7.62 in perfusion: the example now uses membranes at $8 a m², so perfusion no longer pays for
  membranes. (Earlier on 2026-11-20, with membranes at $1,450 a m², fed-batch from 50 m³ cost less than perfusion at 20 m³.) The
  low-lactate example in fed-batch at 200 m³ costs $59.33, against $49.50 in perfusion at 20 m³; with shared medium $49.19 against
  $45.04.
- **The same caveats as for perfusion, in the other direction.** The crew per m³ is held constant: if it fell with tank size as
  between Humbird's two plants, fed-batch would gain more (section 5). The chance of losing a batch is the same per tank-day at
  every size, and no animal cells have been grown above about 25 m³ (section 7).
