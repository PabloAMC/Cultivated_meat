# To do

The one list of open work, decisions and project ideas. Keep it current: tick or delete an item in the same commit that
does it. Reasons and estimates for the projects are in [`research_notes/roadmap_2026-11-15.md`](research_notes/roadmap_2026-11-15.md);
the earlier idea list (A–T, M1–M8) is in [`research_notes/project_review.md`](research_notes/project_review.md).

Last updated 2026-11-16.

## 1. Waiting on Pablo

Open pull requests (each says "no default changes" unless noted):

- [x] **The spread of liking is in the shopper model** (done 2026-11-18, `research_notes/liking_spread.md`). The long-run share at
      equal price is a visible setting, `equal_price_share` (13%, drawn 5–49%), and the only demand dial for the long-run level in the
      bands. The model passes three of four price-response checks. Branch `claude/recalibrate-demand` is superseded; do not merge.
- [ ] **The Engineered cells, all favourable case's demand (55%) and Selected cells' range (5–49%)**: Selected cells' range almost excludes shoppers favouring cultivated meat
      (under 1% of draws above 45%), while the Engineered cells, all favourable case now assumes it. Decide whether Selected cells' range should reach about 60%.
- [ ] **Conventional meat's price response** (METHODS, "When conventional meat's price responds"): with the Engineered cells, all favourable case's demand it is
      worth a tenth to an eighth of the share; model it if the Engineered cells, all favourable case's demand stays.
- [ ] **Plant-based meat's own-price elasticity** still fails (-2.85 against about -1.3): its buyers are a committed minority the
      model does not represent. A spread of liking for plant-based meat, refitted to the 1.2% share, is the candidate fix.
- [ ] **Evidence on the long-run share at equal price** (`demand_heterogeneity_evidence.md` §6): one reading of foods made by
      distrusted processes puts it near 18%. A repeated-exposure or tasting experiment with prices is the measurement that would
      settle it.
- [ ] Price sensitivity differs across shoppers too (4 to 10 times between groups), and plant-based meat's buyers are a concentrated
      minority (7% of households make 82% of spending). Both belong in the same rebuild; plant-based meat's elasticity is -2.85 in
      the model against about -1.3 measured for the category.
- [ ] Adoption over time has first purchase but no repeat or drop-out: plant-based meat's household penetration fell from 20% to 11%
      (GFI, 2021-25) as repeat rates fell. Add a repeat rate to `adoption_timing.py`.
