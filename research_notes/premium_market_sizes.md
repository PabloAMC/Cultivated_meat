# How big are the premium markets? Sizing the premium rows of the market tables

Date: 2026-11-18. Changes defaults: the premium rows of `meat_market.py`'s US, Europe and Global tables. Found while checking
`market_size_loop.md`, which rests on premium products' volume; the main model's Central share rests on it too.

Access levels: **FT** full text read; **SNIP** search snippet; **MEM** background knowledge, unchecked.

## 1. What was wrong

Every region's table carried sushi-grade seafood at 2% of volume (4% in China) and each other premium row (prime or wagyu beef,
heritage pork, organic chicken) at 0.5–1%, with no source. At Central's cost these rows are 99% of cultivated meat's sales, because they
are the only products priced near it. With world meat at about 270 Mt a year of boneless weight, the Global table's rows meant 5.4 Mt
of sushi-grade seafood at $35 a kilo and 1.35 Mt of prime or wagyu beef at $45.

## 2. What the data say

| product | volume, world, a year | source | access |
|---|---|---|---|
| Farmed Atlantic salmon | 2.5 Mt gutted, "about 1.7 million tonnes" of product (2024) | Mowi/Kontali Salmon Farming Industry Handbook 2025 | FT |
| Salmon eaten raw | "around 30%" of Norwegian salmon (Norway is about half of supply) | Norwegian Seafood Council via SalmonBusiness, 2025 | FT |
| Salmon's price | €6.4 a kilo whole and gutted (average since 2014); US retail fillets about $20–33 a kilo | Mowi handbook; price listings | FT; SNIP |
| Sashimi-grade tuna | 360–500 kt (Japan about 300 kt, the rest about 150 kt) | OPRT via VASEP | FT (secondary) |
| All tuna caught | 5.2 Mt, of which bluefin 1% and bigeye 7% (2023) | ISSF via Perishable News | FT (secondary) |
| Yellowtail, eel, sea urchin | about 0.25, 0.28 and 0.07 Mt live weight | — | MEM |
| US beef grading Prime | about 10% of fed cattle (2024); US beef 12.2 Mt carcass weight | Angus/CAB, USDA | SNIP |
| Wagyu | Japan about 0.17 Mt; Australia about 0.07 Mt (2022 projection) | commercial report; AWA via Beef Central | SNIP; FT |
| Organic chicken | 0.67% of US chicken output (2020); 1% of French (2023); Label Rouge 13% of French poultry (2024) | WATT; FranceAgriMer; Réussir | SNIP; SNIP; FT |
| Organic pork | 0.3% of EU output (about 2015); Ibérico about 3.7 million head | Pig World; trade press | SNIP |
| World meat | 378 Mt carcass weight (2024); about 70% of it is boneless meat | FAO Food Outlook Nov 2025; USDA ERS | SNIP |

Worked up to edible weight sold at about $30 a kilo or more:

- **Sushi-grade seafood: about 1.2 Mt a year (80% range 0.6–2.5).** Raw salmon 0.5 (30% of 1.7), sashimi tuna 0.25 (450 kt at 55% loin
  yield), yellowtail, eel, scallop and urchin about 0.3, others about 0.2. Even all farmed salmon plus all sashimi tuna is only about
  2 Mt, and most salmon sells for $20–30 a kilo, not $35.
- **Prime or wagyu beef at $45 a kilo or more: about 0.5 Mt (0.25–0.9).** US Prime is about 0.65 Mt boneless, of which the rib and loin
  that sell above $45 are about 0.2 Mt; wagyu-class beef (Japan, Korea's Hanwoo, Australia, the US) about 0.4 Mt, not all of it above $45.
- **Heritage and organic pork: about 0.4–0.5 Mt** (Ibérico about 0.25, EU organic 0.05), unless Chinese black-pig pork counts, which was
  not quantified.
- **Organic and Label Rouge chicken: about 0.35 Mt** (France 0.2, US organic 0.14, the rest of the EU).

## 3. What changed in the tables

Share of each table's volume. What was removed went to the same species' cut row, so every regional total is unchanged.

| table | row | was | now | basis |
|---|---|---|---|---|
| Global | seafood (sushi), $35 | 2.0% | 0.4% | 1.2 Mt of about 300 Mt |
| Global | beef (prime/wagyu), $45 | 0.5% | 0.2% | 0.5 Mt |
| Global | pork (heritage), $16 | 0.5% | 0.15% | 0.4–0.5 Mt |
| Global | chicken (organic), $13 | 0.5% | 0.12% | 0.35 Mt |
| US | seafood (sushi), $40 | 2.0% | 0.7% | about 0.3 Mt (sashimi tuna 90 kt, raw salmon, others); an inference from the world figures |
| US | chicken (organic), $13 | 1.0% | 0.3% | 0.67% of chicken, which is 41% of US volume |
| US | beef (prime/wagyu), $45 | 0.5% | 0.5% | checks out: about 0.2 Mt of Prime rib and loin |
| Europe | seafood (sushi), $45 | 2.0% | 0.5% | about 0.25 Mt of raw salmon and sashimi tuna; an inference |
| Europe | chicken (organic), pork (ibérico) | 1.0%, 0.5% | unchanged | check out: organic plus Label Rouge is about 3.5% of EU chicken; Ibérico about 0.25 Mt |

**Not changed, and not checked:** China (sushi-grade and live premium seafood at 4%; premium live seafood is a large category there and
no figure was found), Brazil, India and Nigeria; Europe's wagyu row (0.5% at $55, probably high).

## 4. What it does

- **The main model's Central share falls from 0.16% to 0.04% of world meat**, because nearly all of Central's sales were to premium
  rows that were three to five times too large. The US falls from 0.35% to 0.21% and Europe from 0.62% to 0.45%.
- **The best case moves little**, 3.69% to 3.11%: near parity most of its sales are ordinary cuts and mince.
- The uncertainty bands, the tables in RESULTS.md and the side studies were recomputed (CHANGELOG).
- `market_size_loop.md`: premium products alone no longer carry Central past the membrane switch.

## 5. What is still weak

- Retail prices by grade are mostly from memory; the volumes are firmer than the prices. A row at $22–25 a kilo holding all salmon
  (about 1% of volume) would be as defensible as 0.4% at $35.
- The tables' base mixes meat and seafood, and seafood is under-weighted in the Global table (9% of volume; by edible weight it is
  nearer a fifth). That was not changed here.
- Judgement: that sushi-grade seafood at $30 a kilo or more is under 2.5 Mt a year: about 0.9. That prime and wagyu beef at $45 or more
  is under 0.9 Mt: about 0.9.

## Sources

1. Mowi/Kontali, Salmon Farming Industry Handbook 2025 (FT).
2. SalmonBusiness, "30% of Norwegian salmon never gets cooked", 2025 (FT).
3. OPRT sashimi-tuna figures via seafood.vasep.com.vn (FT, secondary); ISSF status of the stocks via Perishable News, 2025 (FT, secondary).
4. MLA Japan market snapshot, January 2025 (FT); Beef Central on the Australian Wagyu Association survey (FT).
5. Réussir on Label Rouge poultry, 2025 (FT); WATT and FranceAgriMer on organic chicken (SNIP).
6. FAO Food Outlook, November 2025; FAO SOFIA 2024 (SNIP).
