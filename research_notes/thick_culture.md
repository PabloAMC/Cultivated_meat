# How thick can a stirred or airlift culture be?

> Repinned 2026-11-27 (the nitrogen and carbon balance: each case's cells are charged the amino acids their ammonia takes and the glucose they ferment; a cleaning route's dialysate is floored at the case's own nutrients). Only the all-favourable example moves, by $0.05 at every cap: its own design $6.97 -> $7.02, at 180 g/L $7.44 -> $7.49 fixed and $7.20 -> $7.25 checked. The conclusions are unchanged.

> **2026-11-25.** The model now chooses the gas flow up to the cap the cells tolerate, and holds a culture thinner by itself
> when its column loop fails its checks. The section 7 table is recomputed. Two scenarios now bubble less gas and lose fewer
> cells: the shared-medium plant $44.53 -> $43.92 (125 g/L), the cautious case $181.13 -> $179.90 (109 g/L). The others do not
> move. "Fixed" now means the scenario's own added equipment and shape, with the model's own gas choice and thinning. The
> conclusion holds: no density cap from 180 to 400 g/L changes any scenario's cost except the all-favourable example's at 180.

> **2026-11-21.** `scenarios.design` now holds a culture thinner when that lets a column loop pass its checks, which is the
> finding of section 7 below, now adopted: every scenario runs the column with recycled oxygen at the densest culture its loop
> passes (low-lactate example 168 g/L, $48.68; cautious 134 g/L, $181.13; all-favourable example 219 g/L in a flat 42 m³ tank,
> $6.97). Oxygen comes from the loop, so no oxygen limit binds; the loop's checks do. The section 7 table is recomputed; the
> rest of this note is the 2026-11-20 snapshot below.
>
> Repinned 2026-11-20 (final pass). Two changes reach this note. (1) `explore()` now lowers the sparger's oxygen transfer in a thick culture itself (`viscous_kla`, this note's section 5), so every scenario's own cost already counts it: the low-lactate example runs at 154 g/L (191 before), the cautious case at 103 g/L (120 before). (2) The all-favourable example is now the one case of `scenarios.all_favourable()` ($7.62): the column and 1 bar in a square 42 m³ tank, a density limit of 320 g/L, 155 g/L reached. Sections 1 and 5 to 8 are rewritten with the figures of `python thick_culture.py`. **Conclusion unchanged and stronger: no scenario's tank reaches 258 g/L, so a density limit of 180, 320 or 400 g/L costs no scenario anything with its own design.** **New finding:** the all-favourable example would cost $7.39 with recycled oxygen in a squat tank if its culture were held at 180 g/L, and $7.17 in a flat tank held at 215 g/L, against $7.62; the cautious case $181.93 at 130 g/L against $185.59. Held thinner, the recycled-oxygen loop passes the pH and pass-rate checks it fails at the density the tank would otherwise reach. `scenarios.design` never holds a culture below its limits, so it misses these designs.

> Earlier repins (2026-11-20 first batch; 2026-11-19 scenario restructure, nutrient floor and audit batch; 2026-11-16 recompute) are recorded in the changelog.

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

Date: 2026-11-20 (research 2026-11-15). Code: `thick_culture.py`; tests: `tests/test_thick_culture.py`; inputs: `tc_*` in `inputs.py`.
Costs are 2025 dollars per kg of wet cells. The cost scan sets the density limit with `vm={"caps": {"thickness of the culture": X}}`.
Since 2026-11-20 the viscosity laws and the oxygen-transfer correction live in `floor_physics` (`viscous_kla`, on by default) and
the page runs them too.

Labels: **MEAS** = measured in the cited work; **INF** = my arithmetic or inference; **JUDG** = judgement. Access: **full** = whole text
read; **part** = sections read, or a fetch summary; **snippet** = search snippet only; **abstract**.

## 1. Answer

The model's density limit is 258 g/L (volume fraction 0.25, 86 million 17.7 um cells per mL); the all-favourable example takes 320 g/L.
No scenario's tank reaches it. Oxygen from the sparger, lowered by viscosity, holds the low-lactate example and the shared-medium plant
at 154 g/L, the all-favourable example at 155 g/L and the cautious case at 103 g/L. The question has two parts, and they have
different answers.

