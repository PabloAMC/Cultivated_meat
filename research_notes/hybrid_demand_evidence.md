# How shoppers value hybrids: products part meat (or cells), part plant

Date: 2026-11-27. An evidence pass for a possible extension: products with a small share of cultivated cells in a plant base (3-30%),
such as those sold in Singapore and the US. The cut's blend rule rests on it since the same day (section 6). Sources are marked read in full, abstract only or
second-hand. φ = (hybrid − plant) / (meat − plant) is computed here from each study's own numbers, not by the authors; φ = 0.5 at a
50/50 blend would mean the value of a blend is linear in its share of meat.

**What no study does:** vary the share of *cultivated cells*. Everything below is meat-plant blends, so it is an analogue only. No
study found measures liking at three or more shares with a plant-based arm, so the shape of the curve cannot be fitted directly.

## 1. Choice and stated-preference studies

| study | design | what it finds | φ |
|---|---|---|---|
| Asioli, Banovic, Barone, Grasso & Nayga 2023, *Appl. Econ. Perspect. Policy* 45(1):44–62, doi:10.1002/aepp.13283 (read in full) | UK, Spain, Denmark; about 2,400 people; burgers 100% beef, 50/50 beef-plant, 100% plant; willingness to pay a kilo, mixed logit | control: the hybrid's discount on beef is £14.90, €21.01, 252.69 kr against the plant burger's £25.75, €40.24, 412.60 kr; information on health, taste or convenience narrows the hybrid's discount (UK £7.11, £1.80, £10.18) | 0.39–0.48 (control); 0.56–0.97 (informed) |
| Profeta et al. 2021, *Foods* 10(1):71, doi:10.3390/foods10010071 (read in full) | Germany and Belgium, n = 1,001; mortadella, salami, nuggets, meatballs at 0, 20, 35, 50, 100% plant | the three plant shares are not ordered; the large step is to 100% meat | 0.20–0.30 |
| Caputo, Sogari & Van Loo 2022, *Appl. Econ. Perspect. Policy*, doi:10.1002/aepp.13247 (read in full) | US, n = 172, tasted then chose | blind, a 70/30 beef-mushroom blend is worth $8.88 a pound against beef's $9.23; told the ingredients first, $6.94, below an animal-like plant burger ($7.73) | 0.85–0.92 blind; about 0.59 informed (against pea) |
| Salgaonkar et al. 2024, *Foods* 13(10):1460, doi:10.3390/foods13101460 (read in full) | US online, n = 454, hot dogs | the hybrid is the least preferred of the three (part-worths −16, beef −2.5, plant 18) | below 0 |
| NECTAR / GFI APAC 2025, sensory report on blended products (read in full) | Singapore, n = 116, blind, 20 products | liking out of 7: meat 5.51, blends 4.55, plant 3.95; "would buy": 85%, 22%, 16% | 0.38 liking; 0.09 purchase |
| NECTAR US 2024 (second-hand, Green Queen) | 1,192 people, blind | the best blended burger liked by 56% against 42% for beef; the average blend 42%; blends trail meat in 7 of 9 categories | |

## 2. Sensory studies

- Petrat-Melin et al. 2023, *Foods* 12:2246 (read in full): a 50/50 hybrid burger and beef liked alike (5.3 and 5.4 out of 9); no plant arm.
- Spencer, Guinard et al. 2016, *Appetite* 105:449–459 (abstract only): 50% and 80% mushroom tacos liked as much as beef; 50% mushroom carne asada
  liked less. Mince tolerates blending; whole cuts less so.
- Baune et al. 2023, *Front. Nutr.*, doi:10.3389/fnut.2023.1101479 (read in full): the best 30% pea-protein hybrid accepted.

## 3. Market record

- Grasso & Jaworska 2020, *Foods* 9:1888 (read in full): 38 hybrid products launched in the UK in 2016–20, 12 still sold; Sainsbury's "Love Meat &
  Veg" (50% vegetables) down to 1 of 5 lines, Waitrose's 50%-pulse lines gone, Tesco's 30–38% lines all still sold; 80% of 201 reviews positive.
