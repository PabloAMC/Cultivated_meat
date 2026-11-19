# How shoppers differ: the evidence on price sensitivity and on liking for cultivated meat

Compiled 2026-11-18 from three reading passes, to decide how the shopper model should represent differences between shoppers. It
changes no default. It corrects one of the model's own checks (section 1) and overturns an assumption made earlier the same day
(section 2). Access levels: **FT** full text read; **ABS** abstract only; **SNIP** search snippet; **SIM** simulated from published
coefficients; **MEM** background knowledge, unchecked.

## 1. The one choice experiment the model was set against, read again

Van Loo, Caputo & Lusk 2020 (Food Policy 95; US, 1,830 respondents in four arms; lab-grown, pea, heme and beef burgers and "none", at
six prices from $2.99 to $10.49 a lb; FT).

- **"About 5% at equal price" is right.** With all four burgers at $5 a lb in the control arm, lab-grown takes 5% of those who buy
  something (beef 72%, pea 16%, heme 7%), 4% counting those who buy nothing. With information on sustainability or technology, 6–7%.
- **The paper reports no elasticity.** The model's check has used "−0.84 to −3.4" as the measured own-price elasticity at equal price
  (`market_share.LUSK_ELAS_BRACKET`). Those two numbers are β × price × (1 − share) for the paper's two price coefficients (−0.178
  for the pooled logit, −0.72 for the random-parameter logit). Neither is the aggregate response; the second ignores the very wide
  spread of liking the same model estimates.
- **Simulating the paper's fitted random-parameter logit gives about −1.5 at equal price** (SIM; the simulation reproduces the
  published shares: 4.3, 14.3, 6.4 and 63.4%). By price of the lab-grown burger, with the others at $5: −0.87 at $3, −1.5 at $5, −2.0
  at $7, −2.4 at $9. Across the four arms at $5: −1.1 to −1.65.
- **Liking for lab-grown is spread very widely.** The lab-grown constant has mean −0.25 and standard deviation 3.75 in the control arm
  (3.6–4.6 across arms), on a scale where a dollar a pound is 0.72. About half of respondents (47–56% by arm) prefer it to buying
  nothing; mean willingness to pay against nothing is −$0.34 to +$0.86 a lb, against $10–11 for beef.
- The price coefficient's spread is imposed (a triangular distribution with spread equal to its mean), so the paper says nothing about
  how price sensitivity varies.

The model's first-contact elasticity at equal price is −3.27: inside the old bracket, and about twice the simulated figure.

## 2. Who likes cultivated meat is not who is insensitive to price

| study | sample | groups found | access |
|---|---|---|---|
| Carzedda & Troiano 2021 (Udine working paper), Italy | 1,069, mostly students; burgers | "cultured supporters" 16%: the most price-sensitive group, and still prefer conventional. "Italian-organic supporters" 35%: the least price-sensitive, and dislike cultured meat most (about −€11 a kg) | FT |
| Washio et al. 2023 (Meat Science), Japan | 4,421; beef mince | "novelty accepters" 12.8%: pay about +185 yen per 100 g for cultured, middling price sensitivity. "Generous customers" 31.9%: price coefficient near zero, and reject cultured meat almost outright | FT |
| Asioli et al. 2022 (Food Policy), UK, Spain, France | 648; burgers | a group willing to pay a premium: 47% (UK, £5.10 a kg), 38% (Spain, €3.35), 30% (France, €2.68); on average Spain and France reject | ABS |
| Slade 2018 (Appetite), Canada | burgers | 11% choose cultured at equal price; liking for plant-based and for cultured "highly, but not perfectly, correlated" | ABS |
| Carlsson, Kataria & Lampi 2022, Sweden | burgers | "almost half" would not choose the lab burger even if free | ABS |

- An **enthusiast group of about 13–16%** appears in both studies that split shoppers. It is not price-insensitive.
- A **price-insensitive group of about a third** appears in both. It buys organic and local, and is the most hostile to cultured meat.
- Probability that liking for cultivated meat and low price sensitivity go together across shoppers: about 0.2. Zero to mildly
  negative is the better prior. **The buyer of organic and welfare-labelled meat is the wrong stand-in for the early buyer of
  cultivated meat.** This is two stated-preference samples, one of students, so confidence is low to moderate.
- Not found: any study reporting a distribution of willingness to pay for cultivated meat, or the correlation between its price
  coefficient and its liking for cultivated meat.

## 3. How much shoppers differ in price sensitivity (meat and eggs)

