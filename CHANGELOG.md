# Change log

## 2026-11-18

The model's response to price checked against four measurements (`demand_checks.py`, `research_notes/demand_checks.md`; **no
default changed**)
- Prompted by Knowles 2026 on plant-based meat's prices. Plant-based meat's own-price elasticity is -1.23 in US retail data
  (GFI, as cited); the model's is -2.85. Sixteen premium meats fit a price sensitivity of 2.2 times meat's against the model's
  8.5. Farmed salmon responded 1.0–1.5% per 1% of price against the model's 3.0–3.4% for premium beef and seafood. Only the one
  choice experiment the model was set to agrees with it. So the model is probably two to four times too price-sensitive.
- Across the price responses the measurements point to, Central's share runs from 0.04% to 1.9%: the demand side is now the model's
  widest uncertainty. The curve that passes all four checks (slope and level from the premium meats) gives Central 0.1% and the
  best case 1.8%. Moving the default to it is the next step (TODO).
- Also: a plant that sells 60% of its capacity makes Central's cells cost $35.38, not $29.42 (`market_size_loop.underused`);
  plant-based meat at price parity would change cultivated meat's share by under 3%.

The premium markets sized from data, and the checks on the market-size loop (`meat_market.py`, `research_notes/premium_market_sizes.md`,
`market_size_loop.py`; **defaults changed**)
- Pablo asked for the loop study's checks to be done and its unknowns found. The first check found a fault in the main model: the
  premium rows of the market tables were unsourced and several times too large. Sushi-grade seafood is about 1.2 Mt a year in the world
  (the Global table had 5.4), prime or wagyu beef at $45 or more about 0.5 Mt (1.35), heritage pork and organic chicken about 0.4 Mt
  each (1.35 each). The Global, US and Europe rows were resized; what was removed went to the same species' cut row. China and the
  low-income tables were not checked.
- **Central's long-run share falls from 0.16% to 0.04% of world meat** at its point cost (median 0.02%, was 0.1%), because nearly all
  its sales were to those rows. The best case moves from 3.7% to 3.1% (median 0.5%, was 0.8%); the US at Central from 0.35% to 0.21%.
  Costs are unchanged. Shares under 0.1% are now printed with two decimals in the tables and on the page.
- Anchored on premium real meats, Central is 0.14%: the earlier agreement with the model (0.16% each) was a coincidence of the oversized
  rows. With premium buyers, Central is 0.17% (0.38% with a strong no-killing value).
- The loop study, revised: with real premium markets Central's sales need 0.64 million m² of membrane a year, short of the million
  taken to bring a food-grade supplier, so Central has two resting points ($28.81, or $20.52 and 0.14% if the cheap membrane exists
  anyway). The best case still reaches parity ($6.11, 10.91%). The food-grade membrane's first price is now $150 a m² (was $250) and
  its floor $50 (was $60), from the prices of water and dairy modules; no steam-tolerant food-grade price is published.
- Other checks, recorded in the note: hollow fibres have held 27–35% animal cells by volume for over two weeks at 4 L (nothing for a
  month above bench scale); the model's premium products respond to price two to three times more strongly than farmed salmon did
  along its demand curve; a hundred-fold scale-up took such industries 15–30 years when it happened.

Cost falling as the market grows, solved with the share (`market_size_loop.py`, `research_notes/market_size_loop.md`; **no default
changed**)
- Pablo's idea: membranes and reactors get cheaper with market size, and the loop starts in premium products that cultivated meat
  comes to undercut. The membrane ($1,450 a m², a pharma price) switches to a food-grade supplier at $250 once demand passes a million
  m² a year, then falls 18% a doubling to $60; the plant falls 10% for each doubling of installed animal-cell tanks, to a microbial
  plant with what animal cells need. Seven new inputs (`ms_*`), used only here.
- Resting points: Central $19.86 and 0.45% of world meat (from $29.42, 0.16%); the best case $6.16 and 11.26% (from $9.66,
  3.69%), which is parity. Today's cells are stuck. Without a food-grade membrane supplier little moves.
- At Central's cost 99% of sales are premium products (sushi-grade seafood, prime beef); their volume alone crosses the membrane
  switch in the central case, not with slow learning, where Central has two resting points.

Cultivated meat as an even more premium meat, competing with welfare labels (`premium_buyers.py`, `research_notes/premium_buyers.md`;
**no default changed**)
- Pablo's idea: shoppers may see cultivated meat as a step above organic or free-range, but it then competes with those labels for the
  same shoppers. Adds a premium class of shoppers (10%, from household panel and survey data; range 5–20%) fitted to the sixteen
  premium products, and a welfare label at 2× on every non-premium shelf, competing with cultivated meat in one logit.
- Central's long-run share 0.29% (main model 0.16%); 0.51% if premium buyers value no killing at a whole extra meat price. Best case 4.61%
  (3.69%). The label on the shelf costs cultivated meat little (0.33% without it). It takes 11–16% of its sales from the label under the
  logit's proportional assumption, up to about half if the two are close substitutes.
- Caveat: the premium class's low price sensitivity is a fit across products; scanner data find organic meat demand more price-elastic.

The shelf price is now per-kg costs plus the shop's percentage margin (`retail_spreads.py`, `research_notes/retail_markup_form.md`)
- Question (Pablo, after Gemini argued the markup should be multiplicative): is the step from a kilo of cells to the shelf a fixed
  $/kg or a percentage? Neither alone. USDA ERS monthly meat prices (1970–2025) show shop prices moving about dollar for dollar with
  wholesale prices over one to five years (beef 0.99–1.17, pork 0.77–0.92, broilers 0.78–0.84), far from the 1.7–2.5 a pure
  percentage would give. But shops set a percentage gross margin (US meat departments 28–32%), which a new, permanently dearer
  product would carry in dollars.
- New rule: shelf = (cost + `markup_add`) / (1 − `retail_margin`), with `markup_add` $2.5/kg (was a flat $5; range $1.5–3.5, was
  $3–8.7) and the new `retail_margin` 28% (15–40%). Fitted to USDA's 2025 spreads at 28%, the per-kg part is $1.6 for broilers and
  $2.9 for beef; the $2.5 adds about $1 for forming cells into a product. Both are drawn in every uncertainty band. One function,
  `price_ratio.shelf_price`, carries the rule in Python, `shelfPrice` on the page; the page gains a shop-margin slider (0 and $5
  give the old flat rule).
- What moved: parity needs cells at $6.14 (was $7.00). Shelf prices of anything above parity rise: Central $44 (was $34), best case
  $16.9 (was $14.7). Long-run share of world meat at the point cost: Central 0.16% (was 0.41%), best case 3.7% (was 8.0%); medians
  of the bands: Central 0.1%, best case 0.8% (0.2–3.4%, was 1.9%). The demand calibration is unchanged (its anchor price is
  frozen). The premium-meat anchoring now gives Central 0.16% (agrees with the model) and the best case 1.8% against the model's
  3.7%. Costs per kg of cells are unchanged.