- Tyson "Raised & Rooted The Blend" launched 2019, dropped December 2020 (second-hand). Sonic's 25%-mushroom burger made permanent in 2018
  (second-hand; status now not verified). No sales volumes or shares for blended meat were found.

## 4. Cultivated hybrids sold

| product | cells | price | status (second-hand) |
|---|---|---|---|
| GOOD Meat chicken, Singapore restaurants | 70% | about S$23 a plate | one bistro stopped serving it by March 2024 |
| GOOD Meat 3, Huber's Butchery | 3% | S$7.20 for 120 g | a production pause reported November 2025 (headline only) |
| Mission Barns pork-fat meatballs, US | a single-digit share of cultivated fat | $13.99 for 304 g | on sale |
| Wildtype salmon, US | the main ingredient after water | about $32 a plate | cleared by the FDA, May 2025 |

No sales volumes were published for any of them.

## 5. What it says for the model

- **Tasted blind, blends lose little** (φ near 0.9 in ground formats). **Chosen with a label, they keep less than a linear share of
  meat's advantage** (φ 0.2–0.5 at 50–80% meat, flat across 20–50% plant, with the large step at 100% meat), and on purchase intent less still.
  Information can put a blend below the plant product.
- **This bears on an assumption the model already makes.** A cut is 80% cells, and the model takes off (1 − 0.8) of the real-meat credit,
  a linear rule (`meat_market.tier_offset`). The labelled-choice studies suggest a blend loses more than its plant share. Profeta's flat
  pattern and step at 100% meat would put an 80% cut nearer a plant product than the linear rule does. The analogue is weak (meat, not
  cells). Section 6 says what was changed.
- For a product of 3–30% cells, the studies put most of the value step at the plant end: a little cultivated meat adds little over a
  plant product in labelled choice. The flavour of a few per cent of cultivated fat (Mission Barns) has no data.
- The best single basis for a parameter: Asioli et al. 2023 (largest sample, three countries, both blend and plant in one design), at one
  share only (50/50); Profeta 2021 for the shape across shares.

## 6. What the model does with it (2026-11-27)

A product that is a share s of cells keeps s^γ of the real-meat credit (`meat_market.blend_kept`; the input `blend_curve`). The
rule before was γ = 1.

| evidence | share of meat | φ | γ = ln φ / ln s |
|---|---|---|---|
| Caputo 2022, tasted blind | 0.70 | 0.85–0.92 | 0.2–0.5 |
| Asioli 2023, told about health, taste or convenience | 0.50 | 0.56–0.97 | 0.04–0.8 |
| **Asioli 2023, control (UK 0.42, Spain 0.48, Denmark 0.39; mean 0.43)** | 0.50 | 0.39–0.48 | **1.1–1.4; 1.2 at the mean** |
| Caputo 2022, told the ingredients | 0.70 | about 0.59 | 1.5 |
| Profeta 2021 | 0.50–0.80 | 0.20–0.30 | 2 at 50% meat, 6 at 80% |

- **Central value 1.2**, from Asioli's control arm: the largest sample, three countries, and labelled choice with no added
  information, which is how the demand model's own weights were measured.
- **Range 0.4 to 2.5, drawn in the bands.** The low end is what blind tasting and informed choice give, the high end Profeta's
  result at 50% meat. The evidence points both ways around the old linear rule, so the central value moves little and most of
  what is new is the uncertainty. Profeta's flat pattern (a step at 100% meat) is not a power curve; 2.5 covers it at 50% meat
  and understates it at 80%.
- **Effect:** at 80% cells a cut keeps 77% of the credit (80% before) and carries −1.24 utils (−1.06 before).
- **Not done:** mince stays all cells. A product of 3–30% cells in a plant base can be set as a cut with the page's cell-share
  slider (down to 10%), where the same curve applies; a hybrid mince is not modelled (TODO.md).

The raw extracts used are not kept in the repository.