- **Viscosity does not stop the stirred tank near 258 g/L. As a viscosity limit, 258 is too low.** At 258 g/L the culture is 2.4 times as
  viscous as medium. A 20 m3 stirrer at the model's 43 W/m3 runs at Reynolds number 2.2e5 there and stays fully turbulent up to about
  600 g/L (volume fraction 0.58). Mixing time, which Humbird's equation does not tie to viscosity, holds. The yield stress is under
  0.001 Pa at 258 g/L and 0.15 Pa at half cells; the impeller's stress is 10^4 times larger. Cells settle at 0.6 cm/h and the gas
  rises 3,000 times faster. Viscosity first bites in the pumps and filters (Clincke 2013), and in oxygen transfer.
- **As the density a tank can hold, 258 is too high for every design the scenarios use.** They feed oxygen with a sparger, and
  viscosity cuts the oxygen transfer: the sparger's limit falls from 196 to 154 g/L in the low-lactate example's tank, from 198 to
  155 g/L in the all-favourable example's and from 120 to 103 g/L in the cautious case's. With no added equipment for oxygen and CO₂ CO2 stops a tank at 120 g/L.
  A closed loop of recycled oxygen avoids the sparger's limit, but it fails the model's pH and pass-rate checks above about 215 g/L
  in the all-favourable example (section 6).
- **The cost is not sensitive to this number.** A limit of 180, 320 or 400 g/L in place of 258 changes no scenario's cost with its
  own design. Counting viscosity in oxygen transfer costs $0.68 a kilo in the all-favourable example (+10%), $1.77 in the low-lactate
  example (+3.7%) and $2.64 in the cautious case (+1.4%); the model now counts it.
- **Probabilities that a 20 m3 tank holds the density for a month with everything else solved, at any cost** (section 8; a rough
  judgement): 258 g/L about 18%, 320 g/L about 6%, 400 g/L about 1%. Most of that risk is the retention device, not viscosity.

## 2. What 258 g/L stands for

Humbird 2021 (PMC8362201, *part*, fetch summary of Sect. 2.2.1): a practical maximum cell density occurs "at a volume fraction of about
0.25", citing Iordan: viscosity "increases sharply as cell-cell collisions become more frequent". He takes 3,000 pg cells of 17.7 um and
gets "86 x 10^6/ml or 258 g/L wet". The number is his own arithmetic and has no citation. It is a rule of thumb about viscosity. It is not
a mixing, power or oxygen calculation: his mixing-time equation (Eq. 2.18) and his kLa equation (Eq. 2.16, after Xing et al. 2009, CHO medium
at 37 C) have no viscosity term in them (*part*). In the model, the 258 limit (`pf_x_visc`) and, since 2026-11-20, the oxygen-transfer correction of section 5 (`viscous_kla`) are
where viscosity enters the core calculation (`floor_physics.explore`).

Check (INF): 258 g/L / 1.036 g/mL = 0.249; 258 g/L / 3 ng = 86e6 cells/mL; 86e6 x 2.9 pL = 0.249. Humbird adds that smaller cells (CHO) reach
more cells per mL "but the maximum mass density is the same".

## 3. Viscosity at volume fractions 0.1 to 0.5

Medium is 0.75 mPa s at 37 C (`pf_medium_viscosity`). Thomas: 1 + 2.5 phi + 10.05 phi^2 + 0.00273 exp(16.6 phi), the equation the model uses
everywhere and Clincke et al. used for CHO. Krieger-Dougherty: (1 - phi/0.65)^(-1.625); Iordan et al. fitted phi0 = 0.65 to CHO at 1,000 per second
(MEAS, *full*). "Apparent" raises the excess over the medium by 1.33 for the shear thinning a large tank sees (`tc_thin`, Tregidgo, below).
Cell counts are for the model cell (2.9 pL). Computed by `thick_culture.viscosity_table()`.

| phi | g/L | million cells/mL | Thomas | Krieger | apparent, mPa s | yield stress, Pa |
|---|---|---|---|---|---|---|
| 0.10 | 104 | 35 | 1.36 | 1.31 | 1.11 | 0 |
| 0.20 | 207 | 69 | 1.98 | 1.82 | 1.73 | 0.0001 |
| **0.25** | **259** | **86** | **2.43** | **2.20** | **2.17** | **0.0005** |
| 0.30 | 311 | 104 | 3.05 | 2.73 | 2.80 | 0.002 |
| 0.35 | 363 | 121 | 4.02 | 3.51 | 3.76 | 0.008 |
| 0.40 | 414 | 138 | 5.70 | 4.72 | 5.43 | 0.024 |
| 0.50 | 518 | 173 | 15.75 | 10.84 | 15.46 | 0.15 |

