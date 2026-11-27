# To do

The one list of open work, decisions and project ideas. Keep it current: tick or delete an item in the same commit that
does it. Reasons and estimates for the projects are in [`research_notes/roadmap_2026-11-15.md`](research_notes/roadmap_2026-11-15.md);
the earlier idea list (A–T, M1–M8) is in [`research_notes/project_review.md`](research_notes/project_review.md).

Last updated 2026-11-24.

Two examples are named in this list. The low-lactate example means cells that make 0.14 mol of ammonia a kilo (the published figure) and 0.42 mol of lactate per mol of glucose (the best published is 1.05), double every 36 hours and weigh 2 ng, grown in perfusion in a 20 m³ tank in a food-grade plant with medium at $0.20 a litre ($48.68 a kilo since 2026-11-21; $49.50 before). The all-favourable example (`scenarios.all_favourable`, $6.97; $7.62 before) means every lever at its most favourable value among this model's own favourable end, Humbird's design and thirteen other published studies, within the model's limits (`research_notes/study_comparison.md`), with 58.7% of meat buyers picking it at the same price.

## 1. Open work

- [ ] **Hybrid mince** (2026-11-27, `research_notes/hybrid_demand_evidence.md`). The blend rule is now a curve (`blend_curve`,
      1.2, drawn 0.4-2.5), and a cut can be set down to 10% cells. Mince is still all cells: a product of 3-30% cells in a plant
      base, sold as mince or nuggets, is not modelled. It needs a cell share for unstructured products and a view on whether such
      a product competes with meat or with plant-based meat. The curve itself rests on meat-plant blends; a choice study that
      varies the share of cultivated cells would replace it.
- [ ] **Industry-average baselines from GFI**, if and when GFI publishes them: add them to `study_assumptions.py` as a study.

- [ ] **Amino acids left in spent medium** (2026-11-27, `research_notes/nutrient_floor.md` section 9). The nitrogen balance says
      cells keeping 95-98% of the amino-acid nitrogen eat about 0.24 kg a kilo; GFI's estimates reach 0.65. Only a large unused
      or secreted share (alanine, glutamate) closes that gap. A measurement of the amino acids in spent medium from a meat-cell
      perfusion would set `aa_intensity` above the floor, and say how much a recycling route (`medium_reuse.py`) could save.

From the full review of 2026-11-19 (`research_notes/full_review_2026-11-19.md`, section 7). **Done on 20-21 November** (CHANGELOG.md;
effects in RESULTS.md, "What changed on 20 and 21 November"):

- [x] **A range for the lactate the cells tolerate**: `sc_lac_limit` 35 mM (20-50, drawn); Humbird's design keeps `pf_lac_limit` 50.
- [x] **Medium preparation capital scaled with the litres passed** (`pf_medium_prep_l_kg`, `pf_medium_prep_exp`).
- [x] **Bubble deaths charged** on the gas the cells meet (`death_share`, `gas_cells`, `ge_kill_protected` drawn); a column that
      strips nothing no longer lowers them, and the bubble cage is charged only on the gas its cells meet.
- [x] **Labour in perfusion**: the fed-batch crew times `pf_labour_perfusion_x` (2.0).
- [x] **A harvest loss of 2%** (`pf_harvest_recovery` 0.98), on every cost per kilo; a vessel's own recovery now scales every cost too.
- [x] **`accept_x` out of the demand and timing bands.**
- [x] **The filter pair**: `rt_membrane_life` 2,415 L/m², Humbird's schedule at his price ($0.60 a litre).
- [x] **The back-test against Humbird's tables** (`humbird_check.py`): growth factors per litre of his fed-batch, utilities in four
      parts, the crew at his 14.2 t per m³, plant items per tank (`floor_physics.tank_items`, `capex_at_size`).
- [x] **Thick cultures take up oxygen more slowly** (`viscous_kla`, `tc_kla_exp`, `tc_thin`): the low-lactate example runs at 154 g/L.
- [x] **The ATF priced with Humbird's accounting** (6.25 times its bare price): the dearest retention device.
- [x] **Defects fixed**: `retention.duty` bleeds per kilo grown; `plant_items.cost_per_kg` uses `explore(items)`; `min_litres`
      consistent; the airlift follows the stirred tank's mixing rule.
- [x] **One most favourable case** (`scenarios.all_favourable`, $7.62), checked lever by lever against Humbird and nine other
      published studies (`study_assumptions.py`); Risner 2021 scenario 4 is the one estimate below it, and breaks four limits.
- [x] **Demand**: plant-based meat's anchor 0.4% of meat by volume; nominal incomes (`REGION_INCOME`, `income_gradient` 0.32);
      conventional meat's price falls as it loses sales (`conv_exponent`); markets closed by law (`closed_share`, world 1.14%).
- [x] **Levers**: maturation (`mature_h`, default 0); cleaning the medium (`clean`, `wash_price`), off by default.
- [x] **The page** opens on Humbird's best estimate as he counts it ($26.99 in 2025 dollars), with five additions as levers.
- [x] **The documents** (RESULTS, METHODS, README, the retention notes) refreshed to the final model (2026-11-21).
- [x] **Older METHODS and RESULTS paragraphs that quoted 2026-11-20 figures** recomputed (2026-11-22): the shelf-price rule, the
      draws of the all-favourable example, the spread's misfits and shares, conventional meat's price response, the adoption curve,
      the sensitivity tornado, the vessel, cleaning, per-tank and maturation figures; paragraphs kept as history now say so.