- Gemini's further claim that margins rise with the quality tier is unsourced, and the one comparison found (French Label Rouge
  chicken 25% against a standard fillet 36%) runs the other way; the 40% end of the range covers a slow-selling niche product.

## 2026-11-17

Pasitka 2024: the mass-basis finding worked through (METHODS and comments only; no number moved)
- The paper's own figures for the mass of a cell disagree: 0.55 ng (10 μm, Extended Data Fig. 4b), 3.3 ng (130 × 10⁶ cells per ml =
  43% w/v) and 9.8 ng (1.7 kg from 173 × 10⁹ cells). Worked through from its figures, the most likely explanation (about 70%) is that the
  cells are 10 μm as reported and both mass figures are counts times a fixed cells-per-gram factor, not weights of cells: the
  micrographs show 9–11 μm cells against their scale bar; the counts match density times harvested volume; 1.7 kg cannot be a pellet from
  about 8 L of culture holding 90 mL of cells; the 2023 paper's "36% w/v" at 108 × 10⁶ has the same ratio as the 43%; and the glucose
  burned could not build 1.7 kg of cells (it fits 0.3–0.65 kg for cells like the model's, the one piece that leans above 95 g). So about 95 g of cells in the 1.7 kg, as METHODS first said, now with the reasoning and the
  odds. A bound that does not depend on cell size (81 g of amino acids per kg of biomass) gives at least 2.5.
- Knock-on recorded in TODO: `sc_glc_measured` draws partly on the paper's per-kg-of-biomass glucose figure.
- Dropped as evidence: Supplementary Table S5's two nutrient costs differing by exactly 100 (more likely a units artefact than "1% protein").
- The decision to drop the paper as the anchor stands: its medium use and plant output scale from the same 10 ng, and even at 3 times
  too wet its $23–26 per kg of wet biomass is $70 or more per kg of cells before capital. The back-test row in METHODS now gives both
  readings (density 72 or 240 g/L against 430 claimed).

Cultivated meat anchored on premium real meats (`premium_curve.py`, `research_notes/premium_curve.md`; **no default changed**)
- Pablo's idea: premium real meats are "real meat plus a virtue, at a premium"; fit the curve they trace and place cultivated meat on it,
  corrected for what differs (no killing, novelty, unnatural).
- Data: ten more premium/share pairs up to 3.6× (`research_notes/high_premium_analogues_data.md`: US eggs by label, organic and
  Label Rouge chicken in France, Britain, Denmark and Switzerland, Austrian organic eggs, Ibérico as a sensitivity). Share falls with
  the premium in every within-source comparison, but far more slowly than the model's curve, which misses the sixteen products by a
  factor of about 6; a fitted curve (shoppers a quarter as price-sensitive, held to the measured at-parity elasticity) misses by 2.4.
  No sign of a loyal niche paying whatever the premium.
- Corrections (`research_notes/cultivated_vs_welfare_meat_evidence.md`, hypothetical studies): no killing +5% of meat's price, novelty
  −30% (half fades), unnatural −20% (likely persists).
- Result: Central 0.40% of world meat in the long run (0.18–0.63%) against the model's 0.41%, an independent check that passes. The best
  case 2.5% (1.2–3.9%) against 8.0%: near parity the two disagree, and the premium data do not reach there.
- `market_share.share(..., slaughter_free_x=1.0)`: an optional switch so a product can be real meat without counting as slaughter-free;
  the default is unchanged. `tests/test_premium_curve.py`, in `run_tests.sh`. RESULTS has a paragraph, and its old line about a
  small group paying whatever the premium is corrected.

## 2026-11-16

Page: where the cost goes (`page_scenarios.js`, `scPartsSVG`; no number moved)
- Under the scenario result, a bar of the cost of a kilo of cells split into six parts (medium, growth factors, bubble protectant,
  filter membranes, running the plant, the plant's capital charge), drawn in dollars so it shrinks as the switches lower the cost,
  each part labelled in dollars and share where it fits. A bracket marks the four parts that scale with the litres of medium;
  ticks mark parity and Central. A list gives each part's dollars, share and change against Central (against the best case when
  Central is chosen). Colours follow the repo's figures and pass a colour-blind check.

Wider bands, and a flaw in the demand model fixed (**headline bands move; no point cost moves**)
- **Bands** (`scenarios.MC_ESTIMATES`, switch `sc_wide_bands`): the scenarios' cost bands now also draw the estimates the cost rests on
  most, each from its own prior: the ammonia the cells tolerate, the protectant's price and dose, the least medium flow, antifoam's cost
  to oxygen transfer and the membrane price. Not drawn: glucose use (a cell trait, held by the switch), salt tolerance (no effect on
  the median, forty times slower), gas flow (a switch).
  - Central $27–38 → **$25–47**, median share 0.2% (unchanged); best case $9–12 → **$10–19**, median share 3.8% → **1.9%**;
    Humbird's design 2.4% → 1.3%. The best case's point cost now sits at about the 4th percentile of its draws.
  - `pf_protectant_price` range 10–260 → **10–120** $/kg: at the catalogue price as the top, the draws' median tonne price was $87.
- **Demand flaw**: `_derive_beta` splits price sensitivity between a dollar channel (income-scaled) and a ratio channel and pins their
  sum at one anchor. Loss aversion above about 1.6 drove the dollar coefficient positive (paying more raised utility), which made
  Central's share rise with loss aversion (0.4% → 1.4%). The coefficient is now capped at zero, in Python and on the page; inert at the
  defaults. The remaining sensitivity to how price splits between dollars and ratios (0.3–0.7%) is recorded as open.
- `answer_rests_on.py`: the band column follows the new draws; the gas-velocity row is left out with the reason (it only rescales
  Humbird's oxygen reference). RESULTS prose, the scenario tables in RESULTS, METHODS and `cost_scenarios.md` updated.

Consolidation: what the answer rests on, and every side study on the current model (`answer_rests_on.py`; **no scenario moves**)
- **What the answer rests on** (`answer_rests_on.py`, a section near the top of RESULTS): every input with a range is moved to
  each end, one at a time. Of 513 inputs (237 with a range), 14 move Central's or the best case's cost by $1 or more and 8 move
  Central by more than $3. The four largest (the ammonia the cells tolerate, the cell filter's life, the protectant's price, the
  least medium flow) have not been measured on meat cells. 11 of the 14 are not in the scenarios' uncertainty bands, so Central's
  band ($27–38) is too narrow. On the demand side, no single input takes the share at Central's cost outside 0.1–1.4%; at the
  best case's cost the same inputs span 1.5–15.6%. `tests/test_answer_rests_on.py`.
- **RESULTS summary**: the revision history at its top is replaced by a four-sentence answer (the history is in this file).
  The bands paragraph says which large inputs the bands leave out. The disc-stack sentence now gives its cost ($26.85 in Central).
- **The seven side studies that ran on a snapshot of an older model now run on the current one** (`tests/_snapshot.py` removed):
  tank size, thick culture, without perfusion, cell retention, nutrient floor, growth-factor and doubling bounds, the least medium
  per kg. Tests re-pinned, notes' tables and prose recomputed. What changed in their conclusions:
  - tank size: 20 m³ is within 0.5–1.8% of the cheapest size (was 0.5%), except the cautious case, 4.6% at 111 m³;
  - thick culture: only the best case reaches 258 g/L; in Central oxygen with the culture's viscosity binds first (151 g/L), so a
    thicker-culture limit is worth nothing there;
  - doubling bounds: "past 16 hours, speed adds little" no longer holds for Central (16 → 8 h saves $3.1), because oxygen now
    limits the density of fast cells;
  - cell retention: Central's filter duty is 8 times the reference's (was 12); the cautious case can no longer run all three tank
    tricks at 180 g/L;
  - without perfusion, the nutrient floor and the least medium per kg: levels move, conclusions hold.
  Probabilities in these notes were judged on the older model and not judged again; the notes say so where it matters.
- Stale quotes fixed in the frontier, audit, design-tricks and TODO notes, the dialyser input's note and the centrifuge text.

The medium cannot be less than the culture that leaves with the cells (`explore`, a medium term "harvest"; **no scenario moves, four side figures do**)
- Cells in suspension are harvested with 1000 / density litres of culture per kg. `explore` let the medium fall below that in thin
  cultures of low-waste cells. It is now a term of the medium balance, in Python and on the page (shown as a bar in the lever
  panel), and a medium figure set by hand is raised to it. Cells on a support are exempt.
- No scenario or tier moved. What did, all thin cultures:
  - the airlift in perfusion: $14.78 → $15.07 in the reference case ($79.17 → $81.94 with today's cells), at 79 g/L;
  - the tank-size study's reference at 100 and 200 m³: $14.59 → $15.02 and $17.30 → $18.29 (its note had said the reference was
    low there by exactly these amounts);
  - the gas-exchange study's cheapest design at 1 mm/s: $17.18 → $17.57;
  - the frontier: $6.85 → **$6.86**, with the steps after "cells double in 16 hours" up by $0.36 (faster cells run thinner);
  - the design search's "medium at the least the physics allows" for today's cells: saves $6.2, not $14.8, because 21.6 litres
    leave with each kg at 46 g/L.

Page: two fixes Pablo asked for
- **"Cost against the price of medium":** labels overlapped and rung 1 ($63) was off the top. The scenarios and the parity line
  are now named in a column at the right, spaced apart, with the axis reaching the dearest scenario.
- **"Selected on a low-waste feed" and "the best meat cells measured" cost the same** in every scenario: they differ only in
  lactate, and ammonia sets the litres of medium for both. Both options now say so. Rung 3's gain over rung 2 ($30.73 → $29.42)
  comes from faster growth (43 → 36 h), not from less waste.
- **Rung 3 renamed** "3. Plus cells selected to grow faster on the low-waste feed (Central)" (was "selected for low waste"); its
  story and the prose in RESULTS and on the page say where its $1.3 comes from. The figure's label column widens to fit.

Cleaning and reusing the medium (`medium_reuse.py`, `research_notes/medium_reuse.md`; one lever corrected, no scenario moved)
- Question: can the ammonia be taken out and the liquid reused (project G)? Method: a liquid balance per kg of cells (fresh medium
  bought, litres cleaned and returned, litres through the cell filter), priced with `explore`, for an ammonium exchanger,
  electrodialysis, dialysis with a thrown-away or a cleaned dialysate, and dialysis across the culture; each route cleans the litres
  that cost least. New inputs `mr_*`, each with its source and range.
- Finding: the liquid a device on the permeate cleans has passed the cell filter either way, and the filter is $0.38 of the $0.75 a
  litre costs in Central. So permeate-side reuse saves $2–4 a kilo (limit $7.3); dialysis across the culture saves $4.4–8.5
  (limit $14.8) if its membrane holds up, which nobody has shown. The evidence is one cited report, one bench study and patent claims.
- **Correction:** `explore`'s `sorbent` lever lowered the litres through the cell filter along with the fresh medium. It no longer
  does (Python and page). No scenario uses the lever; golden figures unchanged. A sorbent taking half the ammonia takes Central to
  $28.22, not $22.97; the best share (42%) gives $27.01.
- `tests/test_medium_reuse.py`, in `run_tests.sh`. RESULTS has a section; METHODS' lever table and the page's sorbent note say the
  filter is not saved.

Every scenario holds dissolved oxygen at half of air saturation (`scenarios.always`, `sc_do_setpoint`; **numbers move, down**)
- Humbird's oxygen transfer implies a tank held at 0.28 mmol/L (130% of air saturation). Pharma holds 30-50%. The scenarios now hold
  0.10 mmol/L (about 47%), which widens the oxygen driving force and needs nothing new. Found by `design_space.py`. Humbird's optimistic
  design keeps his level. Switch `sc_do_scenarios` = 0 restores the earlier figures; the side studies' snapshot tests use it.
- Scenarios (designs chosen again): rung 2 $31.33 → $30.73, Central $29.92 → **$29.42** (191 g/L, oxygen), with shared medium $26.81 →
  $26.56, best case $9.71 → **$9.66** (now at the thickness limit, with recycled oxygen and a squat tank), forecast $25.04 → $24.80.
  Median shares unchanged to one decimal. The first change in this model's history that lowers a headline.
- Recomputed with it: the frontier ($7.03 → $6.85, just under parity), filter flux (Central $48.59 at 1,200 L/m², $94.63 at 450), the
  audit (Central's median over all ranges $36), the company-claims split, the design search (the setpoint is no longer an option: 144
  designs), the vessel grid, RESULTS, METHODS and the notes' ladder sections.
- Vessel grid: a vessel whose column loop fails its checks at full density now runs thinner until it passes (`vessels._thinned`,
  mirrored on the page), in place of dropping the tricks. Central in an airlift: $30.88 at 139 g/L.
- `scenarios.interactions` breaks ties by the switches' order, so Python and the page sort alike.

How far tank design can go (`design_space.py`, `research_notes/design_space.md`; no default changed, no number moved)
- Method: price each limit first (`limit_prices`: the cost if CO₂, oxygen, mixing, the thickness limit, the litres of medium, the
  membranes and others were free), then search every combination of the tank options the model has (288 designs a scenario, under two
  seconds for all), keep those whose column loop passes its checks, and compare with the ordinary tank with every gas limit lifted.
- Findings: tank design is worth $28/kg for today's cells ($62.96 to $34.80) and $1.4–2.8 beyond the scenarios' own designs from
  rung 2 on ($0.4 in the best case). Designs that leave only the thickness limit binding exist: a bubble cage with 1 bar, or 2 bar
  without a cage. Holding dissolved oxygen at half of air saturation is standard practice, unused by the scenarios, and worth $0.5 in
  Central. After the gas limits, the litres of medium dominate ($15.7 in Central against $2.2 for perfect gas exchange).
- The search reproduces every scenario's own tank design exactly. `tests/test_design_space.py`, in `run_tests.sh`.

Bioreactor design tricks and a CFD plan (`research_notes/bioreactor_design_tricks.md`, `research_notes/cfd_plan.md`; no number moved)
- A catalogue of tank design tricks by what they relieve (CO₂, oxygen, mixing, salt, heat), whether something fundamental stops them
  scaling (surface-to-volume, depth, flow-path length, foam, regulation), and where each sits in the model. Today's cells are CO₂-bound;
  Central and the best case are oxygen-bound, so oxygen per watt (two spargers, impellers, antifoam) is now the lever. Not yet in the
  model: two spargers, gas exchange on the filter loop. Perfluorocarbon oxygen carriers are PFAS, close to a non-starter for food.
- The CFD plan: four steps from validation to bubbles, each replacing a named model input. FluidX3D v3.9 builds and runs on the Apple M4
  (505 million updates a second in 32-bit, 766 in 16-bit; one buffer of at most 2.27 GB caps the grid at about 30 or 60 million cells).
  The laminar pipe-flow check converges to 0.16% error in 32-bit but stalls at 23% (FP16S) and 15% (FP16C): use 32-bit for validation.

A stirred tank with a bubble cage (Pablo's design; `vessels.py` row "caged", inputs `vm_cage_*`; no scenario uses it, no number moved)
- An inner cylinder of fine mesh holds a strong sparger; the cells live in the ring around it with the scenario's own soft bubbling.
  The cage's gas (6 mm/s over the tank, 3-12) adds to the ring's, discounted to 80% (0.5-1) because only medium crosses the mesh;
  capital 1.15x a stirred tank. All three are judgements; caged aeration is known only with microcarriers in small tanks.
- Perfusion: reference $11.08 (plain tank $12.51), Central $27.72 ($29.92), today's cells $39.23 ($62.96).
- `vessels_and_modes.md` section 9: the design, the gas-filled variant (a membrane: about 9 m² of wall against 1,200-1,500 m² needed
  for CO₂), and a table of other ways to keep bubbles from cells. RESULTS' vessel table gains the row. `floor_physics.explore` reads
  two new vessel keys, `co2_mult` and `no_protectant` (unused by any row now), mirrored in the page.

Restart from a neighbouring tank (`sc_restart_neighbour`, a fourth setting of "Restart after a loss"; no scenario uses it, no number moved)
- A lost tank reseeded with half the culture of a healthy neighbour: 4 days (3-7) in place of 14 with a fresh seed train, which needs
  about 7 doublings. Worth $0.8 a kilo in Central, $5.6 for today's cells (rung 1, which restarts in 21 days). The donor must test clean.
- The page explains why the company sliders are locked and when oxygen, not CO₂, limits the tank (PR #36).

The scenarios as a ladder ordered by difficulty (`scenarios.LADDER`, `PAGE_ORDER`; Pablo's review; no cost of an existing scenario moved)
- Five rungs, each adding one kind of change: 1. today's measured cells in an ordinary tank, no tricks, today's prices ($63.0);
  2. plus process changes and cheaper inputs ($31.3; the tank tricks alone are worth $19.2); 3. plus selected cells = Central ($29.9);
  4. plus a plant with shared medium ($26.8); 5. plus engineered cells = the best case ($9.7). A forecast row for 2035 ($25.0, median
  share 0.3%) is a first draft of the author's medians, with the odds behind each in RESULTS.
- The reference is renamed "Humbird's optimistic design" and sits beside the ladder: it assumes engineered cells and no tank tricks.
- Every row of the headline table gives the share at its point cost and the median of draws (`bands(None)` for Humbird's design,
  `reported_band` for the company's process), so rows compare: Humbird's design 2.4% median, best case 3.8%.
- `ORDER` keeps the four scenarios the side studies use; `cautious` leaves the page. Page prose, RESULTS, METHODS, README,
  `cost_scenarios.md`, the company-claims table and tests follow. Roadmap: CFD target A5, oxygen transfer per watt for impellers and spargers.

Model audit: drift, accuracy and whether the costs are reasonable price points (`audit.py`, `audit_history.py`, `research_notes/model_audit.md`; no default changed; recomputed after PR #32)
- **Drift:** measured at every commit that touched the cost code. Default $24.01 -> $34.35 (14 Nov), Central $18.14 -> $26.64 -> $29.92, best $6.57 -> $8.95
  -> $9.71 (15-16 Nov). Every step that moved a headline added a cost an earlier version left out; none lowered one.
- **Accuracy:** the model needs 1.2 to 2.8 times less medium than every reported perfusion run and predicts 2.3 times the output of the one
  working 20 m3 plant. Drawing every documented range at once, Central's median is $37 (10th-90th percentile $27-51; the $29.92 point is at the
  19th percentile) and the best case's is $15.1 ($9.71 is the 1st percentile).
- **Shelf price:** a flat $5 markup gives Central $35; a markup proportional to the price (as conventional spreads are) gives $56 and lowers the
  cost at which cultivated meat reaches parity from $7 to $5.6. New inputs `au_retail_share`, `au_processing`. `tests/test_audit.py`, in `run_tests.sh`.

Can a filter hold 5 L/m2/h at 25% cells? (`filter_flux.py`, `research_notes/filter_flux.md`; no default changed)
- The physical ceiling (shear-induced back-transport, as printed in two theses) is 57 to 800 L/m2/h for the model's cells: 5 L/m2/h is not above it
  (under 5% in my judgement). The limit is fouling: CHO membranes fouled after 450-1,200 L/m2 (Pinto 2020, Veje 2024, read in
  full), 3 to 9 times below the default 3,960. At those throughputs Central costs $49-94 and the best case $15-29 (recomputed after PR #32). The flux
  itself barely moves the cost (about $0.2 for halving it); the membrane's throughput does. `tests/test_filter_flux.py`, in `run_tests.sh`.

The frontier: every lever at its limit (`frontier.py`, `research_notes/frontier.md`; no default changed; recomputed after PR #32)
- Central ($29.92) with one lever at a time moved to the limit its research note supports, each kept moved: least medium 6.4 L/kg
  $14.27, 16 h doubling $10.32, shared-medium plant $8.38, 0.2% losses $8.02, gas 6 mm/s **$7.03** ($7.83 with GFI's amino-acid floor).
  At the $7 that parity needs, not below it. With antifoam counted oxygen binds at 177 g/L, so 320 g/L adds nothing ($6.33 without the
  antifoam effect). The litres of medium per kilo are the lever: they set the medium, growth-factor and filtering costs together.
- Growth factors returned by the filter: the share charged is now capped at what is charged without the filter. Once the medium is cut
  to 6.4 L/kg the bleed carries out as much liquid as comes in, and the uncapped formula made returning the proteins cost more.
- `tests/test_frontier.py`, in `run_tests.sh`.

The model against company cost claims (`industry_claims.py`, RESULTS section 1, the page's evidence section; no number moved)
- Each scenario split into the yearly charge on the plant and operating cost. Company figures are operating cost (COGS); the
  scenarios include the plant. Central: $29.9 = $8.2 plant + $21.7 operating, of which $8.2 filter membranes.
- Central's cells in a 20 m³ tank drained and refilled (as Vow runs): operating cost $13.7–14.0, inside the $10–15 an investor reports
  for several companies (Lever VC, NDA data). The plant charge is $9–33 depending on the plant; in a yeast plant with what animal cells
  need, $23.3 in all, below Central in perfusion. At the 27 g/L reported for meat cells, $51–103.
- A table of six claims with their basis (what it is a cost of, capital in or out, model or run, who checked it).
- `tests/test_industry_claims.py` (in `run_tests.sh`) checks RESULTS carries the tables and the figures its prose quotes.

## 2026-11-15

Three costs counted, the plant ladder tied to `explore` (Pablo asked for the long-term choice on each; **numbers move**)
- **Bubble protectant** (poloxamer 188): new inputs `pf_protectant_dose` (2 g/L, 1–5) and `pf_protectant_price` ($30/kg assumed, $10–260;
  catalogue $230–260), charged per litre of medium in every sparged vessel; `explore(protectant_price=)`, a tornado bar, the JS mirror.
- **Antifoam**: `pf_antifoam_otr` default 1 → **0.75** (the middle of the reported 0–50% cut; judgement). Oxygen now limits Central (177 g/L)
  and Cautious.
- **Yeast-style plant buys its oxygen** (`pi_o2_feed` × `pi_o2_price`, $0.33/kg), as item-built plants already did; switch `pf_o2_microbial`.
- **The plant ladder's perfusion rows are `explore()` itself** (filter loop, protectant, oxygen), so they cannot drift again: reference
  tier $11.5 → $12.5 (first plant $14.1 → $14.8), microbial tier $6.6 → $8.0. `plant_floor` 9.8 → 10.8, `plant_floor_lo` 4.9 → 6.3, the
  `overhead` range starts at 10.8. Golden `cost_floor` 11.502 → 12.502.
- Scenarios (designs chosen again): best $8.95 → **$9.71** (R 1.23, median world share 3.8%), central $26.64 → **$29.92** (R 2.91, 0.2%),
  central with shared medium $24.34 → $26.81, cautious $38.97 → $43.79, reference $11.84 → $12.51. Best case and Central now use the column,
  1 bar and a tank as deep as wide (recycled oxygen fails the loop checks); Cautious the column and 1 bar in the tall tank.
- The default's Monte Carlo: R median 3.27 → 3.29; regional bands updated.
- Docs: RESULTS (summary, cost table, the cells-by-tricks tables and the gas-cap table recomputed: they still carried pre-filter-loop
  figures, e.g. bovine cells with glutamine replaced at $17.5 where the model now gives $26.2), METHODS (scenario, tier, tornado, CO₂, species,
  floor Monte Carlo tables: the last still showed a median of $18.6), `cost_scenarios.md`, `vessels_and_modes.md`, `gas_flow_cap.md`.
- **Side studies are now snapshots with a stated basis**: `floor_physics.BEFORE_PROTECTANT` / `BEFORE_FILTER_LOOP` and `tests/_snapshot.py` run
  their tests with the settings their notes were computed with; each note says so at the top and gives the current scenario costs.

Housekeeping (`TODO.md`; no default changed, no headline moved)
- **`TODO.md`**: one list of open PRs, decisions waiting on Pablo, housekeeping and project ideas; `research_notes/roadmap_2026-11-15.md`
  keeps the reasoning for the projects.
- Two new levers from the gas-flow follow-ups, each with a tornado bar and the page mirror (parity holds):
  `explore(strip_eff=)` (CO₂ carried off by the exhaust gas, 0.70–0.96; at 0.70 the reference holds 87 g/L and costs $13.60) and
  `explore(antifoam_otr=)` with new input `pf_antifoam_otr` (default 1, range 0.5–1; sparger oxygen only). Halved, the reference
  becomes oxygen-limited at 97 g/L ($12.88) and Cautious goes from $38.97 to $50.58.
- Poloxamer 188: catalogue price only (~$230–260/kg); at 2 g/L that is $5.6–14 a kilo of cells. Not added; in `gas_flow_cap.md`
  and TODO.md as a decision.
- Notes recomputed with the filter loop: `cost_scenarios.md`, `vessels_and_modes.md` (every figure). `cheap_plant_study.md` and
  `gas_exchange_study.md` stay dated snapshots (their tests pin the old device) with a box of current figures: the tank tricks are
  worth about half as much (the gentler column saves $1.47, not $2.86); the lean plant's break-even loss rate is 3.9% a day.
- `interactive.html` rebuilt (main's copy was older than its source); untracked notes and the growth-rate proposal committed.

Is 20 m3 the right tank size? (`tank_size.py`, `research_notes/tank_size.md`; no number moved)
- Cost against tank size, 2 to 200 m3, for each scenario and the reference, with the tank design (tricks, shape) chosen again at each size
  under the column loop's pH and pass-rate checks. 20 m3 is within 0.4% to 2.3% of the cheapest size: best $8.95 -> $8.82 at 55 m3,
  central $26.64 -> $26.50 at 23 m3, central with shared medium $24.34 -> $24.25 at 34 m3, cautious $38.97 -> $38.08 at 46 m3. The
  20 m3 designs fail the pH check at 23 to 26 m3; without the checks the best case would save 3.4% at 200 m3. Smaller tanks cost
  2% to 4% more at 10 m3 and 20% to 50% more at 2 m3. Labour per m3 is the one assumption that could move the answer (the best case
  would be 7.6% cheaper at 200 m3 if crew per m3 kept falling as in Humbird's plants). Odds for each size are in the note. New inputs
  `ts_ph_relaxed`, `ts_loop_hw_exp`, `ts_hazard_exp` (what-if rows only). `tests/test_tank_size.py`, in `run_tests.sh`.
The least medium per kg of cells that physics allows (`min_litres.py`, `research_notes/min_litres_per_kg.md`; no number moved)
- Waste sets no floor: nitrogen, carbon and energy balances all allow zero ammonia and zero lactate. Delivering the nutrients
  does: 0.58 kg (Best) to 0.64 kg (Central) of amino acids and glucose per kg of cells. If the medium must be what the cells
  sit in, the floor is 14-25 L/kg (Central's 28 is within 10% of it; Best's 11 is not possible). If a concentrate of 100 g/L is
  diluted in the tank, it is 5.8 L/kg (Best) and 6.4 (Central), or 8.0 at the lowest flow per cell measured. Costs at those
  litres: Best $6.94, Central $12.28-13.05, against $8.95 and $26.64. New `ml_*` inputs; `tests/test_min_litres.py`, in
  `run_tests.sh`.
The nutrient floor from GFI's amino-acid prices, and a $0.05 medium setting (`nutrient_floor.py`, `research_notes/nutrient_floor.md`)
- The model's nutrient floor ($1.70 a kilo) is below every figure GFI's December 2025 prices give ($2.50 to $16.09): its amino acids
  are $0.67, against $1.48 at GFI's cheapest tier. The best case, whose medium is set by the floor, would cost $9.76 to $12.36 at
  the cheaper tiers (now $8.95); Central does not move unless amino acids are dear. No default changed.
- New "Price of the medium" setting: **$0.05 a litre**, an aspiration tagged "feed or process". Central at $0.05: $22.68 (the floor
  binds). The best case keeps $0.15, and its rule text says so. "What decides it" for Central now shows the medium price worth
  −$3.96 at its best setting.

What GFI reports about the cost of medium (`research_notes/medium_cost_gfi.md`; no number moved)
- GFI's December 2025 amino acid analysis and January 2023 growth factor report, read in full: amino acids $0.02-0.17 a litre against
  $0.24-0.54 on Humbird's prices; Humbird's amino acids about $18-19 a kilo of cells; company reports of $0.20, $0.07 and $0.63 a
  litre. The model's Central case matches GFI; the best case's medium ($1.72 a kilo, 11 L/kg) sits below it.
- **Correction:** the tier "Humbird fed-batch, as designed" uses the model's feedstock (his cheaper bulk hydrolysate), not his own
  medium cost, which was far higher. The name was not changed.

If perfusion cannot be run at 20 m3 (`downside.py`, `research_notes/no_perfusion_downside.md`; no number moved)
- Each scenario priced in a stirred tank without cell retention, in fed-batch and in fill-and-draw, at the model's own density cap
  and at the 27 g/L shown for meat cells, with the tank design chosen again. Central: $26.64 with perfusion, $40.39 (fed-batch) or
  $43.58 (fill-and-draw) at 62 g/L, $90-97 at 27 g/L. Best case $8.95 -> $13.22 at 92 g/L, $41 at 27 g/L. The food-grade plant with
  shared medium cushions it most ($24.34 -> $28.22). `tests/test_downside.py`, in `run_tests.sh`.

Cheaper membranes for holding cells back (`research_notes/retention_alternatives.md`; no default changed)
- Three routes priced in `retention.py`, from a research pass on reusable and cleanable membranes (new `rt_reuse_*`, `rt_dial_*`,
  `rt_ceramic_*` inputs, each with source and range). Central case, against $26.64 with the default TFF loop: dialyser-grade
  hollow fibres $18.00, ceramic membranes run as a slow TFF loop $19.14, reused pharma modules $20.72. Nothing has been run with
  animal cells at this density for any of them; the odds the central case gets a tenfold cheaper membrane are about 15%.
- Wastewater and food-industry membranes are listed as not costed, with reasons. Dialysis with a cleaned dialysate and cells held
  back without a filter were not researched.

Does a thinner culture pay once filtering costs money? (`retention.density_scan`; no number moved)
- No, for the best, central and shared-medium cases: their tank designs, chosen again under the filter cost, are unchanged, and
  holding the culture below the density the tank allows saves membranes but costs more plant capital per kilo (central: $28.75 at
  180 g/L against $26.64 at 258). The cautious case would save $1.10 at 180 g/L with all three tricks; there is no density
  setpoint switch, so the model does not use it. Membrane life moves the central case by about $30; density barely does.

The filter loop is the model's default (Pablo's decision; numbers move)
- `floor_physics.explore` now prices the device that holds cells back in perfusion as a TFF hollow-fibre loop: hardware per m² of
  membrane sized on the cell-free liquid the bleed does not carry out, plus membranes at about $0.37 a litre filtered. A number
  for `retention` still charges a flat capital and no membranes. `rt_tff_default = 0` restores the old hoped-for device.
- Scenario costs: best $6.57 → **$8.95** (R 0.96 → 1.16: **no scenario reaches price parity now**; median world share 7.9% →
  4.4%), central $18.14 → **$26.64** (0.8% → 0.3%), central with shared medium $15.84 → $24.34, cautious $32.29 → $38.97,
  reference $11.48 → $11.84. The scenarios' tank designs did not change.
- The tornado's retention row is now the life of the filter membranes (5,500 to 900 litres per m²); the widest bar at the reference
  case is now the waste the cells make. The reference-case and scenario Monte Carlo runs draw the membrane life in place of a flat
  retention capital (floor Monte Carlo median $18.6 → $25.7).
- Pinned values updated in `test_floor_physics`, `test_scenarios`, `test_vessels`, `test_retention`. The gas-exchange and
  cheap-plant tests check their notes with the old device; those notes, `cost_scenarios.md` and `vessels_and_modes.md` carry a dated
  line saying so. RESULTS (summary rewritten: no parity, the filter as a cost driver) and METHODS (scenario table, tornado table,
  the default device) follow. The tier ladder keeps the old device.
- The page's JavaScript mirror prices the same loop; parity holds.

Holding the cells back in a 20 m3 perfusion tank (`retention.py`, `research_notes/retention_devices.md`; no default changed)
- The duty from the model: the reference case clears 0.16 m3/h of cell-free permeate (the bleed carries most of the liquid);
  the central case clears 1.88 m3/h from a culture that is a quarter cells; the best case 0.86 m3/h.
- Each real device sized and costed (`rt_*` inputs, each with source and range). Reference case: $10.82-12.25 with any device
  that works, against $11.48. Central: $25.69 (disc-stack separator, 28% of cells burst) to $30.43 (ATF), against $18.14; range
  $21-80. A settler is not possible at 258 g/L; acoustic devices and hydrocyclones are beyond what has been shown.
- Membranes, not hardware, set the cost of filtering the central culture: about $0.37 per litre of permeate, $8.83 a kilo.
- `tests/test_retention.py` (balances, the default reproduced exactly, sizing rules, ranges, pinned headline), in `run_tests.sh`.

Densities not shown for meat cells (no number moved)
- A cell tagged "done at this size" now says "This density is not shown for meat cells" when its density is above the 27 g/L
  reported for meat cells in a vessel of 1 m3 or more (new input `vm_x_meat_shown`: Vow's 538 kg harvest from 20,000 L; range
  27-68 g/L). This flags fed-batch and fill-and-draw in the stirred tank, fed-batch in the bag and the packed bed. The legend
  says the tag is about the vessel, the mode and the size, not the density. The takeaway says the 20 m3 fed-batch and
  fill-and-draw costs assume 62-92 g/L. Python, the JS mirror (parity-checked), the Markdown table, RESULTS, METHODS and the
  research note follow.

Plant names (Pablo's choice; no number moved)
- "A sterile plant without clean rooms" is now **"A food-grade plant"** (Humbird's plant with a sanitary hall in place of the clean
  room). "A lean plant" is now **"A food-grade plant with shared medium"** (the same plant with a shared medium line, two seed
  trains and bought oxygen; nobody has built one). The scenario names follow ("Central: selection and feed only, a food-grade
  plant"; "Central, food-grade plant with shared medium"). The pharma-style plant keeps its name. Internal keys (`lean`, `sterile`,
  `sanitary`) are unchanged. Entries below this one keep the old names.
- The page says above the scenario table and in the vessel section that every scenario uses a 20 m³ stirred tank in perfusion,
  with a continuous harvest, and that nobody has run animal cells in perfusion above about 4 m³.

Vessel types against operating modes (`vessels.py`, `page_vessels.js`, `research_notes/vessels_and_modes.md`)
- **New grid**: five vessels (stirred tank 20 m3, airlift 20 m3, single-use bag 5 m3, packed bed 65 L, hollow fibres 0.5 L) against
  five modes (batch, fed-batch, fill-and-draw, chemostat, perfusion). Only the vessel and the mode change; cells, plant, tank tricks
  and losses are those of the reference case or a scenario. Each cell: cost, density and what limits it, the largest cost item, a
  maturity tag (done at this size / only done smaller / never done with animal cells), or "not possible" with the reason.
- **The modes no longer collapse.** Reference case, stirred tank: batch $62.95, fed-batch $18.20, fill-and-draw $17.81 (unchanged),
  chemostat $33.67, perfusion $11.48 (unchanged). Central scenario: $109.07, $45.29, $48.95, $96.32, $18.14 (unchanged).
- `floor_physics.explore(vm=...)`: a new, optional argument (vessel and mode numbers). Left out, `explore` is unchanged: every golden
  value holds ($11.4801 reference, $18.14 central). The JS mirror `floorExplore` takes the same `vm`; parity is checked over 100 cells
  (reference case, central, best, cautious). `fxCell` now also returns the doubling time.
- New inputs `vm_*` (sizes, airlift shape and oxygen transfer, unit prices, bag/bed/set prices, bed and cartridge densities and cycles,
  batch density, chemostat dilution, restart after a lost cycle, labour exponent, largest perfusion run), each with source and range.
  Bag, bed and set prices are assumptions: no price was found.
- Page: the "Vessel types and operating modes" section is filled. The table follows the switches in "What decides it", with a
  button for the reference case, a one-sentence reading guide, a legend, a plain takeaway, the limits of each vessel and the
  evidence behind each tag. The placeholder from the scenarios work is gone.
- Tests: `tests/test_vessels.py` (anchors, fed-batch against Humbird's formula, chemostat against fill-and-draw, impossible cells,
  expected orderings, golden grid), added to `run_tests.sh`.

Cost scenarios in place of "the floor" (`scenarios.py`, `research_notes/cost_scenarios.md`)
- **The floor is retired as a name.** $11.5/kg was `floor_physics.explore()` at its defaults (a standard 20 m3 perfusion tank,
  120 g/L, a sterile plant, engineered cells, no tank tricks, no lost runs): neither a best case (the best case is $6.6) nor a
  typical one. It is kept, unchanged, as the labelled reference "a standard perfusion tank, no tricks" (`scenarios.reference()`;
  `cost_floor` keeps its name in the code). Every golden value that rests on it is unchanged: $11.4801 in `test_floor_physics`, 11.5020
  `cost_floor` in `test_golden`.
- **Scenarios**: ten switches (kind of cells, growth speed, plant, gas the cells tolerate, tank tricks, tank shape, runs lost, restart
  time, growth factors, medium price), each setting an `explore` argument set with a plain label and a tag for what it needs (genetic
  engineering / selection or adaptation / feed, process or plant / nothing new). Scenarios are presets of the switches:
  best case $6.57 (0.96x, world share 7.9% median, 2.8-17.3%; 15.2% at the point cost, needs genetic engineering), central $18.14 (1.93x, 0.8%
  median, 0.2-2.5%; 1.5% at the point cost; $15.84 in a lean plant, 1.1% median), cautious $32.29 (3.11x, 0.2% median; 0.3% at the point
  cost), the reference $11.48 (5.4%, point estimate), as a company reports $34.35 (0.3%, point estimate). Doubling time is an explicit switch; the
  central case takes 36 h (cost at 30 h $17.80, at 24 h $16.84). Tank design of each scenario = the cheapest the loop checks allow.
- **Review of PR 16 (2026-11-15), the share headline and what the tank design relies on.** The share quoted for a scenario is now the
  **median of its band**, where cost and demand are both uncertain. The 10th-90th percentile sits beside it. The point estimate is kept, labelled.
  Best case 15.2% -> **7.9%** (2.8-17.3), central 1.5% -> **0.8%** (0.2-2.5), central lean 2.3% -> **1.1%** (0.3-3.2), cautious 0.3% -> **0.2%**
  (0.0-0.5). The bands use 4,000 draws (`scenarios.BAND_N`; at 1,000 the best case's median moved by 0.3 points between seeds). No
  cost and no golden value changed. Each scenario now says which tank tricks it uses and what it costs without them (central $23.0, or $30.0
  in the ordinary tall tank; best $7.4 / $9.4; cautious $51.7 / $62.8). The central scenario's story gives the reasoning for 36 h and says what
  24 h is worth ($1.3/kg). `tests/test_scenarios.py` checks the median headline in RESULTS/METHODS/the page and the tricks sentences.
- **New on the page**: the answer table; "What decides it" (switches, live result, what to prioritise, two switches together, which
  switches interact), mirrored in `page_scenarios.js` and checked by `tests/run_parity.py` (16 choices, priorities, interactions, design).
- **Moved (deliberate)**: `floor_physics.explore(growth_factors=)` is a share, not only a flag (`True` still means all; the page's checkbox
  became a slider; tornado range 0 to 1). `cost_model.biomass_cost` is no longer floored at the reference cost (it was never
  reached by the defaults; the page never applied it). The page opens on the central scenario, not on the reference case; its cost
  sliders (medium price, plant running cost, cell efficiency) now start at the reported process and apply only to "As a company reports";
  the Monte Carlo on the page holds the scenario's cost. The "reference plant" label replaces "floor plant" in `PLANT_CONFIGS`.
  The page headline tokens `*_FLOOR*`, `FLOOR_MC_*`, `COST_FLOOR_LEAN` are replaced by scenario tokens. The cells-by-tank grid on
  the page is recomputed from the central scenario (sterile and lean plant; each cell names its limit); the "what stands in the way"
  table is recomputed from the central scenario.
- New inputs (all `sc_*`, with source, range and note): `sc_nh3_*`, `sc_lac_*`, `sc_glc_measured`, `sc_mass_selected_pg`, `sc_td_*`, `sc_gas_*`,
  `sc_hazard_*`, `sc_restart_*`, `sc_gf_*`, `sc_medium_*`, `sc_aspect_*`, `sc_p_top`.
- Docs: README, RESULTS (summary rewritten around the scenarios), METHODS (new section "Cost scenarios"). Numbers that moved in the prose:
  the headline "the floor is about $11.5/kg ... ~5% of world meat" is now the reference row; "price parity needs a cheaper class of plant"
  became "price parity needs the best case or nearly"; the funding list was reordered (better cells first); the lean plant's break-even
  loss rate is about once in 28 days. Section 3's shares by type are unchanged and now labelled "reference case".

Page reorganised (`research_notes/page_structure.md`)
- Order: the answer (scenario table), what decides it, how the cost is built up, from cost to market share, evidence and checks, method and
  sources (collapsed); a jump bar links them. Charts lose their numbers and are named in the text. Each share chart has its explanation under its title,
  in the order of the reasoning (price ratio, how shoppers choose, each kind of meat, how fast).
- New: **Vessel types and operating modes** (`#vessels`): operating mode against plant class for the chosen scenario, and a marked place for the
  airlift, bubble column, batch, fed-batch and chemostat a later session will add. The old mixed list of cases lives on in the method.
- New: cost-model back-test table, "what has and has not been measured", and "the measurements that would move the answer" (each priced from the switches).
- Changed: the all-levers panel (Build your own case) is collapsed, starts from the chosen scenario and has a "Start from a scenario" control; "Use this case"
  sends its cost to the charts. Tank shape slider goes down to 0.5. The scenario table restacks into cards on a phone.
- No golden value moved: `tests/test_golden.py` is unchanged apart from a label ("reference cost").

## 2026-11-14

Gas flow
- What caps the sparge gas flow was researched mechanism by mechanism (`research_notes/gas_flow_cap.md`).
  Humbird's 6 mm/s is a rule of thumb, not a measured limit; the floor keeps it and still costs $11.5/kg.
- Moved: the tornado range for gas flow is 2–9 mm/s, was 2–6, so its bar runs $28.0–8.7, was $28.0–11.5. The
  prior range of `pf_gas_velocity` is 0.002–0.009 m/s, was 0.0006–0.006. No other pinned number moved.
- `explore` reports what the oxygen fed with the sparge gas costs (`gas`, $0.52/kg at the floor) and what
  charging it by gas flow would change (`gas_extra`); neither is added to the total (`floor_physics.oxygen_fed`).

Cost side
- Re-anchored. The default is a company's reported process (SuperMeat 2024) with a yearly charge on its plant;
  Pasitka et al. 2024 is no longer used (its kilogram is mostly liquid and its cost leaves out the plant).
- The floor is derived from physics and published plant costs (`floor_physics.py`), financed like a mature food
  industry: $11.5/kg of cells; $6.6 in a yeast-style plant.
- The CO2 limit on tank density is computed from a gas balance. Further limits: mixing, the energy of growth,
  waste and medium use, salt strength, a least medium flow per cell, contamination.
- Species presets with their own CO2 tolerance; a reconstruction of the one working 20 m3 plant.
- Uncertainty on the floor's own inputs, alone and together with demand; a back-test against reported runs;
  a cross-check of plant costs against other published designs.
- The plant item by item (`plant_items.py`): Humbird's animal-cell plant ($683k per m3) and his yeast plant
  with the same tanks ($130k) rebuilt on one list of nine items, each with options; two new plants in between
  (lean $340k, a yeast plant with additions $175k); the panel's class of plant now sets the items, and they
  can be chosen one by one. Contamination as dynamics (`contamination.py`): time to detection, what is lost,
  and the loss rate at which a cheaper plant stops paying. Write-up: `research_notes/cheap_plant_study.md`.

- Side-study of gas exchange (`gas_exchange.py`, `research_notes/gas_exchange_study.md`): a membrane loop,
  tank shape with the vessel's cost, and a check of a published airlift. Not used in the floor or on the page.
- Tricks as levers (deliberate additions; the floor, $11.48 and 11.16 L/kg, and every earlier number unchanged):
  `explore` gains `column`, `col_pout`, `p_top_barg`, `nh3_kg`, `lac_yield`, `glc_kg`, `sorbent` (+ capacity,
  price, uses) and returns every cap (`limits`) and what sets the medium (`medium_terms`). The page gains a
  "Tricks" group and a "What limits this tank" chart, mirrored in `floorExplore` with nine new parity cases.
  Two new tornado rows: pressure at the top of the tank, ammonia per kg. New inputs `pf_glc_kg`,
  `pf_sorbent_q`, `pf_sorbent_price`, `pf_sorbent_cycles`. RESULTS.md gains the cells-by-tank tables and the
  cheapest combination by gas cap. The waste notes `waste_tricks_sizing.md` and `waste_and_medium_evidence.md`
  are now versioned.
- Cell-side levers (defaults unchanged): `fat_fed` (CO₂ per oxygen from 1.204 to 0.966 when all lipid is fed;
  Humbird's Reaction 2.2), `rq`, `do_mmol` (dissolved-oxygen setpoint; default the 0.28 mmol/L his numbers
  imply), and outputs for oxygen and CO₂ per kg split into upkeep and growth. Inputs `pf_rq_lipid`, `pf_fat_kg`,
  `pf_fat_price`, `ge_atp_per_o2`. Tags (feed or process / selection or adaptation / genetic engineering) on the
  page and in RESULTS.md, whose tables now come with and without genetic engineering.
- Deliberate change: the packed column now takes in culture at the tank's dissolved oxygen (0.28 mmol/L) rather
  than an assumed 0.05, so the oxygen-sweep cases cost up to $0.13/kg more (e.g. $7.43 to $7.52 at 2 mm/s) and an
  air sweep can no longer add oxygen. The note and RESULTS.md were updated.
- Deliberate change: a tank shape other than the default now carries its steel and floor cost in `explore` and on
  the page (`shape_cost`, default on). Moved: the tank-shape tornado row $9.3–25.2 to $9.5–24.4; in METHODS'
  CO₂ table the squat tank $9.3 to $9.5, 150 mbar with the squat tank $8.5 to $8.7, the 200 m³ squat tank at
  200 mbar $10.1 (153 g/L) to $11.3 (137 g/L). The default floor is unchanged.
- The page's "Build your own case" panel, with the tricks and the limits chart, now stands above "How the model
  works" instead of inside it.
- Deliberate change (review of PR 10): the column's default outlet CO2 (`ge_col_pout`) is now 55 mbar, not 20, so
  `explore(column="co2")` moves from $8.60 to $8.62; section 7 of the gas-exchange note keeps its 20 mbar design
  as the first one, and its tests pass 20 explicitly. New: passes an hour, pumped flow, loop volume and alkaline
  exposure in the column's output and on the page (inputs `ge_loop_transit`, `ge_passes_tested`);
  `cheapest_tricks(ph_safe=, tested=)`. RESULTS.md's cheapest-combination table gains the passes and a column
  within the tested passes and the safe pH exposure ($7.45 / $8.5 / $11.7 / $17.2 at 6 / 4 / 2 / 1 mm/s), and no
  longer says the floor barely depends on gas flow.

Demand side
- Price sensitivity above equal price is set by six premium animal products within the range of the one
  choice experiment on cultivated meat. It now acts only on cultivated meat's price difference from
  conventional. Shares at equal price are unchanged; above it they are several times lower.

Page
- Opens on the floor case. "Build your own case" panel with levers, a tornado chart of limiting factors with
  an information card per factor, and a button that sends a case to the main model.

Repository
- Tests run in CI. Research notes behind the new numbers are in `research_notes/`, with how each was read.

## 2026-11-13

- Independent review of the published model; organic-chicken check added; calibration price fixed.
