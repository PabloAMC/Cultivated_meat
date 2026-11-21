# Vessel types and operating modes

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> 2026-11-19 (scenario restructure): a tank that is not washed out is capped by the waste mass balance (section 10); the central
> grid's fed-batch, fill-and-draw and chemostat columns are recomputed. Upside Foods' report is in section 11.

> Repinned 2026-11-20, final pass (the airlift held to the stirred tank's mixing rule at its own shape; per-tank plant items; a vessel's recovery applied to every cost; the bubble cage charged bubble deaths only on the gas the cells meet): the two grids of section 4 are regenerated from `vessels.markdown_table`, and sections 1, 5, 6, 9, 10 and 11 are rewritten to them. Changed conclusions: the airlift is now held by mixing (45 g/L in the reference case, 87 g/L in the low-lactate example) and costs more than the stirred tank in perfusion in both settings ($30.48 against $15.93, $53.11 against $49.50); before this pass it was held by CO2 removal and was cheaper in the low-lactate example. The bubble cage is now cheaper than the plain tank in perfusion in both settings, and the open point of section 9 is closed. Hollow fibres cost about three times more than before, because each half-litre unit now brings its own plant items.

> Repinned 2026-11-20 (model batch: lactate tolerance 35 mmol/L in the scenarios, cells killed by bursting bubbles, a 2% harvest loss, twice the fed-batch crew in perfusion, membrane life 2,415 L/m2, medium preparation capital that scales with the medium passed, utilities in four parts): the two grids of section 4, section 5, the cage's results in section 3 and the densities of sections 10 and 11 are recomputed. Changed conclusions: in the low-lactate example the airlift in perfusion is now cheaper than the stirred tank and the bubble cage dearer (section 5, point 5; the cage paragraph). Figures in the other sections are as they were on 2026-11-19.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.

> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.

> **Updated 2026-11-15 (late), second time.** The grids and the figures in section 5 are recomputed with the model as it now stands:
> the hollow-fibre filter loop in perfusion (`retention.py`), the bubble protectant in every sparged vessel (packed beds and hollow
> fibres are not sparged), and antifoam's quarter cut to the sparger's oxygen. Earlier versions are in git history.

