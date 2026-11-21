# Growth-factor prices and the fastest doubling time

Date: 2026-11-15; every figure regenerated 2026-11-20 on the final model (litres per kilo harvested; the all-favourable example
is `scenarios.all_favourable`, $7.62). Code: `gf_doubling_bounds.py`; tests: `tests/test_gf_doubling_bounds.py`; numbers:
`inputs.py` (`gb_*`). Costs are 2025 dollars per kg of wet cells. Humbird's prices are 2018 dollars; the model scales them by
1.28 (`pf_opex_escalation`). Nothing in the model changes: the module calls `floor_physics.explore`, `floor_physics.Cells` and
`retention.duty`.

Access levels: **FT** = read in full text. **ABS** = abstract only. **SNIP** = search snippet only. **MEM** = from memory.

## 1. Answers in brief

- **Growth factors.** In the low-lactate example (38.8 L per kilo harvested), growth factors cost $1, $2 or $3 a kilo if all four
  proteins sell at 5.5%, 11.0% or 16.5% of Humbird's price. That is insulin at $0.49, $0.98 or $1.47 a gram and transferrin at
  $0.84, $1.69 or $2.53. FGF needs $46, $91 or $137 a gram and TGF-beta $1,323, $2,646 or $3,969. The all-favourable example
  (11.7 L/kg) allows prices 3.3 times higher. The cautious case (the published cells, 146 L/kg) needs prices 3.8 times lower than
  the low-lactate example: 1.5% of Humbird's price for $1 a kilo.
- **What dominates.** Insulin and transferrin dominate the cost at Humbird's prices (72%), because the cells use grams of them.
  TGF-beta and FGF dominate the price gap: bought at the prices found, they are 4,300 to 21,900 times too dear for $1 a kilo in
  the low-lactate example, against 50 times for insulin.
- **Reuse.** A filter that returns the proteins cuts the litres that carry them from 38.8 to 7.7 per kilo in the low-lactate
  example. At Humbird's full price that saves $14.33 of $17.88. In the model it saves nothing in any case shown: the low-lactate
  example's and the cautious case's media are complete, priced with the growth factors in ($0.20 and $0.30 a litre), and the
  all-favourable example buys none. It applies only to a medium at the nutrient floor with growth factors bought on top. FGF2
  that decays (half-life under 10 h) cuts the saving from 80% to 68%. No source shows a filter that holds these proteins back in
  a perfusion tank.
- **Doubling time.** The energy and biosynthesis budget lets an animal cell double in about 8 to 9 h if it can burn twice the
  oxygen West's law gives at 24 h. The range is 5 to 13 h for 3 to 1.5 times. The ribosomes give a similar bound. So physics
  allows doubling far faster than any scenario assumes. Biology and waste, not energy, stop 24 h cells.
- **Cost of speed.** The low-lactate example costs $49.50 at 36 h, $44.14 at 24 h and $40.08 at 16 h. It saves another $6.20
  from 16 h to 8 h, more than the $4.06 from 24 h to 16 h; oxygen supply limits it at every doubling time. Part of the gain is the
  bubbles: they kill the same culture per hour whatever the growth, so they take 8% of the cells grown at 36 h and under 4% at
  16 h. The published cells gain far more: $185.59 at 43 h, $142.91 at 24 h and $124.33 at 16 h. Lactate sets their medium, and a
  faster cell burns less glucose on upkeep per kilo made, so their litres fall with speed. The all-favourable example, at 16 h,
  costs $7.62; at 24 h it would cost $8.85.

## 2. Growth factors

### 2.1 The formulation and the price Humbird and the model use

Humbird's medium holds four proteins (Essential 8 levels, Chen et al. 2011): insulin 0.0194 g/L, transferrin 0.0107, FGF 1e-4, TGF-beta 2e-6. I
checked these in Humbird (Sect. 3.1, FT) and in the GFI report (footnote 4, FT). `floor_physics.py` does not hold them; it holds only a dollar figure.

Humbird's Table 4.4 (FT) prices the four proteins from his price-volume line (Eq. 3.4): insulin $7/g, transferrin $12, FGF $649, TGF-beta $18,837
(2018 dollars). At his concentrations they cost $3.13 per kg of cells, with insulin 37%, transferrin 35%, FGF 18% and TGF-beta 10%.

