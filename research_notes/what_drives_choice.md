# What drives shoppers' choice, and whether "share at equal price" is the right dial

Date: 2026-11-19. A bounded literature review (about 47 tool calls) by a search agent. Access tags: FT full text, PART partly read,
SNIP search snippet or abstract only. Van Loo and Haghani were read directly from the PDF text; other FT items came through a
fetch tool's summariser, so check any number against its source before it becomes a calibration target. No model input is changed
by this note.

**In short.** "Share at equal price" is a recognised summary: Slade 2018 and Van Loo et al. 2020 both report exactly that. One
documented dial is adequate. But the review's median for the long-run value is about 10%, a little under the model's 13%; 5% is too
high to be the bottom of the range; and 55% is about a 98th-percentile case. There is still no usable sales evidence for
cultivated meat. Two structural changes would add realism: shoppers who never buy at any price, and a split of the long-run share
into trying and buying again.

## 1. What people weigh, ranked by evidence

| Rank | Factor | Evidence | Kind |
|---|---|---|---|
| 1 | Taste, and buying again after trying | Meat Demand Monitor: taste, freshness, price and safety are the top four every month; taste in the top four for 56%, price for 50% (Oct 2025) [SNIP]. Lapsed plant-based buyers: 40% taste or texture, 37% too expensive (GFI 2025) [SNIP]; Mintel 2023 (n≈1,400): taste 48%, "meat is better nutrition" 35%, too expensive 34%, texture 24%, too processed 21% [SNIP] | stated reasons, backed by observed lapsing |
| 2 | Price | Real but not sufficient. In Van Loo, beef keeps a majority even with 50% price cuts on the alternatives [FT]. Carlsson, Kataria & Lampi 2022 (Sweden): "almost half" would not choose a lab burger "even if" free [SNIP] | stated |
| 3 | Naturalness, disgust, wariness of food technology, trust | Siegrist & Hartmann 2020 (n=6,128, 10 countries): naturalness and disgust matter in every country; France least accepting, Mexico most [SNIP]. Bryant & Barnett 2020 (26 studies): unnaturalness the lead barrier, then safety, disgust, neophobia, distrust [PART] | stated only |
| 4 | Familiarity, habit, availability | Onwezen et al. 2021 (91 articles): familiarity, neophobia, disgust and social norms recur; cultured meat second-lowest, above insects [SNIP]. In Van Loo, 44% had never heard of lab-grown meat [FT] | stated |
| 5 | Name and information | Small to moderate. Van Loo: information moved lab-grown from 4% to 6–7%; brands did nothing for it [FT]. Tufts 2026: "cultivated" beats "lab-grown" by up to $1.97 in willingness to pay (US) [SNIP]. Van Loo's 5% was measured under the least favourable name | stated |
| 6 | Animal welfare, environment | Weak for the mainstream: about 50% more shoppers put environment in their bottom four than their top four [SNIP]. They matter for meat reducers | stated, consistent with sales |
| 7 | Demographics | Weak. Van Loo Table 6: vegetarian +4.3 points, female −2.4, college +1.6, age −0.3 a year, income not significant, R² 0.02 [FT] | stated |
| 8 | Country | Large. China and India above the US (Bryant & Barnett) [PART]. EIT Food 2025: willing to try 39% under 35, 18% at 55 and over [SNIP]. Would try: Italy 47%, Portugal 53%, Spain 56% (Euroconsumers) [SNIP] | stated |

Against stated intent as a guide: Slade 2018 told respondents all burgers tasted the same, and 92% did not believe it [SNIP].

## 2. What predicted plant-based meat's outcome

- **Size (US, 2025):** $1.0B, down 10%; 0.7% of all meat dollars, 1.4% of packaged meat. Households buying: 11%, from a 20% peak
  in 2021. Repeat rate "over 60%". Price still more than double. The decline came from households leaving (GFI) [FT].
- **Trying and buying again (scanner data):** Neuhofer & Lusk 2022 (38,966 households, 2018–20): 19.9% ever bought; 60% of them
  bought again; 86% also bought ground meat, and their ground-meat spending did not fall [FT]. Cuffey et al. 2023: 68% never, 11%
  once, about 20% more than once; spending falls over 75% after the first month [SNIP]. Sun, Caputo & Taylor 2025 (127,981
  households, 2022): 7.3% bought; 38% of them on one trip only, 76% on five or fewer [FT].
- **Near price parity, in the field:** Malan et al. 2022 (UCLA dining halls): Impossible took 26% at the burrito station, mostly
  from the vegetarian option; beef dishes fell 2.1–4.0 points. Burger King about 15% of burger sales at launch, then declining;
  IKEA 8%; Del Taco 6% to 4% (via Peacock 2023) [FT].
