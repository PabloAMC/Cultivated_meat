# From a kilo of cells to a shelf price: is the retail markup a fixed $/kg or a percentage?

> Names (2026-11-19): the low-lactate example was earlier called Central; the all-favourable example was earlier called the best case. Cells are described by their traits, never as a named kind of cell.

> Repinned 2026-11-19: nutrient floor $2.00 (GFI feed grade), growth factors inside complete media prices, medium settings floor/$0.20/$0.30/$0.50; cut cost rebuilt (0.8 cells + $2 matrix + $2 assembly beyond mince), cuts cheaper.

> Repinned 2026-11-19 (audit batch): cells dearer (ammonia tolerance 4 mM), seafood re-priced by consumption, the tier rule replaced by a blend penalty, the equal-price share drawn around its 13% setting; see audit_2026-11-19.md.

> Repinned 2026-11-19 (second round): shoppers' liking is a Student's t spread (standard deviation 3.9 utils, 4 degrees of freedom) on a 67-point grid, not a normal spread of 5 on fifteen points; see liking_spread.md.

> Repinned 2026-11-20 (engine batch): the scenarios' cells tolerate 35 mmol/L of lactate, bubble deaths and a harvest loss are charged, a washed tank takes twice the fed-batch crew, the membrane lasts 2,415 L/m2, and growth factors, utilities and the crew follow the Humbird back-test, so cells are dearer (the low-lactate example $32.80 to $49.96 a kilo, the all-favourable example $11.67 to $18.71, Published cells in fed-batch $209 to $323) and every share here fell; the demand model did not change; see full_review_2026-11-19.md and humbird_backtest.md.

> Repinned 2026-11-20 (model batch): the all-favourable example keeps haemodialyser fibres for its cells, so it uses far less process membrane and its cells cost $7.62 a kilo, not $18.71 (the low-lactate example $49.50); see market_size_loop.md. The rules table and section 4 are regenerated.

Compiled 2026-11-18, after Pablo asked whether the model's flat $5/kg markup should be multiplicative, as Gemini argued. The
answer changed the model: since this note the shelf price is **(cost + a) / (1 − m)**, with per-kg costs a = $2.5/kg
(`markup_add`) and the shop's gross margin m = 28% of the shelf price (`retail_margin`). The numbers in sections 2 and 4 come
from `retail_spreads.py` and are checked by `tests/test_retail_spreads.py`.

Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet; **MEM** background knowledge, unchecked.

## 1. The two rules, and what each predicts

- **Flat:** shelf = cost + a. A dearer product carries the same dollars of spread.
- **Percentage:** shelf = cost × b, or cost / (1 − m). A dearer product carries proportionally more dollars.

For an existing meat whose wholesale price moves, the flat rule predicts that retail moves by $1 per $1 of wholesale. The
percentage rule predicts that it moves by b = retail/wholesale, which is 1.7–2.5 for US beef, pork and chicken.

## 2. What USDA's own prices show (model; USDA ERS monthly data, 1970–2025)

| | retail, $/kg (2025) | wholesale, $/kg | retail ÷ wholesale | retail change per $1 of wholesale change: over 12 / 36 / 60 months | a at a 28% margin |
|---|---|---|---|---|---|
| Choice beef | 20.68 | 12.03 | 1.72 | 0.74 / 0.99 / 1.17 | $2.86 |
| Pork | 10.91 | 4.32 | 2.52 | 0.58 / 0.77 / 0.92 | $3.53 |
| Broilers | 5.41 | 2.34 | 2.31 | 0.25 / 0.78 / 0.84 | $1.56 |

Retail moves about dollar for dollar with wholesale over three to five years, and less over one. None comes close to the
1.7–2.5 a pure percentage rule predicts. A fit of the levels since 2000 (with a linear trend for the drift in costs) gives
retail = $2.59 + 1.00 × wholesale for beef: a flat rule. The five-year figures also carry general inflation, which pushes
them up, so they overstate the percentage part if anything.

