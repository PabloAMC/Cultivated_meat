# Cheaper ways to hold the cells back

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> **Current figures (2026-11-21, second batch; `python retention.py`).** The low-lactate example now runs at 168 g/L ($48.68
> with the TFF loop), the all-favourable example at 219 g/L ($6.97), Humbird's optimistic design at 120 g/L ($15.72). With the
> three alternatives, in that order: reused pharma modules $30.54 / $7.76 / $14.22; dialyser-grade fibres $26.28 / $6.97 /
> $13.86; ceramic run as a slow TFF loop $27.75 / $7.29 / $14.01. The body below gives the figures of the morning of 2026-11-21
> (the low-lactate example $49.50, the all-favourable example $7.62).

> Figures recomputed 2026-11-21 on the model of 2026-11-20 (lactate tolerated 35 mmol/L, cells killed by bursting bubbles, a 2%
> harvest loss, twice the fed-batch crew in perfusion, membrane life 2,415 L/m² in place of 3,960, medium-preparation capital,
> utilities in four parts, plant items charged per tank, thick cultures taking up oxygen more slowly, the bleed carrying the
> cells grown). Earlier repins: 2026-11-19 (nutrient floor $2.00, growth factors inside complete media prices; audit batch:
> ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance), 2026-11-16 (bubble protectant,
> antifoam, dissolved oxygen at half of air saturation).

Research date: 2026-11-15. Code: `retention.py` (devices `reuse`, `dialyser`, `ceramic`); inputs `rt_reuse_*`, `rt_dial_*`,
`rt_ceramic_*` in `inputs.py`. The full research report, with every source and its access level, is in
`retention_alternatives_sources/reusable_membranes.md`. Most numbers there come from search-result snippets, not pages read in
full, and the report marks each one. No price comes from a quote. Costs are 2025 dollars per kg of wet cells harvested.

## 1. The question

