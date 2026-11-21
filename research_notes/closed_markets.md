# Markets cultivated meat cannot be sold into

2026-11-20 (revised the same day: meat-consumption weights and two religious levels). Code: `meat_market.closed_share` and
`meat_market.world_meat_weight`, applied in `meat_market._rollup` (and the page's `closedShare`); inputs `mk_closed_*`,
`mk_world_pop_m`; meat a head in `meat_market.MEAT_KG_HEAD`. The lever on the page: "Share of the meat market it cannot be sold into".

## What the model does

A region's volume and value shares of cultivated meat are multiplied by (1 − closed share). The closed share is the part of
the region's meat market where a law bans its sale, each law weighted by its share of the region's meat consumption:

* **US states within the US: population share.** No state-level figure for meat eaten a head was found, so meat a head is
  assumed equal between states (an assumption, not a measurement).
* **Italy and Hungary within the EU-27, and the US and the EU-27 within the world: people times meat a head**, from the FAO food
  balance sheets for 2023 (meat supply per person, kg a year, read from Our World in Data's series of it on 2026-11-20): US 122.06,
  EU-27 78.55, Italy 71.2, Hungary 76.33, world 45.12. With the populations below, the US eats 11.23% of the world's meat (4.15% of
  its people) and the EU-27 9.54% (5.48% of its people); Italy and Hungary eat 13.89% of the EU's meat (15.18% of its people).

Until this revision population share was used everywhere, which put the US laws at a third of their weight in the world. The FAO
figures are meat only; the model's markets also hold seafood, which is spread more evenly between the US and the world, so these
weights slightly overstate the US's share of the world's meat and seafood.

Levels (`mk_closed_level`; the page's reference chips):

| Level | What is closed | US | EU-27 | World |
|---|---|---:|---:|---:|
| 0 none | nothing | 0 | 0 | 0 |
| 1 permanent bans (the default) | the five US states with permanent bans | 10.2% | 0 | 1.14% |
| 2 every law in force | also the three US temporary bans and the two contested EU laws | 21.8% | 13.9% | 3.77% |
| 3 (world only) | also the one religious body that has ruled against it: Indonesia, all of it counted | 21.8% | 13.9% | 5.31% |
| 4 (world only) | also the populations whose religious authorities have set conditions (halal or kosher inputs and supervision), if those conditions were not met | 21.8% | 13.9% | 15.9% |

Before the revision (population weights, one religious level of 10%): world 0.42%, 1.74% and 11.7%; EU-27 15.2%.

China, India, Brazil and Nigeria: no law found, so nothing is closed.

## The laws

Populations: US Census Bureau, Vintage 2025 (1 July 2025), US total 341.78M; Eurostat, 1 January 2025, EU-27 451.28M; world 8,231.6M
(UN World Population Prospects 2024, the 2025 figure, not re-fetched).

### US, permanent bans

| State | Law | In force | People (M) | Share of the US |
|---|---|---|---:|---:|
| Florida | SB 1084 (2024) | 1 Jul 2024 | 23.46 | 6.86% |
| Alabama | SB 23 (2024) | 1 Oct 2024 (not re-verified) | 5.19 | 1.52% |
| Mississippi | HB 1006 (2025; also cultivated dairy) | 1 Jul 2025 (not re-verified) | 2.95 | 0.86% |
| Montana | HB 401 (2025) | 1 Oct 2025 (not re-verified) | 1.14 | 0.33% |
| Nebraska | LB 246, signed 20 May 2025 | 2025 (not re-verified) | 2.02 | 0.59% |
| **Total** | | | **34.77** | **10.17%** |

Florida's ban is challenged in court by Upside Foods (ongoing).

### US, temporary bans

| State | Law | Period | People (M) | Share of the US |
|---|---|---|---:|---:|
| Texas | SB 261 (2025) | 1 Sep 2025 to 1 Sep 2027 (enrolled text) | 31.71 | 9.28% |
| Indiana | HB 1425 (2025) | 1 Jul 2025 to 30 Jun 2027 | 6.97 | 2.04% |
| South Dakota | SB 124 (2026) | 1 Jul 2026 to 30 Jun 2031 | 0.94 | 0.27% |
| **Total** | | | **39.62** | **11.59%** |

Not counted: South Dakota HB 1077 (a permanent ban, vetoed, override failed); Wisconsin AB 554 (vetoed); Ohio HB 10 (labelling and
school purchases only); Idaho, Iowa and others (labelling only); Arizona (proposed, no evidence of enactment).

### EU (contested)

| Country | Law | People (M) | Meat a head, kg (FAO 2023) | Share of the EU-27's people | Share of its meat |
|---|---|---:|---:|---:|---:|
| Italy | Law 172/2023 of 1 Dec 2023: production and marketing banned | 58.94 | 71.2 | 13.06% | 11.84% |
| Hungary | Act LXXXIX of 2025, passed 18 Nov 2025 (140-10-18): production and sale banned | 9.54 | 76.33 | 2.11% | 2.05% |
| **Total** | | **68.48** | | **15.18%** | **13.89%** |

The EU-27 eats 78.55 kg a head (FAO 2023), so its meat is 451.28M x 78.55 kg.

Both are contested under EU law. Italy adopted its law during the TRIS standstill and the Commission closed the procedure noting
the breach, which under EU case law can make the ban unenforceable against private parties. In Hungary's TRIS notification the
Commission and Sweden, Lithuania, the Netherlands and Czechia called the ban unjustified, since novel foods are authorised at EU
level. Hungary's date of entry into force was not verified. No other EU member had enacted a ban by November 2026 (Romania and
France have discussed one).

### Religious rulings (the world's levels 3 and 4)

Every major halal or kosher authority that has ruled has given a conditional permission; one body has ruled against:

* International Islamic Fiqh Academy, Resolution 265 (10/26), Doha, May 2025: permissible if the cells come from a halal, properly
  slaughtered animal and the medium has no blood or pig products (so no fetal bovine serum), under credible supervision.
* Singapore, MUIS fatwa of 3 Feb 2024: conditionally halal.
* Malaysia, JAKIM (National Muzakarah Committee, September 2025): conditionally halal, no fetal bovine serum.
* Israel's Chief Rabbi David Lau, January 2023: Aleph Farms' steak kosher (a ruling, not a certification).
* OU Kosher, September 2023: SuperMeat's chicken cell line kosher (mehadrin) and meat.
* Against: Nahdlatul Ulama (Indonesia), national conference of 26 Sep 2021: haram (secondary source).

No population is closed by a religious ruling except, at most, Indonesia's, so the model's default and level 2 count no religious
closure. The two world-only levels say exactly what they count:

* **Level 3, the one body that has ruled against it** (`mk_closed_religious_against`, 1.54% of world meat): all of Indonesia,
  281.2M people at 19.95 kg a head (FAO 2023), against the world's 8,091.7M at 45.12 kg (both 2023, so the share is of the
  same year's totals). Nahdlatul Ulama's followers are roughly half of Indonesians (a rough figure), which gives the low end, 0.7%.
* **Level 4, populations whose authorities have set conditions, if those conditions were not met**
  (`mk_closed_religious_conditions`, 10.6% of world meat): the meat of 47 Muslim-majority countries other than Indonesia (FAO 2023;
  the latest year for Sudan, Somalia, Mali and Chad, 2022, and Brunei, 2009; Kosovo and Palestine, which have no FAO series, at the
  world's 45.12 kg a head), half of Nigeria's (about half its people are Muslim), and Israel's. The largest parts: Pakistan 1.44%,
  Turkey 1.18%, Egypt 0.87%, Iran 0.74%, Malaysia 0.66%, Saudi Arabia 0.53%. Whole countries are counted, so non-Muslims in
  Muslim-majority countries are in, and Muslims elsewhere (India, Europe, Russia, China) and observant Jews outside Israel are
  out; the input's range, 8% to 13%, allows for both. This level is closed only if the conditions (halal or kosher donor cells,
  no blood or pig products in the medium, supervision) were not met; a producer that meets them sells there.

Until this revision a single religious level of 10% (a rough judgement) stood in for both and was labelled as populations whose
authorities had "not yet ruled it permissible", which read as about a tenth of the world being closed for religious reasons.
That was wrong as a reading of the rulings and is retired.

The list of Muslim-majority countries: Afghanistan, Albania, Algeria, Azerbaijan, Bahrain, Bangladesh, Bosnia and Herzegovina,
Brunei, Burkina Faso, Chad, Comoros, Djibouti, Egypt, Gambia, Guinea, Iran, Iraq, Jordan, Kazakhstan, Kosovo, Kuwait, Kyrgyzstan,
Lebanon, Libya, Malaysia, Maldives, Mali, Mauritania, Morocco, Niger, Oman, Pakistan, Palestine, Qatar, Saudi Arabia, Senegal,
Sierra Leone, Somalia, Sudan, Syria, Tajikistan, Tunisia, Turkey, Turkmenistan, United Arab Emirates, Uzbekistan, Yemen
(and Indonesia, counted at level 3).

## Sources

* Census Vintage 2025 state totals (NST-EST2025-ALLDATA): https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html
* Eurostat tps00001: https://ec.europa.eu/eurostat/databrowser/view/tps00001
* Texas SB 261 enrolled text: https://capitol.texas.gov/tlodocs/89R/billtext/html/SB00261F.htm
* National Agricultural Law Center, alternative protein laws: https://nationalaglawcenter.org/state-compilations/alternative-protein-laws-state-compilation/
* CSG Midwest, 4 May 2026 (Nebraska, Indiana, South Dakota, Ohio, Wisconsin): https://csgmidwest.org/2026/05/04/though-not-yet-on-grocery-shelves-lab-grown-meat-is-focus-of-new-laws-and-legislation/
* Penn State agricultural law list: https://aglaw.psu.edu/?p=61903
* Indiana: https://vegconomist.com/cultivated-cell-cultured-biotechnology/cultivated-meat/indiana-enacts-two-year-ban-cultivated-meat-begin-july-2025/
* South Dakota: https://www.wlj.net/sd-governor-signs-lab-grown-meat-moratorium/
* Hungary's vote: https://telex.hu/english/2025/11/18/hungarian-parliament-votes-to-ban-artificial-meat
* Hungary's TRIS objections: https://www.greenqueen.com.hk/eu-commission-hungary-lab-grown-meat-cultivated-ban-tris-notification/
* Italy and TRIS: https://www.foodmanufacture.co.uk/Article/2024/02/07/cultivated-meat-ban-in-italy-violated-eu-rules
* IIFA Resolution 265: https://iifa-aifi.org/en/56085.html
* MUIS: https://www.muis.gov.sg/resources/media-releases/3-feb-24-fatwa-on-cultivated-meat/
* JAKIM: https://www.greenqueen.com.hk/lab-grown-meat-cultivated-halal-muslims-malaysia-islamic-jakim/
* Aleph Farms: https://www.aleph-farms.com/blog/kosher-ruling
* OU and SuperMeat: https://www.foodnavigator.com/Article/2023/09/07/How-does-a-cultivated-chicken-cell-line-meet-kosher-standards
* Nahdlatul Ulama: https://www.nu.or.id/national/2021-nu-munas-decides-cell-based-meat-forbidden-to-be-consumed-o9B3Y
* FAO food balance sheets, meat supply per person (via Our World in Data, fetched 2026-11-20): https://ourworldindata.org/grapher/meat-supply-per-person
* Population, 2023 (Our World in Data, from UN World Population Prospects): https://ourworldindata.org/grapher/population

## Open

* Meat a head is assumed equal between US states; no state-level figure was found.
* The FAO weights are meat only; the markets also hold seafood.
* Effective dates for Alabama, Mississippi, Montana, Nebraska and Hungary were not re-verified.
