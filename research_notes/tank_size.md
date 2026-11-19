# Tank size: is 20 m³ the right size?

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.

> Recomputed 2026-11-16 on the current model (bubble protectant, antifoam's cost to oxygen transfer, bought oxygen in a yeast-style plant, dissolved oxygen held at half of air saturation, medium at least the culture that leaves with the cells).

Research date: 2026-11-15. Code: `tank_size.py` (`size_scan`, `summary`, `what_ifs`, `flatter`), `tests/test_tank_size.py`. Costs are 2025 dollars per kg of wet
cells. Every scenario uses a 20 m³ stirred tank in perfusion with a TFF filter loop. No default, scenario or pinned number moves: the scan calls
`floor_physics.explore(vessel_m3=...)` and adds no physics.

## 1. The answer

**Yes, for cost: 20 m³ is within 0.5% to 2.1% of the cheapest size in every scenario, and the curve is flat.**
Another size saves $0.06 to $1.94 a kilo. (Before the 2026-11-19 audit the cautious case was the exception, at 5.4%. Its saving in dollars has not moved, $1.94 against $1.95. Its cost
has, from $36.42 to $92.17: its published cells now need 95 litres of medium a kilo, and medium and membranes do not depend on tank size.)
**Yes, for risk: no animal cells have run above about 25 m³.**

| Scenario | Cost at 20 m³ | Cheapest size the model finds | Cost there | Saving | Sizes within 1% of the minimum |
|---|---|---|---|---|---|
| Best | $11.46 | 71 m³ | $11.31 | $0.15 (1.3%) | 23 to 158 m³ |
| Central | $32.80 | 43 m³ | $32.29 | $0.52 (1.6%) | 23 to 96 m³ |
| Central, food-grade plant with shared medium | $29.94 | 43 m³ | $29.62 | $0.33 (1.1%) | 21 to 96 m³ |
| Cautious | $92.17 | 111 m³ | $90.23 | $1.94 (2.1%) | 29 to 194 m³ |
| Reference (Humbird's tank, no tricks) | $12.81 | 14 m³ | $12.75 | $0.06 (0.5%) | 11 to 23 m³ |

- **Smaller tanks cost more, and the penalty grows fast below 10 m³.** At 10 m³ a kilo costs 3% to 5% more (best $11.75, central $34.27, cautious $95.21). At 5 m³ it
  costs 7% to 12% more. At 2 m³ it costs 20% to 33% more. The percentages are smaller than before the audit because the costs that do not depend on size grew; the dollars are the same.
- **Larger tanks save little because the loop checks rule out the tricks, not because gas transfer fails.** Without the checks, the cheapest design holds the culture at 258 g/L
  (central; cautious up to 100 m³) or 238 to 258 g/L (best) up to 200 m³, and the best case would save 2.9% at 200 m³, the central case 2.7% at 104 m³. The pH check on the column loop rules out
  those designs already at 20 m³, and the scenarios' own 20 m³ designs above about 24 to 44 m³. Relaxing it to twice the safe dose moves that limit to 35 m³ (best), 40 m³ (central)
  and 157 m³ (cautious).
- **The model's one assumption that would move the answer is labour.** It charges the same crew per m³ at every size. If staff per m³ fell with tank size as they do between
  Humbird's 2 m³ and 20 m³ plants, the best case would be 5.8% cheaper at 158 m³. Section 5 says why that is an upper bound.
- **The cautious scenario gains the most, 2.1% at 111 m³, and is no longer an exception to the 3% bound.** Oxygen holds its culture at about
  120 g/L at every size, so a larger tank's cheaper steel is not offset by a thinner culture. That saves $1.94 a kilo, as before. It is now 2.1% of a $92.17 kilo, not 5.4% of a $36.42
  one. Without the loop checks, 153 m³ saves 1.5%.

## 2. How the scan works

For each case and size, the scan tries every pair of tank tricks (none, column, column and 1 bar extra pressure, column and pressure and recycled oxygen) and tank shape
(liquid 1.6, 1.0, 0.75 or 0.5 times as deep as wide). That is 16 designs, as `scenarios.design` tries at 20 m³. It keeps the cheapest design whose column loop
- is pH-safe: its alkaline dose is at most 1.0 times that of the design judged safe (55 mbar out, 0.5 m³ of loop in a 20 m³ tank), and
- runs at a pass rate dense cultures have taken: at most `ge_passes_tested` (15) tank volumes an hour.

At 20 m³ the scan returns each scenario's own design and cost (the test checks this). Everything else about the scenario is held fixed. The reference case is
shown twice: as defined (Humbird's tall tank, no tricks) and with the design chosen again.

Two things set what a design costs at a size. The bioreactor share of the plant (32%) gets cheaper per m³ with size (Humbird's vessel cost, `capex_at_size`): the
per-m³ price is 2.7 times the 20 m³ price at 5 m³ and 0.49 times at 200 m³. And a deeper tank clears less CO₂ and mixes more slowly, so each trick has a size above which it
no longer lifts the limit.

## 3. Cost against size, and what binds

"Capital" is the tank, plant and column. "Loop" is the retention loop's hardware. "Medium" is feed plus growth factors. "Other" is utilities, other consumables and bought oxygen.
"Density limit" is the cap that sets the culture's density. "Loop checks cost" is what the pH or pass check adds against the cheapest design that fails it.

#### Best

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **14.33** | 5.06 | 0.08 | 0.66 | 3.85 | 2.02 | 2.66 | 238 | oxygen supply | none |
| 5 | column + 1 bar, square 1.0 | **12.39** | 3.11 | 0.08 | 0.66 | 3.85 | 2.02 | 2.66 | 238 | oxygen supply | none |
| 10 | column + 1 bar, squat 0.75 | **11.75** | 2.48 | 0.08 | 0.66 | 3.85 | 2.02 | 2.66 | 238 | oxygen supply | $0.02 (pH) |
| 20 | column + 1 bar + O₂, squat 0.75 | **11.46** | 2.06 | 0.08 | 0.61 | 3.99 | 2.02 | 2.70 | 258 | thickness | $0.14 (pH) |
| 50 | column + 1 bar + O₂, flat 0.5 | **11.34** | 1.94 | 0.08 | 0.61 | 3.99 | 2.02 | 2.70 | 258 | thickness | $0.30 (pH) |
| 100 | column, squat 0.75 | **11.46** | 2.61 | 0.07 | 0.93 | 3.18 | 2.02 | 2.66 | 170 | oxygen supply | $0.47 (pH) |
| 200 | column, flat 0.5 | **11.60** | 2.76 | 0.07 | 0.93 | 3.16 | 2.02 | 2.66 | 169 | oxygen supply | $0.61 (pH) |

#### Central

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **43.72** | 18.39 | 0.26 | 1.34 | 12.74 | 7.15 | 3.83 | 186 | oxygen supply | $3.49 (pH) |
| 5 | column + 1 bar, tall 1.6 | **36.59** | 11.24 | 0.26 | 1.32 | 12.77 | 7.15 | 3.84 | 189 | oxygen supply | $2.43 (pH) |
| 10 | column + 1 bar, square 1.0 | **34.27** | 8.93 | 0.26 | 1.32 | 12.76 | 7.15 | 3.84 | 188 | oxygen supply | $2.18 (pH) |
| 20 | column + 1 bar, square 1.0 | **32.80** | 7.44 | 0.26 | 1.31 | 12.79 | 7.15 | 3.84 | 191 | oxygen supply | $1.72 (pH) |
| 50 | column + 1 bar, flat 0.5 | **32.75** | 7.41 | 0.26 | 1.32 | 12.77 | 7.15 | 3.84 | 189 | oxygen supply | $2.30 (pH) |
| 100 | column, square 1.0 | **33.71** | 8.74 | 0.25 | 1.82 | 11.91 | 7.15 | 3.84 | 137 | oxygen supply | $3.47 (pH) |
| 200 | column, squat 0.75 | **33.86** | 8.88 | 0.25 | 1.81 | 11.93 | 7.15 | 3.84 | 138 | oxygen supply | $3.48 (pH) |

#### Central, food-grade plant with shared medium

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **35.89** | 10.23 | 0.26 | 1.34 | 12.74 | 7.15 | 4.16 | 186 | oxygen supply | $1.22 (pH) |
| 5 | column + 1 bar, square 1.0 | **31.95** | 6.29 | 0.26 | 1.34 | 12.74 | 7.15 | 4.16 | 186 | oxygen supply | $0.92 (pH) |
| 10 | column + 1 bar, square 1.0 | **30.79** | 5.12 | 0.26 | 1.32 | 12.76 | 7.15 | 4.17 | 188 | oxygen supply | $1.01 (pH) |
| 20 | column + 1 bar, square 1.0 | **29.94** | 4.25 | 0.26 | 1.31 | 12.79 | 7.15 | 4.17 | 191 | oxygen supply | $0.77 (pH) |
| 50 | column + 1 bar, flat 0.5 | **29.85** | 4.18 | 0.26 | 1.32 | 12.77 | 7.15 | 4.17 | 189 | oxygen supply | $1.06 (pH) |
| 100 | column, square 1.0 | **30.22** | 4.92 | 0.25 | 1.82 | 11.91 | 7.15 | 4.17 | 137 | oxygen supply | $1.56 (pH) |
| 200 | column, squat 0.75 | **30.29** | 4.98 | 0.25 | 1.81 | 11.93 | 7.15 | 4.17 | 138 | oxygen supply | $1.58 (pH) |

#### Cautious

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **117.78** | 39.93 | 0.82 | 2.76 | 37.30 | 29.41 | 7.56 | 114 | oxygen supply | $20.36 (pH) |
| 5 | column + 1 bar, tall 1.6 | **101.00** | 23.13 | 0.82 | 2.72 | 37.36 | 29.41 | 7.57 | 116 | oxygen supply | $11.38 (pH) |
| 10 | column + 1 bar, tall 1.6 | **95.21** | 17.31 | 0.82 | 2.68 | 37.41 | 29.41 | 7.57 | 118 | oxygen supply | $8.25 (pH) |
| 20 | column + 1 bar, tall 1.6 | **92.17** | 14.25 | 0.82 | 2.63 | 37.48 | 29.41 | 7.57 | 120 | oxygen supply | $6.59 (pH) |
| 50 | column + 1 bar, square 1.0 | **91.16** | 13.25 | 0.82 | 2.63 | 37.48 | 29.41 | 7.57 | 120 | oxygen supply | $6.45 (pH) |
| 100 | column + 1 bar, square 1.0 | **90.32** | 12.39 | 0.82 | 2.58 | 37.56 | 29.41 | 7.57 | 123 | oxygen supply | $5.93 (pH) |
| 200 | column + 1 bar, flat 0.5 | **91.89** | 13.98 | 0.82 | 2.63 | 37.48 | 29.41 | 7.57 | 120 | oxygen supply | $7.47 (pH) |

#### Reference, tank design chosen again

| m³ | design | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit | loop checks cost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | column + 1 bar, tall 1.6 | **16.22** | 8.88 | 0.05 | 0.65 | 2.47 | 2.00 | 2.17 | 226 | oxygen supply | $0.32 (pH) |
| 5 | column + 1 bar, square 1.0 | **12.81** | 5.46 | 0.05 | 0.65 | 2.47 | 2.00 | 2.17 | 226 | oxygen supply | $0.41 (pH) |
| 10 | column + 1 bar, square 1.0 | **11.68** | 4.33 | 0.05 | 0.65 | 2.47 | 2.00 | 2.17 | 226 | oxygen supply | $0.44 (pH) |
| 20 | column + 1 bar, square 1.0 | **11.03** | 3.68 | 0.05 | 0.65 | 2.47 | 2.00 | 2.18 | 226 | oxygen supply | $0.36 (pH) |
| 50 | column + 1 bar, flat 0.5 | **10.97** | 3.62 | 0.05 | 0.65 | 2.47 | 2.00 | 2.17 | 226 | oxygen supply | $0.54 (pH) |
| 100 | column, square 1.0 | **11.60** | 4.81 | 0.03 | 1.00 | 1.58 | 2.00 | 2.18 | 146 | oxygen supply | $1.28 (pH) |
| 200 | column, square 1.0 | **11.50** | 4.70 | 0.03 | 1.00 | 1.58 | 2.00 | 2.18 | 146 | oxygen supply | $1.23 (pH) |

#### Reference as defined (Humbird's tall tank, no tricks)

| m³ | $/kg | capital | loop | labour | membranes | medium | other | g/L | density limit |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 20.54 | 13.75 | 0.03 | 1.00 | 1.58 | 2.00 | 2.17 | 146 | oxygen supply |
| 5 | 14.86 | 8.07 | 0.03 | 1.00 | 1.58 | 2.00 | 2.17 | 146 | oxygen supply |
| 10 | 12.97 | 6.18 | 0.03 | 1.00 | 1.58 | 2.00 | 2.17 | 146 | oxygen supply |
| 20 | 12.81 | 6.36 | 0.02 | 1.22 | 1.04 | 2.00 | 2.17 | 120 | CO₂ removal |
| 50 | 13.53 | 7.70 | 0.00 | 1.65 | 0.00 | 2.00 | 2.18 | 88 | CO₂ removal |
| 100 | 15.88 | 9.30 | 0.00 | 2.08 | 0.00 | 2.14 | 2.36 | 70 | CO₂ removal |
| 200 | 19.37 | 11.47 | 0.00 | 2.62 | 0.00 | 2.69 | 2.58 | 56 | CO₂ removal |

### What binds at each size

- **2 to 10 m³: capital.** A small tank costs more per m³. Capital per kilo falls from $5.06 at 2 m³ to $2.48 at 10 m³ in the best case. The tricks lift the CO₂ limit, and oxygen supply
  sets the density: 238 g/L (best, column + 1 bar), 186 to 188 g/L (central) and 114 to 118 g/L (cautious). The loop check does not bind at 2 or 5 m³ in the best case and costs $0.02
  at 10 m³; in the central case it costs $2.18 to $3.49 at 2 to 10 m³.
- **20 m³: the pH check.** The check already costs $0.14 (best), $1.72 (central) and $6.59 (cautious): a cheaper design exists (a tall tank with column + 1 bar for the best case, and with
  recycled oxygen too for the central and cautious cases) and fails the pH check. The culture sits at 258 g/L (best, set by thickness), 191 g/L (central, set by oxygen supply) or 120 g/L
  (cautious, set by oxygen supply because it runs at 2 mm/s of gas).
- **50 m³ and above: the pH check, then oxygen supply.** A deeper tank clears less CO₂ through the sparger, so the loop must make more passes, and the alkaline dose rises with
  the passes. The 20 m³ designs fail the check at 24 to 44 m³. At 50 m³ the best and central cases move to the flat tank and keep their density (258 and 189 g/L). At 100 m³ and above the
  cheapest passing design drops the pressure (and, for the best case, the recycled oxygen) and keeps the column alone, so the density falls to 169 to 170 g/L (best) and 137 to 138 g/L
  (central). The loop checks cost $2.30 to $3.48 a kilo in the central case at 50 to 200 m³. The cautious case keeps column + 1 bar at every size and holds about 120 g/L.
- **Mixing never binds** in a chosen design: a flat tank mixes fast. In the reference case as defined (tall tank, no tricks), oxygen supply binds at 2 to 10 m³ and CO₂ removal from 20 m³ up,
  and the culture thins from 146 g/L to 56 g/L. That is why the reference's own cost curve turns up above 14 m³.
- **Heat is not modelled.** The cells give off 5.2 kW per m³ of culture at 258 g/L (best), 3.5 kW/m³ at 191 g/L (central) and 2.1 kW/m³ at 120 g/L (cautious). The wall of a 200 m³ tank
  has 1.3 m² per m³ (squat, central) to 1.4 m² per m³ (flat, best), so a jacket alone must take 1.9 to 2.4 kW/m² (central, best; both cultures are thinner there) against 1.2 to 1.8 kW/m²
  at 20 m³. That is near the top of what a jacket removes (my estimate, 1 to 5 kW/m², low confidence). An external heat exchanger on the column loop would take the rest; its
  cost is not in the model.

## 4. The retention loop and size

The TFF loop is sized on permeate per m³ of tank (`floor_physics.explore`, `retention.py`): permeate per kilo is the medium per kilo less what the bleed of cells carries out
(1000 / density); membrane area per m³ is that permeate times the harvest rate per m³, divided by the flux (5 L/m²/h); hardware is $1k per m² times 1.84 for installation; membranes cost $1,450 per
m² and last 3,960 litres. Since the 2026-11-19 audit a lost run throws its membranes away early: the life is multiplied by the share of a planned run an average start completes
(85% at 1% of runs lost a day). That share does not depend on tank size unless the chance of losing a run does.

**What this does at each size.** The area per m³ of tank, and so the loop's cost per kilo, is the same at every size for the same density and medium (the test checks it). The loop is not what
decides the size.

| | Best, 20 m³ | Best, 200 m³ | Central, 20 m³ | Central, 200 m³ |
|---|---|---|---|---|
| Membrane area | 233 m² | 1,215 m² | 343 m² | 2,308 m² |
| ATF-10 equivalents (11 m² each) | 21 | 110 | 31 | 210 |
| Loop hardware, $/kg | 0.08 | 0.07 | 0.26 | 0.25 |
| Membranes, $/kg | 3.99 | 3.16 | 12.79 | 11.93 |
| Membranes, share of the cost | 35% | 27% | 39% | 35% |

**Assumptions in the sizing that favour or penalise a size:**
1. *Hardware per m² does not fall with size.* A big skid costs less per m² than a small one. That penalises large tanks. The what-if (`ts_loop_hw_exp` = 0.3, hardware as V^0.7) changes the best
   optimum from 1.3% to 1.5% and the central from 1.6% to 1.7%. The hardware is under 1% of the cost, so this barely matters.
2. *Membranes cost the same per litre at every size.* They are 27% to 39% of the cost, and they set the loop's cost. They fall at large sizes only because the thinner culture needs less
   permeate per kilo ($12.79 to $11.93 in the central case). The price per m² would fall with a bigger order, but that has nothing to do with tank size.
3. *Flux is 5 L/m²/h whatever the density.* A thinner culture at large size would hold a higher flux. That favours large tanks slightly, through hardware only, so the effect is under $0.05 a kilo.
4. *No unit rounding.* A 2 m³ tank needs 1 to 3 ATF-10 units' worth of membrane; the model charges the fraction. That flatters the smallest tanks by a few cents.
5. *Not charged at any size:* pumping power for the loop, labour and downtime to change membranes (a full set per 33-day run, so 110 to 210 ATF-10 equivalents at 200 m³), sterile connections, and the time culture spends in
   the loop outside the tank. The column loop has a pH and a pass check; the TFF loop pumps the whole culture through fibres and has none. All of these grow with area, so they would penalise
   large tanks, but nothing in the repo prices them.
6. *In the reference case as defined, the model charges no loop at 50 m³ and above.* The bleed at 88, 70 and 56 g/L carries 11.3, 14.2 and 18.0 litres of liquid a kilo, at least the 11.2 litres of
   medium the cells need, so permeate is zero. Until 2026-11-16 the model still bought only 11.2 litres a kilo there, not the 14.2 or 18.0 the bleed removes, so the reference was
   low by $0.44 and $0.99 a kilo at 100 and 200 m³ (on the model of 2026-11-15). `explore` now buys at least what the bleed removes, and the table above has the corrected figures ($15.88 and $19.37). This affected only the reference as defined. In every scenario design the medium exceeds what the bleed removes.

## 5. Other assumptions that favour or penalise a size

The plant model scales only the bioreactor share with size. The rest (buildings, utilities, seed trains) is priced per m³ at its 20 m³ value.

| Assumption | Effect | Direction |
|---|---|---|
| Labour: the same crew per m³ at every size | Humbird's two plants (95 staff for 24 × 20 m³, 132 for 96 × 2 m³) give crew per m³ ∝ (tank size)^-0.54. Extrapolated to 200 m³ it cuts labour by 71%. | Penalises large tanks, rewards small tanks. The exponent comes from two sizes at or below 20 m³; above 20 m³ it is an extrapolation. |
| The chance of losing a run per tank-day is the same at every size | A bigger tank has more ports and seals and loses a whole tankful. BioPlan's survey found larger facilities had about 3 times the contamination of smaller ones (facilities, not tanks). | Flatters large tanks. |
| Seed train and restart time are the same at every size | A 200 m³ tank needs about 3 more doublings of seed than a 20 m³ tank. | Flatters large tanks. |
| Shape: a squat tank mixes faster, by Humbird's Eq. 2.18 (t_m ∝ T^(2/3) (H/T)^2.5) | Used below its fitted range (H/T from 1.6). Wide flat tanks (7 m across at 200 m³) need several impellers. | Flatters large flat tanks. |
| Gas speed through the surface is fixed (the model's rule) | `gas_exchange_study.md` section 2.3 reads the bubble-damage evidence as gas per litre, not per surface: then a deeper tank can pass faster gas (up to 13 mm/s at 200 m³, a speed whose foam nobody has measured). | Penalises large tanks. |

The what-ifs below change one at a time and report the cheapest size and the saving against 20 m³. Each is zero at 20 m³ by construction (the test checks it).

| What-if | Best | Central | Central, shared medium | Cautious | Reference, redesigned |
|---|---|---|---|---|---|
| As modelled | 71 m³, 1.3% | 43 m³, 1.6% | 43 m³, 1.1% | 111 m³, 2.1% | 44 m³, 2.3% |
| No loop checks (physics only) | 200 m³, 2.9% | 104 m³, 2.7% | 104 m³, 1.8% | 153 m³, 1.5% | 200 m³, 3.7% |
| pH check relaxed to twice the safe dose | 44 m³, 1.5% | 71 m³, 2.6% | 71 m³, 1.7% | 153 m³, 3.6% | 34 m³, 2.3% |
| Pass limit at the top of its range (24 an hour) | 71 m³, 1.3% | 43 m³, 1.6% | 43 m³, 1.1% | 111 m³, 2.1% | 44 m³, 2.3% |
| Labour follows Humbird's crew rule | 158 m³, 5.8% | 96 m³, 3.4% | 158 m³, 3.6% | 111 m³, 3.8% | 98 m³, 5.0% |
| Loop hardware has economies of scale | 71 m³, 1.5% | 43 m³, 1.7% | 43 m³, 1.3% | 111 m³, 2.5% | 44 m³, 2.4% |
| Chance of losing a run grows with size (V^0.33) | 32 m³, 0.3% | 24 m³, 0.2% | 19 m³, 0.0% | 19 m³, 0.0% | 44 m³, 2.3% |
| Gas per litre held at its 20 m³ value | 200 m³, 3.6% | 200 m³, 6.3% | 200 m³, 3.7% | 111 m³, 5.2% | 200 m³, 7.0% |
| Favourable to large tanks (pH check relaxed, crew rule, loop economies) | 140 m³, 6.5% | 71 m³, 4.8% | 125 m³, 4.7% | 153 m³, 5.8% | 78 m³, 5.2% |

- **The pass limit never binds first.** The pH check fails before the pass count reaches 15.
- **The crew rule is the largest single effect for the best case, and the least supported above 20 m³.** It would put the best case at 158 m³ and 5.8% cheaper. For the central and cautious
  cases, gas per litre moves the answer more (6.3% and 5.2%). No source gives crew against tank size above 20 m³.
- **A chance of loss that grows with size removes the large-tank gain.** At V^0.33 the best case's optimum drops to 32 m³ and 0.3%, the central case's to 24 m³ and 0.2%, and the
  shared-medium and cautious cases do best at 19 m³. (Before the audit the cautious case still saved 2.6% at 43 m³.) A lost run now also throws its membranes away, so more losses cost more.
- **The most favourable mix saves 4.8% for the central case, at 71 m³.** The best and cautious cases save 6.5% and 5.8%, at 140 m³ and 153 m³,
  sizes nobody has run with animal cells. (Before the audit the cautious case saved 14.0% there.)
- **A flatter tank helps only at 100 m³ and above.** At 50 m³ the scenarios' flat tank (0.5) is already the cheapest shape for the central case ($32.75, against $32.80 at 20 m³); flatter
  costs more ($33.63 at 0.3). At 100 m³ a tank with the liquid 0.4 times as deep as wide (6.3 m across, 2.5 m deep) passes the check with column + 1 bar for $32.79, the 20 m³ price; the scan's
  own choice there (column alone, square) costs $33.71. At 200 m³ the best aspect (0.3) gives $33.20. So flatter tanks hold the cost flat out to 100 m³ and add 1.2% at 200 m³
  (`tank_size.flatter`). The scenarios do not offer these shapes, and nobody has built a tank this wide for cells.

## 6. The largest size at which each design passes

| Scenario | The 20 m³ design | Its limit with the model's checks | Limit with the pH check at twice the safe dose | Largest size that keeps the 20 m³ density, with the design chosen again |
|---|---|---|---|---|
| Best | column + 1 bar + O₂, squat | 24.8 m³ | 34.7 m³ | 24.6 m³ |
| Central | column + 1 bar, square | 24.3 m³ | 40.3 m³ | 23.9 m³ |
| Central, shared medium | column + 1 bar, square | 24.3 m³ | 40.3 m³ | 23.9 m³ |
| Cautious | column + 1 bar, tall | 43.9 m³ | 157.2 m³ | 43.1 m³ |

- **The limit sits 22% to 24% above 20 m³ for the best and central designs, and 120% above for the cautious one.** A design fails when its pH dose passes 1.0 times the safe dose. At 20 m³
  the dose is 0.81 (best), 0.90 (central) and 0.84 (cautious). So each 20 m³ design already runs at 81% to 90% of the check, and 20 m³ is close to the largest size the best and central
  designs allow. (Before the recompute the cautious limit was 26.3 m³.)
- **A re-chosen design holds 258 g/L (best) to 24.6 m³, and the central case's 191 g/L to 23.9 m³.** Above that the central case thins only slightly at first (189 g/L at 50 m³, $32.75), then
  drops to 137 g/L at 100 m³ and costs $0.91 a kilo more there ($33.71) than at 20 m³ ($32.80).
- **The check is a judgement, not a physical limit.** The safe dose is 0.29 of the dose that slowed CHO cells (Paul et al. 2020, via a summary in `gas_exchange_study.md` section 8): one study, and a measure
  (rise × share) the study did not use. At 3.4 times the safe dose the loop would reach that harm. Between 1.0 and 3.4 nothing is measured.

## 7. How likely is each size?

These are judgement, built from the notes cited. They are not a forecast.

**Sources of evidence.** Animal cells have run in a stirred tank at 25 m³ (pharma fed-batch, `Continuous harvest bioreactor progress/biopharma_continuous_culture.md`), at 21 m³ (insect cells,
`floor_physics.SPECIES_PRESETS`, Ashizawa 2022) and at 20 m³ for food (Vow; `Continuous harvest bioreactor progress/cultivated_meat_reactor_progress.md`). Perfusion with a retention device has run at 4 m³
(Genzyme Geel). Vendor ratings stop at 5 m³. Nobody has run animal-cell perfusion above about 4 m³. For meat cells, no perfusion above 10 L is reported, and besides Vow no vessel above 2 m³.
Microbial tanks of 150 m³ and more exist (Quorn's 155 m³ airlift runs continuously), so the steel is not the problem. `vessels_and_modes_sources/operating_modes.md` puts 2% to 3% on anyone having run
animal-cell perfusion at 20 m³ for a month, and 6% at 10 m³ or more.

Three events, for a tank of each size. "Possible" means: with funding and a development programme of up to ten years, nothing in the model's physics or the evidence stops it.

- **H**: the tank is built and run with animal cells for a production run of at least two weeks (any mode, any density).
- **R**: the tank is run in perfusion with a retention device for at least four weeks at 100 g/L or more.
- **D**: the scenario's own design works at that size (R, at the design's density, with its tricks for at least four weeks).

| Size | H, possible | R, possible | R, shown by end of 2035 | D, best | D, central | D, cautious |
|---|---|---|---|---|---|---|
| 2 m³ | 99% | 97% | already shown | 15% | 17% | 19% |
| 5 m³ | 99% | 93% | already shown (4 m³) | 14% | 16% | 19% |
| 10 m³ | 98% | 85% | 25% | 13% | 15% | 17% |
| 20 m³ | 97% | 75% | 12% | 9% | 13% | 15% |
| 50 m³ | 88% | 55% | 4% | 7% | 10% | 11% |
| 100 m³ | 78% | 42% | 2% | 9% | 10% | 8% |
| 200 m³ | 62% | 30% | 1% | 7% | 7% | 6% |

How each column is built:
- **H.** Nothing in the physics stops a stirred tank above 25 m³. Large pharma tanks stop at 25 m³ for batch-size reasons, and the one report at 25 m³ found lower viability traced to CO₂ stripping.
  The odds fall with the size of the step beyond 25 m³ (shear, mixing time, pH and dissolved-gas zones): 88% at 50 m³, 78% at 100 m³, 62% at 200 m³. By the end of 2035 I put H, shown, at about 12% for 50 m³,
  5% for 100 m³ and 2% for 200 m³: the largest vessels in use or planned are 20 to 22 m³ (Vow, Meatly, Orbillion), and the 100,000 L and 250,000 L plans (UPSIDE Glenview, GOOD Meat, BlueNalu) were paused, abandoned or not started.
- **R.** The anchor is `retention_devices.md`: a filter holds 120 g/L at 20 m³ for a month at 75%. Each doubling of size above 20 m³ multiplies the odds by about 0.82, because the area (and the number of
  parallel units, up to 210) grows with the tank, and a failure in one unit has more units to occur in. Below 20 m³ the odds rise toward the 2 m³ perfusion tanks that are standard in pharma.
- **D.** D multiplies R by a density factor and a tricks factor, and takes the two as independent (they are probably positively correlated, which would raise D by a third). The density factor is 0.47 at 258 g/L (35% against 75%
  in `retention_devices.md`) and 0.67 at 145 g/L, straight-line between (0.50 at 238 g/L, 0.59 at 191 g/L, 0.62 at 170 g/L), and 0.67 below 145 g/L. The cautious case keeps 0.67 at its
  120 g/L: `no_perfusion_downside.md` gives it 50% against 75%, judged when it ran at 145 g/L and not judged again. The tricks factor is 0.30 for the column with pressure (a column loop works at
  20 m³: 35%, `gas_exchange_study.md` section 5; pressure 85%), 0.26 with the recycled oxygen too, and 0.35 for the column alone. Best at 100 m³ rises to 9% because its design drops the
  pressure and the recycled oxygen and the density falls to 170 g/L. Example, best at 20 m³: 0.75 × 0.47 × 0.26 = 9%. Each entry is uncertain by a factor of 1.5 either way.

**What the odds say about size.** The chance that the scenario's own design works falls with size, but slowly: it is 14% to 19% at 2 to 5 m³, 9% to 15% at 20 m³ and 6% to 11% at 50 to 200 m³. The small
tanks are likelier but cost 7% to 33% more. Beyond 20 m³ the odds that any perfusion run works fall from 75% to 55%, 42% and 30% (R), and the best saving is $1.94 a kilo (cautious) or less. So the odds-adjusted
answer favours 10 to 20 m³. At 10 m³ the cost is 3% to 5% higher and R rises from 75% to 85%.

## 8. What would change the answer

1. **A measured pH limit for the column loop.** The largest size depends on one check set at 0.29 of the dose that slowed CHO cells. If cells tolerate twice the safe dose, the best and central
   cases run to 44 m³ and 71 m³ and save 1.5% and 2.6%. The experiment is the bench test in `gas_exchange_study.md` section 8.
2. **Labour by tank size above 20 m³.** If crew falls as Humbird's plants suggest, the best case saves 5.8% at 158 m³. A plant design with 100 m³ tanks and a crew count would settle it.
3. **Whether bubbles hurt by surface speed or by gas per litre.** The second rule moves every scenario toward 111 to 200 m³ (4% to 6%). `gas_exchange_study.md` section 2.3 puts 85% on bubble death scaling with gas per litre, but foam at 13 mm/s is unmeasured.
4. **A retention device that scales with the tank.** A settler or disc-stack separator has fewer parallel units, which would make large tanks more likely. The retention note puts 5% on a settler at 258 g/L.

## 9. Not done

- No size above 200 m³. Without the loop checks the best case still falls slowly at 200 m³ (2.9% below 20 m³), and Humbird's vessel cost (`30.7 V + 800` $k) is extrapolated above his range.
- No separate price for a tank built to a different shape beyond the model's steel and floor factor (`gas_exchange.shape_capex_factor`).
- No seed-train sizing, no heat exchanger, no impeller design, no run-length effect on membrane life with size.
- The search offers 16 designs per size. Intermediate pressures and a column outlet other than 55 mbar (`ge_col_pout`) are not searched; either could extend the sizes that pass the pH check.