After `retention_devices.md`, the model prices perfusion's retention as a TFF hollow-fibre loop. Its hardware is cheap. Its
membranes are not: $1,450 per m², replaced after 2,415 litres (Humbird's own replacement schedule), about $0.60 per litre of
permeate, and $0.70 in the low-lactate example once the membranes thrown away with lost runs are counted. In the low-lactate
example that is $22.28 of the $49.50 a kilo. Could membranes from other industries cut the cost per litre?

Prices differ enormously. The same polymers cost $3 to $150 per m² in dialysers and wastewater plants. The model's $1,450 is a
price for small pharma volumes, not a floor set by materials. What decides the answer is how long a membrane lasts with cells at
15–25% of the volume, and nobody has measured that for any of these.

## 2. Results

The low-lactate example: the culture at 154 g/L (15% cells by volume), 1.32 m³/h of permeate (32 litres a kilo). The default TFF
loop costs $49.50.

| Route | Membrane price | Membrane life | Low-lactate example $/kg (range) | Reference / all-favourable example | What has been shown |
|---|---|---|---|---|---|
| Reused pharma modules | $1,450/m² | 12,000 L/m² (first run + 4 reuses) | **31.70** (29.36–35.99) | 14.43 / 8.15 | no reuse data with animal cells; steam limits a module to about 10 cycles |
| Dialyser-grade hollow fibres, replaced often | $8/m² (3–14) | 1,000 L/m² (240–2,000) | **27.52** (27.06–30.06) | 14.07 / 7.62 | whole blood at 32–40% cells by volume, for hours; nothing with animal cells |
| Ceramic membranes, run as a slow TFF loop | $1,500/m² (500–3,000) | 40,000 L/m² (15,000–200,000) | **28.97** (27.16–38.99) | 14.21 / 7.84 | nothing with animal cells; beyond the density any filter has held |
| Wastewater membrane bioreactor | $11–150/m² | 10–16 years | not costed | | it cannot be steamed, is built for a quarter of the solids, and needs coarse bubbles in the culture |
| Food and beverage hollow fibres | not found | 6–8 years in wine | not costed | | sanitised, not sterilised; fluids with under 1% solids |

The ranges move each route's own inputs together to their favourable and unfavourable ends. Reused modules and dialysers are
thrown away with a lost run, so their life is cut by the same share as the default loop's (85% in the low-lactate example). Ceramic
elements are cleaned and kept. With the TFF loop Humbird's optimistic design costs $15.93 and the all-favourable example $7.62; the
all-favourable example's loop already uses dialyser-grade fibres, so the dialyser row equals it there.

- **Each alternative saves $18 to $22 a kilo in the low-lactate example**, because the loop's membranes, replaced after 2,415 L/m²,
  are 45% of its cost. The order is dialyser ($27.52) < ceramic ($28.97) < reused modules ($31.70) < TFF loop ($49.50) < ATF
  ($66.60).
- **Dialysers lead.** They cost $3–14 per m², are sterilised by steam or gamma rays, and are the only mass-made membrane found
  that routinely filters a fluid as thick as the low-lactate example. Their flux is lower (2.5 L/m²/h), so the low-lactate
  example needs about 530 m², roughly 290 dialysers in parallel. Their hardware is therefore a larger cost than their fibre: $0.5k
  per m² for manifolds, connections and pumps, which is an assumption.
- **The catches are real.** A dialyser's fibre bore is 185 µm, 11 cell diameters, so clumps of cells could plug it. Dialysers
  hold back albumin and most growth factors, so a protein in the feed would build up to about 5 times its feed level in the
  low-lactate example (39 litres of medium a kilo, of which the bleed carries 7) unless it is fed only at the rate the bleed
  removes it. That could also be an opening: it would cut the protein used per kilo. It has not been tested.
- **Ceramic is cheaper per litre than pharma but needs a plant around it.** Its elements are rated for years in dairies. A
  stainless housing, a cleaning skid and a spare bank add $3k per m² (assumed), which makes its capital $73k per m³ of tank in
  the low-lactate example. It works only if cleaning in place restores the flux after animal cells foul it. Dairies run it at several
  metres a second across the membrane, which would put about 25 times the shear of an ATF filter on the cells, so it must run
  slowly like a TFF loop.
- **Reuse is the easiest and the weakest.** It keeps the validated module and its sterility, but gives only 2 to 4 times, and one
  patent saw reuse life fall to 30–40% of the first.

## 3. Probabilities

Each figure below is a rough judgement made while building the model with an AI assistant from the research pass; not measured
and not reviewed by an expert. The reasoning is in the research report. A dated snapshot (2026-11-15/16, not re-judged since):
each row names its own price or share of cells by volume, so it does not depend on the density the examples now run at.

| Statement | Probability (the model's rough judgement) |
|---|---|
| The low-lactate example gets membranes at $0.060 per litre or less (a tenth of the model's $0.60) | about 15% |
| Humbird's optimistic design gets the same | about 40% |
| Dialyser or plasma-separator arrays hold the culture for 33 days: at 12% cells by volume / at 25% | 30% / 15% |
| Ceramic run as a slow TFF loop holds 25% and recovers 80% of its flux for 10 runs | 15% |
| Ceramic at the dairy flow keeps 90% of the cells alive | 5% |
| A submerged wastewater module works in a 33-day sterile culture | 5% |
| Reusing pharma modules gives a tenfold cut | 5% |

## 4. What this means

1. **The price of membranes is not the obstacle; their life is.** At $14 per m², a tenfold saving needs only about 230 litres per
   m² of life, 2 days at 5 litres per m² an hour. The pharma membranes in Veje 2024 lasted 900 litres per m² (4.5 days) before
   they fouled. No one has measured any of these routes with a culture this thick for a month.
2. **If membranes did that, the low-lactate example would fall from $49.50 to about $29.5.** That is near the $27.97 of the
   hoped-for device that assumed retention was free of membranes, but it rests on a judgement of about 15%, and it leaves out
   extra capital that reusable systems need and that could not be priced.
3. **The experiment that would settle it:** run dialyser fibres and a ceramic element on a small perfusion culture of a meat cell
   line at 10–25% cells by volume for 33 days. Measure flux against time, cells lost, and flux recovered after cleaning. This is
   a bench experiment and would cost far less than a pilot tank.

## 5. Not found

- Any animal-cell perfusion on ceramic, wastewater, dialyser or plasma-separator membranes.
- Prices per m² for food hollow fibres and plasma separators, and for sterilisable ceramic or stainless housings.
- Flux recovered after cleaning animal-cell fouling off any of them.
- Dialysis with a cleaned dialysate, and cells held back without a filter (clumps, edible carriers, gel beads) were not researched
  in this pass. Clumps and edible carriers were researched on 2026-11-19 (`retention_aggregates.md`); dialysis and gel beads
  remain open.
