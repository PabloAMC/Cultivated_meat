# Cultivated meat: levers, bottlenecks, and where it lands — results

*A techno-economic + adoption model of cultivated meat, anchored to the one empirical TEA
(Pasitka et al., Nature Food 2024) and bounded by the physical feedstock floor (Humbird 2021).
This is the results brief; mechanisms, equations, and every parameter source are in
[METHODS.md](METHODS.md). All numbers reproduce from the code (`python report_figures.py`).*

---

## The model in brief

The model is a chain, computed **per type of meat** (cultivated cost is ~constant across species, but
conventional price ranges ~5×, so the answer differs by animal):

> **biomass cost → retail price ratio R → market share → total penetration**

- **Output 1 — the price ratio** `R = cultivated retail price / conventional price`. *High-trust:* a
  TEA-grounded cost over a known market price. All the action is here.
- **Output 2 — the market share** that ratio buys, rolled up across meat types by volume (animal
  impact) and value ($). *Softer:* a **two-segment, four-product discrete-choice model** —
  conventional / plant-based / cultivated / whole-food, with a mainstream and an ethical segment, and
  **income-dependent price sensitivity** (BLP `ln(income − price)`: richer regions are less
  price-sensitive) — calibrated to plant-based's observed ~1% share and 89% mainstream buyer base.
  Always a **band**, never a point.

**Two gates decide the outcome:** (1) does cost reach parity? (cost-side, dominates); (2) at parity,
how do consumers treat lab-grown real meat? (the acceptance dials — taste-acceptance and cleaner-meat value). We take **no baked-in stance** on
gate 2 — it is the reader's to set.

### The key parameters (the levers — full datasheet in `inputs.py`)

| parameter | central | range | source | what it controls |
|---|---|---|---|---|
| `p_conv` | $12/kg | 10–14 | market | conventional meat price; with markup sets the parity threshold; **meat-tax lever** |
| `markup_add` | $5/kg | 2–7 | assumed | fixed biomass→retail wedge; floor $2 (cultivated skips slaughter) |
| `overhead` (scale-up) | $9.9/kg | 6–15; downside 24.7 | Pasitka Fig.4 | non-media plant cost = **reactor scale-up** |
| `media_price` | $0.63/L | 0.20–0.63 | Pasitka measured / GFI'26 claim | medium cost (centered on measured) |
| `efficiency` | 1.0× | 0.25–1.0 | Pasitka cells / CHO | cell media-use (centered on measured) |
| `accept_x` | 1.0 | 0.6–1.0 | the dial | **cultivated taste-acceptance (friction) — gate 2a** |
| `theta_free_M` | 0 | 0–1.0 | the dial | **mainstream slaughter-free value (upside) — gate 2b** |
| `neophobia_x` / `_p` | 0 | −2 … +1 | the dial | **novelty attitude** on cultivated / plant-based (− = neophobia, + = neophilia); 0 = neutral |
| `eps_own` | −0.9 | −1.4 … −0.5 | scanner | own-price elasticity of the meat **category** |
| `cult_sub_mult` (κ) | 4× | 3–6 | assumed | how many times **more** own-price-elastic *cultivated* is than the category (it has a near-perfect substitute); sets how steeply share falls **above** parity. Realized cultivated elasticity = `eps_own·κ` = −3.6 |
| `process_cost` | $5/kg | 1–15 | ungrounded | scaffold bioprocess (premium products only) |

The cost priors are **centered on Pasitka's measured values**: cheaper medium, more-efficient cells
and bigger reactors are the *optimistic tail*, never assumed. So the central case = what is
demonstrated today; improvements are upside.

---

## 1. The cost levers (Output 1)

Two figures carry the cost story. `cost_vs_inputs` plots biomass cost against the two dominant
inputs — **medium price** (x-axis, its $0.20–0.63 range shaded) and **reactor scale** (one line per
Pasitka reactor config) — with the irreducible floor. `cost_waterfall` walks the cost down from the
scale-up-stall case to the floor.

Ranking the inputs by how much each moves R (sensitivity tornado; the variance column is reused
verbatim from the Monte Carlo, so the two agree by construction):