| study | finding | access |
|---|---|---|
| Lusk, FFAR/FMI report behind Agribusiness 2019; US, eggs, over 2,000 respondents | four groups: 27.5% "price sensitive", 31.3% "price conscious", 6.1% "label conscious", 35.1% "price insensitive"; price coefficients −3.61, −1.47, −2.33, −0.20 (18 times between the ends); the liking for cage-free is about the same in the three big groups | FT |
| same | willingness to pay for cage-free: mean $1.16 a dozen, median $0.30; a quarter above $3. Models with a continuous spread of price sensitivity fit worse than groups | FT |
| Finnish broiler welfare study (Poultry Science 2023) | five groups, 41/19/17/12/11%; price coefficients differ 5 to 19 times | FT |
| Van Loo et al. 2011, US, chicken breast | mean willingness to pay +104% for USDA organic; habitual buyers +244%, non-buyers +26% | ABS |
| Tonsor & Lusk 2021, US, pork loin, retail scanner in 51 markets | own-price elasticity from −2.70 to −0.23 across markets | FT (summary) |

- Three or four groups is the usual finding. In stated choices 45–60% are price-driven and 15–35% price-insensitive; for real purchases
  the price-insensitive group is probably 8–15%.
- Between the most and least price-sensitive groups: 5–19 times in stated choices, probably 4–10 in behaviour (central 6). As a
  continuous spread, a standard deviation of the log price coefficient of 0.6–1.0.
- Low price sensitivity and liking for ethical attributes go together only modestly (a correlation of perhaps 0.2–0.5): in Lusk's eggs
  the high willingness to pay comes from a small price coefficient, not a stronger liking, and that group also pays more for a carton.
- Not found: how concentrated purchases of premium meat are across households; any estimated correlation between price and attribute
  coefficients.

## 4. Plant-based meat: what its elasticity is, and who buys it

| source | what it measures | own-price elasticity | access |
|---|---|---|---|
| GFI/NielsenIQ fact sheet, Nov 2024 (the −1.23 Knowles 2026 cites) | weekly store scanner; item-level regular price; plant-based **beef** only | −1.23; 59% of the response is switching to other products | FT |
| Zhao, Wang, Hu & Zheng (AEPP 2023) | Nielsen scanner 2017–20; the category | −1.48 | ABS, SNIP |
| Caputo, Lusk & Blaustein-Rejto (2025) | basket choice experiment | −0.91 to −0.93 at home; −1.3 to −1.6 away | FT |
| Neuhofer & Lusk (2023 draft); Tonsor, Lusk & Schroeder (2021) | weekly household panel; stated brand choice | −3.8; −2.4 to −3.3 (brand-level or weekly: overstate the category) | FT |

- Best estimate for the category in the long run: about −1.3 (80% range −0.6 to −2.5; low confidence). The model's is −2.85. None of
  these identifies the response to a large, permanent price change.
- **Buying is very concentrated.** A fifth of buyers make 75% of spending (Circana, 2024; FT); 7% of all households make 82% of it
  (GFI/NielsenIQ, 2022; FT). Household reach fell from about 20% (2021) to 11% (2025) while the repeat rate stayed above 60%.
- That the remaining buyers are less price-sensitive than the average buyer of 2021: about 0.65; less than half as sensitive: about 0.3.
  In Tonsor's experiments people who do not regularly eat meat had elasticities of −0.9 to −1.6 for Beyond Beef, regular meat eaters
  −3.6 to −8.6.

## 5. What this says for the model

1. **The flatness the measurements show comes mostly from a spread of liking, not of price sensitivity.** A wide spread of liking
   reproduces the experiment's response at every price with the model's price sensitivity unchanged (`liking_spread.md`).
2. **The premium-buyer recalibration built earlier on 2026-11-18 was not merged** (branch `claude/recalibrate-demand`). It gave
   cultivated meat's price-insensitive tail to organic buyers, which section 2 contradicts.
3. **With a spread of liking, "about half the market at equal price" stops following from novelty fading.** It becomes a premise about
   how far the average shopper's liking recovers, and it is the model's largest unknown.
4. Price sensitivity also differs across shoppers (section 3), and plant-based meat's buyers are a concentrated minority (section 4).
   Both belong in a later rebuild; neither is needed to explain cultivated meat's curve.

## Sources

1. Van Loo, Caputo & Lusk 2020, Food Policy 95, 101931 (FT).
2. Carzedda & Troiano 2021, University of Udine working paper (FT); Washio et al. 2023, Meat Science (FT); Asioli et al. 2022, Food Policy (ABS); Slade 2018, Appetite (ABS); Carlsson, Kataria & Lampi 2022 (ABS).
3. Lusk, report to FFAR and FMI on cage-free eggs (the survey behind Agribusiness 2019) (FT); Finnish broiler welfare study, Poultry Science 2023 (FT); Van Loo et al. 2011, Food Quality and Preference (ABS); Tonsor & Lusk 2021 (FT, summary).
4. GFI/NielsenIQ plant-based pricing fact sheet, November 2024 (FT); Circana household panel report, 2024 (FT); GFI/NielsenIQ migration analysis, 2022 (FT); Neuhofer & Lusk 2022, Scientific Reports (FT); Zhao et al. 2023, AEPP (ABS); Caputo, Lusk & Blaustein-Rejto 2025 (FT); Tonsor, Lusk & Schroeder 2021 (FT).