Still open:

- [x] **The design search never holds a culture below the density its limits allow**: done 2026-11-21 (`scenarios.thinned`,
      `design_space.run`, the page's `scDesign`); the oxygen-feeding loop held thinner now wins every perfusion case
      (`research_notes/two_spargers_and_loop.md` section 1).
- [ ] **The airlift is sensitive to its shape**: with the stirred tank's mixing rule a tall column mixes a thick culture poorly
      (45 g/L in Humbird's design); its cost should be scanned over height-to-width before any conclusion about vessels.
- [ ] **The per-tank building split is a fit** ($74.4k per m³ + $533k a tank, fitted to Humbird's two plants), not his rule; a priced
      plant with 100 m³ tanks would test it. His wild-type plants come out 14% below the engine's plant per m³.
- [x] **Pasitka 2024's supplementary tables** are public and read (2026-11-21, `evidence_pasitka_supplement.md`): Tables S4 and S10
      compute a capital charge (14.6% of the plant a year) but leave it out of the total. With it, the large-scale case is $26.99
      (2024 dollars), $27.7 in 2025 dollars, not $21.49. It also assumes 81 g of amino acids a kilo of cells, a third of the floor's 232 g.
- [ ] **Judgement figures** in the research notes (odds on filters, aggregates, doublings): each should be labelled as a rough
      judgement made while building the model with an AI assistant, with its reasoning, or deleted if it adds nothing checkable.
      Several were set at the low-lactate example's earlier 191 g/L. (2026-11-21: done for the three retention notes,
      `no_perfusion_downside.md` and `cell_trait_routes.md` (its appendix of odds by 2035 deleted), and the "my judgement" lines of
      four more notes; still to read: the odds tables of `tank_size.md` section 7, `gas_flow_cap.md`, `gas_exchange_study.md`,
      `frontier.md` and `gf_and_doubling_bounds.md`, which are labelled but not re-checked against the current densities.)
- [x] **The least-medium-flow cap applied to fed-batch**: done 2026-11-21. In an unwashed tank it stands for by-products, which a batch
      may end 1.3 times above as it may ammonia and lactate; it no longer binds Humbird's design (`humbird_backtest.md` item 11).
- [x] **Humbird's perfusion design**: done 2026-11-21 (`humbird_backtest.md` item 12). Building power by floor and class, crew partly
      per tank, growth factors on his litres like for like: −4%, −27%, 0%. Left: 13.5 L a kilo of process water he does not itemise.
- [x] **`retention.sizing` ignores a sorbent's extra permeate**: done 2026-11-21 (`filter_extra_l` in `retention.duty`, and the page).
- [x] **The dialysis variant at twice the filter's clearance**: the figure checked 2026-11-21 against Fresenius's FX 80 table (278 mL/min
      of urea at 300 mL/min of blood over 1.8 m², 9.3 L/m²/h). How it holds over weeks of fouling in a culture is still unmeasured.
- [x] **The page** (fixed 2026-11-21): its methodology prose quoted the elasticity at R = 2.42 as −3.0 where the model gives −3.06 (−3.1), and
      `{{TRICKS_CENTRAL_ORD}}` is computed but unused (`tests/test_golden.py` fails on both until `build_interactive.py` is fixed).
- [x] **`taste_quality_w`'s upper end** (checked 2026-11-21, fourth batch): it re-solves cleanly across its whole range (−1.0 to
      −0.3; the solved health weights stay above zero, plant-based meat at 0.4%), and is back in METHODS.md's list of assumptions
      with modest leverage. The remark was stale.
- [x] **Owner-attributed comments** (done 2026-11-21): `inputs.py`'s "our probability", "OUR JUDGEMENT" and named credits now read as
      the model's rough judgement or plain dates; `humbird_backtest.md`'s ATF ×1.84 remark dated (the ATF is priced in his accounting
      since 2026-11-20); "my judgement" in four notes relabelled. `humbird_backtest.md` had no other owner attribution.
- [ ] **Still to decide**: whether the meat-buyers setting should be redefined against the world total.
- [ ] **Published cells' lactate on the engine's glucose burn** (from CHANGELOG 2026-11-24): Published cells and the Pasitka
      modification use the measured ratio of lactate to glucose (1.05), which on this engine's glucose burn makes several times the
      lactate Pasitka measured per kilo. The $316 headline rests on it; check it against a measured balance per kilo.
- [ ] **Exchange rates typed from memory** ($1.28 a pound, $1.13 a euro, `study_assumptions.py`): replace with sourced rates.
- [x] **Meat displaced for each kilo sold** (done 2026-11-22, sixth batch): `meat_displaced_per_kg` (1, range 0.5-1) scales the
      animals spared, the entry points' tonnes displaced and the fall in conventional meat's sales behind its price; a lever in the
      side bar's shoppers section. No headline moves at 1.
- [x] **The menu check** (done 2026-11-22, sixth batch; `demand_checks.md` section 8): adding plant-based meat priced like meat
      takes 0.54 points from meat's share (Hope 2026: 2.1, 0 to 4.4): the size passes. 79% of its choices come from meat against
      about 30%: the source fails. Not refitted.
- [ ] **Open from the menu check**: within a segment the flat logit takes a new meat-free option's choices from meat in proportion
      to meat's share; the menu experiment says plant-based meat substitutes more for the vegetarian option. Whether to represent
      that (a nest for the meat-free options, or a closer whole-food substitute), and with what measurement, is undecided.
- [ ] **Smaller**: a sentence each in METHODS on halal and kosher status and substitution across meats; cite the two FDA memos
      (Believer, Wildtype), Negulescu's measured yields and Gu's sorbent data; the research notes still say "Central" in places, and
      three of them (`cost_scenarios.md`, `ammonia_tolerance_and_filter_life.md` section 10, `gas_exchange_study.md`) tie traits to routes.

Open pull requests (each says "no default changes" unless noted):

- [x] **The spread of liking is in the shopper model** (done 2026-11-18, `research_notes/liking_spread.md`). The long-run share at
      equal price is a visible setting, `equal_price_share` (13%, drawn 5–49%), and the only demand dial for the long-run level in the
      bands. The model passes three of four price-response checks. Branch `claude/recalibrate-demand` is superseded; do not merge.
- [x] **Three side analyses count the share of the meat sold** (done 2026-11-21, fourth batch): `uncertainty.py`, `sensitivity.py`
      and `adoption_timing.py` (and the page's timing curve) use x / (x + c), as the roll-up does.
- [x] **Stale prose in two notes** (`market_size_loop.md`, `premium_buyers.md`): repinned on 2026-11-20.
- [ ] **The all-favourable example's demand (58.7% of meat buyers) and the low-lactate example's range (3–52% of all choices)**: the low-lactate example's range almost excludes shoppers favouring cultivated meat
      (under 1% of draws above 45%), while the all-favourable example now assumes it. Decide whether the low-lactate example's range should reach about 60%.
- [x] **Conventional meat's price response**: modelled on 2026-11-20 (`meat_market.conv_exponent`); it takes 3.9 points off the
      all-favourable example's 22.6%.
- [x] **Plant-based meat's own-price elasticity** passes since 2026-11-21 (fourth batch): -1.30 then, -1.03 since the fifth batch (tolerance 0.25), against -1.23 measured (the category
      about -1.3). A spread of liking alone could not do it: in a logit a buyer's elasticity falls only as their own share of
      choices nears one, and 7% of households buying 82% gives them about 4%. The fix is a class of committed buyers (7% of
      shoppers, 82% of the mainstream's plant-based meat, a solved liking) whose response to its price is 0.25 times other
      shoppers' (Tonsor, Lusk & Schroeder 2021), a measured input, not fitted (`demand_checks.md` section 5).
- [ ] **Evidence on the long-run share at equal price** (`demand_heterogeneity_evidence.md` §6): one reading of foods made by
      distrusted processes puts it near 18%. A repeated-exposure or tasting experiment with prices is the measurement that would
      settle it.
- [ ] **The blend penalty after the committed buyers** (2026-11-21, fourth batch): with plant-based meat's committed buyers in the
      model the ordinary shoppers' solved real-meat weight is 5.11 utils (3.40 before), and a cut that is 20% plant protein loses 20%
      of it (1.02 utils, was 0.68). That alone takes the all-favourable example from 24.6% to 23.4% with its own demand. It is the
      existing rule on a better-measured weight; whether a blend should lose that share of the ordinary shopper's dislike of
      plant-based meat is unmeasured (see the cut's cell share below).
- [x] **Price sensitivity across all shoppers** (4 to 10 times between groups). Done 2026-11-22 (fifth batch;
      `demand_checks.md` section 7): 8% of every segment's shoppers (`price_insensitive_share`, 8-15%) respond 0.11 times as
      strongly to every price (`price_insensitive_response`, 0.10-0.25), both fitted within the evidence to the demand checks
      jointly, with the spread of liking refitted (3.55 utils, tail 7). Their liking for cultivated meat
      (`price_insensitive_liking`) is 0 utils above other shoppers' (range -2 to +2), read in utils from the two latent-class
      studies (Washio 2023, Carzedda & Troiano 2021), in which the price-insensitive are the most hostile in money but not in utils.
      The joint misfit fell from 4.20 to 0.87; the low-lactate example's share rose from 0.045% to 0.26% of world meat.
- [ ] **How much the price-insensitive shoppers like cultivated meat** (2026-11-22). 97% of the low-lactate example's sales go to
      them, and across the input's range (-2 to +2 utils) its share runs from 0.11% to 0.58%. Two stated-choice latent-class
      studies are the only evidence. A latent-class or mixed-logit study that reports the joint distribution of the price
      coefficient and the liking for cultivated meat, ideally in a real-purchase setting, would pin it.
- [x] **Repeat buying and dropping out** in `adoption_timing.py` (done 2026-11-21, fourth batch; `repeat_rate` 0.62, 0.50-0.75, from
      GFI/SPINS 2025; `lapse_rate` 0.14 a year, 0.05-0.30, from plant-based meat's household reach falling from 20% to 11% in
      2021-25, while its repeat rate stayed near 62%, not fell). The long run is unchanged; the path is slower in its first years.
      No repeat data exist for cultivated meat.
- [x] The market tables of China, Brazil, India and Nigeria checked, and seafood weighted at 24% of the Global table (done 2026-11-18,
      `premium_market_sizes.md` §6; China's rows are order-of-magnitude). India's premium goat and seafood rows are unchecked.
- [x] #19 Plain, direct sentences for all page text (wording only): done 2026-11-21 (fourth batch, CHANGELOG). Every meat price names
      its meat ("same shop price as US minced beef or pork cuts", "the price of the conventional meat it copies"); no "out of reach",
      "beat", "path", "ladder" or "frame"; dollars are 2025 dollars. The setting's name was renamed on 2026-11-22 (fifth batch):
      "Added equipment for oxygen and CO₂".
- [x] #29 The frontier: replaced on 2026-11-20 by the path from Humbird's design to the all-favourable example (`frontier.py`, $15.95 → $7.62).
- [x] #30 Filter flux: the flux is not the limit, the membrane's throughput is. Settled on 2026-11-20 with #45: `rt_membrane_life`
      is Humbird's 2,415 L/m² at his price.
- [ ] #45 Ammonia and filter-life evidence (`research_notes/ammonia_tolerance_and_filter_life.md`). (a) Done 2026-11-20: life is
      Humbird's 2,415 L/m² paired with his $1,450 a m²; the evidence's median is about 1,500 (the low-lactate example $63.1 there).
      (b) The scenarios take 4 mmol/L of ammonia (`sc_nh3_limit`), Humbird's design 5. (c) Open: the bands draw life and price
      separately; drawing price / life as one quantity would change every band.
- [ ] #31 Model audit: costs have only drifted up; the low-lactate example's median over all ranges is $33. **Decisions inside:** show
      the spread beside each point; membrane life; first-plant or mature financing; ~~a markup that is a share of price~~ (done 2026-11-18: per-kg costs plus a 28% margin, `research_notes/retail_markup_form.md`).

Decisions taken 2026-11-15 (late), on Pablo's instruction to pick the long-term option (numbers moved; CHANGELOG has them):

- [x] The plant ladder's perfusion rows are now `explore()` itself; `plant_floor` 9.8 → 10.8, `plant_floor_lo` 4.9 → 6.3.
- [x] The yeast-style plant buys its oxygen ($0.33/kg).
- [x] Poloxamer is costed: 2 g/L at an assumed $30/kg (catalogue $230–260). **Replace the price with a supplier quote.**
- [x] Antifoam's central value is 0.75 (the middle of 0–50%). Oxygen now limits the low-lactate example and Cautious. **A measurement in dense
      meat-cell culture would replace this judgement**; it is worth about $1.8/kg in the low-lactate example and $3.7 in Cautious.

Found while doing it (not changed):

- [x] (2026-11-21: the claim is corrected; above 100 mbar oxygen, not the salt rule, holds the tank at 121 g/L, and the gas flow
      tolerated moves the design more) **METHODS calls CO₂ tolerance "the single measurement that would move the reference case most", but the tornado now
      shows 100 → 200 mbar moving it by $0.2**: the salt limit (bicarbonate uses up the osmolality lactate needs) caps the CO₂
      level the tank can run at. Either the claim or the salt rule needs a second look.
- [x] (2026-11-21: they are `explore()` itself; `plant_floor_hi` $17.7 → $20.3, the plant knob's range $13.5-37.1) **The fill-and-draw rows of the plant ladder are older than `explore`**: they cost $19.4 / $17.9 where `explore` gives about
      $24 / $22 for the same plants, because they skip the waste and least-flow caps. `plant_floor_hi` (the cautious end of the
      default's plant range) comes from one of them.
- [ ] Side-study notes are snapshots (header at the top of each). Regenerate them when each study is next touched. (2026-11-21:
      regenerated or given a box of current figures: `no_perfusion_downside.md`, `vessels_and_modes.md` section 4,
      `gas_exchange_study.md`, `cheap_plant_study.md`, the three retention notes. 2026-11-22 (documents sweep): `min_litres_per_kg.md`
      (both tables and their prose), `filter_flux.md` (section 4), `gf_and_doubling_bounds.md` (sections 1 and 2),
      `gas_flow_cap.md` (the box and the experiments), the status box of `ammonia_tolerance_and_filter_life.md`, the tables of
      `cost_scenarios.md` and `study_comparison.md` (with a box), and the demand notes `liking_spread.md` and `market_size_loop.md`
      (prose recomputed). Still snapshots, each saying so in its header: `tank_size.md` and `thick_culture.md` outside their
      recomputed sections, `model_audit.md` sections 1-6, the bodies of the retention notes and of `vessels_and_modes.md`,
      `nutrient_floor.md`'s 2026-11-20 section, and inline costs of 2026-11-20 in `design_space.md`, `medium_reuse.md`,
      `premium_curve.md`, `retail_markup_form.md` and `demand_checks.md` sections 1-4.)
- [x] Rebuilt `figures/` with LaTeX (2026-11-16); fixed five labels whose bare `$` broke the LaTeX build.

- [x] "Food-grade plant with shared medium": name kept (Pablo prefers explanatory names); the switch note and RESULTS now say what it removes and that the shared medium line is the smallest saving.

Raised by Pablo on 2026-11-16 (open):

- [x] **What the low-lactate example is for.** Done 2026-11-16: the scenarios are a ladder ordered by difficulty; the low-lactate example is rung 3, and a dated forecast row sits beside it.
- [x] **The reference case** is now "Humbird's optimistic design", shown beside the ladder, not on it; tank tricks come at rung 2.
- [x] **Comparable shares:** every row gives the share at its point cost and the median of draws (Humbird's design 2.4% median, the all-favourable example 3.8%).
- [x] **Growth factors are a separate line from the medium.** Done 2026-11-19: announced and reported medium prices are complete media
      with growth factors inside (`sc_medium_complete` on); the growth-factor line applies only to the medium at the nutrient floor.
- [ ] **Hybrid vessels and stirring** (CFD target A5 in the roadmap; `cfd_plan.md` step 3). A stirred tank with a draft tube and sparging, or other impellers. Now that oxygen limits the low-lactate example,
      oxygen transfer per watt (impeller, sparger design) matters; in the model only the vessel's oxygen multiplier would change.

- [x] **The forecast's medians**: dropped with the forecast (2026-11-19).
- [x] **`sc_medium_complete` on** (2026-11-19): the low-lactate example $29.42 -> $26.43. A complete medium cannot cost less than the nutrients plus its
      growth factors (`floor_physics.explore`, `gf_in_medium`).
- [x] **The nutrient floor from GFI** (2026-11-19, `nutrient_floor.md` §6): $1.70 -> $2.00 a kilo (feed-grade amino acids, 232 g/kg);
      medium settings $0.05 and $0.15 replaced by "at the nutrient floor". The all-favourable example $9.66 -> $9.96.
- [ ] **A supplier's tonne quote for the five amino acids hydrolysate cannot supply** (glutamine, arginine, asparagine, cystine,
      serine). The need-weighted mean is done (`nutrient_floor.md` §7). Evidence pass 2026-11-21 (`evidence_amino_acid_prices.md`):
      serine decides it (30% of the amino-acid cost, about 400 t a year made, no tonne quote); at today's quotes the floor would be
      about $2.35–2.45. $6.36 is kept as the long-run price, which assumes new serine capacity. Draft request in
      `evidence_outreach_drafts.md` (a).
- [x] **What a cut costs** (2026-11-19, `structuring_cost.md`): 0.8 cells + $2 matrix + $2 assembly beyond mince, in place of cells + $6.
- [ ] **How much of a cut can be cells, and whether shoppers treat a blend as cultivated meat.** Cuts sold are 10-30% cells; the model
      takes 80%. A lower share makes cuts cheaper, but the shopper model would then overstate demand. Options: tie the cut tier's
      authenticity offset to the cell share, or calibrate blends against plant-based whole cuts (Redefine Meat, Planted).
- [ ] **Mince is 100% cells while a cut is 80%.** Commercial mince products are blends too (GOOD Meat 3%, Upside's soy blend); decide
      whether mince should carry the same cell share, or say why not.
- [x] **The audit batch** (2026-11-19, `audit_2026-11-19.md`): ammonia tolerance 4 mM, lost-run membranes, glucose balance, seafood
      prices, the tier rule replaced, the equal-price share's range, the cut's inputs in the bands, the median as headline.
- [x] **The tail of shoppers' liking** (2026-11-19): Student's t, sd 3.9, 4 degrees of freedom; the 15-point rule replaced.
- [ ] **Farmed salmon's response still fails, narrowed** (1.5-4.0 against 1-1.5 since 2026-11-22; 3.7-4.2 before). With the
      price-insensitive shoppers in the model (`demand_checks.md` section 7) the dearest premium product (organic chicken, 4.7
      times its meat's price) responds at 1.52, the top of salmon's range; heritage pork 1.84, premium fillets and shrimp 2.36 and
      sushi-grade seafood, nearest its meat's price, 4.00. No setting of the class within the evidence puts all four inside: with
      a tenth of the price response the range is 1.42-3.96, with 15% of shoppers 1.23-3.29 (at a misfit of 4.4). Why, as far as the
      model can say: near meat's price a product's buyers are mostly ordinary shoppers, whose response is steep; farmed salmon's
      buyers liked it and paid little attention to price at a modest premium. Left failing and documented.
- [x] **Page leftovers** (done 2026-11-21, fourth batch): the charts of levels 4-5 are drawn at the screen's width on a phone (under
      560 px; `lvW`, `lvBox`), with their names and keys moved inside or under the plot; the entry-points chart has one colour, no
      zones; `tests/render_probe.js` draws the first screen's bars of each kind of meat (`tpSellBars`); the unused generators of
      `page_sections.py` are gone. Tables (the vessel grid, the steps, the parameters) still scroll sideways on a phone.
- [x] (2026-11-21: put right in `audit.py`, plus the lactate tolerated, the bubble kill and the harvest recovery; `min_litres.py` still
      uses Humbird's 5 mM, which is its stated reference) **`audit.py` draws lag the scenarios** (growth factors bought on top of a complete medium; the floor medium charged a price;
      `sc_nh3_limit` not drawn): as drawn the low-lactate example $34/$46/$65, put right $28/$38/$58. `min_litres.py` still uses Humbird's 5 mM.
- [x] **The nutrient floor's glucose**: tied to the balance 2026-11-21 (0.311 kg a kilo with no lactate; −$0.004).
- [ ] **Regional seafood rows** are still single "fillet" rows; split them as the world's were. Not done 2026-11-21: the world split
      rests on a premium share of edible weight (16%) with no regional counterpart in `world_seafood_prices.md`; it needs each
      region's premium share and prices. It does not touch the cost estimate.
- [x] **The filter pair** (life set to Humbird's 2,415 L/m² on 2026-11-20; the text below is the question as it stood). Life 3,960 L/m² at the pharma price $1,450 (2018 dollars, not escalated) is the generous end if membranes
      stay at pharma prices; settled as a pair on 2026-11-18, to revisit with a supplier's quote.
- [x] **A tank that is not perfused breaks the waste mass balance** (found and fixed 2026-11-19, scenario restructure). An unwashed
      tank's density is now end factor x level allowed / waste made per kilo (`pf_batch_end_x` 1.3, Humbird's own fed-batch design;
      the last doublings above the level grow slower, `pf_batch_half_x`). The low-lactate example's batch stops at 37 g/L (was 56) and costs $64.9;
      the published cells' at 14 g/L. `research_notes/vessels_and_modes.md` section 10.
- [x] **Restructure the scenarios** (2026-11-19): a switch for how the tank is run; cells as four traits with a routes table and
      `routes_needed`; what it would take; reference points from fed-batch to the all-favourable example; the plant-cost axis.
      A forecast drawn from odds was built and dropped at the author's direction.
- [x] **The page, rebuilt around traits** (stale wording replaced 2026-11-21; Pablo's later decisions override the first plan of a
      routes verdict and clouds). Done: the levers in a bar at the side with references and context, by section (cells; reactor and
      how it is run; medium; shoppers), many in collapsible groups, each section's result beside them; vessels, retention devices and
      modes chosen with the cost each gives; each trait shows only the best value measured in meat cells, with its source; no routes
      verdict, no route claims, no cloud of dots (the point and the range for 8 in 10 draws); the cost shown is the point, not a median
      (since the fourth batch also in level 1's cards, steps and table, and the methods prose); no named kinds of cell (the
      level-4 switch and the cells-by-tank rows are named by their ammonia and lactate since the fourth batch); the page opens at
      Humbird's best estimate and leads with no number but the floor and the best the model finds; no reference that gives only a
      cost is drawn on the share map; white background, Computer Modern. `tests/test_easy_view.py` checks most of this.
- [x] **The page: one set of controls** (a): done 2026-11-22 (fifth batch, CHANGELOG). The side bar is the page's only set of
      controls: the level "How the tank and the plant set the cost" lost its eleven switches and "Every cell and tank setting"; what
      the side bar lacked moved into it by section (the tank design and its button, the plant item by item and two more plant
      classes, reported cells, the other reference points, ten more levers); the level shows results only, from the side bar's state.
- [x] **"Tank tricks" renamed** (c): done 2026-11-22 (fifth batch). The setting is "Added equipment for oxygen and CO₂" on the
      page, in scenarios.py and in the documents; code keys (`tricks`, "none"/"column"/"pressure"/"oxygen") unchanged.
- [ ] **The page, what is left**: (b) the methods prose and the shopper histogram quote shares as the median of draws with the
      shopper settings drawn too (a band statement, not a cost).
- [x] **Refresh the prose of RESULTS sections 2-4** for the share of the meat sold and the 2 ng weight of the cells that make almost no ammonia or lactate (2026-11-19: RESULTS,
      METHODS and README recomputed; the demand dial is stated first as a share of meat buyers; the dated notes removed).
- [ ] **The routes table's weakest cells**: a lactate yield below 1.05 in any meat cell; a figure for ammonia below 0.14 mol a kilo in any meat
      cell; whether the spinner/shaker gap in Hubalek 2023 is real.
- [ ] **Upside Foods' FDA memo**, when published (2026-11-21: its first memo is public and silent on scale; the memo for the product
      cleared in September 2026, with 20,000+ L tanks reported in the press, is not yet on FDA's site; re-check in December 2026): the operating mode, density and waste levels of a 20 m³ process. It would anchor
      rung 1 and `pf_batch_end_x` (research_notes/vessels_and_modes.md section 11; best guess fed-batch, 75%).
- [ ] (2026-11-21: still not a setting. Perfusion is the cheapest mode in every perfusion-capable rung and in the all-favourable
      search, and the batch rungs take fed-batch as the mode reported at 20 m³ (Upside Foods); adding it would change no
      headline. Left for a decision on whether a batch plant should take the cheaper of the two) **Fill-and-draw as a setting?** In a plant with shared medium it beats fed-batch by about 3% (it needs a seed only to restart),
      in Humbird's plant fed-batch wins by 8%. Not offered as a setting; add it if a batch plant should take the cheaper of the two.
      (2026-11-21: a 100 m³ fed-batch looked cheaper than perfusion with the shared-medium plant, but that set it against 20 m³
      perfusion. In a tank of the same size perfusion is cheaper at 20, 50 and 100 m³ in every rung: $42.0 against $43.6 at
      100 m³, rung 5. Only rung 6's cells at 200 m³ favour fed-batch, by $0.31. `scenarios.plant_axis`, `tank_size.perfusion_at`.)
- [ ] **Aggregates in the scenarios**: priced in `retention.scenario_cost("aggregates")`, offered by no switch. Checked 2026-11-21:
      they would not lower the all-favourable example ($7.39 against $6.97); they would take the low-lactate example to $26.51, but
      the biology (aggregates of 100-300 µm held for a month at 150+ g/L) has not been shown (`retention_aggregates.md`), so they
      stay a device on the page, not a switch.
- [ ] **SciFi Foods' bovine cell lines, open through Tufts.** GFI bought SciFi Foods' eight bovine lines at auction (August 2024) and
      released them through the Tufts open cell bank (October 2025): fibroblasts immortalised by CRISPR (p53 knockout and TERT
      insertion), adapted to suspension and grown serum-free; TU-GFI-SCL4 reportedly run in a 500 L bioreactor, SCL3 used in an FDA
      submission; two serum-free media (FSF4, FSF6) published. No growth or metabolism data are public yet (doubling time, density,
      ammonia, lactate). When Tufts or users publish them, they would be the first single, publicly available line to anchor
      "Published cells" on, in place of today's mix of traits from two lines. Sources:
      https://gfi.org/resource/suspension-adapted-bovine-cell-lines/ ,
      https://cellularagriculture.tufts.edu/resources/open-cell-bank ,
      https://agfundernews.com/exclusive-open-source-moment-for-cultivated-meat-as-gfi-releases-scifi-foods-cell-lines-to-academia
      (16 Oct 2025).
- [x] The sections below the summary still call Humbird's optimistic design "the reference case": renamed throughout the documents
      and notes on 2026-11-21 (the code's identifiers and docstrings keep "reference"; `audit_2026-11-19.md` keeps it as a quoted name).

From the design search (`design_space.py`):

- [x] The lower dissolved-oxygen setpoint is in every scenario (`sc_do_setpoint`, 2026-11-16): the low-lactate example $29.92 → $29.42, the all-favourable example $9.71 → $9.66.
- [x] The design search and `scenarios.design` drop a design whose column loop fails at full density: done 2026-11-21 (see above).
- [ ] Add the missing options to the search as levers: two spargers and the column on the filter loop done 2026-11-21 (levers,
      off by default; the all-favourable search tries both); restart from a neighbour is the restart switch's 4-day setting already.
      A gas-exchange membrane module on the loop is not priced: no membrane is both priced and rated for steaming.
- [ ] Weight "unproven elements" by the odds in the research notes, to rank designs by expected cost.

From the design-tricks survey (`bioreactor_design_tricks.md`):

- [x] **Two spargers**: a lever since 2026-11-21 (`spargers=2`); worth little, because fine bubbles kill ten times the cells per
      litre of gas and the oxygen-feeding loop already lifts oxygen (`two_spargers_and_loop.md`).
- [x] **Gas exchange on the filter loop**: the column on the loop is a lever since 2026-11-21 (`col_on_loop`, $0.01-0.06 a kilo); a
      membrane module stays unpriced (no source).
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
      saves $2–4 a kilo in the low-lactate example, because the liquid still passes the cell filter ($0.38 of the $0.75 a litre costs); dialysis
      across the culture saves $4–9 if its membrane holds up. The sorbent lever counted the filter as saved and was corrected
      (the $22.97 quoted here before is $28.22).
- [ ] **Bench tests the reuse study asks for**: electrodialysis of real spent medium (removal per pass, nutrients and growth factors
      lost, energy); a dialyser on a dense culture for weeks (clearance against time); a dialysate cleaned to under 10% make-up.
- [ ] **What the least medium flow is made of** (16 of the low-lactate example's 28 L/kg): nutrients, small by-products or large ones. It decides
      which reuse route can go below 16 L.
- [x] **Reuse on the page** as a lever (2026-11-20: `clean`, `wash_price`, off by default); a measured input for any route is still missing.
- [x] **Bands widened** (2026-11-16, `scenarios.MC_ESTIMATES`): they draw the ammonia the cells tolerate, the protectant's price and
      dose, the least medium flow, antifoam and the membrane price. The low-lactate example $27–38 → $25–47; the all-favourable example $9–12 → $10–19, median share
      3.8% → 1.9%. The protectant prior now stops at $120/kg (was the $260 catalogue price): a judgement until a quote arrives.
- [x] **Wrong-way demand inputs** (2026-11-16): a real flaw (the dollar channel's price coefficient could turn positive at high loss
      aversion) is fixed; the rest is an open question below.
- [ ] **Dollars or ratios**: how much of the price response is in dollars and how much is a ratio to the cut's price is not pinned by
      the data; it moves the low-lactate example's share 0.3–0.7%. Find data that separates them (premium-cut elasticities against commodity ones),
      or draw `w_ratio` in the bands with a precomputed calibration grid.
- [x] **The all-favourable example's point cost is below most of its draws** (5% of draws below $6.97 since 2026-11-21): explained in
      `model_audit.md` section 3f (priors skewed to the costly side; not a defect) and said in its story on the page.
- [x] **Judgements set at the low-lactate example's 191 g/L** (2026-11-19): done 2026-11-21. The example now runs at 168 g/L; the
      tables in `no_perfusion_downside.md` and the retention notes are labelled as the model's rough judgement and marked as dated
      snapshots (each row names its own density), and `cell_trait_routes.md`'s appendix of odds by 2035 is deleted.
- [x] **The last snapshot parts**: `tests/test_gas_exchange.py` and `tests/test_plant_items.py` (done 2026-11-21): the checks run with
      `floor_physics.BEFORE_FILTER_LOOP` are marked as history (the notes' dated snapshots), and each test gained `_check_current`,
      which pins the note's box of figures at the model's own settings.
- [x] `explore` let fresh medium fall below the liquid that leaves with the harvested cells. Floor added 2026-11-16 (a medium term,
      "harvest"); no scenario moved, the airlift in perfusion went from $14.78 to $15.07.

- [ ] **Demand near price parity** (`premium_curve.md`): anchored on premium real meats the all-favourable example's cells take 2.5%, against the model's
      5.4% with the ordinary demand. The premium data start at 1.5×. Find data on labels sold at or near parity (cage-free eggs after retailer pledges, Dutch
      Beter Leven 1 star, Label Rouge promotions) to see which is closer.
- [ ] **Show the premium-meat anchoring on the page**, or refit κ to the sixteen premium products? Open; nothing changed so far.

Bench measurements that would settle the two biggest inputs (from #45; each is cheaper than a pilot tank, and no meat-cell data exists):

- [ ] **Ammonia at density:** the real cell line in a 1–2 L perfusion at 10–20% cells by volume, serum-free, ammonium held at
      2, 3, 4, 5 and 7 mM for 10 days each, pH fixed; repeat 4 and 7 mM on cells raised slowly to that level. The answer is the
      highest level that keeps growth within 10%. A rough estimate: $15–40k, two to three months.
- [ ] **Filter life with meat cells:** 0.025 m² hollow fibres (0.2 µm and one wide-pore) on a meat-cell perfusion at 15–20% cells
      by volume, at 2.5 and 5 L/m²/h, with the model's antifoam and protectant doses and one daily backflushed module; record
      pressure and sieving against litres per m² and against days. A rough estimate: $20–50k, six weeks.
- [ ] **Life and price of a cheaper membrane class together:** prices are already bracketed ($3–14 a m² dialyser fibre to $1,450
      pharma, `retention_alternatives.md`); what is missing is how long the cheap classes (dialyser, wide-pore, ceramic) last in
      a thick animal-cell culture. A quote alone cannot settle it, so the filter bench run above should include one of them.
      Until then life and price stay as they are; nobody has offered a price (Pablo, 2026-11-16).

- [x] **`sc_glc_measured` re-derived** (2026-11-18): the central 0.84 rests on CHO data, not Pasitka; the range is now 0.67–3.6, and
      the high end moves Published cells by $92 a kilo, not the low-lactate example.

Things only Pablo can do:

- [ ] Find one bioprocess engineer to read RESULTS and METHODS (GFI science team, Humbird, the Unjournal workshop).
- [ ] Check the AI Office's rules on outside activities before publishing new work.
- [ ] Ask a supplier (BASF or a distributor) for a tonne price of poloxamer 188 (the model assumes $30/kg; band $5–100 since
      2026-11-21, `evidence_poloxamer_price.md`). Draft request in `evidence_outreach_drafts.md` (b).

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
| G | Medium regeneration TEA | levers since 2026-11-20 | `explore(clean=...)`, `wash_price`: $0.8–3.5/kg on the permeate, $3.9–15.8 across the culture in the low-lactate example; next is bench data |
| A3 | Oxygen, CO₂ and pH gradients at 20 and 200 m³ | idea | after A0–A2; since the per-tank plant items `tank_size.md` finds every example 5–7% cheaper at about 90–170 m³ |
| F | Cost-optimal growth rate (the proposal PDF) | idea | two-day check first: is it worth more than ~$1.7/kg? |
| H | Bench foam test, or a protocol for a partner lab | idea | optional |

## 4. Done since the project review (for reference)

Gas exchange and the column (B, K, A) · what caps the gas flow (M3) · plant items and contamination (J, G) · holding the
cells back (I) and cheaper membranes · vessel × mode grid · scenarios · tank size 2–200 m³ · thick culture above 258 g/L ·
least medium per kg · the nutrient floor and GFI medium costs · growth-factor prices and the fastest doubling · the case
without perfusion. Each has a note in `research_notes/` and a CHANGELOG entry.