```
KEY KNOBS — drivers of R   (baseline, all inputs at their measured/central value, R = 2.42)
  input         R(lo)  R(hi)  swing  var%   helpful end
  efficiency     1.54   2.42   0.88     4%   0.25x  (CHO-grade cells)
  p_conv         2.90   2.07   0.83    10%   $14/kg (expensive meat / meat tax)
  media_price    1.61   2.42   0.80     0%   $0.2/L (company claim)
  overhead       2.09   2.84   0.75    13%   $6/kg  (large-reactor scale)
  markup_add     2.17   2.58   0.42     4%   $2/kg
  swing = full lo→hi move (potential).  var% = share of the realised MC spread.
```

Two honest readings, and they differ in a way that matters:

- **By potential swing, four levers are comparable** (efficiency, p_conv, medium, scale all ~0.8).
  No single input gets to parity alone — the most helpful lever's optimistic end is still R ≈ 1.5.
- **By realised contribution to the band, reactor scale-up (13%) and conventional price (10%) lead.**
  Medium price and cell efficiency have *large potential* but *small realised* contribution —
  because we center them on the measured values, so they are upside, not expected movement.

So the lever the industry most touts — **medium price — has a big potential effect but contributes
~0% to the expected spread**, while **scale-up is the biggest realised driver, the least
demonstrated, and carries the largest downside:**

| Pasitka reactor config (Fig. 4) | biomass COGS | R | reading |
|---|---|---|---|
| large-scale perfusion 20 m³ | $22/kg | 2.25 | scale-up succeeds (their headline target) |
| TFF 5 m³ (10×5,000 L) | $24/kg | 2.42 | demonstrated-scalable base (the central case) |
| ATF 0.5 m³ (many small vessels) | **$38.8/kg** | 3.65 | **scale-up stalls — the downside** |

The irreducible **floor is ~$7.5/kg** (amino acids $0.5 + glucose $1 + minimal plant overhead $6),
sitting right at the parity threshold — reachable in principle, but only if the optimistic end of
every lever lands together. Pasitka's continuous run was at **1.8 L**; pilot hardware at 300 L;
scalability *claimed* to 5,000 L — the cheap projections assume reactor volumes nobody has built.

## 2. Where the price ratio lands (Output 1)

```
basic product vs commodity meat ($12/kg), Monte Carlo over the cost inputs:
  price ratio R:   P50 = 1.93   80% CI [1.54, 2.35]   90% CI [1.45, 2.47]
  long-run share:  P50 = 11.6%  80% CI [4.1, 25.7]
  0% of draws reach parity (R ≤ 1)
```

The basic commodity product most likely sits **about 2× a conventional price**, consistent with
Pasitka's own published projections (R ≈ 2.25–2.42); the band's optimistic tail (cheap medium + CHO
cells + large reactors all landing) approaches but does not cross parity. The medium-cost
breakthrough is real and moves R from ~2.4 toward ~1.6; the remaining gap is **scale-up and plant
overhead** — the parts least demonstrated and the parts that do not fall with medium chemistry.

## 3. The two gates (what decides ~1% vs tens-of-percent)

**Gate 1 — cost (dominates).** Because the achievable R for the basic product most likely sits above
parity, gate 1 alone yields the low-share world for most of the distribution.

**Gate 2 — acceptance.** *At parity*, cultivated's standing is **two meaningful dials** that span the
whole believable range — the widest lever on the at-parity
outcome. `accept_x` (taste-acceptance: is cultivated credited as real meat?) carries the
**friction**; `theta_free_M` (does the mainstream value no-slaughter / cleaner meat?) carries the
**upside**. We take no stance:

| dial | cultivated share | reading |
|---|---|---|
| taste-acceptance `accept_x` = 0.6 | ~12% | strong taste friction (not credited as real meat) |
| `accept_x` = 0.8 | ~27% | modest friction |
| **`accept_x` = 1.0, `theta_free_M` = 0** | **~50%** | equivalent real meat + mild health edge (neutral default) |
| &nbsp;&nbsp;↳ *no health edge* (`health_x` = `health_c`) | *~47%* | *cultivated exactly equivalent to conventional* |
| slaughter-free value `theta_free_M` = 0.5 | ~60% | mainstream starts valuing no-slaughter |
| `theta_free_M` = 1.0 | ~69% | mainstream values no-slaughter |

