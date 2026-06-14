# Cultivated meat: a levers-and-bottlenecks model

*How cheap can cultivated meat plausibly get, and how many animals would that displace?*

A small, fully-reproducible techno-economic + adoption model that answers the two questions a
funder actually cares about. It is anchored to the **one empirical TEA** (Pasitka et al., *Nature
Food* 2024) and bounded by the **physical feedstock floor** (Humbird 2021). Every number is sourced
and lives in exactly one place; every result reproduces from the code with one command.

- **Read the findings:** [RESULTS.md](RESULTS.md) (results brief) or [POST.md](POST.md) (the essay).
- **Read the methods:** [METHODS.md](METHODS.md) (mechanisms, equations, every parameter + source).
- **Play with it:** open [interactive.html](interactive.html) in a browser — a self-contained,
  dependency-free explorer (the Python model hand-ported to JS, kept in lock-step by a parity test).
- **Critical read:** [REVIEW.md](REVIEW.md).

---

## The model in one line

A chain, computed **per type of meat** — because cultivated *cost* is ~constant across species (it's
animal cells in a bioreactor) while conventional *price* ranges ~5× (cheap chicken to sushi):

> **biomass cost → retail price ratio `R` → market share → total penetration**

It produces **two outputs of deliberately different trust levels**:

- **Output 1 — the price ratio `R` = cultivated retail price / conventional price.** *High-trust:* a
  TEA-grounded cost projection over a *known* market price. Most of the leverage is here.
- **Output 2 — the market share** that `R` buys, rolled up across meat types. *Softer:* a calibrated
  two-segment, four-product discrete-choice demand model on transplanted elasticities. **Always a
  band, never a point.**

For the headline numbers and conclusions, see [RESULTS.md](RESULTS.md) — they are not repeated here
on purpose (see *Design principles* below).

---

## The ladder

The model is built **one mechanism per rung**. No rung is a sketch; no rung introduces something a
later rung deletes. A rung that needs a number it cannot yet produce takes it as an *input*.

| Rung | File | Adds |
|---|---|---|
| 1. Price ratio | [`price_ratio.py`](price_ratio.py) | `R` and the parity-cost **threshold** (additive markup). No cost mechanism — takes biomass cost as input. |
| 2. Cost + scale-up | [`cost_model.py`](cost_model.py) | Pasitka component cost; the **scale-up bottleneck** (overhead across 3 reactor configs); the irreducible floor; the cost waterfall. |
| 3. Demand → share | [`market_share.py`](market_share.py) | Two-segment, four-product discrete-choice model (conventional / plant-based / cultivated / whole-food), calibrated to plant-based's real ~1% share. |
| 4. Timing | [`adoption_timing.py`](adoption_timing.py) | Rollout (Bass diffusion) + fading neophobia + **cost-milestone paths** over 30 yr. |
| 5. Uncertainty | [`uncertainty.py`](uncertainty.py) | Monte-Carlo distribution over `R` and share from the sourced priors — the endpoint, not a path. |
| 6. Scaffolding | [`scaffolding.py`](scaffolding.py) | The structured (premium-seafood) product + scaffold cost — the most speculative rung, flagged loudly. |

Cross-cutting analyses on top of the ladder:

- [`meat_market.py`](meat_market.py) — cultivated's share across the **spectrum of meats** (price and
  demand run opposite; the entry point is the mid-cuts, not luxury or commodity).
- [`sensitivity.py`](sensitivity.py) — the **tornado**: which knobs move `R` and the share most
  (the levers & bottlenecks), cross-checked against the Monte-Carlo variance shares.

---

## Quickstart

```bash
# from the model/ directory
python -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt                     # numpy, matplotlib, markdown

python inputs.py            # print the full datasheet: every number, with source + MC range
python report_figures.py    # regenerate the curated figure set into figures/
```

Runtime deps are just **numpy + matplotlib** (and `markdown` for the HTML builders). The
Python↔JS parity test additionally wants **Node.js 18+** on `PATH`, but skips gracefully if absent.

### Run an individual rung

Each rung module runs as a script and emits its figure(s). Most take a `--no-latex` flag (figures
render with real LaTeX when a TeX engine is present, else a clean fallback):

```bash
python cost_model.py
python market_share.py
python uncertainty.py --target sushi-salmon --fix process_cost=5   # pin any input
python sensitivity.py --no-latex
```

---

## Reproducing the outputs

| To regenerate… | Run |
|---|---|
| The curated report figures (`figures/*.png`) | `python report_figures.py` |
| The interactive explorer (`interactive.html`) | `python build_interactive.py` |
| The standalone essay (`POST.html` from `POST.md`) | `python build_html.py` |
| The full test suite (rebuilds the page first) | `./run_tests.sh` |
| Publish the explorer to the personal site | `python publish_site.py [--push]` |

