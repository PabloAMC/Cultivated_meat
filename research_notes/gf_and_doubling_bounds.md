# Growth-factor prices and the fastest doubling time

> Repinned 2026-11-19 (scenario restructure): every kind of cell weighs 2 ng, so the all-favourable example's cells are no longer Humbird's 3 ng; it costs $11.67 at most likely values, not $11.46, and its figures here are the earlier ones unless a table says otherwise (the tests pin the new ones). The ammonia range of the low-lactate example's cells now runs from 0.04 mol/kg.

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50.
> Repinned 2026-11-19 (audit batch): ammonia tolerance 4 mM, lost runs pay for their membranes, glucose from the cells' balance (published cells need about 95 L/kg); see audit_2026-11-19.md.
> What this changed here: Central uses 35 L/kg (was 28), Best 13.75 (was 11.16) and the cautious case, the published cells, 95.5 (was 28).
> So every required price fell, the cautious case no longer needs the same prices as Central (it needs prices 2.7 times lower), and
> speed is now worth far more to the published cells than to Central.

Recomputed 2026-11-16 on the current model (bubble protectant, antifoam's cost to oxygen transfer, bought oxygen in a yeast-style plant, dissolved oxygen held at half of air saturation, medium at least the culture that leaves with the cells).

Date: 2026-11-15. Code: `gf_doubling_bounds.py`; tests: `tests/test_gf_doubling_bounds.py`; numbers: `inputs.py` (`gb_*`). Costs are 2025 dollars
per kg of wet cells. Humbird's prices are 2018 dollars; the model scales them by 1.28 (`pf_opex_escalation`). Nothing in the model changes: the
module calls `floor_physics.explore`, `floor_physics.Cells` and `retention.duty`.

Access levels: **FT** = read in full text. **ABS** = abstract only. **SNIP** = search snippet only. **MEM** = from memory. Probabilities are my
judgement, not forecasts of the industry.

## 1. Answers in brief

- **Growth factors.** In Central (35 L/kg), growth factors cost $1, $2 or $3 a kilo if all four proteins sell at 6.1%, 12.2% or 18.3% of Humbird's price. That is
  insulin at $0.55, $1.09 or $1.64 a gram and transferrin at $0.93, $1.87 or $2.80. FGF needs $51, $101 or $152 a gram and TGF-beta $1,467,
  $2,935 or $4,402. The all-favourable example (13.75 L/kg) allows prices 2.5 times higher. The cautious case (the published cells, 95.5 L/kg) needs prices
  2.7 times lower than Central: 2.2% of Humbird's price for $1 a kilo. Before the audit batch it needed the same prices as Central, since both used 28 L/kg.
- **What dominates.** Insulin and transferrin dominate the cost at Humbird's prices (72%), because the cells use grams of them. TGF-beta and FGF
  dominate the price gap: bought at the prices found, they are 3,900 to 19,800 times too dear for $1 a kilo in Central, against 45 times for insulin.
- **Reuse.** A filter that returns the proteins cuts the litres that carry them from 35 to 5.6 per kilo in Central. At Humbird's full price that saves
  $10.46 of $12.44. In the model it now saves nothing in Central or the cautious case: since 2026-11-19 their media are complete, priced
  with the growth factors in ($0.20 and $0.30 a litre), so the model charges no growth factors to save (it saved $2.39 of $2.99 in Central
  when 30% of Humbird's price was bought on top). It applies only to a medium at the nutrient floor, with growth factors bought on top. FGF2 that decays (half-life under 10 h) cuts that saving by about 12%. No source shows a filter that holds these proteins back in a
  perfusion tank.
- **Doubling time.** The energy and biosynthesis budget lets an animal cell double in about 8 to 9 h if it can burn twice the oxygen West's law gives
  at 24 h. The range is 5 to 13 h for 3 to 1.5 times. The ribosomes give a similar bound. So physics allows doubling far faster than any
  scenario assumes. Biology and waste, not energy, stop 24 h cells.
- **Cost of speed.** Central costs $32.80 at 36 h, $30.32 at 24 h and $28.30 at 16 h. Central saves another $3.39 from 16 h to 8 h, more than
  the $2.02 from 24 h to 16 h; oxygen supply limits Central at every doubling time. The published cells gain far more: $92.17 at 43 h, $72.20 at
  24 h and $63.13 at 16 h. Lactate sets their medium, and a faster cell burns less glucose on upkeep per kilo made, so their litres fall with speed.

## 2. Growth factors

### 2.1 The formulation and the price Humbird and the model use

Humbird's medium holds four proteins (Essential 8 levels, Chen et al. 2011): insulin 0.0194 g/L, transferrin 0.0107, FGF 1e-4, TGF-beta 2e-6. I
checked these in Humbird (Sect. 3.1, FT) and in the GFI report (footnote 4, FT). `floor_physics.py` does not hold them; it holds only a dollar figure.

Humbird's Table 4.4 (FT) prices the four proteins from his price-volume line (Eq. 3.4): insulin $7/g, transferrin $12, FGF $649, TGF-beta $18,837
(2018 dollars). At his concentrations they cost $3.13 per kg of cells, with insulin 37%, transferrin 35%, FGF 18% and TGF-beta 10%.

The model charges `pf_growth_factors` = $3.1 (x 1.28 = $3.97) at 11.2 L/kg. That is $0.356 a litre. Humbird's own table prices at his concentrations
give $0.470 a litre in 2025 dollars. **The model is 24% below that.** The reason: Humbird's batch holds about 115 g/L, so it uses 8.65 L/kg, and the
model spread his $3.13 over 11.2 L/kg. The effect is that "30% of his price per litre" is 22.8% of his table prices. I left this alone, since no
pinned number may move. The tables below use the concentrations and shares directly, so they do not depend on the gap.

### 2.2 Prices each protein needs

`required_prices(litres, target)`. Litres are explore's: Best 13.75 (ammonia sets it at the 4 mmol/L tolerance; it was 11.16, set by lactate), Central 35.0 (ammonia) and
cautious 95.5 (lactate, now that glucose comes from the cells' own balance). "Shared" splits
the budget as Humbird's prices do, so all four fall by the same fraction. "Alone" gives one protein the whole budget. Prices in $/g.

| Scenario, target | Insulin | Transferrin | FGF | TGF-beta | Fraction of Humbird's price |
|---|---|---|---|---|---|
| Best (13.75 L/kg), $1 | 1.39 | 2.38 | 129 | 3,735 | 15.5% |
| Best, $2 | 2.78 | 4.76 | 257 | 7,470 | 31.0% |
| Best, $3 | 4.16 | 7.14 | 386 | 11,206 | 46.5% |
| Low-lactate example (35 L/kg), $1 | 0.55 | 0.93 | 51 | 1,467 | 6.1% |
| Low-lactate example, $2 | 1.09 | 1.87 | 101 | 2,935 | 12.2% |
| Low-lactate example, $3 | 1.64 | 2.80 | 152 | 4,402 | 18.3% |
| Cautious (95.5 L/kg), $1 | 0.20 | 0.34 | 19 | 538 | 2.2% |
| Cautious, $2 | 0.40 | 0.69 | 37 | 1,076 | 4.5% |
| Cautious, $3 | 0.60 | 1.03 | 56 | 1,613 | 6.7% |
| Low-lactate example, $1, one protein alone | 1.47 | 2.67 | 286 | 14,286 | |
| Humbird's price, 2025 dollars | 8.96 | 15.36 | 831 | 24,111 | 100% |

Best buys no growth factors in the scenario; the Best rows say what it would take if it did. Central and cautious buy none on top either since
2026-11-19: their complete media carry the growth factors in the litre price. Before, at the 28 L/kg both then used, Central assumed $2.99
(30% of Humbird's price) and cautious $5.97 (60%), so cautious needed a price 2 to 6 times below its assumption to reach $1 to $3.

GFI's three medium uses (8, 13, 42 L/kg) at $1 give, for insulin: $2.39, $1.47, $0.45 a gram; for transferrin $4.09, $2.52, $0.78. GFI's own targets
(insulin and transferrin $1/g, growth factors $100/g; Table 1, FT) cost $0.55 a kilo at Best's litres, $1.41 at Central's 35 L/kg and $3.85 at the cautious case's 95.5. So the targets hold at 8 to 14 L/kg
and fail at 35.

### 2.3 Against the prices found

| Protein | Price found, $/g | Access | Needed, the low-lactate example $1 | Times too dear |
|---|---|---|---|---|
| Insulin | 24.75 (Indian exports, 2013-16, falling about 18% a year; 484-793 kg a year) | FT (Europe PMC) | 0.55 | 45 |
| Transferrin | 182 (InVitria, 10 g); 352 at 1 g | FT of the supplement, via the pf-tea evidence file | 0.93 | 195 |
| FGF2 | 196,000 (ORF Genetics, 2022); 7,470 made in-house (Venkatesan) | FT of GFI's page; Venkatesan not read | 51 | 3,900 (150 in-house) |
| TGF-beta | 29,000,000 (Sigma research grade) | FT (Humbird footnote 111) | 1,467 | 19,800 |

Two cautions. Gotham's $24.75/g is an export price from a few hundred kilos, which Humbird's footnote calls a production cost; it is a market price. The
Pharmaoffer trade page gives an average of $36.4/g over 12 months (SNIP; the page returned 403 when I fetched it).

**Which factor dominates.**
- *In cost at Humbird's prices:* insulin and transferrin, 72%, because the dose is grams per kilo of cells (0.68 g insulin and 0.37 g transferrin at 35 L/kg).
- *In cost at the prices found:* TGF-beta (72%) and FGF2 (24%) of a $2,800 kilo in Central; insulin and transferrin are 3%.
- *In the gap to close:* TGF-beta, then FGF2. But the dose is small: even at $10,000 a gram, TGF-beta adds $0.70 a kilo in Central. It only matters at research prices.
- *At the price floor (below):* insulin and transferrin, again by mass.

### 2.4 Floors on production cost

A bulk protein made by microbes or in plants has a cost set by titre, recovery and scale. What I found:

| Anchor | $/kg | Access |
|---|---|---|
| Common food enzymes, Novozymes quotes at 200-1,000 kg | 12-25 | FT of GFI's footnote, second-hand |
| Bulk technical albumin, traded | 40-70 | pf-tea evidence (grade C); GFI 2025 |
| Albumin, pf-tea bottom-up, capture-only route, my own model | 143 | model result |
| Transferrin, pf-tea bottom-up, 100 t/y, design-point titre | 314 | model result, analogy to albumin's plant |
| Transferrin, same, best published titre (2.29 g/L, 10 L) | 949 at 100 t/y; 1,939 at 10 t/y | model result |
| Humbird's price-volume line at 13.7 t/y of insulin | 8,300 (his perfusion table) | FT |
| Humbird's line at 160 t/y | 1,000 | FT |
| Recombinant lactoferrin from rice, cash cost at 600 kg/y | 5,900 | SNIP |

Three readings.
1. The price of a protein falls with its volume on Humbird's line (Eq. 3.4: log10 price = 4.90 - 0.861 log10 volume, $/kg and MT/y). A $1 kilo
   in Central needs insulin at about 434 t/y and transferrin at 232 t/y. That is 0.6 Mt of cells a year at 35 L/kg. FGF and TGF-beta need the same
   volume, because the line has one slope for every protein. A $3 kilo needs 0.18 Mt (121 t/y of insulin); the $2.99 Central assumed before 2026-11-19, at 28 L/kg, sat near that scale. The
   world makes about 3 t a year of recombinant human insulin (Humbird footnote 113), so the demand is 40 to 145 times the whole insulin market.
2. My transferrin model gives $0.31 to $0.95 a gram at 100 t/y. Central needs $0.93 for a $1 kilo. So the design-point titre clears it and the
   best published titre just misses it. This is weaker than before the audit batch, when Central needed $1.17 and both cleared it. Both clear
   the $2.38 Best needs. Only the design-point titre clears the $0.34 the cautious case needs, and barely. At 10 t/y it costs $1.9 a gram:
   enough for Best, not for Central. I have no bottom-up model for insulin, FGF or TGF-beta.
3. Venkatesan et al. made TGF-beta and FGF2 in-house for $0.82 per litre of medium (GFI page, FT; the paper itself not read). At 35 L/kg that is $29
   a kilo, 29 times Central's $1 budget for all four proteins. TGF-beta is a disulfide-linked dimer made as a latent complex; I found no cost estimate for it
   from microbes or plants at scale.

### 2.5 Reuse: what a filter that returns the proteins saves

`reuse(key)`. The permeate (retention.duty's flow) is protein-free, so only the bleed carries the proteins out. That is 3.88 L/kg in Best
(1000 / 258 g/L), 5.24 in Central (191 g/L) and 8.32 in the cautious case (120 g/L). A first fill adds 0.17 (Best), 0.35 (Central) and 0.67 (cautious) L/kg.

| Scenario | Medium L/kg | Permeate L/kg (share) | Full price, no reuse | Full price, reuse | Scenario's own assumption, no reuse | With reuse |
|---|---|---|---|---|---|---|
| Best | 13.75 | 9.9 (72%) | $4.89 | $1.44 | $0 (none bought) | $0 |
| Low-lactate example | 35.0 | 29.8 (85%) | $12.44 | $1.99 | $0 (in the $0.20 medium) | $0 |
| Cautious | 95.5 | 87.2 (91%) | $33.96 | $3.20 | $0 (in the $0.30 medium) | $0 |

At Humbird's full price reuse saves $10.46 in Central, $30.76 in the cautious case and $3.45 in Best. The cost with reuse did not move, because
the bleed did not; the saving grew because the permeate did. Against the scenarios' own assumptions it
saves nothing since 2026-11-19, because the growth factors are inside the complete media prices and not charged on their own. Before, it saved
$2.39 of $2.99 in Central and $4.06 of $5.97 in the cautious case. Whatever share of a complete medium's price is growth factors would still be
saved by such a filter, but the price does not say how much that share is, so the model cannot count it.

Four limits on this number.
- **Decay.** The tank holds a retained protein for 35 h (Best), 53 h (Central) or 64 h (cautious), the time the bleed takes to turn over the liquid.
  Wild-type FGF2 has a half-life under 10 h at 37 C (vendor pages and a review, SNIP). With it decaying and the other three stable, the full-price cost
  in Central rises from $1.99 to $3.20 and the saving falls from 84% to 74%. FGF2-G3, the engineered form, lasts over 7 days (vendor claim, SNIP; a preprint
  reports over 20 days). I did not find half-lives for insulin, transferrin or TGF-beta; the cells also take them up.
- **The model's filter passes proteins.** The default TFF loop uses 0.2 micron hollow fibres (Repligen Spectrum, per the retention note). Those pass all
  four proteins. Holding them back needs an ultrafilter or a dialyser fibre, which the retention note says would raise a protein to about 7 times its feed
  level. I have not priced the lower flux.
- **Adsorption and shear.** No measurement of growth-factor retention by a filter in cultivated-meat perfusion exists in the notes I hold
  (`waste_and_medium_evidence.md`, item N).
- **Price follows volume.** If prices follow Humbird's line, using less protein shrinks the market, so each gram costs more. Cost per kilo then goes as
  litres^0.139, and the saving in Central falls from 84% to 23%. The 84% holds only if the price sits on a production-cost floor that a bigger plant does not lower.

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

**Result.** Both budgets put the fastest doubling an animal cell could sustain at **about 5 to 13 h by calculation, central 8 to 9 h**; my odds (section 4) put the median at 8 h. The fastest in the literature are 4 to 8 h, with
cultivated-meat lines expected at 12 to 24 h after optimisation (GFI technical summary, Nov 2025, FT, via `species_cell_parameters.md`; I could not check which
cells reach 4 to 8 h). A cell line that doubles in 20 h (chicken fibroblasts, SNIP) uses about 1.1 times the oxygen of one at 24 h, by the model's split.
Other limits sit outside this budget: DNA replication (S phase of 6 to 8 h in most mammalian cells, MEM) and the oxygen the tank can supply.

### 3.3 Cost at each doubling time

`scan_doubling`: `explore(doubling_h=...)` with each scenario's own settings and tank design held fixed. $/kg.

| Doubling time | Best | Low-lactate example | Cautious |
|---|---|---|---|
| 8 h (beyond any meat cell shown) | 9.60 | 24.91 | 51.76 |
| 12 h | 10.06 | 26.95 | 58.03 |
| 16 h | 10.53 | 28.30 | 63.13 |
| 20 h | 10.98 | 29.38 | 67.78 |
| 24 h | **11.46** (own) | 30.32 | 72.20 |
| 30 h | 12.18 | 31.60 | 78.62 |
| 36 h | 14.08 | **32.80** (own) | 84.91 |
| 43 h | 16.39 | 34.14 | **92.17** (own) |

- Central saves $2.48 from 36 h to 24 h, $4.50 to 16 h and $7.89 to 8 h. Best saves $0.93 from 24 h to 16 h. The cautious case saves $19.97
  from 43 h to 24 h and $29.03 to 16 h.
- Central's medium does not shrink with speed. Ammonia sets its 35 L/kg whatever the doubling time. Capital and labour fall instead. Ammonia
  also sets Best's 13.75 L/kg up to 30 h; at 36 h and 43 h the least medium flow sets it (16.2 and 19.4 L/kg).
- The cautious case's medium does shrink with speed. This is new. Lactate sets it, and the cells' glucose now follows their oxygen use, which
  has an upkeep part that grows with the time a kilo takes to make. Its litres are 95.5 per kilo at 43 h, 78.9 at 24 h, 71.8 at 16 h and 64.8 at 8 h.
- Oxygen supply now binds Central and cautious at every doubling time, so their density falls with speed: Central from 204 g/L (43 h) and 191 (36 h, own) to
  159 at 24 h, 127 at 16 h and 80 at 8 h; cautious from 120 (43 h) to 75 (16 h) and 47 g/L (8 h). Best holds 258 g/L down to 8 h; the thickness of the culture
  binds it. This changed: before, oxygen bound Best at the fast end and Central not at all. Fast cells also need more oxygen per gram.
- Central's 36 h is far from any energy limit. The model's own odds for 24 h together with low ammonia are about 10% (`sc_td_central`).

## 4. Probabilities (judgement)

| Statement | Probability |
|---|---|
| Physics (energy, biosynthesis, ribosomes) lets an animal cell double in 12 h or less, at 37 C | 90% |
| ... in 8 h or less | 50% |
| ... in 6 h or less | 25% |
| ... in 4 h or less | 5% |
| Fastest doubling physics allows: median 8 h, 80% interval 4.5 to 12 h | |
| A meat-species line is shown in serum-free suspension at 50 g/L or more with doubling at or under 24 h, by 2035 | 40% |
| ... 20 h | 20% |
| ... 16 h | 7% |
| ... 12 h | 2% |
| Insulin made at a production cost of $1/g or less in a plant of 100 t/y or more (cost floor, not the industry reaching that scale) | 80% |
| Transferrin, the same | 70% |
| FGF2 at $100/g or less at 1 t/y or more | 65% |
| TGF-beta at $2,000/g or less at 10 kg/y or more | 45% |
| All four at the prices that give the low-lactate example $3 a kilo (judged at 28 L/kg; see below), at a scale of 0.2 Mt of cells a year | 55% |
| ... $1 a kilo (0.6 Mt of cells a year) | 25% |
| Cultivated meat reaches 0.2 Mt a year by 2040 | 8% |
| A filter that holds back insulin and transferrin cuts the low-lactate example's growth-factor cost by half or more at 20 m3 (the cost of the proteins, wherever it is charged; the model now charges it inside the medium's price) | 20% |
| ... by a quarter or more | 30% |

The two Central rows were judged at 28 L/kg. At 35 L/kg the prices asked are 20% lower (18.3% of Humbird's price for $3 a kilo, not 22.8%)
and the scales are 0.18 and 0.63 Mt. I have not re-judged the odds; they are if anything a little high.

The doubling-time odds are for the speed alone. The scenario notes (`inputs.py`, `sc_td_central`) put about 10% on 24 h together with ammonia at or below
0.14; that joint event is rarer than either part. The growth-factor odds are for the production cost of each protein at the stated scale. They do not say the
industry will reach that scale, which is the last-but-one row.

## 5. What would change these numbers

- A measured price of insulin or transferrin at 100 t/y or more (a quote or a plant cost). It would replace my transferrin model and fill the insulin gap.
- A measurement of growth-factor retention and decay in a perfusion culture of meat cells. It would settle section 2.5.
- Oxygen uptake of a fast cultivated-meat line (GFI names this a data gap). It would replace the 2x scope with a measurement.
- The Humbird gap (section 2.1): either his 8.65 L/kg or the model's 11.2 sets the price per litre. Using his per-litre price would change a growth-factor cost of 30%
  of his price at 35 L/kg from $3.73 to $4.93. It was not moved here. Since 2026-11-19 it moves only a medium at the nutrient floor, the one
  setting that buys growth factors on top.

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
7. pf-tea (my own model, `results/analyses.json`): transferrin and albumin cost cases. Evidence grades in `pf-tea/data/evidence/transferrin.yaml`.
8. Harsini F., Frohlich B., Swartz E. (2025). Technical summary: cell growth modeling review. GFI. FT, as used in `species_cell_parameters.md`. Wagner et al. (2011) via that review, ABS.
9. Goudar C.T., Piret J.M., Konstantinov K.B. (2011). Biotechnol Prog 27:1347. ABS, via `species_cell_parameters.md`.
10. Ingolia N.T. et al. (2011). Cell 147:789, via the BioNumbers entry (SNIP).
11. Vendor pages for FGF2 and FGF2-G3 half-lives (Qkine, Reprocell, LifeTein; SNIP); Dvorak P. et al. thermostable FGF2 preprint (bioRxiv 100636; SNIP).
12. Pharmaoffer insulin-human trade page (403; SNIP only); lactoferrin plant-made cost ($5.90/g at 600 kg/y; SNIP via a search summary).