Measured points:
- **Tregidgo et al. 2023** (Chem Eng Res Des 194:344, *part*: the viscosity and mixing sections): CHO at 20 to 100e6 cells/mL, 37 C. Below 40e6 cells/mL
  the culture is water-like. At 100e6 it shear-thins: 1.3 mPa s at 1,000 per second, 1.8 mPa s at 45 per second, 2.4 mPa s at the low shear of 50 rpm,
  and up to 3 times the low-density value below 40 per second (large scatter). That is the Thomas value at a quarter cells (1.8 mPa s with
  0.75 mPa s medium). Their cell volume was not given, so the match is loose. **Thomas is about right, within 30%, for the viscosity the impeller sees.**
- **Iordan et al. 2007** (arXiv:0709.3671, *full*): CHO spun down and re-diluted, 20 C, 0 to 60% by volume. Yield-stress fluid at high volume; the
  yield stress grows as phi^8.4; elastic cell-cell interaction "at large concentrations (phi >= 0.4)". The yield stresses in the table come from
  their scaling with their stress scale 1.4 Pa (`tc_yield_sigma`, INF; the plotted values were not extracted).
- **Clincke et al. 2013 part I** (PMC3752962, fetch summary): phi 0.1 at 4e7 cells/mL and 0.5 at 2e8. Their advice: stay under 1.46e8 (phi 0.37, 383 g/L)
  so cells keep 2 um apart. The TFF inlet pressure was 0.52-0.54 bar at 1.2-1.3e8 and 0.8-1.0 bar at 2e8; the ATF's vacuum failed at 1.2-1.3e8.
  Thomas gives 3.7 against 18.9 for that step (INF, phi 0.33 and 0.51), and the pressure rose only 1.7 times, so Thomas probably overstates at phi 0.5
  (the flow differed between those points). **Growth fell from 0.4 to 0.15 per day above 1.5e8 cells/mL**, which the cost model does not have.

An arithmetic slip in an earlier note: `retention_devices_sources/membrane_filters.md` section 3 gives Thomas = 2.27 at phi 0.25. The equation gives 2.43
(2.42 at 258 g/L); Krieger gives 2.20. The conclusion there is unchanged.

## 4. The stirrer and mixing time

Humbird's tank: 20 m3, 16 m3 of liquid, 2.34 m wide, 3.74 m deep, impeller a third of the width (0.78 m), 43 W/m3, so 688 W. With a power number of 5
(`tc_np`, the cautious end; large tanks use 1.3-1.5) the stirrer turns at 46.8 rpm and the tip moves at 1.9 m/s. Computed by `thick_culture.stirrer`.

| phi | g/L | Re | turbulent? | power to keep Re at 10,000, W/m3 | smallest eddies near the impeller, um | stress ratio (impeller / yield) |
|---|---|---|---|---|---|---|
| 0.10 | 104 | 429,000 | yes | 0 | 28 | 9e9 |
| 0.25 | 259 | 221,000 | yes | 0 | 46 | 4e6 |
| 0.40 | 414 | 88,000 | yes | 0.06 | 92 | 8e4 |
| 0.50 | 518 | 31,000 | yes | 1.4 | 201 | 1e4 |
| 0.55 | 570 | 16,000 | yes | 11 | | |
| 0.60 | 622 | 7,600 | borderline | 98 | | |

- **Same mixing time needs the same power.** In fully turbulent flow, mixing time depends on power per volume and geometry, and not on viscosity
  (Humbird Eq. 2.18). Tregidgo measured a constant mixing number (time x speed) from Re 5,600 up in a 250 mL tank, and a mixing time about
  twice that of water only at their lowest speed (*part*). So the stirrer power for the same mixing time stays 43 W/m3 up to phi 0.55 (570 g/L).
  Above that it climbs: 98 W/m3 at 0.6.
- **Where it leaves the turbulent regime** (`tc_re_turb` 10,000; 5,600 from Tregidgo): 603 g/L with the shear thinning at 1.33, 545 g/L at 3, 612 g/L
  with Krieger. With a power number of 1.5 the margin is 1.5 times larger.
