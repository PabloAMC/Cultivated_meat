# Design tricks for a 20 m³ animal-cell tank: what each relieves, and whether it scales

Compiled 2026-11-16 at Pablo's request ("explore the possible tricks on the design of the bioreactor"). Reading, arithmetic and
the model only; nothing measured. Access levels: **model** (computed with this repository's code), **repo** (an earlier research
note, which carries its own sources), **search** (a search-engine summary, not read), **memory** (my background knowledge, not
checked this session; treat as a lead). The CFD plan that would test several of these is `cfd_plan.md`.

## 1. What limits the tank today (model)

| case | cost | density | what binds | the next limits |
|---|---|---|---|---|
| Rung 1, Published cells, ordinary tank, 2 mm/s | $63.0 | 46 g/L | CO₂ removal | oxygen 70, mixing 219, thickness 258 g/L |
| Humbird's optimistic design, 6 mm/s | $12.5 | 120 g/L | CO₂ removal | oxygen 146 (with antifoam), mixing 189 |
| Low-lactate example (column, 1 bar, squarer tank, oxygen held at half of air saturation) | $29.4 | 191 g/L | oxygen supply | thickness 258 |
| All-favourable example (the same, with recycled oxygen and a squat tank) | $9.7 | 258 g/L | thickness of the culture | — |