The model charges `pf_growth_factors` (x 1.28 for 2025 dollars) over the litres of Humbird's own fed-batch (`pf_medium_prep_l_kg`,
8.65 L/kg): $0.46 a litre. Humbird's own table prices at his concentrations give $0.47 a litre in 2025 dollars, so the two agree
within 2%. Until 2026-11-20 the model spread his figure over the 11.2 L/kg of his cells in perfusion and charged $0.356 a litre,
24% below his prices; the Humbird back-test (`humbird_backtest.md`) closed that gap. The tables below use the concentrations and
shares directly, so they never depended on it.

### 2.2 Prices each protein needs

`required_prices(litres, target)`. Litres are explore's, per kilo harvested: the all-favourable example 11.7 (ammonia sets it; it
takes Humbird's 50 mmol/L of lactate tolerated), the low-lactate example 38.8 (ammonia) and the cautious case 146.2 (lactate).
"Shared" splits the budget as Humbird's prices do, so all four fall by the same fraction. "Alone" gives one protein the whole
budget. Prices in $/g.

| Scenario, target | Insulin | Transferrin | FGF | TGF-beta | Fraction of Humbird's price |
|---|---|---|---|---|---|
| All-favourable example (11.7 L/kg), $1 | 1.63 | 2.80 | 151 | 4,395 | 18.2% |
| All-favourable example, $2 | 3.27 | 5.60 | 303 | 8,789 | 36.5% |
| All-favourable example, $3 | 4.90 | 8.40 | 454 | 13,184 | 54.7% |
| Low-lactate example (38.8 L/kg), $1 | 0.49 | 0.84 | 46 | 1,323 | 5.5% |
| Low-lactate example, $2 | 0.98 | 1.69 | 91 | 2,646 | 11.0% |
| Low-lactate example, $3 | 1.47 | 2.53 | 137 | 3,969 | 16.5% |
| Cautious (146.2 L/kg), $1 | 0.13 | 0.22 | 12 | 351 | 1.5% |
| Cautious, $2 | 0.26 | 0.45 | 24 | 703 | 2.9% |
| Cautious, $3 | 0.39 | 0.67 | 36 | 1,054 | 4.4% |
| Low-lactate example, $1, one protein alone | 1.33 | 2.41 | 258 | 12,879 | |
| Humbird's price, 2025 dollars | 8.96 | 15.36 | 831 | 24,111 | 100% |

The all-favourable example buys no growth factors; its rows say what it would take if it did. The low-lactate example and the
cautious case buy none on top either since 2026-11-19: their complete media carry the growth factors in the litre price. Before,
at the 28 L/kg both then used, the low-lactate example assumed $2.99 (30% of Humbird's price) and the cautious case $5.97 (60%).

GFI's three medium uses (8, 13, 42 L/kg) at $1 give, for insulin: $2.39, $1.47, $0.45 a gram; for transferrin $4.09, $2.52, $0.78.
GFI's own targets (insulin and transferrin $1/g, growth factors $100/g; Table 1, FT) cost $0.47 a kilo at the all-favourable
example's litres, $1.56 at the low-lactate example's 38.8 L/kg and $5.89 at the cautious case's 146.2. So the targets hold at 8 to
12 L/kg and fail at 39.

### 2.3 Against the prices found

| Protein | Price found, $/g | Access | Needed, the low-lactate example $1 | Times too dear |
|---|---|---|---|---|
| Insulin | 24.75 (Indian exports, 2013-16, falling about 18% a year; 484-793 kg a year) | FT (Europe PMC) | 0.49 | 50 |
| Transferrin | 182 (InVitria, 10 g); 352 at 1 g | FT of the supplement, via the pf-tea evidence file | 0.84 | 216 |
| FGF2 | 196,000 (ORF Genetics, 2022); 7,470 made in-house (Venkatesan) | FT of GFI's page; Venkatesan not read | 46 | 4,300 (164 in-house) |
| TGF-beta | 29,000,000 (Sigma research grade) | FT (Humbird footnote 111) | 1,323 | 21,900 |

Two cautions. Gotham's $24.75/g is an export price from a few hundred kilos, which Humbird's footnote calls a production cost; it is a market price. The
Pharmaoffer trade page gives an average of $36.4/g over 12 months (SNIP; the page returned 403 when fetched).

**Which factor dominates.**
- *In cost at Humbird's prices:* insulin and transferrin, 72%, because the dose is grams per kilo of cells (0.75 g insulin and 0.42 g transferrin at 38.8 L/kg).
- *In cost at the prices found:* TGF-beta (72%) and FGF2 (24%) of a $3,100 kilo in the low-lactate example; insulin and transferrin are 3%.
- *In the gap to close:* TGF-beta, then FGF2. But the dose is small: even at $10,000 a gram, TGF-beta adds $0.78 a kilo in the low-lactate example. It only matters at research prices.
- *At the price floor (below):* insulin and transferrin, again by mass.

### 2.4 Floors on production cost

A bulk protein made by microbes or in plants has a cost set by titre, recovery and scale. What was found:

| Anchor | $/kg | Access |
|---|---|---|
| Common food enzymes, Novozymes quotes at 200-1,000 kg | 12-25 | FT of GFI's footnote, second-hand |
| Bulk technical albumin, traded | 40-70 | pf-tea evidence (grade C); GFI 2025 |
| Albumin, pf-tea bottom-up, capture-only route | 143 | model result |
| Transferrin, pf-tea bottom-up, 100 t/y, design-point titre | 314 | model result, analogy to albumin's plant |
| Transferrin, same, best published titre (2.29 g/L, 10 L) | 949 at 100 t/y; 1,939 at 10 t/y | model result |
| Humbird's price-volume line at 13.7 t/y of insulin | 8,300 (his perfusion table) | FT |
| Humbird's line at 160 t/y | 1,000 | FT |
| Recombinant lactoferrin from rice, cash cost at 600 kg/y | 5,900 | SNIP |

Three readings.
1. The price of a protein falls with its volume on Humbird's line (Eq. 3.4: log10 price = 4.90 - 0.861 log10 volume, $/kg and
   MT/y). A $1 kilo in the low-lactate example needs insulin at about 489 t/y and transferrin at 262 t/y. That is 0.64 Mt of cells
   a year at 38.8 L/kg. FGF and TGF-beta need the same volume, because the line has one slope for every protein. A $3 kilo needs
   0.18 Mt (137 t/y of insulin). The world makes about 3 t a year of recombinant human insulin (Humbird footnote 113), so the
   demand is 45 to 160 times the whole insulin market.