- **Cavern.** A yield-stress fluid moves only in a cavern round the impeller. The cavern fills a tank of width 3 impeller diameters when the impeller stress
  (Np rho N^2 D^2 = 1,900 Pa) exceeds the yield stress by about (T/D)^3 = 27, to within a coefficient of order 1 (the form of Solomon et al. 1981,
  *snippet*; I did not read the coefficient). The ratio is 10^4 or more up to phi 0.5.
- **Eddies grow.** Humbird picks 43 W/m3 so that the smallest eddies are one cell across (20 um in water, factor 50 for peak dissipation near the impeller). At the same
  power the eddies are 46 um at 258 g/L and 92 um at 414 g/L, if the cells feel the bulk viscosity. Cells smaller than the eddies may not.
  The thick culture is gentler on the cells, not harsher.
- **Airlift.** The rising gas gives rho g u_s = 60 W/m3 at 6 mm/s, more than the stirrer's 43 (`gas_power`; 59 W/m3 in `gas_flow_cap.md`). An airlift
  has no impeller to stall. Eddies at the combined power: 37 um at 258 g/L. Its mixing time is not computed here (no measurement was found). Its oxygen
  limit is the sparger's, and viscosity cuts that the same way (section 5).

## 5. Oxygen and CO2, hold-up, settling and heat

**Oxygen (INF from a snippet, with a wide range).** Oxygen transfer falls with the apparent viscosity to the power -0.4 in stirred tanks (Yagi and Yoshida 1975, a
university course note, *snippet*; `tc_kla_exp`, range 0 to 0.6). Evidence against a large effect at lower density: Amgen's CHO perfusion cultures from
1e5 to 35e5 cells/mL lost almost no kLa (AIChE 2017 abstract, 403 on fetch, *snippet*), and a 20,000 L study reported no kLa change between cell-free and spent
harvest medium (Bioprocess International 2024, *part*). Evidence for: a 2025 Biotechnology Journal paper reports a 10-40% fall with culture rheology (*snippet*, not read).
No measurement was found at 1e8 cells/mL or more in a stirred tank.

| phi | g/L | kLa x (0.4 exponent) | gas hold-up at 6 mm/s | settling, cm/h | cells' heat, kW/m3 |
|---|---|---|---|---|---|
| 0.10 | 104 | 0.85 | 4.3% | 1.45 | 2.1 |
| 0.25 | 259 | 0.65 | 5.0% | 0.62 | 5.2 |
| 0.40 | 414 | 0.45 | 6.3% | 0.22 | 8.3 |
| 0.50 | 518 | 0.30 | 8.9% | 0.09 | 10.4 |

The oxygen a sparger can feed solves x = x_base x kLa factor(x), where x_base is the model's limit (`thick_culture.oxygen_limit`):

| tank | the sparger's oxygen limit, kLa of medium | with viscosity (exponent 0.4) | range, exponent 0 to 0.6, shear thinning 1 to 3 |
|---|---|---|---|
| Humbird's tank, 6 mm/s | 146 | **121** | 96-146 |
| Low-lactate example's design (column + 1 bar, tall) | 196 | **154** | 118-196 |
| Cautious case's design (column + 1 bar, tall) | 120 | **103** | 84-120 |
| All-favourable example's design (column + 1 bar, square, 42 m³) | 198 | **155** | 120-198 |

Since 2026-11-20 `explore()` applies this correction itself (`viscous_kla`), so these are the densities the scenarios run at. A closed
loop of recycled oxygen feeds its oxygen through the column, not a sparger, so kLa does not enter; the loop pays for viscosity through
its film and pump, which `column_design` computes at the density asked. No scenario uses it at its own density (section 6).

**CO2.** CO2 leaves with the sparge gas, whose equilibrium does not depend on viscosity to first order. The model's limit (120 g/L at 20 m3, 6 mm/s) stands. Clincke's
wave bag reached 31 kPa (310 mbar) CO2 at 2e8 cells/mL and named it a limit, with viscosity and oxygen. Hold-up is computed from the bubbles' rise speed with a
rigid-sphere drag law (Schiller-Naumann, INF) scaled to the measured 4% at 6 mm/s (`gas_flow_cap.md` section 3: 3.5% at 4.2 mm/s, 4.5% at 7.7 mm/s). Hold-up
rises 25% by 258 g/L and about 55% at 414 g/L, which helps transfer and costs liquid volume. It does not stop anything below 10%.

