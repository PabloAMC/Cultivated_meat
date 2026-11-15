# Vessel types and operating modes

> **Note, 2026-11-15.** The figures in this note were computed with the old hoped-for device that holds the cells back in a
> perfusion tank ($89k per m3 of tank, no membranes). The model now prices a hollow-fibre filter loop with its membranes
> (`retention.py`, `research_notes/retention_devices.md`), so its perfusion cases cost more. Perfusion cells in the grids below are now dearer: in the reference case the stirred tank is $11.84, the airlift $14.11, the bag $17.23; in the central case the stirred tank is $26.64. The other modes do not change. RESULTS.md has the current reference grid.

Research date: 2026-11-15. Code: `vessels.py` (grid), `floor_physics.explore(vm=...)` (the physics), `page_vessels.js` (the page's
mirror). Inputs: `inputs.py` `vm_*`. Costs are 2025 dollars per kg of wet cells, for a plant built to each design.

Three research passes sit behind this note. Each has its own file with every source, its URL and how much of it was read:

- `vessels_and_modes_sources/airlift_bubble_column_bags.md`: airlift, bubble column, rocking bag, single-use stirred bag.
- `vessels_and_modes_sources/packed_bed_hollow_fibre.md`: fixed and packed beds, hollow fibres.
- `vessels_and_modes_sources/operating_modes.md`: batch, fed-batch, fill-and-draw, chemostat, perfusion, retention devices,
  continuous harvest at scale, cultivated-meat news for 2025-2026.

Access levels used below: **full** (read in full), **part** (read in part, or through a fetch tool's extract), **abstract**,
**snippet** (a search result only), **secondary** (another document quotes it).

## 1. The question

People often compare "stirred tank" with "perfusion" as if they were two options. They are answers to two different
questions. The vessel is what holds the cells: a stirred tank, an airlift, a bed of carriers, a cartridge of hollow fibres,
a single-use bag. The operating mode is how the vessel is run: batch, fed-batch, fill-and-draw, chemostat, perfusion. Before
this work the model priced one vessel, the stirred tank. It also gave the same $17.81 to batch, fed-batch, chemostat and
fill-and-draw, because all of them were treated as "waste not washed out".

The grid below changes only the vessel and the mode. It holds the cells, the plant class, the tank tricks and the losses
fixed, in one of two settings:

- **the reference case**: `floor_physics.explore()` at its defaults (engineered cells doubling every 24 h, a food-grade plant
  without clean rooms, no tank tricks, no losses). The stirred tank in perfusion gives $11.48.
- **the central scenario** (`scenarios.py`): selected cells on a low-waste feed, doubling every 36 h, a food-grade plant, gas
  at up to 4 mm/s, the column with pressure and recycled oxygen, a squat tank, 1% of runs lost a day, a 14-day restart,
  30% of growth factors bought, medium at $0.20 a litre. The stirred tank in perfusion gives $18.14.

Each vessel is priced at the largest unit that has been built for animal cells, up to 20 m3. A bag is 5 m3, a fixed bed
65 litres, a hollow-fibre unit half a litre. So the rows also differ in unit size where the vessel cannot reach 20 m3. A plant of
small units needs more staff per m3. The model scales labour with the number of tanks per m3, to the power 0.54. That
exponent comes from Humbird's two plants: 95 staff for 24 x 20 m3, 132 staff for 96 x 2 m3.

## 2. The vessels: what limits each one

| | Stirred tank | Airlift (bubble column) | Single-use bag | Packed bed | Hollow fibres |
|---|---|---|---|---|---|
| Oxygen in | Bubbles; Humbird's cap 29 mmol/L/h with 90% O2 at 6 mm/s | Bubbles; kLa about the same as a stirred tank at the same gas speed (32 vs 26 per hour at 6 mm/s, Negulescu 2023's correlation, quoted in full by Hubbard 2024) | Bubbles, as a stirred tank; a 2,000 L XDR bag measured kLa 1-20 per hour at 0.01 vvm (Cytiva note, full) | Medium pumped through the bed and oxygenated outside; about 9 mmol/L/h of unit volume on air (calculated), enough for 113 g/L only with enriched gas | Through the fibre wall; oxygen falls along the fibre, which caps its length; no figure per litre found |
| CO2 out | Only in the sparge gas; a deeper tank clears less | The same, but the tank is taller: it needs 15.8 mm/s for the gas per litre a 20 m3 stirred tank gets at 6 mm/s (calculated) | As a stirred tank, at a smaller and squatter size | Into the gas over a falling film (vendor, qualitative) | Through a gas-transfer module (vendor) |
| Mixing and shear | Stirrer must mix faster than oxygen is used | Gas does the mixing; no measured mixing time for animal cells found | As a stirred tank | Flow through the bed at 1-2 cm/s (Pall, full) | Flow in the fibres |
| What caps the density | O2, CO2, mixing, thickness (258 g/L) | As a stirred tank, with the taller shape | As a stirred tank | Room on the carriers: 490,000 Vero cells per cm2 in 6.9 days (Pall, full), 113 g/L of unit at 3 ng a cell | Room between fibres: 2.14e9 HEK cells in a 0.48 L Quantum circuit (part), 13 g/L |
| Largest unit with animal cells | about 25 m3 (pharma); 20 m3 for food (Vow) | 2 m3 published (Lonza, full); 10 m3 claimed; 1.25 m3 for cultivated meat (Ark, unpublished). Non-animal: Quorn 155 m3, continuous | 5 m3 single-use stirred (WuXi has installed them); rocking bags stop at 500 L | iCELLis 500: 500 m2 in 59-71 L; 660 m2 run (full) | Terumo Quantum, 2.1 m2 |
| Cost per unit against a stirred vessel | 1 | 0.8 (0.5-1.0) [assumed]: no stirrer, but a taller shell and a compressor. A Quorn cost model and Humbird's plant scaled to 155 m3 agree at about $270k/m3, i.e. near 1 | 0.5 (0.4-1.0) for the frame [vendor claim], plus a bag each run at $20 per litre (5-30) [assumed: no price found] | 1.0 (0.3-1.5) of Humbird's $0.8M packaged vessel [assumed: no price found], plus a bed each run at about $10,000 (2,000-30,000) [assumed] | 0.035 (0.02-0.1): a Quantum lists at about EUR 25,000 (snippet), plus a set each run at about $3,000 [assumed] |

