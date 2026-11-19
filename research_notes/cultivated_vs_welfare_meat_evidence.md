# Cultivated meat vs premium welfare-labelled meat: sizing three differences

> Names (2026-11-19): "Selected cells" was called Central; "Engineered cells, all favourable" was called the best case.

Compiled 2026-11-17 from web sources.

**Purpose.** The demand curve is being re-anchored on premium real meats ("real meat plus a virtue, at a
premium": organic, free-range, slow-growth or higher-welfare chicken; see `premium_meat_analogues.md`) and
then shifted for cultivated meat by what differs. This note sizes three differences, each as a
willingness-to-pay (WTP) difference relative to a welfare-labelled product:

1. no animal is killed (up);
2. novelty (down, likely to fade), which maps to `neophobia_x` in `market_share.py`;
3. "unnatural" (down, possibly persistent), which maps to the authenticity `tier_offset`.

In a logit, Δu = |β_price| × ΔWTP. A small share is multiplied by about e^Δu. WTP is quoted below as a
fraction of the conventional price, so the model's own price coefficient converts it
(Δu ≈ |β|·p_ref·(ΔWTP/p_ref)). The Van Loo-scale conversions are reported as that experiment's own units
and do not transfer to the model.

**Conventions**
- **Access:** FT = full text read; AB = abstract, summary page or press summary of the paper; SN = search
  snippet only; **memory** = from my prior knowledge, not checked this session.
- "Derived" means I computed it from published numbers, and the arithmetic is shown.
- Already in `premium_meat_analogues.md` or METHODS.md and not repeated here: Van Loo, Caputo & Lusk 2020
  as the elasticity source (its WTP and share results ARE used below for a different purpose), and the
  premium-product shares and elasticities.
- **A caveat that applies to every stated-preference row:** these are hypothetical choices. Stated welfare
  premiums (15–45%) sit far above the revealed ones: organic chicken holds about 2.4–4.6% of volume at
  1.4–2.6×. Clark et al. 2017 also find publication bias in welfare WTP. Compare products **within** a
  design (cultured against conventional, or label against no label), not one study's levels against
  another's.

---

## 0. The net gap at first contact (all three differences together)

These designs price cultured meat against conventional meat for the same respondents. Their net penalty is
the sum of no-slaughter (+), novelty (−), unnaturalness (−) and expected taste and safety doubts (−).

| Source | Design | Quantity | Framing | Access |
|---|---|---|---|---|
| Van Loo, Caputo & Lusk 2020, *Food Policy* | US; N = 1,830; Dec 2018 – Jan 2019; hypothetical labelled DCE, burger patties at $2.99–10.49/lb; random-parameter logit (RPL); 4 information arms | Lab-grown ASC mean −0.25 (SD 3.75) vs beef 7.33 (SD 4.72); price coefficient −0.72/$ (control, Table 3). 47% hold a positive value for lab-grown, against 94% for beef (Table 4). Mean WTP vs "none": lab −$0.34/lb, beef $10.18/lb (Table 5). Unconditional shares with every product at $5/lb: beef 63%, lab 4% (Fig. 3A); conditional: 72% vs 5%. **Derived:** ln(5/72) = −2.67 utils = −$3.7/lb at 0.72/$, about **−74% of price** | "Lab-grown"; Memphis Meats brand in one arm | FT |
| Van Loo et al. 2020, information arms | same | Lab-grown WTP vs none: control −$0.34, brand +$0.33, sustainability info +$0.86, technology info +$0.32 per lb. Share with a positive value: 47% → 56% with sustainability info. Unconditional share 4% → 6–7% | Environmental and technology text | FT |
| Slade 2018, *Appetite* (as cited in Van Loo 2020) | Canada; hypothetical DCE; all burgers at $4 | Shares: beef 65–67%, plant-based 21%, cultured 11% (Van Loo quotes both 65 and 67). **Derived:** Δu = ln(11/67) = −1.8 | "Cultured" | FT (secondary, within Van Loo) |
| Yang, Min, Nguyen & Qing 2024, *Front. Sustain. Food Syst.* | China, 5 cities; N = 998; Oct 2020; online DCE with cheap talk; beef burger at ¥27/30/33; RPL | WTP vs farm-raised, ¥ per burger: cultured −21.5 [−29.7, −13.3] pooled; −35.9 with no information; −13.7 with positive information. Plant-based −17.8 pooled. **Derived:** about −72% of the ¥30 mid price pooled, −120% uninformed, −46% informed | "Cultured meat" | FT |
| Asioli et al. 2022, *Food Policy* 112 | UK, Spain, France; N = 648; hypothetical DCE; attributes: production method, carbon label, antibiotics, price | Spain and France reject cultured beef burger on average; UK more positive. Segment paying a premium: UK 47% (£5.10/kg), Spain 38% (€3.35/kg), France 30% (€2.68/kg) | "Cultured beef" | SN |
| Escribano, Gaspar & Mesías 2021, *Sustainability* | Spain; N = 444; DCE | Negative WTP for plant-based and cultured vs conventional, most negative for cultured; only 1 of 3 clusters shows some acceptance | — | SN |
| Yuan et al. 2025/26, *JAAEA* (working-paper version AAEA 2021) | China, multiple cities; N = 571; DCE, cultured chicken | No premium for cultured chicken on average; information raised WTP by ¥8.66 per 500 g. The 2021 version reported a premium, so the two versions conflict | Information treatments | SN |
| Kantor & Kantor 2021, *Front. Sustain. Food Syst.* | US; N = 300 (Prolific); 2020–21; slider WTP anchored on a $1 conventional patty | Cultured: $2.10 under the environmental framing (its text includes "no cows are killed"); $2.66 under the "best burger" framing | Framed as equal in taste: the authors call it gold-standard bias | FT |
| Purdue Consumer Food Insights, Mar 2024 | US; N ≈ 1,200 | Willing to try: about 90%+ for conventional meats, about 60% for cultivated (about 30 pp lower) | "Cultivated" | SN / AB (press release) |

**Reading.** The first-contact net gap against conventional meat, in hypothetical designs, is about
**−50% to −120% of price, central −70%**. On Van Loo's scale this is about −2.7 utils at equal price;
Slade gives about −1.8. Before the curve is shifted, this needs splitting into the three components below
plus expected-taste doubts. Taste is already a separate model dial, so the CE penalty must not be applied
whole.

---

## 1. No animal is killed (up)

| Source | Design | Quantity | Framing | Access |
|---|---|---|---|---|
| Lusk 2018, report for FFAR / *Poultry Sci.* (slow-growth chicken) | US; N = 2,049; late 2017; hypothetical DCE on chicken breast at $1.99–5.99/lb; labels: organic, no antibiotics ever, no hormones, non-GMO, slow growth; latent-class logit | Mean WTP premiums, control (no information): slow growth **$0.58/lb** (median 0.61); organic **$1.38–1.87/lb** (with or without brands; the text and the table header disagree on which is which). Pro-slow-growth information (NPR/NYT): slow growth $2.11–2.44; anti (NCC): $0.24–0.43 (Table 9). At a $0.50 premium against unlabelled breast, slow growth is chosen by 45% (control), 54% (pro) and 41% (anti). **Derived:** against the $3.99 mid price, slow growth ≈ +15%, organic ≈ +35–47% | Welfare label invented for the study; low awareness (1.2% had heard of it) | FT |
| Clark, Stewart, Panzone, Kyriazakis & Frewer 2017, *Food Policy* 68 | Meta-analysis of 54 WTP studies | Small positive WTP for farm-animal welfare, standardised effect 0.63 SD; varies by species and region. A companion paper (*Animals* 2017) finds publication bias, so WTP is overstated | — | AB |
| Lagerkvist & Hess 2011, *ERAE* 38(1) | Meta-analysis, 24 studies, 106 estimates | WTP rises with income; information on living conditions shifts it; framing welfare as a legal requirement lowers stated WTP. No pooled % premium retrieved | — | AB |
| Experimental auction, *Animals* 2023 13(21):3367 | Netherlands; N = 101 students; real-money auction | Certified free-range chicken (innovative husbandry): **+13.2%** over conventional | Marketing information arms | SN |
| Cornelissen & Piqueras-Fiszman 2022, *J. Food Sci.* | Netherlands; N = 288 (press says 323); five patty types rated | Cultured meat rated high on **ethical, animal-friendly**, sustainable and interesting; low on safe and natural; healthiness comparable to meat | Within-subject comparison with meat, plant-based, fish, insects | SN |
| GFI / Morning Consult 2025 | US; N = 1,067; June 2025 | "Real meat grown from animal cells, without harming animals": 54% find it believable, 45% say it makes them more likely to try. Claims about antibiotics and disease risk do slightly better (46–47%). In a highlighting task, "no kill / without harming / more humane" is rated appealing, but **"slaughter" is unappealing even when it appears as "not slaughtered"** (Oct 2024, N = 3,517). Non-meat-eaters are 5% of likely triers, against 4% of the population: not over-represented | Positive description supplied | FT |
| Wilks & Phillips 2017, *PLOS ONE* | US MTurk; N = 673; 2016 | 65% would try, about 1/3 would eat regularly; vegetarians and vegans see more benefits but are **less** willing to try | — | SN |
| EIT Food Consumer Observatory factsheet 2025 | Review of European studies | Prosocial motives (animal welfare, sustainability) play a "secondary role" for omnivores; omnivores currently see **organic meat** as the best source of responsible meat; being a locavore inhibits willingness to pay a premium for cultured meat | — | FT |
| Reithmayer, Danne & Mußhoff 2019/2021 (DARE DP 1907; *Poultry Sci.*); BFJ 2020 | Germany; N = 482 and 526; hypothetical DCEs on eggs | A "no killing" attribute on a real animal product: in-ovo sexing is preferred to culling male chicks, but a high error rate or no use for the screened eggs removes any positive WTP; about 11% reject both options | Pictures raise the preference | AB |

**What it implies.** For the mainstream shopper, the welfare virtue is worth roughly **+15% of price**
stated against a pure welfare label (slow-growth, free-range: Lusk +15%, Dutch auction +13%). Organic's
+35–47% bundles health and naturalness, so it is not a pure welfare benefit. Shoppers do credit cultivated
meat as more animal-friendly (Cornelissen; GFI). There is no evidence that "no slaughter" is valued
**much more** than "better life":

- the claim performs like the health claims (GFI);
- the word "slaughter" backfires even when negated;
- the people who care most about animals (vegetarians) are not more willing to eat it;
- the one "no killing" analogue (in-ovo sexing) shows a modest, conditional premium;
- information arms that included animal or environmental benefits added about +24% of price in Van Loo
  ($1.20/lb on $5) and about +74% in Yang 2024. Both treatments also reduce unfamiliarity, so they bound
  the virtue from above rather than measure it.

**Shift relative to a pure welfare-labelled product: central +5% of conventional price, range −5% to +20%.**
Relative to **organic**, the virtue difference is about zero, and organic's health and naturalness halo
shows up as an extra negative in section 3.

- P(the sign is positive vs a free-range or slow-growth label) ≈ **0.65**.
- P(the difference persists in the long run, given that it exists) ≈ **0.8**: it is a real attribute,
  although its salience may fall.

---

## 2. Novelty (down, likely to fade)

| Source | Design | Quantity | Framing | Access |
|---|---|---|---|---|
| Rolland, Markus & Post 2020, *PLOS ONE* | Netherlands (Limburg); N = 193; Jun–Aug 2017; **real tasting** of two identical conventional burgers, one labelled "cultured"; 3 positive-information arms; hypothetical WTP | Acceptance score (range 3–15) before information 10.14–10.69 → after information 11.17–11.75 → after tasting 11.98–12.36 (SD about 2.0–2.8): **+1.7 to +1.8 points, about 0.7 SD**. The "cultured"-labelled sample was liked more (F = 4.26, p = 0.04). 58% would pay a premium, averaging 37% (€0.37 on €1.00). Information content did not matter | Positive information only; Post co-founded Mosa Meat; respondents were older (mean age 56) | FT (via Europe PMC) |
| Chong, Leung & Fernandez 2024, *Future Foods* 9 | Singapore, Huber's Butchery; N = 107 paying diners; Apr–Jun 2023; 88% first-time tasters; **real purchase** | Acceptance before eating 4.19/5, "significantly" higher after; would eat again 4.41/5; flavour 4.21. Deterrents: high markup 63.5%, safety 33%, flavour 30% | Self-selected diners | SN / AB (press reports of the paper) |
| Bryant & Sanctorum 2021, *Appetite* 161 | Belgium; two cross-sections, N = 1,001 (2019) and 1,000 (2020); representative | No significant change in cultured-meat attitudes; **39.3% would buy in both years**. Plant-based attitudes improved | — | SN |
| GFI / Morning Consult, US snapshots 2024 and 2025 | US; N = 1,067 (June 2025); repeated annually | Appealing: 18% (top-2 of 5); likely to try a free sample: 30% top-2 (59% at least somewhat); likely to buy: 19% top-2 (44% at least somewhat). **"Did not change significantly from 2024."** Awareness under 50%. Net perceptions against conventional meat: natural −35, tasty −30, understand what's in it −29, safe −17, healthy −11, environment +10 | Positive description supplied | FT |
| AP-NORC, Feb 2023 | US; N = 1,247; AmeriSpeak probability panel | 18% extremely or very likely to try, 30% somewhat, 50% not interested; most of the uninterested say it "just sounds weird", nearly half worry about safety | "Cell-based / lab-grown" | AB |
| Yu et al. 2025, *Trends Food Sci. Technol.* (meta-analysis) | 48 articles to Aug 2024; random-effects meta-analysis of correlations | Familiarity has a **small positive** effect on willingness to consume; publication year moderates (more recent studies show more acceptance); only one longitudinal sample in the literature | — | SN |
| Van Loo et al. 2020 (information arms) | as above | Information adds +$0.66 to +$1.20/lb (13–24% of price) to lab-grown WTP; conditional shares barely move (lab-grown 4–7%) | — | FT |
| Yang et al. 2024 (information arm) | as above | Positive information cuts the cultured WTP gap from −¥35.9 to −¥13.7 per burger (from −120% to −46% of price) | — | FT |
| Deloitte 2023 (plant-based meat, the cautionary analogue) | US; N = 2,000 consumers plus 100 grocery executives | Plant-based meat unit volume −17% and dollar sales −11% in the year despite an 8% price rise; limited pool of repeat buyers; falling health perceptions; about half of occasional buyers see it as superior | Trial does not guarantee repeat | SN |

**What it implies.** Information and tasting reliably cut first-contact aversion in experiments:
0.7 SD in Rolland, and a halved WTP gap in Yang. Familiarity correlates weakly with acceptance (Yu 2025).
But **no population-level fade has yet been observed**: Belgium 2019→2020 was flat and the US 2024→2025
was flat. AP-NORC 2023 and YouGov 2024 put rejection at about 50%. Exposure so far has been
media-only, so the experimental fade has not yet been tested on a population. Plant-based meat shows that
trial driven by novelty can reverse once taste disappoints. That is a taste effect, which the model carries
separately.

**Split of the first-contact gap.** Of the about −70% net gap in section 0, the fading parts are the reasons
GFI rejecters give: doubts about taste or texture (29%), "don't understand what's in it" (22%), unsafe
(20%), "wait until others have tried it" (10%), and part of "no reason to eat it" (28%). These are roughly
60% of the substantive reasons; "unnatural" (41%) and "rather support farmers" (32%) are the persistent ones.

**Novelty penalty relative to a welfare-labelled product (which has none): central −30% of conventional
price at first contact, range −15% to −60%.** This excludes the expected-taste part if the model's taste dial
already carries it; include about −10% more if it does not.

- P(the sign is negative) ≈ **0.97**.
- P(at least half of it fades within about 10 years of broad retail availability) ≈ **0.55**.
- P(it fades almost fully) ≈ **0.3**.

The fade evidence is experimental, not population-level, and cultivated meat has become politically
polarised in the US. *Memory, not checked this session:* Florida and Alabama banned its sale in 2024.

---

## 3. "Unnatural" (down, possibly persistent)

| Source | Design | Quantity | Framing | Access |
|---|---|---|---|---|
| Siegrist & Hartmann 2020, *Appetite* 155:104814 | 10 countries (AU, CN, UK, FR, DE, MX, ZA, ES, SE, US); N = 6,128 | Perceived naturalness and disgust are important predictors of acceptance in **every** country; acceptance highest in Mexico, lowest in France | — | AB |
| Siegrist, Sütterlin & Hartmann 2018, *Meat Science* | Switzerland; experiments | Cultured meat has low acceptance because it is perceived as unnatural; information about its production and benefits **raised acceptance of conventional meat** | — | SN |
| Anderson & Bryant 2018 (Faunalytics), pre-registered | US; N = 1,185 (Ipsos, census-balanced); 2018 | 66% agree "it is important for meat to be natural" (9% disagree); 34% agree "clean meat is unnatural" (34% disagree). Messages that clean meat is natural, or that naturalness doesn't matter, **did not beat the control**. Only "conventional meat is unnatural" raised WTP (chicken and fish, marginally) | 4 message arms | AB (the study's summary page) |
| GFI / Morning Consult 2025 | US; N = 1,067 | Net "natural" score against conventional −35, the largest gap; "minimally processed" −17. Among rejecters (n = 315): "not natural" 41% (top reason), "rather support farmers" 32% | — | FT |
| YouGov US daily poll, 29 May 2024 | US; N = 9,272 | Asked to imagine lab-grown meat **identical in taste, nutrition and cost**, 50% still prefer animal meat (68% of Republicans) | Isolates the non-taste, non-price residual | SN |
| "Is cultured meat a promising consumer alternative?" (*Appetite* 2022; authors not verified, possibly the Hocquette group) | 10 countries; N = 3,091 | Food neophobia, being a locavore and concern about food technology inhibit willingness to try, buy and pay a premium | — | SN |
| **GM foods.** Lusk, Jamal, Kurlander, Roucan & Taulman 2005, *JARE* 30(1) | Meta-analysis, 25 studies, 57 estimates | Premium for non-GM food of almost 29% (outlier excluded; figure from a citing review) | — | SN |
| GM foods: Hess, Lagerkvist, Redekop & Pakseresht 2016, *ERAE* 43(5) | Meta-survey, 214 studies, 1,713 questions, 58 countries | Stated benefits give no significant positive reaction; price discounts and perceived risks lower evaluation; after controlling for question type, the EU is no more averse than elsewhere | — | AB |
| GM foods, US trend: Pew Research 2016 and 2018 | US representative | "GM foods worse for health": **39% (2016) → 49% (2018)**, up 23 pp among low-science-knowledge respondents; unchanged among high-knowledge ones | — | SN |
| GM foods, EU trend: Eurobarometer | EU | Concern about GM ingredients 63% (2005), 66% (2010) → 27% (2019), but the 2019 format (pick from a list) is not comparable to earlier ones. GM-labelled food is still nearly absent from EU shelves (memory) | — | SN |
| **Irradiation.** Fox, Hayes & Shogren 2002; He, Fletcher & Rimal (about 2005) | US; experimental auctions and surveys | Consumer resistance to irradiation "very strong"; information improves acceptance only to a limited degree; beef suppliers trialled irradiated ground beef but promotion made little progress. *Memory:* FDA approved irradiation of red meat in 1997; irradiated ground beef stayed niche; the main processor, SureBeam, went bankrupt around 2004 | — | SN / memory |
| **Microwave ovens** | US history (The Henry Ford) | Fears of radiation leakage slowed adoption; standards in 1971 eased them; by 1986 a quarter of US households owned one, about 90% by the early 2000s | Large private convenience benefit | SN |
| **Pasteurisation** | Canada and US history | Early resistance from farmers and consumers; more than 90% of Canadian milk pasteurised by 1964; a raw-milk niche persists | Safety benefit, then mandates | SN |
| **Plant-based meat, "ultra-processed" image** | Deloitte 2023; GFI 2024 sales | Falling health perceptions and an "ultra-processed" image are named drivers of the 2022–24 decline (US plant-based sales −4% in 2024) | Industry analysis | SN |