**Settling.** Stokes' speed of a 17.7 um cell is 2.4 cm/h in medium (cell 1.036 g/mL, medium 1.007); crowding (Richardson-Zaki, (1 - phi)^4.65) cuts it to
0.62 cm/h at 258 g/L. With nothing stirring, a cell falls the 3.74 m of liquid in 25 days. The gas rises 3,000 times faster. **Settling does not matter in a stirred or
airlift tank.** It matters only to a settler (`retention_devices.md`).

**Heat.** At 120 g/L the cells give off 2.4 kW/m3 (`gas_flow_cap.md`); the model's `pf_heat_per_o2` gives 2.4 here too. At 258 g/L it is 5.2 kW/m3, or 83 kW in the tank. A jacket on the
wall and floor takes off about 7.9 kW/m3 per m3 of liquid in the tall tank and 7.0 kW/m3 in the squat one, with U = 400 W/m2/K and 10 K
(`tc_jacket_u`, `tc_cool_dt`; both assumed; nothing was found for a 20 m3 animal-cell tank). That puts the jacket's limit at **396 g/L (tall) and 349 g/L (squat)**. Internal coils or colder
water lift it. The model does not count heat removal; 258 g/L is inside the jacket's reach, 400 g/L is not.

## 6. Which limit binds first (g/L; volume fraction = g/L / 1,036)

`thick_culture.limits_at`, printed by `python thick_culture.py` ("limits of three tanks").

| limit | Humbird's tank, no added equipment for oxygen and CO₂ | Low-lactate example's design | All-favourable example's design |
|---|---|---|---|
| CO2 removal | **120** (0.12) | none (column) | none (column) |
| mixing rule (oxygen transfer vs mixing time) | 189 (0.18) | 350 | 635 |
| oxygen supply, kLa of medium | 146 | 196 | 198 |
| oxygen supply, with viscosity | **121** (0.12) | **154** (0.15) | **155** (0.15) |
| column loop checks (pH exposure, 15 passes/h) | none | none | none |
| the model's viscosity rule | 258 (0.25) | 258 | 320 (0.31) |
| jacket cooling | 396 (0.38) | 396 | 286 (0.28; a 42 m³ square tank has less wall per m³) |
| ATF filter, Clincke | 321 (0.31) | 321 | 321 |
| stirrer leaves turbulent flow | 603 (0.58) | 603 | 629 |
| TFF filter, Clincke | 518 (0.50) | 518 | 518 |

- **Without the added equipment for oxygen and CO₂, the plain tank stops at 120 g/L from CO2**, then oxygen with viscosity at 121 (146 without) and the mixing rule at 189. It never reaches 258.
- **With the column and 1 bar, oxygen with viscosity comes first** (154 and 155 g/L in the two examples, 103 in the cautious case). **Then heat** at about
  290-400 g/L, **then the ATF's vacuum** at 321 (4 L, Clincke), **then the TFF at 518**. Stirring, the thing the 258 rule was meant to protect, comes last at about 600.
- **With recycled oxygen (the closed loop), the first limit is the loop's own checks.** The column must pass the CO2 the sparger cannot, which grows faster than
  density. In the all-favourable example's flat tank the loop needs 7.5 passes an hour at 200 g/L, 10.6 at 215 and 29.5 at 258, against the 15 an hour dense
  cultures have taken (`ge_passes_tested`); its pH exposure is 0.63 of the dose judged safe at 200 g/L, 0.88 at 215 and 2.5 at 258. So the loop passes up to
  about 215 g/L. These are screening rules, not physical walls: a larger column passes more culture and costs more (`scenarios.design` refuses such designs).
- Clincke's own advice (1.46e8 cells/mL, phi 0.37, 383 g/L) and the onset of elasticity (phi 0.4, 414 g/L) lie near the jacket's limit and well under the turbulence limit.

## 7. What the cost does if the density limit is 180, 258, 320 or 400 g/L

