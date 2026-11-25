#!/usr/bin/env python3
"""
study_assumptions.py — what each published cost study assumes, and Humbird's design with one study's assumptions at a time.

Why
---
The published cost analyses of cultivated meat disagree by orders of magnitude, mainly on a handful of assumptions: the price
of the medium, the cells (waste, doubling time, weight), the density, the size and kind of tank and how it is run, the grade
and cost of the plant, and the financing. The owner (2026-11-20): "I think it would be useful to build as modifications over
Humbird: eg Humbird but with cheaper media. Label them with the TEA they refer to."

What is here
------------
STUDIES          one entry per study: name, year, citation, the system it models in one plain sentence, its own reported
                 cost with its basis, and the assumptions that separate the studies, each with a source reference. Only values
                 read in the source are recorded. A value worked out from them says "derived" and shows the arithmetic. What
                 a study does not state is left out. "PDF page" is the page of the PDF file in Cultivated_meat_TEAs/, not the
                 number printed on the page.
modifications()  an ordered list of modifications over HUMBIRD'S BEST ESTIMATE (the page's starting point "humbird_best":
                 humbird_check.page_start(), his Table 4.7 design on hydrolysate, like for like in today's dollars), each
                 labelled with its study and expressed in the page's own lever vocabulary:
                     traits   {trait: value in the model's unit}          (the page's tpSetTrait)
                     held     {key: value in the slider's unit}           (tpSetHeld; build_interactive.PAGE_PARAMS, capex_x,
                                                                           medium_price)
                     plant    "lean" | "sterile" | "pharma"               (tpSetPlant)
                     vm       [vessel, way of running it]                 (tpSetVM)
                     device   a retention device                          (tpSetDevice)
                 An assumption the levers cannot represent carries `not_representable` and the reason, and no settings.

The starting point is his own published best estimate: fed-batch in 20 m3 stirred tanks, clean rooms, 7.5% over 10 years,
soy hydrolysate, growth factors bought (rebased 2026-11-20; until then the base was this model's perfusion variation on his
cells, and the first modifications put his own assumptions back).

STUDY_LEVERS     what each study assumes on each lever of the all-favourable case (scenarios.favourable_levers), with its page.
LIMITS, REJECTED the named limits of the model, and every study value that breaks one: the study, the assumption with its page
                 reference, the limit, the value against the limit and the limit's source. A rejected value is not a source for
                 scenarios.all_favourable().
ESTIMATES        each study's own most favourable published estimate, its basis, the year of its dollars, and `estimates()`:
                 the same as a kilo of wet cells in today's dollars (US consumer prices, CPI below; Humbird's by the model's
                 own two escalation inputs).
EXCEPTIONS       the studies whose estimate is below the all-favourable case, each with the assumptions that break a limit and
                 what its design costs in this engine with those brought inside the limits (`exceptions()`).

Run
---
    python study_assumptions.py      # each modification alone and all together, beside each study's own reported cost
"""
from __future__ import annotations

import copy

import floor_physics as fp
from inputs import value

DIR = "Cultivated_meat_TEAs/"