So there are two regimes. **Without a bubble-free way to remove CO₂, CO₂ binds**, and every trick that removes CO₂ without bubbles
pays a lot (the column with 1 bar of pressure is worth $20.6/kg for Published cells). **Once CO₂ is dealt with, oxygen binds** (antifoam is taken to
cut the sparger's oxygen transfer by a quarter), and the tricks worth having are those that put oxygen in per watt and per litre of
gas. Beyond both sits the thickness of the culture (258 g/L, Humbird's viscosity estimate, `thick_culture.md`).

## 2. The catalogue

"Scales?" asks whether something fundamental (a law of geometry or physics, not an engineering gap) stops it at 20 m³ and above.
"In the model" names where it lives, if anywhere.

### A. Gas into and out of the tank directly

| trick | what it relieves | scales? | evidence of scale | in the model |
|---|---|---|---|---|
| More gas per litre, with a protectant | CO₂ and oxygen | yes, until foam; foam is the cap, not physics of transfer (`gas_flow_cap.md`) | 0.1–0.2 vvm in dense CHO at 3–200 L (repo) | the "gas the cells tolerate" switch |
| Pure oxygen in the sparge gas | oxygen | yes; cost is bought or made oxygen | standard in pharma (memory) | Humbird's 90% oxygen is the default |
| Pressure in the headspace | oxygen (not CO₂) | yes; steam-rated steel takes 1–3 bar | none with cells at 1 bar gauge (repo) | the "1 bar" added equipment for oxygen and CO₂ |
| Two spargers: a microsparger for oxygen, a drilled pipe for CO₂ | decouples oxygen and CO₂; fewer, larger bubbles strip CO₂ with less foam | yes | common in high-density pharma processes (memory; Xing et al. describe stripping with larger bubbles, repo) | **not in the model**: one gas flow does both jobs |
| Microspargers (fine bubbles) | oxygen per litre of gas | yes, but more foam and more cell damage per bubble surface | common (search) | not separate |
| Antifoam choice and dose | oxygen (antifoam costs transfer) | yes | effect 0–50% (repo) | `pf_antifoam_otr` = 0.75, a judgement |
| Dissolved-oxygen setpoint held low | oxygen (bigger driving force) | yes | cells grow at 10–100% air saturation (repo) | in every scenario since 2026-11-16 (`sc_do_setpoint`) |
| Squat tank shape | CO₂ (more gas per litre at the same velocity), mixing | yes; costs steel and floor | geometry (model) | the tank-shape switch |

### B. Gas exchange away from the cells

| trick | what it relieves | scales? | evidence of scale | in the model |
|---|---|---|---|---|
| Packed stripping column beside the tank | CO₂ without bubbles; oxygen with an oxygen sweep | yes: towers are ordinary industrial equipment; the open questions are the cells (film, pH, deposits) | not with animal cells (repo) | the "column" added equipment for oxygen and CO₂ |
| Bubble cage (Pablo's design): sparger in a fine-mesh inner cylinder | gas the cells never feel | **poorly**: the mesh area grows as size² while volume grows as size³, so exchange per litre falls; fine mesh clogs | microcarriers, small tanks (search) | vessel row "Stirred tank with a bubble cage" |
| Gas-filled inner cylinder (a membrane) | oxygen with pressure; CO₂ only with a CO₂-free sweep | only by packing area: about 9 m² of wall against 1,200–1,500 m² needed (`vessels_and_modes.md` §9) | — | not a row |
| Membrane bundle in the tank or on a loop | bubble-free oxygen and CO₂ | yes if area is packed; the obstacles are a steam-rated, non-wetting, non-fouling fibre at under about $100/m² | 50 L tubular, about 200 L dynamic membrane (search) | set aside (`gas_exchange_study.md` §7.5) |
| **Gas exchange on the filter loop** | uses the perfusion loop's pump and piping for a column or membrane module | yes; same as the column | — | **not in the model**; the column is costed with its own pump |
| Pre-conditioned feed (CO₂-free, oxygen-saturated medium) | almost nothing: medium holds about 1 mmol/L of oxygen against an uptake of 18–40 mmol/L per hour (arithmetic) | — | — | not needed |

The filter loop already carries the culture out of the tank and back. The medium it removes takes about 3% of the cells' CO₂ in the
Humbird's optimistic design and about 6% in the low-lactate example (model, with 15 mM of bicarbonate above the fresh medium's; the model leaves this out). The
useful trick is to put the CO₂ column, or a membrane module, on that same loop, so the gas exchange shares its pump, piping and
sterile boundary. Whether the filter's flow rate (set by the permeate) and the column's (set by CO₂) can share a loop is a design
question for the next pass.

### C. The cells

| trick | what it relieves | scales? | in the model |
|---|---|---|---|
| Fat in the feed in place of fat made from glucose | CO₂ per oxygen (respiratory quotient 1.20 → 0.97) | yes; needs a carrier or emulsion | the "fat taken from the feed" lever (repo) |
| Cells selected for CO₂ tolerance | CO₂ (density proportional to tolerated pCO₂) | yes; but the salt limit caps how much CO₂ the tank can hold (TODO.md) | the CO₂-tolerance lever |
| Cells that consume lactate | salt budget, medium | yes | the waste levers |
| Lower temperature (33 °C) | oxygen per cell, heat | yes; growth slows too | not in the model |

### D. The medium

| trick | what it relieves | scales? | in the model |
|---|---|---|---|
| Oxygen carriers (perfluorocarbon emulsions) | oxygen capacity, effective transfer | **cost and recycling at scale; perfluorocarbons are PFAS**, which the EU is moving to restrict, so close to a non-starter for food | no |
| Recombinant oxygen-carrying proteins | oxygen capacity | cost | no |
| A non-bicarbonate buffer (for example HEPES) | the salt budget at high CO₂ | cost per litre, and food status | no; worth a check because the salt limit binds |
| Base choice (sodium hydroxide vs carbonate) | salt and CO₂ load | yes | no |
| Ammonia sorbent, electrodialysis, dialysis | medium per kg (not the cell filter, unless the exchange is across the culture) | yes | the sorbent lever; `medium_reuse.py` and `medium_reuse.md` price the others |

### E. Vessel and mixing

| trick | what it relieves | scales? | in the model |
|---|---|---|---|
| Impeller choice (radial vs axial, multiple impellers) | oxygen per watt, mixing, shear | yes | not separate; the vessel's oxygen multiplier would carry it (CFD target A5) |
| Draft tube with impeller (stirred airlift) | mixing per watt, gentle circulation | yes | CFD target A5 |
| Airlift | no stirrer | yes (155 m³ for fungus) but tall, so less gas per litre | vessel row |
| Surface aeration (rocking bags, orbital shaking) | bubble-free | **no**: surface per litre falls with size; about 2.5 m³ is the practical limit (search, vendor) | bag row only |
| Internal coils or jacket area for heat | heat, at 200 m³ (about 470 kW) | jacket area per volume falls with size; coils fix it | not a limit at 20 m³ (repo) |

### F. Plant and operation

| trick | what it relieves | in the model |
|---|---|---|
| Restart from a healthy neighbouring tank | lost time after a loss (4 days in place of 14) | restart setting (added today) |
| Many small tanks or few large | CO₂ (shallower) against capital | tank-size study: 20 m³ is within 0.5–1.8% of the cheapest (cautious 4.6%) (repo) |
| Continuous harvest | output per tank | perfusion and fill-and-draw rows |

## 3. What would pay most, given the limits above

1. **For Published cells (CO₂-bound): any bubble-free CO₂ removal.** The column with pressure ($20.6/kg), the bubble cage ($23.7/kg, a
   judgement-heavy estimate), or more gas the cells tolerate. The deciding experiments are cell-side: a film of dense culture on packing, and gas steps
   with protectant (`gas_exchange_study.md`).
2. **For the low-lactate example (oxygen-bound): oxygen per watt and per litre of gas.** Two spargers, impeller choice, the antifoam's
   real cost to transfer, and pressure. (The dissolved-oxygen setpoint is now in every scenario; with it the all-favourable example reaches the
   thickness limit.) Two-sparger operation is the one not yet in the model, and it is
   standard practice; it should be a lever.
3. **The salt limit** is now quietly binding where CO₂ tolerance should help (TODO.md). A non-bicarbonate buffer or a different base
   would test whether that limit is real.
4. **Put gas exchange on the filter loop**, and cost the shared loop.

## 4. Fundamental scaling problems, in short

- **Surface-to-volume** (falls as 1/size): surface aeration, bubble cages, wall membranes, jacket cooling. These need area packed
  into the volume (fibres, coils) or they stop at a few m³.
- **Depth** (CO₂ removal per litre of gas falls with liquid depth): tall tanks and airlifts. Squat tanks and external columns fix it.
- **Length of a flow path** (oxygen falls along it): packed beds and hollow-fibre reactors stay small.
- **Foam**: grows with gas flow; it is the likelier cap on sparging at scale, and cannot be simulated reliably.
- **Regulation, not physics**: perfluorocarbon oxygen carriers (PFAS) and poloxamer's food status (`gas_flow_cap.md`).
