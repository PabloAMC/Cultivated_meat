# Ammonia the cells tolerate, and how long a cell filter lasts

Research date: 2026-11-16. A literature pass on the two inputs that move Central most (`answer_rests_on.py`, RESULTS.md "What
the answer rests on"): `pf_nh3_limit` (5 mmol/L, range 2–10) and `rt_membrane_life` (3,960 L/m², range 900–5,500). **No input
was changed.** Costs are 2025 dollars per kg of wet cells. I computed them on the model as it stood on 2026-11-16 by moving one
input with each scenario's tank design held, as `answer_rests_on.py` does. No test pins them, so they will drift as the model
changes.

Sources already in `waste_and_medium_evidence.md`, `waste_handling.md`, `retention_devices.md`, `retention_alternatives.md` and
`filter_flux.md` are not repeated unless this pass adds a number. Two research agents ran the searches. I re-opened the sources
marked **checked** myself and confirmed the quoted numbers. The other rows are as the agents read them.

Access: **full** (read in full), **part** (sections or the table read, or a fetch tool's extract), **abstract**, **snippet**
(search result only), **secondary** (quoted by another document, which is named). "mM" is total ammonium (NH4+ plus NH3), added
as NH4Cl, unless a row says otherwise. No meat-relevant source measured free NH3.

## Summary

1. **Ammonia.** No source measures the ammonia tolerance of bovine, chicken or fish satellite cells. The meat-relevant cells that
   have been measured lose 10–55% of their growth rate at 2.5–5 mM, without adaptation:
   - catfish ovary cells, 45% at 2.5 mM and 55% at 5 mM;
   - mouse 3T3 fibroblasts, 39% at 5 mM;
   - human foreskin fibroblasts, 13% (not significant) at 5 mM;
   - pig muscle stem cells, 22% when started at 3.8 mM instead of 1.1 mM;
   - bovine FAPs, inhibited above 5 mM.

   CHO, the source of the 5 mM figure, is more tolerant (IC50 33 mM in one study). Hybridomas raised gradually or adapted grow at
   10–21 mM. Meat-cell processes that state a set-point hold ammonium at 2–3 mM.
2. **What the model's number has to mean.** In perfusion the cells live at the limit all the time, and, as far as I read the code, the
   model charges no slower growth there. So the value should be the level at which Central's selected cells lose little growth, about 10%. That is
   not an IC50. For unadapted meat-relevant cells that level is about 1–3 mM. Selection, which Central assumes, could raise it.
   Only hybridoma data show by how much.
3. **Ammonia verdict.** 5 mM is at the generous end of the meat-relevant evidence.
   - My median for Central's cells is about 3.5–4 mM.
   - P(true value within a factor of 1.5 of 5 mM, i.e. 3.3–7.5 mM) ≈ **45%**; P(below 3.3) ≈ 45%; P(above 7.5) ≈ 10%.
   - Moving to 4 mM would put Central at $34.0 (from $29.4); 3.5 mM would put it at $37.2.
4. **Filter life.** Small-pore fibres (0.2–0.65 µm) in dense CHO perfusion usually foul or lose sieving after about 6–30 days.
   That is a few hundred to about 2,500 L/m². Clincke's best fibre (about 5,500 L/m²) is the only one at or above the model's
   3,960. An industry design framework assumes **1,000 L/m²** for cell-retention filtration at 50–120 million cells/mL. A Merck
   study at 85–100 million cells/mL (about 15–26% cells by volume) says a filter swap at large scale "only extends the culture
   duration by a couple of days". Large-pore ceramic fibres (5–7 µm) reached 4,600–16,000 L/m², but at a density not given and
   with CHO.
5. **Filter verdict.** 3,960 L/m² is optimistic for the pharma fibre the model prices.
   - My median for one fibre at 18% cells by volume over a month is about 1,500 L/m² (80% interval 500–4,000).
   - P(true value within a factor of 1.5 of 3,960, i.e. 2,640–5,940 L/m²) ≈ **20%**.
   - Moving to 1,500 would put Central at $43.1; 2,000 would put it at $37.6.
6. **The two errors compound.** A lower ammonia limit needs more medium, so more permeate per kg, so more membrane. Both at my
   medians (4 mM, 1,500 L/m²) give Central **$51.9** (best case $17.1), against $29.4 and $9.7 now.

## 1. Ammonia: what the model assumes

`floor_physics.washout_litres` sets the medium per kg so that ammonia made per kg divided by medium per kg equals
`pf_nh3_limit`. Central's selected cells make 0.14 mol/kg (`sc_nh3_selected`, Hubalek 2023, bovine FAPs fed alpha-ketoglutarate
in place of glutamine). At 5 mM that is 28 L/kg. The tank sits at the limit at steady state. As far as I read `floor_physics.py`, the model charges no slower growth
at the limit (my reading of the washout function only). Halving the limit doubles the medium and the permeate.

Humbird's 5 mM is "the limits of 5 mmol/L NH3", chosen within 2–10 mM "reported for mammalian cells", mostly CHO and hybridoma.
The model's label says NH3. Most of the sources behind that range report total ammonium, so I read the limit as total ammonium (my reading; I did not check Humbird's wording against his sources).