**What it implies.** Naturalness is the most consistently measured barrier: it predicts rejection in every
country and is the top stated reason. It also resists counter-messaging (Anderson & Bryant; Siegrist 2018
backfire). YouGov's "identical in taste, nutrition and cost" item suggests a large residual that is neither
taste nor price.

The analogues split by whether the technology gave the **consumer** a large private benefit:

- **faded:** microwave ovens (convenience) and pasteurisation (safety, then mandates);
- **persisted for decades:** GM foods (US concern rose in 2016–18) and irradiation (about 30 years niche).
  Both offered mainly producer-side or credence benefits.

At price and taste parity, cultivated meat's benefits to the consumer are credence ones (ethics,
environment, antibiotics), so it resembles GM and irradiation more than microwave ovens. Relative to a
**welfare-labelled** product the gap is wider than relative to conventional meat, because free-range and
especially organic carry a naturalness **bonus**.

**Persistent "unnatural" shift: central −20% of conventional price vs a free-range or slow-growth product,
range −5% to −45%.** Against organic (naturalness plus health halo), use about −30%. Relative to
conventional meat alone it is about −15%.

- P(the sign is negative) ≈ **0.9**.
- P(at least half of it persists in the long run, 20+ years) ≈ **0.6**.

Two cautions. A US majority of 66% says meat should be natural while only 34% call cultivated meat
unnatural, so the penalty is concentrated in a minority with strong views, which a single logit constant
represents poorly. Second, naming and framing move it (avoid "lab-grown").