# ---------------------------------------------------------------------------------------------------------------------------
# The studies. Each assumption is (what, value as the source gives it, source reference).
# ---------------------------------------------------------------------------------------------------------------------------
STUDIES = {
    "humbird2021": dict(
        name="Humbird 2021", year=2021,
        citation="D. Humbird, 'Scale-up economics for cultured meat: techno-economic analysis and due diligence', 2021 "
                 "(Humbird21Cultivated.pdf)",
        system="A plant making about 7,000 tonnes of wet cells a year, as fed-batch in 24 stirred tanks of 20 m³ or as perfusion "
               "in 96 stirred tanks of 2 m³.",
        cost="$36.79 a kilo (fed-batch) and $51.29 a kilo (perfusion)", cost_value=51.29,
        basis="a kilo of wet cells, with the yearly charge on the plant; his plant is costed in 2018 dollars",
        explains="The starting point here is his best estimate: fed-batch in 20 m³ tanks on plant hydrolysate, $21.00 in his "
                 "dollars. His perfusion design is 96 tanks of 2 m³, with glucose and amino acids bought one by one ($18.39 a "
                 "kilo of cells) and growth factors ($2.78).",
        assumptions=[
            ("reported cost, fed-batch", "$36.79 a kilo of wet cells", "Table 4.6, PDF page 62"),
            ("reported cost, fed-batch with plant hydrolysate", "$21.00 a kilo; macronutrients $3.39 against $19.08", "Table 4.7, PDF page 62"),
            ("reported cost, fed-batch, wild-type metabolism", "$236.58 (amino acids), $225.03 (hydrolysate)", "Table 4.7, PDF page 62"),
            ("reported cost, perfusion", "$51.29 a kilo of wet cells", "Table 4.13, PDF page 69"),
            ("reported cost, perfusion, wild-type metabolism", "$484.37 a kilo", "Table 4.14, PDF page 69"),
            ("medium, perfusion", "macronutrients $18.39 and micronutrients (growth factors) $2.78 a kilo of cells", "Table 4.13, PDF page 69"),
            ("hydrolysate price", "$2 a kilo of mixed amino acids", "Section 4.1, PDF page 58"),
            ("cells", "3,000 pg wet, doubling every 24 hours; lactate 0.50 mol per mol of glucose burned (Reaction 2.10)",
             "Sections 2.1 and 2.2, PDF pages 18 to 25; Figure 4.5 caption"),
            ("wild-type waste", "0.070 mol ammonia and 0.474 mol lactate per mol of dry cell mass (Reaction 2.9); derived: "
             "0.070 x 13.6 mol per kg wet = 0.952 mol ammonia a kilo; 0.474 / 0.333 mol glucose (Reaction 2.9) = 1.42 mol lactate per mol glucose",
             "Reaction 2.9, PDF page 23; Table 2.3, PDF page 25"),
            ("density limit", "258 g/L of wet cells at a volume fraction of 0.25, whatever the cell size; the culture is then about twice "
             "as viscous as water, on a packing limit of 0.65", "Section 2.1 and Table 2.2, PDF pages 19 and 20"),
            ("oxygen and waste limits", "5 mmol/L of ammonia and 50 mmol/L of lactate; gas at 0.006 m/s at most; 100 mbar of CO₂; with "
             "90% oxygen a 20 m³ tank holds 120 g/L", "Section 2.3, PDF pages 29 to 34"),
            ("amino-acid prices", "$40 to $156 a kilo, one by one; 487 kg a batch of about 1,850 kg of cells (derived: 0.263 kg a kilo)",
             "Table 3.4, PDF page 46; Table 4.4, PDF page 61"),
            ("perfusion density and device", "195 g/L at 1.0 tank volume a day with two ATF 10 devices; 140 g/L at 0.5 a day with one",
             "Section 4.2, PDF page 66"),
            ("vessels", "fed-batch 24 x 20 m³; perfusion 96 x 2 m³", "Sections 4.1 and 4.2, PDF pages 57 and 66"),
            ("plant grade", "clean rooms for the cell-culture area; buildings are $3.08 a kilo in fed-batch, and a sanitary area "
             "would halve that", "Table 4.7 and Section 4.1, PDF pages 58 and 62"),
            ("capital", "fed-batch $327.9M for 480 m³; derived: $683k per m³ of production tank. Perfusion $663M for 192 m³; "
             "derived: $3.45M per m³", "Table 4.3, PDF page 60; Table 4.14, PDF page 69"),
            ("financing", "7.5% over 10 years: a capital charge of 14.6% of the plant's cost a year, plus 4% maintenance and 5% insurance",
             "Section 3.1, PDF page 44; Tables 4.3 and 4.5"),
            ("financing of his yeast benchmark", "10% over 20 years; derived: a payment of 11.7% of the plant's cost a year, a higher "
             "interest rate than his 7.5% and a lower yearly payment than his 14.6%, because of the 20 years", "Appendix A, PDF page 99"),
            ("labour", "95 staff, $1.45 a kilo (fed-batch); 132 staff, $1.99 a kilo (perfusion)", "Tables 4.5 and 4.12"),
        ]),
    "cedelft2021": dict(
        name="CE Delft 2021", year=2021,
        citation="R. Vergeer, P. Sinke, I. Odegard, 'TEA of cultivated meat: future projections for different scenarios', CE Delft, "
                 "November 2021, with corrigendum (Delft21Cultivated.pdf)",
        system="A plant making 10,000 tonnes of cultivated meat a year: cells grown in 130 stirred tanks of 10 m³ with three "
               "harvests, then matured on scaffolds in perfusion reactors of 2 m³.",
        cost="$6.43 a kilo in its most favourable scenario for 2030; $150 to $22,421 at current medium prices", cost_value=6.43,
        basis="a kilo of cultivated meat (cells after maturation), not a kilo of cells; the year of the dollars is not stated",
        explains="Its capital is about a fifth to a third of this model's per m³ of tank and is repaid over 30 years with no "
                 "interest. Its medium holds 15 g of sugars for a kilo of meat, where the cells of this model burn about 320 g. "
                 "Its figure is for meat after a maturation stage, which this model does not have.",
        assumptions=[
            ("reported cost by scenario", "$22,421, $1,708, $150, $116, $18, $8, $7.16, $6.43 a kilo for scenarios 1 to 8", "Figure 4, PDF page 18"),
            ("reported cost, final", "$6.43 a kilo", "Section 3.2, PDF page 28"),
            ("density", "50 million cells a mL at most", "Table 5, PDF page 37"),
            ("cell volume", "3,500 µm³; derived: 50e6 x 3,500e-12 mL = 17.5% of the volume", "Table 5, PDF page 37"),
            ("cell volume, scenario 8", "5,000 µm³; derived: 50e6 x 5,000e-12 mL = 25% of the volume, and 5.2 ng a cell at 1.03 g/mL",
             "Section 3.2.5, PDF page 27"),
            ("medium, low use", "250 g of amino acids at $2.13 a kilo, 15 g of sugars and 7.5 litres of water for a kilo of meat; "
             "8.0 litres a kilo", "Table 11, PDF page 41"),
            ("doubling time", "30 hours", "Table 5, PDF page 36"),
            ("vessels", "130 stirred tanks of 12.5 m³ (10 m³ working) and 430 perfusion reactors of 2.5 m³ (2 m³ working). Table 5 "
             "(PDF page 36) says 4,300 perfusion reactors; the costing uses 430", "Table 2, PDF page 13"),
            ("way of running", "semi-continuous, three intermediate harvests, 42 days from vial to harvest", "Table 5, PDF page 36"),
            ("plant grade", "food grade; no clean rooms and no drug-production standards", "Section 2.3.2, PDF page 13"),
            ("capital", "about $450M for the 10,000-tonne plant ($320M in scenario 8); derived: 450,000 / 2,700 m³ of all vessels = "
             "$167k per m³, or 450,000 / 1,625 m³ of stirred tanks = $277k per m³", "Section 3.2.3, PDF pages 23 and 27; Table 2"),
            ("financing", "payback in 4 years (commercial) or in 30 years (its social criterion); no interest rate is used: the "
             "yearly cost is the investment divided by the years, $110M or $15M", "Section 3.2.3, PDF pages 23 and 24"),
            ("labour", "about 200 staff", "Section 3.2.3, PDF page 23"),
        ]),
    "risner2021": dict(
        name="Risner 2021", year=2021,
        citation="D. Risner et al., 'Preliminary techno-economic assessment of animal cell-based meat', Foods 10(1):3, 2021 "
                 "(Risner21Preliminary.pdf)",
        system="Enough 20 m³ stirred tanks, run in batches, to make 121,000 tonnes of meat a year, in four scenarios from "
               "current laboratory figures to every technical problem solved.",
        cost="about $437,000 a kilo (scenario 1) to $1.95 a kilo (scenario 4)", cost_value=1.95,
        basis="the least price of a kilo of wet cells that pays the yearly capital and operating costs; the tanks are the only "
              "capital; 2019 dollars",
        explains="Scenario 4 fills the whole tank with cells (derived: 200 million cells a mL of 5,000 µm³ each is 100% of the "
                 "volume), doubles them every 8 hours, feeds a kilo of cells 7 litres of medium holding 45 g of glucose, and "
                 "counts only the tanks as capital. It sets no limit from oxygen, CO₂, ammonia or lactate.",
        assumptions=[
            ("reported cost", "$437,000, $57,200, $44,600 and $1.95 a kilo for scenarios 1 to 4", "Table 2, PDF page 9"),
            ("medium price", "$376.80 a litre (scenario 1) to $0.24 a litre (scenario 4)", "Section 3, PDF page 9"),
            ("medium use", "8.56e8 litres a year for 1.21e8 kg in scenario 4; derived: 7.1 litres and $1.70 a kilo of cells",
             "Table 2, PDF page 9; Table A1, PDF page 19"),
            ("glucose", "0.0356 mol a litre of medium in scenario 4; derived: x 7.1 litres x 180 g = 45 g a kilo of cells", "Table A4, PDF page 20"),
            ("limits", "the cells of a 20 m³ tank may total 20 m³, which the study says leaves no room for the medium; oxygen "
             "uptake is set equal to transfer, with no limit on transfer, CO₂, ammonia or lactate", "Appendix A, PDF pages 12 and 16"),
            ("density", "10 million, 95 million, 95 million and 200 million cells a mL", "Table A1, PDF page 19"),
            ("cell volume and density", "5.00e-15 m³ a cell at 1,060 kg per m³; derived: 2.0e8 x 5.0e-9 mL = 1.0 mL of cells per mL", "Table A2, PDF page 19"),
            ("doubling time", "24, 16, 16 and 8 hours", "Table A2, PDF page 19"),
            ("vessel", "20 m³ tanks at $50,000 per m³ unit cost, scale exponent 0.6, Lang factor 2; no other equipment is counted",
             "Table A1, PDF page 19; Appendix A, PDF page 12"),
            ("financing", "90% debt at 5%, equity at 15%, over 20 years, each with its own repayment; derived: 0.9 x 8.02% + 0.1 x "
             "15.98% = 8.8% of the tanks' cost a year, plus 15% for fixed manufacturing costs", "Tables A1 and A7, PDF pages 19 and 22"),
        ]),
    "negulescu2023": dict(
        name="Negulescu 2023", year=2023,
        citation="P. G. Negulescu et al., 'Techno-economic modeling and assessment of cultivated meat: impact of production "
                 "bioreactor scale', Biotechnology and Bioengineering 120(4):1055, 2023 (Negulescu22Technoeconomic.pdf)",
        system="An industry making 100,000 tonnes of unstructured beef a year by fed-batch in stirred tanks of 42 m³ or 211 m³ "
               "or in airlift tanks of 262 m³.",
        cost="$35, $25 and $17 a kilo for the 42 m³ tanks, the 211 m³ tanks and the 262 m³ airlift", cost_value=17.0,
        basis="a kilo of product (about 97% wet cells), with straight-line depreciation over 10 years and no financing cost; "
              "the year of the dollars is not stated",
        explains="Its saving comes from larger tanks at the same 100 g/L; it checks oxygen and sets no limit from CO₂. In this "
                 "model a larger tank holds a thinner culture, because CO₂ leaves only in the gas bubbled through, so on "
                 "Humbird's design larger tanks cost more a kilo. Its medium is $1.40 a litre.",
        assumptions=[
            ("reported cost", "$35, $25, $17 a kilo with depreciation; $25, $20, $16 without", "Table 2, PDF page 8"),
            ("medium", "$1.396 a litre; 10.2 litres a kilo of fresh cells", "Section 2.2.1, PDF page 6"),
            ("density", "each step ends at 100 g of fresh cells a litre (3.3e7 cells a mL at 3 ng a cell)", "Section 2.2, PDF page 4"),
            ("doubling time", "23 hours", "Section 2.2, PDF page 4"),
            ("vessels", "stirred tanks of 42 m³ and 211 m³, an airlift of 262 m³; food-grade 304 stainless steel", "Section 2.3 and Table 2, PDF pages 6 and 8"),
            ("way of running", "fed-batch, with a 10-day maturation step in the production tank", "Section 2.2, PDF pages 4 and 6"),
            ("capital", "$438M, $1,172M and $366M per facility", "Table 2, PDF page 8"),
            ("financing", "straight-line depreciation over 10 years, 5% salvage; no project financing", "Section 2.3, PDF page 6"),
        ]),
    "garrison2022": dict(
        name="Garrison 2022", year=2022,
        citation="G. L. Garrison, J. T. Biermacher, B. W. Brorsen, 'How much will large-scale production of cell-cultured meat "
                 "cost?', Journal of Agriculture and Food Research 10:100358, 2022 (Garrison22How.pdf)",
        system="A plant with four 20 m³ stirred tanks, half of each harvested ten times in a 51-day cycle, making 548 tonnes a year.",
        cost="$63.69 a kilo", cost_value=63.69,
        basis="a kilo of cell-cultured meat, packed and delivered; the year of the dollars is not stated",
        explains="Its labour is $17.65 a kilo (94 staff for 80 m³ of tank) and its medium $19.66 a kilo, against $1.82 and "
                 "$4.34 in Humbird's best estimate in today's dollars. Its capital per m³ of tank is close to Humbird's.",
        assumptions=[
            ("reported cost", "$63.69 a kilo: medium $19.66, labour $17.65, tanks and equipment $17.81", "Table 2, PDF page 5"),
            ("medium", "2,880 kL a year at $3,743 a kL; derived: $3.74 a litre and 2,880,000 / 548,400 = 5.3 litres a kilo. "
             "The text on PDF page 6 calls the same base price '$374/L', a misprint: PDF page 3 gives $3.74 a litre",
             "Table 2, PDF page 5; Section 3.2.1, PDF page 6"),
            ("reported cost, most favourable variant", "$17.10 a kilo with the cheapest published medium and tanks and labour cut by 75%",
             "Section 3.2, PDF page 6"),
            ("vessels", "four 20 m³ final tanks, each with seed tanks of 200 L, 1,000 L and 5,000 L", "Section 2.3.1, PDF page 4"),
            ("capital", "$60M for all equipment; derived: 60,000 / 80 m³ = $750k per m³ of tank. The building is rented", "Section 2.3.1, PDF page 4"),
            ("financing", "the tanks are paid off over 10 years at 10%; derived: $9,764,724 a year on $60M is 16.27%",
             "Section 2.3, PDF page 4; Table 2, PDF page 5"),
            ("labour", "94 employees at $102,997", "Table 2, PDF page 5"),
        ]),
    "pasitka2024": dict(
        name="Pasitka 2024", year=2024,
        citation="L. Pasitka et al., 'Empirical economic analysis shows cost-effective continuous manufacturing of cultivated "
                 "chicken using animal-free medium', Nature Food, 2024 (Patiksa24Empirical.pdf)",
        system="A plant with 50 m³ of tanks in continuous perfusion, projected from 20-day runs of chicken fibroblasts in a "
               "1.8-litre tank: 25 tanks of 2 m³ with ATF devices, or 10 tanks of 5 m³ with tangential-flow filters.",
        cost="$6.2 to $6.8 a pound of a product that is half cells; derived: about $21 to $24 a kilo of wet cells",
        cost_value=24.0,
        basis="a kilo of wet cells (derived: $6.8 x 2.2046 = $14.99 a kilo of product = half a kilo of cells + $3 of plant "
              "ingredients, so cells = (14.99 - 3) x 2 = $23.98). The study gives $23.26 to $26.44 as its range; its cost lines "
              "show maintenance and insurance and no payment on the plant; the year of the dollars is not stated",
        explains="It projects 1.8 kilos of wet cells per litre of tank a month from a 1.8-litre run without animal components, "
                 "held at 10 to 28 million cells a mL. Its 130 million cells a mL (43% weight per volume) is a separate run in "
                 "5-litre glass tanks with serum. Its measured cells make far more lactate and double far more slowly than Humbird's.",
        assumptions=[
            ("reported cost", "$6.8 a pound of product with tangential-flow filters; $6.2 a pound in the abstract; $23.26 to "
             "$26.44 a kilo of wet biomass over its range of plant cost", "Abstract, PDF page 1; Figure 4, PDF page 7; PDF pages 2, 6 and 8"),
            ("medium", "$0.63 a litre, without animal components", "Abstract, PDF page 1"),
            ("medium use", "24 million litres for 1.07 million kilos of wet cells a year; derived: 22.4 litres a kilo", "PDF page 6"),
            ("density", "up to 130 million cells a mL, 43% weight per volume, with tangential-flow filters; 90 million with ATF; in "
             "5-litre glass tanks with 10% serum. The weight of a cell is not consistent across the study: 430 g/L / 130e6 a mL "
             "is 3.3 ng, and 1.7 kg / 173e9 cells in the continuous run is 9.8 ng, so the 43% is a weight of wet pellet",
             "Abstract and Figure 1, PDF pages 1 and 3; PDF page 2"),
            ("doubling time", "61 hours through the 20-day continuous run", "PDF page 2"),
            ("waste", "145 g glucose gave 76 g lactate and 2.4 g ammonia per kilo of wet cells; derived: (76 / 90.08) / (145 / 180.16) "
             "= 1.05 mol lactate per mol glucose, and 2.4 / 17.03 = 0.14 mol ammonia a kilo", "PDF page 4"),
            ("levels held", "lactate below 30 mM and ammonia below 3 mM", "PDF page 2"),
            ("output", "1.8 kg of wet cells per litre of tank a month", "Methods, PDF page 9"),
            ("vessels and device", "25 x 2 m³ with ATF, 10 x 5 m³ with tangential-flow filters, or 2 x 25 m³", "PDF page 6"),
            ("losses", "1.3% of production lost", "PDF page 6"),
        ]),
    "supermeat2024": dict(
        name="SuperMeat 2024", year=2024,
        citation="SuperMeat, 'Cultivating the future: a deep dive into cost-effective cultivated meat production', company "
                 "report, November 2024, not peer reviewed (Supermeat24Cultivating.pdf)",
        system="A plant with five lines of 25 m³ tanks in perfusion through a tangential-flow filter with continuous bleeding "
               "for 45 days, projected from 10-litre runs.",
        cost="$13.4 a pound with depreciation, $11.8 without; derived: $29.5 and $26.0 a kilo", cost_value=29.5,
        basis="a kilo of 100% cultivated chicken (cells after a short maturation); depreciation is its only charge on the plant",
        explains="Its medium costs $0.50 a litre and it uses about 30 litres a kilo (derived), about $15 a kilo against $4.34 "
                 "for the nutrients of Humbird's best estimate. Its cells weigh a third of Humbird's and double half as fast.",
        assumptions=[
            ("reported cost", "$11.8 a pound without depreciation, $13.4 with", "PDF page 20"),
            ("medium", "under $0.5 a litre, fed at 1.5 tank volumes a day while bleeding", "PDF pages 3 and 18"),
            ("medium use", "92,772 kL a year for 6.7 million pounds; derived: 92,772,000 / 3,039,000 kg = 30.5 litres a kilo", "PDF page 20"),
            ("density", "80 million cells a mL while bleeding; derived: x 1.04 ng = 83 g/L", "PDF page 18"),
            ("cell weight", "1.04 g per billion stem cells, 1.75 g per billion mature cells", "PDF page 18"),
            ("doubling time", "0.5 doublings a day while bleeding; derived: 48 hours", "PDF page 18"),
            ("vessel and device", "25,000-litre tanks, perfusion with a tangential-flow filter", "PDF pages 18 and 20"),
            ("losses", "3% rejected", "PDF page 18"),
            ("labour", "100 full-time employees and 13 outsourced positions", "PDF page 18"),
        ]),
    "lever2025": dict(
        name="Lever VC 2025", year=2025,
        citation="Lever VC, 'Insights on cultivated meat production costs', investor report, 2025, not peer reviewed "
                 "(Lever25Insights.pdf)",
        system="Not a design: figures the investor says it checked across several companies.",
        cost="$10 to $15 a kilo, some companies below $10", cost_value=12.5,
        basis="a kilo of cell mass, as a cost of production; whether the plant is charged, and wet or dry, are not stated",
        explains="It gives no design, and does not say whether the plant is charged.",
        assumptions=[
            ("reported cost", "$10 to $15 a kilo of cell mass, some below $10", "PDF page 3"),
            ("medium", "$1 a litre or less at numerous companies, several under $0.50", "PDF page 3"),
            ("density", "60 to 90 g/L at several companies", "PDF page 3"),
        ]),
    "gfi2021": dict(
        name="GFI 2021", year=2021,
        citation="The Good Food Institute, 'Anticipatory life cycle assessment and techno-economic assessment of commercial "
                 "cultivated meat production', summary of CE Delft's two studies, 2021 (GFI21Anticipatory.pdf)",
        system="A summary of CE Delft's study: the same 10,000-tonne plant.",
        cost="$6.43 a kilo ($2.92 a pound)", cost_value=6.43,
        basis="as CE Delft 2021: a kilo of cultivated meat in the most favourable scenario",
        explains="As CE Delft 2021.",
        assumptions=[
            ("reported cost", "as low as $6.43 a kilo", "PDF page 2"),
            ("capital", "$450M for a plant making 10,000 tonnes a year", "PDF page 7"),
        ]),
    "gfi2026": dict(
        name="GFI 2026", year=2026,
        citation="The Good Food Institute, 'State of the Industry: cultivated meat, seafood and ingredients', 2026 "
                 "(GFI_2026-State-of-the-Industry-report-Cultivated-meat-seafood-and-ingredients.pdf)",
        system="Not a design: a yearly review that reports what companies announced.",
        cost="no cost a kilo; medium at $0.20 a litre or below", cost_value=None,
        basis="a litre of medium, as announced by companies in 2025; not audited",
        explains="It reports no cost a kilo.",
        assumptions=[
            ("medium", "several companies announced $0.20 a litre or below in 2025", "Commercial landscape, overview, PDF page 8"),
            ("medium", "food-grade amino acids allow media below $0.20 a litre", "Science and technology, PDF page 30"),
        ]),
    # ---- added 2026-11-24: four analyses by parties with a stake in the result, none peer reviewed. The first and the last
    # were read in full; Gourmey's and Aleph's reports are not public, so only what the companies announced is recorded.
    "ark2023": dict(
        name="Ark Biotech 2023", year=2023,
        citation="Y. Quint and others, 'Cultivated meat's path to price parity: a techno-economic analysis', Ark Biotech, company "
                 "report, 2023, not peer reviewed; Ark sells large bioreactors (Quint23Cultivated.pdf)",
        system="A plant making 50,000 tonnes a year in fed-batch: 25 m³ stirred tanks as the baseline, and the company's own "
               "tank design up to 1,000 m³ as a lever. It counts the cell culture only.",
        cost="$29.5 a pound as the baseline; $2.0 a pound with all four levers; derived: $65.0 and $4.4 a kilo", cost_value=29.5 * 2.2046,
        basis="a kilo of cells leaving the tank: nothing after the bioreactor, no packaging, and the plant charged as straight-line "
              "depreciation over 15 years with no interest",
        explains="Its baseline medium costs $2 a litre, $20.8 of its $29.5 a pound. Its lowest figure needs tanks of 1,000 m³, forty "
                 "times the largest used for animal cells, cells that gain 128% in mass in a differentiation step, and medium at "
                 "$0.25 a litre. It charges the plant no interest.",
        assumptions=[
            ("reported cost", "$29.5 a pound baseline: medium $20.8, depreciation $3.9, utilities $2.2, other $2.6", "Exhibit 2, PDF page 5"),
            ("reported cost", "$2.0 a pound with 1,000 m³ tanks, 50% higher density, 128% differentiation and medium at $0.25 a litre",
             "Exhibit 1, PDF page 4"),
            ("reported cost", "example paths down to $0.3 a pound, with a 3,000% gain in mass over 20 days of differentiation; "
                              "derived: $0.66 a kilo, a third of this model's nutrient floor", "Exhibit 10, PDF page 14"),
            ("medium", "$2 a litre as the baseline, $0.25 as the lever", "Exhibit 1, PDF page 4"),
            ("medium use", "9.1 litres a pound in fed-batch; derived: 20 litres a kilo", "Exhibit 6, PDF page 8"),
            ("density", "20 million cells a mL in fed-batch after 8 days, 30 million as the lever; derived at 2.5 ng: 50 and 75 g/L",
             "Exhibit 1, PDF page 4"),
            ("cell weight", "2,500 picograms", "Exhibit 1, PDF page 4"),
            ("doubling time", "24 hours, after a lag of 2 days", "Exhibit 3, PDF page 7"),
            ("vessel", "25,000-litre stirred tanks as the baseline; its own design at 100, 250 and 1,000 m³", "Exhibit 8, PDF page 12"),
            ("financing", "depreciation over 15 years with no salvage value, no interest", "Exhibit 8, PDF page 12"),
            ("scope", "everything after the bioreactor, packaging, selling costs and margins are left out", "Exhibit 8, PDF page 12"),
        ]),
    "cellag2024": dict(
        name="Cellular Agriculture Ltd 2024", year=2024,
        citation="I. Argyle and I. Dunsford (Cellular Agriculture Ltd), 'Techno-economic assessment and media cost modelling', "
                 "Appendix 1 of the Royal Agricultural University's report 'Culture Clash', July 2024, not peer reviewed; the "
                 "authors' company makes the hollow-fibre bioreactor it models (Argyle24Technoeconomic.pdf)",
        system="Bovine cells grown and matured in the company's hollow-fibre bioreactors, at two sizes: a farm-scale plant making "
               "150 tonnes a year and a factory making 60 tonnes a week. The process flow is not disclosed.",
        cost="£14.68 to £20.64 a kilo of cultured biomass", cost_value=14.68 * 1.28,
        basis="a kilo of finished cultured biomass, before it is made into a product; the plant is divided over 20 years with no interest",
        explains="It uses 140 litres of medium a kilo and assumes about 70% of the water and medium is recovered. Growth factors are "
                 "replaced by an additive priced at £0.40 a kilo of biomass, from talks with a supplier; with growth factors at "
                 "today's prices the same model gives £15,537 a kilo. It charges the plant no interest.",
        assumptions=[
            ("reported cost", "factory of 60 tonnes a week: £14.68 to £15.12 a kilo (plant £3.58, running costs £11.09 to £11.53)",
             "Table 5, PDF page 7"),
            ("reported cost", "farm-scale plant of 150 tonnes a year: £20.19 to £20.64 a kilo (plant £6.92)", "Table 5, PDF page 7"),
            ("reported cost", "with a defined medium and growth factors at today's prices: £15,537 a kilo", "Table 4, PDF page 7"),
            ("medium use", "140 litres a kilo of cultured meat, following Hubalek 2022", "PDF page 3"),
            ("medium", "basal medium from food-grade ingredients at £0.03 to £0.05 a litre, ingredients only", "Tables 1 to 3, PDF page 6"),
            ("growth factors", "replaced by an additive at £0.40 a kilo of biomass", "PDF page 3"),
            ("recycling", "about 70% of the water and useful medium recovered", "PDF page 2"),
            ("vessel", "hollow-fibre bioreactors at every stage", "PDF page 2"),
            ("financing", "the plant divided by the yearly output over 20 years, no interest", "PDF page 2"),
            ("oxygen", "0.232 kg of oxygen a kilo of cultured meat", "Table 6, PDF page 8"),
        ]),
    "gourmey2025": dict(
        name="Gourmey and Arthur D. Little 2025", year=2025,
        citation="Gourmey (now PARIMA), 'Gourmey sets new cost benchmark in cultivated meat production', company announcement of "
                 "an assessment by Arthur D. Little, 28 May 2025; the assessment itself is not public "
                 "(gourmey.com/blogs/gourmey-sets-new-cost-benchmark-in-cultivated-meat-production)",
        system="A plant of six 5,000-litre tanks run continuously with duck embryonic stem cells in suspension, making 1,700 "
               "tonnes a year.",
        cost="€7 a kilo ($3.43 a pound); below €10 a kilo for the finished product", cost_value=3.43 * 2.2046,
        basis="the announcement does not say whether €7 is a kilo of cells or of product, nor whether the plant is charged; trade "
              "press reports that the product assessed is about half cells",
        explains="Its 1,700 tonnes a year from 30 m³ of tank is 57 tonnes per m³, four times the 14.5 of Humbird's best estimate. Its "
                 "medium costs €0.20 a litre with no growth factors. The density, the litres of medium a kilo and the financing "
                 "are not published.",
        assumptions=[
            ("reported cost", "€7 a kilo ($3.43 a pound) at commercial scale; below €10 a kilo for finished product", "company announcement, 28 May 2025"),
            ("product", "a finished product about half cultivated cells, the rest plant ingredients", "press report, Green Queen, 28 May 2025"),
            ("output", "1,700 tonnes a year from six 5,000-litre bioreactors; derived: 57 tonnes per m³ of tank a year", "company announcement, 28 May 2025"),
            ("capital", "under €35M per facility; derived: under €1.17M per m³ of tank", "company announcement, 28 May 2025"),
            ("medium", "€0.20 a litre, with no growth factors or serum", "company announcement, 28 May 2025"),
            ("mode", "continuous runs in suspension, cells not differentiated", "company announcement, 28 May 2025"),
            ("doubling time", "less than 16 hours, as the company told the press", "press report, Green Queen, 28 May 2025"),
        ]),
    "aleph2025": dict(
        name="Aleph Farms and Eridia 2025", year=2025,
        citation="Aleph Farms, 'First of its kind independent TEA shows Aleph Cuts will reach 47% margin at price parity with "
                 "beef cuts', company announcement of an analysis by Eridia (a joint venture of Bühler and ZETA), September 2025; "
                 "the analysis itself is not public (aleph-farms.com/journals/cultivated-beef-tea-profitability)",
        system="A plant with 5,000-litre tanks making a cultivated beef cut from cells that are not modified or immortalised. The "
               "number of tanks, the output and the way they are run are not published.",
        cost="$6.45 a pound with the plant; as low as $4.08 a pound in its sensitivity analysis; derived: $14.2 and $9.0 a kilo",
        cost_value=6.45 * 2.2046,
        basis="a kilo of the end product, a beef cut; the share of cells in it is not stated; running costs and the plant are both counted",
        explains="It publishes a cost, a wholesale price ($27 a kilo) and a payback of 2.5 years, and none of the process figures "
                 "behind them: no density, medium price, litres a kilo, output or plant cost.",
        assumptions=[
            ("reported cost", "$6.45 a pound, running costs and capital both counted", "company announcement, September 2025"),
            ("reported cost", "as low as $4.08 a pound of end products in the sensitivity analysis", "company announcement, September 2025"),
            ("price", "sold wholesale at $27 a kilo ($12.25 a pound), the price of premium beef cuts; a 47% gross margin", "company announcement, September 2025"),
            ("payback", "as low as 2.5 years", "company announcement, September 2025"),
            ("vessel", "5,000-litre bioreactors", "company announcement, September 2025"),
        ]),
}

