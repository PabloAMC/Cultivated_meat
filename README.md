# Cultivated meat: cost and market share

*A cost and demand model: how cheap can cultivated meat plausibly get, and how much conventional meat
would that displace?*

**👉 [Open the interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html).** It
leads with the findings, lets you change every assumption, and explains how the model works in plain
language (“How the model works”, at the bottom of the page).

- **The findings:** [RESULTS.md](RESULTS.md).
- **Code-level methods and sources:** [METHODS.md](METHODS.md).
- **Run it offline:** open [interactive.html](interactive.html) in a browser. It is self-contained. The
  Python model is ported to JavaScript, and a parity test keeps the two in step.
- **The essay:** [Cultivating hope](https://forum.effectivealtruism.org/posts/ED2ag8hYTWf4kmL3x/cultivating-hope-calibrating-the-expectations-for-cultivated)
  on the EA Forum.

**Scenarios** describe the cost of a kilo of cells. They form a ladder ordered by how hard each change is: the published cells (the best
meat cells in the published record), then process changes and cheaper inputs, then cells selected to make less lactate and grow faster
(Selected cells), then a cheaper plant, then engineered cells (the Engineered cells, all favourable case). A forecast for
2035, Humbird's optimistic design and the process one company reports sit beside the ladder.
Each is a preset of ten switches, and each states what has to go right for it. See [RESULTS.md](RESULTS.md) and the page.
Earlier versions called Humbird's optimistic design the floor. It was then $11.5/kg; it is now $12.8, with the filter loop and the protectant counted.
The model keeps it as a labelled comparison, not a limit.

The reported cost is what a company reports for its own process (SuperMeat 2024). The physics of oxygen and CO₂ exchange and Humbird's plant design (2021) bound the scenarios.
Every number is sourced and lives in one place, and every result reproduces from the code.

> **Disclaimer.** The views expressed here are purely those of the author, Pablo Antonio Moreno Casares, and may
> not in any circumstances be regarded as stating an official position of the European Commission. The model and
> its page were built with the help of an AI assistant (Claude, Anthropic), and no human expert has reviewed them
> yet. This is research, not investment,
> business or policy advice.

---

## The model in four steps

The model runs for each type of meat and region, because cultivated meat costs about the same whatever animal it
copies, while conventional prices vary about fivefold (cheap chicken to sushi). It has four steps:

1. **Cost → price.** The cost of growing a kilo, plus retail costs, divided by the price of the meat beside
   it, gives the price ratio **R**.
2. **Price → choice.** Shoppers choose between conventional meat, plant-based meat, cultivated meat and
   beans. They weigh price, taste, “is it real meat?”, health and animal welfare. This is a two-segment logit
   calibrated to plant-based meat's observed ~1.2% share. How much shoppers like cultivated meat differs from one shopper
   to the next (a Student's t spread, fitted to a choice experiment and to premium real meats).
3. **Every meat, every region.** The model repeats the choice at each meat type's local price, then adds up by volume and by value.
4. **Over time.** The share starts from wary shoppers and grows as the product spreads and becomes familiar.

The two outputs deserve different levels of trust. **R** is a cost built from measured data over an observed
price, so it is fairly solid. **The market share** depends on how people will treat a product that nobody can buy yet, so
it is always a band.

---

## Modules

| step | module | what it adds |
|---|---|---|
| 1 | [`price_ratio.py`](price_ratio.py) | R and the parity threshold (per-kg costs plus the shop's percentage margin) |
| 1 | [`cost_model.py`](cost_model.py) | the reported cost stack (medium and plant), three plant cases, Humbird's optimistic design, the cost waterfall |
| 1 | [`scenarios.py`](scenarios.py) | the cost scenarios: ten switches, what has to go right for each scenario, what to prioritise, interactions, bands |
| 1 | [`vessels.py`](vessels.py) | vessel type against operating mode, everything else held: cost, limit and maturity of each combination |
| 1 | [`retention.py`](retention.py) | holding the cells back in a 20 m³ perfusion tank: the duty and each real device's cost; every scenario uses the filter loop it prices |
| 2 | [`market_share.py`](market_share.py) | the four-product, two-segment demand model, its calibration and self-checks |
| 3 | [`meat_market.py`](meat_market.py) | share by meat type and region; volume and value totals; the regional Monte Carlo |
| 3 | [`scaffolding.py`](scaffolding.py) | structured products (cuts, fillets): cells bound with plant protein, and the cost of assembling them |
| 3 | [`foothold.py`](foothold.py) | entry points: which specific products cultivated can reach first, and what each displaces |
| 4 | [`adoption_timing.py`](adoption_timing.py) | rollout (Bass diffusion), fading novelty, cost-milestone paths over 30 years |
| – | [`uncertainty.py`](uncertainty.py) | Monte Carlo over R and share |
| – | [`sensitivity.py`](sensitivity.py) | which inputs move R and share most (tornado) |
| – | [`growth_rate.py`](growth_rate.py) | side-study: does growing the cells slower ever lower the cost per kg? |
| – | [`floor_physics.py`](floor_physics.py) | the cost of a kilo of cells from oxygen and CO₂ physics, by reactor type and plant class (with no arguments it gives Humbird's optimistic design) |
| – | [`design_space.py`](design_space.py) | what each tank limit is worth, and a search over every combination of tank design options |
| – | [`medium_reuse.py`](medium_reuse.py) | cleaning and reusing the medium: an ammonium exchanger, electrodialysis and dialysis, priced with the cell filter counted |
| – | [`industry_claims.py`](industry_claims.py) | the model against company cost claims, on the same basis: plant charge and operating cost split |
| – | [`plant_items.py`](plant_items.py), [`contamination.py`](contamination.py) | side-study: the plant's capital item by item, and the contamination a cheaper plant can afford |

---

## Quickstart

```bash
# from the model/ directory
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt                     # numpy, matplotlib

python inputs.py            # the datasheet: every number, its source and its Monte Carlo range
python report_figures.py    # regenerate the curated figures into figures/
python market_share.py      # the demand model's calibration and self-checks
```

Runtime dependencies are **numpy** and **matplotlib**. The
Python↔JS parity test also needs **Node.js 18+**; it skips cleanly if Node is missing. Most scripts take
`--no-latex` (figures use real LaTeX when a TeX engine is present, otherwise a clean fallback):

```bash
python cost_model.py
python uncertainty.py --target sushi-salmon --fix process_cost=5   # pin any input
python sensitivity.py --no-latex
```

---

## Reproducing the outputs

| to regenerate… | run |
|---|---|
| the curated figures (`figures/*.png`) | `python report_figures.py` |
| the interactive explorer (`interactive.html`) | `python build_interactive.py` |
| the full test suite (rebuilds the page first) | `./run_tests.sh` |

> **`build_interactive.py` is generative.** It reads constants and slider ranges from `inputs.py` and
> `meat_market.py`, ports the model functions into the JavaScript embedded in `interactive.html`, and fills
> every number in the page's text from the model at build time. **Never hand-edit `interactive.html`**: it is
> overwritten on every build. Edit the Python, then rebuild.

The explorer is served from this repository's GitHub Pages (`pabloamc.github.io/Cultivated_meat/`), which is
also where the personal site and the EA Forum post link, so pushing a rebuilt `interactive.html` to `main`
updates the live page.

---

## Design principles

What makes the model trustworthy, and what to preserve when editing (details in [METHODS.md](METHODS.md)):

1. **One source for every number.** Each value lives once in [`inputs.py`](inputs.py) as an `Input` record
   with its point value, Monte Carlo range, unit, source and a note, so the point estimate and the
   uncertainty band can't drift apart. The inputs each Monte Carlo band samples are also listed once there.
2. **No free knobs.** Every number is sourced, derived, solved to a published fact, a judgement shown as a
   range, or an assumption whose leverage is reported. The scenarios are built from tank physics and Humbird's plant
   design; the reported cost is one company's report (SuperMeat 2024), treated as directional evidence.
3. **Three forms, kept in sync by tests.** The Python source of truth, the generated JavaScript, and the
   prose:
   - **Python ↔ JS:** `tests/run_parity.py`, including a statistical check that the page's Monte Carlo band
     matches Python's.
   - **Code ↔ numbers in the prose:** every model number in the page is a build-time token, and the golden
     test checks the tokens and the Monte Carlo figures quoted in RESULTS.md and METHODS.md.
   - **Code ↔ equations described in words:** a manual discipline; see the checklist in METHODS.md.

**The workflow rule:** after any change to a model function, run `python build_interactive.py` and
`./run_tests.sh` before committing.

---

## Tests

```bash
./run_tests.sh        # rebuilds interactive.html, then runs both checks
```

- **Golden values** ([`tests/test_golden.py`](tests/test_golden.py)): pins the headline outputs (R, the
  plant-based share, the at-parity share, the plant-based-milk check, the derived price coefficients, the
  regional income gradient, the US totals) and checks that every number quoted in the page and the Markdown
  docs matches the model. If a change is intentional, update `GOLDEN` in the same commit.
- **Python ↔ JS parity** ([`tests/run_parity.py`](tests/run_parity.py)): runs the page's JavaScript under
  Node and checks it matches the Python model to 1e-4 over ~2,000 grid points, plus the calibration, the milk
  check, the timing rung and the Monte Carlo band.

More in [`tests/README.md`](tests/README.md).

---

## Repository map

```text
model/
├── inputs.py            ← the datasheet: every number, source and Monte Carlo range (start here)
├── price_ratio.py       ← step 1: R and the parity threshold
├── cost_model.py        ← step 1: the reported cost stack, the plant cases, Humbird's optimistic design
├── scenarios.py         ← step 1: the cost scenarios (switches, presets, priorities, interactions, bands)
├── page_sections.py     ← the page's computed tables (answer table, bottlenecks, cells by tank, vessels, evidence)
├── page_scenarios.js    ← the page's live switches (a JavaScript mirror of scenarios.py)
├── vessels.py           ← step 1: vessel type against operating mode
├── page_vessels.js      ← the page's vessel-by-mode table (a JavaScript mirror of vessels.py)
├── market_share.py      ← step 2: the four-product, two-segment demand model
├── meat_market.py       ← step 3: share by meat type and region
├── scaffolding.py       ← step 3: structured products and the cost of assembling them
├── foothold.py          ← step 3: entry points (specific products)
├── adoption_timing.py   ← step 4: rollout, fading novelty, cost-milestone paths
├── uncertainty.py       ← Monte Carlo over R and share
├── sensitivity.py       ← which inputs matter most
├── growth_rate.py       ← side-study: cost against doubling time (not used in the headline)
├── floor_physics.py     ← the cost of cells from tank physics, by reactor type and plant class
├── plant_items.py       ← side-study: plant capital item by item (Humbird's plant and his yeast plant)
├── contamination.py     ← side-study: detection, losses and break-even loss rates for cheaper plants
├── design_space.py      ← what each tank limit is worth; search over tank designs
├── medium_reuse.py      ← cleaning and reusing the medium (exchanger, electrodialysis, dialysis)
├── industry_claims.py   ← the model against company cost claims (plant charge vs operating cost)
├── common.py            ← shared plotting helpers (no model logic)
├── report_figures.py    ← builds the curated figure set
├── build_interactive.py ← generates interactive.html (model → JS/SVG explorer + text)
├── run_tests.sh         ← rebuild + run the tests
├── tests/               ← golden-value and Python↔JS parity tests
├── figures/             ← curated PNGs (diagnostics/ holds the rest)
├── RESULTS.md           ← the findings
├── TODO.md              ← open work, decisions waiting, project ideas
├── METHODS.md           ← code-level methods, sources and the anti-drift checklist
├── DESIGN_authenticity_demand.md ← design note behind the entry-point analysis (historical)
└── REVIEW.md            ← a June 2026 review of the explorer (historical)
```

---

## Sources

Cost: **Humbird 2021** for the plant design, the feedstock and the physics of scale-up; **SuperMeat 2024** (a company
report) for the reported cost; **Hubalek et al. 2023** and **Pasitka et al. 2024** (*Nature Food*) for what the published cells
make (Pasitka is no longer the cost anchor: METHODS.md, "Why Pasitka is not the anchor"). Demand: calibrated to observed plant-based shares (GFI/SPINS/NIQ),
price sensitivity from grocery scanner meta-analyses and a cultivated-meat choice experiment (Van Loo, Caputo &
Lusk 2020), the ethical segment from Gallup. Every parameter's source is tagged in [`inputs.py`](inputs.py).
