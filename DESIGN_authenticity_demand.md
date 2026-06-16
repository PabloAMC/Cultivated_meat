# Design note — authenticity-WTP demand extension (DRAFT for review)

*Status: proposal, not built. This is the principled economic model the foothold work kept
gesturing at; the goal here is to replace a stack of patches (margin caveats, prestige/aspirational
split, rent discounts, incumbent-response notes) with **one** primitive, and to fold the foothold
scorecard into the structural demand model rather than maintaining it as a parallel heuristic.*

*Red-pen targets are marked **[Q]**. Provisional numbers are flagged. Nothing is calibrated yet.*

---

## 1. The one missing primitive

The current `market_share.py` treats **real-tissue** as a single binary attribute (cultivated = 1,
conventional = 1) with a segment-fixed weight. That conflates two genuinely different things:

- **real-tissue (functional):** *"is this genuine animal tissue?"* — cultivated **is** (=1). This is
  the identifying premise and is why cultivated competes with conventional, not plant-based.
- **authenticity (provenance / credence):** *"is this the specific authentic product — terroir,
  wild-caught, heritage, the grade/brand?"* — cultivated is **not** (=0), by construction.

For commodity meat these coincide (real tissue ≈ "the thing"), so the conflation is harmless. For
luxury they **diverge**: cultivated wagyu is real tissue but is not authentic A5 wagyu. The current
model hands cultivated full real-tissue credit even there, so it **overstates luxury share and is
blind to the rent.**

The fix is to add **authenticity as its own characteristic** and make the **taste for it
heterogeneous across consumers**. Almost everything we bolted on is then *emergent*:

| Bolted-on patch | Emerges from |
|---|---|
| rent ≠ cost; margin overstated | hedonic value of the authenticity characteristic (Rosen 1974) |
| prestige core vs aspirational base | the two tails of the authenticity-WTP distribution |
| luxury incumbent holds price, cedes volume | best response to bimodal demand (Veblen corner) |
| realizable "fuel" | (achievable price − cost) × addressable share × volume, all in-model |
| foothold ranking & the descent | the entrant's attainable surplus as cost falls / acceptance grows |

Organizing primitive: **the distribution of willingness-to-pay for authenticity, interacted with
cultivated's attribute position and a roughly fixed cost.**

---

## 2. Specification

### 2.1 Two characteristics where there was one

Keep `real_tissue` (functional) exactly as today. **Add** `authenticity` (provenance):

| product | real_tissue | authenticity |
|---|---|---|
| conventional (authentic) | 1 | 1 |
| cultivated | 1 | **0** |
| plant-based | 0 | 0 |
| whole-food | 0 | 0 |

`authenticity` is scaled per category by **`A_cat` ∈ [0,1]** — the *authenticity intensity* of the
category: ≈ 0 for commodity chicken, large for iberico / wagyu / wild bluefin / caviar. `A_cat` is
**not** hand-set — it is pinned by the observed price-tier gap (§4).

### 2.2 Heterogeneous taste for authenticity (the random coefficient, discretised)

We cannot estimate a continuous distribution (§5), so use a **two-point type** on top of the existing
M/E segments:

- **Prestige type** (fraction `φ_pre` of a category's buyers): authenticity weight `λ_pre` *large* —
  buys only the authentic product, price-inelastic, **never switches** to cultivated.
- **Aspirational type** (fraction `1 − φ_pre`): authenticity weight `λ_asp ≈ 0` — buys the category
  for taste/quality/safety, **switches on price**; this is cultivated's addressable base.

`φ_pre` varies by category (caviar ≈ all prestige; salmon mostly aspirational) and is pinned from the
prestige-tier volume share (§4). **[Q]** two types vs three (add a mid "premium" type)? Two is the
minimum that produces the core/base split; start there.

### 2.3 Revised utility

For segment `s ∈ {M,E}`, authenticity-type `τ ∈ {pre,asp}`, product `j`:

```
V[j,s,τ] = α·ln(y_eff − price_j)            (BLP income–price, as today)
         + q·taste_j
         + w_sl(s)·slaughter_j
         + w_rt(s)·realtissue_j             (functional real-meat, as today)
         + w_h(s)·health_j
         + λ(τ)·A_cat·authenticity_j        (NEW: provenance rent, heterogeneous)
         + ξ_j                              (per-product offset incl. cultivated novelty/neophobia)
```

Population share of cultivated = Σ_s Σ_τ weight(s,τ)·P(x | s,τ).
- **Prestige** (`λ_pre·A_cat` large): `P(x) ≈ 0` in high-`A_cat` categories — the core doesn't move.
- **Aspirational** (`λ_asp ≈ 0`): chooses on price + cultivated's capturable premiums — competitive.

cultivated's **capturable** premiums (safety / sustainability / welfare = the old `defect_*`) enter
through `health_j` and `slaughter_j` (and a possible new `safety_j` term), valued from WTP literature
(§5) — these are real and cultivated keeps them; only the `authenticity` term is forfeited.

---

## 3. The reference-price / hedonic correction

The authentic price decomposes (hedonically) into a base and a rent:

```
p_auth  =  p_base  +  rent ,      rent ≈ value of authenticity to the marginal prestige buyer
```

`p_base` = the **accessible tier** price of the same category (serrano vs bellota; farmed vs
sushi-grade salmon; standard vs A5 wagyu). The aspirational segment faces `p_base`, and **cultivated
competes against `p_base`, not the headline `p_auth`.** So:

```
R_x  =  cultivated_retail_price / p_base        (NOT / p_auth)
```

This is the single correction that fixes the "margin is overstated" problem *and* the
"incumbent-cedes-volume" problem at once: cultivated earns `p_base` (+ its own attribute premiums),
forfeits `rent`, and the prestige core (volume `φ_pre`, price `p_auth`) is shown as **out of reach
(rent), not addressable.**

In the foothold panel this means: for luxury categories the **reference price = `p_base`**, the
**addressable volume = the aspirational base** `(1 − φ_pre)·V_cat`, and the prestige core is drawn
separately as a greyed "rent — unaddressable" marker.

---

## 4. Calibration & identification (calibrate, do not estimate)

Per **luxury category**, pin from observable market structure:

| parameter | pinned by | source hook |
|---|---|---|
| `A_cat` (authenticity intensity) | the rent fraction `(p_auth − p_base)/p_auth` | observed prestige vs accessible tier prices |
| `φ_pre` (prestige buyer fraction) | volume split prestige-tier / total | category volume data |
| `λ_pre` (prestige weight) | global; set so prestige buyers rationalise paying `rent` (won't switch) | one global solve |

Globally:
- `λ_asp ≈ 0` (aspirational buyers ~indifferent to provenance) — **[Q]** exactly 0, or a small swept value?
- cultivated's attribute premiums (safety / sustainability / welfare): from **stated-preference /
  conjoint WTP studies** (organic, welfare-certified, contaminant-free, sustainable-seafood premia —
  these exist), entered as `health`/`slaughter`/`safety` positions, **swept**.
- PB ~1% moment (existing) still pinned by the calibration solve.

Everything new is **weakly identified → swept → reported as a band**, never a point. Validation: the
extended model must still (a) reproduce PB's ~1%, (b) reproduce the PB-milk out-of-sample ~15%, and
(c) rationalise the observed prestige/accessible price gaps in each luxury category it's pointed at.

---

## 5. What fades and what is permanent (dynamics)

Distinguish two parts of cultivated's `authenticity = 0` disadvantage:

- **Novelty / neophobia** (`ξ_x`): *fades* with exposure (mere-exposure; already in Rung 4). Recovers
  the **aspirational base** over time.
- **Structural authenticity gap** (`λ_pre·A_cat`): *permanent* — cultivated will never be "wild-caught"
  or DO-certified terroir. The **prestige core is never recovered**, at any acceptance level.

So acceptance growth lifts cultivated toward the aspirational ceiling but **not** through it — a clean,
honest cap that the current model lacks.

---

## 6. How the foothold layer is derived (no more parallel heuristic)

The foothold scorecard ordinals become **projections of the structural model**, not hand-set vibes:

- `authenticity` ordinal → `A_cat` (from the price-tier rent fraction). Derived.
- `defect_*` ordinals → cultivated's capturable attribute premiums (the `health`/`slaughter`/`safety`
  positions). Sourced from WTP studies.
- **realizable fuel** (the thing to maximise) → `(p_base + premiums − cost) × P(x | aspirational) ×
  (1−φ_pre)·V_cat`. This automatically collapses pure-prestige categories (caviar: `φ_pre`→1, tiny
  base) and rewards big-aspirational-base categories (salmon, foie-gras-style, accessible-wagyu).
- `tractability` / `transferability` stay as a **separate, explicitly-labelled supply/strategy
  overlay** (they govern *when* cultivated can make a product and whether capability transfers — not
  the equilibrium share), so they don't masquerade as demand parameters.

The waterline / margin×share panels then become **read-outs of the structural model**, not a second
model.

---

## 7. Scope guards (what we deliberately do NOT do)

- **No full BLP estimation** — unidentified pre-commercially; would launder priors into false
  precision (the "noise not clarity" failure mode).
- **No oligopoly supply game** — the one robust incumbent result (luxury brands defend via
  certification / labeling / regulation, *not* price) enters demand as raised authenticity *salience*
  (a credence-good / GI mechanism), not a price reaction.
- **No change to the cost side** — the media-driven waterline + irreducible floor stay as-is.
- **Luxury outputs stay bands / scenarios**, never forecasts.

---

## 8. Implementation plan (if approved)

1. **`inputs.py`** — add, per luxury category: `p_auth`, `p_base`, `phi_pre`, `A_cat` (derived),
   with provenance tags + MC ranges. Add cultivated attribute-premium priors.
2. **`market_share.py`** — add the `authenticity` characteristic and the two-point `τ` mixture;
   extend `_utilities`/`_segment`/`share` and the calibration solve to carry it. Reference price for a
   given comparison switches to `p_base`.
3. **`tests/test_golden.py`** — pin the new headline values (luxury aspirational shares, the
   prestige-core ≈ 0 result) and keep PB ~1% / PB-milk ~15% green.
4. **`build_interactive.py`** — re-port the extended JS; **`tests/run_parity.py`** must stay green
   (this is the biggest cost — the mixture adds a dimension to the JS mirror).
5. **`foothold.py` / the panel** — derive `authenticity`/`defect` from the structural objects; switch
   the luxury reference to `p_base`; draw the prestige core as a separate "rent — unaddressable"
   marker; replace gross margin with **realizable fuel**.
6. **`METHODS.md` / `RESULTS.md`** — document the new characteristic, the calibration moments, the
   fade-vs-permanent split, and the epistemic status (calibrated, swept, banded).

Sequence smallest-first, each gated: **(2)+(3) first** — does the extended demand model still hit PB
~1% and PB-milk ~15%, and does it rationalise one luxury price-gap (e.g. salmon farmed-vs-sushi)?
If yes, proceed to the JS/panel; if the calibration can't hold the moments, stop and report.

---

## 9. Risks & open questions for red-pen

- **[Q] Identification of `φ_pre` / `A_cat`.** Are prestige-vs-accessible price tiers and volume
  splits observable cleanly enough per category, or only for a few (salmon, wagyu, ham)? If only a
  few, we restrict the structural treatment to those and keep others heuristic.
- **[Q] Two types vs a continuous distribution.** Two points give the core/base split; a continuous
  (e.g. log-normal authenticity-WTP) is more honest but harder to pin. Start two, note the limitation.
- **[Q] Does `p_base` double-count with the authenticity term?** Risk: discounting price *and*
  penalising authenticity in utility = double penalty. Resolution: prestige buyers face `p_auth` with
  the authenticity term; aspirational buyers face `p_base` with `λ_asp≈0`. Keep the two consistent so
  the rent is counted once. **Needs careful wiring in the solve.**
- **[Q] Parity-test burden.** The mixture roughly doubles the share computation the JS must mirror.
  Worth it? Alternative: keep the structural model in Python only, and have the panel call a
  precomputed table rather than re-deriving in JS (breaks the "live sliders" property for the new
  parameters). Trade-off to decide.
- **[Q] Attribute-premium WTP transfer.** Borrowing organic/welfare/sustainable WTP estimates onto
  cultivated is itself a transplant (like the meat-elasticity transplant). Flag as soft.

---

*End of draft. The single decision that unlocks the rest: adopt **authenticity as a separate,
heterogeneously-valued characteristic with `p_base` as cultivated's reference price**. Everything in
§2–§6 follows from that; §7 keeps it from sprawling.*