(Away from parity — at the likely R ≈ 2 — price and elasticity dominate instead: the share tornado
there is led by the cost→R levers (efficiency, medium price) and `eps_own`, the acceptance dials second.) The tens-of-percent world needs
cost at parity **and** (real-meat acceptance **or** a clean-meat preference). *Demand calibration
holds (self-checks):* with cultivated absent the model reproduces plant-based's real ~1.2%, carried
~89% by the **mainstream** (flexitarians), matching the GFI buyer data; at parity a new cultivated
product draws **−45 pp from conventional** vs only −0.6 pp from plant-based — the no-nest IIA proof,
driven by the shared `real_tissue` attribute. Two notable findings: (i) the **ethical segment is only a
cultivated adopter at parity (~20%) but falls off sharply with any premium** (~9% at R=1.6) — the same cheap whole-food option that keeps
ethical plant-based low also means ethical buyers won't pay a big cultivated *premium* (beans
out-compete it); (ii) a cross-category check reproduces **plant-based milk's ~15%** from the same shared
coefficients and milk-appropriate positions, milk winning only because it reached price+taste parity in
use (coffee/cereal) and has no cheap substitute — meat did neither. The model predicts the ordering
**cultivated ≈ conventional ≫ plant-based at parity** (cultivated escapes the not-real penalty, being
real tissue) as a *structural prediction*; cultivated's slight edge over conventional is a deliberate,
removable **health** assumption (a mild −0.1 conventional health position — strip it and the two sit
level at ~47%, see the no-edge row above), not the load-bearing result. General-population
plant-based-at-parity ≈ 10% (we pin to the GFI buyer split, **not** to the UCLA ~26% dining-hall figure). **Same functional form for every
option:** price (BLP `ln(income−price)`), a **two-sided reference-dependent loss-aversion** term in the
canonical form (`−λ·max(0,price_ratio−1) + 1·max(0,1−price_ratio)` — penalises a premium at slope −λ,
rewards a discount at the unit rate, so λ itself is the loss/gain asymmetry; applied to plant-based and
cultivated alike — no cultivated-only "parity cliff"), taste, slaughter-free, real-tissue, and **health**
(a per-product position × a segment-specific weight — the whole-food health premium that replaces the old
free outside-option constant, so there is now no free fitted constant). **Habit** is not a separate fitted parameter (not
identified from heterogeneity without panel data — Heckman); it lives in the diffusion dynamics (§timing)
and the long-run acceptance dials (`accept_x`, `theta_free_M`); launch food-neophobia is a transient that fades to 0. **Convenience** (the third PTC factor) is proxied by rollout, not modelled
separately.

*Robustness & scope (self-check [6]).* These demand parameters are **calibrated to moments, not estimated**
(no large cultivated-meat scanner panel exists), so Output 2 is a band. Re-solving the calibration as each
judgement anchor sweeps its range, the central share at the likely R≈2.4 (~8.2%) moves most with
**`cult_sub_mult`** (the substitutability lever, 3.3→12.7% over κ=3–6); **loss aversion** — formerly the top
lever — now barely moves it (the elasticity double-counting fix removed its hidden price-sensitivity, leaving
it to shape only the parity kink), as do the plant-based-fitting internals — so the answer turns on two
*behavioural-price* judgement calls, which we surface rather than bury. κ is the softest, but **not
ungrounded**: the one choice experiment that varied cultivated's own price across six levels (Van Loo, Caputo
& Lusk 2020) brackets its at-parity own-price elasticity at **−0.84 to −3.4**, and the model's implied
at-parity (cold) elasticity at κ=4 is **−1.5 — inside that bracket** (self-check [4b], golden-guarded). What
the data *cannot* pin is the elasticity at the R≈2.4 premium where κ actually bites (no DCE has priced
cultivated that far above parity), so the −3.6 there is a functional-form extrapolation from the at-parity
measurement — the honest residual on this lever. This is a **partial-equilibrium** model (prices exogenous, no
supply response), a **two-class** (not continuous random-coefficients) logit, with a single calibrated price
coefficient — the right simplifications given the sparse data; an estimated random-coefficients system would
be false rigor here.

## 4. Penetration by type of meat — price and demand run opposite (Output 2)