2. The pf-tea transferrin model gives $0.31 to $0.95 a gram at 100 t/y. The low-lactate example needs $0.84 for a $1 kilo. So the
   design-point titre clears it and the best published titre just misses it. Both clear the $2.80 the all-favourable example
   needs. Neither clears the $0.22 the cautious case needs. At 10 t/y it costs $1.9 a gram: enough for the all-favourable example,
   not for the low-lactate example. There is no bottom-up model here for insulin, FGF or TGF-beta.
3. Venkatesan et al. made TGF-beta and FGF2 in-house for $0.82 per litre of medium (GFI page, FT; the paper itself not read). At
   38.8 L/kg that is $32 a kilo, 32 times the low-lactate example's $1 budget for all four proteins. TGF-beta is a disulfide-linked
   dimer made as a latent complex; no cost estimate for it from microbes or plants at scale was found.

### 2.5 Reuse: what a filter that returns the proteins saves

`reuse(key)`. The permeate (retention.duty's flow) is protein-free, so only the bleed carries the proteins out: the culture that
leaves with the cells, 6.96 L per kilo harvested in the all-favourable example (155 g/L), 7.22 in the low-lactate example (154 g/L)
and 10.43 in the cautious case (103 g/L). A first fill adds 0.20, 0.48 and 0.84 L/kg.

| Scenario | Medium L/kg | Permeate L/kg (share) | Full price, no reuse | Full price, reuse | Scenario's own assumption, no reuse | With reuse |
|---|---|---|---|---|---|---|
| All-favourable example | 11.7 | 4.7 (40%) | $5.38 | $3.30 | $0 (none bought) | $0 |
| Low-lactate example | 38.8 | 31.6 (81%) | $17.88 | $3.55 | $0 (in the $0.20 medium) | $0 |
| Cautious | 146.2 | 135.8 (93%) | $67.33 | $5.19 | $0 (in the $0.30 medium) | $0 |

At Humbird's full price reuse saves $14.33 in the low-lactate example, $62.14 in the cautious case and $2.08 in the all-favourable
example. Against the scenarios' own assumptions it saves nothing, because the growth factors are inside the complete media prices
and not charged on their own (or, in the all-favourable example, not bought). Whatever share of a complete medium's price is
growth factors would still be saved by such a filter, but the price does not say how much that share is, so the model cannot
count it.

Four limits on this number.
- **Decay.** The tank holds a retained protein for 23 h (the all-favourable example), 53 h (the low-lactate example) or 64 h
  (cautious), the time the bleed takes to turn over the liquid. Wild-type FGF2 has a half-life under 10 h at 37 C (vendor pages and
  a review, SNIP). With it decaying and the other three stable, the full-price cost with reuse in the low-lactate example rises from
  $3.55 to $5.71 and the saving falls from 80% to 68%. FGF2-G3, the engineered form, lasts over 7 days (vendor claim, SNIP; a
  preprint reports over 20 days). No half-lives were found for insulin, transferrin or TGF-beta; the cells also take them up.
- **The model's filter passes proteins.** The default TFF loop uses 0.2 micron hollow fibres (Repligen Spectrum, per the retention
  note). Those pass all four proteins. Holding them back needs an ultrafilter or a dialyser fibre, which the retention note says
  would raise a protein to about 7 times its feed level. The lower flux is not priced here.