- **Stated against observed:** Van Loo put plant-based at 23% at equal price [FT]. The realised peak was roughly 6–8% of
  ground-meat spending in 2020 and has fallen a third or more since (denominators not matched). A good choice experiment on the
  closest analogue overstated by roughly 2–3×.
- **Does a kilo of plant-based meat sold replace a kilo of meat? (added 2026-11-22):** Winslow, Peacock, Dhargawe, Sherman, Green
  & Mathur 2026 ("New alternatives, same orders", SocArXiv, doi:10.31235/osf.io/tpyk9_v1): 1.2 million US and Canadian restaurant
  transactions, 2016-23; plant-based meats took 1-9% of orders at a $1-2.50 premium, and meat orders did not measurably fall
  (pooled about -1%, range -15% to +16%; also within customers) [ABS]. Hope, Green, Peacock & Mathur 2026 (Food Quality and
  Preference 143:105931): a randomised online menu, 4,431 US adults; adding Sofritas and a chicken-style plant-based meat priced
  like chicken cut meat orders by 2.1 points (95% CI -4.4 to +0.1; Sofritas alone -1.1), most of the new options' orders coming
  from the vegetarian option; a fall of 5 points or more was ruled out [ABS]. Grocery: Cuffey et al. 2023, Neuhofer & Lusk 2022,
  Meyer et al. 2024 find plant-based sales without a detectable fall in meat bought; Peacock 2026 (Appetite 216:108301) reviews
  them. The model uses this twice: the menu check (`demand_checks.md` section 8) and the range of `meat_displaced_per_kg`
  (not carried over to cultivated meat, which is meat).
- **Taste:** NECTAR 2025 (122 products): only 20 were rated the same or better than meat by at least half of tasters [SNIP].

What follows for cultivated meat: getting people to try is cheap. The ceiling is set by how many buy again and how often, and
that depends on taste. Cultivated meat's real-tissue advantage belongs in the buy-again term. "Too processed" was a secondary
reason for leaving plant-based (21%) but is the first barrier for cultivated meat.

## 3. Is the dial defensible, and what else is used

It is the standard summary of a choice experiment (Van Loo, following Lusk & Tonsor 2016), and it is the market-potential input
that an adoption curve needs, so a judgement is unavoidable.

- **Choice experiment with shoppers who differ, deflated for hypothetical bias.** Murphy et al. 2005: median stated-to-actual
  ratio 1.35 over 28 studies, strongly right-skewed [SNIP]; Penn & Hu 2018 (131 studies): "almost twofold" [SNIP]. Haghani et
  al. 2021: bias concentrates in total willingness to pay and in opting in, not in marginal trade-offs [PART]. The model's share is
  conditional on buying meat, which removes part of the inflation, not the part specific to a novel option.
- **Segments.** No cultivated-meat choice experiment was found that reports a rejecter class. Nearby evidence:

  | Source | Willing | Uncertain | Not willing | Tag |
  |---|---|---|---|---|
  | Netherlands (n=231) | 45.5% | 36.8% | 17.7% | FT |
  | UK (n=366) | 34.7% | 34.7% | 30.6% | FT |
  | France (n=484) | none | 41.5% | 58.5% | FT |
  | Spain (n=210) | none | 63.3% | 36.7% | FT |
  | Germany, trust profiles (n=1,099) | trusting 17.5%, optimistic 37.5% | sceptical 20.7% | distrustful 24.3% | SNIP |

  The first four are small convenience samples (Foods 11:197, 2022). In Van Loo, 53% value lab-grown below buying nothing [FT].
- **Trial-and-repeat models** (Parfitt-Collins, Fourt-Woodlock, ASSESSOR, BASES): share = trial × repeat × buying rate. They need
  a physical product or panel data; no published validation was found for a category that does not exist yet.
- **Analogues.** Plant milk: 13% of US milk dollars, 38% of households, 75% repeat, at over twice the price [FT, GFI]. Cage-free
  eggs: votes for bans ran 15–20 points above purchase shares (Lusk) [SNIP]. Outcomes look two-humped and are partly set by
  retailers and regulators.

Best practice for a category that does not exist is to triangulate: a deflated choice experiment, a reference-class prior, and a
trial-and-repeat breakdown updated as sales arrive.

## 4. Numbers for calibration

- **Try against regular use (US):** Wilks & Phillips 2017: 65% would try; about a third would eat it regularly [SNIP].
- **Stated shares at equal price:** Van Loo (N=1,830; 461 in the control): lab-grown 5% of buyers, 4% of all, 6–7% with
  information; beef 72%. Slade (Canada): cultured 11%, plant-based 21%, beef 65% [SNIP].
