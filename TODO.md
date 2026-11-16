# To do

The one list of open work, decisions and project ideas. Keep it current: tick or delete an item in the same commit that
does it. Reasons and estimates for the projects are in [`research_notes/roadmap_2026-11-15.md`](research_notes/roadmap_2026-11-15.md);
the earlier idea list (A–T, M1–M8) is in [`research_notes/project_review.md`](research_notes/project_review.md).

Last updated 2026-11-16.

## 1. Waiting on Pablo

Open pull requests (each says "no default changes" unless noted):

- [ ] #19 Plain, direct sentences for all page text (wording only).
- [ ] #29 The frontier: every lever at its limit, one at a time ($26.64 → $5.49).
- [ ] #30 Filter flux: the flux is not the limit, the membrane's throughput is. **Decision inside:** move `rt_membrane_life`
      (3,960 L/m²) towards the measured 450–1,200? At 1,200 Central is $46.95.
- [ ] #31 Model audit: costs have only drifted up; Central's median over all ranges is $33. **Decisions inside:** show
      the spread beside each point; membrane life; first-plant or mature financing; a markup that is a share of price.

Decisions taken 2026-11-15 (late), on Pablo's instruction to pick the long-term option (numbers moved; CHANGELOG has them):

- [x] The plant ladder's perfusion rows are now `explore()` itself; `plant_floor` 9.8 → 10.8, `plant_floor_lo` 4.9 → 6.3.
- [x] The yeast-style plant buys its oxygen ($0.33/kg).
- [x] Poloxamer is costed: 2 g/L at an assumed $30/kg (catalogue $230–260). **Replace the price with a supplier quote.**
- [x] Antifoam's central value is 0.75 (the middle of 0–50%). Oxygen now limits Central and Cautious. **A measurement in dense
      meat-cell culture would replace this judgement**; it is worth about $1.8/kg in Central and $3.7 in Cautious.

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

- [ ] **What Central is for.** It has drifted from a forecast ("what is plausible") to a description of today's measured cells in a
      future plant. Decide whether to split it into "today's cells at 20 m³" and a dated forecast (each switch at its forecast median).
- [ ] **The reference case assumes the hardest thing (engineered cells) but not the easiest (tank tricks).** Tank tricks are feed or
      process changes; genetic engineering is the hardest tag. Rethink the reference, or the ladder of scenarios, by difficulty.
- [ ] **Shares that cannot be compared.** The table's scenario shares are medians of draws; the reference and the company figure are
      point estimates (reference 4.3% looks above best 3.8%, whose point estimate is 7.9%). Show both kinds side by side, or give every row a band.
- [ ] **Growth factors are a separate line from the medium.** They are dissolved in the medium, but priced separately because the medium
      prices companies report exclude them. Say so on the page, or fold them into one "medium with growth factors" figure.
- [ ] **Hybrid vessels and stirring.** A stirred tank with a draft tube and sparging, or other impellers. Now that oxygen limits Central,
      oxygen transfer per watt (impeller, sparger design) matters; in the model only the vessel's oxygen multiplier would change.

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
| A | FluidX3D tank: validate, mixing vs shape, the column's return plume | idea | first step: does FluidX3D run under OpenCL on the M4 |
| E | Hybrids and fat: cells as 5–20% of a plant-based product | idea | the near-term case for animals |
| D | Reported-run ledger with mass-balance flags | idea | merges T and S of the old list |
| G | Medium regeneration TEA | idea | sizing done in `waste_tricks_sizing.md` |
| A3 | Oxygen, CO₂ and pH gradients at 20 and 200 m³ | idea | after A0–A2; `tank_size.md` says 20 m³ is within 0.5% of the cheapest |
| F | Cost-optimal growth rate (the proposal PDF) | idea | two-day check first: is it worth more than ~$1.7/kg? |
| H | Bench foam test, or a protocol for a partner lab | idea | optional |

## 4. Done since the project review (for reference)

Gas exchange and the column (B, K, A) · what caps the gas flow (M3) · plant items and contamination (J, G) · holding the
cells back (I) and cheaper membranes · vessel × mode grid · scenarios · tank size 2–200 m³ · thick culture above 258 g/L ·
least medium per kg · the nutrient floor and GFI medium costs · growth-factor prices and the fastest doubling · the case
without perfusion. Each has a note in `research_notes/` and a CHANGELOG entry.