BASE_LABEL = "Humbird's best estimate (2021), like for like in today's dollars"
BASE_KEY = "humbird_best"                    # the page's starting point the modifications are defined on (build_interactive.REF_ORDER)
BASE_VM, BASE_PLANT, BASE_DEVICE = ["stirred", "fedbatch"], "pharma", "tff"


def humbird_aa_price() -> float:
    """Humbird's own amino acids as a price the page's amino-acid lever can take, $ a kilo of amino acids in today's dollars:
    his glucose and amino acids cost $19.08 a kilo of cells in fed-batch (Table 4.7, column 1, 2018 dollars), about $0.10 of it
    glucose (Table 4.11); the rest, in today's dollars, over this model's amino acids per kilo of cells (aa_intensity)."""
    return round((19.08 - 0.10) * value("pf_opex_escalation") / value("aa_intensity"), 0)


def _mods() -> list:
    aa = humbird_aa_price()
    return [
        # ---- the plant and its financing
        dict(key="no_clean_rooms", studies=["cedelft2021", "negulescu2023"],
             label="CE Delft 2021 and Negulescu 2023: Humbird 2021 design but with a food-grade plant without clean rooms",
             text="Both studies build a food-grade plant with no clean rooms. Humbird puts his tanks in clean rooms and notes that "
                  "a sanitary hall would halve the cost of his buildings (his Section 4.1). The plant here is then this model's "
                  "own count of his plant items in a food-grade hall, not his total.",
             solid="A design choice, not a measurement. No plant of this size exists with or without clean rooms.",
             own="$6.43 a kilo of meat (CE Delft); $35 a kilo (Negulescu, 42 m³ tanks)", settings={"plant": "sterile"}),
        dict(key="yeast_finance", studies=["humbird2021"],
             label="Humbird 2021, Appendix A: his design but with the financing of his baker's-yeast benchmark, 10% interest over 20 years",
             text="He finances his cultivated-meat plants at 7.5% over 10 years and his yeast plant at 10% over 20 years. The "
                  "interest rate is higher, but the 20 years make the yearly payment smaller: 11.7% of the plant's cost in place "
                  "of 14.6%.",
             solid="A judgement about investors, stated by him as an assumption.",
             own="$21.00 a kilo (his best estimate)", settings={"held": {"fin_rate": 10.0, "fin_life": 20.0}}),
        dict(key="finance_delft", studies=["cedelft2021"],
             label="CE Delft 2021: Humbird 2021 design but with the plant paid back over 30 years at no interest",
             text="Its favourable scenarios divide the investment by 30 years and charge no interest. In the study the change takes "
                  "the cost from $18 to $8.",
             solid="An assumption about investors. The study calls it a social criterion, against 4 years for a commercial one. "
                   "The plant must be repaid at a market rate of interest: money lent at no interest is not a cost of production, "
                   "so this model's most favourable case does not take it.",
             own="$6.43 a kilo of meat", settings={"held": {"fin_rate": 0.0, "fin_life": 30.0}}),
        dict(key="capex_third", studies=["cedelft2021", "negulescu2023"],
             label="CE Delft 2021 and Negulescu 2023: Humbird 2021 design but with a plant that costs a third as much to build",
             text="Both cost a plant at far less per m³ of tank than Humbird's $683k: derived, $167k to $277k (CE Delft) and "
                  "$209k (Negulescu's 42 m³ tanks). A third is the lowest the lever goes.",
             solid="Paper designs from equipment prices and installation factors. Neither has been built.",
             own="$6.43 a kilo of meat (CE Delft); $35 a kilo (Negulescu, 42 m³ tanks)", settings={"held": {"capex_x": 0.34}}),
        # ---- the medium
        # (the dearest medium first: where two boxes set the same lever the later is used, so the totals keep $0.50)
        dict(key="medium_140", studies=["negulescu2023"],
             label="Negulescu 2023: Humbird 2021 design but with a complete medium at $1.40 a litre",
             text="Negulescu prices its medium at $1.396 a litre, growth factors included: 10.2 litres and $14.2 for a kilo of "
                  "fresh cells. Here the growth factors of Humbird's design are still bought on top; the lever \"Growth factors "
                  "bought on top of the medium's price\" takes them out.",
             solid="Priced from bulk quotes for each component of a published medium.",
             own="$35 a kilo (42 m³ tanks)", settings={"held": {"medium_price": 1.40}}),
        dict(key="medium_020", studies=["gfi2026"],
             label="GFI 2026: Humbird 2021 design but with a complete medium at the $0.20 a litre companies announced",
             text="Several companies announced medium at $0.20 a litre or below in 2025. Humbird's nutrients cost $4.34 for a "
                  "kilo of cells in today's dollars; at $0.20 a litre the medium costs less than that, and the model then charges "
                  "what the nutrients in it cost at feed-grade prices.",
             solid="Company announcements, reported by GFI and not audited.",
             own="no cost a kilo reported", settings={"held": {"medium_price": 0.20}}),
        dict(key="medium_050", studies=["supermeat2024", "lever2025"],
             label="SuperMeat 2024 and Lever VC 2025: Humbird 2021 design but with a complete medium at $0.50 a litre",
             text="SuperMeat prices its medium at under $0.50 a litre and Lever VC says several companies are under $0.50. "
                  "Pasitka 2024 reports $0.63.",
             solid="SuperMeat's is a projected price at scale. Lever VC's figures were seen under confidentiality.",
             own="$29.5 a kilo (SuperMeat); $10 to $15 (Lever VC)", settings={"held": {"medium_price": 0.50}}),
        # ---- the tank and how it is run
        dict(key="perfusion_25", studies=["supermeat2024"],
             label="SuperMeat 2024: Humbird 2021 design but with perfusion through a membrane filter in 25 m³ tanks",
             text="SuperMeat's plant holds the cells back with a tangential-flow filter in 25 m³ tanks and bleeds cells off for "
                  "45 days. Humbird's best estimate is fed-batch; his own perfusion design stops at 2 m³.",
             solid="Projected from 10-litre runs. The largest perfusion run found with animal cells is 4 m³.",
             own="$29.5 a kilo with depreciation (derived from $13.4 a pound)",
             settings={"vm": ["stirred", "perfusion"], "held": {"tank_m3": 25.0}}),
        dict(key="humbird_perfusion", studies=["humbird2021"],
             label="Humbird 2021, Table 4.13: his design but with his own perfusion plant, 2 m³ tanks with an alternating-flow filter",
             text="His perfusion plant is 96 tanks of 2 m³, the largest an ATF 10 unit serves, at 195 g/L. In his report it costs "
                  "$51.29 a kilo with amino acids bought one by one; this box keeps the hydrolysate of his best estimate.",
             solid="ATF units are used in pharma at up to about 2 m³.",
             own="$51.29 a kilo (his perfusion case, amino acids bought one by one)",
             settings={"vm": ["stirred", "perfusion"], "device": "atf", "held": {"tank_m3": 2.0}}),
        dict(key="large_tanks", studies=["negulescu2023"],
             label="Negulescu 2023: Humbird 2021 design but with stirred tanks of 211 m³",
             text="Its cost falls from $35 to $25 a kilo when 42 m³ tanks become 211 m³ ones at the same density. Here the cost "
                  "rises: CO₂ leaves only in the gas bubbled through, so a larger tank holds a thinner culture. The study checks "
                  "oxygen and sets no limit from CO₂.",
             solid="No animal cells have been grown above about 25 m³.",
             own="$25 a kilo (211 m³ tanks)", settings={"held": {"tank_m3": 211.0}}),
        dict(key="company_density", studies=["supermeat2024", "lever2025"],
             label="SuperMeat 2024 and Lever VC 2025: Humbird 2021 design but with a culture no denser than the 83 g/L companies report",
             text="SuperMeat reports 83 g/L (derived from 80 million cells a mL at 1.04 ng) and Lever VC 60 to 90 g/L. Humbird's "
                  "fed-batch tank ends at 120 g/L.",
             solid="Reported by companies; not peer reviewed.",
             own="$29.5 a kilo (SuperMeat); $10 to $15 (Lever VC)", settings={"held": {"x_cap": 83.0}}),
        # ---- the nutrients and the cells
        dict(key="humbird_amino_acids", studies=["humbird2021"],
             label="Humbird 2021, Table 4.6: his design but with amino acids bought one by one at his prices",
             text=f"His first design buys amino acids one by one at $40 to $156 a kilo: $19.08 a kilo of cells with the glucose, "
                  f"against $3.39 on hydrolysate, and his total is $36.79 in place of $21.00. The lever takes ${aa:.0f} a kilo of "
                  "amino acids: his cost of amino acids for a kilo of cells in today's dollars, over the 232 g of amino acids "
                  "this model's cells take up.",
             solid="Market prices he collected for 2018.",
             own="$36.79 a kilo", settings={"held": {"aa_price": aa}}),
        dict(key="wild_type", studies=["humbird2021"],
             label="Humbird 2021, Table 4.7: his design but with the waste of his wild-type cells, not his enhanced ones",
             text="His design rests on cells that make far less ammonia and lactate than ordinary animal cells. With his "
                  "wild-type figures (0.95 mol of ammonia a kilo, 1.42 mol of lactate per mol of glucose, both derived from "
                  "his Reaction 2.9) his own cost rises to $225 a kilo on hydrolysate.",
             solid="The wild-type figures follow measured cultures of hamster cells. The enhanced ones are assumed.",
             own="$225.03 a kilo (fed-batch on hydrolysate)",
             settings={"traits": {"nh3_kg": 0.95, "lac_yield": 1.42}}),
        dict(key="pasitka_cells", studies=["pasitka2024"],
             label="Pasitka 2024: Humbird 2021 design but with the cells they measured in continuous perfusion",
             text="Their chicken fibroblasts made 1.05 mol of lactate per mol of glucose and 0.14 mol of ammonia a kilo, doubled "
                  "every 61 hours, and were held below 30 mM of lactate and 3 mM of ammonia. The waste figures are derived from "
                  "the amounts they report. The weight of a cell is left at Humbird's: the study's own figures give 3.3 ng and "
                  "9.8 ng.",
             solid="Measured, in a 1.8-litre tank over 20 days.",
             own="about $21 to $24 a kilo of wet cells (derived)",
             settings={"traits": {"nh3_kg": 0.14, "lac_yield": 1.05, "doubling_h": 61.0},
                       "held": {"lac_limit": 30.0, "nh3_limit": 3.0}}),
        dict(key="supermeat_cells", studies=["supermeat2024"],
             label="SuperMeat 2024: Humbird 2021 design but with the cells they report, 1.04 ng each and doubling every 48 hours",
             text="They report 1.04 g per billion stem cells and half a doubling a day while cells are bled off. Small cells "
                  "breathe more per gram, so a tank holds fewer grams of them.",
             solid="Reported by the company from 10-litre runs. Not peer reviewed.",
             own="$29.5 a kilo with depreciation (derived from $13.4 a pound)",
             settings={"traits": {"mass_pg": 1040.0, "doubling_h": 48.0}}),
        # ---- what the levers cannot represent, or what breaks a limit of the model
        dict(key="pasitka_density", studies=["pasitka2024"], not_representable=True,
             label="Pasitka 2024: Humbird 2021 design but with the 430 g/L they report with a tangential-flow filter",
             text="They report up to 130 million cells a mL, 43% weight per volume, in 5-litre glass tanks with serum.",
             reason="The density lever reaches 430 g/L, and nothing moves: a 20 m³ tank cannot pass the oxygen for it, and a "
                    "fed-batch tank is stopped by its waste first. The figure is also a weight of wet pellet: the study's own "
                    "cell counts give 3.3 ng and 9.8 ng a cell.",
             own="about $21 to $24 a kilo of wet cells (derived)"),
        dict(key="risner_scenario4", studies=["risner2021"], not_representable=True,
             label="Risner 2021: Humbird 2021 design but with the cells of its scenario 4",
             text="Scenario 4 has 200 million cells a mL, each of 5,000 µm³, doubling every 8 hours. Derived: those cells fill "
                  "100% of the tank's volume.",
             reason="Humbird puts the limit of a culture that still flows at 25% of the volume as cells, and no animal cell "
                    "line has been measured doubling in 8 hours; the doubling-time lever stops at 12.",
             own="$1.95 a kilo of wet cells"),
        dict(key="negulescu_airlift", studies=["negulescu2023"], not_representable=True,
             label="Negulescu 2023: Humbird 2021 design but with airlift tanks of 262 m³",
             text="Its cheapest case, $17 a kilo, is a 262 m³ airlift priced from a 1997 figure for a 190 m³ one.",
             reason="The page's airlift is 20 m³, and the tank-size lever acts on the stirred tank only, up to 250 m³.",
             own="$17 a kilo"),
    ]


