# Do announced medium prices include growth factors?

Compiled 2026-11-18. The rule below is in the code behind the input `sc_medium_complete`, **on since 2026-11-19**, with every cost
study repinned. The same day the $0.15 a litre setting was dropped and the $0.05 aspiration became "at the nutrient floor"
(`nutrient_floor.md` §6), so the table in section 3 is on the model before those two changes.
Access levels: **FT** full text read; **FT(s)** full article read through a summarising fetcher; **ABS** abstract only; **SNIP**
search snippet; **MEM** background knowledge, unchecked.

## 1. The question

The model priced the medium per litre from announced and modelled figures ($0.15–0.50) and added growth factors (insulin, transferrin,
FGF2, TGF-β and similar) on top, as a fraction of Humbird's $3 per kg of cells. If the announced prices already include growth factors,
the model counted them twice: $3.0 a kilo in Central.

## 2. What each source includes

| source | price a litre | growth factors included? | evidence | access |
|---|---|---|---|---|
| SuperMeat, "A Deep Dive Into Cost-Effective Cultivated Meat Production", Nov 2024 | under $0.5, at scale | **yes** | its chemically defined medium is "formulated with precise concentrations of amino acids, vitamins, growth factors, and trace elements" | FT |
| Pasitka et al. 2024, Nature Food, Supplementary Table S5 | $0.63 (animal-component-free medium) | **yes**, a line of its own | growth factors 2 kg a year, $0.18M of $15.1M of nutrients: about $0.0075 a litre, 1.2% of the medium's cost | FT |
| GFI (Specht), medium cost analysis, 2020 | $0.24 in its cheapest scenario | **yes**, by construction | Essential 8 levels (insulin 19.4, transferrin 10.7, FGF2 0.1, TGF-β 0.002 mg/L) at $4/g: about $0.12 a litre | FT |
| Lever VC report via AgFunderNews, Apr 2025 | "several" companies under $0.50 (unnamed) | probably | "aren't watered-down media formulations" | FT(s) |
| Vow, same article | no price | yes | "low concentration of two growth factors only" | FT(s) |
| Meatly, 2024–25 (pet food) | $0.30–1.25 | none needed | growth factors replaced by food-grade ingredients | FT(s) |
| Humbird 2021 | no price a litre | **separately**: $3 per kg of cells at Essential 8 levels | the source of the model's growth-factor line | FT |

## 3. Judgement and the change

- About 0.85 that the $0.10–0.50 a litre announced or modelled prices already include whatever growth factors those processes use.
  The remaining 0.15 is mostly unnamed companies' accounting, not evidence of basal-only prices.
- Where included, growth factors are cheap: about $0.01–0.12 a litre, $0.1–1.5 a kilo of cells.
- **The change (when `sc_medium_complete` is on):** the medium settings $0.15, $0.20, $0.30 and $0.50 a litre are complete media; with one of them the growth-factor
  switch adds nothing. It still applies to the $0.05 aspiration, which is the nutrients alone. The cost of growth factors is now
  carried by the medium's price.

| scenario | now | with the rule on |
|---|---|---|
| 1. Today | $62.96 | $56.99 |
| 2. Process changes and cheaper inputs | $30.73 | $27.74 |
| 3. Central | $29.42 | $26.43 |
| 4. Food-grade plant with shared medium | $26.56 | $23.57 |
| 5. Best case | $9.66 | $9.66 (it buys no growth factors) |
| Forecast for 2035 | $24.80 | $21.82 |

- Caveat: the company figures are self-reported projections at scale, not audited prices, and GFI has called SuperMeat's optimistic.
  The bigger risk may be the medium's price itself, which the medium switch already spans ($0.05–0.50).

## Sources

1. SuperMeat, A Deep Dive Into Cost-Effective Cultivated Meat Production, November 2024.
2. Pasitka et al. 2024, Nature Food, and its Supplementary Information, Table S5.
3. GFI (Specht), clean meat production volume and medium cost, 2020.
4. AgFunderNews on the Lever VC report, April 2025.
5. Humbird 2021, Biotechnology and Bioengineering.