Cultivated cost is ~constant; conventional price is not — so R and share differ sharply by meat type
(`penetration_by_type_*`). Premium is now defined **per species** (a structured product ≥ 2.5× its
species' everyday form: wagyu beef, sushi seafood, organic chicken, heritage pork). At the cost
floor, neutral dials, US:

```
  meat type                $/kg  vol%    R    cult share   tier
  chicken (ground)            5   20%  2.50     15.2%      basic
  chicken (cuts)              9   20%  2.06     13.2%      cut
  chicken (organic)          13   ~1%  1.42     11.7%      premium <- above parity, demand-capped low
  beef (ground)              11   13%  1.14     48.4%      basic   <- reachable (near parity), top share
  beef (steak/cuts)          20   10%  0.93     42.0%      cut     <- sweet spot
  beef (prime/wagyu)         45   ~0%  0.41     36.8%      premium <- very cheap (R=0.41) yet held BELOW the cuts
  pork (processed)            8   12%  1.56     34.7%      basic
  pork (cuts)                12    8%  1.54     22.3%      cut
  pork (heritage)            20   ~0%  0.93     19.4%      premium
  turkey (ground/proc.)       5    3%  2.50     15.2%      basic
  turkey (breast/cuts)        9    3%  2.06     13.2%      cut
  seafood (mince/canned)     10    2%  1.25     44.4%      basic
  seafood (fillet)           24    4%  0.77     49.6%      cut     <- sweet spot (top cut)
  seafood (sushi)            40    2%  0.46     34.0%      premium <- very cheap (R=0.46) yet held below the cuts
  rabbit (cuts)              16   ~0%  1.16     33.0%      cut
  TOTAL — by VOLUME (impact) 27.4%  |  by VALUE ($ market) 31.8%
```

**No easy entry point:** cheap mince is unreachable on price (R ≫ 1); ultra-premium (wagyu R = 0.41,
sushi R = 0.46) is *price-cheap* but **demand-resistant** — the authenticity penalty and low price-elasticity
hold it well below what its deep discount would otherwise buy. A basic product at R = 0.41 would take ~86%;
wagyu, with the same price, takes only ~37% — the authenticity cap is doing real work, just not flattening
it to nothing. **The reachable window is the near-parity basics and structured cuts — beef ground (~48%,
near parity), salmon fillet (~50%), beef steak (~42%)** — where price is reachable and the demand penalty is
moderate; these out-draw the discounted-but-resistant ultra-premium. Cultivated is cheapest exactly where
demand resists most, and most accepted where it is hardest to beat on price — so the near-parity cuts are the
robust entry window.

## 5. Total penetration, by region (Output 2 headline)

Rolling up across the spectrum, sampling cost + acceptance dials + elasticity, **at each region's local
meat prices and income** (`report_regional_band`):

```
total cultivated penetration of meat (N=30,000), 80% CI [P10, P90]:
  region   income/cap   by VOLUME (impact)        by VALUE ($ market)
  Europe    $62k        P50  9.6%  [3.3, 20.8]    P50 14.6%  [ 5.2, 29.4]  <- easiest (rich + priciest meat)
  US        $86k        P50  5.6%  [1.7, 14.3]    P50  8.2%  [ 2.7, 19.2]
  global    $24k        P50  3.9%  [1.0, 11.1]    P50  6.6%  [ 2.0, 16.7]
  China     $27k        P50  3.1%  [0.9,  8.3]    P50  6.3%  [ 2.1, 14.8]
  Brazil    $22k        P50  1.2%  [0.3,  4.8]    P50  2.1%  [ 0.6,  7.2]
  India     $11k        P50  0.5%  [0.1,  1.7]    P50  1.3%  [ 0.4,  3.5]
  Nigeria    $6k        P50  0.3%  [0.1,  2.2]    P50  0.5%  [ 0.1,  2.8]  <- hardest (cheap meat + price-sensitive)
```

Two forces set the ordering, and they **compound**: (1) *local meat price* — Europe's expensive meat
puts parity nearest; (2) *income* — through a genuine **Berry–Levinsohn–Pakes** price term `α·ln(y_eff − price)`:
a given price is a bigger bite the poorer the consumer, so richer consumers are less price-sensitive. The
effective income is damped, `y_eff = income_ref·(income/income_ref)^0.5`, so the rich-poor own-price-elasticity
ratio matches the empirical ~2× (Muhammad/ERS) rather than raw BLP's over-steep ~6×. **Europe is easiest**
(rich *and* priciest meat). **Low-income regions are hardest** — India, Brazil and Nigeria have *cheap* meat
(R far above 1) *and* high price-sensitivity, so cultivated barely registers (sub-1% at today's cost). That is
the most consequential thing the income channel surfaces, since those regions hold much of the world's future
meat demand. (Low-income local meat prices/mixes are rough, illustrative.) Bands are wide and right-skewed:
low end = scale-up-stalls / friction; long tail = scale-up-wins / preferred.

> *Methodological note (2026-06-12).* The income channel is **genuine Berry–Levinsohn–Pakes**: income enters
> inside the log (`α·ln(y_eff − price)`, a single constant `α`), so the diminishing-marginal-utility-of-income
> curvature is the mechanism, with a damping exponent `φ` that reconciles raw BLP (too steep for food, ~6×)
> with the empirical ~2× food-elasticity gradient. (An earlier draft froze income inside the log and re-added
> it as a separate multiplier — that was not BLP and disabled the curvature; this restores it, verified against
> its own linearisation to <0.01pp at meat prices.) Each meat type's absolute price uses its own conventional
> price (chicken vs chicken, steak vs steak), not a single commodity price. Separately, the demand model's
> default is now a **symmetric** price response (no loss-aversion
> kink): the asymmetry was near-inert on the headline, not identifiable from the available data, and —
> per Bell & Lattin (2000) — apt to be confounded with the price-response heterogeneity that `κ` already
> carries. Loss aversion remains an off-by-default exploratory dial.

One place parity is reachable today: **structured product vs premium seafood.** Vs sushi salmon
($40/kg), R P50 = 0.82 and 90% of draws are at/below parity — but here the lone new unknown,
**scaffold process cost** (no TEA), is the top spread driver (~19%), and premium demand is hostile.

## 6. What a technical funder should prioritise

The model points the marginal R&D dollar at the **binding** constraint, not the most visible one:

1. **Reactor scale-up is the binding cost lever** (biggest realised driver, least demonstrated,
   largest downside): demonstrating large-volume animal-cell perfusion (CO₂/O₂ transfer, shear,
   sterility at scale) beats further medium-chemistry wins. The cheap projections assume reactors
   nobody has built.
2. **Plant overhead at scale** (the largest floor term) sets where the floor lands vs parity — fund
   independent, at-scale facility-cost data (the GFI 2026 report flags this as the field's data gap).
3. **Medium price is a *potential* lever but already a company-claimed success** — verify the
   sub-$0.20/L claims rather than re-fund them; centered on the measured $0.63 it is upside, not the
   expected path.
4. **`p_conv` is a policy lever:** a meat tax moves R toward parity as much as a major cost win, and
   it is exogenously controllable.
5. **Scaffold process cost** is the single biggest *unmeasured* number and gates the premium-seafood
   path — a scaffolding TEA is the literature's clearest hole.

**Bottom line:** the medium-cost breakthrough is real but does not, by itself, reach parity. The gap
to parity is **scale-up and plant overhead** — physical, least-demonstrated, least likely to fall
with more bench chemistry. That is where philanthropic, public-goods-shaped money plausibly moves
the trajectory.

---

### Figures (curated set — `python report_figures.py`; diagnostics in `figures/diagnostics/`)
1. `cost_vs_inputs` — the two big cost levers (medium price × reactor scale) and the floor.
2. `cost_waterfall` — where the cost goes; scale-up is the biggest single step.
3. `sensitivity_tornado_share` — which knobs move the final share most (eps_own + cost levers at the
   likely R; the acceptance dials at parity).
4. `share_vs_ratio` — the share a given price ratio buys (the willingness-to-pay demand curve).
4b. `pb_milk_vs_meat` — the cross-category validation **depicted**: plant-based MILK vs MEAT, the same
   machinery with swapped product positions → ~15% vs ~1% (milk wins on price + taste parity and no cheap rival).
5. `cost_paths_timing` — penetration over 30 years by cost-milestone path (the cost→time coupling).
6–9. `penetration_by_type_{us,eu,china,global}` — share **by type of meat** (price vs demand oppose).
10. `report_regional_band` — total penetration band by region (volume & value).