def modifications(with_notes: bool = True) -> list:
    """The modifications in order. With `with_notes`, the assumptions that cannot be represented come last, flagged
    `not_representable`, with the reason."""
    out = []
    for m in _mods():
        m = dict(m)
        m["study_names"] = [STUDIES[s]["name"] for s in m["studies"]]
        if m.get("not_representable") and not with_notes:
            continue
        out.append(m)
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# The Python equivalent of the page's levers on Humbird's best estimate (page_scenarios.js tpParamsFor with hbKey "humbird_best")
# ---------------------------------------------------------------------------------------------------------------------------
_PY_ARG = {"gas_v": "gas_velocity", "pco2": "pco2_mbar", "maint": "maintenance_share", "kla_exp": "viscous_kla"}       # floorExplore's name -> explore's
LEVER_KINDS = ("traits", "held", "plant", "vm", "device")


def merge(mods: list) -> dict:
    """The lever settings of several modifications together. Where two set the same lever, the later in the list is used."""
    out = {"traits": {}, "held": {}}
    for m in mods:
        s = m.get("settings") or {}
        out["traits"].update(s.get("traits", {}))
        out["held"].update(s.get("held", {}))
        for k in ("plant", "vm", "device"):
            if k in s:
                out[k] = s[k]
    return out


def levers(settings: dict) -> set:
    """The levers a set of settings moves, as names: 'trait:lac_yield', 'held:fin_rate', 'plant', 'vm', 'device'."""
    return ({f"trait:{k}" for k in settings.get("traits", {})} | {f"held:{k}" for k in settings.get("held", {})}
            | {k for k in ("plant", "vm", "device") if k in settings})


def explore_arguments(settings: dict) -> tuple:
    """(explore keyword arguments without the medium's price, datasheet inputs to set, retention device, his nutrient cost a
    kilo or None) for lever settings on Humbird's best estimate, as the page builds them (tpParamsFor): his cell as the four
    traits, his yearly charge, growth factors bought; fed-batch and clean rooms unless the settings say otherwise; his plant's
    cost while the plant is his; his filter sets and his count of the end of a batch while the tank is run his way; the four
    additions of this model at none; his nutrient cost for a kilo of cells grown unless a price a litre is set."""
    import build_interactive as BI
    import humbird_check as HC
    import scenarios as S
    par = {p[0]: p for p in BI.PAGE_PARAMS}
    kw0, over0 = HC.conditions(HC.BEST, "today")
    tr = HC.page_traits()
    kw = {"doubling_h": kw0["doubling_h"], "mass_pg": kw0["mass_pg"], "nh3_kg": tr["nh3_kg"], "lac_yield": tr["lac_yield"],
          "glc_balance": True, "vessel_m3": kw0["vessel_m3"], "charge": kw0["charge"], "growth_factors": kw0["growth_factors"],
          "plant": "sanitary", "mode": "perfusion"}
    reg = {}
    vm = list(settings.get("vm") or BASE_VM)
    if vm == ["stirred", "fedbatch"]:
        kw.update(copy.deepcopy(S.setting("mode", "fedbatch").kw))
    elif vm != ["stirred", "perfusion"]:
        raise ValueError(f"vessel and mode {vm} are not priced here")
    plant = settings.get("plant", BASE_PLANT)
    if plant != "sterile":
        kw.update(S.setting("plant", plant).kw)
        if kw.get("vm", {}).get("kind") == "cyclic" and kw.get("items", {}).get("seed") == "two":
            kw["items"] = {**kw["items"], "seed": "full"}
    if kw.get("vm", {}).get("kind") == "cyclic":                                   # the tank run his way
        kw["vm"] = {**kw["vm"], "cons_run": kw0["vm"]["cons_run"]}
        kw["antifoam_otr"] = over0["pf_antifoam_otr"]
        reg.update({k: over0[k] for k in ("pf_batch_end_x", "pf_batch_half_x", "pf_medium_prep_exp", "pf_consumables_low")})
    kw.update(min_perfusion=1e-9, kill=0.0, viscous_kla=False)                     # the model's additions, at none
    reg.update(pf_harvest_recovery=over0["pf_harvest_recovery"], pf_protectant_dose=over0["pf_protectant_dose"])
    kw.update(settings.get("traits", {}))
    held = settings.get("held", {})
    fin = HC.page_finance()
    for k, v in held.items():
        if k in ("capex_x", "medium_price"):
            kw[k] = v
            continue
        key, _g, _n, _u, kind, arg, _d, scale = par[k][:8]
        if kind == "kw":
            kw[_PY_ARG.get(arg, arg)] = v / scale
        elif kind == "fx" and arg == "aa":
            reg["aa_bulk_price"] = v                                               # the slider is $ a kilo of amino acids
        elif kind == "fx" and arg == "tff.mem_price":
            reg["rt_membrane_price"] = v / scale
        elif kind == "fxx" and arg == "labour_x":
            reg["pf_labour"] = value("pf_labour") * v                              # the page's multiplier on the whole crew
        elif kind == "fx" and arg == "harvest_loss":
            reg["pf_harvest_recovery"] = 1.0 - v / scale                           # the slider is % of the cells grown
        elif kind != "fin":
            raise ValueError(f"the lever {k} is not priced here")
    if any(k in held for k in ("fin_rate", "fin_life", "fin_upkeep")):
        i, n, u = (held.get("fin_rate", fin["rate"]) / 100.0, held.get("fin_life", fin["life"]),
                   held.get("fin_upkeep", fin["upkeep"]) / 100.0)
        kw["charge"] = (i / (1.0 - (1.0 + i) ** -n) if i > 1e-9 else 1.0 / n) + u
    nutrients = None if "medium_price" in held else HC.page_nutrients_kg()
    return kw, reg, settings.get("device", BASE_DEVICE), nutrients


def result(settings: dict) -> dict:
    """The engine's result for Humbird's best estimate with these lever settings."""
    kw, reg, device, nutrients = explore_arguments(settings)
    with fp._inputs_set(reg):
        if nutrients is not None:           # his nutrients cost what he gives for a kilo of cells grown, whatever the litres
            r0 = fp.explore(medium_price=0.0, **kw)
            kw["medium_price"] = nutrients / (r0["medium_l"] * r0["harvested_share"])
        washed = kw.get("vm", {}).get("washed", kw["mode"] == "perfusion")
        if device != "tff" and washed:              # a device holds cells back only where waste is washed out (the page's tpEval)
            import retention
            return retention.scenario_cost(device, kw)
        return fp.explore(**kw)


def cost(settings: dict) -> float:
    """Cost of a kilo of cells, $: Humbird's best estimate with these lever settings."""
    return float(result(settings)["total"])


# ---------------------------------------------------------------------------------------------------------------------------
# Starting sets: one study's design, as a reasonable but ambitious long-term estimate, on Humbird's best estimate
# ---------------------------------------------------------------------------------------------------------------------------
# The owner, 2026-11-24: "there should be a button to change to other of the assumptions in the literature (not just 'published
# cells'). Otherwise it looks we are just explaining his paper." Later the same day: "it is ok to assume optimistic assumptions
# (like market maturity and so on) but they should be possible too", and "61h was from her experiment, but that is not the long
# term ambition ... Revise all the TEAs to make sure they propose reasonable but ambitious long term estimates."
#
# The rule each set follows (shown on the page):
#   1. the study's own design is kept: plant grade and cost where it gives one, tank size, way of running, retention device,
#      the weight of its cells, the years over which it repays the plant;
#   2. where the study gives a more favourable projection of its own (a scenario or a sensitivity), that projection is used;
#   3. where a value is what one lab run or today's ingredients gave, not a projection for a mature industry, the set uses the
#      long-term targets below (`target` says which, in words);
#   4. anything beyond a limit of the model is corrected (`corrected`): a plant is repaid with interest at a market rate (a
#      study that charges none, or no payment, gets Humbird's 7.5% over the study's own years, or his 10), the cells take up
#      what the mass balance gives, and every lever stays inside its range.
# Anything the study does not state stays Humbird's (`left` lists what the page cannot set). A set is NOT the study's own cost:
# `own` gives that, and the plot of plant against running costs shows both.
#
# The long-term targets (rule 3):
#   cells: Humbird's design cells, doubling every 24 hours and making his low ammonia and lactate. Most studies project 23 to 30
#     hours (Negulescu 2023, Ark Biotech 2023, CE Delft 2021); no serum-free meat cell has been published doubling this fast
#     (39 hours, Stout 2022), so the target is ambitious; the fastest published, with serum, is 15 hours (Stout 2023).
#   medium: $0.20 a litre with growth factors in it, what several companies announced in 2025 (GFI 2026, not audited). The
#     model never charges less than the nutrients the cells eat ($2.00 a kilo of cells), so the target cannot go below what
#     is possible.
LT_DOUBLING_H = 24.0


def _cpi(year: int) -> float:
    """cpi() below, for the sets defined before it: 2025 dollars per dollar of `year`."""
    return value("cpi_u_2025") / value(f"cpi_u_{year}")