- **Adsorption and shear.** No measurement of growth-factor retention by a filter in cultivated-meat perfusion exists in the notes
  (`waste_and_medium_evidence.md`, item N).
- **Price follows volume.** If prices follow Humbird's line, using less protein shrinks the market, so each gram costs more. Cost
  per kilo then goes as litres^0.139, and the saving in the low-lactate example falls from 80% to 20%. The 80% holds only if the
  price sits on a production-cost floor that a bigger plant does not lower.

## 3. Doubling time

### 3.1 The budget

West's law (Humbird Eq. 2.8, FT): 0.148 x M^0.75 pW per cell, 60 pW at 3,000 pg. The model turns this into oxygen at 483 kJ/mol (`pf_heat_per_o2`): 0.149 mmol
O2 per gram of wet cells per hour at a 24 h doubling. At 5 ATP per O2 (`ge_atp_per_o2`, P/O of 2.5), that is 0.745 mmol ATP per gram per hour.

`floor_physics.Cells` splits that rate into upkeep (`pf_maintenance_share`, 0.5, with a range of 0.31 to 1.0) and growth. At 24 h, growth takes 0.373 mmol ATP per
gram per hour. A gram is made at 0.0289 per hour, so the model spends **12.9 mmol ATP to make a gram of wet cells**.

**Bottom-up cost.** Humbird's composition (Table 2.1, FT) is 70% protein, 15% lipid, 10% carbohydrate and 5% RNA/DNA by dry mass, and a gram of wet cells
holds 0.30 g dry. The cost of joining the building blocks:

| Part | ATP per unit | mmol ATP per g dry mass |
|---|---|---|
| Protein, 4 ATP per peptide bond, 110 g/mol per residue (MEM) | 4 | 25.5 |
| Lipid made from glucose, 42 ATP per palmitate (7 ATP and 14 NADPH at 2.5 each; MEM) | 42 | 24.6 |
| RNA and DNA, 9 ATP per nucleotide (MEM) | 9 | 1.4 |
| Carbohydrate, 2 ATP per hexose (MEM) | 2 | 1.2 |
| **Total** | | **52.7 (15.8 per g wet)** |

Fed lipid drops the total to 8.4 per gram wet. Adding 60% for folding, uptake and ribosome and mRNA turnover raises it to 25.3. The sum counts no carbon
skeleton: Humbird's Reactions 2.2 to 2.6 show anabolism barely costs energy, since the amino acids come from the medium.