The literature agrees on the time series:
- coffee: "approximately cent-for-cent" (Nakamura & Zerom 2009, NBER WP 15255; FT);
- beef: six-month pass-through 19–35%, and a long-run elasticity of 0.88 (Roeger & Leibtag 2011, ERS ERR-112; FT);
- beef, pork, chicken: beef one-for-one; pork and chicken 1.4–1.45 per dollar, which the authors put down to USDA's conversion
  factors (Hahn & Green 2000, JARE; FT).

## 3. Why a percentage part still belongs in the rule for cultivated meat

The time series answers a different question from ours: how a shop prices the same product when its cost swings. Cultivated
meat is a new product whose cost sits several times above chicken's, permanently. For that, the evidence points to a margin
set as a percentage:

- US meat departments run gross margins of 27.6% (Progressive Grocer, about 2011; SNIP) and 28–32% (Cooperative Grocer
  2016; FT); grocers describe pricing as unit cost plus the target margin (Cooperative Grocer, about 2009; FT).
- Wohlgenant & Mullen (1987, WJAE; FT) find for beef that about 20–26% of the farm-to-retail spread moves with the retail
  price, and reject a fixed markup.
- In French supermarkets in 2024 a premium Label Rouge whole chicken carried a 25% margin (€1.63 of €6.46) and a chicken
  fillet 36%: a lower percentage on the premium product, but more euros per kilo (OFPM 2025 report via Réussir; secondary FT).
- Shrink, the cost of holding stock and card fees scale with the product's value (MEM; standard retail accounting).
- **A direct comparison, added 2026-11-18:** Beyond Meat's ground product and conventional 80/20 ground beef both sell in US shops at
  about twice the price the retailer pays, so retailers and distributors take about $1 a lb more on the dearer product (Knowles 2026,
  from Beyond's filings; FT). That is a pure percentage markup on one pair of products, more than this note's rule gives a dearer
  product. It includes distributor margin and trade spend, and it is one company.

A rule that takes the **whole** wholesale-to-retail spread as a percentage (42–65% of retail, the audit's
(cost + $1)/(1 − 45%)) double-counts: that spread includes the per-kg costs of cutting, packing and transport.

## 4. The rule now in the model, and what it changes

Shelf price = (cost + a) / (1 − m), with a = $2.5/kg (range $1.5–3.5) and m = 28% (range 15–40%). Both are drawn in the
uncertainty bands. The per-kg part is fitted to USDA's 2025 spreads at a 28% margin (table above: chicken $1.6, beef $2.9;
pork's $3.5 includes curing bacon and ham), plus about $1 to form cells into a product (`au_processing`).

| rule | cells' cost for parity with $12 meat | All-favourable example: shelf price, share | Low-lactate example: shelf price, share |
|---|---|---|---|
| flat $5 a kilo (the model before 2026-11-18) | $7.00 | $12.0, 6.84% | $53.7, 0.14% |
| per-kg $2.5 + a 15% margin | $7.70 | $11.1, 7.59% | $60.2, 0.09% |
| **per-kg $2.5 + a 28% margin (the model now)** | $6.14 | $13.2, 5.58% | $71.1, 0.05% |
| per-kg $2.5 + a 40% margin | $4.70 | $15.8, 3.76% | $85.3, 0.02% |
| $1 + 45%: the whole spread as a percentage (the 2026-11-16 audit) | $5.60 | $14.5, 4.44% | $90.3, 0.02% |

Shares are the long-run share of world meat by weight. The parity threshold moves little, from $7.0 to $6.1, because every
rule is fitted to commodity meat's own spread. The shares above parity, where every scenario sits, fall: the low-lactate
example's point share ($49.50 a kilo of cells) by nearly two-thirds, from 0.14% to 0.05%. The all-favourable example's cells
($7.62 a kilo) are only a little above the parity threshold, so the rule matters less for it: its share falls by about a fifth,
from 6.85% to 5.44%, and a 15% margin would give it more than the flat rule. The all-favourable example here is its cells with
the model's ordinary demand (13% at equal price), not its own 55%. (These shares use the costs of the 2026-11-20 model batch,
in which the all-favourable example keeps haemodialyser fibres for its cells. With the 2026-11-20 engine batch's costs ($18.71
a kilo for the all-favourable example's cells) they were 0.14% to 0.05% and 2.18% to 1.13%. With the costs of the 2026-11-19 audit batch and the
Student's t spread of liking fitted later that day they were 0.56% to 0.21% and 4.77% to 3.16%. With the audit batch's normal
spread they were 0.34% to 0.08% and 4.29% to 2.81%; with a heavier tail of liking the rule matters less where cultivated meat is
far dearer than meat. Before that batch, with the rebuilt cut cost, they were 1.29% to 0.53% and 6.63% to 4.97%; before the cut cost was rebuilt, 0.50% to 0.13% and
4.48% to 2.74%; when the rule was changed, 0.41% to 0.16% and 8.0% to 3.7%; and with the premium markets sized from data and every
shopper alike, 0.14% to 0.04% and 7.4% to 3.1%.)