LT_MEDIUM = 0.20
EUR_USD_2025 = 1.13            # dollars per euro, about the 2025 average; typed from memory, to be checked against an official series
PASITKA_CAPEX_X = 0.755        # the study's $1,295k per m³ of tank (2025 dollars) over this model's plant for the set
PASITKA_CAPEX_K_M3 = 63.1e3 / 50.0   # $k per m³ of tank, 2024 dollars (Table S4: $63.1M for 10 tanks of 5 m³)
GOURMEY_CAPEX_X = 0.761        # "under €35M" for six 5 m³ tanks: €1.17M, $1.32M per m³ in 2025 dollars, over this model's plant
GOURMEY_CAPEX_K_M3 = 35e3 / 30.0 * EUR_USD_2025     # $k per m³ of tank, 2025 dollars, an upper bound
# What a set does with each of a study's assumptions (the owner, 2026-11-24: "We should make clear exactly what we modified from
# each TEA, so it is auditable"). Each set carries `audit`: one row per assumption, (item, lever, what the study says with where,
# why, what the set uses). `lever` names the page's lever ("trait:doubling_h", "held:tank_m3", "vm", "device", "plant"), or
# "result:density" etc. for a figure this model works out, or None; where the lever is in the set's settings, the value the set
# uses is written from the settings (audit_rows), so the table cannot disagree with what is priced. tests/test_study_assumptions.py
# checks that every lever a set moves has a row.
KEPT = "Kept"
OWN = "The study's own projection"
TARGET = "Long-term target"
CORRECTED = "Corrected"
HUMBIRD = "Not stated: Humbird's"
MODEL_DEFAULT = "Not stated: this model's"
NOT_SET = "Not set on this page"
WORKED = "Worked out by this model"
AUDIT_KINDS = (KEPT, OWN, TARGET, CORRECTED, HUMBIRD, MODEL_DEFAULT, NOT_SET, WORKED)
AUDIT_WHY = {
    KEPT: "the study's value",
    OWN: "the study's more favourable scenario or sensitivity, not its base case",
    TARGET: "the study's value is what one lab run or today's ingredients gave; the set uses the long-term target",
    CORRECTED: "the study's value is beyond a limit of this model; the set uses the nearest possible value",
    HUMBIRD: "the study does not give it; Humbird's best estimate is kept",
    MODEL_DEFAULT: "the study does not give it, and Humbird's design has no equivalent the set can keep; this model's default is used",
    NOT_SET: "the page has no lever for it; the set leaves it out",
    WORKED: "this model works it out from the cells and the tank, whatever the study states",
}
_CELLS_T = "Humbird's design cells (the long-term target: most studies project 23 to 30 hours)"
SETS = [
    dict(key="humbird_perfusion", study="humbird2021", label="Humbird 2021, perfusion", name="Humbird's perfusion design (2021)",
         mods=["humbird_perfusion"], extra={},
         text="His other design: perfusion in 2 m³ tanks with an alternating-flow filter, on the plant hydrolysate of his best estimate.",
         own="$51.29 a kilo of wet cells in 2018 dollars with amino acids bought one by one (his Table 4.13)",
         audit=[
             ("Vessel and way of running", "vm", "perfusion in 96 stirred tanks (Section 4.2, PDF page 66)", KEPT, None),
             ("Tank size", "held:tank_m3", "2 m³, the largest an ATF 10 serves (Section 4.2, PDF page 66)", KEPT, None),
             ("Device that holds the cells back", "device", "alternating-flow filters (Section 4.2, PDF page 66)", KEPT, None),
             ("Nutrients", None, "amino acids bought one by one, $18.39 a kilo of cells (Table 4.13, PDF page 69)", OWN,
              "his plant hydrolysate, as in his best estimate (Table 4.7, column 2)"),
             ("Density", "result:density", "195 g of cells a litre (Section 4.2, PDF page 66)", WORKED, None),
             ("Everything else", None, "his best estimate's cells, plant and financing", KEPT, "the same"),
         ]),
    dict(key="cedelft", study="cedelft2021", label="CE Delft 2021",
         mods=["no_clean_rooms", "capex_third"],
         extra={"traits": {"doubling_h": 30.0, "mass_pg": 3610.0},
                "held": {"tank_m3": 10.0, "fin_rate": 7.5, "fin_life": 30.0, "medium_price": LT_MEDIUM, "gf_buy": 0.0}},
         text="Its most favourable scenario (8): a cheap food-grade plant without clean rooms paid back over 30 years, 10 m³ tanks, "
              "cells of 3.6 ng doubling every 30 hours.",
         own="$6.43 a kilo of meat in its most favourable scenario",
         audit=[
             ("Plant grade", "plant", "food grade, no clean rooms (Section 2.3.2, PDF page 13)", KEPT, None),
             ("Plant cost", "held:capex_x", "about $167k to $277k per m³ of tank (derived; Section 3.2.3, PDF pages 23 and 27)",
              CORRECTED, None),
             ("Years to repay the plant", "held:fin_life", "30, its social criterion (Section 3.2.3, PDF page 24)", KEPT, None),
             ("Interest on the plant", "held:fin_rate", "none: the investment divided by 30 years (Section 3.2.3, PDF page 24)",
              CORRECTED, None),
             ("Tank size", "held:tank_m3", "10 m³ working volume (Table 2, PDF page 13)", KEPT, None),
             ("Way of running", None, "semi-continuous, three harvests (Table 5, PDF page 36)", NOT_SET, "fed-batch, as Humbird"),
             ("Doubling time", "trait:doubling_h", "30 hours (Table 5, PDF page 36)", KEPT, None),
             ("Weight of a cell", "trait:mass_pg", "3,500 µm³ (Table 5, PDF page 37); 3.6 ng at 1.03 g/mL (derived)", KEPT, None),
             ("Medium price", "held:medium_price", "low medium use at future prices, with cheaper growth factors; no price a "
              "litre (Table 11, PDF page 41; Section 3.2.5)", TARGET, None),
             ("Growth factors bought on top", "held:gf_buy", "included in its medium at future prices (Section 3.2.5)", TARGET, None),
             ("Sugar fed", None, "15 g of sugars a kilo of meat (Table 11, PDF page 41)", CORRECTED,
              "what this model's mass balance gives (311 g of glucose a kilo of cells at Humbird's growth)"),
             ("Density", "result:density", "50 million cells a mL, 18% of the volume (Table 5, PDF page 37)", WORKED, None),
             ("Maturation", None, "a second stage in 2 m³ perfusion reactors (Table 2, PDF page 13)", NOT_SET, "left out: cells as grown"),
             ("Waste the cells make", None, "not stated", HUMBIRD, "Humbird's"),
         ]),
    dict(key="risner", study="risner2021", label="Risner 2021",
         mods=[],
         extra={"traits": {"doubling_h": 15.0},
                "held": {"tank_m3": 20.0, "medium_price": round(0.24 * _cpi(2019), 2), "gf_buy": 0.0, "capex_x": 0.34,
                         "fin_rate": 6.0, "fin_life": 20.0}},
         text="Its most favourable scenario (4), brought inside the limits.",
         own="$1.95 a kilo of wet cells in 2019 dollars (scenario 4)",
         audit=[
             ("Tank size", "held:tank_m3", "20 m³ (Table A1, PDF page 19)", KEPT, None),
             ("Way of running", None, "batches (Appendix A, PDF page 12)", NOT_SET, "fed-batch, as this page prices the scenario elsewhere"),
             ("Doubling time", "trait:doubling_h", "8 hours in scenario 4 (Table A2, PDF page 19)", CORRECTED, None),
             ("Weight of a cell", None, "5,000 µm³, 5.3 ng (Table A2, PDF page 19)", CORRECTED,
              "3 ng, Humbird's; heavier than any measured for meat cells"),
             ("Density", "result:density", "200 million cells a mL, which fills the tank (Table A1, PDF page 19)", CORRECTED, None),
             ("Medium price", "held:medium_price", "$0.24 a litre in 2019 dollars in scenario 4 (Section 3, PDF page 9)", OWN, None),
             ("Growth factors bought on top", "held:gf_buy", "priced at nothing in scenario 4 (Table A3, PDF page 20)", OWN, None),
             ("Plant cost", "held:capex_x", "the tanks only, $778,000 for a 20 m³ tank (PDF page 7)", CORRECTED, None),
             ("Interest on the plant", "held:fin_rate", "90% debt at 5%, equity at 15% (Table A7, PDF page 22)", KEPT, None),
             ("Years to repay the plant", "held:fin_life", "20 (Table A7, PDF page 22)", KEPT, None),
             ("Fixed manufacturing costs", None, "15% of the plant a year (Tables A1 and A7)", NOT_SET, "this model's labour, energy and supplies"),
             ("Waste the cells make, and what they tolerate", None, "no limit set (Appendix A, PDF page 16)", CORRECTED, "Humbird's"),
         ]),
    dict(key="negulescu", study="negulescu2023", label="Negulescu 2023",
         mods=["no_clean_rooms", "capex_third"],
         extra={"traits": {"doubling_h": 23.0},
                "held": {"tank_m3": 42.0, "x_cap": 100.0, "fin_rate": 7.5, "fin_life": 10.0, "medium_price": LT_MEDIUM, "gf_buy": 0.0}},
         text="Its smaller stirred plant: fed-batch in 42 m³ tanks to 100 g a litre, a cheap food-grade plant, cells doubling every 23 hours.",
         own="$35 a kilo of product with 42 m³ tanks",
         audit=[
             ("Plant grade", "plant", "food grade, 304 stainless steel (Section 2.3, PDF page 6)", KEPT, None),
             ("Plant cost", "held:capex_x", "$438M for the 42 m³ plant (Table 2, PDF page 8)", CORRECTED, None),
             ("Interest on the plant", "held:fin_rate", "none: straight-line depreciation (Section 2.3, PDF page 6)", CORRECTED, None),
             ("Years to repay the plant", "held:fin_life", "10, with a 5% salvage value (Section 2.3, PDF page 6)", KEPT, None),
             ("Tank size", "held:tank_m3", "42 m³; also 211 m³ and a 262 m³ airlift (Table 2, PDF page 8)", KEPT, None),
             ("Way of running", None, "fed-batch (Section 2.2, PDF page 4)", KEPT, "fed-batch"),
             ("Densest culture", "held:x_cap", "100 g of cells a litre (Section 2.2, PDF page 4)", KEPT, None),
             ("Doubling time", "trait:doubling_h", "23 hours (Section 2.2, PDF page 4)", KEPT, None),
             ("Medium price", "held:medium_price", "$1.396 a litre, from 2022 bulk prices of a published serum-free medium "
              "(Section 2.2.1, PDF page 6)", TARGET, None),
             ("Growth factors bought on top", "held:gf_buy", "included in its medium (Section 2.2.1, PDF page 6)", KEPT, None),
             ("Differentiation", None, "10 days in the tank (Section 2.2, PDF page 4)", NOT_SET, "left out: cells as grown"),
             ("Waste the cells make", None, "Humbird's enhanced metabolism (Section 2.2.1, PDF page 6)", KEPT, "Humbird's"),
         ]),
    dict(key="garrison", study="garrison2022", label="Garrison 2022",
         mods=[],
         extra={"held": {"tank_m3": 20.0, "medium_price": round(0.28 * _cpi(2020), 2),
                         "gf_buy": 0.0, "labourx": 0.25, "capex_x": 0.34, "fin_rate": 10.0, "fin_life": 10.0}},
         text="Its most favourable variant: Specht's cheapest medium, labour and bioreactors cut by 75%.",
         own="$17.10 a kilo of meat, packed and delivered, in its most favourable variant; $63.69 as its base case",
         audit=[
             ("Tank size", "held:tank_m3", "four 20 m³ tanks (Section 2.3.1, PDF page 4)", KEPT, None),
             ("Way of running", None, "half of each tank harvested ten times in a 51-day cycle (Section 2.3.1, PDF page 4)",
              NOT_SET, "fed-batch"),
             ("Medium price", "held:medium_price", "$0.28 a litre, Specht 2020's lowest scenario, in its variant; $3.74 in its base "
              "case (Section 3.2.1, PDF page 6)", OWN, None),
             ("Growth factors bought on top", "held:gf_buy", "included in the medium (Section 3.2.1, PDF page 6)", OWN, None),
             ("Labour", "held:labourx", "94 staff, cut by 75% in its variant (Table 2; Section 3.2.1)", OWN, None),
             ("Plant cost", "held:capex_x", "$60M of equipment for 80 m³, $750k per m³ (derived), cut by 75% in its variant "
              "(Section 2.3.1; Section 3.2.1)", CORRECTED, None),
             ("Interest on the plant", "held:fin_rate", "10% (Section 2.3, PDF page 4)", KEPT, None),
             ("Years to repay the plant", "held:fin_life", "10 (Section 2.3, PDF page 4)", KEPT, None),
             ("Cells", None, "not described", HUMBIRD, "Humbird's"),
         ]),
    dict(key="pasitka", study="pasitka2024", label="Pasitka 2024",
         mods=[],
         extra={"vm": ["stirred", "perfusion"], "device": "tff",
                "held": {"tank_m3": 5.0, "medium_price": LT_MEDIUM, "gf_buy": 0.0, "harvest_loss": 1.3,
                         "capex_x": PASITKA_CAPEX_X, "mem_price": 50.0}},
         text="Its plant with tangential-flow filters, with the long-term targets for the cells and the medium.",
         own="$24.06 a kilo of wet cells for this design in 2024 dollars (its Table S10), or $32.66 with the payment on the "
             "plant its Table S4 works out",
         audit=[
             ("Vessel and way of running", "vm", "continuous perfusion (PDF page 6)", KEPT, None),
             ("Device that holds the cells back", "device", "tangential-flow filters (PDF page 6)", KEPT, None),
             ("Tank size", "held:tank_m3", "10 tanks of 5 m³ (PDF page 6)", KEPT, None),
             ("Plant cost", "held:capex_x", "$63.1M for 50 m³ of tank (Table S4)", KEPT, None),
             ("Interest on the plant", "held:fin_rate", "14.6% a year worked out in Table S4 and left out of the total (Table S10)",
              CORRECTED, None),
             ("Years to repay the plant", "held:fin_life", "with the 14.6% above (Table S4)", CORRECTED, None),
             ("Filter membranes", "held:mem_price", "24 a year at $16,000 for about 24 million litres, about 2 cents a litre "
              "filtered (Table S6)", KEPT, None),
             ("Cells lost", "held:harvest_loss", "1.3% of production (PDF page 6)", KEPT, None),
             ("Medium price", "held:medium_price", "$0.63 a litre, the 2024 price of its animal-free medium (Abstract)", TARGET, None),
             ("Growth factors bought on top", "held:gf_buy", "included in its medium (Figure 2b)", KEPT, None),
             ("Doubling time", None, "61 hours in a 1.8-litre run (PDF page 2)", TARGET, _CELLS_T + ": 24 hours"),
             ("Waste the cells make", None, "0.14 mol of ammonia a kilo, 1.05 mol of lactate per mol of glucose, in that run "
              "(PDF page 4)", TARGET, _CELLS_T),
             ("Ammonia and lactate the cells tolerate", None, "held below 3 mM and 30 mM in that run (PDF page 2)", TARGET,
              "Humbird's 5 mM and 50 mM"),
             ("Glucose and amino acids fed", None, "145 g and 81 g a kilo of cells (PDF page 4; Table S5)", CORRECTED,
              "what this model's mass balance gives"),
             ("Weight of a cell", None, "3.3 ng or 9.8 ng, from two of its figures (Abstract; PDF page 2)", HUMBIRD, "3 ng"),
             ("Density", "result:density", "up to 130 million cells a mL with serum in 5-litre tanks (Abstract)", WORKED, None),
             ("Labour", None, "Table S8", NOT_SET, "this model's"),
         ]),
    dict(key="supermeat", study="supermeat2024", label="SuperMeat 2024",
         mods=["perfusion_25", "medium_050"],
         extra={"traits": {"mass_pg": 1040.0}, "held": {"gf_buy": 0.0, "harvest_loss": 3.0, "fin_rate": 7.5, "fin_life": 10.0}},
         text="Its plant: perfusion through a membrane filter in 25 m³ tanks, its medium at scale, with the long-term target for the cells.",
         own="$29.5 a kilo of cultivated chicken with depreciation (derived from $13.4 a pound)",
         audit=[
             ("Vessel and way of running", "vm", "perfusion with continuous bleeding (PDF page 18)", KEPT, None),
             ("Tank size", "held:tank_m3", "25,000 litres (PDF pages 18 and 20)", KEPT, None),
             ("Weight of a cell", "trait:mass_pg", "1.04 g per billion stem cells (PDF page 18)", KEPT, None),
             ("Doubling time", None, "half a doubling a day while bled, from 10-litre runs (PDF page 18)", TARGET, _CELLS_T + ": 24 hours"),
             ("Density", "result:density", "80 million cells a mL, 83 g a litre, from 10-litre runs (PDF page 18)", TARGET, None),
             ("Medium price", "held:medium_price", "under $0.50 a litre at scale (PDF pages 3 and 18)", KEPT, None),
             ("Growth factors bought on top", "held:gf_buy", "included in its medium (PDF page 7)", KEPT, None),
             ("Cells lost", "held:harvest_loss", "3% rejected (PDF page 18)", KEPT, None),
             ("Interest on the plant", "held:fin_rate", "none: depreciation only (PDF page 20)", CORRECTED, None),
             ("Years to repay the plant", "held:fin_life", "not stated", HUMBIRD, None),
             ("Plant cost", None, "not given per m³", HUMBIRD, "Humbird's"),
             ("Labour", None, "100 staff and 13 outsourced (PDF page 18)", NOT_SET, "this model's"),
         ]),
    dict(key="ark", study="ark2023", label="Ark Biotech 2023",
         mods=[],
         extra={"traits": {"mass_pg": 2500.0},
                "held": {"tank_m3": 25.0, "x_cap": 75.0, "medium_price": round(0.25 * _cpi(2023), 2), "gf_buy": 0.0,
                         "fin_rate": 7.5, "fin_life": 15.0}},
         text="Its levers within reach: 25 m³ fed-batch tanks to 75 g a litre and a medium at $0.25 a litre.",
         own="$4.4 a kilo of cells with all four of its levers ($2.0 a pound); $65.0 as its baseline",
         audit=[
             ("Tank size", "held:tank_m3", "25,000-litre stirred tanks (Exhibit 8, PDF page 12)", KEPT, None),
             ("Way of running", None, "fed-batch (Exhibit 6, PDF page 8)", KEPT, "fed-batch"),
             ("Weight of a cell", "trait:mass_pg", "2,500 picograms (Exhibit 1, PDF page 4)", KEPT, None),
             ("Doubling time", None, "24 hours after a 2-day lag (Exhibit 3, PDF page 7)", KEPT, "24 hours"),
             ("Densest culture", "held:x_cap", "30 million cells a mL as its lever, 20 million as baseline (Exhibit 1, PDF page 4)", OWN, None),
             ("Medium price", "held:medium_price", "$0.25 a litre as its lever, $2 as baseline (Exhibit 1, PDF page 4)", OWN, None),
             ("Growth factors bought on top", "held:gf_buy", "included in its medium (Exhibit 2, PDF page 5)", KEPT, None),
             ("Interest on the plant", "held:fin_rate", "none: depreciation (Exhibit 8, PDF page 12)", CORRECTED, None),
             ("Years to repay the plant", "held:fin_life", "15 (Exhibit 8, PDF page 12)", KEPT, None),
             ("Larger tanks", None, "its own design up to 1,000 m³ as a lever (Exhibit 8, PDF page 12)", NOT_SET,
              "left out: this model finds larger tanks dearer, because they clear less CO₂"),
             ("Differentiation", None, "a 128% gain in mass as a lever (Exhibit 1, PDF page 4)", NOT_SET, "left out: cells as grown"),
             ("Plant cost", None, "not given per m³", HUMBIRD, "Humbird's"),
         ]),
    dict(key="gourmey", study="gourmey2025", label="Gourmey and Arthur D. Little 2025",
         mods=[],
         extra={"traits": {"doubling_h": 16.0}, "vm": ["stirred", "perfusion"], "device": "tff",
                "held": {"tank_m3": 5.0, "medium_price": round(0.20 * EUR_USD_2025, 2), "gf_buy": 0.0,
                         "capex_x": GOURMEY_CAPEX_X}},
         text="Its announced plant: six 5 m³ tanks run continuously, cells doubling in under 16 hours, medium at €0.20 a litre.",
         own="€7 a kilo, of cells or of a product half cells (not stated)",
         audit=[
             ("Vessel and way of running", "vm", "continuous runs in suspension (company announcement, 28 May 2025)", KEPT, None),
             ("Device that holds the cells back", "device", "not stated", MODEL_DEFAULT, None),
             ("Tank size", "held:tank_m3", "six 5,000-litre bioreactors (company announcement, 28 May 2025)", KEPT, None),
             ("Plant cost", "held:capex_x", "under €35M a facility, under €1.17M per m³ (derived; company announcement)", KEPT, None),
             ("Doubling time", "trait:doubling_h", "under 16 hours (press report, Green Queen, 28 May 2025)", KEPT, None),
             ("Medium price", "held:medium_price", "€0.20 a litre (company announcement, 28 May 2025)", KEPT, None),
             ("Growth factors bought on top", "held:gf_buy", "none (company announcement, 28 May 2025)", KEPT, None),
             ("Output", "result:output", "1,700 tonnes a year from 30 m³, 57 tonnes a m³ (derived; company announcement)", WORKED, None),
             ("Density, litres of medium, weight of a cell, financing", None, "not stated", HUMBIRD, "Humbird's, or this model's limits"),
         ]),
]
# studies with no set, and why (shown under the buttons)
SETS_NOT_OFFERED = ("No button: Humbird's wild-type cells (a sensitivity case of his, not a long-term estimate; it stays as a "
                    "box in \"Why published cost studies disagree\"); Lever VC 2025 and Aleph Farms 2025 (no design published); "
                    "GFI 2021 (CE Delft's study); GFI 2026 (a medium price only); Cellular Agriculture Ltd 2024 (hollow-fibre "
                    "reactors at a scale this page cannot price).")


def sets() -> list:
    """The starting sets with their merged lever settings."""
    mods = {m["key"]: m for m in modifications(with_notes=False)}
    out = []
    for st in SETS:
        e = dict(st)
        e["settings"] = merge([mods[k] for k in st["mods"]] + [{"settings": st["extra"]}])
        e["study_name"] = STUDIES[st["study"]]["name"]
        e.setdefault("name", f"{st['label']}'s assumptions on Humbird's design")
        e["audit_rows"] = audit_rows(e)
        out.append(e)
    return out


