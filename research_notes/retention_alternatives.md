# Cheaper ways to hold the cells back

Research date: 2026-11-15. Code: `retention.py` (devices `reuse`, `dialyser`, `ceramic`); inputs `rt_reuse_*`, `rt_dial_*`,
`rt_ceramic_*` in `inputs.py`. The full research report, with every source and its access level, is in
`retention_alternatives_sources/reusable_membranes.md`. Most numbers there come from search-result snippets, not pages read in
full, and the report marks each one. No price comes from a quote. Costs are 2025 dollars per kg of wet cells.

## 1. The question

After `retention_devices.md`, the model prices perfusion's retention as a TFF hollow-fibre loop. Its hardware is cheap. Its
membranes are not: $1,450 per m², replaced after 3,960 litres, about $0.37 per litre of permeate. In the central case that is
$8.8 of the $26.64 a kilo. Could membranes from other industries cut the cost per litre?

Prices differ enormously. The same polymers cost $3 to $150 per m² in dialysers and wastewater plants. The model's $1,450 is a
price for small pharma volumes, not a floor set by materials. What decides the answer is how long a membrane lasts with cells at
a quarter of the volume, and nobody has measured that for any of these.

## 2. Results

Central case, the culture at 258 g/L, 1.88 m³/h of permeate. The default TFF loop costs $26.64.

| Route | Membrane price | Membrane life | Central $/kg (range) | Reference / best | What has been shown |
|---|---|---|---|---|---|
| Reused pharma modules | $1,450/m² | 12,000 L/m² (first run + 4 reuses) | **20.72** (19.17–23.80) | 11.15 / 7.16 | no reuse data with animal cells; steam limits a module to about 10 cycles |
| Dialyser-grade hollow fibres, replaced often | $8/m² (3–14) | 1,000 L/m² (240–2,000) | **18.00** (17.68–19.73) | 10.83 / 6.34 | whole blood at 32–40% cells by volume, for hours; nothing with animal cells |
| Ceramic membranes, run as a slow TFF loop | $1,500/m² (500–3,000) | 40,000 L/m² (15,000–200,000) | **19.14** (17.76–26.79) | 10.96 / 6.68 | nothing with animal cells; beyond the density any filter has held |
| Wastewater membrane bioreactor | $11–150/m² | 10–16 years | not costed | | it cannot be steamed, is built for a quarter of the solids, and needs coarse bubbles in the culture |
| Food and beverage hollow fibres | not found | 6–8 years in wine | not costed | | sanitised, not sterilised; fluids with under 1% solids |

The ranges move each route's own inputs together to their favourable and unfavourable ends.

- **Dialysers lead.** They cost $3–14 per m², are sterilised by steam or gamma rays, and are the only mass-made membrane found
  that routinely filters a fluid as thick as the central case. Their flux is lower (2.5 L/m²/h), so the central case needs about
  750 m², roughly 420 dialysers in parallel. Their hardware is therefore a larger cost than their fibre: $0.5k per m² for
  manifolds, connections and pumps, which is an assumption.
- **The catches are real.** A dialyser's fibre bore is 185 µm, 11 cell diameters, so clumps of cells could plug it. Dialysers
  hold back albumin and most growth factors, so a protein in the feed would build up to about 7 times its feed level in the
  central case unless it is fed only at the rate the bleed removes it. That could also be an opening: it would cut the
  protein used per kilo. It has not been tested.
- **Ceramic is cheaper per litre than pharma but needs a plant around it.** Its elements are rated for years in dairies. A
  stainless housing, a cleaning skid and a spare bank add $3k per m² (assumed), which makes its capital $104k per m³ of tank in
  the central case. It works only if cleaning in place restores the flux after animal cells foul it. Dairies run it at several
  metres a second across the membrane, which would put about 25 times the shear of an ATF filter on the cells, so it must run
  slowly like a TFF loop.
- **Reuse is the easiest and the weakest.** It keeps the validated module and its sterility, but gives only 2 to 4 times, and one
  patent saw reuse life fall to 30–40% of the first.

## 3. Probabilities (judgement, from the research pass)

| Statement | Probability |
|---|---|
| The central case gets membranes at $0.037 per litre or less (a tenth of today's) | about 15% |
| The reference case gets the same | about 40% |
| Dialyser or plasma-separator arrays hold the culture for 33 days: at 12% cells by volume / at 25% | 30% / 15% |
| Ceramic run as a slow TFF loop holds 25% and recovers 80% of its flux for 10 runs | 15% |
| Ceramic at the dairy flow keeps 90% of the cells alive | 5% |
| A submerged wastewater module works in a 33-day sterile culture | 5% |
| Reusing pharma modules gives a tenfold cut | 5% |

## 4. What this means

1. **The price of membranes is not the obstacle; their life is.** At $14 per m², a tenfold saving needs only about 400 litres per
   m² of life, 3 to 4 days at 5 litres per m² an hour. That is about what the pharma membranes in Veje 2024 reached before they
   fouled. No one has measured any of these routes with a culture this thick for a month.
2. **If membranes did that, Central would fall from $26.64 to about $18 to $19.** That is near the old $18.14 that assumed
   retention was free, but it rests on a 15% chance, and it leaves out extra capital that reusable systems need and that could
   not be priced.
3. **The experiment that would settle it:** run dialyser fibres and a ceramic element on a small perfusion culture of a meat cell
   line at 10–25% cells by volume for 33 days. Measure flux against time, cells lost, and flux recovered after cleaning. This is
   a bench experiment and would cost far less than a pilot tank.

## 5. Not found

- Any animal-cell perfusion on ceramic, wastewater, dialyser or plasma-separator membranes.
- Prices per m² for food hollow fibres and plasma separators, and for sterilisable ceramic or stainless housings.
- Flux recovered after cleaning animal-cell fouling off any of them.
- Dialysis with a cleaned dialysate, and cells held back without a filter (clumps, edible carriers, gel beads) were not researched
  in this pass. They remain open.