---

## Summary for the model

| Difference | Selected cells (fraction of conventional price, vs a free-range or slow-growth label) | Range | P(sign right) | P(persists long run) | Model dial |
|---|---|---|---|---|---|
| No slaughter | +0.05 | −0.05 to +0.20 | 0.65 | 0.8 | `w_slaughter` (mainstream) |
| Novelty (first contact) | −0.30 | −0.15 to −0.60 | 0.97 | about 0.45 (at least half gone in about 10 years: 0.55) | `neophobia_x` |
| Unnatural | −0.20 (−0.30 vs organic) | −0.05 to −0.45 | 0.9 | 0.6 | `tier_offset` (authenticity) |
| Net at first contact (excluding the taste dial) | about −0.45 | −0.2 to −0.9 | — | — | cross-check: the CE net gap of −0.5 to −1.2 includes expected taste and the welfare label's own +0.15 |

Convert with Δu = |β_price|·p_ref·(fraction). All magnitudes come from hypothetical designs, whose WTP
levels are inflated. The **ratios** between components are better supported than their levels.

---

## Sources

1. Van Loo, E.J., Caputo, V., Lusk, J.L. (2020). Consumer preferences for farm-raised meat, lab-grown meat, and plant-based meat alternatives: Does information or brand matter? *Food Policy* 95:101931. https://edepot.wur.nl/530803 (FT)
2. Slade, P. (2018). If you build it, will they eat it? Consumer preferences for plant-based and cultured meat burgers. *Appetite* 125:428–437. Cited in [1] (FT secondary).
3. Yang, M., Min, S., Nguyen, T.T., Qing, P. (2024). Promoting artificial meat to improve food security and reduce resource-environment pressure: is it practicable in China? *Front. Sustain. Food Syst.* 8. https://frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2024.1488747/full (FT)
4. Asioli, D., et al. (2022). Consumers' valuation of cultured beef burger: A multi-country investigation using choice experiments. *Food Policy* 112:102376. https://ideas.repec.org/a/eee/jfpoli/v112y2022ics0306919222001452.html (SN)
5. Escribano, A.J., Peña, M.B., Díaz-Caro, C., Elghannam, A., Crespo-Cebada, E., Mesías, F.J. (2021). Stated preferences for plant-based and cultured meat: A choice experiment study of Spanish consumers. *Sustainability* 13(15):8235. https://dx.doi.org/10.3390/su13158235 (SN; author list from memory)
6. Yuan, et al. (2025/26). Consumers' valuation for cultured meat: A multi-city choice experiment in China. *JAAEA*. https://onlinelibrary.wiley.com/doi/10.1002/jaa2.70028 ; working paper https://ideas.repec.org/p/ags/aaea21/313957.html (SN)
7. Kantor, B.N., Kantor, J. (2021). Public attitudes and willingness to pay for cultured meat. *Front. Sustain. Food Syst.* 5:594650. https://frontiersin.org/journals/sustainable-food-systems/articles/10.3389/fsufs.2021.594650/full (FT)
8. Purdue Consumer Food Insights, cultivated meat survey (March 2024). https://purdue.edu/newsroom/2024/Q2/survey-tallies-consumer-attitudes-toward-lab-grown-meat-alternatives (SN / AB)
9. Lusk, J.L. (2018). Consumer beliefs, knowledge, and willingness-to-pay for sustainability-related poultry production practices (slow-growth chicken), report; published as Lusk (2018) *Poultry Science*. https://foundationfar.org/wp-content/uploads/2021/03/Lusk-report_broiler_Jan-2018.pdf (FT); blog https://jaysonlusk.com/blog/2018/8/20/slow-growth-chicken-what-do-consumers-think
10. Clark, B., Stewart, G.B., Panzone, L.A., Kyriazakis, I., Frewer, L.J. (2017). Citizens, consumers and farm animal welfare: A meta-analysis of willingness-to-pay studies. *Food Policy* 68:112–127. https://econpapers.repec.org/RePEc:eee:jfpoli:v:68:y:2017:i:c:p:112-127 (AB)
11. Lagerkvist, C.J., Hess, S. (2011). A meta-analysis of consumer willingness to pay for farm animal welfare. *ERAE* 38(1):55–78. https://ideas.repec.org/a/oup/erevae/v38y2011i1p55-78.html (AB)
12. Can marketing increase willingness to pay for welfare-enhanced chicken meat? Evidence from experimental auctions. *Animals* 13(21):3367 (2023). https://www.mdpi.com/2076-2615/13/21/3367 (SN)
13. Cornelissen, K., Piqueras-Fiszman, B. (2022). Consumers' perception of cultured meat relative to other meat alternatives and meat itself: A segmentation study. *J. Food Sci.* doi:10.1111/1750-3841.16372. https://edepot.wur.nl/582508 (SN)
14. GFI / Morning Consult (2025). U.S. consumer snapshot: Cultivated meat 2025. https://gfi.org/wp-content/uploads/2026/02/U.S.-consumer-snapshot-Cultivated-meat.pdf (FT)
15. Wilks, M., Phillips, C.J.C. (2017). Attitudes to in vitro meat: A survey of potential consumers in the United States. *PLOS ONE* 12(2):e0171904. (SN)
16. EIT Food Consumer Observatory (2025). Cultured Meat factsheet. https://www.eitfood.eu/files/EIT-Food-Consumer-Observatory_Cultured-Meat_Factsheets_V4_2025-05.pdf (FT)
17. Reithmayer, C., Danne, M., Mußhoff, O. (2019). Look at that! The effect pictures have on consumer preferences for in ovo gender determination as an alternative to culling male chicks. DARE DP 1907. https://ideas.repec.org/p/ags/gadadp/298419.html (AB); Reithmayer & Mußhoff, *British Food Journal* 2020 (SN)
18. Rolland, N.C.M., Markus, C.R., Post, M.J. (2020). The effect of information content on acceptance of cultured meat in a tasting context. *PLOS ONE* 15(4):e0231176. https://pmc.ncbi.nlm.nih.gov/articles/PMC7162467 (FT via Europe PMC)
19. Chong, M., Leung, A., Fernandez, T.M. (2024). On-site sensory experience boosts acceptance of cultivated chicken. *Future Foods* 9. https://doaj.org/article/60556cf500ee4c298ee178ef8d4a8690 ; press summary https://www.greenqueen.com.hk/?p=71624 (SN / AB)
20. Bryant, C., Sanctorum, H. (2021). Alternative proteins, evolving attitudes: Comparing consumer attitudes to plant-based and cultured meat in Belgium in two consecutive years. *Appetite* 161. https://researchportal.bath.ac.uk/en/publications/alternative-proteins-evolving-attitudes-comparing-consumer-attitu/ (SN)
21. AP-NORC (2023). Few adults are interested in trying "lab-grown" meat. https://apnorc.org/?p=7717 (AB)
22. Yu, et al. (2025). Willingness to consume cultured meat: A meta-analysis. *Trends Food Sci. Technol.* https://www.researchgate.net/publication/395134195_Willingness_to_consume_cultured_meat_A_meta-analysis (SN)
23. Deloitte (2023). Plant-based meat consumer perceptions. https://www2.deloitte.com/us/en/insights/industry/retail-distribution/plant-based-meat-consumer-perceptions.html (SN)
24. Siegrist, M., Hartmann, C. (2020). Perceived naturalness, disgust, trust and food neophobia as predictors of cultured meat acceptance in ten countries. *Appetite* 155:104814. https://www.sciencedirect.com/science/article/pii/S0195666320301045 (AB)
25. Siegrist, M., Sütterlin, B., Hartmann, C. (2018). Perceived naturalness and evoked disgust influence acceptance of cultured meat. *Meat Science* 139:213–219. https://www.foodnavigator.com/Article/2018/02/19/Emphasise-cultured-meats-properties-not-production-as-a-path-to-acceptance (SN)
26. Siegrist, M., Hartmann, C. (2020). Consumer acceptance of novel food technologies. *Nature Food* 1:343–350. (AB; full text not read)
27. Anderson, J., Bryant, C. (2018). Messaging to overcome naturalness concerns in clean meat acceptance (Faunalytics). https://faunalytics.org/naturalness-concerns-and-clean-meat-acceptance-a-faunalytics-study/ (AB)
28. YouGov US daily questions, 29 May 2024. https://today.yougov.com/topics/politics/survey-results/daily/2024/05/29/9b1cc/2 (SN)
29. Is cultured meat a promising consumer alternative? Exploring key factors determining consumer's willingness to try, buy and pay a premium for cultured meat. *Appetite* (2022). https://www.researchgate.net/publication/363408134 (SN)
30. Lusk, J.L., Jamal, M., Kurlander, L., Roucan, M., Taulman, L. (2005). A meta-analysis of genetically modified food valuation studies. *JARE* 30(1):28–44. https://ageconsearch.umn.edu/record/30782 (SN)
31. Hess, S., Lagerkvist, C.J., Redekop, W., Pakseresht, A. (2016). Consumers' evaluation of biotechnologically modified food products: new evidence from a meta-survey. *ERAE* 43(5):703–736. https://ideas.repec.org/a/oup/erevae/v43y2016i5p703-736..html (AB)
32. Pew Research Center (2018). Americans are narrowly divided over health effects of genetically modified foods. https://www.pewresearch.org/short-reads/2018/11/19/americans-are-narrowly-divided-over-health-effects-of-genetically-modified-foods/ (SN)
33. Eurobarometer trends on GM food concern (2005, 2010, 2019), as summarised by the Genetic Literacy Project. https://geneticliteracyproject.org/2019/07/19/most-europeans-fear-biotech-crops-new-survey-busts-the-popular-anti-gmo-myth/ (SN)
34. Fox, J.A., Hayes, D.J., Shogren, J.F. (2002). Consumer preferences for food irradiation: How favorable and unfavorable descriptions affect preferences for irradiated pork in experimental auctions. *J. Risk Uncertainty* 24:75–95 (memory for the citation); He, Fletcher & Rimal on irradiated beef, https://ideas.repec.org/a/ags/jlofdr/27070.html (SN)
35. The Henry Ford, "Americans adjust to microwave cooking". https://www.thehenryford.org/explore/blog/americans-adjust-to-microwave-cooking/ (SN)
36. Arrell Food Institute, "How we came to drink pasteurized milk". https://arrellfoodinstitute.ca/how-we-came-to-drink-pasteurized-milk/ (SN)

**Not found or not read:** a design that prices cultivated meat **and** a welfare label (free-range,
organic) for the same respondents. None was found after several targeted searches, so the comparison in
section 1 is assembled across studies. Full texts of Asioli 2022, Escribano 2021, Yuan 2026, Siegrist &
Hartmann 2020 and Lusk 2005 were blocked (bot protection or 403), so their numbers are SN or AB.