- **Van Loo's spread of liking (control, relative to "none")** [FT]: lab-grown mean −0.25, sd 3.75 (3.6–4.6 across treatments);
  beef mean 7.33, sd 4.72; price −0.72 per $/lb. The covariances are restricted to zero, so the sd of lab-grown minus beef is
  about 6.0 and their correlation is assumed, not estimated. **To check:** that the model's `liking_sd` of 5 is in this scale.
- **After tasting:** Rolland et al. 2020 (n=193; both burgers were in fact conventional): 58% would pay a premium, 37% on
  average [SNIP]. Huber's, Singapore 2023 (107 diners): taste 4.2/5 [SNIP]. Both self-selected, both intent.
- **Observed cultivated-meat sales:** none usable. Only Wildtype, GOOD Meat and Vow had sustained sales in 2025 [SNIP].
- **Blends:** thin. ProVeg UK 2022 (n=1,000): 35% would probably or definitely buy a plant and cultivated hybrid, slightly below
  plant-based [SNIP]. No head-to-head experiment found.

## 5. The agent's recommendation

**(a) One dial is adequate** if the page says: it is the market potential of the adoption curve, a judgement; the measured 5% is
a stated choice among meat buyers, under the name "lab-grown", with no tasting; and it is the product of reach × buying again ×
share of purchases, with plant-based meat's values beside it.

**(b) Two structural changes.**
1. **Shoppers who never buy.** A normal spread of liking lets a low enough price win back everyone, against Carlsson and the
   cluster studies. Suggested long-run sizes (the agent's judgement): US and northern Europe 20–30%; France and Italy 35–50%;
   Singapore- or China-type markets 10–15%. Test first: price cultivated meat at half of conventional; if the model's share
   passes about 75%, the cap would bind.
2. **Trying × buying again.** Long-run share = availability × ever tried × buy again × share of purchases among those who do.
   Plant-based anchors: ever tried 20–32%, buy again 60–65%, about one purchase a month, 86% still buying meat. Tie cultivated
   meat's buy-again rate to the taste credit, so the per-tier authenticity offsets act there.

**(c) Long-run share at equal price** (taste parity, on every shelf, wariness faded, a US-like market; the agent's judgement, low
confidence):

| Percentile | 10th | 25th | 50th | 75th | 90th |
|---|---|---|---|---|---|
| Share | 2% | 5% | 10% | 20% | 35% |

P(below 5%) about 25%; P(above 49%) about 3%. Down: stated 5–11% deflated 2–3× gives 2–5%; a lasting block of rejecters;
plant-based products at parity quality still stalled; politics. Up: the worst name and 44% unaware in the base study; real tissue
removes the main reason people left plant-based; plant milk reached 13% at twice the price. Regions: about 5% for France and
Italy, 15–20% for Singapore- or China-type markets.

## Sources

[Van Loo et al. 2020](https://edepot.wur.nl/530803) · [Neuhofer & Lusk 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9336146/) ·
[Sun, Caputo & Taylor 2025](https://www.choicesmagazine.org/choices-magazine/submitted-articles/what-explains-the-recent-slowing-growth-of-the-plant-based-meat-alternatives-market) ·
[GFI market research](https://gfi.org/marketresearch/) ·
[Peacock 2023](https://rethinkpriorities.org/publications/price-taste-and-convenience-competitive-plant-based-meat-would-not-currently-replace-meat) ·
[Haghani et al. 2021](https://arxiv.org/pdf/2102.02940) · [Four-country clusters](https://pmc.ncbi.nlm.nih.gov/articles/PMC8774966) ·
[Lusk 2020](https://jaysonlusk.com/blog/2020/7/3/consumer-preferences-for-beef-alternatives) ·
[Bryant & Barnett 2020](https://doi.org/10.3390/app10155201) · [Carlsson et al. 2022](https://swopec.hhs.se/gunwpe/abs/gunwpe0798.htm) ·
[Slade 2018](https://pubmed.ncbi.nlm.nih.gov/29501683/) · [German trust profiles](https://pubmed.ncbi.nlm.nih.gov/40180288/) ·
[Rolland et al. 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7162467) ·
[Huber's study](https://goodmeat.co/all-news/first-ever-in-market-study-of-cultivated-meat-demonstrates-strong-acceptance) ·
[Mintel 2023](https://FoodNavigator.com/Article/2023/08/08/consumers-abandon-plant-based-meat-category-citing-taste-nutrition-price-concerns-mintel-reports) ·
[Meat Demand Monitor](https://agmanager.info/sites/default/files/pdf/MDM_Oct-2025.pdf) ·
[Tufts naming study](https://now.tufts.edu/2026/06/09/new-research-examines-how-naming-shapes-consumer-acceptance-cultivated-meat) ·
[Kantor & Kantor 2021](https://www.frontiersin.org/articles/10.3389/fsufs.2021.594650)
