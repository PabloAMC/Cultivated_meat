# World seafood prices, weighted by who eats the fish

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

Date: 2026-11-19. A bounded web search (38 tool calls) by a search agent, after the audit found that the world seafood rows carry
the model's headline (fillets were 39% of Central's sales) and came from no weighted source. Tags: FT full text, SNIP search
snippet, [conv] a conversion, [inference] a judgement, [recall] from memory and not re-verified. Exchange rates assumed: CNY 7.1,
IDR 16,500, BDT 122, INR 86, VND 26,000, JPY 150, EUR 1.12, BRL 5.45, NGN 1,500 per USD.

**In short.** The old rows averaged $13.6 a kilo over all seafood. Weighted by consumption it is about **$10 a kilo of edible
fish**. The one "fillet" row ($16 for 64% of seafood) hid two populations: a mass market near **$7** (whole fish and ordinary
fillets, most of it in Asia) and a premium tier near **$20** (salmon, shrimp, cod, tuna loins). Adopted 2026-11-19.

Not verified: GlobalProductPrices lists no fish, so the old rows cannot have been its cross-country mean; FAO SOFIA and the EUMOFA
report returned 403 (their figures are snippets); country weights are FAO per-capita times population from memory.

## 1. Retail prices where the fish is eaten

| Country (share of food fish) | Quoted | $/kg as sold [conv] | $/kg edible [conv] |
|---|---|---|---|
| China (~36%), grass carp | wholesale 16.4–18.2 yuan/kg (SunSirs, SNIP); market 10.89 yuan/500 g, Tianjin (FT) | 3.1 whole | 5.6–6.2 |
| China, silver / common / crucian carp | 5.95 / 8.33 / 12.58 yuan/500 g (Tianjin, FT) | 1.7 / 2.3 / 3.5 | 3.3 / 4.7 / 7 |
| China, hairtail | 14.02–17.75 yuan/500 g (SNIP) | 3.9–6.1 | 6–9 |
| China, shrimp | pond price 39 yuan/kg (Tridge, SNIP) | 5.5 at the farm; about 9–11 retail [inference] | 17–22 |
| Indonesia (~7%) | mackerel, tuna, milkfish Rp 35,000–43,000/kg (Bapanas, SNIP) | 2.1–2.6 | 3.6–4.7 |
| India (~8%) | rohu wholesale Rs 180–230/kg; basa fillet Rs 676/kg (SNIP) | 2.1–2.7 whole; 7.9 fillet | 4.5–6 |
| Bangladesh (~3%) | rui Tk 300–320, pangas Tk 180–235 (SNIP) | 1.2–2.6 | 2.5–5.2 |
| Japan (~3%) | tuna 513, yellowtail 472, salmon 328 yen/100 g (MAFF, Jan 2026, SNIP) | 22–34 | 22–34 |
| US (~4.5%) | all seafood $10.52/lb; fresh $10.02, frozen $7.58, shelf-stable $5.33 (Circana, SNIP) | 23.2; 22.1 / 16.7 / 11.8 | about the same |
| EU (~6%) | households spent €62.8bn in 2024 on 22.89 kg a head live weight (EUMOFA, SNIP) | €6.1/kg live weight | 14–18 |
| Nigeria (~1%) | mackerel N7,000–9,000/kg, Lagos (SNIP) | 4.7–6.0 | 8–10 |
| Brazil (~1%) | tilapia fillet R$32.22/kg wholesale (CEPEA, SNIP) | 5.9; about 9–11 retail [inference] | 9–11 |

Edible share taken as 50–60% for whole fish (in Asia head, skin and belly are eaten). Weighted: China 8.5, India 5.5, Indonesia 5,
EU 21, US 23, Japan 23, the rest about 8, gives **about $9.7 a kilo edible** [inference]. Top-down check: first-sale value about
$452bn for 185 Mt of animals [recall] is $2.7/kg live weight, $5.4 edible, $10–12 at a 1.8–2.2× retail markup [inference].

## 2. Product form

FAO (2022, SNIP): live, fresh or chilled 43%; frozen 35%; prepared and preserved 12%; cured 10%. Most fish in Asia and Africa
is sold whole or gutted; boneless fillet is mainly a rich-country and export form [inference]. Premium species by edible weight
[recall + inference]: salmonids about 2.8 Mt, shrimp 3.5–4.5, premium whitefish 1.3, non-canned tuna 0.8, crab and lobster 1.8,
premium cephalopods and marine finfish about 3: 13–14 Mt of about 84 Mt, 16%.

## 3. The rows adopted (`meat_market.GLOBAL_MARKET`)

| Row | Share of seafood | Share of the table | Low | Selected cells | High, $/kg edible |
|---|---|---|---|---|---|
| processed, canned, cured, minced | 27% | 0.0659 | 5 | **7** | 9 |
| mass-market whole fish and ordinary fillets | 55% | 0.1341 | 5 | **7** | 10 |
| premium fillets and shrimp | 16.4% | 0.0400 | 15 | **20** | 26 |
| sushi-grade (unchanged) | 1.6% | 0.0040 | | **35** | |

Before: canned $8 (34%), fillet $16 (64%), sushi $35 (1.6%). The mass-market row is sold bone-in while a cultivated product is
boneless; the boneless premium (Indian basa fillet $7.9 against about $5 edible-equivalent whole) is why its high end is $10.
Confidence: about 60% that the mass-market price lies in $5.5–9, and about 85% that it is below the old $16.

## 4. Regional tables

| Region | Fillet row before | Finding | Now |
|---|---|---|---|
| China | $14 | too high for a row with two-thirds of volume: carp $3–7, hairtail $6–9, only shrimp at $17 or more | $9 |
| EU | $28 | households' own spend gives $14–18 for all seafood, against the table's $24.6 average | $21 |
| India | $8 | matches boneless basa; high for bone-in rohu ($4.5–6) | $6 |
| US | $24 | fresh and frozen blend to $19–22; all seafood $23.2; the table averages $21.9 | unchanged |
| Brazil, Nigeria | $12, $10 | plausible | unchanged |

## Sources

- Tianjin and Xinyang market monitors: https://www.itiger.com/news/1143673626 ; SunSirs: https://www.sunsirs.com/uk/detail_news-29430.html
- Indonesia (Bapanas via Bisnis): https://ekonomi.bisnis.com/read/20251008/12/1918434/harga-pangan-hari-ini-810-beras-turun-tipis-ikan-naik
- Bangladesh: https://bdnews24.com/bangladesh/8bc1c2642914
- US (Circana via SeafoodSource): https://www.seafoodsource.com/news/foodservice-retail/us-seafood-inflation-spiked-at-grocery-stores-to-end-2025
- EU (EUMOFA 2025): https://eumofa.eu/-the-eu-fish-market-2025-edition-is-online
- FAO SOFIA 2024: https://www.fao.org/newsroom/detail/fao-report-global-fisheries-and-aquaculture-production-reaches-a-new-record-high/en
- Nigeria: https://nairametrics.com/2026/11/01/lagos-food-prices-maize-ogbono-and-garri-record-sharp-increases-in-october/
- Brazil (CEPEA): https://cepea.org.br/br/tilapia-cepea/tilapia-cepea-baixa-oferta-mantem-preco-da-tilapia-em-alta.aspx
- Japan (MAFF): https://www.maff.go.jp/j/zyukyu/anpo/kouri/k_gyuniku/fish/attach/pdf/index-49.pdf
