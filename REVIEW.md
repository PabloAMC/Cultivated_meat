# Tough-but-fair review of the interactive cultivated-meat model

Scope: `build_interactive.py` (the generator) and `interactive.html` (its output, with the
embedded JS engine and the methodology write-up). I read the in-page methodology cold first —
before any code — to judge whether the model *as explained* is intuitive, then read the JS
engine, then cross-checked the Python source of truth (`market_share.py`, `cost_model.py`,
`adoption_timing.py`, `inputs.py`) and ran the model and both test suites.

Headline verdict: **this is a strong, unusually honest model, and the explanation is genuinely
good.** The chain (cost → price ratio → discrete-choice share → Bass×neophobia timing) is the
right framework, the calibration is pinned to real moments, the JS mirrors the Python to ~1e-16
(verified), and the write-up is candid about what is forced vs judged. The issues below are
about *polish and a few specific claims*, not about a broken model. The single most important
finding is a class of **stale illustrative numbers in the prose** (now fixed) — a credibility
risk precisely because the model itself is so careful.

Severity key: **[A]** correctness/credibility (fix before it's seen by reviewers) ·
**[B]** clarity/explanation · **[C]** architecture/maintainability · **[D]** judgement-call /
worth-considering. ✅ = already fixed in this pass.

> **Clarity pass (2026-06-11, second round).** Separately from the correctness fixes below, the
> methodology was re-read from a newcomer's standpoint and restructured for readability:
> - **Added a plain-language on-ramp** at the very top — the question the model answers, the
>   three-step shape (cost→price, price→share, share→over-time), the central bet (cultivated *is*
>   real tissue, so it pulls from beef), and the measured-vs-judgement framing of "what to argue
>   about" — all before any equation. A smart reader with no background now gets the gestalt first.
> - **Demoted the referee-objection rebuttals into marked "For the skeptical reader" asides**
>   (new `.aside` CSS) so the main narrative flows and the defences are there when wanted. The
>   audience wants the rigor, so nothing was deleted — just visually separated.
> - **De-duplicated** the "no free fitted constant / no hidden standing knob" refrain (was stated
>   ~5×, now once in the main text + once in its aside) and cut the third redundant restatement of
>   the V_j terms (the equation, a plain-words gloss, *and* a prose re-walk → now gloss + glossary
>   table). Net effect: clearer structure, ~same length (concision was the lowest priority).
>
> All headline numbers unchanged; golden + drift + JS↔Python parity still pass.

> **Polish pass (2026-06-11, third round) — clarity refinements.**
> - **Headline tiles:** removed the broken `ⓘ` circled-i glyph (now plain "long-run ceiling" with a
>   hover tooltip) and removed the `R_x` tile entirely (ill-defined without a stated comparator).
> - **Figure 1** redrawn as **stacked cultivated + plant-based** bars per meat type (cultivated solid
>   by tier, plant-based green on top); three totals lines; retitled accordingly.
> - **Figure 3** retitled "Cultivated cost vs the two big inputs" (was ambiguous about whose cost).
> - **Figure 4** now plots the **plant-based operating point** too — a green dot on the PB curve at its
>   own R_p (~1.77), the true analogue of the cultivated dot; makes the "same price, very different
>   share" thesis legible in one figure.
> - **R / R_x consistency:** standardized on `R_x` for cultivated's price ratio in every prose, tooltip
>   and §4 spot (`R_p` for plant-based; bare `R` only as a generic axis word). Verified no bare-R leaks.
> - **Slider tooltips rewritten for reader usefulness:** mean length ~95→70 words (worst offenders
>   premium_resistance 179→121, loss_aversion 165→102). Pattern: what it is → what moving it does + the
>   key auto-computed number → default, and whether it's *measured* or *judgement*. Cut the ALL-CAPS
>   shouting, repeated "SWEPT in MC" boilerplate, and editorial hedging; kept one load-bearing source each.

---

## What is genuinely good (so the critique is calibrated)

- **Right model class, honestly labelled.** A two-segment, four-product random-utility logit
  with BLP income and reference-dependent loss aversion is exactly what an applied economist
  would reach for, and the page says so — *and* labels itself "calibrated, partial-equilibrium,
  a band not a forecast." That framing is correct and rare.
- **The no-nest trick is the right call.** Using a shared `real_tissue` attribute + two
  consumer types to get "cultivated cannibalises conventional, not the veggie burger" — instead
  of a nested logit — is elegant, transparent, and the self-check `[3]` proves it works
  (−45pp from conventional, −0.6pp from plant-based).
- **The β-derivation is correct and subtle.** The two-channel fix (income slope + loss-aversion
  slope) so the *realised* own-price elasticity equals κε is done right: I measured −3.59 at the
  anchor vs the −3.6 target. The double-counting it fixes was a real trap.
- **The PB-milk out-of-sample check is the model's best feature.** Holding the meat-calibrated
  coefficients fixed and swapping only positions reproduces milk's ~15% — that's a real
  falsification opportunity the model passes, and it's the strongest evidence the machinery
  isn't just curve-fit to one number.
- **Judgement parameters are exposed and swept, not buried.** κ, ρ (premium resistance),
  ν_x0 — the genuinely unidentified levers are sliders *and* in the Monte Carlo. This is the
  right discipline for an AP/founder audience.
- **Real tests exist and pass.** `run_parity.py` (JS↔Python to 1e-16 over 2000+ grid points)
  and `test_golden.py` (17 pinned values) both pass. The de-duplicated penetration roll-up
  (one `typeR`/roll-up shared shape) is good hygiene.

---

## [A] Correctness & credibility

### A1 ✅ Stale illustrative numbers throughout the prose (the big one)
The commit that "restructured health as a calibrated attribute and removed the free whole-food
intercept" (`4407a3a`) lifted **every at-parity figure by ~2–3 pp** (the neutral parity share
went 46.7% → **49.9%**). But the *illustrative* numbers sprinkled through the methodology and
the slider tooltips were never re-synced. Verified live-model values vs the old prose:

| Where | Prose said | Model gives |
|---|---|---|
| Parity, neutral | ~47% | **49.9%** |
| a_x = 0.8 / 0.6 / 1.1 | 25 / 11 / 59% | **27 / 12 / 62%** |
| θ_free = 0.5 / 1.0 | 57 / 67% | **60 / 69%** |
| b_x ladder (1→0) | 47/34/24/16/10% | **50/36/24/15/9%** |
| ν_x = −1 / 0 / +1 | 25 / 47 / 70% | **27 / 50 / 72%** |
| κ ladder @2.4 (3/4/5) | 13 / 8 / 5% | **14 / 9 / 6%** |

**Worst case — the λ tooltip was not just stale but self-contradictory.** It said
"At R=2.4: λ=1 → ~34%, λ=2.25 → ~8%, λ=4 → ~1%", implying loss aversion is a *huge* lever on the
headline. The model gives **8.8 / 9.1 / 1.4%** — λ=1 and λ=2.25 are nearly identical. That's the
model's *own* central design claim ("β absorbs λ's slope, so λ shapes the kink, not the level")
— yet the tooltip's ladder asserted the opposite. The 34% was pre-β-fix behaviour. Anyone who
dragged λ to 1 and saw ~9% (not 34%) would have lost trust in the whole page.

**Fixed:** all of the above corrected in `build_interactive.py`; the λ tooltip now reads
"λ=1 → ~9%, λ=2.25 → ~9%, and only the extreme λ=4 bites (→ ~1%)", consistent with the design.
Regenerated `interactive.html`; golden + parity tests still pass.

> **Root-cause recommendation (C-level, not yet done):** these numbers should be *computed from
> the model at build time* and string-substituted into the prose, exactly as the page already
> does for the param/price tables and the `income_check`. Hand-typed illustrative numbers will
> drift again on the next recalibration. This is the highest-leverage architectural fix.

### A2 ✅ Stale module docstring (`adoption_timing.py` line ~21)
The top-of-file narrative said neophobia decays "**toward ZERO**." The code (and every other
comment in the file) fades it toward the **long-run `neophobia_x`** slider (default 0, but a
dial swept [−2, 1] in the MC). A reader trusting the docstring would misunderstand the timing
rung's ceiling. **Fixed** to say "toward the long-run `neophobia_x` (the slider, default 0)."

### A3 [A] The headline number is the *equilibrium* ceiling, but reads like a forecast
The big "cultivated penetration · vol / val" number at the top of the page is the **long-run
equilibrium** share (novelty fully faded, ν_x = 0), ~9%/X% at today's cost. The timing chart
just below correctly shows today's *realised* share starting near the cold ~5%. A fast reader
sees a confident big number and may take it as "what share cultivated gets," not "the ceiling it
would reach decades out if it hit this cost." The methodology *does* explain equilibrium-vs-path
clearly — but the headline tile doesn't carry that caveat.
**Recommend:** label the headline tile something like "long-run ceiling (equilibrium)" or add a
one-line sub-caption, so the equilibrium framing travels with the number even when the prose
isn't read. (Not auto-fixed — it's a presentation judgement for you.)

---

## [B] Explanation / how intuitive the model reads

Overall the cold-read was *positive*: a non-economist can follow cost→R→share→timing, the
attribute table is clear, and "a 0 in the table is not a special case" is a nice touch. Remaining
friction points:

### B1 [B] The §2 utility equation is dense for a first read
`V_j = α ln(y − R_j p_conv) − λ(d_j)⁺ + (d_j)⁻ + q(a_j−1) + wˢg_j + wʳᵗb_j + wʰζ_j + ξ_j` lands
all at once. It *is* eventually unpacked term-by-term, but a reader hits the full expression
before the unpacking. Consider a one-line plain-language gloss immediately under it ("price you
can afford, plus a penalty for being dearer than normal, plus taste, ethics, real-meat, health,
and a novelty constant") before the formal walk-through.

### B2 [B] "47% on habit and brand alone" — but the model has no habit/brand term
The parity-reading paragraph attributes the ~50% split to "habit and brand." But the model
deliberately has **no** habit term (the page says elsewhere habit lives in the timing rung, per
Heckman). At parity with neutral dials, the 50% is really "two attribute-identical real-meat
products split the real-meat buyers via the logit's symmetry." Calling it "habit and brand" is
a slightly misleading shorthand that a sharp reader will catch against your own limitations
section. Reword to "on the logit's symmetry — two attribute-identical real-meat options split
the segment."

### B3 [B] The realised elasticity is −3.6 *only at the anchor*, ~−0.8 near parity
The κ explanation repeatedly cites "realised ε_x = −3.6," which is exactly right *at cultivated's
operating point (R≈2.4)*. But the local elasticity is ~−0.8 at parity and ~−1.7 at R=1.5
(I measured these). The prose mostly says "at its own operating point," so it's defensible — but
a reader who reads "−3.6" as a global property will be confused that share falls slowly just
above parity. One sentence noting the elasticity is largest far above parity (a property of the
BLP+kink shape) would pre-empt the confusion.

### B4 [B] BLP `α ln(y − price)` linkage to "price-sensitivity" is asserted, not shown
The income term's intuition ("richer = less price-sensitive") is stated and is correct, but the
reader is asked to take the `α = −β(y_ref − p_x)` normalisation on faith via the chain-rule note.
That note is good; consider also giving the punchline ("so doubling income roughly halves the
felt premium") so the *direction and magnitude* are concrete, not just the calculus.

### B5 [D] "no free fitted constant" is technically true but rhetorically over-claimed
The page proudly states the demand model has "no free fitted constant" because the old
whole-food intercept ξ_w was reparameterised as a *solved* health weight × a *fixed* health
position. That's a fair structural improvement — but `health_w = +2.0` is itself an assumed
position with no external anchor, and `w_health_M/E` are solved to hit moments. So a free
constant was replaced by (one assumed position + one solved weight) hitting the same moments.
It *is* more interpretable, but "no free fitted constant" slightly oversells it. Suggest
softening to "no *unexplained* constant — the outside option's standing is now a named (health)
attribute, with its weight solved to the same two moments the old intercept hit."

---

## [C] Architecture / maintainability

### C1 [C] The model is hand-ported twice (Python + ~750 lines of mirrored JS)
This is the structural elephant. `build_interactive.py` contains the entire model a *second*
time, as a hand-written JS port inside a 1700-line raw-string `HTML` template. The parity test
is excellent and catches divergence — but every model change must be made in two languages and
kept in sync by hand. The de-dup of the roll-up shows the team feels this pain.
**Options, in increasing effort:** (a) keep as-is but make the parity test a pre-commit hook so
divergence can't land; (b) generate more of the JS constants from Python (already done for the
JSON config — extend it to the illustrative numbers, A1's root cause); (c) longer term, compile
one source (e.g. transpile a restricted Python core, or write the core once in JS and call it
from Python via a JS runtime) so there's a single source of truth. (a)+(b) are cheap wins.

### C2 [C] 2290-line generator with a 1700-line embedded string is hard to navigate
The JS lives as one giant raw string. Splitting the JS into a few named string constants by
concern (model engine / SVG helpers / chart renderers / UI wiring) — concatenated at build —
would make both editing and diffing far easier, without changing output. The SVG species-icon
functions (~70 lines of path data) in particular could live in their own block.

### C3 [C] Test temp-file cleanup fails under the user's mount
`run_parity.py` tries to `os.remove(tests/_model_extracted.js)` and hits `PermissionError` on
the mounted filesystem (works fine in /tmp). Minor, but it means the test appears to "fail" when
run in place. Wrap the cleanup in `try/except OSError`, or write the temp file to
`tempfile.gettempdir()`.

---

## [D] Modelling judgement calls worth a second look (not errors)

- **D1 — Additive markup is load-bearing and the page knows it.** The $5/kg additive (not %)
  markup sets the parity threshold and is flagged honestly. Fine as-is; just confirming it's the
  right thing to keep front-and-centre, because it does more work than κ on the *cost* side.
- **D2 — Whole-food taste ≈ 0.3 and `health_w = +2.0` are unanchored but low-leverage.** The
  page says whole-food's taste "trades off with its solved baseline appeal," which is true, so
  its exact value washes out. Worth a one-line note that the same is true of `health_w` (its
  level is absorbed by the solved weight), so no one mistakes +2.0 for a measured quantity.
- **D3 — Two consumer types, one price coefficient.** Correctly listed as a limitation. For an
  exploratory tool this is the right simplicity; a continuous random-coefficients version would
  be false precision given zero cultivated choice data. No change — just endorsing the call.
- **D4 — Income enters utility through `ln(y − price)` with a damped cross-region gradient.**
  The monotonicity guard (income-aware β cap) is correctly implemented and I verified share is
  monotone-decreasing in R across all regions. Good. The only subtlety: the BLP form makes
  low-income regions *more* premium-sensitive, which is the intended ~2–3× gradient, but it's
  worth a sanity note that at very low income the `y − price` term can get small for premium
  cuts; the cap handles it, but it's the fragile corner.
- **D5 — Disruption-theory lens (per project brief).** The model captures the Christensen-style
  insight well *structurally*: cultivated is cheapest where demand resists most (premium,
  authenticity-bought) and most accepted where it can't win on price (cheap staples), so the
  entry window is mid-cuts. That's a genuine, defensible "no easy foothold" result. One thing the
  model can't see (and the limitations should perhaps name): disruptive entry often starts in a
  *non-consumption* or *new-attribute* niche (e.g. pet food, novel species, allergen-free,
  cell-line IP plays) rather than competing head-to-head on the existing price ladder. The model
  is a substitution model on today's ladder; the classic disruption path may route *around* it.
  Worth one limitation bullet.

---

## Priority order — ALL IMPLEMENTED (2026-06-11)

1. ✅ **A1** — stale prose numbers, esp. the λ ladder. Credibility-critical; fixed.
2. ✅ **A1-root** — *all 22* illustrative numbers are now COMPUTED FROM THE MODEL at build time
   (`illustrative_numbers()` in build_interactive.py) and injected via `{{TOKEN}}` placeholders,
   so they can never drift again. `main()` raises if any token is unsubstituted. A new
   drift-guard test (`test_golden.py::check_illustrative_numbers_in_html`) asserts every token
   is computed, every computed value is used, and the generated HTML carries no stray `{{...}}`.
   *(This also surfaced one more stale number I'd missed: the b_p→1 tooltip said ~9%, model gives 12%.)*
3. ✅ **A3** — headline tile relabelled "ceiling (equilibrium ⓘ)" with a hover note, and the lede
   now says the big numbers are the long-run equilibrium ceiling, not a forecast of today's share.
4. ✅ **A2** — docstring fix (fades toward long-run `neophobia_x`, not zero).
5. ✅ **B1–B5** — plain-language gloss under V_j (B1); "habit and brand" → logit-symmetry (B2);
   "−3.6 is the local elasticity at the anchor; smaller near parity" caveat (B3); income is a
   second-order lever at today's prices punchline (B4); "no *unexplained* fitted constant" with the
   reparameterised-not-eliminated clarification (B5).
6. ✅ **C2** — split the one 1700-line `HTML` raw string into `PAGE_HTML` (markup/CSS/methodology)
   + `JS_ENGINE` (the model+charts+wiring), concatenated in `main()`. Output byte-identical;
   golden+parity still pass.
7. ✅ **C3** — `run_parity.py` now writes its temp JS to the system temp dir and wraps cleanup in
   `try/except OSError`, so the parity test runs IN PLACE on the mounted filesystem (it used to
   fail there with PermissionError).
8. ✅ **D2** — note that `health_w`'s *level* washes out (only the product `wʰ·ζ_w` is identified).
9. ✅ **D5** — added the "substitution model on today's ladder; real disruption may route around it
   via non-consumption/new-attribute niches" limitation bullet.

All tests green after the changes: golden (17 pinned values unchanged), illustrative-drift guard
(22 values, 22 placeholders, consistent), and JS↔Python parity (1e-16 over 2000+ points).

What I did **not** find: no math errors in the cost model, the β-derivation, the calibration
solve, the softmax, or the Bass×neophobia coupling; no JS↔Python divergence; no monotonicity
violations; no broken tests. The bones are sound — this was a finishing pass, not a rebuild.

### Residual honesty note on the drift guard
The new guard enforces "illustrative shares are *only ever placeholders*," which catches the
common drift modes (unsubstituted token, typo'd token, dead computed value, stale literal that
removes a token entirely). It cannot catch a stale literal hand-typed *next to* a still-live copy
of the same token (e.g. one of `AX_08`'s two uses reverted while the other stays). That residual
gap is small now that every illustrative number is tokenized; closing it fully would require
banning bare `~NN%` literals from the template, which is impractical given legitimate data anchors
(`~5%`, `~89%`, …). Flagged rather than over-engineered.
