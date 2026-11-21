# Can a filter hold 5 L/m²/h at 25% cells for a month?

Date: 2026-11-15; costs recomputed 2026-11-20 on the final model (section 4). The default membrane life became 2,415 L/m² on 2026-11-20 (section 5). Code: `filter_flux.py`; tests: `tests/test_filter_flux.py`; inputs `ff_*` in `inputs.py`. The research report with every source,
its URL and how much of it was read is `filter_flux_sources/flux_limit_sources.md`. Costs are 2025 dollars per kg of wet cells. No default changed.

## 1. The question

The default retention device is a TFF hollow-fibre loop at a permeate flux of 5 L/m²/h. Its membranes are replaced after 2,415
litres a m² (3,960, one 33-day run at 5 L/m²/h, until 2026-11-20). Two questions. Is 5 L/m²/h above a physical limit? And is such a life
what has been measured?

## 2. The physical limit is not the problem

Cells carried to the membrane by the liquid passing through it are swept back by shear-induced diffusion. The limiting flux, as
printed in a thesis that restates Belfort, Davis and Zydney (1994) (Vyas 1999, Eq. 2.18, full text read and the page image checked), is

J = 0.078 × shear × (φ_w a⁴ / (φ_b L))^(1/3) × ln(φ_w/φ_b)

for the wall shear rate, the cell radius a, the fibre length L, and the cell volume fraction at the wall (0.6) and in the bulk. A
second form (Davis and Sherwood, in Kromkamp 2005) has 0.072 and no logarithm. The primary papers were not readable. The form is
checked in these two theses.

For 17 µm cells (Vyas's formula, the research pass's arithmetic; the module uses the model's cell and agrees within 5%):

| fibre length | shear | cells by volume | ceiling | against 5 L/m²/h |
|---|---|---|---|---|
| 0.3 m | 1,000 /s | 12% | 200 L/m²/h | 40× |
| 0.3 m | 2,000 /s | 25% | 171 | 34× |
| 1.0 m | 1,000 /s | 25% | **57** (the worst corner) | 11× |
| 0.3 m | 4,000 /s | 12% | 801 | 160× |

- **5 L/m²/h needs only about 25–90 /s of shear.** Fibres run at 1,250–5,500 /s.
- **Real suspensions fall short of the model.** Yeast gave fluxes 2 to 4 times lower (Redkar and Davis 1993, abstract only). Cut
  the worst corner by 4 and it is still about 14 L/m²/h.
- **A short test agrees.** One ATF test on CHO cells at about 13–16% by volume ran at 69 L/m²/h without exceeding its critical flux
  (Veje 2024, full text read).
- **The caveat:** the model is for rigid, non-sticking spheres, and its second form is valid only below 10% cells. The 12–25% here is an extrapolation.

Rough judgement (made while building the model with an AI assistant; not measured and not reviewed by an expert): under 5%
that 5 L/m²/h is above the back-transport limit. The reasoning: the worst corner of the table is 11 times above it, still about
3 times after the yeast shortfall, and a CHO test ran at 69 L/m²/h without reaching its critical flux.

## 3. What has been measured is the problem

Real filters are limited by slow fouling, not by cells piling up at the wall.

| Source (read in full) | Cells | Flux | What happened |
|---|---|---|---|
| Veje et al. 2024 (CHO, ATF) | about 50–60e6 cells/mL (13–16% by volume) | 8.3 L/m²/h | the pressure jumped after 3 to 6 days, about 1,200 L/m² |
| Pinto et al. 2020 (CHO, TFF) | 75e6 cells/mL | 1–2 L/m²/h | the pressure rose after 900–1,200 L/m² (0.2 µm) or 450–900 (0.65 µm) |
| Radoniqi et al. 2018, Veje 2024 | | 2–3 L/m²/h | the usual flux in perfusion |
| Mostafavi et al. 2025 (reverse-asymmetric fibre) | up to 25e6 cells/mL (4–7%) | 152–229 L/m²/h | 14 days with no fouling, in 1.5 L |

- **The default life is 2 to 5 times the measured throughput.** 2,415 L/m² against 450–1,200 (the earlier default, 3,960, was 3 to 9 times). It is Humbird's
  replacement schedule, about 20 days at 5 L/m²/h. Measured membranes fouled before that at all but the lowest fluxes.
- **The measured cells were thinner** than 25% by volume, and the cultures had antifoam and cell debris. Meat cells may foul
  more or less. The one counter-example filtered 150–230 L/m²/h for two weeks at a low density.
- **Life is a time in the model, and a throughput in the data.** The model's `rt_membrane_life` does not change with the flux.
  A membrane replaced once per run at 2.5 L/m²/h filters 1,980 L/m², under the default.

What would have to be true for the default to hold: a meat-cell culture at 12–25% cells by volume fouls a standard
microfiltration fibre no faster than the best measured CHO runs did at thinner densities, so that 5 L/m²/h holds for about 20
days. The later evidence pass put the median life at about 1,500 L/m², with an 80% interval of 500–4,000
(`ammonia_tolerance_and_filter_life.md`).

## 4. What it does to the cost

| Cost per kg with the filter at (flux, membrane life) | Default (5, 2,415) | The earlier default (5, 3,960) | (5, 1,200) | (2.5, 1,200) | (2.5, 450) |
|---|---|---|---|---|---|
| Low-lactate example | **$49.50** | $40.81 | $72.05 | $72.33 | $147.05 |

The all-favourable example ($7.62) is not in the table: it holds its cells back with dialyser-grade hollow fibres, whose flux,
life and price it sets itself (`scenarios.all_favourable`), so the cell filter's flux and life do not move it.

- **The hardware barely matters; membrane life does.** Halving the flux doubles the membrane area but moves the low-lactate example by $0.3. The
  membrane's throughput moves it by $23 to $98.
- **Moving the default from 3,960 to 2,415 added $8.69 to the low-lactate example.**
- **Caveat:** the short-life columns include the lost-run factor, as the default does; a membrane replaced
  several times a run loses less than that to a lost run, so they are high by up to about 15% of the membrane cost.
- **At the measured CHO throughput, the low-lactate example costs $72–147.** That is not a forecast: the data are from thinner cultures of a pharma line.
  It says the default still sits above the measured CHO range, by a factor of two at its top.
- **Life and price act together.** A membrane adds price ÷ life to each litre filtered. A 1,500 L/m² membrane costs the low-lactate example nothing extra at $901 a m² or less, and a 1,000 L/m² membrane at $600 or less (`filter_flux.break_even_price`).

## 5. What this means

1. **The decision was taken on 2026-11-20:** `rt_membrane_life` is 2,415 L/m², Humbird's own schedule, paired with his price. At 1,200 L/m² the low-lactate example would be $72.05. The model's range still
   spans 900–5,500.
2. **The experiment that settles it:** run a hollow-fibre filter on a meat cell line at 10–25% cells by volume at 2–5 L/m²/h and
   record the pressure against litres filtered per m². Fouling is slow, so it takes weeks. A bench filter of 0.025 m² is enough.
3. **What would raise the life:** the reverse-asymmetric fibre with an open 40 µm side facing the feed (Mostafavi 2025), cleaning
   in place, or a lower flux. None is shown with a thick meat-cell culture.

## 6. What was not found

The primary papers (Zydney and Colton 1986; Davis and Leighton 1987; Belfort et al. 1994), Karst 2016 and Clincke 2013 in full, a
damage threshold for cells in shear, and a table of plasma flux against shear for blood at 40% haematocrit.
