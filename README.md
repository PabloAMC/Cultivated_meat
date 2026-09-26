# Cultivated meat: how much of the meat market can it win — and how fast?

*A cost and demand model: how cheap can cultivated meat plausibly get, and how much conventional meat
would that displace?*

**👉 [Open the interactive explorer](https://pabloamc.github.io/Cultivated_meat/interactive.html).** It
leads with the findings, lets you change every assumption, and explains how the model works in plain
language (“How the model works”, at the bottom of the page).

- **The findings:** [RESULTS.md](RESULTS.md).
- **Code-level methods and sources:** [METHODS.md](METHODS.md).
- **Run it offline:** open [interactive.html](interactive.html) in a browser. It is self-contained; the
  Python model is ported to JavaScript and kept in step by a parity test.
- **The essay:** [Cultivating hope](https://forum.effectivealtruism.org/posts/ED2ag8hYTWf4kmL3x/cultivating-hope-calibrating-the-expectations-for-cultivated)
  on the EA Forum.

The model is anchored to the only peer-reviewed cost study built on measured production data (Pasitka et
al., *Nature Food* 2024) and bounded by the physical feedstock floor (Humbird 2021). Every number is sourced
and lives in one place, and every result reproduces from the code.

---

## The model in four steps

Computed for each type of meat and region, because cultivated meat costs about the same whatever animal it
copies, while conventional prices vary about fivefold (cheap chicken to sushi):

1. **Cost → price:** what a kilo costs to grow, plus retail costs, divided by the price of the meat beside
   it: the price ratio **R**.
2. **Price → choice:** shoppers choose between conventional meat, plant-based meat, cultivated meat and
   beans, weighing price, taste, “is it real meat?”, health and animal welfare (a two-segment logit
   calibrated to plant-based meat's observed ~1.2% share).
3. **Every meat, every region:** repeat at each meat type's local price, then add up by volume and by value.
4. **Over time:** start from today's wary shoppers and grow as the product spreads and becomes familiar.

The two outputs carry different levels of trust. **R** is a cost built from measured data over an observed
price: fairly solid. **The market share** depends on how people will treat a product nobody can buy yet, so
it is always a band.

---

## Modules

| step | module | what it adds |
|---|---|---|
| 1 | [`price_ratio.py`](price_ratio.py) | R and the parity threshold (additive markup) |
| 1 | [`cost_model.py`](cost_model.py) | Pasitka's cost stack, the reactor scale-up lever, the floor, the cost waterfall |
| 2 | [`market_share.py`](market_share.py) | the four-product, two-segment demand model, its calibration and self-checks |
| 3 | [`meat_market.py`](meat_market.py) | share by meat type and region; volume and value totals; the regional Monte Carlo |
| 3 | [`scaffolding.py`](scaffolding.py) | structured products (cuts, fillets) and their scaffold cost; the most speculative part |
| 3 | [`foothold.py`](foothold.py) | entry points: which specific products cultivated can reach first, and what each displaces |
| 4 | [`adoption_timing.py`](adoption_timing.py) | rollout (Bass diffusion), fading novelty, cost-milestone paths over 30 years |
| – | [`uncertainty.py`](uncertainty.py) | Monte Carlo over R and share |
| – | [`sensitivity.py`](sensitivity.py) | which inputs move R and share most (tornado) |

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
   range, or an assumption whose leverage is reported. The cost side is anchored to Pasitka throughout;
   company reports are treated as directional evidence.
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
├── cost_model.py        ← step 1: Pasitka's costs, the scale-up lever, the floor
├── market_share.py      ← step 2: the four-product, two-segment demand model
├── meat_market.py       ← step 3: share by meat type and region
├── scaffolding.py       ← step 3: structured products and their scaffold cost
├── foothold.py          ← step 3: entry points (specific products)
├── adoption_timing.py   ← step 4: rollout, fading novelty, cost-milestone paths
├── uncertainty.py       ← Monte Carlo over R and share
├── sensitivity.py       ← which inputs matter most
├── common.py            ← shared plotting helpers (no model logic)
├── report_figures.py    ← builds the curated figure set
├── build_interactive.py ← generates interactive.html (model → JS/SVG explorer + text)
├── run_tests.sh         ← rebuild + run the tests
├── tests/               ← golden-value and Python↔JS parity tests
├── figures/             ← curated PNGs (diagnostics/ holds the rest)
├── RESULTS.md           ← the findings
├── METHODS.md           ← code-level methods, sources and the anti-drift checklist
├── DESIGN_authenticity_demand.md ← design note behind the entry-point analysis (historical)
└── REVIEW.md            ← a June 2026 review of the explorer (historical)
```

---

## Sources

Cost: **Pasitka et al. 2024** (*Nature Food*) for the cost stack and reactor designs; **Humbird 2021** for the
feedstock floor and why scale-up is hard. Demand: calibrated to observed plant-based shares (GFI/SPINS/NIQ),
price sensitivity from grocery scanner meta-analyses and a cultivated-meat choice experiment (Van Loo, Caputo &
Lusk 2020), the ethical segment from Gallup. Every parameter's source is tagged in [`inputs.py`](inputs.py).