- [x] The market tables of China, Brazil, India and Nigeria checked, and seafood weighted at 24% of the Global table (done 2026-11-18,
      `premium_market_sizes.md` §6; China's rows are order-of-magnitude). India's premium goat and seafood rows are unchecked.
- [ ] #19 Plain, direct sentences for all page text (wording only).
- [ ] #29 The frontier: every lever at its limit, one at a time ($26.64 → $5.49).
- [ ] #30 Filter flux: the flux is not the limit, the membrane's throughput is. **Decision inside:** move `rt_membrane_life`
      (3,960 L/m²) towards the measured 450–1,200? At 1,200 the Selected cells case is $46.95.
- [ ] #45 Ammonia and filter-life evidence (`research_notes/ammonia_tolerance_and_filter_life.md`; no default changed). **Decisions
      inside:** (a) `rt_membrane_life` (3,960) is probably the generous end (median about 1,500; 20% that it is within 1.5x), but a
      membrane adds price / life per litre, so moving life alone ($29.42 → $43.09 at 1,500) would pair a pessimistic life with
      today's $1,450 a m². Move life and price together, or leave both. This replaces the framing of #30. (b) `pf_nh3_limit`
      (5) stays: the evidence is spiked, unadapted cells and the Selected cells case assumes selection (45% that 5 is within 1.5x).
      (c) The bands draw life with mode 3,960 and price from $1,050–1,450, so both are one-sided; moving the modes (or drawing
      price / life as one quantity) changes every band and share figure.
- [ ] #31 Model audit: costs have only drifted up; Selected cells' median over all ranges is $33. **Decisions inside:** show
      the spread beside each point; membrane life; first-plant or mature financing; ~~a markup that is a share of price~~ (done 2026-11-18: per-kg costs plus a 28% margin, `research_notes/retail_markup_form.md`).

Decisions taken 2026-11-15 (late), on Pablo's instruction to pick the long-term option (numbers moved; CHANGELOG has them):

- [x] The plant ladder's perfusion rows are now `explore()` itself; `plant_floor` 9.8 → 10.8, `plant_floor_lo` 4.9 → 6.3.
- [x] The yeast-style plant buys its oxygen ($0.33/kg).
- [x] Poloxamer is costed: 2 g/L at an assumed $30/kg (catalogue $230–260). **Replace the price with a supplier quote.**
- [x] Antifoam's central value is 0.75 (the middle of 0–50%). Oxygen now limits Selected cells and Cautious. **A measurement in dense
      meat-cell culture would replace this judgement**; it is worth about $1.8/kg in the Selected cells case and $3.7 in Cautious.

Found while doing it (not changed):

- [ ] **METHODS calls CO₂ tolerance "the single measurement that would move the reference case most", but the tornado now
      shows 100 → 200 mbar moving it by $0.2**: the salt limit (bicarbonate uses up the osmolality lactate needs) caps the CO₂
      level the tank can run at. Either the claim or the salt rule needs a second look.
- [ ] **The fill-and-draw rows of the plant ladder are older than `explore`**: they cost $19.4 / $17.9 where `explore` gives about
      $24 / $22 for the same plants, because they skip the waste and least-flow caps. `plant_floor_hi` (the cautious end of the
      default's plant range) comes from one of them.
- [ ] Side-study notes are snapshots (header at the top of each). Regenerate them when each study is next touched.
- [x] Rebuilt `figures/` with LaTeX (2026-11-16); fixed five labels whose bare `$` broke the LaTeX build.

- [x] "Food-grade plant with shared medium": name kept (Pablo prefers explanatory names); the switch note and RESULTS now say what it removes and that the shared medium line is the smallest saving.

Raised by Pablo on 2026-11-16 (open):

- [x] **What the Selected cells case is for.** Done 2026-11-16: the scenarios are a ladder ordered by difficulty; the Selected cells case is rung 3, and a dated forecast row sits beside it.
- [x] **The reference case** is now "Humbird's optimistic design", shown beside the ladder, not on it; tank tricks come at rung 2.
- [x] **Comparable shares:** every row gives the share at its point cost and the median of draws (Humbird's design 2.4% median, Engineered cells, all favourable 3.8%).
- [x] **Growth factors are a separate line from the medium.** Done 2026-11-19: announced and reported medium prices are complete media
      with growth factors inside (`sc_medium_complete` on); the growth-factor line applies only to the medium at the nutrient floor.
- [ ] **Hybrid vessels and stirring** (CFD target A5 in the roadmap; `cfd_plan.md` step 3). A stirred tank with a draft tube and sparging, or other impellers. Now that oxygen limits Selected cells,
      oxygen transfer per watt (impeller, sparger design) matters; in the model only the vessel's oxygen multiplier would change.

- [x] **The forecast's medians**: dropped with the forecast (2026-11-19).
- [x] **`sc_medium_complete` on** (2026-11-19): Selected cells $29.42 -> $26.43. A complete medium cannot cost less than the nutrients plus its
      growth factors (`floor_physics.explore`, `gf_in_medium`).
- [x] **The nutrient floor from GFI** (2026-11-19, `nutrient_floor.md` §6): $1.70 -> $2.00 a kilo (feed-grade amino acids, 232 g/kg);
      medium settings $0.05 and $0.15 replaced by "at the nutrient floor". Engineered cells, all favourable $9.66 -> $9.96.
- [ ] **A supplier's tonne quote for the five amino acids hydrolysate cannot supply** (glutamine, arginine, asparagine, cystine,
      serine), and GFI's need-weighted mean price: both would firm up the floor.
- [x] **What a cut costs** (2026-11-19, `structuring_cost.md`): 0.8 cells + $2 matrix + $2 assembly beyond mince, in place of cells + $6.
- [ ] **How much of a cut can be cells, and whether shoppers treat a blend as cultivated meat.** Cuts sold are 10-30% cells; the model
      takes 80%. A lower share makes cuts cheaper, but the shopper model would then overstate demand. Options: tie the cut tier's
      authenticity offset to the cell share, or calibrate blends against plant-based whole cuts (Redefine Meat, Planted).
- [ ] **Mince is 100% cells while a cut is 80%.** Commercial mince products are blends too (GOOD Meat 3%, Upside's soy blend); decide
      whether mince should carry the same cell share, or say why not.
- [x] **The audit batch** (2026-11-19, `audit_2026-11-19.md`): ammonia tolerance 4 mM, lost-run membranes, glucose balance, seafood
      prices, the tier rule replaced, the equal-price share's range, the cut's inputs in the bands, the median as headline.
- [x] **The tail of shoppers' liking** (2026-11-19): Student's t, sd 3.9, 4 degrees of freedom; the 15-point rule replaced.
- [ ] **Farmed salmon's response still fails** (3.6-3.7 against 1-1.5). No spread that keeps the choice experiment's elasticities reaches
      it without a block of shoppers who ignore price (the mixture's corner). The Engineered cells, all favourable case's share with its own demand is the least
      pinned consequence of the fit (shapes that fit give 14-17%).
- [ ] **Page leftovers**: charts in levels 4-5 keep a fixed size and scroll sideways on a phone; the entry-points chart still colours
      zones; `tests/render_probe.js` calls a removed function; `page_sections.py` has unused generators.
- [ ] **`audit.py` draws lag the scenarios** (growth factors bought on top of a complete medium; the floor medium charged a price;
      `sc_nh3_limit` not drawn): as drawn Selected cells $34/$46/$65, put right $28/$38/$58. `min_litres.py` still uses Humbird's 5 mM.
- [ ] **The nutrient floor's glucose** is a third glucose figure (0.32 kg a kilo, all burned); tie it to the balance (a few cents).
- [ ] **Regional seafood rows** are still single "fillet" rows; split them as the world's were.
- [ ] **The filter pair.** Life 3,960 L/m² at the pharma price $1,450 (2018 dollars, not escalated) is the generous end if membranes
      stay at pharma prices; settled as a pair on 2026-11-18, to revisit with a supplier's quote.
- [x] **A tank that is not perfused breaks the waste mass balance** (found and fixed 2026-11-19, scenario restructure). An unwashed
      tank's density is now end factor x level allowed / waste made per kilo (`pf_batch_end_x` 1.3, Humbird's own fed-batch design;
      the last doublings above the level grow slower, `pf_batch_half_x`). Selected cells' batch stops at 37 g/L (was 56) and costs $64.9;
      the published cells' at 14 g/L. `research_notes/vessels_and_modes.md` section 10.
- [x] **Restructure the scenarios** (2026-11-19): a switch for how the tank is run; cells as four traits with a routes table and
      `routes_needed`; what it would take; reference points from fed-batch to Engineered cells, all favourable; the plant-cost axis.
      A forecast drawn from odds was built and dropped at the author's direction.
- [ ] **The page**: rebuild around traits as sliders with the routes verdict (`MODEL.sc.cell_routes`, `trait_verdicts`), the clouds,
      what it would take, and the contour chart the author approved; the page still shows the old case names and five-rung texts.
- [x] **Refresh the prose of RESULTS sections 2-4** for the share of the meat sold and the 2 ng engineered cell (2026-11-19: RESULTS,
      METHODS and README recomputed; the demand dial is stated first as a share of meat buyers; the dated notes removed).
- [ ] **The routes table's weakest cells**: a lactate yield below 1.05 in any meat cell; a figure for ammonia in a meat cell selected
      for it; whether the spinner/shaker gap in Hubalek 2023 is real.
- [ ] **Upside Foods' FDA memo**, when published: the operating mode, density and waste levels of a 20 m³ process. It would anchor
      rung 1 and `pf_batch_end_x` (research_notes/vessels_and_modes.md section 11; best guess fed-batch, 75%).
- [ ] **Fill-and-draw as a setting?** In a plant with shared medium it beats fed-batch by about 3% (it needs a seed only to restart),
      in Humbird's plant fed-batch wins by 8%. Not offered as a setting; add it if a batch plant should take the cheaper of the two draws should take the
      cheaper of the two.
- [ ] **Aggregates in the scenarios**: priced in `retention.scenario_cost("aggregates")`, offered by no switch.
- [ ] **SciFi Foods' bovine cell lines, open through Tufts.** GFI bought SciFi Foods' eight bovine lines at auction (August 2024) and
      released them through the Tufts open cell bank (October 2025): fibroblasts immortalised by CRISPR (p53 knockout and TERT
      insertion), adapted to suspension and grown serum-free; TU-GFI-SCL4 reportedly run in a 500 L bioreactor, SCL3 used in an FDA
      submission; two serum-free media (FSF4, FSF6) published. No growth or metabolism data are public yet (doubling time, density,
      ammonia, lactate). When Tufts or users publish them, they would be the first single, publicly available line to anchor
      "Published cells" on, in place of today's mix of traits from two lines. Their immortalisation is genetic engineering, though
      not the metabolic engineering the "engineered cells" setting means. Sources:
      https://gfi.org/resource/suspension-adapted-bovine-cell-lines/ ,
      https://cellularagriculture.tufts.edu/resources/open-cell-bank ,
      https://agfundernews.com/exclusive-open-source-moment-for-cultivated-meat-as-gfi-releases-scifi-foods-cell-lines-to-academia
      (16 Oct 2025).
- [ ] The sections below the summary still call Humbird's optimistic design "the reference case"; rename throughout, or keep the short name.

From the design search (`design_space.py`):

- [x] The lower dissolved-oxygen setpoint is in every scenario (`sc_do_setpoint`, 2026-11-16): Selected cells $29.92 → $29.42, best $9.71 → $9.66.
- [ ] The design search and `scenarios.design` drop a design whose column loop fails at full density; running it thinner might pass
      (the vessel grid now does, `vessels._thinned`).
- [ ] Add the missing options to the search as levers: two spargers, gas exchange on the filter loop, restart from a neighbour.
- [ ] Weight "unproven elements" by the odds in the research notes, to rank designs by expected cost.

From the design-tricks survey (`bioreactor_design_tricks.md`):

- [ ] **Two spargers** (a microsparger for oxygen, a drilled pipe for CO₂) as a lever: standard practice, and oxygen now binds Selected cells.
- [ ] **Gas exchange on the filter loop**: cost the column or a membrane module sharing the perfusion loop's pump and piping.
- [ ] **A non-bicarbonate buffer or a different base**, to test whether the salt limit is real where CO₂ tolerance should help.

Leads on reusing the medium (project G), from two books Pablo downloaded on 2026-11-16 (kept outside the repository: *Cellular
Agriculture*, Fraser, Kaplan, Newman and Yada eds., 2024, and *Cultivated Meat*, Soccol et al. eds., Springer 2024; chapters read in part):

- [ ] **Electrodialysis with selective membranes**: over 90% of ammonium and 99% of lactate removed from culture medium (Nir 2023,
      as cited in Soccol's waste-management chapter). Find the primary source; it is not in `waste_and_medium_evidence.md`.
- [ ] **Dialysis loops in patents**: Future Meat / Yissum (WO2018011805: a dialyser with an ammonia filter on the dialysate, at least
      90% of the perfusion liquid recirculated; WO2021152536: hollow fibres wrapped in absorbent, inside the tank) and Avant Meats
      (WO2023012523: a membrane of 500 Da or more keeps growth factors in; nitrifying bacteria take the ammonia and an enzyme turns
      lactate into pyruvate). Patent claims, not data.
- [ ] **Microalgae on spent medium** (Haraguchi 2021-2023): ammonia taken up, extract fed back, C2C12 cells grew as on standard medium.
- [ ] **Schneider, Marison and von Stockar 1996**, "The importance of ammonia in mammalian cell culture": the review both books cite for
      ion exchange, gas-permeable membranes and electrodialysis. Read it in full.
- [x] Electrodialysis and dialysis priced (`medium_reuse.py`, `research_notes/medium_reuse.md`, 2026-11-16). Cleaning the permeate
      saves $2–4 a kilo in the Selected cells case, because the liquid still passes the cell filter ($0.38 of the $0.75 a litre costs); dialysis
      across the culture saves $4–9 if its membrane holds up. The sorbent lever counted the filter as saved and was corrected
      (the $22.97 quoted here before is $28.22).
- [ ] **Bench tests the reuse study asks for**: electrodialysis of real spent medium (removal per pass, nutrients and growth factors
      lost, energy); a dialyser on a dense culture for weeks (clearance against time); a dialysate cleaned to under 10% make-up.
- [ ] **What the least medium flow is made of** (16 of Selected cells' 28 L/kg): nutrients, small by-products or large ones. It decides
      which reuse route can go below 16 L.
- [ ] **Add reuse to the page** as a lever (litres cleaned, on the permeate or across the culture), once a route has a measured input.
- [x] **Bands widened** (2026-11-16, `scenarios.MC_ESTIMATES`): they draw the ammonia the cells tolerate, the protectant's price and
      dose, the least medium flow, antifoam and the membrane price. Selected cells $27–38 → $25–47; Engineered cells, all favourable $9–12 → $10–19, median share
      3.8% → 1.9%. The protectant prior now stops at $120/kg (was the $260 catalogue price): a judgement until a quote arrives.
- [x] **Wrong-way demand inputs** (2026-11-16): a real flaw (the dollar channel's price coefficient could turn positive at high loss
      aversion) is fixed; the rest is an open question below.
- [ ] **Dollars or ratios**: how much of the price response is in dollars and how much is a ratio to the cut's price is not pinned by
      the data; it moves Selected cells' share 0.3–0.7%. Find data that separates them (premium-cut elasticities against commodity ones),
      or draw `w_ratio` in the bands with a precomputed calibration grid.
- [ ] **The Engineered cells, all favourable case's point cost is at the 3rd–4th percentile of its draws**: its limits are tied at about 11 L/kg. Say so on the page
      next to the Engineered cells, all favourable case, or define the Engineered cells, all favourable case by its median.
- [x] **Re-judge the probabilities** at Selected cells' 191 g/L (2026-11-19 restructure): `no_perfusion_downside.md` section 3 and the
      odds recorded in `cell_trait_routes.md` (45% possible). Still to do: `tank_size.md` section 7, column D, and `retention_devices.md` section 5,
      which keep their 258 g/L wording.
- [ ] **The last snapshot parts**: `tests/test_gas_exchange.py` and `tests/test_plant_items.py` still check some figures with the filter
      loop and the protectant switched off (`floor_physics.BEFORE_FILTER_LOOP`). Recompute them, or mark those sections as history.
- [x] `explore` let fresh medium fall below the liquid that leaves with the harvested cells. Floor added 2026-11-16 (a medium term,
      "harvest"); no scenario moved, the airlift in perfusion went from $14.78 to $15.07.

- [ ] **Demand near price parity** (`premium_curve.md`): anchored on premium real meats the Engineered cells, all favourable case takes 2.5%, against the model's
      8.0%. The premium data start at 1.5×. Find data on labels sold at or near parity (cage-free eggs after retailer pledges, Dutch
      Beter Leven 1 star, Label Rouge promotions) to see which is closer.
- [ ] **Show the premium-meat anchoring on the page**, or refit κ to the sixteen premium products? Open; nothing changed so far.

Bench measurements that would settle the two biggest inputs (from #45; each is cheaper than a pilot tank, and no meat-cell data exists):

- [ ] **Ammonia at density:** the real cell line in a 1–2 L perfusion at 10–20% cells by volume, serum-free, ammonium held at
      2, 3, 4, 5 and 7 mM for 10 days each, pH fixed; repeat 4 and 7 mM on cells raised slowly to that level. The answer is the
      highest level that keeps growth within 10%. My guess: $15–40k, two to three months.
- [ ] **Filter life with meat cells:** 0.025 m² hollow fibres (0.2 µm and one wide-pore) on a meat-cell perfusion at 15–20% cells
      by volume, at 2.5 and 5 L/m²/h, with the model's antifoam and protectant doses and one daily backflushed module; record
      pressure and sieving against litres per m² and against days. My guess: $20–50k, six weeks.
- [ ] **Life and price of a cheaper membrane class together:** prices are already bracketed ($3–14 a m² dialyser fibre to $1,450
      pharma, `retention_alternatives.md`); what is missing is how long the cheap classes (dialyser, wide-pore, ceramic) last in
      a thick animal-cell culture. A quote alone cannot settle it, so the filter bench run above should include one of them.
      Until then life and price stay as they are; nobody has offered a price (Pablo, 2026-11-16).

- [x] **`sc_glc_measured` re-derived** (2026-11-18): the central 0.84 rests on CHO data, not Pasitka; the range is now 0.67–3.6, and
      the high end moves today's cells by $92 a kilo, not Selected cells.

Things only Pablo can do:

- [ ] Find one bioprocess engineer to read RESULTS and METHODS (GFI science team, Humbird, the Unjournal workshop).
- [ ] Check the AI Office's rules on outside activities before publishing new work.
- [ ] Ask a supplier (BASF or a distributor) for a tonne price of poloxamer 188 (the model assumes $30/kg).

## 2. Housekeeping

Done on `claude/housekeeping` (2026-11-15):

- [x] Committed the project review, the waste-handling note and the growth-rate proposal.
- [x] Rebuilt `interactive.html`: main's page was older than its source.
- [x] `cost_scenarios.md` and `vessels_and_modes.md`: every figure recomputed with the filter loop.
- [x] `cheap_plant_study.md` and `gas_exchange_study.md`: kept as dated snapshots (their tests pin the old device), with
      a box of current figures at the top. The tank tricks are worth about half as much with the filter loop.
- [x] Antifoam and CO₂ stripping efficiency as levers (`explore(antifoam_otr=, strip_eff=)`), tornado bars, page mirror.
- [x] Checked that the airlift and bag rows of the vessel grid use the filter loop's duty (they do).

Still open:

- [ ] The gas-flow follow-ups not done: whether the gas cap is a velocity or a vvm (4); reading the paywalled primaries (6).
- [ ] The local `main` checkout fell 10 PRs behind origin once; pull before starting a session.

## 3. Projects

In the suggested order (roadmap, section 3). Status: idea / started / done.

| | project | status | notes |
|---|---|---|---|
| P | **Plant capital for animal cells**: an itemised, quoted cost of one food-grade 20 m³ sterilisable line (tank, piping, instruments, seed, medium sterilisation, cleaning) | idea | `industry_claims.py` shows company COGS agree with the model; the plant charge is the gap ($9–33/kg). Two or three vendor quotes or an engineering firm's costed design |
| B | Inverse model: what a cell line must deliver for a target cost | idea | #29 (frontier) is the forward version; this inverts it into a spec |
| C | Value of information: which experiment buys the most $/kg | idea | uses B and the odds in the gas-exchange and frontier notes |
| A | FluidX3D tank: validate, mixing vs shape, the column's return plume, the bubble cage's mesh | started | runs on the M4, pipe flow validated in 32-bit (`cfd_plan.md`); next: Rushton power number and mixing time |
| E | Hybrids and fat: cells as 5–20% of a plant-based product | idea | the near-term case for animals |
| D | Reported-run ledger with mass-balance flags | idea | merges T and S of the old list |
| G | Medium regeneration TEA | first pass done 2026-11-16 | `medium_reuse.py`: $2–4/kg on the permeate, $4–9 across the culture; next is bench data |
| A3 | Oxygen, CO₂ and pH gradients at 20 and 200 m³ | idea | after A0–A2; `tank_size.md` says 20 m³ is within 0.5–1.8% of the cheapest (cautious: 4.6%, at 111 m³) |
| F | Cost-optimal growth rate (the proposal PDF) | idea | two-day check first: is it worth more than ~$1.7/kg? |
| H | Bench foam test, or a protocol for a partner lab | idea | optional |

## 4. Done since the project review (for reference)

Gas exchange and the column (B, K, A) · what caps the gas flow (M3) · plant items and contamination (J, G) · holding the
cells back (I) and cheaper membranes · vessel × mode grid · scenarios · tank size 2–200 m³ · thick culture above 258 g/L ·
least medium per kg · the nutrient floor and GFI medium costs · growth-factor prices and the fastest doubling · the case
without perfusion. Each has a note in `research_notes/` and a CHANGELOG entry.
