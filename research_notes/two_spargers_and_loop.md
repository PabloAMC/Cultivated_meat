# Two spargers, a column on the filter loop, and thinner cultures in the design search

2026-11-21. Code: `floor_physics.explore` (`spargers`, `micro_share`, `col_on_loop`, `MICRO_GRID`), `scenarios.design` and
`scenarios.thinned`, `design_space.run`, `scenarios.all_favourable`. Inputs: `ge_spargers`, `ge_micro_o2_x`, `ge_micro_kill_x`,
`ge_sparger2_k`, `ge_col_on_loop`. Page: two levers in the side bar ("Spargers in the tank", "CO₂ column on the filter loop"),
mirrored in `floorExplore`. TODO items: "the design search never holds a culture below the density its limits allow", "two
spargers", "gas exchange on the filter loop". All costs are per kilo of wet cells harvested, in 2025 dollars.

## 1. Thinner cultures in the design search

**What was wrong.** `scenarios.design` and `design_space.py` dropped a tank design whose CO₂ loop failed its checks (the pH
exposure judged safe, and no more than 15 tank volumes an hour through the loop) at the density the other limits allow. A thinner
culture makes less CO₂, so the same loop may pass at a lower density. The vessel grid already did this (`vessels._thinned`).

**What changed.** A design whose loop fails is run again at the densest culture its loop passes (24 halvings between 0 and the
density it failed at), and kept if it costs less. The choice carries that density as `thin` (g/L), which `explore_kwargs` applies
as a cap named "what the column can strip safely". The page's `scDesign` does the same steps; moving a switch by hand drops the cap
(the design is chosen again if the page is choosing it).

**What it found.** The column that also feeds recycled oxygen ("oxygen" in the tricks switch) fails its checks at full density in
every perfusion case, and was never chosen. Held thinner it is the cheapest design in each:

| Case | Before (2026-11-21, after the Humbird fixes) | Now | The design now |
|---|---:|---:|---|
| Low-lactate example | $49.22 (1 bar, tall tank, 154 g/L, oxygen) | $48.68 | oxygen column, tall tank, held at 168 g/L |
| Shared-medium plant | $44.73 | $44.53 | the same, 168 g/L |
| Cells that make almost no ammonia or lactate | $27.44 | $27.26 | the same, 168 g/L |
| Published cells, in perfusion (cautious) | $185.09 | $181.13 | oxygen column, tall tank, 134 g/L |
| All-favourable example | $7.42 (1 bar, square tank, 155 g/L) | $6.98 | oxygen column, flat tank (liquid half as deep as wide), 219 g/L |

The denser culture is bought with more gas, so bubbles kill more of the cells grown (9.1% in the all-favourable example against 8.0%
in Humbird's optimistic design); its nutrients per kilo harvested are 0.6% above his design's, per kilo grown below. The
column with recycled oxygen and a lime scrubber is two elements nobody has run with animal cells (`design_space.py`).

## 2. Two spargers

**The option.** A fine-bubble (sintered) sparger for oxygen beside the drilled pipe. From `gas_flow_cap.md` (drilled holes
against sintered spargers): fine bubbles pass 4-20 times the oxygen per litre of gas (`ge_micro_o2_x`, 4: the low end, because at
Humbird's 6 mm/s a drilled pipe already uses about a tenth of the oxygen it bubbles), kill about ten times the cells per litre of
gas (`ge_micro_kill_x`, 10), and both kinds of bubble leave a 3.7 m deep tank saturated with CO₂, so splitting the gas does not
change the CO₂ removed. A vendor note says fine-bubble spargers are not recommended for perfusion because they plug; that is not
priced. The second sparger with its gas line costs a quarter of the $164k Humbird gives a 20 m³ bioreactor's internals (Table 3.3),
$41k per tank in his accounting for bioreactors (`ge_sparger2_k`, an assumed share).

**The engine.** A share s of the gas cap goes through the fine-bubble sparger. The oxygen limit becomes the one-sparger limit x
(4 s^0.8 + (1 - s)^0.8) (kLa ~ gas^0.8 for each bubble population), never more than the next limit; the cells killed scale by
1 + 9 s. The share is the one that costs least on a grid of 23 values (`MICRO_GRID`); the page searches the same grid. The antifoam's
cut to oxygen transfer is charged on both spargers (one snippet says fine bubbles do not pay it; not taken).

**What it is worth.** Little, because fine bubbles kill so many cells that only 1-13% of the gas goes through them:

| Case | One sparger | Two spargers, tank design chosen again |
|---|---:|---:|
| Humbird's optimistic design (CO₂ holds it at 120 g/L) | $15.72 | $15.78 (the sparger's cost only) |
| Low-lactate example, 1 bar, tall tank (oxygen-bound) | $49.22 | $49.15 (1% of the gas through it, 165 g/L) |
| Published cells in perfusion, oxygen column without recycled oxygen | $192.03 | $190.95 (3%) |
| All-favourable example, 1 bar, square tank | $7.42 | $6.96, but the loop then fails its checks |
| Every case, with the tank design chosen again | as section 1 | $0.01-0.10 more: the oxygen column already lifts oxygen |

Since the oxygen column held thinner already lifts the oxygen limit, two spargers add only their cost to every scenario as now
designed, and the all-favourable example does not take them. They are a lever on the page, off at the start; they matter in a tank
without the oxygen column, where oxygen binds.

## 3. Gas exchange on the filter loop

**A column on the loop.** In perfusion the culture already circulates through the cell filter's loop, whose pumps are in the TFF
hardware (`rt_tff_hw`). A dense CHO filter loop ran at 15 tank volumes an hour for weeks (Clincke 2013, `ge_passes_tested`), as much
as the column's own checks allow, so the column's flow fits a loop of that kind. On the loop (`col_on_loop`) the column buys no pump
of its own: $30k for 300 m³/h scaled with flow to the 0.6 power, times 3 for installation (`ge_pump_cost`, `ge_pump_flow`,
`ge_install_x`, all from `gas_exchange.py`). The pumping power is still paid, for the column's head. It saves $0.03-0.06 a kilo in
the cases with a column; the all-favourable example takes it ($6.98 to $6.97). Whether the filter's flow (set by the shear in its
fibres) and the column's (set by CO₂) can be the same flow is a design question; the model takes the smaller of the column's flow
and 15 tank volumes an hour as shared.

**A membrane module on the loop** (hollow fibres exchanging gas, as in a blood oxygenator) is not priced. The earlier search
(`gas_exchange_study.md` section 7.5) found no gas-exchange membrane that is both priced and rated for repeated steaming;
membrane-aerated wastewater modules are sold by the thousand m² with no price per m². Without a price and a life it cannot be a
lever. It stays open.

## 4. What would settle it

- A fine-bubble sparger in a dense perfusion culture for a month: whether it plugs, and the cells it kills per litre of gas with
  protectant (the 10 times is a rough figure from a review).
- The flow a full-scale TFF loop recirculates for its fibres' shear, against the column's flow.
- The open questions of the column itself (a film of dense culture on packing for weeks, the pH exposure): section 8 of
  `gas_exchange_study.md`.