**Check.** 15.8 mmol per gram fits inside West's 24 h rate with a 39% share left for upkeep. That sits between the 31% measured in cells at zero growth (GFI
2025 review, Fig. 3.5b, from Wagner et al. 2011, ABS) and the model's 50%. A bottom-up cost of 25 would leave none, so the cost must stay below about 18.
**Check 2.** The model gives 0.194 mmol O2 per gram per hour at a 15 h doubling. CHO cells burn 0.18 to 0.21 (Goudar et al. 2011, ABS: 5.1-5.8 pmol per cell per day;
Humbird's CHO mass of 1,167 pg, FT). The agreement is partly by construction, since West's law fits CHO.

### 3.2 The limit

The cell burns `k` times West's 24 h rate and spends everything above upkeep on growth:

    mu_max = mu_24 + (k - 1) x P_24 / (ATP per gram made),    doubling time = ln 2 / mu_max.

| Respiration, relative to West at 24 h | Bottom-up cost (15.8) | Model's own split (12.9) | Fed lipid (8.4) |
|---|---|---|---|
| 1.0 | 24.0 h | 24.0 h | 24.0 h |
| 1.5 | 13.2 h | 12.0 h | 9.5 h |
| 2.0 | 9.1 h | 8.0 h | 5.9 h |
| 3.0 | 5.6 h | 4.8 h | 3.4 h |

How much more can a cell burn? Cells held at an uncoupler typically reach 2 to 4 times their resting rate (MEM; not read in this pass). Mitochondria fill
10 to 20% of a fast cell line and about 35% of heart muscle (MEM). I take 2 as the central value and 1.5 to 3 as the range (`gb_resp_scope`).
Glycolysis could add ATP, but it makes lactate, which the model already limits.

**Ribosomes.** Protein must double with the cell. A mammalian ribosome adds 5.6 amino acids a second in mouse stem cells (Ingolia et al. 2011, SNIP; other cells
give 3 to 5), has a mass of 4.3 MDa (MEM), and rRNA is 80% of cell RNA and 65% of a ribosome (MEM). At Humbird's 5% RNA the ribosomes allow doubling in
**15.3 h**. At 3.5 aa/s, 24.5 h. A doubling in 12 h needs 6.4% RNA, 8 h needs 9.6% and 6 h needs 12.7% (at 5.6 aa/s). Fast bacteria hold 20 to 30% RNA (MEM), so this
limit also sits near 5 to 8 h if the cell builds more ribosomes.

**Result.** Both budgets put the fastest doubling an animal cell could sustain at **about 5 to 13 h by calculation, central 8 to 9 h**. The fastest in the literature are 4 to 8 h, with
cultivated-meat lines expected at 12 to 24 h after optimisation (GFI technical summary, Nov 2025, FT, via `species_cell_parameters.md`; I could not check which
cells reach 4 to 8 h). A cell line that doubles in 20 h (chicken fibroblasts, SNIP) uses about 1.1 times the oxygen of one at 24 h, by the model's split.
Other limits sit outside this budget: DNA replication (S phase of 6 to 8 h in most mammalian cells, MEM) and the oxygen the tank can supply.

### 3.3 Cost at each doubling time

`scan_doubling`: `explore(doubling_h=...)` with each scenario's own settings and tank design held fixed. $/kg.

| Doubling time | All-favourable example | Low-lactate example | Cautious |
|---|---|---|---|
| 8 h (beyond any meat cell shown) | 6.47 | 33.88 | 102.21 |
| 12 h | 7.05 | 37.53 | 114.20 |
| 16 h | **7.62** (own) | 40.08 | 124.33 |
| 20 h | 8.20 | 42.21 | 133.77 |
| 24 h | 8.85 | 44.14 | 142.91 |
| 30 h | 9.87 | 46.86 | 156.40 |
| 36 h | 10.94 | **49.50** (own) | 169.83 |
| 43 h | 12.24 | 52.56 | **185.59** (own) |

- The low-lactate example saves $5.36 from 36 h to 24 h, $9.42 to 16 h and $15.62 to 8 h. The all-favourable example would cost
  $1.23 more at 24 h than at its own 16 h. The cautious case saves $42.68 from 43 h to 24 h and $61.26 to 16 h.
- The low-lactate example's litres per kilo grown do not change with speed: ammonia sets them at 35.0 whatever the doubling time.
  Per kilo harvested they rise from 36.4 at 8 h to 39.5 at 43 h, because the bubbles kill a larger share of slow cells. Ammonia
  sets the all-favourable example's litres up to 20 h (11.3 to 11.9 L/kg) and lactate from 24 h (12.5 to 16.1).
- The cautious case's medium shrinks with speed. Lactate sets it, and the cells' glucose follows their oxygen use, which has an
  upkeep part that grows with the time a kilo takes to make. Its litres are 146.2 per kilo harvested at 43 h, 118.1 at 24 h, 106.6
  at 16 h and 95.3 at 8 h.
- Oxygen supply binds all three at every doubling time, so their density falls with speed: the low-lactate example from 162 g/L
  (43 h) and 154 (36 h, own) to 133 at 24 h, 110 at 16 h and 73 at 8 h; the cautious case from 103 (43 h) to 68 (16 h) and 44 g/L
  (8 h); the all-favourable example from 222 (43 h) to 155 (16 h, own) and 106 g/L (8 h). Fast cells need more oxygen per gram, and
  a thick culture takes oxygen up more slowly.
- The low-lactate example's 36 h is far from any energy limit.

## 4. Rough judgements

Each figure below is a rough judgement made while building the model with an AI assistant; not measured and not reviewed by an
expert. The reasoning is beside each.

| Statement | Judgement | Reasoning |
|---|---|---|
| Fastest doubling physics allows an animal cell at 37 C | median about 8 h, 80% range 4.5 to 12 h | section 3.2: the energy budget at 1.5 to 3 times West's rate gives 5 to 13 h; the ribosomes at 5 to 10% RNA give 8 to 15 h; the fastest reported cells double in 4 to 8 h |
| Insulin, then transferrin, made at a production cost of $1/g or less in a plant of 100 t/y or more | likely (about 70 to 80%) | section 2.4: food enzymes sell at $0.01 to $0.03 a gram; the pf-tea transferrin model gives $0.31 to $0.95 at that scale; insulin is a smaller, simpler protein made at scale already |
| FGF2 at $100/g or less at 1 t/y or more; TGF-beta at $2,000/g or less at 10 kg/y or more | about even for each | in-house FGF2 already costs $7,470 a gram; no cost estimate for TGF-beta from microbes or plants was found |
| All four at the prices that give the low-lactate example $3 a kilo (0.18 Mt of cells a year) | about even | needs every protein near its production floor and a volume far above today's market |
| A filter that holds back insulin and transferrin halves the low-lactate example's growth-factor cost at 20 m3 | unlikely (about 20%) | section 2.5: it needs a protein-tight membrane at the cell filter's flux, and retention, decay and adsorption are unmeasured |

These are for the production cost of each protein at the stated scale, or for the speed alone. They do not say that the industry
reaches that scale, or that a cell line combines that speed with low waste.

## 5. What would change these numbers

- A measured price of insulin or transferrin at 100 t/y or more (a quote or a plant cost). It would replace the transferrin model
  and fill the insulin gap.
- A measurement of growth-factor retention and decay in a perfusion culture of meat cells. It would settle section 2.5.
- Oxygen uptake of a fast cultivated-meat line (GFI names this a data gap). It would replace the 2x scope with a measurement.

## 6. Sources

1. Humbird D. (2021). Scale-up economics for cultured meat. Biotechnol Bioeng 118:3239. Full text, local PDF (`Cultivated_meat_TEAs/Humbird21Cultivated.pdf`): Sect. 2.2
   (Reactions 2.2-2.11, Eq. 2.8, footnote 41), Sect. 3.1 (Eq. 3.4, Table 3.6, footnotes 111-115), Tables 4.4 and 2.1. The long report (Humbird-R) is the source of the other inputs.
2. Swartz E. et al. (2023). Anticipated growth factor and recombinant protein costs and volumes for cost-competitive cultivated meat. GFI. Full text,
   https://gfi.org/cultivated-meat-growth-factor-report (Executive summary; Box 2; Table 1; footnotes 4 and 8).
3. GFI. Growth factor cost page. Full text of the page, https://gfi.org/solutions/scaffolds-with-growth-factors (ORF Genetics $196/mg; Venkatesan $7.47/mg).
4. Gotham D., Barber M.J., Hill A. (2018). Production costs and potential prices for biosimilars of human insulin and insulin analogues. BMJ Glob Health 3:e000850.
   Full text through Europe PMC (PMC6157569): API $24,750/kg from Indian export records.
5. Chen G. et al. (2011). Chemically defined conditions for human iPSC derivation and culture. Nat Methods 8:424 (Essential 8 levels; as quoted by the pf-tea evidence file, FT there).
6. Stout A.J. et al. (2022). Beefy-9, Commun Biol 5:466, Supplementary Table 3 (transferrin price), as quoted in `pf-tea/data/evidence/transferrin.yaml` (FT there).
7. pf-tea (the owner's own protein-cost model, `results/analyses.json`): transferrin and albumin cost cases. Evidence grades in `pf-tea/data/evidence/transferrin.yaml`.
8. Harsini F., Frohlich B., Swartz E. (2025). Technical summary: cell growth modeling review. GFI. FT, as used in `species_cell_parameters.md`. Wagner et al. (2011) via that review, ABS.
9. Goudar C.T., Piret J.M., Konstantinov K.B. (2011). Biotechnol Prog 27:1347. ABS, via `species_cell_parameters.md`.
10. Ingolia N.T. et al. (2011). Cell 147:789, via the BioNumbers entry (SNIP).
11. Vendor pages for FGF2 and FGF2-G3 half-lives (Qkine, Reprocell, LifeTein; SNIP); Dvorak P. et al. thermostable FGF2 preprint (bioRxiv 100636; SNIP).
12. Pharmaoffer insulin-human trade page (403; SNIP only); lactoferrin plant-made cost ($5.90/g at 600 kg/y; SNIP via a search summary).