`thick_culture.cost_by_cap(key)`, printed by `python thick_culture.py`. Two readings. **Fixed**: the scenario's own tank design, the loop's checks not
applied (since 2026-11-25 the model itself chooses the gas flow and thins a failing loop, so "fixed" keeps only the added equipment and shape). **Checked**: the added equipment for oxygen and CO₂ and shape chosen again among the scenario switches' settings, as `scenarios.design` does, with the loop's checks applied
(a design whose column breaks the pH or pass-rate rules is refused). $/kg; the density reached in brackets.

| scenario | 180 | 258 (model) | 320 | 400 |
|---|---|---|---|---|
| All-favourable example, fixed | 7.49 (180) | **7.02** (219; its own limit is 320) | 7.02 (219) | 7.02 (219) |
| All-favourable example, checked | 7.25 (180; recycled oxygen, squat) | 7.02 (219) | 7.02 (219) | 7.02 (219) |
| Low-lactate example, fixed and checked | 48.68 (168) | **48.68** (168) | 48.68 (168) | 48.68 (168) |
| Low-lactate example, shared medium, fixed and checked | 43.92 (125) | **43.92** (125) | 43.92 (125) | 43.92 (125) |
| Cautious, fixed and checked | 179.90 (109) | **179.90** (109) | 179.90 (109) | 179.90 (109) |

Since 2026-11-21 every scenario's own design is the column with recycled oxygen held thinner than its limits allow, at the densest
culture its loop passes (168, 134 and 219 g/L), so the "checked" reading finds the same design as the scenario except where the cap
binds. The table before that day (2026-11-20): all-favourable $7.62 at 155 g/L (checked $7.39 at 180), low-lactate $49.50 at
154, shared medium $45.04, cautious $185.59 at 103.

- **No scenario benefits from a thicker culture**: oxygen from the sparger binds at 103 to 155 g/L, under 180. A limit of 180 g/L costs nothing either.
  (Before 2026-11-20 the low-lactate example ran at 191 g/L and 180 g/L cost it $0.38.)
- **A thinner limit can lower the checked cost** (new 2026-11-20). Held at 180 g/L, the all-favourable example's culture lets the recycled-oxygen loop in a
  squat tank pass its checks, and that design costs $7.39 against its own $7.62. Scanning the limit in steps of 5 g/L, the cheapest is $7.17 at 215 g/L
  (recycled oxygen, flat tank); above 215 the loop fails its checks and the case falls back to its own design. The cautious case reaches $181.93 at 130 g/L
  with recycled oxygen in a tall tank, against $185.59. `scenarios.design` and `scenarios.all_favourable()` choose the tank design at the density the tank
  would reach and never hold a culture thinner to let a design pass, so they miss these. This is reported for the engine's owner; the figures in this note
  and the scenarios' costs are the model's as it stands.
- If the sparger's oxygen did not fall with viscosity (`cost_viscous_oxygen`, the correction turned off): the all-favourable example $6.94 (198 g/L), the
  low-lactate example $47.73 (196 g/L), with shared medium $44.15, the cautious case $182.95 (120 g/L). The model counts the correction.
- **The gain from thickness is small** because capital is a smaller share than the medium and retention. A thicker culture also asks more of the retention device: Clincke's growth rate
  fell 60% above 1.5e8 cells/mL (phi 0.37). Output is density x growth rate, so 400 g/L (phi 0.39) could make less than 320. The scan holds growth fixed.
- `explore(x_scale=...)` scales only the CO2 limit, so it is not a density limit for the whole tank; the scan uses the `vm` cap.

## 8. Probabilities

The probabilities in this section are a rough judgement made while building the model with an AI assistant; not measured and not
reviewed by an expert. The model does not use them. The reasoning for each is given below the table.

Definition: a 20 m3 stirred or airlift tank of 17 um animal cells holds the density for at least 30 days of continuous perfusion at the scenario's duty, at any cost.
Evidence for the densities shown: Clincke 4 L, 2.14e8 cells/mL (phi 0.5) with a TFF loop for days; 50 L, phi 0.13 for 50 days (Ott 2024, `membrane_filters.md`); 195 L, 1e8 for days
(Xu 2020); a vendor datasheet gives 160-264e6 cells/mL in 40 L (`gas_flow_cap.md`, VEND). Nothing at 1,000 L or more above 1e8 cells/mL was found.