Research date: 2026-11-15; updated 2026-11-20. Code: `vessels.py` (grid), `floor_physics.explore(vm=...)` (the physics), `page_vessels.js` (the page's
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

- **the reference case**: `floor_physics.explore()` at its defaults (cells that make almost no ammonia or lactate, doubling every 24 h, a food-grade plant
  without clean rooms, no tank tricks, no losses). The stirred tank in perfusion gives $15.93.
- **the low-lactate example** (`scenarios.py`, `central`): cells that make less lactate (0.42) on a low-waste feed, doubling every 36 h, a food-grade plant, gas
  at up to 4 mm/s, the column with 1 bar of pressure, a tank as deep as wide, 1% of runs lost a day, a 14-day restart,
  medium at $0.20 a litre with the growth factors in its price, dissolved oxygen held at half of air saturation, ammonia held to 4 mmol/L and lactate to 35 mmol/L, glucose from the cells' own balance. The stirred tank in perfusion gives $49.50.

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
| Fed-batch | As batch, feeding concentrate | As batch | Waste build-up (ammonia or lactate, whichever is further above the level of cells that make almost no ammonia or lactate) and "other waste and spent food" (the least medium a cell needs) | 1000 / density | As batch |
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
  restart (14 days in the low-lactate example), because the tank must be regrown to its density. No source gives contamination rates
  by mode at production scale (operating_modes.md, section 3c). If contamination comes per start, not per day, batch loses more.
- **Vessels whose cells sit on a support** (packed bed, hollow fibre) cannot run fill-and-draw or a chemostat: there is no free
  culture to draw off. Their medium is pumped round from a separate tank, so a batch is that tank filled once. Topping it up is the
  same run, so fed-batch is not a separate mode. In perfusion the bed is still grown and emptied in cycles: 6.6 doublings from a
  seed of 5,000 cells per cm2 and 3 days to harvest and set up (Pall, full; turnaround assumed). Detaching gives back 90% of the
  cells (assumed: no fixed-bed figure found).

## 4. Results

### Reference case (the stirred tank in perfusion is $15.93)

| vessel (unit size) | Batch | Fed-batch | Fill-and-draw | Chemostat | Perfusion |
|---|---|---|---|---|---|
| Stirred tank (20 m3) | **$71.88** (25 g/L, the food in one fill; done at this size) | **$21.10** (92 g/L, other waste and spent food; done at this size; this density is not shown for meat cells) | **$19.98** (92 g/L, other waste and spent food; done at this size; this density is not shown for meat cells) | **$37.43** (55 g/L, other waste and spent food; only done smaller) | **$15.93** (120 g/L, clearing CO₂; only done smaller) |
| Stirred tank with a bubble cage (20 m3) | **$73.42** (25 g/L, the food in one fill; only done smaller) | **$21.20** (92 g/L, other waste and spent food; only done smaller) | **$20.09** (92 g/L, other waste and spent food; never done with animal cells) | **$37.88** (55 g/L, other waste and spent food; never done with animal cells) | **$14.84** (176 g/L, getting oxygen in; never done with animal cells) |
| Airlift (bubble column) (20 m3) | **$69.30** (25 g/L, the food in one fill; only done smaller) | **$39.14** (45 g/L, mixing; only done smaller) | **$36.96** (45 g/L, mixing; never done with animal cells) | **$35.96** (55 g/L, other waste and spent food; never done with animal cells) | **$30.48** (45 g/L, mixing; never done with animal cells) |
| Single-use bag (5 m3) | **$1,154** (25 g/L, the food in one fill; done at this size) | **$337.33** (92 g/L, other waste and spent food; done at this size; this density is not shown for meat cells) | **$48.75** (92 g/L, other waste and spent food; only done smaller) | **$93.73** (55 g/L, other waste and spent food; only done smaller) | **$33.58** (121 g/L, getting oxygen in; only done smaller) |
| Packed bed (0.065 m3) | **$3,609** (113 g/L, room on the carriers; done at this size; this density is not shown for meat cells) | as batch | not possible | not possible | **$3,603** (113 g/L, room on the carriers; done at this size; this density is not shown for meat cells) |
| Hollow fibres (0.00048 m3) | **$1,824,438** (13 g/L, room between the fibres; done at this size) | as batch | not possible | not possible | **$1,824,433** (13 g/L, room between the fibres; done at this size) |

### The low-lactate example (the stirred tank in perfusion is $49.50)

| vessel (unit size) | Batch | Fed-batch | Fill-and-draw | Chemostat | Perfusion |
|---|---|---|---|---|---|
| Stirred tank (20 m3) | **$104.11** (25 g/L, the food in one fill; done at this size) | **$71.76** (37 g/L, waste building up; done at this size; this density is not shown for meat cells) | **$76.35** (37 g/L, waste building up; done at this size; this density is not shown for meat cells) | **$126.49** (26 g/L, waste building up; only done smaller) | **$49.50** (154 g/L, getting oxygen in; only done smaller) |
| Stirred tank with a bubble cage (20 m3) | **$105.66** (25 g/L, the food in one fill; only done smaller) | **$72.35** (37 g/L, waste building up; only done smaller) | **$77.05** (37 g/L, waste building up; never done with animal cells) | **$127.76** (26 g/L, waste building up; never done with animal cells) | **$46.51** (246 g/L, getting oxygen in; never done with animal cells) |
| Airlift (bubble column) (20 m3) | **$100.24** (25 g/L, the food in one fill; only done smaller) | **$69.11** (37 g/L, waste building up; only done smaller) | **$73.42** (37 g/L, waste building up; never done with animal cells) | **$121.51** (26 g/L, waste building up; never done with animal cells) | **$53.11** (87 g/L, mixing; never done with animal cells) |
| Single-use bag (5 m3) | **$1,243** (25 g/L, the food in one fill; done at this size) | **$850.26** (37 g/L, waste building up; done at this size; this density is not shown for meat cells) | **$194.20** (37 g/L, waste building up; only done smaller) | **$327.06** (26 g/L, waste building up; only done smaller) | **$88.93** (107 g/L, getting oxygen in; only done smaller) |
| Packed bed (0.065 m3) | **$4,969** (113 g/L, room on the carriers; done at this size; this density is not shown for meat cells) | as batch | not possible | not possible | **$4,968** (113 g/L, room on the carriers; done at this size; this density is not shown for meat cells) |
| Hollow fibres (0.00048 m3) | **$2,326,368** (13 g/L, room between the fibres; done at this size) | as batch | not possible | not possible | **$2,326,366** (13 g/L, room between the fibres; done at this size) |

Tags: "done at this size" means animal cells have been grown this way at this unit size, for any product. The tag is about
the vessel, the mode and the size. It does not say that anyone has reached the density in the cell. In both grids, the stirred
tank in fed-batch and fill-and-draw, the bag in fed-batch and the packed bed (vaccine cells) carry the tag at densities above
27 g/L. The densest meat-cell culture reported in a vessel of 1 m3 or more is Vow's 538 kg harvest from a 20,000 L tank, about
27 g/L if the tank was full (`vm_x_meat_shown`; a poorly sourced 68 g/L is the top of its range). The page marks those cells
"This density is not shown for meat cells". Only Vow's stirred tank
grows cells for food at 20 m3. "Only done smaller" means animal cells have been grown this way only in smaller vessels. "Never done
with animal cells" means no record was found.

## 5. What the grid says

1. **Perfusion is the cheapest mode in every stirred or bubbled vessel, in both settings.** The stirred tank in perfusion costs
   $15.93 in the reference case and $49.50 in the low-lactate example. One combination that nobody has run costs less in both: the
   stirred tank with a bubble cage ($14.84 and $46.51, section 9). Nobody has run animal cells in perfusion above about 4 m3
   (Genzyme's 4,000 L tanks at Geel; operating_modes.md, section 5e). A rough judgement made while building the model with an AI
   assistant, not measured and not reviewed by an expert: 2-3% that anyone has run it at 20 m3 for a month, because no paper, filing
   or vendor note found describes a cell-retention device at that size.
2. **The modes that run at 20 m3 today cost more.** Fed-batch and fill-and-draw cost $21.10 and $19.98 in the reference case. In the
   low-lactate example they cost $71.76 and $76.35 (with the perfusion tank's design held; `no_perfusion_downside.md` chooses it again).
   Since the 2026-11-19 mass balance (section 10) a batch of the low-lactate example's cells stops at 37 g/L: 1.3 times the 4 mmol/L of
   ammonia perfusion is held to, at 0.14 mol a kilo. The reference case's batch is held at 92 g/L by other by-products. These costs
   assume 37-92 g of cells a litre. The one 20 m3 plant for meat cells reports harvests of about 27 g/L, and Upside's capacity implies
   33-136 g/L (section 11). So $21.10 is not a demonstrated cost.
3. **A chemostat costs more than fill-and-draw** ($37.43 against $19.98 in the reference case). It must run below the top growth
   rate, and the least medium a cell needs then caps the density lower. It also sits at its density all the time, so since
   2026-11-19 it is held to the steady-state waste level itself, with no end-of-batch allowance (26 g/L in the low-lactate example,
   held by lactate at 35 mmol/L since 2026-11-20; 29 g/L before, held by ammonia).
4. **Batch is the dearest stirred-tank mode.** One fill of medium feeds only a thin culture ($71.88), and the unspent medium leaves with
   the cells.
5. **An airlift is held by mixing, and costs more than a stirred tank unless waste holds both thinner.** Since 2026-11-20 the
   airlift follows the stirred tank's mixing rule at its own tall shape (3 times as deep as wide): its rising gas gives about the
   power per litre a stirrer gives (39-59 W/m3 at 4-6 mm/s, against the stirrer's 43), and no mixing time has been measured in an
   animal-cell airlift above 2 m3. A stirred tank of the same shape is held at the same density. In the reference case that is
   45 g/L, against the stirred tank's 120 g/L held by CO2: fed-batch costs $39.14 against $21.10, and perfusion $30.48 against $15.93.
   At 45 g/L each m3 makes 42% fewer kilos, so every line per kilo rises (in fed-batch: the plant $15.03 to $25.70, labour $2.97 to
   $5.08, the medium $2.16 to $3.50 at 23.3 litres a kilo), against $23.18 for fed-batch and $18.12 for perfusion with the old
   exemption and the model's other changes. In the low-lactate example waste holds an unwashed tank at 37 g/L, below the mixing
   limit, so the airlift's fed-batch costs a little less than the stirred tank's ($69.11 against $71.76: its vessel is priced at 0.8
   of a stirred one). In perfusion mixing holds it at 87 g/L: $53.11 against $49.50. **Changed 2026-11-20 (final pass):** before,
   the airlift had no mixing limit, was held by CO2 (79 g/L) and, in the low-lactate example, by the column's checks (139 g/L with
   the culture run thinner, $47.60), which made it cheaper than the stirred tank there. Held at 87 g/L, the column loop passes its
   checks with the example's own tricks. The result moves steeply with the airlift's shape (section 6), and nobody has run animal
   cells in an airlift in perfusion.
6. **A single-use bag pays for a new bag every run.** That makes it closest to a stirred tank in perfusion ($33.58), where a run
   lasts a month. In two-day batch cycles the bags alone cost hundreds of dollars a kilo. At a 10-14-day pharma fed-batch the bag cost
   per kilo would be about 5 times lower, still far above a steel tank.
7. **Packed beds and hollow fibres are not a route to cheap cells.** Built as they exist (65 litres and half a litre a unit), they
   cost thousands and about two million dollars a kilo (since 2026-11-20 each small unit brings its own plant items, such as makeup
   tanks and filter housings: `floor_physics.tank_items`). Even a 20 m3 bed priced like a stirred tank, with carriers that cost
   nothing, every cell recovered and a stirred tank's crew, costs $44.05 in the reference case (`vessels.what_if_bed`), against $15.93
   in perfusion. The bed is seeded thin and emptied every run, so it makes 4.2 tonnes per m3 a year against 19.9. Ever After Foods
   claims 286-400 g/L of cells plus edible scaffold in a packed bed; at 258 g/L the same most favourable case costs about $21. That claim is
   unpublished and counts the scaffold.

## 6. What to check

- **Bag and bed prices.** No vendor or published price was found for a 5,000 L bag, an iCELLis 500 bed, a fixed-bed unit or a Quantum
  set. The rows for these vessels rest on assumed prices (ranges in `inputs.py`). The conclusions hold across those ranges: the packed
  bed's most favourable case without any consumable is still $44.
- **Airlift oxygen transfer.** The airlift's oxygen transfer is set equal to the stirred tank's (0.7-1.2). That rests on one correlation
  for air and water. No measurement in an animal-cell airlift above 1 m3 was found. Since 2026-11-20 the airlift's result is set by
  mixing at its tall shape, not by oxygen, unless the multiplier falls below about 0.3 (reference case: $30.48 at 1.0, $30.92 at 0.4,
  $34.07 at 0.3, where oxygen binds).
- **Airlift mixing and shape** (liquid 3 times as deep as wide, 2-8). The airlift is held to the stirred tank's mixing rule at its
  own shape; no mixing time for an animal-cell airlift above 2 m3 was found. Under that rule the cost moves steeply with the shape
  (reference case, perfusion): $15.93 at 2 (held by CO2 at 103 g/L), $30.48 at 3, $94.67 at 5 and $273.68 at 8 (held by mixing at
  45, 14 and 5 g/L). A measured mixing time in a large airlift would settle more of the airlift row than any other input.
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

## 9. A stirred tank with a bubble cage, and other ways to keep bubbles away from cells (added 2026-11-16)

**The design.** Two cylinders, one inside the other. The inner one is a bubble column; the outer ring holds the cells, stirred
gently by impeller blades turning around the inner cylinder, with soft bubbling from the floor. The inner cylinder can bubble hard
because no cells are in it. For the cells to stay out, its wall must pass medium but not cells: a fine mesh. This is **caged
aeration**, a known design: a sparger inside a fine-mesh cage, used with cells on microcarriers in bench and pilot tanks, with
mesh of about 85 µm (a BioProcess International review of impellers, [search summary](https://www.bioprocessintl.com/cell-line-development/which-impeller-is-right-for-your-cell-line-)).
A patent on aeration devices notes that "large scale fine-mesh components" could be very costly to make
([US20130175716A1](https://patents.google.com/patent/US20130175716), search summary). Single cells of 10–20 µm need a mesh finer
than that, which clogs; this was not found at any size.

**In the model** (`vessels.py`, row "Stirred tank with a bubble cage"; inputs `vm_cage_*`). The ring bubbles as the plain tank does at
the scenario's gas setting, so the protectant and its cost stay. The cage adds gas at `vm_cage_gas` (6 mm/s over the tank's
cross-section, 3–12; capped by foam, not by cells), discounted by `vm_cage_exchange` (0.8, 0.5–1) because its oxygen and CO₂ reach
the cells only with the medium that crosses the mesh. Capital 1.15 times a stirred tank (1.05–1.4). Every one of these is a
judgement: no exchange rate across a cage, no 20 m³ cage and no price were found. Results, perfusion (recomputed 2026-11-20, final
pass): reference case $14.84 against $15.93 in the plain tank (176 g/L against 120, oxygen now binds); the low-lactate example $46.51
against $49.50 (246 g/L against 154, oxygen); published cells (rung 1, no tricks) $179.10 against $205.78 (158 g/L against 46). The
cage does not touch the medium: the published cells' litres (146 a kilo at 35 mmol/L of lactate) and their membranes cost the same
with or without it; the denser tank still takes 13% off their cost. **Closed 2026-11-20:** the model had charged the cells killed by
bursting bubbles on all the gas passed, the cage's included (12.6% of the cells in the reference case against 8% in the plain tank),
although the cage's bubbles do not meet the cells. That was a defect: since the final pass the cage's gas exchanges oxygen and CO₂ but
is not charged for bubble deaths (`vm["gas_away"]`), and the cage loses the same 8% as the plain tank.

**Variant: the inner cylinder full of gas, under pressure.** Then the wall must hold liquid out and let gas through: a gas-permeable
membrane, which is membrane aeration. Pressure raises the oxygen driving force (as the model's 1 bar trick does) but does not help
CO₂, which leaves in proportion to the difference between its pressure in the liquid and in the sweep gas. The difficulty is area.
An inner cylinder 0.8 m across in the 20 m³ tank (liquid 3.74 m deep) has about 9.4 m² of wall. Removing the reference case's CO₂
needs roughly 1,200–1,500 m² of membrane at the fluxes reached in blood CO₂-removal devices (`project_review.md`, item B), over 100
times more. Folded membranes or a bundle of hollow fibres in the cylinder would add the area; that is the membrane loop the
gas-exchange study set aside because no membrane was found that is both priced and rated for repeated steaming (`gas_exchange_study.md`, 7.5).

**Other designs that keep bubbles away from cells, or soften them** (search summaries unless a note is named):

| design | how it works | largest scale found | in the model |
|---|---|---|---|
| Caged aeration | sparger inside a fine-mesh cage | bench and pilot, microcarriers | the bubble-cage row (this section) |
| Packed stripping column beside the tank | culture runs down packing as a film; no bubbles | not with animal cells | the "column" tank trick (`gas_exchange_study.md`) |
| Membrane aeration (silicone tubing, hollow fibres, rotating membranes) | gas diffuses through a membrane | 50 L tubular pilot; dynamic membrane aeration to about 200 L | not a row; needs large area (above) |
| Surface aeration: rocking bags, orbitally shaken tanks | gas enters through a moving free surface | rocking bags of tens of litres hold the densest CHO; orbital shakers to about 1–2.5 m³ (vendor) | not a row |
| Airlift, internal or external loop | gas in a riser drives circulation; cells meet the bubbles | 2 m³ with animal cells (Lonza); 155 m³ for fungus (Quorn) | the airlift row |
| Stirred airlift (draft tube plus impeller) | impeller inside or around a draft tube | not found with animal cells at scale | CFD target A5 (`roadmap_2026-11-15.md`) |
| Microspargers and ceramic spargers | many fine bubbles: more oxygen per litre of gas, more foam | common in pharma | not a separate row |
| Oxygen carriers in the medium (perfluorocarbons) | the medium holds more oxygen | lab | not in the model |

## 10. The waste mass balance of a tank that is not washed out (added 2026-11-19, scenario restructure)

**The defect.** In any mode, the litres of medium a kilo of cells leaves with must hold the waste that kilo made, at no more than the
level the cells tolerate: litres per kilo ≥ waste made per kilo / level allowed. In perfusion the model already did this (the
"ammonia" and "lactate" medium terms). A tank that is not washed out leaves with 1000 / density litres a kilo, so its density can be at
most level / waste per kilo (mmol/L divided by mol/kg is g/L). The model instead scaled Humbird's fed-batch figure (120 g/L for his
enhanced cells) by the cells' waste. That let the low-lactate example's fed-batch end at 7.8 mmol/L of ammonia, against the 4 its perfusion is held
to, and seem to need half the medium (18 against 35 L/kg).

**The fix** (`floor_physics.explore`, mirrored in the page's `floorExplore`). The density of a tank that is not washed out is at most

    end factor x min(ammonia limit / ammonia per kilo, lactate room / lactate per kilo)

with the same ammonia limit (4 mmol/L in the scenarios, Humbird's 5 in his design) and the same lactate room (50 mmol/L, or less where
the salt limit binds) as perfusion. A chemostat sits at its density all the time, so its end factor is 1. A batch, or a
fill-and-draw tank at the top of its cycle, may end above the steady-state level, because only its last doublings see it: the end
factor is `pf_batch_end_x`. Above the level the last doublings grow slower (`floor_physics.batch_slowdown`): growth is the switch's
speed up to the level and falls as 1 / (1 + (c / K)^h) above it, with a 10% loss at the level and 50% at K = `pf_batch_half_x` times
it. The other caps on an unwashed tank (other by-products, CO₂, oxygen) are unchanged. `pf_x_unperfused` is kept only for Humbird's
own fed-batch design (the tiers, and the labour per m³ of his fed-batch plant, which sets every case's crew).

**The end factor, 1.3 (range 1.0–2.0).** Humbird's own fed-batch design ends at 1.3 times his perfusion limits: 120 g/L of his
enhanced cells, which make 0.054 mol of ammonia and 0.56 mol of lactate a kilo, hold 6.5 mmol/L of ammonia and 67 mmol/L of lactate
at harvest, against the 5 and 50 he holds perfusion to. A short evidence check, both ways:

- *For a factor above 1.* CHO fed-batch cultures end at 5–15 mmol/L of ammonia and peak at 10–94 mmol/L of lactate (Freund and
  Croughan 2018: 94 in the unadapted line, 10 in the lactate-adapted one; `waste_and_medium_evidence.md`); harm from lactate begins
  near 20–40 mmol/L in CHO (patent and review snippets found this pass). Pig muscle stem cells' growth fell with ammonium but not
  with lactate (Qiu 2026); mouse myoblasts grew faster with 5 mmol/L of lactate added (search snippet). Only the last doubling or so
  sees the end level, and the model charges the slower growth there.
- *Against.* Unadapted meat-relevant cells lose about 10% of their growth at 1–3 mmol/L of ammonia and about 50% at 3–10
  (`ammonia_tolerance_and_filter_life.md`), and the scenarios' 4 mmol/L is already the note's median for meat cells at the level where the loss of growth is small. Meat-cell
  processes hold lactate under 30 mmol/L (Pasitka 2024), below the scenarios' 35 (50 before 2026-11-20); catfish cells slowed 14% at 2.5 mmol/L of lactate.
- *Reading.* 1.3 is Humbird's own implicit choice and sits inside both bodies of evidence. 1.0 (held to the perfusion level) is the
  cautious end; 2.0 is where the last doubling would grow about a quarter slower. The growth loss above the level is charged: at
  1.3 it lengthens a two-doubling batch by 0.6%; at 2.0 by 6%.

**K, 3 (range 2–5).** The ratio of the level that halves growth to the level with a small loss: catfish ovary cells about 0.6 and 3
mmol/L, 3T3 about 1.5 and 8, HFF-1 about 2 and 10 (ratios of 2.5 to 5).

**What it does.** Held to 1.3 times 4 mmol/L, the low-lactate example's cells end a batch at 37 g/L (it was 56; at 1.0 they would stop at
29). The published cells, whose lactate is 4.8 mol a kilo, end at 9.5 g/L, held by lactate at 1.3 times 35 mmol/L (14 g/L before 2026-11-20, at 1.3 times 50). Humbird's enhanced cells are held by
other by-products at 92 g/L, as before, so his design and the reference case do not move.

## 11. What Upside Foods reports (added 2026-11-19)

Source: AgFunderNews, 17 November 2026 (trade press, company statements, as reported). Upside Foods says it has
validated a single-vessel process at 20,000 litres over 18 months, in "multiple 20,000+ liter bioreactors", taking about three weeks
from cells to meat, for a capacity of "more than one million pounds" a year (454 t). It does not say how the tanks are run; a
scientific memo to the FDA is promised. Its product is "a double-digit percentage" cells.

**Arithmetic.** If the 454 t is product with 10–25% cells, from 3 to 5 tanks of 16 m³ of liquid harvested once every three weeks
(17.3 harvests a year), each harvest must hold 33 to 136 g of cells a litre. If the 454 t were cells, a fed-batch would need 326 g/L
even with five tanks, above the 258 g/L at which a culture becomes too thick; one 20 m³ perfusion tank at the low-lactate example's
productivity (14.9 t of cells per m³ a year, 299 t a tank; 18.0 t before 2026-11-20) would make about two thirds of it. The capacity is
almost certainly product. A rough judgement made while building the model with an AI assistant, not measured and not reviewed by an
expert: fed-batch is the more likely way the tanks are run (about 75%), because it is the standard pharma mode at 20 m³, no cell
retention device at that size has been reported, and a three-week cycle from cells to meat fits a batch better than a month-long
perfusion run.

**What it anchors.** Fed-batch at 20 m³ is shown for meat cells, so it is the first rung of the ladder (`scenarios.LADDER`). The
density it implies says something about the cells. In the model the best published meat cells stop a 20 m³ batch at 9.5 g/L, held
by their lactate (1.05 mol per mol of glucose, about 4.8 mol a kilo). Reaching 33 g/L, the bottom of Upside's range, needs a
lactate yield of about 0.48 mol per mol of glucose (at the 35 mmol/L of lactate the scenarios allow since 2026-11-20); the scenarios'
cells that make less lactate (0.42) reach 37 g/L. Vow's reported 27 g/L needs about 0.57. So the two companies that report densities at 20 m³ hold cells that make less lactate than any published meat cell,
or run their batches at higher lactate than the model allows.