# ---------------------------------------------------------------------------------------------------------------------------
# Plant against running costs (the owner, 2026-11-24: "an interactive plot depicting the OPEX vs CAPEX of the different TEAs and
# the limit"). "Plant" is every cost that scales with what the plant cost to build: its yearly payment with interest,
# maintenance and insurance. "Running" is everything else: medium, growth factors, filters and supplies, labour, energy.
# This engine's `capital` is the first; its total less `capital` the second.
# ---------------------------------------------------------------------------------------------------------------------------
def split(settings: dict) -> dict:
    """Plant and running costs of a kilo of cells, $, for lever settings on Humbird's best estimate."""
    r = result(settings)
    return {"plant": float(r["capital"]), "running": float(r["total"] - r["capital"]), "total": float(r["total"])}


# Each study's own split, where it publishes one, as it reports it: (plant, running) in its own money and unit, the factor to
# dollars, the year of its dollars, and where the figures are. Every figure is brought to 2025 dollars by consumer prices
# (Humbird's by his own escalation, humbird_check.his_today). `set` names the starting set of the same study, if any;
# `same` says whether the study's figure is the case the set models.
_LB = 2.2046                    # pounds in a kilo (LB below)
SPLITS = [
    dict(key="humbird_best", study="humbird2021", label="Humbird 2021, best estimate", set="humbird_best", same=True,
         his="fb_hydro", basis="a kilo of wet cells",
         how="his Table 4.7, column 2: plant (capital charge, maintenance, insurance) $11.33, the rest $9.67, in 2018 dollars"),
    dict(key="humbird_perfusion", study="humbird2021", label="Humbird 2021, perfusion", set="humbird_perfusion", same=False,
         his="pf_aa", basis="a kilo of wet cells",
         how="his Table 4.13: plant $22.61, the rest $28.68, in 2018 dollars, with amino acids bought one by one (the set uses "
             "his hydrolysate)"),
    dict(key="cedelft", study="cedelft2021", label="CE Delft 2021", set="cedelft", same=True,
         plant=320.0 / 30.0 / 10.0, running=6.43 - 320.0 / 30.0 / 10.0, fx=1.0, year=2021, basis="a kilo of meat after maturation",
         how="scenario 8: $6.43 a kilo; its plant, $320M over 30 years with no interest, on 10,000 tonnes a year is $1.07 "
             "(derived; Section 3.2.5, PDF page 27); the rest $5.36. The year of its dollars is not stated: 2021 is taken"),
    dict(key="negulescu", study="negulescu2023", label="Negulescu 2023", set="negulescu", same=False,
         plant=35.0 - 25.0, running=25.0, fx=1.0, year=2022, basis="a kilo of product, about 97% wet cells",
         how="42 m³ tanks: $35 a kilo with depreciation, $25 without (Table 2, PDF page 8), so $10 of plant; the year of its "
             "dollars is not stated: 2022 is taken. Its medium at $1.40 a litre (the set uses $0.20)"),
    dict(key="garrison", study="garrison2022", label="Garrison 2022", set="garrison", same=True,
         plant=0.25 * 17.81, running=17.10 - 0.25 * 17.81, fx=1.0, year=2022, basis="a kilo of meat, packed and delivered",
         how="its most favourable variant, $17.10 a kilo (Section 3.2.1, PDF page 6): tanks and equipment at a quarter of its "
             "$17.81 (Table 2, PDF page 5), $4.45 (derived); the rest $12.65"),
    dict(key="pasitka", study="pasitka2024", label="Pasitka 2024", set="pasitka", same=False,
         plant=5.31, running=24.06 - 5.31, fx=1.0, year=2024, basis="a kilo of wet cells",
         how="its design with tangential-flow filters, $24.06 a kilo (Table S10): maintenance and insurance $5.31, the rest "
             "$18.75. It leaves out the payment on the plant its Table S4 works out, $8.60 a kilo. Its cells and medium are "
             "those of its 1.8-litre run (the set uses the long-term targets)"),
    dict(key="supermeat", study="supermeat2024", label="SuperMeat 2024", set="supermeat", same=False,
         plant=(13.4 - 11.8) * _LB, running=11.8 * _LB, fx=1.0, year=2024, basis="a kilo of cultivated chicken",
         how="$13.4 a pound with depreciation and $11.8 without (PDF page 20): $3.53 and $26.01 a kilo (derived). Its cells are "
             "those of its 10-litre runs (the set uses the long-term targets)"),
    dict(key="ark", study="ark2023", label="Ark Biotech 2023, baseline", set="ark", same=False,
         plant=3.9 * _LB, running=(29.5 - 3.9) * _LB, fx=1.0, year=2023, basis="a kilo of cells leaving the tank",
         how="its baseline, $29.5 a pound: depreciation $3.9, the rest $25.6 (Exhibit 2, PDF page 5); $8.60 and $56.44 a kilo "
             "(derived). Its lever case, which the set models, gives no split"),
    dict(key="cellag", study="cellag2024", label="Cellular Agriculture Ltd 2024", set=None, same=False,
         plant=3.58, running=11.09, fx=None, year=2024, basis="a kilo of cultured biomass",
         how="the factory of 60 tonnes a week: plant £3.58, running costs £11.09 (Table 5, PDF page 7), at $1.28 a pound "
             "sterling; the plant divided over 20 years with no interest"),
]


def splits_reported() -> list:
    """SPLITS in 2025 dollars a kilo (in each study's own unit of product)."""
    import humbird_check as HC
    out = []
    for d in SPLITS:
        e = {k: d[k] for k in ("key", "study", "label", "set", "same", "basis", "how")}
        e["study_name"] = STUDIES[d["study"]]["name"]
        if "his" in d:
            h = HC.his_today(d["his"])
            e["plant"], e["running"] = h["capital"], h["total"] - h["capital"]
        else:
            fx = GBP_USD_2024 if d["fx"] is None else d["fx"]
            e["plant"], e["running"] = d["plant"] * fx * cpi(d["year"]), d["running"] * fx * cpi(d["year"])
        out.append(e)
    return out


_PLANT_NAMES = {"lean": "a food-grade plant with shared medium", "sterile": "a food-grade plant", "pharma": "a pharma-style plant with clean rooms"}
_DEVICE_NAMES = {"tff": "a membrane filter loop (tangential flow)", "atf": "alternating-flow filters"}
_MODE_NAMES = {"fedbatch": "fed-batch", "perfusion": "perfusion"}


def _used(lever: str, settings: dict, r: dict) -> str:
    """The value a set uses for `lever`, in words, from its settings (or from the engine's result for "result:...")."""
    if lever.startswith("result:"):
        k = lever.split(":")[1]
        if k == "density":
            return f"{r['density']:.0f} g of cells a litre, limited by {r['limit']}"
        if k == "output":
            return f"{r['output']:.1f} tonnes a m³ of tank a year"
        return f"{r[k]:.1f} litres a kilo of cells"
    if lever == "vm":
        return f"a stirred tank in {_MODE_NAMES[settings['vm'][1]]}"
    if lever == "device":
        return _DEVICE_NAMES[settings.get("device", BASE_DEVICE)]
    if lever == "plant":
        return _PLANT_NAMES[settings["plant"]]
    kind, k = lever.split(":")
    v = settings["traits" if kind == "trait" else "held"][k]
    if k == "doubling_h":
        return f"{v:g} hours"
    if k == "mass_pg":
        return f"{v / 1000.0:.2f} ng"
    return {"tank_m3": f"{v:g} m³", "x_cap": f"no more than {v:g} g of cells a litre", "fin_rate": f"{v:g}% interest",
            "fin_life": f"{v:g} years", "medium_price": f"${v:.2f} a litre in 2025 dollars, growth factors in it",
            "gf_buy": "none" if v == 0 else f"{v:g}% of Humbird's", "harvest_loss": f"{v:g}%",
            "capex_x": f"${r.get('capex', 0):,.0f}k per m³ of tank" if r.get("capex") else f"{v:.2f} times this model's plant",
            "mem_price": f"${v:,.0f} a m²",
            "labourx": f"${v * value('pf_labour') * value('pf_opex_escalation'):.2f} a kilo of labour, as Humbird's fed-batch plant would pay"}[k]


def audit_rows(e: dict) -> list:
    """A set's audit as dicts: item, what the study says, what the set uses, why (AUDIT_KINDS)."""
    r = result(e["settings"])
    out = []
    for item, lever, says, why, used in e["audit"]:
        if lever and (lever.startswith("result:") or lever in ("vm", "device", "plant") and lever in e["settings"]
                      or ":" in lever and lever.split(":")[1] in e["settings"].get("traits" if lever.startswith("trait") else "held", {})):
            used = _used(lever, e["settings"], r)
        elif used is None:
            used = "Humbird's"
        out.append({"item": item, "lever": lever, "study": says, "used": used, "why": why})
    return out


def table() -> dict:
    """Each modification alone and together on Humbird's best estimate: `lower` is every modification that lowers the cost
    alone, together (where two set the same lever, the later in the list is used); `higher` the same for those that raise it."""
    mods = modifications(with_notes=False)
    base = cost({})
    rows = [{"key": m["key"], "label": m["label"], "cost": cost(m["settings"]), "own": m["own"]} for m in mods]
    return {"base": base, "rows": rows, "all": cost(merge(mods)),
            "lower": cost(merge([m for m, r in zip(mods, rows) if r["cost"] < base - 1e-9])),
            "higher": cost(merge([m for m, r in zip(mods, rows) if r["cost"] > base + 1e-9]))}


# ---------------------------------------------------------------------------------------------------------------------------
# What each study assumes on each lever of the all-favourable case, and the values that break a limit of the model
# ---------------------------------------------------------------------------------------------------------------------------
# US consumer prices, all urban consumers, yearly averages: the official BLS CPI-U figures stored once in inputs.py (cpi_u_YEAR,
# series CUUR0000SA0, fetched 2026-11-20). Until 2026-11-20 they were typed here from memory. Every study, Humbird's included,
# is brought to today's dollars by the same rule: `cpi(year)`.
TODAY = 2025
CPI = {y: value(f"cpi_u_{y}") for y in range(2018, TODAY + 1)}


def cpi(year: int) -> float:
    """Today's dollars per dollar of `year` (CPI-U, the year capped at TODAY)."""
    return CPI[TODAY] / CPI[min(year, TODAY)]


# lever (the first explore() argument of its row in scenarios.favourable_levers; "recovery" and "vessel_m3" are rows too;
# "medium_kg" and "glucose_g" are what a kilo of cells is fed, compared in tests/test_ordering.py) -> study -> [(value, where)].
# Every value a study states is listed, the rejected ones too (REJECTED says why they are not sources).
STUDY_LEVERS = {
    "nh3_kg": {"pasitka2024": [(0.14, "2.4 g of ammonia a kilo of wet cells, measured (PDF page 4); derived: 2.4 / 17.03")]},
    "lac_yield": {"pasitka2024": [(1.05, "76 g of lactate from 145 g of glucose a kilo of wet cells, measured (PDF page 4); derived")]},
    "mass_pg": {
        "risner2021": [(5300.0, "5.00e-15 m³ a cell at 1,060 kg per m³, in every scenario (Table A2, PDF page 19); derived: 5.3 ng")],
        "cedelft2021": [(3610.0, "3,500 µm³ (Table 5, PDF page 37); derived at 1.03 g/mL, the wet cells of Humbird's Table 2.2"),
                        (5160.0, "5,000 µm³ in scenario 8 (Section 3.2.5, PDF page 27); derived at 1.03 g/mL")],
        "negulescu2023": [(3000.0, "3 ng a cell (Section 2.2, PDF page 4)")],
        "supermeat2024": [(1040.0, "1.04 g per billion stem cells (PDF page 18)")],
        "ark2023": [(2500.0, "2,500 picograms a cell (Exhibit 1, PDF page 4)")]},
    "doubling_h": {
        "risner2021": [(24.0, "scenario 1 (Table A2, PDF page 19)"), (16.0, "scenarios 2 and 3 (Table A2, PDF page 19)"),
                       (8.0, "scenario 4 (Table A2, PDF page 19)")],
        "cedelft2021": [(30.0, "Table 5, PDF page 36")],
        "negulescu2023": [(23.0, "Section 2.2, PDF page 4")],
        "pasitka2024": [(61.0, "through the 20-day continuous run, measured (PDF page 2)")],
        "supermeat2024": [(48.0, "0.5 doublings a day while bleeding (PDF page 18); derived")],
        "ark2023": [(24.0, "24 hours, after a lag of 2 days (Exhibit 3, PDF page 7)")]},
    "nh3_limit": {"pasitka2024": [(3.0, "ammonia held below 3 mM (PDF page 2)")]},
    "lac_limit": {"pasitka2024": [(30.0, "lactate held below 30 mM (PDF page 2)")]},
    "growth_factors": {"risner2021": [(0.0, "scenario 4 prices insulin, transferrin, FGF-2 and TGF-β at nothing (Table A3, PDF page 20)")]},
    "x_visc": {
        "risner2021": [(53.0, "scenario 1: 10 million cells a mL (Table A1, PDF page 19); derived at 5.3 ng: 5% of the volume"),
                       (504.0, "scenarios 2 and 3: 95 million cells a mL (Table A1, PDF page 19); derived: 47.5% of the volume"),
                       (1060.0, "scenario 4: 200 million cells a mL (Table A1, PDF page 19); derived: 100% of the volume")],
        "cedelft2021": [(258.0, "50 million cells a mL of 5,000 µm³ in scenario 8 (Table 5, PDF page 37; PDF page 27); derived: 25% "
                                "of the volume, Humbird's own limit")],
        "negulescu2023": [(100.0, "each step ends at 100 g of fresh cells a litre (Section 2.2, PDF page 4)")],
        "pasitka2024": [(430.0, "130 million cells a mL, 43% weight per volume, in 5-litre glass tanks with serum (Abstract and "
                                "Figure 1, PDF pages 1 and 3)")],
        "supermeat2024": [(83.0, "80 million cells a mL at 1.04 ng (PDF page 18); derived")],
        "lever2025": [(90.0, "60 to 90 g/L at several companies (PDF page 3)")],
        "ark2023": [(75.0, "30 million cells a mL as its lever, 20 million as its baseline (Exhibit 1, PDF page 4); derived at 2.5 ng")]},
    "vessel_m3": {
        "cedelft2021": [(10.0, "stirred tanks of 10 m³ working volume (Table 2, PDF page 13)")],
        "risner2021": [(20.0, "Table A1, PDF page 19")],
        "negulescu2023": [(211.0, "stirred tanks of 211 m³; also 42 m³, and an airlift of 262 m³ that this engine does not price "
                                  "(Table 2, PDF page 8)")],
        "garrison2022": [(20.0, "four 20 m³ tanks (Section 2.3.1, PDF page 4)")],
        "pasitka2024": [(5.0, "10 tanks of 5 m³ with tangential-flow filters; also 25 of 2 m³ and 2 of 25 m³ (PDF page 6)")],
        "supermeat2024": [(25.0, "25,000-litre tanks (PDF pages 18 and 20)")],
        "ark2023": [(25.0, "25,000-litre stirred tanks as the baseline; also its own design at 100, 250 and 1,000 m³, which this "
                           "engine does not price (Exhibit 8, PDF page 12)")]},
    "recovery": {
        "risner2021": [(0.0882, "90% debt at 5% and equity at 15% over 20 years, each with its own repayment (Table A7, PDF page 22); "
                                "derived: 0.9 x 8.02% + 0.1 x 15.98%")],
        "cedelft2021": [(0.25, "payback in 4 years, its commercial criterion (Section 3.2.3, PDF page 24)"),
                        (1.0 / 30.0, "payback in 30 years with no interest, its social criterion (Section 3.2.3, PDF page 24)")],
        "negulescu2023": [(0.095, "straight-line depreciation over 10 years to a 5% salvage value, no interest (Section 2.3, PDF page 6)")],
        "garrison2022": [(0.1627, "10% over 10 years (Section 2.3, PDF page 4; Table 2, PDF page 5)")],
        "pasitka2024": [(0.0, "its cost lines show maintenance and insurance and no payment on the plant (Figure 4, PDF page 7)")],
        "ark2023": [(1.0 / 15.0, "depreciation over 15 years with no salvage value, no interest (Exhibit 8, PDF page 12)")],
        "cellag2024": [(1.0 / 20.0, "the plant divided by the yearly output over 20 years, no interest (Fixed cost estimation, PDF page 2)")]},
    # the medium for a kilo of cells, in today's dollars (the study's figure x consumer prices since its year: CPI below)
    "medium_kg": {
        "risner2021": [(1.70 * cpi(2019), "scenario 4: 7.1 litres a kilo at $0.24 a litre, $1.70 in 2019 dollars (Table 2, PDF page 9); derived")],
        "negulescu2023": [(14.2 * cpi(2022), "10.2 litres a kilo at $1.396 a litre, $14.2 (Section 2.2.1, PDF page 6); derived")],
        "garrison2022": [(19.66 * cpi(2022), "$19.66 (Table 2, PDF page 5)")],
        "pasitka2024": [(14.1 * cpi(2024), "22.4 litres a kilo at $0.63 a litre, $14.1 (PDF pages 1 and 6); derived")],
        "supermeat2024": [(15.3 * cpi(2024), "30.5 litres a kilo at $0.50 a litre, $15.3 (PDF page 20); derived")]},
    "glucose_g": {
        "risner2021": [(45.0, "scenario 4: 0.0356 mol a litre (Table A4, PDF page 20) in 7.1 litres a kilo; derived")],
        "cedelft2021": [(15.0, "15 g of sugars for a kilo of meat, low medium use (Table 11, PDF page 41)")]},
}
# the direction that is favourable for the levers that are not rows of scenarios.favourable_levers
EXTRA_DIRECTION = {"medium_kg": "lower", "glucose_g": "lower"}