Only the bioreactor share of the plant (32%, Humbird) changes with the vessel. The rest of the plant (buildings, utilities,
seed train) is priced per m3 as for 20 m3 tanks. That flatters vessels made of many small units.

## 3. The modes: what each one does in the model

| | What happens | Cycle or run | What caps the density | Medium per kg | What a loss costs |
|---|---|---|---|---|---|
| Batch | Fill, grow, empty; all the food in the first fill | 2 doublings from the seed + 10 h (Humbird's fed-batch cycle) | The food in one fill: 25 g/L (12-45) [assumed from CHO batch peaks of about 1e7 cells/mL] | 1000 / density | The cycle's cells and 2 extra days |
| Fed-batch | As batch, feeding concentrate | As batch | Waste build-up and "other waste and spent food" (the least medium a cell needs) | 1000 / density | As batch |
| Fill-and-draw | Half drained and refilled each cycle; never emptied | 33-day runs; the culture averages 72% of its cap | As fed-batch | 1000 / density | A tankful and the scenario's restart |
| Chemostat | Medium in and culture out all the time | 33-day runs; dilution at 0.6 of the top growth rate (0.4-0.9) | As fed-batch, at the slower growth rate | 1000 / density | As fill-and-draw |
| Perfusion | Medium through, cells held back, cells bled off | 33-day runs (Humbird) | O2, CO2, mixing, thickness: waste is washed out | Set by washing out ammonia and lactate | As fill-and-draw |

Details:

- **Retention device for perfusion.** The model keeps its existing assumption: a device at the price one design study hopes for
  (Pasitka 2024's "large-scale PD", $89k per m3 of tank). Nothing holds cells back at 20 m3 today. Pasitka's own supplementary costs
  imply $35k per m3 for TFF and $350k per m3 for ATF filters (secondary). Humbird's ATF filters cost about $460k per m3.
- **Chemostat.** A chemostat must run below the top growth rate, or the culture washes out. A HeLa chemostat gave the most cells
  per hour at about 0.6 of the washout rate (Korean J. Biotechnol. 1989, abstract); mouse LS cells peaked at 0.30-0.35 per day.
  The model builds the chemostat's cells with a doubling time 1/0.6 times longer, so their upkeep, waste and least medium flow
  follow from the same rules as for slow cells. No animal-cell chemostat above about 1 litre was found.
- **Batch.** Real batch cultures start thinner: a model of a 20 m3 batch train (Brenner et al. 2026, Front. Nutr., part) seeds the
  last stage at 2% of its final density, 5.6 doublings. The model keeps Humbird's 2 doublings for batch and fed-batch, so that
  the two differ only in what caps the density. This flatters batch.
- **Losses.** The scenario's chance of losing a run per day applies to every mode. A short batch cycle is less exposed, and the
  next seed is ready, so a lost cycle adds `vm_restart_cycle_days` (2 days, range 1-14). A continuous run keeps the scenario's
  restart (14 days in the central scenario), because the tank must be regrown to its density. No source gives contamination rates
  by mode at production scale (operating_modes.md, section 3c). If contamination comes per start, not per day, batch loses more.
- **Vessels whose cells sit on a support** (packed bed, hollow fibre) cannot run fill-and-draw or a chemostat: there is no free
  culture to draw off. Their medium is pumped round from a separate tank, so a batch is that tank filled once. Topping it up is the
  same run, so fed-batch is not a separate mode. In perfusion the bed is still grown and emptied in cycles: 6.6 doublings from a
  seed of 5,000 cells per cm2 and 3 days to harvest and set up (Pall, full; turnaround assumed). Detaching gives back 90% of the
  cells (assumed: no fixed-bed figure found).

## 4. Results

### Reference case (the stirred tank in perfusion is $11.48)

| vessel (unit size) | Batch | Fed-batch | Fill-and-draw | Chemostat | Perfusion |
|---|---|---|---|---|---|
| Stirred tank (20 m3) | **$62.95** (25 g/L, the food in one fill; done at this size) | **$18.20** (92 g/L, other waste and spent food; done at this size) | **$17.81** (92 g/L, other waste and spent food; done at this size) | **$33.67** (55 g/L, other waste and spent food; only done smaller) | **$11.48** (120 g/L, clearing CO₂; only done smaller) |
| Airlift (bubble column) (20 m3) | **$59.97** (25 g/L, the food in one fill; only done smaller) | **$20.03** (79 g/L, clearing CO₂; only done smaller) | **$19.59** (79 g/L, clearing CO₂; never done with animal cells) | **$32.10** (55 g/L, other waste and spent food; never done with animal cells) | **$15.17** (79 g/L, clearing CO₂; never done with animal cells) |
| Single-use bag (5 m3) | **$1,078** (25 g/L, the food in one fill; done at this size) | **$292.80** (92 g/L, other waste and spent food; done at this size) | **$38.18** (92 g/L, other waste and spent food; only done smaller) | **$74.50** (55 g/L, other waste and spent food; only done smaller) | **$15.46** (190 g/L, clearing CO₂; only done smaller) |
| Packed bed (0.065 m3) | **$3,730** (113 g/L, room on the carriers; done at this size) | as batch | not possible | not possible | **$3,726** (113 g/L, room on the carriers; done at this size) |
| Hollow fibres (0.00048 m3) | **$610,043** (13 g/L, room between the fibres; done at this size) | as batch | not possible | not possible | **$610,039** (13 g/L, room between the fibres; done at this size) |

### Central scenario (the stirred tank in perfusion is $18.14)

| vessel (unit size) | Batch | Fed-batch | Fill-and-draw | Chemostat | Perfusion |
|---|---|---|---|---|---|
| Stirred tank (20 m3) | **$109.07** (25 g/L, the food in one fill; done at this size) | **$45.29** (62 g/L, other waste and spent food; done at this size) | **$48.95** (62 g/L, other waste and spent food; done at this size) | **$96.32** (37 g/L, other waste and spent food; only done smaller) | **$18.14** (258 g/L, how thick the culture can be; only done smaller) |
| Airlift (bubble column) (20 m3) | **$92.55** (25 g/L, the food in one fill; only done smaller) | **$39.09** (62 g/L, other waste and spent food; only done smaller) | **$42.16** (62 g/L, other waste and spent food; never done with animal cells) | **$81.38** (37 g/L, other waste and spent food; never done with animal cells) | **$38.69** (57 g/L, clearing CO₂; never done with animal cells; with no tricks, $17.15 if the loop passed) |
| Single-use bag (5 m3) | **$1,154** (25 g/L, the food in one fill; done at this size) | **$469.40** (62 g/L, other waste and spent food; done at this size) | **$97.88** (62 g/L, other waste and spent food; only done smaller) | **$195.83** (37 g/L, other waste and spent food; only done smaller) | **$40.11** (138 g/L, clearing CO₂; only done smaller) |
| Packed bed (0.065 m3) | **$5,178** (113 g/L, room on the carriers; done at this size) | as batch | not possible | not possible | **$5,174** (113 g/L, room on the carriers; done at this size) |
| Hollow fibres (0.00048 m3) | **$685,153** (13 g/L, room between the fibres; done at this size) | as batch | not possible | not possible | **$685,149** (13 g/L, room between the fibres; done at this size) |

Tags: "done at this size" means animal cells have been grown this way at this unit size, for any product. The tag is about
the vessel, the mode and the size. It does not say that anyone has reached the density in the cell. In both grids, the stirred
tank in fed-batch and fill-and-draw, the bag in fed-batch and the packed bed (vaccine cells) carry the tag at densities above
27 g/L. The densest meat-cell culture reported in a vessel of 1 m3 or more is Vow's 538 kg harvest from a 20,000 L tank, about
27 g/L if the tank was full (`vm_x_meat_shown`; a poorly sourced 68 g/L is the top of its range). The page marks those cells
"This density is not shown for meat cells". Only Vow's stirred tank
grows cells for food at 20 m3. "Only done smaller" means animal cells have been grown this way only in smaller vessels. "Never done
with animal cells" means no record was found.

## 5. What the grid says

1. **Perfusion in a stirred tank is the cheapest combination in both settings.** It costs $11.48 in the reference case and $18.14 in
   the central scenario. Nobody has run animal cells in perfusion above about 4 m3 (Genzyme's 4,000 L tanks at Geel). We put 2-3% on
   anyone having run it at 20 m3 for a month (operating_modes.md, section 5e).
2. **The modes that run at 20 m3 today cost more.** Fed-batch and fill-and-draw cost about $18 in the reference case. In the central
   scenario they cost $45-49. The gap grows because the central cells make more ammonia: without washing it out, the culture stops
   at 62 g/L instead of 92. These costs assume 62-92 g of cells a litre. Nobody has shown that density for meat cells at this
   size. The one 20 m3 plant for meat cells reports harvests of about 27 g/L. So $18.20 is not a demonstrated cost.
3. **A chemostat costs more than fill-and-draw** ($33.67 against $17.81 in the reference case). It must run below the top growth
   rate, and the least medium a cell needs then caps the density lower.
4. **Batch is the dearest stirred-tank mode.** One fill of medium feeds only a thin culture ($62.95), and the unspent medium leaves with
   the cells.
5. **An airlift costs about what a stirred tank costs when waste is not washed out.** In perfusion it costs more ($15.17 against
   $11.48), because its taller shape passes less gas per litre and clears less CO2. In the central scenario, the column loop runs
   17% over the pH-safe dose in the taller tank. The grid then uses the cheapest trick setting that passes, which is none ($38.69). If
   the loop were allowed, the airlift would cost $17.15.
6. **A single-use bag pays for a new bag every run.** That makes it close to a stirred tank only in perfusion ($15.46), where a run
   lasts a month. In two-day batch cycles the bags alone cost hundreds of dollars a kilo. At a 10-14-day pharma fed-batch the bag cost
   per kilo would be about 5 times lower, still far above a steel tank.
7. **Packed beds and hollow fibres are not a route to cheap cells.** Built as they exist (65 litres and half a litre a unit), they
   cost thousands and hundreds of thousands of dollars a kilo. Even a 20 m3 bed priced like a stirred tank, with carriers that cost
   nothing, every cell recovered and a stirred tank's crew, costs $42.19 in the reference case (`vessels.what_if_bed`), against $11.48
   in perfusion. The bed is seeded thin and emptied every run, so it makes 4.3 tonnes per m3 a year against 22.1. Ever After Foods
   claims 286-400 g/L of cells plus edible scaffold in a packed bed; at 258 g/L the same best case costs about $20. That claim is
   unpublished and counts the scaffold.

## 6. What Pablo should check

- **Bag and bed prices.** No vendor or published price was found for a 5,000 L bag, an iCELLis 500 bed, a fixed-bed unit or a Quantum
  set. The rows for these vessels rest on assumed prices (ranges in `inputs.py`). The conclusions hold across those ranges: the packed
  bed's best case without any consumable is still $42.
- **Airlift oxygen transfer.** The airlift's oxygen transfer is set equal to the stirred tank's (0.7-1.2). That rests on one correlation
  for air and water. No measurement in an animal-cell airlift above 1 m3 was found. The airlift's result is driven by CO2 and its tall
  shape, not by oxygen, unless the multiplier falls below about 0.4.
- **Airlift shape** (liquid 3 times as deep as wide, 2-8). A squatter airlift clears more CO2 but circulates less well.
- **Batch density** (25 g/L) is a textbook CHO figure, not found in a primary source in this pass.
- **Chemostat dilution** (0.6 of the top growth rate) rests on one HeLa abstract and one mouse-cell paper.
- **Loss rates by mode.** The grid applies the same chance of loss per day to every mode. No source compares modes.
- **Unit sizes.** Every vessel is priced at its largest unit. A packed bed or hollow-fibre unit built for food at a larger size does
  not exist; section 5, point 7, prices the most favourable version.

## 7. Not modelled

- A rocking bag (500 L at most; 0.6-4 mmol O2/L/h in air) as its own row: the single-use stirred bag stands in for single-use vessels.
- Microcarriers in a stirred tank (the stirred tank's physics with a surface cap); aggregates; edible-scaffold beds.
- Cell age and genetic drift ending long runs; fouling of retention devices; cells lost through the device (no figure found).
- Medium recycling, and a perfusion N-1 seed that would let fed-batch start denser.

## 8. Cultivated-meat bioreactor progress, 2025-2026 (new since the repo's continuous-harvest notes)

From `operating_modes.md`, section 7 (company claims and trade press unless marked):
- Meatly plans a 20,000 L pilot in London (Food Manufacture, May 2026).
- Orbillion Bio and Solar Biotech plan 20,000 L.
- Organoid Farm (Japan) ran a 200 L scaffold-free beef trial (May 2026).
- Magic Valley (Australia) runs 3,000 L bioreactors.
- Ever After Foods and Roslin Technologies claim up to 19 times the productivity of a stirred tank in an edible packed bed (2026).
- Mission Barns reports more than 100 runs of its adherent pilot.
- Brenner et al. 2026 (Front. Nutr., part) is a peer-reviewed full-process model of a batch train to 20 m3. It gives 30.7 days from a
  frozen vial to a 20 m3 batch.
- No peer-reviewed report of cultivated-meat culture at 100 L or above was found. Vow remains the only producer known to run 20 m3.