| statement | 258 g/L | 320 g/L | 400 g/L |
|---|---|---|---|
| A. Viscosity, stirrer and cavern do not stop the tank (phi 0.25 / 0.31 / 0.39) | 97% | 94% | 85% |
| B. A, and heat and gas transfer (oxygen, CO2) work with the added equipment, at any cost | 51% | 28% | 12% |
| C. B, and a retention device holds it a month at the low-lactate example duty (`retention_devices.md`: 35% at 258) | **18%** | **6%** | 1% |
| a plain sparged tank, no added equipment for oxygen and CO₂, holds it | 1% | under 1% | under 1% |

How the rows combine: B = A x heat (95%, 90%, 80%) x gas side given the added equipment (55%, 33%, 17%); C = B x retention (35%, 20%, 8%).
- A is high because the Reynolds number is 2e5 to 9e4 and the yield stress is tiny. The risk in A is meat cells, which may clump and rise in viscosity in ways CHO does not (fibroblasts, DNA from lysed
  cells), and the measured shear thinning, which reaches 3 times.
- The gas side is the repo's untested added equipment for oxygen and CO₂: a column loop at the pass rate and pH exposure needed, 1 bar of headspace and recycled oxygen. At 258 g/L the recycled-oxygen loop needs about 30 passes an hour in the all-favourable example; the low-lactate example's sparger cannot feed more than 154 g/L.
- Retention is the largest risk. The ATF stopped at 1.3e8 cells/mL (phi 0.31); only the TFF has gone beyond, and only for days at 4 L.
- Two comparison points. At 180 g/L: A 98%, B 70%, C about 40% (retention 55%). At 120 g/L, Humbird's optimistic design, `retention_devices.md` gives 75%.

## 9. What would settle it

1. Oxygen transfer (kLa) in a stirred tank of 1 m3 or more at 1e8 cells/mL or more, measured in the culture, not in cell-free medium. It sets whether the sparger's oxygen is 154 or 196 g/L in the low-lactate example's design (121 or 146 in Humbird's tank).
2. The viscosity of a meat-cell culture (fibroblast or muscle line) at phi 0.2 to 0.4 at 37 C, with the flow curve below 40 per second.
3. A month-long run of any filter loop above 1e8 cells/mL at a scale of 100 L or more.
4. A column-loop pass through live cells at 15 or more passes an hour for a week.
5. Whether growth slows above phi 0.37 in a meat-cell line, as Clincke's CHO did.

## 10. Sources and what was not found

| source | what it gives | access |
|---|---|---|
| Humbird 2021, PMC8362201 | the 258 g/L rule, kLa and mixing equations without viscosity | *part* (fetch summary) |
| Iordan, Duperray, Verdier 2007, arXiv:0709.3671 | Krieger fit phi0 = 0.65, yield stress ~ phi^8.4, elasticity from phi 0.4 | *full* |
| Clincke et al. 2013, PMC3752962 | phi 0.1 at 4e7 and 0.5 at 2e8; pressures; limits at 1.3-2.1e8; growth 0.4 to 0.15 per day; CO2 31 kPa | *part* (fetch summary) |
| Tregidgo et al. 2023, Chem Eng Res Des 194:344 (UCL repository) | CHO viscosity at 20-100e6 cells/mL, 37 C; mixing number constant from Re 5,600 | *part* (text extracted; sections 3.3-3.5 read) |
| Yagi and Yoshida 1975, via a university course note | kLa ~ apparent viscosity^-0.40 | *snippet* |
| Amgen AIChE 2017 abstract (kLa up to 35e6 cells/mL); Bioprocess Intl 2024 (20,000 L); 2025 Biotechnology Journal | kLa against cell density and rheology | *snippet*; *part*; *snippet* |
| Solomon, Elson, Nienow, Pace 1981 | cavern size form | *snippet* |
| repo notes: `gas_flow_cap.md`, `gas_exchange_study.md`, `membrane_filters.md`, `retention_devices.md` | tank, hold-up, heat, loop numbers, retention odds | *full* |

Not found: absolute viscosity of CHO or meat cells at phi 0.3-0.5 at 37 C; kLa at 1e8 cells/mL or more in a stirred tank above 1 L; mixing time in a thick culture above 1 L; the coefficient of
the cavern equation; Grenville's transition-regime mixing correlation (not used); any heat-transfer figure for a jacketed 20 m3 animal-cell tank; rheology of meat-cell suspensions.