## 5. On Gemini's answer

Gemini's core claim, that shops set percentage margins, is right for pricing a new product, and is now in the model. Two
parts go further than the evidence:

1. **Pure multiplication on the whole cost.** It does not fit the dollar-for-dollar pass-through in section 2, and it ignores
   the per-kg costs (forming, packing, cold chain) that do not scale with price.
2. **Margins that rise with the quality tier** (12–20% on standard chicken to 32–42% on organic, with sell-through rates of
   80–88%). No sources were given, and the one direct comparison found runs the other way: Label Rouge at 25% against a
   standard fillet at 36% in France. The model holds the margin constant across products; the 40% end of its range covers
   the possibility that a slow-selling niche product carries a higher margin.

Its point about **slow sales** is fair and is not in the model: a product with a fraction of a percent of the market spoils
more per kilo sold and earns less per metre of chilled shelf, which pushes the margin up early on. The long-run share assumes
cultivated meat is on every shelf and selling steadily.

## 6. Judgement

- That (cost + a)/(1 − m) describes how a new, dearer meat would be priced better than a flat $/kg: **about 0.75**; that it is
  closer than a whole-spread percentage: about 0.65 (lowered from 0.75 after the Beyond comparison).
- That the flat $5 holds up (for example, retailers pricing it as a loss-leader, or most volume going to restaurants or
  direct sales with other margins): **about 0.15**.
- That the whole spread scales as a percentage: **about 0.20** (raised from 0.10 after the Beyond comparison).
- That the shop's margin on cultivated meat lies within 15–40%: **about 0.8**.

## 7. What would settle it

- A wholesale (ex-factory) price and the shelf price of the same plant-based or premium meat SKU at several retailers; a
  few such pairs fix a and m directly.
- The ERS organic broiler study (LDP-M-150, 2006) gives wholesale premiums of 169–262%; the matching retail premiums were not
  found.

## Sources

1. USDA ERS, Meat Price Spreads, "Historical monthly price spread data for beef, pork, broilers" (CSV, read 2026-11-18). A
   compact extract is in `retail_markup_form_sources/`.
2. Wohlgenant & Mullen 1987, "Modeling the farm-retail price spread for beef", WJAE. https://ageconsearch.umn.edu/record/32229/files/12020119.pdf (FT)
3. Hahn & Green 2000, JARE. https://ageconsearch.umn.edu/record/30840/files/25010109.pdf (FT)
4. Roeger & Leibtag 2011, ERS ERR-112. https://ageconsearch.umn.edu/record/102757/files/ERR112.pdf (FT)
5. Nakamura & Zerom 2009, NBER WP 15255. https://nber.org/system/files/working_papers/w15255/w15255.pdf (FT)
6. McShane, Chen, Anderson & Simester 2016, Marketing Science, via Kellogg Insight. https://insight.kellogg.northwestern.edu/article/what-do-customers-pay-when-wholesale-prices-change (ABS/SNIP): cost increases often pass through at above 100%, cuts flat.
7. Cooperative Grocer archive, meat department pricing. https://archive.grocer.coop/node/13399 (FT)
8. Réussir, "Volaille: les marges sous la loupe du rapport OFPM 2025". https://www.reussir.fr/lesmarches/volaille-les-marges-sous-la-loupe-du-rapport-ofpm-2025 (secondary FT)
9. Knowles, "Why is plant-based meat still so expensive?", Net Primary Production, 16 November 2026. https://netprimary.substack.com/p/why-is-plant-based-meat-still-so (FT; figures not read)
