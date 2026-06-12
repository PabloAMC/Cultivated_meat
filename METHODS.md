# Cultivated meat model — methods

*This is the methodology reference: the mechanisms, the equations, and every parameter with its
source. For the findings, see [RESULTS.md](RESULTS.md). The model is built one mechanism per rung;
every concrete number lives once in [`inputs.py`](inputs.py) (run `python inputs.py` to print the
datasheet), and the cost equation exists once (`uncertainty.R_from_inputs`) shared by every rung.*

## Design rules

1. **Every rung runs and produces a figure.** No rung is a sketch.
2. **No rung introduces a model a later rung deletes.** A rung that needs a number it cannot yet
   produce takes it as an *input* rather than faking a mechanism.
3. **Every number is sourced in `inputs.py`** with a provenance tag and (where uncertain) a
   Monte-Carlo prior, so the point estimate and the uncertainty band can never drift apart.

## Keeping code, JS, and prose in sync — the anti-drift checklist

The model exists in three coupled forms — the Python source of truth, the hand-ported JS in
`interactive.html`, and the methodology *prose* (equations + quoted numbers). Divergence between them
is the model's biggest maintenance risk. Three layers, three guards; the first two are automated, the
third is a discipline because no test can verify that English correctly describes an equation.

**Layer 1 — Python ↔ JS code.** *Fully automated.* `tests/run_parity.py` runs the embedded JS under
Node and asserts it matches the Python model to ~1e-12 over a 2000-point grid (price × both acceptance
dials × elasticity × income), plus the calibration solve, the milk check, and the timing rung. **Rule:
after ANY change to a Python model function, re-run `build_interactive.py` (which re-ports the JS) and
`run_tests.sh` before committing.** Never hand-edit the JS in `interactive.html` — it is generated.

**Layer 2 — code ↔ numbers quoted in prose.** *Automated, two mechanisms.* (a) Every illustrative
**share %** in the prose/tooltips is a `{{TOKEN}}` computed in `build_interactive.illustrative_numbers()`
and substituted at build time — never hand-typed; `check_illustrative_numbers_in_html` enforces that
every token is computed and every computed value is used. (b) Every model-**derived non-share figure**
(an elasticity, the cost floor, `eps_own×κ`) is pinned in `tests/test_golden.check_derived_prose_numbers`,
which re-derives it from the live model and asserts the rounded figure appears in the page. **Rule: when
you quote a new model-derived number in the prose, either route it through a `{{TOKEN}}` (if it is a
share %) or add it to `check_derived_prose_numbers` (otherwise). Do not hand-type a derived number with
no guard** — that is exactly how the stale `−0.95` elasticity slipped in. *External-data* constants (the
Lusk `[−3.4,−0.84]` bracket, the `+0.2/−0.4/−1.5` tier offsets, DOIs) are sourced, not derived, so they
are guarded by review, not by these tests — keep them out of the derived-number guard.

**Layer 3 — code ↔ equations/words in prose.** *Manual — no test can check prose English.* When you
change a model **equation or its structure**, walk this list:
- **Single-source every constant.** A number must live once, in `inputs.py` (or as a derived quantity).
  If you find yourself typing a value into prose, ask whether it should be a `{{TOKEN}}` or a guarded
  derived number instead.
- **If you change a slope, coefficient, or sign**, grep the methodology block in `build_interactive.py`
  (`<details class="methods">`) for every place that *describes* it, not just the equation that defines
  it. The stale `λ/2.25` kink lived in §5 prose long after the λ default changed in §2.
- **If you add or remove a term/equation in the code**, add or remove it in the methodology section
  too (the cost floor and value-weight roll-up were in the code but missing from the prose).
- **Keep the four files aligned**: `inputs.py` (datasheet), `build_interactive.py` (prose + JS),
  `METHODS.md` and `RESULTS.md` (write-ups). A figure quoted in more than one of these is a drift
  candidate — prefer pointing to the single source over re-quoting.
- **Always finish with `./run_tests.sh`**, which rebuilds the page and runs all four checks. Green means
  Layers 1–2 hold; Layer 3 is on you to have walked.

## Sourcing discipline (Pasitka-anchored)

The cost stack is anchored to **Pasitka et al. 2024** (*Nature Food*) — the one *empirical* TEA —
throughout. The **scale-up risk is expressed inside Pasitka's own three reactor configurations**
(their Fig. 4), *not* via Humbird's headline $37/$51. **Humbird 2021** supplies only (a) the
physical amino-acid feedstock floor and (b) the *rationale* for why scale-up is hard (CO₂/O₂
transfer, shear, sterility caps on vessel size) — never a load-bearing cost number. Company claims
(e.g. sub-$0.20/L medium) are tagged **[GFI26]** and treated as *self-reports*, weak directional
evidence, after the GFI 2026 State-of-the-Industry report's own caveat that they are not
independently verified.

## No free knobs — the provenance audit

Every number is forced into one of five categories; none is a free constant left to taste. Run
`python inputs.py` for the datasheet that tags each one.

1. **Sourced** — taken from a citation: `p_conv`, `media_intensity`, `media_price`, `overhead` (Pasitka
   Fig. 4), `aa_intensity`/`aa_bulk_price` (Humbird), `eps_own` (scanner meta-analyses), `price_pb_mult`
   (GFI/NIQ), `taste_quality_p` (Nectar), `w_eth` (Gallup), `pb_mainstream_frac`/`pb_share_target`
   (GFI/SPINS), `income_*` (World Bank, Muhammad/ERS), `price_wf_mult` (BLS), and the Bass `p_innov`/`q_imit`
   (literature). (`loss_aversion` is now an off-by-default dial, λ=1; see the reference-term note below.)
