# Five operating modes of animal-cell culture: evidence for a cultivated-meat cost model

Compiled 2026-11-15. About 40 tool calls. Repo notes (Continuous harvest bioreactor progress/*, perfusion_rate_osmolality.md, co2_sparging_settling.md, cost_scenarios.md, cheap_plant_study.md) were read first; findings already in them are cited as "repo" and not repeated.

**Labels.** Evidence type: MEASURED (experiment, reported), VENDOR (supplier claim), REVIEW (review/trade-press claim), MODEL (design study/techno-economic assumption), INF (my inference or arithmetic).
**Access levels.** *read in full* = I opened the page and nothing was cut; *read part* = opened but through the fetch tool's extract (WebFetch returns a model summary, not raw text, so treat as "read part" even when the whole page was fetched) or truncated; *abstract only*; *snippet* = search-result summary only; *secondary* = number comes from another document in the repo or another article quoting it. No source below is "read in full" in the strict sense; Humbird 2021 and Clincke 2013 Part II were fetched whole but through the extract tool. Two searches/fetches (cell-loss-in-permeate query; Thermo perfusion-hardware PDF) failed with an API error and were not retried in the same wording.

---

## 0. Summary table (proposed model inputs, all INF unless a source is given)

| | Batch | Fed-batch | Fill-and-draw | Chemostat + bleed | Perfusion + retention |
|---|---|---|---|---|---|
| Inoculum as share of final density | 2-5% (CHO 0.3-0.5e6 to ~1-2e7; Brenner 2026 model ~2%) | 3-5% pharma; 25% Humbird (two doublings); 50% with intensified N-1 seeding (10e6) | 50% (f = 0.5, set by the model); patents quote 30-80% drawn | n/a (steady state) | n/a (steady state after a start-up phase) |
| Doublings per cycle | 4.3-5.6 | 5 pharma, 2 Humbird | ln(1/(1-f))/ln2 = 1.0 at f = 0.5 | continuous | continuous |
| Cycle / run length | 3-7 d (INF from doubling count and 24-h doubling; pharma "10-14 d" is fed-batch) | 10-14 d pharma (REVIEW), 7 d intensified | cycle = 1 doubling time plus lag; run = N cycles (unknown, see 1c) | weeks (planning bound 20-40 d, INF) | 30-100 d (REVIEW); Humbird design about 33-36 d between turnarounds (INF from 10 x 72 h, 91% uptime) |
| Turnaround | 10 h (Humbird via repo inputs.py); 24-48 h is more usual in pharma but I did not find a source | same | at each reset only | at each reset | 72 h (Humbird 2021, read part) |
| What stops it | substrate, lactate/ammonia, osmolality, CO2 | ammonia/lactate, osmolality, CO2, viability decline | waste build-up between draws; contamination; drift | washout, contamination, drift | fouling, contamination, cell ageing, planned campaign limit |
| Density attained (animal cells) | CHO ~1e7/mL (recall, not sourced here) | 15-22e6/mL CHO (snippets, Clincke) | caps at batch-like level | batch-like level at D < mu_max (see 6) | 1-2e8/mL CHO (Clincke 1.0-1.3e8 at 5.5 RV/d; 2.1e8 at 8-10 RV/d, repo) |
| Largest animal-cell run found | 25 m3 | 25 m3 | 20 m3 (Vow, option stated in dossier; frequency of use unknown) | lab (about 1 L class) | 4 m3 (Genzyme Geel) |

---

## 1a. Cycle structure and times

### Pharma CHO
- **Fed-batch seeding and length.** Conventional fed-batch starts at about 0.5e6 cells/mL and runs about 14 days; seeding at 10e6 from a perfusion N-1 shortens it to 7 days. Source: Repligen ESACT 2019 poster, https://cn.repligen.com/_default_upload_bucket/ESACT_HD-HPH_Final_02May19.pdf — *snippet* (via search summary). Another group's "10-20e6 seeding" and "2-10e6 seeding shortens the run" claims are from the same search summary (*snippet*, source not opened). REVIEW/VENDOR.
- **Fed-batch peak density.** Merck media study: 20-22e6 cells/mL on day 7 with Cellvento 4CHO; 14.5-17.5e6 by day 10 with others. https://www.merckmillipore.com/UY/es/technical-documents/technical-article/pharmaceutical-and-biopharmaceutical-manufacturing/media-development/fed-batch-yields-in-upstream-bioprocessing — *snippet*. VENDOR.
- **Fed-batch comparison run.** 0.8e6 seed, maximum 15-18e6 cells/mL, harvest at 12 days. Clincke et al. 2013 Part II (identified by matching numbers with repo perfusion note ref [2]), https://pmc.ncbi.nlm.nih.gov/articles/PMC3752935 — *read part*. MEASURED, 2 L.
- **Turnaround.** Nothing sourced for 20 m3 stainless. A vendor blog (Alicat) puts same-product changeover on reusable equipment at 6-10 h; Cytiva and Pall say stainless needs longer turnaround because of CIP/SIP (https://www.alicat.com/should-i-switch-to-single-use-bioreactors/, https://www.pall.com/br/pt/biotech/blog/single-use-stainless-steel-bioreactor.html) — *snippet*, VENDOR. Not found: any measured hours for 20,000 L CHO. Searched: "stainless bioreactor turnaround CIP SIP hours 20,000 L". The repo's 10 h is Humbird's figure (repo inputs.py cites "Humbird-R Sect. 4.2"; I did not open that document).
- **Plain batch (no feed).** Not found with a primary source for CHO (searches returned fed-batch only). The model's batch peak of ~1e7/mL is my recall.

### Humbird 2021 (Biotechnol Bioeng 118:3239), https://pmc.ncbi.nlm.nih.gov/articles/PMC8362201 — *read part* (fetch extract). MODEL
- Fed-batch: 80% working volume of a 20 m3 vessel; wild-type cells "after two cell mass doublings, the batch ends with 5 mM NH3" (Sect. 2.2.5, Fig. 4a); enhanced cells reach about 110 g/L before NH3 inhibition. The extract found no inoculation fraction, cycle time or turnaround in this paper; the repo's inputs.py takes 482 to 1,849 kg growth (a factor of 3.8, 1.9 doublings, inoculum about 26% of final) and 10 h turnaround from the longer engrXiv report (secondary).
- Perfusion: seed trains of 125 L and 500 L in fed-batch; the production vessel is first run fed-batch to about 120 g/L, then perfused; steady-state share of time about 91%; 10 scheduled 72-h turnarounds per year; 2 m3 vessels, 96 of them (197 m3); harvest 9 kg/h wet cell mass per vessel; dual ATF-10 at 1 RV/d gives 195 g/L; one ATF at 0.5 RV/d gives 140 g/L; ATF-10 "up to 1000 L/d"; ATF membrane replacement $16k each, 20 per bioreactor per year. No contamination or chemostat/draw-fill content in this paper (neither term appears).
- INF: run between turnarounds is (365 d x 0.91 / 10 =) about 33 d of steady state, about 36 d including each turnaround.

### Cultivated-meat reports
- **Brenner et al. 2026**, "Decoding cultured meat manufacturing: a full process model", Front. Nutr. 13, doi:10.3389/fnut.2026.1844185, https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2026.1844185/full — *read part* (first 100k of 128k characters). **New relative to repo.** MODEL, batch only, fed-batch/perfusion explicitly not modelled. Train from cryovial to 20,000 L: stage durations fixed at 120 h each, 724.8 h total expansion (30.7-d batch); doublings per stage 5.64, 4.00, 3.97, 3.32, 3.00, 5.64 (last stage 2e13 to 1e15 cells at 5e7 cells/mL, 105-110 g/L); final stage inoculum 2e13 cells into 20 m3 is about 1e6 cells/mL, i.e. 2% of final (INF arithmetic). About 2,000 kg per batch. Contamination rate, turnaround, uptime: not reported. Useful for (i) batch inoculation fraction and doublings and (ii) restart cost from a vial: about 30 d (matches repo's 21-30 d).
- **Humbird/fed-batch, Believer/Pasitka 2024, SuperMeat 2024, Vow:** see repo. New attempt this pass: Nature Food page redirected to a login wall (not read); no new Pasitka numbers. Repo already has Pasitka's SI retention costs.
- **Vow draw-and-fill, cycle data.** Not found. The FSANZ dossier (repo) names the option but gives no densities or cycle times. Search snippets (secondary, unreliable and mutually inconsistent): a Wikipedia mirror says a "four-week process"; one 2025 report says up to 2,200 lb (about 1 t) per month from the 20,000 L reactor and another says more than 1,200 lb in one week; the FoodNavigator 538 kg "single harvest" is in the repo. INF: 538 kg per harvest at about 1 t/month would mean roughly two harvests a month, which is closer to batch/complete-harvest than to daily draw-and-fill; the sources conflict and I give this little weight. Probability that Vow's routine mode at 20 m3 is draw-and-fill with several draws per run: about 35%; complete-harvest batches: about 65%.

### Fill-and-draw definition in the patent literature
- "Fill and draw closely resembles repeated batch; typically 30-80% of tank volume removed, then about the same volume of fresh medium added; phases can be continued indefinitely." US 10,844,345 (high-density fill-and-draw fermentation; probably a microbial process), https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10844345 — *snippet*. Repo also has US 9,212,214: typically 80%. MODEL/claim only; "indefinitely" is not a measurement.
- Mammalian "intermediate harvest" fed-batch with data (not fill-and-draw but closest measured repeated-harvest CHO): Frontiers Bioeng Biotechnol 2023, 10.3389/fbioe.2023.1211410, https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2023.1211410/full — *read part* (100k of 124k characters). 3 L working volume; six 2-day cycles over 17 d; re-seeded to 20e6 cells/mL after each harvest via a cell-retaining harvest; peak 31-41e6; viability above 93% (PerfM) until day 17; ended by plan after six repetitions; contamination and stability not reported. MEASURED, bench.

## 1b. Run lengths in days, and why runs end

| Mode | Run length | Reason it ends | Source and access |
|---|---|---|---|
| Batch | 3-7 d (INF); pharma fed-batch 10-14 d | nutrient/by-product limit, by design | see 1a |
| Fed-batch | 10-14 d | same, plus viability decline | Repligen poster (*snippet*); BPI 2016 (repo) |
| Fill-and-draw | not found (number of cycles before a full reset; no published cultivated or pharma figure) | contamination (INF), wall fouling or biofilm (INF), drift/ageing (INF) | searched "repeated batch / semi-continuous / draw and fill ... number of cycles"; only patents and a bench repeated-harvest paper returned |
| Chemostat | animal cells: HeLa dialysis chemostats to 40 d (1965, repo); CHO continuous study lysed cells accumulated over 200 h (repo); no production-scale figure | not found | repo |
| Perfusion | 30-100 d (BPI 2016, repo); rFVIII campaigns "months" (repo); 47-d run, TFF, and 30-d ATF runs at bench (Clincke Part II, *read part*) | hollow-fibre or spin-filter fouling (BPI history, repo), device failure (swappable ATF), planned cell-age limit, contamination | |

- **Cell age (genetic drift) as an end of run.** No universal CHO limit exists: it is set per process by the "limit of in vitro cell age", tested once at banking (ICH Q5B/D). An industry study aged lines for 30, 60 and 90 doublings (about 60 d) and saw up to 13% of host-cell proteins vary with age. https://www.biopharminternational.com/view/risk-based-genetic-characterization-strategy-recombinant-cho-cell-lines-used-clinical-and-commerci-0 — *snippet*. REVIEW. Repo has the 220-generation drift thesis.
- **INF (doublings arithmetic).** Seed train from vial about 20-25 doublings. A perfusion or chemostat run of 30-60 d at 1.5-2 d doubling adds 15-40 doublings; fill-and-draw at f = 0.5 adds one doubling per cycle, so 30 cycles is 30 doublings. All are within the 60-90 doubling range tested in CHO. Cell-age is therefore unlikely to be the first limit for immortalised or CHO-like lines in runs under 60 d (credence 70%); for primary or finite-lifespan cultivated-meat lines it is unknown.

## 1c. Fill-and-draw: cycles before reset
Not found in any source. My planning prior (INF, low confidence): 20-60 cycles (20-60 d at 24 h) before a forced reset, set by contamination hazard rather than ageing. P(a published cultivated-meat or pharma fill-and-draw run of at least 20 cycles at 1 m3 or above exists) about 25%.

---

## 2. Density reached and what stops it

- Fed-batch CHO: 15-22e6/mL (above). Perfusion CHO: 1.0-1.3e8/mL at 5.5 RV/d in 11-12 d with 2.5 pL cells (Clincke II, *read part*): that run's growth stopped at pCO2 34 kPa in one run; the other drivers (viscosity at ~0.37-0.5 packed fraction, oxygen) are in the repo.
- Wild-type, no waste engineering: Humbird gets only about 7 g/L (fed-batch, ammonia 5 mM) and about 20 g/L (perfusion at 2 RV/d); enhanced cells 110 g/L (fed-batch) and 195 g/L (perfusion at 1 RV/d, O2-limited). *read part*. MODEL.
- GFI 2023 survey (22 respondents, early 2023), https://gfi.org/resource/trends-in-cultivated-meat-scale-up-and-bioprocessing/ — *read part*: reported or estimated yields 5-10 g/L up to 300-360 g/L (Believer, 2 L, estimated); proliferation modes: fed-batch 13, batch 10, "continuous processing" 10, perfusion 8 (multiple selections). REVIEW/company claims. Draw-and-fill not mentioned.
- Brenner 2026 batch model at 20 m3: 105-110 g/L, 5e7 cells/mL. MODEL, assumption, not measurement.

## 3c. Loss behaviour

### Contamination rates (new vs repo)
- Repo already holds: Powell 2025 (11.2% of batches lost, 19.5% beyond flasks, run length unstated); Harsini & Swartz 2-5%/5-10%/>10% all-cause; BioPlan 2.3% contamination for >=1,000 L (2008) and about 3.2% of failures in 2022; Humbird "about 2%"; Lim 2006 10% contamination and 10% fouling assumed for spin-filter perfusion with a 3% break-even; BioPlan 2011 perception data (63.9% worried about perfusion contamination versus 3.8% for fed-batch).
- **Not found:** any measured contamination rate by operating mode at production scale (BioPhorum, BioPlan primary data, CAACB tables by process type). Searched: "BioPlan perfusion vs fed-batch contamination incidents", "BioPhorum continuous contamination risk", "Pollock 2013 failure rates". The CAACB survey collected process type per event but I found no published split. Pollock 2013's perfusion failure assumptions are in the paper but I could not extract them.
- **One production anecdote (new):** a stainless-steel, steam-traced perfusion plant (two systems at 20 RV/d each, volume not stated) found endotoxin in product after four months; contamination was "not rampant", the onset could not be dated, four months of product were quarantined and then dumped, "millions of dollars" of medium; the company switched its next product to fed-batch. https://www.bioprocessonline.com/doc/be-better-prepared-with-your-new-continuous-manufacturing-perfusion-system-than-we-were-0001 — *read part* (fetch extract). REVIEW/opinion column, one case.
- **Qualitative trade claim:** perfusion has the longer exposure and more interventions, but a contaminated perfusion run still keeps the product harvested before onset, whereas fed-batch loses the whole batch (*snippet*, several trade sources via BPI/GEN, not opened).
- **INF, hazard translation.** Pharma batch contamination loss about 2% per 12-14 d batch is about 0.15-0.2% per day (repo pf_hazard_pharma = 0.2%). At the same per-day hazard: P(run lost) = 1-exp(-h T) is 6.8% for 35 d, 11% for 60 d, 2.7% for a 14-d batch. If the hazard per day were instead 3x higher in continuous operation (more connections and longer exposure), a 35-d run loses about 19%. I would put 60% on "per-day hazard in continuous modes is higher than in batch", 30% on "same", 10% on "lower".
- **INF, what a lost run costs differs by mode.** In batch the batch is lost (biomass accumulated so far, on average about half a batch, plus restart). In perfusion, chemostat and fill-and-draw the product is harvested continuously, so only the standing crop is lost: standing crop / harvest rate = 1/mu days of output (1.4-3 d at mu 0.5-0.23 d^-1), plus restart. The dominant cost is the restart: about 21-30 d if the seed train must be regrown from a vial (Brenner 2026 model gives 30.7 d from a cryovial; repo 14-30 d), shorter if a seed vessel is held. So per-event loss is mostly "days of downtime x tank output", nearly the same in all modes; mode matters through how many events occur (run length x hazard) and through what is in the tank. Probability this framing is right to within a factor of 2 for the loss per event: 65%.
- **Start-up failure.** UPSIDE: a run fails if the seed is not sterile (repo cheap_plant_study ref 14). Applies to every restart, so it penalises short runs per day of operation (a batch needs a fresh seed each 4-14 d; a perfusion run once per 30-60 d).

### Physical cell losses
- **Product yield with bleed (mAb, not cells).** Clincke II, TFF#10 (47 d) share of total mAb produced: harvest 52%, bleed loss 32%, residual 16%; ATF#9: harvest 71%, bleed 22%, residual 7%; production yield about 54-71% (ATF) and 46-56% (TFF) at 25e6 cells/mL; without bleed Y_prod 86-92% but the harvested concentration fell to under 50% of target after 10 d. *read part*. MEASURED, 2-4 L. For a cell product the bleed is the product; INF: the relevant loss is only cells that die or go to permeate, not the bleed.
- **Cells lost through the retention device (percent of mass).** Not found. Searched three ways ("ATF retention efficiency permeate", "TFDF cells passing", "settler retention percent"). Known items: repo has inclined-settler retention 96-99% in a small avian-cell system; Centritech lab centrifuge viable-cell recovery never below 98% but dead-cell recovery about 80% (abstract record, https://scilit.com/publications/c56be3822ac5641f0942b24c09e28582, via search summary — *snippet*, MEASURED lab). INF: hollow-fibre 0.2 um devices retain essentially all cells (permeate loss under 1% of cell mass), but I could not source this; credence 80%.
- **Cell death in the bleed/harvest.** No quantitative figure. Clincke II viability "mostly 90-95%" in perfusion (repo). The chemostat HeLa data: no viability given in what I could read.
- **Cell-specific perfusion rate.** In repo (50-60 pL/cell/d typical; 8-30 at best). Not repeated.

---

## 4. Retention devices (perfusion) and scale

All $ are vendor or derived unless stated. Repo already has the inclined-settler, acoustic and Romann information; additions are marked NEW.

| Device | Capital | Capacity and largest scale | Fouling/lifetime | Source and access |
|---|---|---|---|---|
| ATF-10 hollow fibre (Repligen) | Pasitka SI: 50 units = $17.5M, i.e. $350k per unit, one per m3 of a 50 m3 plant (INF, repo secondary). A reseller lists the stainless device alone at $9,999.98, used/listing unverified (https://mbglick.com/shop/repligen-xcell-atf-10-stainless-steel-device-atf-cell-retention-system/, *snippet*). The 35-fold gap is probably skid, controller, installation and single-use modules versus a bare device; unresolved | ~11 m2, 30-80 L/min ATF flow, "up to 1000 L/d" perfusion per unit (Pollock via Humbird); rated 200-5,000 L (vendor); "scaled up to 5000 L" (vendor, repo); 2,000 L needs "multiple parallel ATF" (Romann 2024, repo); Sartorius 2,000 L perfusion example names ATF modules, run unnamed (Sherman 2016, https://www.bioprocessintl.com/perfusion-cell-culture/continuous-cell-culture-operation-at-2-000-l-scale, *read part*; NEW) | Humbird: 20 membrane replacements per bioreactor per year at $16k each (INF: one every 18 d per bioreactor, or every 36 d per device if two per vessel); Romann: TFF may need several months without cleaning at about 2 L/m2/h (repo) | |
| TFF (levitated pump) | Pasitka SI: 10 units $1.75M ($175k each, $35k/m3 at 50 m3, INF); 2 "large-scale" units $2.42M (about $1.2M each, $48k/m3) | "preferred at large scale" (Romann, repo); TFDF rated 1-2,000 L (vendor, repo) | as above | repo |
| Inclined plate settler | not found | 3,000 L N-1 at 15.8e6 cells/mL; 2,000 L bleed-recycling settler (40 channels); overflow velocity about 1 cm/h (repo) | no membrane to foul; residence time 1-1.5 h, retention 96-99% small scale, growth penalty (doubling 26-32 h vs 25 h ATF) (repo) | repo |
| Acoustic (BioSep) | not found | 1-1,000 L/d vendor; tested to 200-400 L/d (repo); larger "very difficult" because of power | no fouling; heating limit | repo |
| Disc/continuous centrifuge (Centritech Cell II, Pneumatic Scale Angelus; Kendro) | not found | Cell II is a single-use-insert continuous centrifuge for perfusion and harvest; the vendor pages give no L/h I could read; Kendro: nothing found (searched) (https://www.pharmaceutical-tech.com/products/pneumaticscaleangelus/carr-centritech-separation-systems, *snippet*; NEW) | no membrane; viable recovery 98%+ (lab model) | |
| Hydrocyclone | not found | listed as "more recently" used (2002 review, abstract record https://pubmed.ncbi.nlm.nih.gov/11991177/ via snippet) | | |
| Spin filter | cheap | filter area does not scale with volume; largely abandoned (BPI history, repo) | run ends when the screen fouls | repo |
| Cultivated-meat alternatives | Ever After Foods packed bed, Mission Barns adherent "built-in perfusion" (cells held on a substrate: no separate retention device); Mission Barns reports "100+ successful runs" in San Francisco, volume and failure count not stated (AgFunderNews, 15 Aug 2024, https://agfundernews.com/mission-barns-unveils-novel-scalable-adherent-bioreactor-for-cultivated-meat-fat, *read part*; NEW detail) | | | |

INF: at ATF-10 capacity (1,000 L/d per unit) a 20 m3 tank at 1 RV/d needs 20 units; at Pasitka's $350k per unit that is $7M ($350k per m3 of tank, about 4 times the repo's pf_capex_retention of $89k/m3, which assumes a cheaper device). At TFF numbers ($35k/m3) the retention hardware would be small. The ATF capex sits within a factor of 10 of the repo's, so capex of the retention device per m3 should be treated as spanning $35k-350k/m3 with the central estimate depending on which Pasitka line is believed.

## 5e. Continuous harvest at 20-50 m3 in animal cells

- Largest animal-cell perfusion found: two 4,000 L perfusion bioreactors at Genzyme Geel (2003-2005), retention device not named (repo). 2,000 L is the norm for modern single-use perfusion (Sartorius 2016, BPI; repo Romann 2024). Vendors offer 3,000-5,000 L single-use vessels aimed at perfusion (Thermo HyPerforma DynaDrive 5,000 L, https://www.rdworldonline.com/thermo-fisher-scientific-launches-new-larger-hyperforma-dynadrive-s-u-b-s-for-cell-culture-production/, *snippet*, VENDOR; NEW) with 2,000 L the "commonly accepted" commercial single-use maximum (BioPharm, *snippet*).
- Nothing new found for Genzyme/Sanofi beyond the repo; no 8,000 L mode confirmation. Quorn is a fungus (155 m3 airlift, about 1,000 h; repo): non-animal.
- Cultivated meat: no perfusion or chemostat above 10 L reported (repo); Brenner 2026 model is batch-only; the Believer plant (20,000 L vessels, unvalidated) failed (repo).
- **Probabilities (INF).** (i) An animal-cell perfusion run of at least 1 month at 4 m3 or more has been run commercially: 90% (Geel). (ii) At 10 m3 or more: 6%. (iii) At 20 m3 or more: 2-3%. (iv) A cultivated-meat company has run perfusion of at least a month at 1 m3 or more: 20% (Believer's 2,000 L is unknown; Ever After/Mission Barns' modes are not suspension perfusion). (v) A cultivated-meat 20 m3 vessel has run a continuous, no-retention mode (chemostat or multi-day draw-and-fill) for at least 4 weeks: 20-25%; I find no evidence either way, and Vow's dossier lists draw-and-fill as an option.

## 6. Chemostat for animal cells

- **Evidence (all lab):** mouse LS cells, steady-state maximum density at D = 0.30-0.35 per day (1973-74; J Gen Virol 20:29, repo and *snippet*); HeLa chemostat (Korean J. Biotechnol, 1989), *abstract only*, https://koreascience.or.kr/article/JAKO198911922248747.page: maximum cell density at D = 0.020 per h, washout at 0.050 per h, maximum cell productivity (mL cells per L per h) at D = 0.030 per h, so productivity peaked at about 0.6 of the washout rate (0.020/0.050 = 0.4 for density); at low D the culture needed a "maintenance period", deviating from theory (abstract, with an inconsistent 0.012 in the Korean text). MEASURED, lab, reactor volume not stated. Other items (HeLa dialysis chemostat 40 d at 1.2e6/mL; CHO lysed cells 8e5/mL after 200 h; patent CHO D mean mu about 0.22/d) are in the repo.
- **Dynamics:** mammalian continuous cultures show multistability, hysteresis and sharp metabolic transitions; dilution-rate/cell-density ratio is a better control variable than D (modelling, PLoS Comput Biol 2017 and Maximum-entropy 2018, via search snippets of https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6411232/; *snippet*; MODEL). Washout is abrupt if D > mu_max, so margin is needed.
- **Realistic D/mu_max (INF):** 0.4-0.7 for maximum biomass productivity; central 0.5. With mu_max 0.7/d (24-h doubling) that is D about 0.35/d, matching the 0.3-0.35 per day measured for LS cells. P(D/mu_max of 0.5 +/- 0.2 is where a food-grade chemostat would sit) 70%. Above 0.8 I expect instability or a growth-rate decline (P 75%).
- **Productivity and medium (INF):** chemostat output per m3 = D x X_ss. Medium use per kg of cells = 1 / X_ss litres per kg, the same as batch at the same density; so, with no waste washout beyond what cells and spent medium carry out together, X_ss is capped like batch (inhibitor-limited), unlike perfusion. The repo already makes this point; I confirm nothing in the 2026 literature contradicts it.
- **Scale:** not found for animal cells above lab scale. P(a commercial retention-free chemostat of animal cells above 1 m3 ever ran for at least a month) about 10%. The microbial exception (Quorn) ended runs after about 30-40 d because of mutant variants (repo).
- **Drift and loss risks:** washout from a contamination or a stir/gas failure; selection for fast growers (benign for biomass); lysed cells accumulate (CHO continuous study, repo); wall growth.

## 7. New relative to repo notes, 2025-2026 (cultivated meat)

All CO/PRESS/search-summary unless stated. Access is *snippet* for all except where marked.
- **Brenner et al. 2026 process model** (above), *read part*; MODEL; the only 2026 peer-reviewed full-process model I found. It confirms batch inoculation at about 2% of final and 5.64 doublings in the 20 m3 stage.
- **Meatly (UK):** 20,000 L pilot in London planned, Series A GBP 10.4M (Food Manufacture, 7 May 2026, https://www.foodmanufacture.co.uk/Article/2026/05/07/meatly-is-planning-to-open-a-20000-litre-pilot-cultivated-meat-site-in-london/); pet food 2027. Repo had only the 320 L pilot.
- **Orbillion Bio and Solar Biotech:** plan 20,000 L, "over 4 million lb per year" (vegconomist, about July 2026, date inferred from image paths).
- **Organoid Farm (Japan):** 200 L scaffold-free beef trial, Green Queen 5 May 2026; plant 2028 (https://www.foodbusinessmea.com/japans-organoid-farm-completes-200-litre-cultivated-beef-trial-ahead-of-2028-plant-launch/).
- **Magic Valley (Australia):** expanded pilot with 3,000 L bioreactors, 150,000 kg per year claimed (vegconomist).
- **Ever After Foods and Roslin Technologies:** claim up to 19-fold higher protein and dry-biomass productivity versus a stirred-tank benchmark with an edible packed-bed scaffold (2026, foodingredientsfirst). Company claim; not suspension culture.
- **The Cultivated B:** AUXO V reported to have started manufacturing at its Burlington, Ontario plant (undated); delivery lead times up to two years.
- **Ark Biotech:** TEA claiming parity (about Aug 2026). TEA, not a run.
- **Mission Barns:** pilot has "100+ successful runs" (Aug 2024; the repo had the 2025 approvals but not this).
- **Not found in 2026:** any new numeric data for Mosa Meat (1,000 L, Bluu 1,000 L trout harvest are in the repo), Aleph Farms, Wildtype, Gourmey beyond the repo, Meatable (closed Dec 2025, repo), any peer-reviewed report at 100 L or above. Searched two combined queries on named companies and "cultivated meat news Oct-Nov 2026": nothing dated after July 2026 surfaced. P(missed a 2025-26 peer-reviewed cultivated-meat paper with at least 100 L data): about 15% (same as repo).

---

## 8. Judgement calls and probabilities (INF, my numbers)

| Call | P |
|---|---|
| Per-day contamination hazard in 30-60 d continuous operation exceeds that of 10-14 d batch operation at the same plant standard | 60% (30% same, 10% lower) |
| Cost per contamination event is dominated by restart days, not by tank contents (continuous modes) | 70% |
| Fill-and-draw at f = 0.5 sustains at least 20 cycles at 20 m3 without forced reset | 50% (no evidence) |
| A food-grade chemostat reaches a steady state above 50 g/L wet without waste-reduced cell lines | 15% (repo gives 25% for fill-and-draw/chemostat; I agree it is low) |
| Animal-cell perfusion at 20 m3 has been run for a month anywhere | 2-3% |
| Retention-device capital at 20 m3 is between $35k and $350k per m3 of tank (with Pasitka SI as sole anchor) | 70% |
| Cell age limits a 30-60 d run for immortalised lines | 30% |

## 9. Not found (what I searched)
- Plain-batch CHO inoculation and peak with a primary source; turnaround hours for 20 m3 stainless CHO plant (3 queries).
- Contamination or failure rates by mode at production scale: BioPhorum, BioPlan primary, CAACB split by process (3 queries).
- Pollock 2013 and Lim 2006 per-run failure assumptions in the text (abstract level only).
- Cell loss to permeate for ATF/TFF/TFDF/settler (3 queries; one failed with an API error).
- Centritech Cell II and Kendro throughput and price; hydrocyclone data (1 query).
- Fill-and-draw cycles to reset in any animal-cell process (2 queries).
- Animal-cell chemostat above lab scale (2 queries).
- Pasitka full text (login wall); Vow draw-and-fill cycle data; any new Genzyme/Sanofi perfusion volumes.

## 10. Source list with access level

- Humbird 2021, https://pmc.ncbi.nlm.nih.gov/articles/PMC8362201 — read part (fetch extract).
- Clincke et al. 2013 Part II, https://pmc.ncbi.nlm.nih.gov/articles/PMC3752935 — read part.
- Brenner et al. 2026, https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2026.1844185/full — read part.
- Frontiers Bioeng Biotechnol 2023 intermediate harvest, https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2023.1211410/full — read part.
- GFI trends page, https://gfi.org/resource/trends-in-cultivated-meat-scale-up-and-bioprocessing/ — read part.
- Sherman et al. 2016 (Sartorius), https://www.bioprocessintl.com/perfusion-cell-culture/continuous-cell-culture-operation-at-2-000-l-scale — read part.
- BioProcess Online perfusion contamination column, https://www.bioprocessonline.com/doc/be-better-prepared-with-your-new-continuous-manufacturing-perfusion-system-than-we-were-0001 — read part.
- AgFunderNews Mission Barns, https://agfundernews.com/mission-barns-unveils-novel-scalable-adherent-bioreactor-for-cultivated-meat-fat — read part.
- HeLa chemostat 1989, https://koreascience.or.kr/article/JAKO198911922248747.page — abstract only (read part).
- Repligen ESACT poster, Merck fed-batch article, Alicat/Pall blogs, Thermo DynaDrive, Centritech, patent US 10,844,345, ICH/CHO age (BioPharm), chemostat dynamics (PMC6411232), Food Manufacture/vegconomist/Green Queen 2026 items — snippet only.
- Pasitka SI retention costs, Vow dossier, Genzyme Geel, BPI/BioPharm 2016, Romann 2024, Powell 2025, Lim 2006 — secondary (via repo notes).