def limits() -> dict:
    """The named limits of the model: key -> (plain name, value, unit, source)."""
    from inputs import AA_FLOOR, GLUCOSE_OTHER_FLOOR
    floor = AA_FLOOR + GLUCOSE_OTHER_FLOOR
    return {
        "nutrients_cost": ("the nutrient floor: cells cannot cost less than the nutrients they are built from", floor, "$ a kilo of cells",
                           f"inputs.py: {value('aa_intensity') * 1000:.0f} g of amino acids at feed-grade prices (GFI 2025), glucose, salts "
                           "and vitamins; research_notes/nutrient_floor.md"),
        "nutrients_mass": ("the mass balance: cells cannot be built and fuelled from less sugar than they burn",
                           value("glucose_intensity") * 1000.0, "g of glucose a kilo of cells",
                           "inputs.py glucose_intensity, from Humbird 2021, Section 2.2: 0.36 kg of glucose a kilo of wet cells for "
                           "his enhanced cell (Reaction 2.11)"),
        "thickness": ("the thickest culture that still flows", value("pf_x_visc"), "g of wet cells a litre",
                      "Humbird 2021, Section 2.1 and Table 2.2, PDF pages 19 and 20: cells at 25% of the volume, where the culture "
                      "is about twice as viscous as water; spheres cannot pack beyond 65%. The all-favourable case allows 320 g/L "
                      "(31%), this model's own stretch (research_notes/thick_culture.md gives a 20 m³ tank at 320 g/L a 6% "
                      "chance); no study's value between 258 and 320 depends on it"),
        "growth": ("a growth rate faster than any measured in animal cells", value("cr_td_engineering"), "hours to double",
                   "inputs.py cr_td_engineering: immortalised bovine muscle cells with serum, Stout 2023, the fastest doubling "
                   "of a meat cell line found; Humbird 2021, Section 2.2, PDF page 24, adds that fast growth and little waste "
                   "do not go together"),
        "oxygen": ("oxygen transfer and CO₂ removal for the tank", None, "g of wet cells a litre",
                   "the engine, from Humbird 2021, Section 2.3, PDF pages 29 to 34: gas at 0.006 m/s at most, 100 mbar of CO₂; a "
                   "20 m³ tank on 90% oxygen holds 120 g/L"),
        "waste": ("the waste the cells tolerate against what they make", None, "mmol a litre",
                  "the engine, from Humbird 2021, Section 2.3, PDF page 31: 5 mmol/L of ammonia and 50 of lactate"),
        "capital": ("the plant must be repaid at a market rate of interest", None, "share of the plant's cost a year",
                    "an economic condition, not a physical limit: a long-run price must pay for the money a plant ties up, at a "
                    "market rate. Humbird 2021, Section 3.1, PDF page 44, quotes 5.4% as the cost of capital of food processing, "
                    "the lowest he gives; this model's 5.4% over 20 years is a payment of 8.3% a year. The interest lever still "
                    "goes to 0%, with a chip 'no interest (CE Delft 2021)', so the effect can be seen"),
        "mass": ("a meat cell heavier than any measured growing in suspension", value("cr_mass_measured_max_pg"), "pg",
                 "inputs.py cr_mass_measured_max_pg: the larger of Humbird's 3 ng and the heaviest credible measurement of a meat "
                 "cell growing in suspension (SuperMeat 2024, 1.75 ng weighed, about 2.3 ng from its diameter). The same rule as "
                 "for growth: a value beyond what has been measured is rejected unless a measurement exists"),
    }


# Every study value that is more favourable than a limit allows. `value` is the study's, `limit_value` what the limit allows,
# both in `unit`. The page references are those of STUDY_LEVERS; `why` is one plain sentence a reader sees.
REJECTED = [
    dict(study="risner2021", lever="x_visc", value=1060.0, limit="thickness", limit_value=258.0, unit="g of wet cells a litre",
         assumption="200 million cells a mL, each of 5,000 µm³ (scenario 4)", ref="Tables A1 and A2, PDF page 19",
         why="The cells fill 100% of the tank, with no room for medium, which the study itself notes (Appendix A, PDF page 12). "
             "Humbird's limit for a culture that still flows is 25% of the volume."),
    dict(study="risner2021", lever="x_visc", value=504.0, limit="thickness", limit_value=258.0, unit="g of wet cells a litre",
         assumption="95 million cells a mL, each of 5,000 µm³ (scenarios 2 and 3)", ref="Tables A1 and A2, PDF page 19",
         why="The cells are 47.5% of the tank's volume, against Humbird's limit of 25%."),
    dict(study="risner2021", lever="doubling_h", value=8.0, limit="growth", limit_value=15.0, unit="hours to double",
         assumption="cells that double every 8 hours (scenario 4)", ref="Table A2, PDF page 19",
         why="No animal cell line has been measured doubling faster than about 15 hours."),
    dict(study="risner2021", lever="glucose_g", value=45.0, limit="nutrients_mass", limit_value=None, unit="g of glucose a kilo of cells",
         assumption="0.0356 mol of glucose a litre in 7.1 litres of medium a kilo of cells (scenario 4)",
         ref="Table A4, PDF page 20; Table 2, PDF page 9",
         why="The medium holds 45 g of glucose for a kilo of cells, a seventh of what Humbird's most efficient cell burns."),
    dict(study="cedelft2021", lever="glucose_g", value=15.0, limit="nutrients_mass", limit_value=None, unit="g of glucose a kilo of cells",
         assumption="15 g of sugars for a kilo of meat (low medium use)", ref="Table 11, PDF page 41",
         why="The medium holds 15 g of sugars for a kilo of meat, about a twentieth of what Humbird's most efficient cell burns."),
    dict(study="cedelft2021", lever="recovery", value=1.0 / 30.0, limit="capital", limit_value=None, unit="share of the plant's cost a year",
         assumption="the plant paid back over 30 years with no interest (scenarios 6 to 8)", ref="Section 3.2.3, PDF page 24",
         why="The plant must be repaid at a market rate of interest: money lent for 30 years at no interest is not a cost of "
             "production. The study calls it a social criterion."),
    dict(study="pasitka2024", lever="x_visc", value=430.0, limit="thickness", limit_value=258.0, unit="g of wet cells a litre",
         assumption="130 million cells a mL, 43% weight per volume, in 5-litre glass tanks with serum",
         ref="Abstract and Figure 1, PDF pages 1 and 3",
         why="43% is a weight of wet pellet in a 5-litre tank, not a culture stirred at scale; the study's own cell counts give "
             "3.3 ng and 9.8 ng a cell. Its cost projection does not use it: it rests on a run held at 10 to 28 million cells a mL."),
    dict(study="pasitka2024", lever="recovery", value=0.0, limit="capital", limit_value=None, unit="share of the plant's cost a year",
         assumption="no payment on the plant among its cost lines", ref="Figure 4, PDF page 7; Supplementary Tables S4 and S10",
         why="The plant must be repaid at a market rate of interest: a plant that is never repaid is not a cost of production. "
             "Its Table S4 computes a charge of 14.6% of the plant a year, but Table S10 leaves it out of the total: with it, "
             "the large-scale case is $26.99 a kilo of cells in 2024 dollars, not $21.49."),
    dict(study="ark2023", lever="recovery", value=1.0 / 15.0, limit="capital", limit_value=None, unit="share of the plant's cost a year",
         assumption="the plant written off over 15 years with no interest", ref="Exhibit 8, PDF page 12",
         why="The plant must be repaid at a market rate of interest: depreciation alone leaves out what the money costs. The "
             "study also counts nothing after the bioreactor."),
    dict(study="cellag2024", lever="recovery", value=1.0 / 20.0, limit="capital", limit_value=None, unit="share of the plant's cost a year",
         assumption="the plant divided over 20 years of output with no interest", ref="Fixed cost estimation, PDF page 2",
         why="The plant must be repaid at a market rate of interest: depreciation alone leaves out what the money costs."),
    # 2026-11-20: cell weight follows the same rule as doubling time
    dict(study="risner2021", lever="mass_pg", value=5300.0, limit="mass", limit_value=None, unit="pg",
         assumption="a cell of 5.00e-15 m³ at 1,060 kg per m³, 5.3 ng (every scenario)", ref="Table A2, PDF page 19",
         why="An assumption of the analysis, not a measurement. No meat cell growing in suspension has been measured above "
             "about 2.3 ng (SuperMeat 2024), so the heaviest allowed is Humbird's 3 ng."),
    dict(study="cedelft2021", lever="mass_pg", value=5160.0, limit="mass", limit_value=None, unit="pg",
         assumption="a cell of 5,000 µm³ in scenario 8, 5.2 ng at 1.03 g/mL", ref="Section 3.2.5, PDF page 27",
         why="An assumption of the analysis, not a measurement, beyond any meat cell measured growing in suspension."),
    dict(study="cedelft2021", lever="mass_pg", value=3610.0, limit="mass", limit_value=None, unit="pg",
         assumption="a cell of 3,500 µm³, 3.6 ng at 1.03 g/mL", ref="Table 5, PDF page 37",
         why="An assumption of the analysis, not a measurement, beyond any meat cell measured growing in suspension."),
]


def rejected() -> list:
    """REJECTED with each limit's name, value and source filled in from `limits()`."""
    L = limits()
    out = []
    for r in REJECTED:
        name, val, _unit, src = L[r["limit"]]
        r = dict(r, study_name=STUDIES[r["study"]]["name"], limit_name=name, limit_source=src)
        if r["limit_value"] is None:
            r["limit_value"] = val if val is not None else value("plant_charge_mature") - 0.09
        out.append(r)
    return out


def is_rejected(lever: str, study: str, v: float) -> bool:
    return any(r["lever"] == lever and r["study"] == study and abs(r["value"] - v) < 1e-9 for r in REJECTED)


def favourable_value(lever: str, study: str, better: str) -> tuple:
    """A study's most favourable value on a lever that breaks no limit, and where it is from: (value or None, text). For a lever
    without a direction (`better` == "cost") the first value listed."""
    vals = STUDY_LEVERS.get(lever, {}).get(study)
    if not vals:
        return (None, "not stated")
    ok = [(v, w) for v, w in vals if not is_rejected(lever, study, v)]
    bad = [(v, w) for v, w in vals if is_rejected(lever, study, v)]
    note = "".join(f"; its {v:g} is not taken (it breaks a limit: study_comparison.md)" for v, _w in bad)
    if not ok:
        return (None, "none that respects the limits" + note)
    v, w = ok[0] if better == "cost" else (min if better == "lower" else max)(ok, key=lambda x: x[0])
    return (v, w + note)


# ---------------------------------------------------------------------------------------------------------------------------
# Each study's own most favourable published estimate, as a kilo of wet cells in today's dollars
# ---------------------------------------------------------------------------------------------------------------------------
LB = 2.2046                     # pounds in a kilo
GBP_USD_2024 = 1.28             # dollars per pound sterling, about the 2024 average; typed from memory, to be checked against an official series

# published: the figure as the study prints it; per_kg_cells: the same as $ a kilo of wet cells in the study's own dollars, with
# `how`; year: the year of its dollars, with `year_how` (stated, or why this year is taken); ref: where it is printed.
ESTIMATES = {
    "humbird2021": dict(published="$21.00 a kilo of wet cells", ref="Table 4.7, column 2, PDF page 62", per_kg_cells=21.00,
                        how="already a kilo of wet cells, with the yearly charge on the plant", year=2018,
                        year_how="his buildings and equipment are in 2018 dollars (Table 3.2, PDF page 40)"),
    "cedelft2021": dict(published="$6.43 a kilo of cultivated meat", ref="Section 3.2.5, PDF page 28 (scenario 8)", per_kg_cells=6.43,
                        how="the product is cells after maturation, 70 to 77% water (PDF page 10), so it is taken as a kilo of wet "
                            "cells; the plant is repaid over 30 years with no interest",
                        year=2021, year_how="not stated; the year of publication is taken (prices were collected from December 2020)"),
    "risner2021": dict(published="$1.95 a kilo of cell-based meat", ref="Table 2, PDF page 9 (scenario 4)", per_kg_cells=1.95,
                       how="its meat is the wet mass of the cells (Appendix A, PDF page 15); only the tanks are charged as capital",
                       year=2019, year_how="energy prices are in January 2019 dollars and the medium at 2019 prices (PDF pages 5 and 6)"),
    "negulescu2023": dict(published="$16 a kilo of product without depreciation, $17 with", ref="Table 2, PDF page 8 (262 m³ airlift)",
                          per_kg_cells=16.0 / 0.97,
                          how="the product is about 97% wet cells (PDF page 6): $16 / 0.97, with the other 3% counted as free",
                          year=2022, year_how="not stated; it uses a 2021 plant-cost index and 2022 glucose prices"),
    "garrison2022": dict(published="$63.69 a kilo of meat; $17.10 with the cheapest published medium and tanks and labour cut by 75%",
                         ref="Table 2, PDF page 5; Section 3.2, PDF page 6", per_kg_cells=17.10,
                         how="the meat is all cells, packed and delivered; the lower figure is a variant the study computes, not its estimate",
                         year=2022, year_how="not stated; the year of publication is taken"),
    "pasitka2024": dict(published="$6.2 a pound of a product that is half cells", ref="Abstract, PDF page 1; Figure 4, PDF page 7",
                        per_kg_cells=(6.2 * LB - 3.0) * 2.0,
                        how="a kilo of product is half a kilo of wet cells and $3 of plant ingredients, as the study's own $6.8 a "
                            "pound and $24.06 a kilo of cells imply: ($6.2 x 2.2046 - $3) x 2; no payment on the plant",
                        year=2024, year_how="not stated; the year of publication is taken (it compares with a 2024 retail price)"),
    "supermeat2024": dict(published="$11.8 a pound without depreciation, $13.4 with", ref="PDF page 20", per_kg_cells=11.8 * LB,
                          how="the product is all cells after a short maturation: $11.8 x 2.2046",
                          year=2024, year_how="not stated; the year of publication is taken"),
    "lever2025": dict(published="$10 to $15 a kilo of cell mass; some companies below $10, with no figure", ref="PDF page 3",
                      per_kg_cells=10.0,
                      how="the low end of the range it states; wet or dry mass and whether the plant is charged are not stated",
                      year=2025, year_how="the year of the report"),
    "gfi2021": dict(published="$6.43 a kilo ($2.92 a pound)", ref="PDF page 2", per_kg_cells=6.43,
                    how="CE Delft's figure, which this report summarises", year=2021, year_how="as CE Delft 2021"),
    "gfi2026": dict(published=None, ref="PDF pages 8 and 30", per_kg_cells=None,
                    how="it gives no cost of cells or of meat, only prices of medium a litre", year=2026, year_how=""),
    "ark2023": dict(published="$2.0 a pound with all four of its levers ($29.5 as its baseline)", ref="Exhibit 1, PDF page 4",
                    per_kg_cells=2.0 * LB,
                    how="a kilo of cells leaving the tank, with no differentiation credit removed: $2.0 x 2.2046. The headline figure "
                        "is taken; its Exhibit 10 (PDF page 14) also shows example paths down to $0.3 a pound, which need cells "
                        "that gain 3,000% in mass while differentiating",
                    year=2023, year_how="not stated; the year of publication is taken"),
    "cellag2024": dict(published="£14.68 a kilo of cultured biomass (factory of 60 tonnes a week)", ref="Table 5, PDF page 7",
                       per_kg_cells=14.68 * GBP_USD_2024,
                       how="already a kilo of cultured biomass; pounds to dollars at 1.28, about the 2024 average rate (typed from "
                           "memory, not fetched from an official series)",
                       year=2024, year_how="not stated; the year of publication is taken"),
    "gourmey2025": dict(published="€7 a kilo ($3.43 a pound)", ref="company announcement, 28 May 2025", per_kg_cells=3.43 * LB,
                        how="the company's own dollar figure, $3.43 x 2.2046, read as a kilo of cells, the more favourable reading: "
                            "the announcement does not say of what, and the press reports a product about half cells. Whether "
                            "the plant is charged is not stated",
                        year=2025, year_how="the year of the announcement"),
    "aleph2025": dict(published="as low as $4.08 a pound of end products ($6.45 as its estimate, with the plant)",
                      ref="company announcement, September 2025", per_kg_cells=4.08 * LB,
                      how="the low end of its sensitivity analysis, $4.08 x 2.2046, read as a kilo of cells, the more favourable "
                          "reading: the share of cells in the product is not stated",
                      year=2025, year_how="the year of the announcement"),
}