2. **Derived** — computed from other quantities, never typed: the price coefficient `β` (solved at
   cultivated's own modeled price & share — the `price_calib` fix), the parity threshold (`p_conv −
   markup_add`), the cost floor, and the cost-path `R` endpoints (from the cost model).
3. **Solved to a moment** — pinned by one equation to one published datum: `w_realtissue_M`,
   `w_health_M/E` (the 89% buyer split, the 1.2% PB share, the meatless rate). Calibration, not fitting.
4. **Judgement, but swept** — the few genuine judgement calls are *never* presented as a point; their
   leverage is shown explicitly. `cult_sub_mult` and `loss_aversion` (the two behavioural-price levers,
   self-check [6]); the acceptance dials `accept_x`/`theta_free_M` (Gate 2, always a band);
   `markup_add` (swept 2–7, bounded by the USDA farm-to-retail spread).
5. **Assumed but shown not to matter** — verified non-load-bearing: re-solving the calibration while
   sweeping `q_taste`, `taste_quality_w`, `w_slaughter_E`, `w_realtissue_E`, `wf_mainstream_target` moves
   the cultivated answer **< 0.2 pp** (the calibration solve absorbs them; PB stays pinned at 1.2%). The
   timing-only knobs (`accept_rate`, `neophobia_launch`) set *when*, not the ceiling. `glucose_other_floor` (~$1 of
   the ~$7.5 floor) is the one remaining small pure assumption, and it lives inside the floor *band*.

The single load-bearing **assumption** (not a number) is `real_tissue`: that cultivated, being real
tissue, inherits conventional's standing and escapes the plant-based penalty — stated as the model's
identifying premise, and the structural reason cultivated sits with conventional (far above plant-based)
at parity. The baseline also gives cultivated a **mild health edge** over conventional (`health_c`=−0.1,
`health_x`=0 — no antibiotics/contamination, controlled fat), which lifts it to a slight lead at parity
(~50% vs conventional's ~43%); this is a deliberate, *flaggable* assumption — set `health_x`=−0.1 (no edge)
and cultivated sits just below conventional at the neutral ~47%. We report it openly rather than bury it
(see "an honest health caveat" below).

## The two outputs

- **Output 1 — `R = p_cult / p_conv`** and how close it gets to parity (`R = 1`). Because cultivated
  cost is ~constant across animals while conventional price is not, `R` is computed **per meat type**.
- **Output 2 — the market share** that `R` buys, rolled up across meat types (by volume = impact,
  by value = market). Always a **band**.

**Trust gradient:** Rungs 1–2 (and the sensitivity rung) are the high-trust half — a TEA-grounded
cost projection over a known market price. Rungs 3–4 are the softer half — a best-guess share off
transplanted meat elasticities. Lead with Output 1; present Output 2 as a band.

## The ladder

| Rung | File | Adds |
|---|---|---|
| 1. Price ratio | `price_ratio.py` | `R` and the parity-cost **threshold** (additive markup). No cost mechanism. |
| 2. Cost + scale-up | `cost_model.py` | Pasitka component cost; the **scale-up bottleneck** (overhead across 3 reactor configs); the irreducible floor; the cost **waterfall**. |
| 3. Demand → share | `market_share.py` | two-segment, four-product discrete-choice model (conventional / plant-based / cultivated / whole-food), calibrated to plant-based's real ~1%. |
| 4. Timing | `adoption_timing.py` | rollout (Bass) + growing acceptance, driven by discrete **cost-milestone paths** over 30 yr. |
| 5. Uncertainty | `uncertainty.py` | Monte Carlo over the priors → distribution of `R` and share. |
| **S. Sensitivity** | `sensitivity.py` | **tornado + key-knobs table: which inputs move `R` and share most.** |
| 6. Scaffolding | `scaffolding.py` | structured-product cost vs a premium target (Wildtype/BlueNalu). |
| 7. Meat market | `meat_market.py` | share across the meat spectrum; volume/value roll-up; price vs demand oppose. |

Two shared modules sit beneath: `inputs.py` (the datasheet) and `common.py` (plotting plumbing).

---

## Rung 1 — the price ratio (`price_ratio.py`)

```
p_cult = biomass_cost + markup_add        (ADDITIVE markup)
R      = p_cult / p_conv
parity (R=1)  ⟺  biomass_cost ≤ p_conv − markup_add     ← the THRESHOLD
```

The markup is **additive** (fixed $/kg: processing, cold-chain, retail margin do *not* shrink as
biomass gets cheaper). A multiplicative markup would let the retail wedge vanish at low cost and
make parity look easy. Because it is a fixed addend, parity has a hard cost threshold set by just
two numbers — `markup_add` ($5/kg) and `p_conv` ($12/kg) → **biomass ≤ $7/kg for parity.** These two
are the most leverage-heavy inputs in the model (`p_conv` is also where a meat tax enters). The
`markup_add` prior floors at **$2** (below conventional's ~$4): cultivated skips slaughter / evisceration
/ carcass breakdown, a real slice of the farm-to-retail wedge, so its retail markup can sit slightly
below conventional's — at that floor the parity threshold rises to ~$10/kg biomass.

## Rung 2 — the cost model, the scale-up bottleneck, and the floor (`cost_model.py`)

```
biomass_cost = media_cost + overhead
media_cost   = media_intensity[L/kg] × efficiency × media_price[$/L]
```

**Anchors (Pasitka):** `media_intensity` = 22.4 L/kg (24×10⁶ L → 1.07×10⁶ kg/yr at the projected
50,000 L facility); `media_price` = $0.63/L (empirical ACF medium, down from $3.31/L — albumin
removal was the big cut); `efficiency` = 1.0 (Pasitka cells; 0.25 = "CHO-grade", ~4× less media).
The base case reproduces Pasitka's published **$24/kg** wet-biomass COGS.

### The scale-up bottleneck (`overhead`, the model's single biggest cost lever)

Pasitka reports *no* empirical $/kg; their COGS are **modelled** for a 50,000 L facility at three
reactor configs (Fig. 4). Non-media overhead **falls with reactor scale** because consumables and
filters dominate the small-vessel case:

| config | overhead | total COGS | R |
|---|---|---|---|
| ATF 0.5 m³ (many small vessels) — scale-up **stalls** | $24.7/kg | $38.8/kg | 3.65 |
| TFF 5 m³ (10×5,000 L) — current base | $9.9/kg | $24/kg | 2.42 |
| perfusion 20 m³ — scale-up **wins** | $7.9/kg | $22/kg | 2.25 |

So the `overhead` prior is **the scale-up knob**, sampled triangular **lo=6.0 (irreducible plant
floor, optimistic tail) / mode=9.9 (TFF, the demonstrated-scalable base) / hi=15.0 (scale-up proves
harder than the clean projection)**. The central band is *centered on the demonstrated config* so the
median is neutral, not pessimistic. The full scale-up-**stall** case (ATF, ~$24.7/kg overhead,
$38.8/kg total) is carried as an explicit **downside scenario** (the cost scenario table and the
waterfall), not folded into the central band — a commercial plant only falls back to many small
vessels if larger reactors fail (Humbird's CO₂/sterility argument), so it is a tail, not the centre.
Pasitka's empirical continuous run was at **1.8 L**; pilot hardware at 300 L; claimed scalability to 5,000 L —
the cheap projections assume reactor volumes nobody has demonstrated.

### The irreducible floor (`cost_floor`)

What remains after every *reducible* part (recombinant albumin/growth factors, single-use filters,
small-scale capital) is engineered toward zero — what the cells must physically eat plus the minimal
cost of running a plant:

| component | value | basis |
|---|---|---|
| amino acids | ~$0.5/kg | 0.26 kg/kg wet × $2/kg bulk hydrolysate **[Humbird Table 3.4]**. Comparable to chicken feed cost — *no* order-of-magnitude feedstock advantage. |
| glucose + other bulk nutrients | ~$1/kg | irreducible energy/building blocks [assumed] |
| running a plant | ~$6/kg | minimal plant overhead at scale **[Pasitka]** (nutrients ~66–70% of perfusion COGS → non-nutrient remainder ~$6/kg). The least-constrained term; dominates the floor's width. |
| **= floor** | **~$7.5/kg** (band $7–10) | → R ≈ 1.04 |

The floor sits **right at the parity threshold ($7/kg)** — so parity on a basic product is, at best,
marginal, *and* it assumes the scale-up ceilings are engineered away. If they are not, the floor is
unreachable at any media price. The **cost waterfall** (`cost_waterfall.png`) walks ATF → scale-up →
cheaper media → cell efficiency → floor, making the bottleneck and the irreducible floor visual.

## Rung 3 — demand → share (`market_share.py`)

A **two-segment, five-attribute discrete-choice (latent-class logit) model.** Consumers choose among
**four products** — conventional meat `c`, plant-based meat `p`, cultivated `x`, and a **whole-food /
non-meat outside option** `w` (beans/tofu/lentils) — each carrying five attributes: price-ratio,
taste_quality, slaughter_free (0/1), real_tissue (0/1), and **health** (a position per product). Two
latent **segments** mix by population weight: mainstream `M` (taste/price-driven, weights real_tissue)
and ethical `E` (weights slaughter_free and health, ~5% = Gallup veg+vegan). Each segment is a **flat**
multinomial logit:

```
V_sj = V_price(price_j, income)                                             # income-scaled price term
       + f·[ −λ·max(0, price_ratio_j − 1) + 1·max(0, 1 − price_ratio_j) ]   # reference term (λ=1 ⇒ symmetric)
       + q_taste·taste_j + w_slaughter[s]·slaughter_j
       + w_realtissue[s]·real_tissue_j + w_health[s]·health_j + ξ_j[s]
P_sj = softmax_j(V_sj)
share_j = w_eth·P_E(j) + (1 − w_eth)·P_M(j)
# EVERY product uses this same rule (a products×attributes table · segment×weights). Income enters
# the BLP price term V_price = α·ln(y_eff − price), y_eff = income_ref·(income/income_ref)^φ (§across-
# regions). The reference term is SYMMETRIC by default (λ=1 ⇒ no kink, no loss aversion); λ>1 turns the asymmetry
# on as an exploratory dial. The constant ξ_j = ν_j + τ_j (novelty + cultivated authenticity) is 0 for
# every product at baseline — there is NO free fitted constant anywhere, including the outside option,
# whose standing is now its health attribute (see Calibration).
# No cultivated-only term: the reference term applies to plant-based (1.77×) and cultivated (R) alike.
```

This structure makes **plant-based a genuine competing
product** (its own price premium, taste, slaughter-free position) and **ethical demand a distinct
high-WTP segment** that can adopt above parity (`R>1`), as the user requested.

**Why a FLAT logit reproduces "cultivated cannibalises CONVENTIONAL, not the veggie burger" without a
nest (the IIA fix).** A single logit obeys IIA (a new option steals proportionally). We do not add a
nest. Instead the result emerges from **preference heterogeneity + the shared `real_tissue`
attribute**: real_tissue makes conventional own almost the entire (large) mainstream segment, so a
proportional reduction there comes overwhelmingly out of *conventional* in absolute terms; plant-based
and whole-food barely register in the mainstream and are hardly touched. The ethical segment (~5%) is
where cultivated also draws from plant-based/whole-food. `real_tissue` is the **minimal extra
structure** (one shared characteristic) that does the job the retired real-meat nest did — and it is
exactly what cultivated SHARES with conventional, the structural reason cultivated can succeed where
plant-based stalled. A milder claim than a nest; the [3] self-check verifies it numerically.

**Price, from first principles (for the non-economist).** This is the one place a reader without
microeconomics can feel a coefficient is "out of the blue," so here is the whole chain, with every number
either sourced or *derived from* the model rather than typed in:

1. *Utility and the price term.* Each product gets a utility score `V_j`; shares are `softmax(V)` (the
   logit). Price lowers utility. The naïve form is `β·price_j`, where `β<0` is the **marginal utility of a
   dollar** — how much one more dollar of price hurts.

2. *Why richer buyers care less (the price form).* A dollar matters less to a rich household, so instead of a
   flat `β·price` we use the **Berry–Levinsohn–Pakes (1995)** log curvature `V_price = α·ln(y_eff − price_j)`,
   with income entering inside the log via the (damped) effective income `y_eff = income_ref·(income/income_ref)^φ`
   (poorer = more price-sensitive; see point 6). Locally this still behaves like `β·price` at the reference income
   (its slope at the anchor is exactly `β`), so steps 3–4 pin a single number, `β`, and the log curvature tilts
   it correctly across incomes.

3. *We do not guess `β` — we pin it to a measured elasticity.* In any logit, the own-price elasticity of a
   product is an identity, **`elasticity_j = β · price_j · (1 − share_j)`**. Rearranged, `β` is whatever
   reproduces a *target elasticity* at a given price and share. So calibrating `β` reduces to: "what is
   cultivated's own-price elasticity, and at what price/share?"

4. *The target elasticity (sourced).* Meat's measured own-price elasticity is `eps_own = −0.9` (scanner
   meta-analyses; Andreyeva 2010, Gallet 2010/12). Cultivated's own price should bite **harder** than the
   meat *category's*, because conventional meat is a near-perfect substitute for it (a category has no close
   substitute and is therefore inelastic; a single product inside it is not). We multiply by
   `cult_sub_mult ≈ 4` → target **`eps_x = eps_own·cult_sub_mult = −3.6`** (κ is applied **once** — it
   defines the target; `β` below merely delivers it). κ is the model's softest demand lever, so it is
   **swept 3–6** and is one of the two levers self-check [6] reports. **It is, however, bracketed by the one
   direct measurement.** Van Loo, Caputo & Lusk (2020, *Food Policy* 95:101931) priced lab-grown meat across
   six levels ($2.99–$10.49/lb) in a US choice experiment, identifying its **own-price elasticity at parity**;
   their two models bracket it at **−0.84** (conditional logit, the average consumer) to **−3.4** (random-
   parameter logit, whose steepness comes from preference heterogeneity — lab-grown's random-coefficient SD
   exceeds its mean, i.e. ~half the population is positive on it, half negative). κ is precisely the flat-logit
   stand-in for that heterogeneity, so the model's **implied at-parity (cold) elasticity must land inside
   [−3.4, −0.84]** — and at κ=4 it does (**−1.5**), reported by self-check **[4b]** and guarded as a golden
   value. *The residual caveat (a functional-form limit, not a κ one):* Lusk measures the elasticity **at
   parity**, but the realized target −3.6 is at cultivated's **operating point R≈2.4**, where the BLP+kink
   form is steeper. So the data ground the **shape near parity**; the −3.6 at R≈2.4 is an **extrapolation** —
   no choice experiment has priced cultivated at ~2.4× conventional. (See limitations.)

5. *The anchor is derived, not invented — and the calibration counts BOTH price channels.* Price enters the
   utility through two terms: the BLP income term (local slope `β`) **and** the loss-aversion term (slope
   `−loss_aversion/p_conv` on the loss side, where cultivated's premium sits). So the realized own-price
   elasticity is `eps_x = (β − loss_aversion/p_conv)·p_anchor·(1 − share)`, and we solve `β` so this **total**
   response hits the target at cultivated's **own** operating point: price `p_anchor = biomass_cost +
   markup_add` (the cost rung's output — change `overhead`, `media_price`, `markup_add` or `p_conv` and it
   moves), share = cultivated's own modeled share there — a short **fixed point** (`market_share._derive_beta`,
   ~3 steps). Then `β = eps_x / (p_anchor·(1 − share)) + loss_aversion/p_conv`. **Nothing here is a free
   constant** (no hand-set "anchor price"). Adding back the `loss_aversion/p_conv` term is the **double-counting
   fix**: an earlier version omitted it, so the *realized* elasticity came out ≈ −5 — far steeper than the −3.6 target — and
   `loss_aversion` silently doubled as a second price-sensitivity lever. Now the realized cultivated elasticity
   is the target **−3.6** at today's price and eases toward ≈ −1 near parity (both sane). At the default λ=1
   the reference term is symmetric (its unit slope is just part of the total price response β absorbs); when λ
   is turned up it shapes only the **kink** at parity — either way `cult_sub_mult` cleanly owns the elasticity
   *level*. (Income enters via the BLP log; see point 6.)

6. *Across regions — genuine Berry–Levinsohn–Pakes.* Income enters **inside the log**:
   `V_price = α·ln(y_eff − price)`, with `α = −β·(income_ref − anchor_price)` a single constant. The
   diminishing-marginal-utility-of-income curvature IS the mechanism — the same price is a larger, more
   painful bite the poorer the consumer, so richer consumers are less price-sensitive with no extra term.
   The cross-region tilt comes only from the **damped effective income** `y_eff = income_ref·(income/income_ref)^φ`
   (φ = `income_gradient`, default **0.5**): raw BLP (φ = 1, y_eff = actual income) is too steep for food
   (~6× rich→poor own-price-elasticity ratio), so φ < 1 damps the curvature to the empirical ~2× gradient
   (Muhammad et al. 2011, USDA ERS); φ = 0 removes income. At the US reference `y_eff = income_ref`, so the
   US and every at-parity number are invariant to φ. **Correction (2026-06-12):** an earlier form froze income
   inside the log and re-added it as a separate multiplier `f = (income_ref/income)^φ` — that was *not* BLP and
   disabled the curvature; this restores genuine BLP (verified against its own first-order linearisation to
   <0.01pp at meat prices, where price ≪ income). Each meat type's absolute price uses its own conventional
   price `p_ref` (chicken vs chicken, steak vs steak), not a single commodity price; only cultivated's price
   varies via R, so only its R-response is an observable output.

**Reference-dependent price term (two-sided, uniform across products; asymmetry OFF by default).** A
second price-related term in the form `−λ·max(0, price_ratio_j − 1) + 1·max(0, 1 − price_ratio_j)`:
consumers compare each product to the conventional price, so a product priced *above* it takes a penalty
at slope −λ and one priced *below* it earns a discount reward at the **unit** rate, with λ the loss/gain
asymmetry. **The default is λ = 1, which makes this term symmetric** — it collapses to a smooth linear
`(1 − price_ratio_j)` with **no kink and no loss aversion** — folded into the (income-scaled) price
response. We default to λ = 1 deliberately: (i) λ is **near-inert on the headline** anyway (the β-derivation
absorbs its slope, so it only reshapes the parity kink, not the elasticity level); (ii) the asymmetry is
**not identifiable** from the available cultivated-meat data; and (iii) per **Bell & Lattin (2000)**
(*Marketing Science* 19:185) estimated loss aversion in aggregate choice data is largely *confounded with
unmodelled price-response heterogeneity* — which this model already carries in `κ` (the real-tissue
random-coefficient stand-in), so a separate asymmetric kink would risk double-counting it. Setting λ > 1
(toward the Tversky–Kahneman 1992 median ~2.25) turns the asymmetry back on as an **exploratory dial**;
it applies to **every** product by its own `d_j = price_ratio_j − 1` (plant-based at 1.77×, cultivated at
R), never a cultivated-only "parity cliff". *On reference points:* the comparison is **contextual** (the
competitor's current price, a cross-sectional gap that does **not** fade), distinct from a **temporal**
reference anchored to a product's own price history (which adapts and is transient — that time-varying
effect lives in the neophobia fade, not here).

**Calibration — a demographic-conditional, reduced-form standing.** Plant-based's position is pinned
from data: price premium `price_pb_mult`=1.77 [GFI/NIQ], taste deficit `taste_quality_p` [Nectar 2025:
only ~16% of PB SKUs reach blind parity], `w_eth`=5% [Gallup], `eps_own` [scanner]. The non-price
standing of non-real-meat products and the outside option are **solved at runtime** from cross-sectional
anchors (three monotone 1-D bisections, `solve_calibration`):
`w_realtissue_M` so the **mainstream carries ~89% of plant-based buyers** (GFI/Morning Consult — most PB
buyers are flexitarians, not the 5% ethical core); the **segment-specific health weights**
`w_health_M`/`w_health_E` (times the whole-food health position, `health_w`=+2 — "beans are the healthy
choice") so the mainstream meatless-by-choice share and the residual ethical PB rate match (total PB ≈
1.2% [GFI/SPINS] by construction). This whole-food **health premium replaces** the old free outside-option
intercept: the model now carries **no free fitted constant** — the outside option's standing is a named
attribute (its health) times a calibrated weight. Splitting the health weight by segment — the
ethical/health-minded weight health heavily, the mainstream much less (the solved `w_health_M` lands at
~0.26× the taste weight, *below* the ~0.5× discrete-choice anchor of Malone & Lusk 2017) — is what lets
`w_realtissue_M` be pinned to the buyer split without the cheap bean option leaking into the mainstream,
and beans are the *ethical* default, a *rare* mainstream choice.

**Is cultivated's "standing" a fitted parameter? No — and the distinction matters.** Two different things
wear the word *standing*, and only one is calibrated:

- **Cultivated's own acceptance dials — `accept_x` (taste-acceptance) and `theta_free_M` (mainstream
  slaughter-free value) — are NOT fitted.** They are **scenario axes
  with a neutral default** (`accept_x=1`, `theta_free_M=0` = cultivated treated as
  *equivalent* to conventional). We never tune them to hit a target; every cultivated headline is reported
  as a **band across them**, and the reader sets them (this is exactly Gate 2). There is no cultivated-meat
  choice data to fit them to — inventing a point value would be the false precision we are avoiding.
- **What IS solved (`w_realtissue_M`, `w_health_M/E`) is pinned to published moments, not free.** These
  are *not* cultivated's standing — they are the *plant-based / whole-food* standings, and each is the
  unique value reproducing a **measured** datum (the 89% flexitarian buyer split [GFI]; the ~1.2% PB share
  [GFI/SPINS]; the mainstream meatless rate). That is *calibration to a moment* — one equation, one unknown,
  the standard discrete-choice practice when you have aggregate moments but no micro-data — not curve-fitting
  with free knobs. (The health weights are weights on a *named attribute*, so even these solved numbers have
  a meaning — the whole-food health premium — rather than being free intercepts.)

So the quantity cultivated's share *depends on* (its standing) is never fitted: it is the dial the reader
turns. What we fit is only the surrounding plant-based world, and only to numbers that are actually observed.
The single load-bearing *assumption* (not a fit) is `real_tissue`: that cultivated, being real tissue,
inherits conventional's standing and escapes the plant-based penalty — stated as the identifying premise.

`w_realtissue_M` is a **reduced-form bundle** (genuine real-tissue preference + processed/habit
residual). We do **not** split it into a separate static *habit* term: in the cross-section habit is not
identified from heterogeneity (Heckman's state-dependence-vs-heterogeneity problem) and we have no panel
data, so an estimated habit constant would be spurious. **Habit instead lives where it is identified:**
the diffusion + neophobia-fading dynamics of Rung 4 (its market-level reduced form) and the long-run
acceptance dials `accept_x`/`theta_free_M` (scenarios, not fitted numbers). `real_tissue` is the **identifying
assumption** that cultivated, being real tissue, *inherits conventional's standing and escapes the
plant-based penalty* — the load-bearing premise, which yields **cultivated ≈ conventional ≫ plant-based
at parity** as a structural *prediction* (not a fitted result); cultivated's slight lead over conventional
is the mild health edge above, removable with one dial. **Convenience** (the third PTC factor;
Bryant/Peacock) is *not* modelled separately — availability is proxied by the Rung-4 rollout — and is
folded into the same reduced-form term; noted as a known omission.

**An honest health caveat (the one place the baseline tilts toward cultivated).** Every other neutral
default treats cultivated as *equivalent* to conventional. The health attribute is the exception: the
baseline gives conventional a mild negative health position (`health_c`=−0.1; red/processed-meat
guidance) while cultivated sits at 0, so cultivated carries a small **+0.1-util health edge** —
defensible (no antibiotics, no faecal contamination, controlled fat are genuine attributes of cultured
tissue) but an *assumption*, and the only one that moves the at-parity headline in cultivated's favour
(~47% → ~50%, enough to put it just past conventional). We surface it three ways rather than bury it:
(i) it is a single exposed position, (ii) the no-edge case (`health_x`=`health_c`) returns the ~47%
"equivalent" headline, and (iii) the mainstream health *weight* is held at ~0.26× the taste weight,
*below* the discrete-choice anchor (Malone & Lusk 2017: health ≈ 0.5× taste), so health is deliberately
a minor lever for the taste-and-price-first mainstream. A skeptic who rejects the edge should read the
~47% figure; the headline does not depend on cultivated being *healthier*, only on it being *real meat*.

**Self-checks (`market_share.py`):** [1] plant-based ≈ 1.2% with cultivated absent, whole-food ≫ PB;
[1b] PB buyer split ≈ 89% mainstream / 11% ethical (GFI), mainstream meatless ≈ 6%; [2] cultivated at
parity spans ~11% (taste friction) → ~74% (strong clean-meat pull) over the acceptance dials; [3] at
parity cultivated draws **−40 pp from conventional** vs −0.5 pp plant-based (the no-nest proof); [3b]
the **ethical segment adopts cultivated at parity (~16%) but falls off sharply with any premium** (~8% at R=1.6) — a *finding*:
the cheap whole-food option that keeps ethical PB low also means ethical consumers won't pay a big
cultivated premium (beans out-compete it); [4] a cross-category **PB-milk validation** — holding the
*same* shared coefficients (`q_taste`, β, income) and swapping only the product positions to
milk-appropriate values yields ~15% (observed ~15%); [5] general-population plant-based-at-parity ≈ 8% — a
structural prediction (we pin to the GFI buyer split, **not** to the UCLA ~26% dining-hall figure, whose sample
likely over-weights ethical/PB-friendly diners); [6] **demand-calibration robustness** — re-solving the
calibration as each judgement anchor sweeps its range. At the likely R≈2.4 the central share (~8.2%) now moves
most with **`cult_sub_mult`** (3.3→12.7% over κ=3–6); **`loss_aversion`** — formerly the top lever — now barely moves it (the
double-counting fix removed its hidden price-sensitivity, leaving it to shape only the parity kink), while the PB-fitting internals
(`w_eth`, `pb_mainstream_frac`, `wf_mainstream_target`) barely move it (~0.1 pp) — so the cultivated answer
turns on two *behavioural-price* judgement calls, not on the plant-based-fitting choices.

**What this model is, and is not (honest scope).** It is a **calibrated, partial-equilibrium discrete-choice
demand model** — standard theory (random-utility logit + latent-class heterogeneity + BLP income +
reference-dependent loss aversion), with parameters *calibrated to moments* (PB share, the 89% buyer split,
meta-analytic elasticities), **not structurally estimated** — because no cultivated-meat choice data exists
(pre-commercial). So Output 2 is a *band/scenario*, never a forecast. Deliberate simplifications, named rather
than faked: (i) **two latent classes**, not a continuous random-coefficients mixture (the segments are
illustrative types, their sizes pinned not estimated); (ii) a **single price coefficient** calibrated to one
(meat own-price) elasticity, not a full substitution matrix — and `cult_sub_mult` is a reduced-form stand-in
for a `real_tissue` random coefficient (the model's least data-disciplined lever, quantified in [6]); (iii)
**no supply side / equilibrium** — prices are exogenous (the cost rung gives them), with no producer response
or pass-through; (iv) **habit** is in the diffusion rung + the neophobia transient, not a separately fitted term
(Heckman). These are the right simplifications for the question and the (absent) data; reaching for an
estimated random-coefficients system here would be false rigor.

## Rung 4 — timing (`adoption_timing.py`)

Two demand processes over 30 years: (1) **market rollout** (Bass diffusion, `p_innov`=0.02,
`q_imit`=0.40) — the product reaching shelves toward a ceiling; (2) **food-neophobia fading** — the
launch wariness (`neophobia_launch`, the reaction to a *novel* food; Pliner & Hobden 1992) decaying
with cumulative *availability* toward **zero** (the mere-exposure effect), which *raises* the ceiling.
This is **gated by sensory parity**: familiarity cures "it's weird", not "it's worse" — and even once
neophobia fades, a *taste* deficit (`accept_x`<1) persists (the plant-based lesson). Cultivated's escape
is that it is real tissue, so sensory parity is physically attainable.

**Neophobia is a named, ± dial on BOTH novel meats.** Instead of a generic cultivated-only "standing"
catch-all, novelty attitude is a single behavioural primitive (Pliner & Hobden 1992) applied symmetrically
to the two non-conventional meats: `neophobia_x` (cultivated) and `neophobia_p` (plant-based). It is a
**utility offset (utils): negative = neophobia** (the novel food is shunned), **positive = neophilia**
(novelty is a draw), 0 = neutral — adjustable either way. The **default is 0** (neutral), so it does not
move the central headline; it is an exploration dial alongside `accept_x`/`theta_free_M`. The timing rung
adds an **extra launch wariness** (`neophobia_launch`) that decays with exposure *onto* the long-run
`neophobia_x` (so cultivated's neophobia relaxes from `neophobia_x + neophobia_launch` toward `neophobia_x`).
This is the "no symmetry-breaking garbage collector" fix: cultivated's deviations from conventional are now
all *named* (price, taste, slaughter-free, real-tissue, neophobia), each interpretable, none a fudge —
and the novelty term is symmetric across the two novel products, not a cultivated-only special case.

**The cost→time coupling.** Rather than a smooth (false-precision) learning curve, the simulation is
driven by a few named **cost-milestone paths** (`COST_PATHS`): step functions where `R` drops when a
milestone lands. The `R` endpoints are *derived from the cost model* (Pasitka base → medium-banked →
both-levers → floor), so they cannot drift from Rung 2; only the milestone *year*
(`milestone_year_breakthrough`) is the declared unknown. Each year `R(t)` comes from the active path,
the Rung-3 WTP curve gives the ceiling, and rollout × acceptance give the realised trajectory
(`cost_paths_timing`). We show several paths (a scenario band), never one curve.

## Rung 5 — uncertainty (`uncertainty.py`)

**Not a time axis** — in a pre-commercial field cost falls in milestone-gated jumps with unknown
timing, so there is no calibratable `R(t)`. Instead: the **endpoint distribution**. Monte Carlo
(N=20,000) over the priors → distribution of achievable `R` and the long-run share it implies, as a
range with confidence intervals. `R_from_inputs` is the one cost→R equation; `spread_contribution`
attributes the spread to each input (reused by the sensitivity rung). The cost priors are **centered
on Pasitka's measured values** (medium $0.63/L, cells eff=1.0), so improvements are the optimistic
tail, never assumed. Pin any input on the CLI (`--fix media_price=0.2`) to ask "if this definitely
lands, what then?".

Result (commodity): **R P50 = 1.93, 80% CI [1.54, 2.35], 0% at/below parity** — consistent with
Pasitka's own published projections (R ≈ 2.25–2.42). The realised spread is driven by **overhead /
scale-up (~13%)** and **`p_conv` (~10%)**. The long-run share it implies: **P50 ≈ 11.6%, 80% CI
[4.1, 25.7]**.

## Rung S — sensitivity: levers & bottlenecks (`sensitivity.py`)

The headline output for a technical reader. Two complementary views that can *legitimately differ*:

- **One-at-a-time (OAT) tornado** (the lead): sweep each input lo→hi with all others at mode; rank
  by how far the output moves. This is the **potential** swing of each lever.
- **Variance share** (the cross-check): reused *verbatim* from `uncertainty.spread_contribution`, so
  the number matches the Monte Carlo exactly. This is the **realised** contribution to the band.

With the measured-centered priors the two views diverge in an informative way: medium price and cell
efficiency have *large potential swings* (big OAT bars) but *small realised contributions* (~0% of
the band), because they are centered on the measured value — they are upside, not expected movement.
Reactor scale-up and `p_conv` lead the *realised* spread. So the OAT answers "how much could this
lever move things"; the variance answers "how much does it move the expected band". Both are shown.

Figures: `sensitivity_tornado_R` (cost levers on R; scale-up leads the realised spread),
`sensitivity_tornado_share` (cost levers via R + demand dials; at the baseline R≈2.4 the cost levers
(efficiency, medium price) and `eps_own` lead share, the acceptance dials lead it *at parity*). See RESULTS §1, §3.

## Rung 6 — scaffolding (`scaffolding.py`, most speculative)

Structured (cut/fillet) products vs a **premium** target:
```
structured_cost = biomass_cost + scaffold_frac × material_price + process_cost
```
Material price is anchored (Gu25: synthetic PLA/PCL ~$2–20/kg, a minority of mass). **Process cost
is grounded in no TEA** — carried as a wide $1–15/kg band, the single most speculative number. The
strategic point: a structured product competes with $25–40/kg premium cuts, not $12/kg commodity, so
the larger denominator absorbs the scaffold cost — which is why cultivated-seafood firms chase
premium species.

## Rung 7 — the meat market (`meat_market.py`)

Cultivated *cost* is ~constant across species; conventional *price* ranges ~5×. So `R` and share
differ enormously per meat type; we roll up by **volume** (impact) and **value** (market). Demand is
**tier-dependent and runs opposite to price:** basic everyday meat is price-uncompetitive
but demand-friendly (cleaner-meat pull, no authenticity issue); premium/luxury is price-competitive
but demand-hostile (authenticity, price-insensitivity). **The sweet spot is mid-cuts** (salmon
fillet, beef steak), not ultra-luxury and not cheap mince. Per-region local prices **and region income**
(via the income→price-sensitivity term, `REGION_INCOME`) give a penetration band: **Europe is easiest** (rich + priciest
meat), while low-income regions (India, Brazil, Nigeria) are hardest — cheap meat *and* high
price-sensitivity compound. See RESULTS §4–5.

---

## Cruxes

- **Gate 1 (cost, dominates):** does cost reach parity? Most likely *no* for the basic product
  (R P50 ≈ 2.0), and the binding lever within Gate 1 is **scale-up** (overhead, ~half the spread).
- **Gate 2 (demand, at parity):** the acceptance dials (`accept_x`, `theta_free_M`) — cultivated's
  standing vs conventional — span ~11% (friction) to ~74% (preferred)
  at parity. No baked-in stance; the reader sets them.

The **low-share world** holds if cost stays above parity (Gate 1, most likely) **or** standing is
negative. The **tens-of-percent world** needs cost at parity **and** neutral-to-positive standing.

## Running it

```bash
cd model
../.venv/bin/python inputs.py                       # the datasheet (every number + source)
../.venv/bin/python cost_model.py --no-latex        # cost, scale-up scenarios, waterfall
../.venv/bin/python sensitivity.py --no-latex       # tornado + key-knobs table
../.venv/bin/python uncertainty.py --no-latex       # the R / share distribution
../.venv/bin/python meat_market.py --region eu --no-latex
../.venv/bin/python report_figures.py --no-latex    # the curated 9-figure report set
```
Flags: `--no-latex` (no TeX), `--show`, `--outdir`, `--formats`, `--fix name=value`.

## Sources

- **Pasitka et al. 2024**, *Empirical economic analysis … cultivated chicken using animal-free
  medium*, **Nature Food** 5:35–50. The empirical TEA; cost anchors + the three reactor configs.
- **Humbird 2021**, *Scale-up economics for cultured meat*. The amino-acid feedstock floor and the
  physical scale-up constraints (used as rationale, not cost numbers).
- **GFI 2026**, *State of the Industry Report: Cultivated meat, seafood, and ingredients*. Company
  self-reported media-cost claims (sub-$0.20/L), tagged as unverified.
- **Gu et al. 2025** — scaffold materials. **Peacock 2023** (EA Forum) — the at-parity plant-based
  displacement evidence for the acceptance dials.
- **Demand calibration (Rung 3):** **Nectar "Taste of the Industry" 2024 & 2025** — plant-based blind
  taste-tests (only ~16% of 122 SKUs reach sensory parity → taste is the binding constraint, and the
  PB taste deficit `taste_quality_p`). **GFI/NIQ retail pricing 2024** — PB-meat +77% price premium
  (`price_pb_mult`). **GFI–SPINS/Circana 2024** — PB-meat ~0.8% of meat $ / ~1.7% packaged, declining
  (`pb_share_target`); PB-milk ~15% share / ~40% household penetration (the [4] validation anchor).
  **Gallup 2023** — US 4% vegetarian + 1% vegan (`w_eth`). **GFI/Morning Consult 2024** — ~89% of
  PB-meat buyers are non-veg/vegan (pins `w_realtissue_M` via the mainstream buyer split).
- **Income & regions (Rung 3 price term, Rung 7 roll-up):** **Berry, Levinsohn & Pakes 1995**
  (*Econometrica*) — the `α·ln(income − price)` price form (richer = less price-sensitive). **World Bank
  2023–24** — GDP per capita (PPP) by region (`income_ref`, `REGION_INCOME`). **Muhammad et al. 2011**
  (USDA ERS) — food demand is ~2–3× more price-responsive in low- vs high-income countries (sets the
  damped gradient `income_gradient`). **BLS 2025** — US dried-bean retail price ($3.40/kg → `price_wf_mult`).