> **`build_interactive.py` is generative.** It reads constants and slider ranges straight from
> `inputs.py` + `meat_market.py` and hand-ports ~20 model functions into the JS embedded in
> `interactive.html`. **Never hand-edit the JS in `interactive.html`** — it is overwritten on every
> build. Edit the Python, then rebuild.

---

## Design principles

These three rules are the reason the model can be trusted — and the things to preserve when editing.
The full discipline (with the provenance audit and the anti-drift checklist) is in
[METHODS.md](METHODS.md).

1. **Single source of truth for every number.** Every concrete value lives once in
   [`inputs.py`](inputs.py) as an `Input` record carrying both its point value *and* its
   Monte-Carlo prior, plus its unit, source, and a note. So the point estimate and the uncertainty
   band can never drift apart. Run `python inputs.py` for the self-documenting datasheet.

2. **No free knobs.** Every number is forced into one of five categories — *sourced*, *derived*,
   *solved to a published moment*, *judgement-but-swept*, or *assumed-but-shown-not-to-matter*. None
   is a constant left to taste. The cost stack is **Pasitka-anchored** throughout; company claims are
   tagged as unverified self-reports.

3. **The model exists in three coupled forms, kept in sync by tests.** The Python source of truth,
   the generated JS in `interactive.html`, and the prose (equations + quoted numbers). Divergence is
   the biggest maintenance risk, so:
   - **Python ↔ JS** is guarded automatically by `tests/run_parity.py`.
   - **Code ↔ numbers quoted in prose** is guarded by computed `{{TOKEN}}`s + golden derived-number
     checks.
   - **Code ↔ equations described in words** is a manual discipline (no test can check English) —
     see the anti-drift checklist in [METHODS.md](METHODS.md).

**The workflow rule:** after *any* change to a Python model function, re-run
`python build_interactive.py` (re-ports the JS) and `./run_tests.sh` before committing.

---

## Tests

```bash
./run_tests.sh        # rebuilds interactive.html, then runs both checks
```

- **Golden-value regression** ([`tests/test_golden.py`](tests/test_golden.py)) — pins the headline
  outputs (the price ratio `R`, the plant-based share, the at-parity cultivated share, the
  plant-based-milk cross-check, the derived β / calibration values, the regional income gradient, the
  US roll-ups). Any accidental formula or default change is caught with the old-vs-new value shown.
  If a change is intentional, update `GOLDEN` in the same commit so the move is explicit in the diff.
- **Python ↔ JS parity** ([`tests/run_parity.py`](tests/run_parity.py)) — extracts the embedded JS,
  runs it under Node, and asserts it matches the Python model to a tight tolerance over a ~2,000-point
  grid plus the calibration solve, the milk check, and the timing rung. Skips (does not fail) if Node
  is absent.

More detail in [`tests/README.md`](tests/README.md).

---

## Repository map

```
model/
├── inputs.py            ← the datasheet: every number, source, and MC prior (start here)
├── price_ratio.py       ← Rung 1: R and the parity threshold
├── cost_model.py        ← Rung 2: Pasitka cost + scale-up bottleneck + floor
├── market_share.py      ← Rung 3: the four-product, two-segment demand model
├── adoption_timing.py   ← Rung 4: rollout + neophobia + cost-over-time
├── uncertainty.py       ← Rung 5: Monte-Carlo over R and share (shared cost→R equation)
├── scaffolding.py       ← Rung 6: structured / premium-seafood product
├── meat_market.py       ← cultivated share across the spectrum of meats
├── sensitivity.py       ← the tornado: levers & bottlenecks, ranked
├── common.py            ← shared plotting style / figure saving (no model logic)
├── report_figures.py    ← builds the curated figure set in story order
├── build_interactive.py ← generates interactive.html (Python model → JS/SVG explorer)
├── build_html.py        ← renders POST.md → self-contained POST.html
├── publish_site.py      ← publishes the explorer to the personal site
├── run_tests.sh         ← rebuild + run the test suite
├── tests/               ← golden-value + Python↔JS parity tests
├── figures/             ← curated PNGs (diagnostics/ holds the rest)
├── METHODS.md           ← mechanisms, equations, parameter sourcing, anti-drift checklist
├── RESULTS.md           ← the results brief (headline numbers + figures)
├── POST.md / POST.html  ← the essay write-up
└── REVIEW.md            ← critical read
```

---

## Sources

The model is anchored to **Pasitka et al. 2024** (*Nature Food*) — the one empirical TEA — for the
cost stack, with **Humbird 2021** supplying the physical amino-acid feedstock floor and the rationale
for why scale-up is hard. Demand is calibrated to observed plant-based shares (GFI / SPINS / NIQ),
elasticities transplanted from scanner meta-analyses, and ethical-segment weights from Gallup. Every
parameter's provenance is tagged in [`inputs.py`](inputs.py); run `python inputs.py` to print it.