def estimates() -> dict:
    """ESTIMATES with `today`: $ a kilo of wet cells in today's dollars. Humbird's is converted as the page converts it (his
    capital by the plant-cost index, everything else by consumer prices: humbird_check.his_today); the others by consumer
    prices from the year of their dollars (CPI)."""
    import humbird_check as HC
    out = {}
    for k, e in ESTIMATES.items():
        e = dict(e, name=STUDIES[k]["name"])
        if e["per_kg_cells"] is None:
            e["today"] = None
        else:                   # the same rule for every study, Humbird's included (2026-11-20; it used his_today until then)
            f = cpi(e["year"])
            e["today"] = e["per_kg_cells"] * f
            e["factor_how"] = f"consumer prices (BLS CPI-U), {TODAY} over {min(e['year'], TODAY)}: x {f:.3f}"
        out[k] = e
    return out


def risner_inside_limits() -> dict:
    """Risner's scenario 4 in this engine with the assumptions that break a limit brought inside it (2026-11-20: his 5.3 ng cell
    too, held at the heaviest allowed, 3 ng); his 20 m³
    tanks run in batches, his tanks-only capital ($778,000 for a 20 m³ tank, PDF page 7: $38.9k per m³, taken as 2018 dollars)
    and his yearly charge on it (8.8% + 15%), no growth factors bought, his medium at $0.24 a litre in 2019 dollars (which in
    today's dollars is $2.14 a kilo of cells, just above the nutrient floor); but cells
    that double in 15 hours (the fastest measured), a density the tank's oxygen, CO₂ and waste allow (Humbird's limits and his
    enhanced cell's waste, since the study states none), and nutrients that cost at least the nutrient floor. Labour, energy
    and the cells lost are this engine's own."""
    import scenarios as S
    kw = dict(mass_pg=value("cr_mass_measured_max_pg"), doubling_h=value("cr_td_engineering"), vessel_m3=20.0, capex_2018=778.0 / 20.0, charge=0.0882 + 0.15,
              growth_factors=0.0, medium_price=0.24 * cpi(2019))
    kw.update(copy.deepcopy(S.setting("mode", "fedbatch").kw))
    return fp.explore(**kw)


# The studies whose most favourable estimate is below the all-favourable case. Each names the REJECTED assumptions behind it and,
# where the study publishes enough, a function giving its design in this engine with those brought inside the limits.
EXCEPTIONS = {
    "risner2021": dict(levers=(("x_visc", 1060.0), ("doubling_h", 8.0), ("glucose_g", 45.0), ("mass_pg", 5300.0)), inside=risner_inside_limits,
                       inside_how="its 20 m³ batch tanks, tanks-only capital and financing and $0.24 a litre of "
                                  "medium, with cells of 3 ng (not 5.3), a 15-hour doubling, the density that oxygen, CO₂ and waste allow, and "
                                  "at least the nutrients the cells are built from"),
    "ark2023": dict(levers=(("recovery", 1.0 / 15.0),)),
}
# The studies with no estimate to compare, and why.
NOT_COMPARED = {"gfi2026": "it gives no cost of cells or of meat, only prices of medium a litre"}
# Assumptions the all-favourable case does not take although no physical limit rules them out, because they are not like for like
# with a lever of the engine. Reported in study_comparison.md for the owner to decide.
NOT_LIKE_FOR_LIKE = [
    ("What the plant costs to build", "CE Delft 2021: $167k to $277k per m³ of tank (derived; Section 3.2.3, PDF page 23); Negulescu "
     "2023: $209k per m³ at 42 m³ (derived; Table 2, PDF page 8); Risner 2021: $39k per m³, the tanks alone (PDF page 7). The "
     "all-favourable case builds this model's own food-grade plant with shared medium item by item from Humbird's equipment list. "
     "The studies' plants hold different equipment and make different amounts per m³, so a cost per m³ does not carry over."),
    ("Staff", "Risner 2021 and Lever VC 2025 state no staff; CE Delft 130 to 200 for 10,000 tonnes. The all-favourable case keeps "
     "the model's staff per m³ of tank, from Humbird."),
]


def comparison() -> dict:
    """Each study's most favourable estimate against the all-favourable case: {'all_favourable': $, 'rows': [...], 'below':
    [...]}. A row is compared (`today` given), or `not_compared` with the reason. `below` lists, for each study whose estimate
    is under the all-favourable case, the rejected assumptions behind it and its design inside the limits."""
    import scenarios as S
    fav = S.all_favourable()["cost"]
    est, rej = estimates(), rejected()
    rows, below = [], []
    for k in STUDIES:
        e = est[k]
        row = dict(key=k, name=e["name"], published=e["published"], ref=e["ref"], how=e["how"], year=e["year"], year_how=e["year_how"],
                   per_kg_cells=e["per_kg_cells"], today=e["today"], factor_how=e.get("factor_how", ""), not_compared=NOT_COMPARED.get(k))
        row["below"] = e["today"] is not None and e["today"] < fav
        rows.append(row)
        if row["below"]:
            ex = EXCEPTIONS.get(k)
            inside = ex["inside"]() if ex and ex.get("inside") else None
            below.append(dict(key=k, name=e["name"], published=e["published"], today=e["today"],
                              assumptions=[r for r in rej if r["study"] == k and (ex is None or (r["lever"], r["value"]) in ex["levers"])],
                              listed=ex is not None, inside=None if inside is None else inside["total"],
                              inside_density=None if inside is None else inside["density"],
                              inside_how=ex.get("inside_how") if ex else None))
    return {"all_favourable": fav, "rows": rows, "below": below}


def _af_split() -> dict:
    """The all-favourable case's plant and running costs (scenarios.all_favourable), $ a kilo of cells."""
    import scenarios as S
    r = S.all_favourable()["result"]
    return {"plant": float(r["capital"]), "running": float(r["total"] - r["capital"]), "total": float(r["total"])}


def page_data() -> dict:
    """What the page's card needs (MODEL.tp.studies): the modifications with their lever settings, the notes, each study's own
    reported cost and its most favourable estimate in today's dollars, and the estimates below the all-favourable case."""
    keep = ("key", "label", "text", "solid", "own", "settings", "not_representable", "reason")
    c = comparison()
    est = {r["key"]: r for r in c["rows"]}
    return {"base_label": BASE_LABEL, "base_key": BASE_KEY,
            "base": {"vm": BASE_VM, "plant": BASE_PLANT, "device": BASE_DEVICE},
            "mods": [{k: m[k] for k in keep if k in m} for m in modifications()],
            "sets": [{k: e[k] for k in ("key", "label", "name", "study_name", "text", "own", "settings", "audit_rows")} for e in sets()],
            "audit_why": AUDIT_WHY,
            "sets_not_offered": SETS_NOT_OFFERED,
            "splits": splits_reported(),
            "af_split": _af_split(),
            "studies": [{"key": k, "name": s["name"], "system": s["system"], "cost": s["cost"], "basis": s["basis"],
                         "explains": s["explains"], "published": est[k]["published"], "today": est[k]["today"],
                         "today_how": (est[k]["how"] + "; " + est[k]["factor_how"]) if est[k]["today"] is not None else est[k]["how"]}
                        for k, s in STUDIES.items()],
            "all_favourable": c["all_favourable"],
            "below": [{"name": b["name"], "published": b["published"], "today": b["today"], "inside": b["inside"],
                       "inside_how": b["inside_how"],
                       "assumptions": [{"assumption": a["assumption"], "ref": a["ref"], "limit": a["limit_name"], "why": a["why"]}
                                       for a in b["assumptions"]]} for b in c["below"]]}


def markdown() -> str:
    """The tables of research_notes/study_comparison.md, from the code: the all-favourable case lever by lever with every
    source's value, the rejected values, the estimates, and the modifications."""
    import scenarios as S
    a = S.all_favourable()
    names = dict(S.FAV_SOURCES)
    show = lambda v: "none" if v is None else (", ".join(str(x) for x in v) if isinstance(v, tuple) else f"{v:.4g}" if isinstance(v, float) else str(v))
    out = ["### The all-favourable case, lever by lever\n"]
    for r in a["levers"]:
        better = {"lower": "lower is favourable", "higher": "higher is favourable", "cost": "the setting that costs least is taken"}[r["better"]]
        out.append(f"**{r['lever']}** ({r['unit']}; {better}). Taken: **{show(r['value'])}**, from {names[r['source']]}.\n")
        out.append("| source | value | where it is from |")
        out.append("|---|---|---|")
        for sk, sn in S.FAV_SOURCES:
            v, w = r["sources"][sk]
            if v is None and w == "not stated":
                continue
            out.append(f"| {sn} | {show(v)} | {w} |")
        silent = [sn for sk, sn in S.FAV_SOURCES if r["sources"][sk] == (None, "not stated")]
        if silent:
            out.append(f"\nNot stated by: {', '.join(silent)}.")
        out.append("")
    out.append("### What a kilo of cells is fed\n")
    out.append("| study | medium for a kilo of cells, today's dollars | glucose for a kilo of cells, g |")
    out.append("|---|---|---|")
    for k, st in STUDIES.items():
        m, g = STUDY_LEVERS["medium_kg"].get(k), STUDY_LEVERS["glucose_g"].get(k)
        if m or g:
            out.append(f"| {st['name']} | {'$%.2f: %s' % m[0] if m else ''} | {'%g: %s' % g[0] if g else ''} |")
    out.append("")
    out.append("### Study values that are not taken, and the limit each breaks\n")
    out.append("| study | what it assumes | where | its value | the limit allows | the limit | the limit's source |")
    out.append("|---|---|---|---|---|---|---|")
    for r in rejected():
        out.append(f"| {r['study_name']} | {r['assumption']}. {r['why']} | {r['ref']} | {r['value']:.4g} {r['unit']} | {r['limit_value']:.4g} | "
                   f"{r['limit_name']} | {r['limit_source']} |")
    out.append("")
    c = comparison()
    out.append(f"### Each study's most favourable estimate against the all-favourable case (${c['all_favourable']:.2f})\n")
    out.append("| study | as published | where | as a kilo of wet cells | year of its dollars | in today's dollars | against the case |")
    out.append("|---|---|---|---|---|---|---|")
    for r in c["rows"]:
        if r["today"] is None:
            out.append(f"| {r['name']} | none | {r['ref']} | not compared: {r['not_compared']} | | | |")
            continue
        out.append(f"| {r['name']} | {r['published']} | {r['ref']} | ${r['per_kg_cells']:.2f}: {r['how']} | {r['year']}: {r['year_how']} | "
                   f"**${r['today']:.2f}** ({r['factor_how']}) | {'**below**' if r['below'] else 'above'} |")
    out.append("")
    t = table()
    out.append(f"### The modifications on Humbird's best estimate (${t['base']:.2f})\n")
    out.append("| modification | cost alone | change | the study's own reported cost |")
    out.append("|---|---:|---:|---|")
    for r in t["rows"]:
        out.append(f"| {r['label']} | ${r['cost']:.2f} | {r['cost'] - t['base']:+.2f} | {r['own']} |")
    out.append(f"| Every modification that lowers the cost alone, together | ${t['lower']:.2f} | {t['lower'] - t['base']:+.2f} | |")
    out.append(f"| Every modification that raises the cost alone, together | ${t['higher']:.2f} | {t['higher'] - t['base']:+.2f} | |")
    out.append(f"| All together (where two set the same lever, the later is used) | ${t['all']:.2f} | {t['all'] - t['base']:+.2f} | |")
    out.append("")
    return "\n".join(out)


def main() -> None:
    t = table()
    print(f"  {BASE_LABEL}: ${t['base']:.2f} a kilo of cells\n")
    print(f"  {'cost alone':>10}  {'change':>8}  modification  [the study's own reported cost]")
    for r in t["rows"]:
        print(f"  {'$' + format(r['cost'], '.2f'):>10}  {r['cost'] - t['base']:>+8.2f}  {r['label']}  [{r['own']}]")
    print(f"\n  {'$' + format(t['all'], '.2f'):>10}  all together (where two set the same lever, the later in the list is used)")
    print(f"  {'$' + format(t['lower'], '.2f'):>10}  every modification that lowers the cost alone, together")
    print(f"  {'$' + format(t['higher'], '.2f'):>10}  every modification that raises the cost alone, together")
    print("\n  Assumptions the levers cannot represent, or that break a limit of the model:")
    for m in modifications():
        if m.get("not_representable"):
            print(f"    {m['label']}\n      {m['reason']}")
    c = comparison()
    print(f"\n  Each study's most favourable estimate against the all-favourable case (${c['all_favourable']:.2f}):")
    for r in c["rows"]:
        if r["today"] is None:
            print(f"    {r['name']:<16} not compared: {r['not_compared']}")
        else:
            print(f"    {r['name']:<16} {r['published']}  ->  ${r['per_kg_cells']:.2f} a kilo of wet cells in {r['year']} dollars, "
                  f"${r['today']:.2f} today{'   BELOW' if r['below'] else ''}")
    for b in c["below"]:
        print(f"\n  {b['name']} is below." + ("" if b["inside"] is None else
              f" Inside the limits its design costs ${b['inside']:.2f} a kilo here ({b['inside_density']:.0f} g/L)."))
        for a in b["assumptions"]:
            print(f"    {a['assumption']} ({a['ref']}): {a['value']:g} against {a['limit_value']:g} {a['unit']}; {a['limit_name']}")


if __name__ == "__main__":
    main()