## 2. Ammonia: evidence

| Source | Cells | Conditions | Value | Access |
|---|---|---|---|---|
| Slivac et al. 2010, Cytotechnology, doi:10.1007/s10616-010-9312-y (PMC2995142) | Channel catfish ovary (CCO) line, adherent | 5% FBS, 30 °C, bicarbonate buffer, pH not stated; NH4Cl spiked 24 h after seeding at 0–20 mM; endpoint specific growth rate | μ (h⁻¹): control 0.0260; 1 mM 0.0212 (−18%); 2.5 mM 0.0143 (−45%); 5 mM 0.0116 (−55%, cells lost in the last 2 days); 7.5 mM 0.0046 (−82%); 10 mM 0.0042 (−84%); 20 mM dead within 24 h. Half-inhibition about 3 mM (my interpolation). Its glutamine-fed cultures themselves reached 2–2.5 mM | part, **checked** (Table 1 and results) |
| Moreno-Sánchez et al. 2020, Front Oncol (PMC7160333) | Mouse 3T3 and human HFF-1 fibroblasts (non-cancer controls) | DMEM, 10% FBS, 2-D, +5 or +10 mM NH4Cl, n = 3; pH not stated | 3T3: μ −39% at 5 mM, −54% at 10. HFF-1: −13% (not significant) at 5, −47% at 10. The text claims an IC50 "around 1 mM (data not shown)", which the table does not support for growth rate | part (Table 1) |
| Hassell, Gleave & Butler 1991, Appl Biochem Biotechnol 30:29, doi:10.1007/BF02922022 | 8 lines incl. human diploid fibroblasts (HDF), Vero, BHK | 2 mM NH4Cl; endpoint growth and final yield | HDF, 293, Vero, PQXB1/2: under 14% inhibition. McCoy, MDCK: final yield −50–60%. HeLa, BHK: over 75% inhibition | abstract |
| Cruz et al. 2000, Enzyme Microb Technol 27:43 | BHK-21 (fibroblast-like) | Stirred vs static cultures; model fit of growth | Ammonia constant for growth about 1.1 mM in stirred cultures, 3.5 mM in static ones | snippet |
| Qiu et al. 2026, Metabolic Engineering, doi:10.1016/j.ymben.2026.01.001 (preprint 10.1101/2025.09.30.679571) | Pig (*Sus scrofa*) muscle stem cells (Ivy Farm line), suspension, shake flasks | Proprietary SR7 medium with serum-derived factors; pH held about 7.5; two batch runs starting at 1.07 vs 3.82 mM NH4+; the high run stayed mostly above 4 mM | Peak μ 0.0664 vs 0.0516 h⁻¹ (−22%); peak biomass 0.59 vs 0.39 g/L (−34%). NH4+ correlated significantly with lower growth rate, lactate did not. Only two conditions, passage 59 vs 64; glucose and glutamine uptake also halved | part, **checked** (preprint) |
| Bodiou et al. 2025, Sci Rep, doi:10.1038/s41598-025-97813-7 (Mosa Meat) | Bovine satellite cells on microcarriers | 3–6 million cells/mL, stirred | Spent medium exceeded 3 mM ammonia and 10 mM lactate ("data not shown"). A level reached, not a tolerance | part |
| Jacobtorweihe et al. 2025, Eng Life Sci, doi:10.1002/elsc.70035 | Quail cell line, high-density perfusion (virus production) | — | Ammonium "remained below a critical level of 2–3 mM". The 2–3 mM is the authors' working limit, not a measurement | part |
| Takahashi et al. 1985, J Cell Physiol, doi:10.1002/jcp.1041250114 | IMR-90 human lung fibroblasts | 0.1 mM NH4Cl | Fewer cell divisions; size not given. An outlier, far below every other row | abstract |
| Liu et al. 2022, Bone Research, doi:10.1038/s41413-022-00215-y | Bone-marrow mesenchymal stem cells | 5 mM (dose as quoted by Hubalek 2023) | Proliferation *rose*, through glutamine synthetase turning ammonia into glutamine | abstract + secondary (Hubalek 2023) |
| Stern, Dasarathy & Mozdziak 2017 (doi:10.1007/s11626-016-0088-z) and 2019 (Front Sustain Food Syst 3:115) | Chick, rat and C2C12 myotubes | Differentiation medium, pH 7.4, 2.5–10 mM ammonium acetate, 24–48 h | **Differentiation only.** At 10 mM chick myotubes grew wider; C2C12 and rat myotubes shrank | abstract (2017); part (2019) |
| Yang & Butler 2000, Biotechnol Bioeng 68:370 | CHO (EPO) | NH4Cl, 4-day batch | Growth inhibited above 5 mM; IC50 33 mM | abstract |
| Doyle & Butler 1990, J Biotechnol, doi:10.1016/0168-1656(90)90053-e | Mouse hybridoma | NH4Cl at pH 6.8–7.8 | IC50 (total) 4 mM at pH 7.8, 7.6 mM at pH 6.8. A 1.9-fold shift per pH unit, against about 10-fold if free NH3 alone were toxic | abstract |
| McQueen & Bailey 1990, Biotechnol Bioeng 35:1067, doi:10.1002/bit.260351102 | Mouse hybridoma, controlled reactor | Constant external pH 6.8–7.6 | 3 mM little effect; 10 mM substantial inhibition; external pH had only minor effects on growth | abstract |
| Newland et al. 1994, Biotechnol Bioeng 43:434 | Mouse hybridoma | Inoculated into, ramped up to, or stepped up in ammonium | Inoculation above 2 mM inhibited growth. No inhibition above 10 mM when NH4Cl was raised gradually over a batch. In continuous culture each of five steps (2.8 → 3.7 → 4.0 → 4.9 → 7.7 → 13.5 mM) gave strong inhibition, then the cells settled at a lower density | abstract (via search summary) |
| Matsumura et al. 1991, Cytotechnology 7:103 | Two mouse hybridoma lines, serum-free | Serial ammonium increases in continuous culture | Line 4C10B6 grew at up to 21 mM NH4Cl at 80% viability | abstract (via search summary) |
| Schumpp & Schlaeger 1992 | HL-60 clones selected for resistance | — | Grew in 4 mM ammonium plus 60 mM lactate | snippet (agent's note) |
| US patent 5,156,964 (Cetus) | Hybridoma | Adapted to 5 or 10 mM | Adapted to 5 mM: +49% antibody yield; adapted to 10 mM: worse | part (agent's read) |

Already in the repo's notes, for comparison: bovine FAPs, proliferation inhibited above 5 mM at day 4 (Hubalek 2023); hybridoma
halved at about 4 mM (Ozturk 1992); CHO no inhibition to 10 mM (Lao and Toth 1997); an insect line slowed above 6.25 mM (Letcher
2024); chicken fibroblasts held below 3 mM in perfusion (Pasitka 2024); lamb satellite cells, 1.8–33 mM quoted from the
literature (Pakbin 2025).

**Not found:**
- A proliferation dose-response for bovine, chicken, duck or quail satellite cells or myoblasts, for C2C12 or QM7 myoblasts, or
  for 3T3-L1 preadipocytes.
- Any meat cell adapted or selected for ammonia tolerance.
- Any meat-relevant source that reports free NH3, or that runs a dose-response at high density or in serum-free medium.

### Reading

- **Meat-relevant cells look more sensitive than CHO.** Every meat-relevant line measured loses 10–55% of its growth rate at 2.5–5
  mM. Human diploid fibroblasts and Vero are the tolerant exceptions, with under 14% loss at 2 mM. CHO, which most of Humbird's
  range comes from, shows onset at 5 mM and an IC50 of 33 mM in one study. The two outliers point opposite ways: IMR-90 slowed at
  0.1 mM; mesenchymal stem cells grew faster at 5 mM.
- **The right comparison is a small growth loss, not half.** A perfusion tank holds the cells at the limit for weeks, and the
  model charges no slower growth there. A 20% slower growth rate at 5 mM would itself raise the cost, and the model does not count
  it. For unadapted meat-relevant cells, a 10% loss comes at about 1–3 mM: catfish lose 18% at 1 mM; pig cells lose 22% between
  about 1 and 4 mM.
- **Slow build-up and adaptation raise tolerance; sudden steps and stirring lower it.** Hybridomas raised gradually showed no
  inhibition above 10 mM, but each step in continuous culture inhibited them, and one line was adapted to 21 mM (Newland 1994,
  Matsumura 1991, abstracts). BHK showed a lower constant in stirred than in static culture (1.1 vs 3.5 mM, snippet). A tank
  that builds ammonia up slowly from a low start sits between the two cases. The only adaptation evidence is in hybridomas and
  HL-60. None is in meat cells, and one patent saw no gain from adapting to 10 mM.
- **pH and free NH3.** The only pH series is Doyle & Butler on hybridoma: the total-ammonium IC50 moved 1.9-fold per pH unit.
  Free NH3 is about 1% of total at pH 7.4 and about 2% at pH 7.7 (my arithmetic from a pKa near 9.25 at 37 °C, which I did
  not source). So at tank pH it is a few tenths of a mM. McQueen & Bailey found external pH hardly mattered. Together the two
  papers suggest both forms contribute, and I cannot say how much of the effect is free NH3. The pig cells ran at pH 7.5. I did not check what tank pH the model assumes, so this is a gap, not a correction.
- **Selecting for tolerance is plausible but unshown.** Central already assumes cells selected for growth on the low-waste
  feed. Whether selection also lifts ammonia tolerance is open. I found no meat-cell evidence either way.

## 3. Ammonia: what the evidence supports

| | Value |
|---|---|
| Model | 5 mM (range 2–10) |
| Meat-relevant unadapted cells, 10% growth loss | about 1–3 mM |
| Meat-relevant unadapted cells, 50% growth loss | about 3–10 mM (catfish about 3; 3T3 about 8; HFF-1 about 10; pig and bovine FAPs unknown) |
| Meat-cell process set-points and levels reached | 2–3 mM held (Pasitka, quail); above 3 mM reached at 3–6 million cells/mL (Bodiou) |
| After selection or slow adaptation (hybridoma only) | 10–21 mM, with a growth cost in continuous culture |
| My median for Central's selected cells, at the level where growth loss is small | **3.5–4 mM** |
| My 80% interval | 2–8 mM |

- **Probability the model's 5 mM is within a factor of 1.5 of the truth** (3.3–7.5 mM) for meat cells at production density:
  **about 45%**. P(true value below 3.3 mM) ≈ 45%; P(above 7.5 mM) ≈ 10%. The evidence leans one way because every
  meat-relevant dose-response is at or below the model's value. The probability stays well above that of a random guess
  because Central's cells are selected, glutamine-free and fed gradually, all of which favour the model.
- **Weak spots in this reading.** Most meat-relevant doses were applied as a sudden spike on cells growing in serum, at low
  density, over days, with pH not reported. High-density serum-free perfusion has never been tested with meat cells. Two
  sources contradict the pattern (IMR-90 at 0.1 mM; mesenchymal stem cells growing faster at 5 mM). The pig result has two
  conditions and a confounded uptake change. The 10% loss level is my interpretation of what the model needs, not something any
  paper measured.
- **Cost of moving it** (Central, tank design held; best case in brackets where computed):

  | `pf_nh3_limit` | 7.5 | 5 (now) | 4 | 3.5 | 3.33 | 3 |
  |---|---|---|---|---|---|---|
  | Central $/kg | 22.45 | 29.42 | 33.99 | 37.19 | 38.50 | 41.45 |
  | Best case $/kg | 9.66 | 9.66 | 11.15 | | | 13.83 |

  The best case is unchanged above 5 mM, which I take to mean its cells make so little ammonia that lactate sets the medium (inferred from the numbers, not traced in the code).
- **The experiment that settles it.** Run the real cell line in a 1–2 L perfusion at 10–20% cells by volume, serum-free, with
  the medium made to hold ammonium constant at 2, 3, 4, 5 and 7 mM (add NH4Cl to the feed), tank pH fixed at the pH the model
  assumes. Run each level for at least 10 days, and record growth rate, viability and lactate. Repeat the 4 and 7 mM levels on
  cells that have spent four weeks rising slowly to that level. The pass criterion is the largest ammonium level at which
  growth stays within 10% of the 1 mM level. A 96-well dose-response at low density is cheaper but is the test that already
  exists in the literature. The perfusion version is the one that matches the model. My guess is $15–40k and two to three
  months.


## 4. Filter life: what the model assumes

`rt_membrane_life` = 3,960 L/m² = 5 L/m²/h for a 33-day run, one membrane per run. It is a throughput in the cost
(`$/L = price / life`) but a time in its derivation, and it does not move with flux. Central's membranes cost $8.3 of $29.4 a
kg. Prior notes already set the measured range: 450–1,200 L/m² for CHO at 50–75 million cells/mL (Veje, Pinto), 5,500 for
Clincke's best fibre (`filter_flux.md`, `retention_devices.md`).

## 5. Filter life: evidence added by this pass

L/m² figures marked *mine* are my arithmetic or the research agent's from the stated flux, area and days. The source gives no
L/m².

| Source | Cells and device | Density, flux, area | Life | Access |
|---|---|---|---|---|
| Madabhushi et al. 2025, Biotechnol Bioeng 122:1684, doi:10.1002/bit.28987 (PMC12152464), Merck | CHO, ATF or TFF, 0.2 µm PVDF (Asahi Microza), 3 L glass and 50 L XDR | 85–100 million cells/mL from day 10 to 28 (about 15–26% cells by volume, *mine*); 2 vessel volumes/day; large-scale flux about 4.4 L/m²/h; area not stated | Control and no-antifoam runs reached day 28. The excess-antifoam run "only lasted for 14 days after which the filter fouled completely". "Swapping filters only extends the culture duration by a couple of days." Antifoam, not cell density, is the paper's main cause | full for the quoted sentences, **checked** |
| Coffman et al. 2021, Biotechnol Bioeng, doi:10.1002/bit.27690 (PMC8248397), authors from Boehringer Ingelheim, Amgen, Pfizer, UCL and others | Industry framework for 500–2,000 L perfusion | 50–120 million cells/mL, 0.5–2 vessel volumes/day, 20-day lots | Its Table 3 lists "TFF 1000 L/m²" for the cell-retention filter. Text: sieving "can reach as low as 50%–60% transmission after only 20 days", and "the high cell density increased the rate of membrane fouling". Wide-pore fibres kept over 85% for 40 days | part, **checked** (Table 3 row and these sentences). I did not find prose saying what the 1,000 refers to, so I read it as a design capacity |
| Clincke et al. 2013 Part II, Biotechnol Prog 29:768, doi:10.1002/btpr.1703 (PMC3752935) | CHO in a 4 L wave bag, 0.2 µm TFF, 850 cm² | up to 1.3e8 cells/mL, 1e8 held a month | "In TFF#10 run, the 1st HF lasted 30 days, during which time filter fouling increased"; a second fibre was irreversibly fouled. Adds the sieving decline to Part I's 5,500 L/m² | full (agent) |
| Meissner application note 2026 (vendor), SepraPor | CHO DG44, 250 mL, ATF, 0.2 µm, 110 cm² | 60–80 million cells/mL, 1 vessel volume/day, about 1 L/m²/h (*mine*) | Run 2 fouled on day 11 (about 180 L/m², *mine*); run 4 ran 20 days with stable pressure (about 390 L/m², *mine*, not exhausted). Sieving still fell from 83% to 46% | full (agent), vendor document |
| Boehringer Ingelheim patent WO2017180814A1; Wang et al. 2019, Biotechnol J 14:e1800137 | CHO, TFF, 5–7 µm ceramic hollow fibre | density not stated | Conventional 0.2–0.65 µm fibres "must be replaced every 5-7 days". Large-pore fibre: 4,601 and 8,570 L/m² at plugging in two cell lines; patent claims up to 16,000 L/m² and 35 days | patent part (agent); paper snippet. I could not reopen the patent page, so these are the agent's read |
| Woodside et al. 1998, quoted in the patent | CHO, flat-plate membranes, 2–10 µm | 1–4 L/m²/h | Changed every 5–7 days: 120–670 L/m² (*mine*) | secondary |
| Walther, McLarty & Johnson 2019, Biotechnol Bioeng, doi:10.1002/bit.26811 | CHO, ATF | 40 million cells/mL | Above 60 L/m²/day (2.5 L/m²/h) the protein sieving coefficient fell by over 1% a day | abstract |
| Karst et al. 2020, Biotechnol Prog, doi:10.1002/btpr.3040 | 3,000 L N-1 perfusion, TFF | high density, number not in abstract | A pressure rise on the last day was reversible polarisation; a 30% cut in permeate flow cut pressure 75% | abstract |
| Pasitka et al. 2024, Nature Food 5:693, supplementary cost tables | Chicken fibroblasts, up to 130 million cells/mL, hollow-fibre ATF case | cost analysis for a 50,000 L plant | No filter-change data in what I could see. The cost table assumes 600 filter membranes a year on 50 ATF devices ($9.14/kg). The agent put this at about 3,600 L/m² per filter if all medium left as permeate through 11 m² units (*mine*, two assumed inputs) | part (abstract, figure legends, supplement) |

**Not found:**
- Any bovine, porcine, chicken or fish perfusion run with a measured filter life.
- Filter-change intervals from a cultivated-meat company or patent.
- How much life cleaning in place restores. Only qualitative reports: backflushing and a flow reversal help partly (Coffman citing Wang 2017/2019; Madabhushi at small scale), a flow step removes the cake for a few days (Clincke), and raised pressure did not restore sieving (Meissner).
- Full texts of Kelly 2014, Karst 2016, Wang 2017, WuDunn 2024 and Tavernier 2025 (paywalled or blocked). Pasitka's methods are paywalled.

### Reading

- **Small-pore fibres in dense CHO perfusion foul or lose sieving in about 6–30 days.** Sources: Meissner (11–20 days), Veje
  (3–6 days), Madabhushi's control (clean to day 28, but swaps buy only days), Clincke (30 days), Coffman (50–60% sieving by day
  20) and the patent (5–7 days). In L/m² that is about 180–2,500, with Clincke's best fibre the single case near 5,500.
- **Both a time limit and a throughput limit show up.** Meissner fouled at about 1 L/m²/h after 11 days and Veje at 8.3 L/m²/h
  after 4.5, so a lower flux does not buy proportionally more days. Walther and Karst show a high flux makes things worse per
  day. The model's single number cannot represent that. It treats life as litres per m², so lower flux would lower the
  area and not change the life.
- **Antifoam matters, and the model uses it.** Madabhushi's excess-antifoam run died at day 14 while the one without it ran to
  28. Central runs with bubble protectant and antifoam. I have not checked how their doses compare with the paper's.
- **The cell density in the best data is close to Central's.** Madabhushi's 85–100 million cells/mL is the same range as
  Central's 18% by volume, so this is not just the "thinner than 25%" caveat from `filter_flux.md`. The meat cells' size and
  stickiness are still unmeasured.
- **One counter-signal.** Pasitka's cost analysis implies filters lasting about 3,600 L/m², close to the model's value. That is a
  company's cost assumption, from my arithmetic with two assumed inputs, not a measurement. Large-pore ceramic fibres show
  4,600–16,000 L/m², at undisclosed density, with a different (unpriced) fibre.

## 6. Filter life: what the evidence supports

| | L/m² |
|---|---|
| Model | 3,960 (range 900–5,500) |
| Industry design capacity (Coffman) | 1,000 |
| Small-pore fibres, dense CHO, range of reports | about 180–2,500; best single fibre about 5,500 |
| Pasitka's cost assumption (my arithmetic) | about 3,600 |
| Large-pore ceramic (Wang 2019) | 4,600–16,000 |
| My median, one standard fibre at 18% cells by volume over a month | **about 1,500** (80% interval 500–4,000) |

- **Probability the model's 3,960 L/m² is within a factor of 1.5 of the truth** (2,640–5,940) for meat cells at production
  density: **about 20%**. P(true value below 2,640) ≈ 70%; P(above 5,940) ≈ 10%. The two research passes agree with each other
  and with the earlier 15–25% in `filter_flux.md`.
- **Why not lower.** Clincke's fibre, Pasitka's cost line and the large-pore data all sit at or above 3,960. If wide-pore
  fibres or backflushing are adopted, the model's value is fair.
- **Cost of moving it** (Central, tank design held):

  | `rt_membrane_life` L/m² | 5,940 | 3,960 (now) | 3,000 | 2,640 | 2,000 | 1,500 | 1,200 | 900 |
  |---|---|---|---|---|---|---|---|---|
  | Central $/kg | 26.64 | 29.42 | 32.08 | 33.58 | 37.58 | 43.09 | 48.59 | 57.75 |
  | Best case $/kg | | 9.66 | 10.51 | | 12.27 | | 15.79 | 18.73 |

- **The experiment that settles it.** Run 0.025 m² hollow-fibre modules (0.2 µm, and one wide-pore) on a 1–2 L meat-cell
  perfusion held at 15–20% cells by volume with the model's antifoam and protectant doses. Test at 2.5 and 5 L/m²/h, one module
  per condition and one replicate. Record pressure and product sieving against litres per m² and against days, to the point
  the pressure reaches the limit or day 33. Include one module that is backflushed daily. That separates the time limit from
  the throughput limit and gives the number the model uses. It takes about six weeks on a bench rig (my guess $20–50k). The
  cheaper partial test is the same run on CHO at Central's density, to check that meat cells foul no worse than CHO.

## 7. What it means for the model

1. **Both inputs sit at the favourable end of their evidence.** I would move neither range's ends. I would move the modes: the
   ammonia limit towards 4 mM, and the membrane life towards 1,500–2,000 L/m². That is a decision for Pablo. I have changed
   nothing.
2. **Size of the move, Central, tank design held:**

   | change | Central $/kg | best case $/kg |
   |---|---|---|
   | now (5 mM; 3,960 L/m²) | 29.42 | 9.66 |
   | ammonia limit 4 mM | 33.99 | 11.15 |
   | membrane life 2,000 L/m² | 37.58 | 12.27 |
   | membrane life 1,500 L/m² | 43.09 | |
   | both (4 mM; 2,000 L/m²) | 44.67 | 14.69 |
   | both (4 mM; 1,500 L/m²) | 51.86 | 17.08 |

   The two compound because less ammonia tolerance means more medium and more permeate, and so more membrane.
3. **The filter is the larger move.** Moving the ammonia limit by 20% adds $4.6 to Central. Moving filter life to 2,000–1,500 L/m² adds
   $8–14. Its evidence is also better, with a design figure from industry (1,000), a large-scale study at the model's own
   density, and a prior pass that reached the same conclusion.
4. **What would change my view.** A bovine or chicken line shown to hold 10% growth at 5 mM or more in perfusion, or a month on
   one filter at 15–20% cells by volume, would move me back. Each of the two experiments above could do it, so each is worth
   more than further searching.

## 8. How far this was checked

- Re-opened by me: Slivac 2010 (Table 1), Qiu 2026 (preprint text), Coffman 2021 (Table 3 row and sieving sentences),
  Madabhushi 2025 (density, flux and the quoted sentences). The search summaries for Cruz 2000, Yang & Butler 2000, Newland 1994
  and Matsumura 1991 agree with the agent's numbers.
- Taken from the research agents without reopening: Moreno-Sánchez 2020, Bodiou 2025, Jacobtorweihe 2025, Takahashi 1985,
  Stern 2017/2019, Doyle & Butler 1990, McQueen & Bailey 1990, Clincke Part II, Meissner, the patent and Wang 2019, Walther,
  Karst 2020, Pasitka's supplement. The agents' L/m² conversions are marked *mine* and I have not re-derived them.
- The free-NH3 fractions in Section 2 use a pKa I did not source.
- Probabilities are my judgement from the evidence above, not from a model.
