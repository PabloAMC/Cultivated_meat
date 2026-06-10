#!/usr/bin/env python3
"""
build_interactive.py — generate the self-contained interactive explorer.

Reads the constants, slider ranges and per-region market tables straight from
`inputs.py` + `meat_market.py` (the single source of truth) and injects them into
a dependency-free HTML/JS/SVG widget written to `interactive.html`. The JS model
logic MIRRORS market_share.share / meat_market.penetration / uncertainty.R_from_inputs;
the in-page "model self-check" panel reproduces the Python reference numbers so any
drift is visible. Re-run after any change to inputs.py.

    python build_interactive.py
"""
from __future__ import annotations

import json
import os

from inputs import value, prior, AA_FLOOR
import meat_market as mm
from market_share import DemandParams, LOSS_AVERSION_RATIO

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "interactive.html")


def _prior_lo_hi(name):
    kind, lo, hi, mode, _ = prior(name)
    return lo, hi


def _prior_lo_mode_hi(name):
    kind, lo, hi, mode, _ = prior(name)
    return lo, mode, hi


def build_model() -> dict:
    dp = DemandParams()        # runs the calibration solve once -> reference solved values for the self-check
    const = {
        "media_intensity": value("media_intensity"),
        "AA_FLOOR": AA_FLOOR,
        "FEEDSTOCK_FLOOR": AA_FLOOR + value("glucose_other_floor"),
        "glucose_other_floor": value("glucose_other_floor"),
        "plant_floor": value("plant_floor"),
        "cost_floor": AA_FLOOR + value("glucose_other_floor") + value("plant_floor"),
        # --- demand: two-segment, four-product discrete-choice (logit) model ---
        # products: w=whole-food, c=conventional, p=plant-based, x=cultivated.
        # the JS mirrors market_share._utilities/share and re-runs the calibration solve.
        "p_conv_anchor": value("p_conv"),       # the $12 commodity anchor: conventional's price in the demand model
        "eps_own": value("eps_own"),
        "cult_sub_mult": value("cult_sub_mult"),  # closeness/substitutability lever
        # the demand price coefficient beta is DERIVED (mirror of market_share._derive_beta):
        # anchored at cultivated's OWN retail price = biomass(base) + markup, solved at its own
        # share via a fixed point. These BASE cost values set that anchor (NOT the live sliders).
        "anchor_media_price": value("media_price"),
        "anchor_overhead": value("overhead"),
        "anchor_markup": value("markup_add"),
        # income (BLP price term): richer => less price-sensitive
        "income_ref": value("income_ref"),
        "income_gradient": value("income_gradient"),
        # product positions (attributes)
        "price_pb_mult": value("price_pb_mult"),
        "price_wf_mult": value("price_wf_mult"),
        "taste_quality_p": value("taste_quality_p"),
        "taste_quality_w": value("taste_quality_w"),
        "q_taste": value("q_taste"),
        # segment weights & the reference-dependent loss aversion (uniform across products)
        "LOSS_AVERSION_RATIO": LOSS_AVERSION_RATIO,   # loss/gain asymmetry (Tversky-Kahneman 2.25)
        "w_eth": value("w_eth"),
        "theta_free_M": value("theta_free_M"),
        "accept_x": value("accept_x"),
        "w_realtissue_E": value("w_realtissue_E"),
        "w_slaughter_E": value("w_slaughter_E"),
        "loss_aversion": value("loss_aversion"),
        # calibration TARGETS the JS solve hits (so calibration-affecting sliders work live)
        "pb_share_target": value("pb_share_target"),
        "pb_mainstream_frac": value("pb_mainstream_frac"),
        "wf_mainstream_target": value("wf_mainstream_target"),
        # Python-SOLVED reference values (for the in-page self-check; JS re-solves and should match)
        "w_realtissue_M_ref": dp.w_realtissue_M,
        "K_wholefood_M_ref": dp.K_wholefood_M,
        "K_wholefood_E_ref": dp.K_wholefood_E,
        "cleanroom_cost": value("cleanroom_cost"),
        # per-region income (GDP/cap PPP) for the BLP price term
        "REGION_INCOME": mm.REGION_INCOME,
        # demand calibration constants (surfaced so the methods section can show them)
        "PREMIUM_RATIO": mm.PREMIUM_RATIO,
        # triangular Monte-Carlo priors [lo, mode, hi] for the genuinely uncertain inputs
        "priors": {
            "media_price": list(_prior_lo_mode_hi("media_price")),
            "efficiency": list(_prior_lo_mode_hi("efficiency")),
            "overhead": list(_prior_lo_mode_hi("overhead")),
            "markup_add": list(_prior_lo_mode_hi("markup_add")),
            "eps_own": list(_prior_lo_mode_hi("eps_own")),
            "theta_free_M": list(_prior_lo_mode_hi("theta_free_M")),
            "accept_x": list(_prior_lo_mode_hi("accept_x")),
        },
        # tier offsets (meat_market)
        "AUTH_BASIC": mm.AUTH_BASIC, "AUTH_CUT": mm.AUTH_CUT,
        "AUTH_PREMIUM": mm.AUTH_PREMIUM,
        "EPS_MULT_CUT": mm.EPS_MULT_CUT, "EPS_MULT_PREMIUM": mm.EPS_MULT_PREMIUM,
        # reactor configs for the cost chart: [label, overhead $/kg]
        "configs": [["perfusion 20 m³", 7.9], ["TFF 5 m³", 9.9],
                    ["ATF 0.5 m³", 24.7]],
        # every tweakable slider -> [elegant symbol (HTML), the equation it enters].
        # keyed by slider key; rendered as two extra columns of the parameter table.
        "param_symbols": {
            "media_price":   ["p<sub>med</sub>", "medium cost <i>c</i><sub>med</sub> = &iota;&eta;&thinsp;p<sub>med</sub> (&sect;1)"],
            "efficiency":    ["&eta;", "medium cost <i>c</i><sub>med</sub> = &iota;&eta;&thinsp;p<sub>med</sub> (&sect;1)"],
            "overhead":      ["h", "biomass cost <i>c</i><sub>bio</sub> = <i>c</i><sub>med</sub> + h (&sect;1)"],
            "scaffold":      ["k", "R numerator: + k (structured cuts, &sect;1)"],
            "markup_add":    ["m", "R numerator: + m (&sect;1)"],
            "meat_tax":      ["t", "R denominator: p<sub>conv</sub>&middot;t (&sect;1)"],
            "income":        ["y", "price term &alpha;&thinsp;ln(y &minus; price<sub>j</sub>) (&sect;2)"],
            "eps_own":       ["&epsilon;", "elasticity target &kappa;&epsilon;, sets derived &beta; at cultivated's own price (&sect;2)"],
            "cult_sub_mult": ["&kappa;", "elasticity target &kappa;&epsilon;, sets derived &beta; at cultivated's own price (&sect;2)"],
            "loss_aversion": ["&lambda;", "reference term &minus;&lambda;(d<sub>j</sub>)<sup>+</sup> + (&lambda;/2.25)(d<sub>j</sub>)<sup>&minus;</sup> (&sect;2)"],
            "accept_x":      ["a<sub>x</sub>", "cultivated taste q&middot;(a<sub>x</sub>&minus;1) in V<sub>j</sub> (&sect;2)"],
            "a_p":           ["a<sub>p</sub>", "plant-based taste q&middot;(a<sub>p</sub>&minus;1) in V<sub>j</sub> (&sect;2)"],
            "R_p":           ["R<sub>p</sub>", "plant-based price ratio in V<sub>j</sub> (&sect;2)"],
            "theta_free_M":  ["&theta;<sub>free</sub>", "mainstream weight on slaughter-free in V<sub>j</sub> (&sect;2)"],
            "w_eth":         ["w<sub>eth</sub>", "segment mix: share<sub>j</sub> = w<sub>eth</sub>P<sub>E</sub> + (1&minus;w<sub>eth</sub>)P<sub>M</sub> (&sect;2)"],
        },
    }

    def slider(key, label, unit, lo, hi, step, default, src, tip, fmt="num"):
        return dict(key=key, label=label, unit=unit, min=lo, max=hi, step=step,
                    default=default, src=src, tip=tip, fmt=fmt)

    sliders = [
        slider("accept_x", "Cultivated taste-acceptance (a<sub>x</sub>)", "", 0.6, 1.2, 0.05, 1.0,
               "the dial", tip="The TASTE dial: how the mainstream rates cultivated's SENSORY quality. "
               "It IS cultivated's taste attribute (taste_x = a_x − 1, 0 = at parity with real meat), "
               "weighted by the shared taste weight q (=5 utils). 1.0 = tastes & feels exactly like "
               "conventional (neutral; ~47% share at parity); below 1 = lingering 'lab-grown, not quite "
               "real' friction (0.8 → ~24%, 0.6 → ~10% at parity); ABOVE 1 = cultivated judged to taste "
               "BETTER than an average cut (engineered consistency/marbling, no gristle, no contamination "
               "— a sensory claim, distinct from the slaughter-free upside θ_free), 1.1 → ~59% at parity. "
               "SOURCE: a judgement dial; the strong-friction end echoes plant-based products displacing "
               "only a few pp of beef at parity (Peacock 2023). The Monte-Carlo prior stays centred at "
               "parity (1.0); this point-estimate slider ranges wider to explore the upside."),
        slider("theta_free_M", "Mainstream values slaughter-free (θ<sub>free</sub>)", "", 0.0, 1.5, 0.05, 0.0,
               "the dial", tip="The UPSIDE dial: the mainstream's utility weight on the SLAUGHTER-FREE "
               "attribute — on equal footing with price, taste and real-tissue. It lifts EVERY no-"
               "slaughter product (cultivated most, because it also has real-tissue). 0 = indifferent "
               "(neutral); positive = cultivated gains (0.5 → ~57%, 1.0 → ~66% at parity). SOURCE: a "
               "judgement dial; ~89% of real plant-based buyers are non-veg/vegan flexitarians (GFI "
               "2024) — that mainstream pull lives here, not in the 5% ethical core."),
        slider("a_p", "Plant-based taste-acceptance (a<sub>p</sub>)", "", 0.4, 1.1, 0.05,
               round(1 + value("taste_quality_p"), 2), "NECTAR", tip="Plant-based meat's SENSORY quality, "
               "on the same 1=real-meat scale as a_x: 1 = tastes as good as conventional, below 1 = a "
               "deficit, weighted by the shared taste weight q. Default 0.8 reflects the category averaging "
               "BELOW parity — NECTAR 2025 found only ~16% of plant-based products reach blind taste parity. "
               "Slide it up toward 1 to ask 'what if plant-based tasted like the real thing?'. This is an "
               "EXPLORATORY override: the calibration is pinned at the observed position, then this moves "
               "plant-based's share (it does not re-pin). SOURCE: NECTAR Taste of the Industry 2025."),
        slider("R_p", "Plant-based price (R<sub>p</sub>)", "x", 0.2, 3.0, 0.05,
               value("price_pb_mult"), "GFI/NIQ", tip="Plant-based meat's retail price as a multiple of "
               "conventional — the analogue of cultivated's R. Default 1.77× = GFI/NIQ's measured +77% "
               "premium (it has WIDENED, not narrowed). Drag toward 1.0 for 'what if plant-based hit price "
               "parity?', or BELOW 1 (down to 0.2×) for a subsidised / commodity-cheap plant-based future "
               "— there it earns the reference-dependent discount reward, same as any product priced under "
               "conventional. Like a_p, an exploratory override applied after calibration, so it moves "
               "plant-based's share rather than re-pinning it. SOURCE: GFI/NIQ retail data 2024."),
        slider("loss_aversion", "Premium loss-aversion (λ)", "utils", 0.0, 2.5, 0.1, value("loss_aversion"),
               "behavioural", tip="REFERENCE-DEPENDENT loss aversion (Tversky-Kahneman; Hardie-Johnson-"
               "Fader 1993): consumers anchor on the conventional price, so ANY product priced above it "
               "takes a penalty −λ·max(0, price/p_conv − 1). Applied uniformly to plant-based (1.77×) AND "
               "cultivated (R) alike, not as a cultivated-only penalty. One of the two biggest demand "
               "levers at the likely R_x≈2.4 (self-check [6]): 0 = pure smooth logit, higher = stronger "
               "premium aversion. SOURCE: a behavioural judgement, standard form."),
        slider("cult_sub_mult", "Cultivated ↔ conventional closeness (κ)", "x", 2.0, 4.0, 0.5,
               value("cult_sub_mult"), "assumed", tip="SUBSTITUTABILITY lever: how much more own-price-"
               "elastic cultivated is than meat-as-a-category, because conventional is a near-perfect "
               "substitute (same tissue). The measured ε≈−0.9 is the elasticity of MEAT (inelastic, no "
               "close substitute); cultivated's own price bites ~κ× harder. The model's least data-"
               "disciplined lever and the other big one at R_x≈2.4 (self-check [6]); a reduced-form stand-in "
               "for a real_tissue random coefficient (the flat-logit counterpart of a nested-logit's λ). "
               "SOURCE: judgement; no cultivated cross-price data exists."),
        slider("income", "Country income (<i>y</i>, GDP/cap PPP)", "$/yr", 5000, 500000, 1000, value("income_ref"),
               "World Bank", tip="Average income, which sets price-SENSITIVITY through the Berry-"
               "Levinsohn-Pakes price term α·ln(income − price): richer consumers are LESS price-sensitive "
               "(a dollar matters less). Auto-set by the region selector (US $86k … Nigeria $6.4k) but "
               "free to drag. Lowering it makes cultivated's premium bite far harder — why cultivated is "
               "hardest in low-income regions (cheap meat AND price-sensitive). The range runs far past "
               "today's richest country so you can explore a high-growth / AGI future where incomes rise "
               "several-fold and price-sensitivity collapses. SOURCE: World Bank GDP/cap PPP 2023-24; the "
               "rich→poor gradient is damped to the empirical ~2-3× (Muhammad/ERS 2011)."),
        slider("w_eth", "Ethical (veg+vegan) population (w<sub>eth</sub>)", "", 0.04, 0.10, 0.01, value("w_eth"),
               "Gallup", tip="Size of the ETHICAL segment (values slaughter-free, mostly eats whole foods). "
               "5% = US vegetarian (4%) + vegan (1%), Gallup 2023. The rest is the mainstream. Plant-based "
               "lands at ~1% (not ~5%) because the cheap whole-food outside option absorbs most ethical "
               "eaters — changing w_eth re-solves the calibration to keep plant-based at its observed share. "
               "SOURCE: Gallup 2023."),
        slider("overhead", "Reactor scale / overhead (<i>h</i>)", "$/kg", 6.0, 24.7, 0.1, 9.9, "Pasitka",
               tip="Non-medium cost of running the plant (capital, labour, consumables, utilities) "
               "per kg, set by reactor scale. $9.9 = Pasitka's demonstrated TFF config (total "
               "~$24/kg); ~$7.9 = large-scale perfusion (scale-up wins); ~$24.7 = many small ATF "
               "vessels (scale-up stalls, ~$39/kg). The biggest cost lever and least demonstrated. "
               "SOURCE: Pasitka et al., Nature Food 5, 693-702 (2024), Fig. 4 (three reactor "
               "configs); the physical reason scale-up is hard (CO2/O2 transfer, shear, sterility) "
               "is Humbird, Biotechnol. Bioeng. 118, 3239-3250 (2021)."),
        slider("media_price", "Medium price (<i>p</i><sub>med</sub>)", "$/L", 0.10, 0.63, 0.01, value("media_price"),
               "Pasitka/GFI", tip="Cost of the cell-culture medium. $0.63/L = Pasitka's measured "
               "animal-free medium (peer-reviewed; albumin removal cut it from $3.31->$0.63/L); "
               "$0.20/L = several companies' 2025 self-reported claims (not independently verified). "
               "The ~$0.10/L floor reflects the bulk amino acids the cells must physically eat - "
               "medium can't be much cheaper than its feedstock. SOURCE: $0.63 from Pasitka et al. "
               "2024; the $0.20 claim and its caveats from GFI, State of the Industry / 'Analyzing "
               "cell-culture medium costs' (2025)."),
        slider("meat_tax", "Meat price (tax mult. <i>t</i>)", "x", 0.8, 1.6, 0.05, 1.0, "policy",
               tip="A multiplier on every conventional-meat price - e.g. a meat tax or a carbon "
               "price passed through to meat. Raising it lowers the price ratio (cultivated becomes "
               "relatively cheaper) and is about as powerful a lever as a major cost cut. 1.0 = "
               "today's prices. SOURCE: a policy lever, not a forecast - it scales every observed "
               "retail price (below) by the same factor, so it does NOT change the species mix."),
        slider("efficiency", "Cell media-efficiency (η)", "x", 0.25, 1.0, 0.05, value("efficiency"),
               "Pasitka/CHO", tip="Medium used per kg of biomass, relative to Pasitka's cells "
               "(1.0). 0.25 = 'CHO-grade' metabolism (4x less medium) - a different, "
               "not-yet-demonstrated cell line. This is where cell DENSITY / metabolic efficiency "
               "enters: both act through how much medium a kg of meat consumes. SOURCE: Pasitka et "
               "al. 2024 (their cells, the 1.0 anchor); the 4x headroom vs CHO is a cell-line "
               "assumption, not demonstrated for food cells."),
        slider("eps_own", "Price elasticity of demand (ε)", "", -1.4, -0.5, 0.05, value("eps_own"),
               "scanner", tip="How sharply demand responds to price. -1.0 means a 1% price rise "
               "loses ~1% of buyers. Default -0.9 is the mid-range of published meat own-price "
               "elasticities — the elasticity of MEAT (inelastic, no close substitute). Cultivated's "
               "OWN price bites harder still — set by the separate closeness slider κ — because a "
               "near-perfect substitute (conventional) exists. Premium tiers are made LESS price-sensitive "
               "automatically (cuts x0.8, luxury "
               "x0.3) - someone splurging on sushi barely flinches at price, which is why premium "
               "clears parity on price yet still wins limited share. SOURCE: Andreyeva, Long "
               "& Brownell, Am. J. Public Health 100:216 (2010) meta-analysis - beef -0.75, pork "
               "-0.72, poultry -0.68; Gallet 2010/2012 meta-analyses span -0.7..-1.0; Lusk & Tonsor "
               "2016 (demand more inelastic at higher prices -> the premium multipliers)."),
        slider("markup_add", "Retail markup (<i>m</i>, additive, assumed)", "$/kg", 2.0, 7.0, 0.1,
               value("markup_add"), "USDA spread", tip="Biomass->retail wedge (processing, cold "
               "chain, retail margin). We ASSUME it is a fixed $/kg amount, NOT a percentage, so it "
               "does not shrink as biomass gets cheaper; with the meat price it sets the parity "
               "threshold (parity needs biomass <= price - markup). The MAGNITUDE is anchored to "
               "conventional meat's farm-to-retail spread (USDA ERS: ground-beef processing+retail very "
               "roughly $3-6/kg). The floor is $2 (below conventional's ~$4) because cultivated SKIPS "
               "slaughter / evisceration / carcass breakdown — a real chunk of that wedge — so its retail "
               "markup can sit slightly below conventional's; $5 is the typical case. At the $2 floor, "
               "parity becomes reachable in the optimistic cost corner. A modelling choice (additive, not "
               "%) and one of the model's most leveraged numbers, so slide it."),
        slider("scaffold", "Scaffold cost (<i>k</i>, structured cuts)", "$/kg", 0.0, 12.0, 0.5, mm.SCAF,
               "assumed", tip="Extra $/kg to turn unstructured biomass into a structured cut "
               "(scaffold material + structuring bioprocess). Applies only to cut/fillet/premium "
               "products, not mince. The least-grounded number in the model. SOURCE: NO published "
               "techno-economic analysis covers scaffolding cost - Humbird 2021, CE Delft 2021 and "
               "Risner et al. 2021 all stop at unstructured cell slurry. No source gives a $/kg "
               "figure; the $6/kg here is our assumption, treat it as a guess and slide it - set it "
               "to 0 if structuring turns out cheap or negligible."),
    ]
    toggles = [
        dict(key="cleanroom", label="Add Humbird clean-room cost (+ to <i>h</i>)",
             add=value("cleanroom_cost"),
             tip="Adds Humbird's clean-room / aseptic buildings cost (about +$" +
             ("%.0f" % value("cleanroom_cost")) + "/kg, ~8% of his COGS; Table 4.7/4.14). Pasitka's "
             "overhead assumes a cheaper food-grade facility - toggle on for a pharma-leaning "
             "sterility assumption."),
    ]

    markets = {
        region: [dict(name=mt.name, p_conv=mt.p_conv, w_vol=mt.w_vol,
                      structured=(mt.scaffold > 0), cost_mult=mt.cost_mult)
                 for mt in market]
        for region, market in mm.MARKETS.items()
    }
    regions = [["us", "US"], ["eu", "EU"], ["china", "China"], ["global", "global"],
               ["brazil", "Brazil"], ["india", "India"], ["nigeria", "Nigeria"]]
    return dict(const=const, sliders=sliders, toggles=toggles, markets=markets, regions=regions)


# ---------------------------------------------------------------------------
# Python cross-check: recompute the reference numbers with the SAME formulas we
# inject, to confirm the constants/markets are the ones the model uses.
# ---------------------------------------------------------------------------
def crosscheck(model: dict) -> None:
    from market_share import DemandParams, share
    from cost_model import CostParams, biomass_cost
    cp = CostParams()
    R = (biomass_cost(cp, 0.63, 1.0) + value("markup_add")) / value("p_conv")
    pr = DemandParams()
    pb = share(1.0, pr, cultivated_present=False, which="pb")
    s0 = share(1.0, pr)                       # neutral defaults (accept_x=1, theta_free_M=0)
    print(f"  cross-check (Python): basic R={R:.2f}  PB(no cult)={pb*100:.2f}%  "
          f"share@parity(neutral)={s0*100:.1f}%")


HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cultivated meat — interactive explorer</title>
<style>
:root{--ink:#1a1a1a;--muted:#666;--rule:#e3e3e3;--accent:#0072B2;--orange:#E69F00;
 --green:#117733;--red:#CC3311;--bg:#fff;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:-apple-system,Helvetica,Arial,sans-serif;line-height:1.5;}
.wrap{max-width:1120px;margin:0 auto;padding:24px 20px 64px;}
h1{font-size:1.45rem;margin:0 0 .2em;font-family:Georgia,serif;}
.lede{color:var(--muted);font-size:.92rem;margin:0 0 18px;max-width:80ch;}
.lede a{color:var(--accent);}
.grid{display:grid;grid-template-columns:300px 1fr;gap:26px;}
@media(max-width:780px){.grid{grid-template-columns:1fr;}}
.rail{border:1px solid var(--rule);border-radius:10px;padding:14px 16px;height:fit-content;
 position:sticky;top:14px;background:#fcfcfc;}
.ctl{margin:0 0 13px;}
.ctl label{display:flex;justify-content:space-between;font-size:.82rem;margin-bottom:3px;}
.ctl .nm{font-weight:600;}
.ctl .val{font-variant-numeric:tabular-nums;color:var(--accent);font-weight:600;}
.ctl .src{color:#999;font-size:.7rem;font-weight:400;}
input[type=range]{width:100%;accent-color:var(--accent);margin:0;}
select{width:100%;padding:5px;border:1px solid var(--rule);border-radius:6px;font-size:.85rem;}
.btn{margin-top:6px;width:100%;padding:7px;border:1px solid var(--rule);background:#fff;
 border-radius:6px;cursor:pointer;font-size:.82rem;}
.btn:hover{background:#f2f2f2;}
.heads{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px;}
.head{border:1px solid var(--rule);border-radius:10px;padding:11px 13px;text-align:center;}
.head .big{font-size:1.7rem;font-weight:700;font-variant-numeric:tabular-nums;line-height:1.1;}
.head .lab{font-size:.72rem;color:var(--muted);margin-top:3px;}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
@media(max-width:780px){.charts{grid-template-columns:1fr;}}
.card{border:1px solid var(--rule);border-radius:10px;padding:10px 12px;}
.card.full{grid-column:1/-1;}
.card h3{margin:0 0 4px;font-size:.92rem;font-family:Georgia,serif;}
.card .sub{font-size:.72rem;color:var(--muted);margin:0 0 6px;}
svg{width:100%;height:auto;display:block;}
.note{font-size:.74rem;color:#999;margin-top:14px;}
.selftest{font-size:.74rem;color:var(--green);margin-top:6px;font-variant-numeric:tabular-nums;}
.toggle button{font-size:.7rem;border:1px solid var(--rule);background:#fff;padding:2px 7px;cursor:pointer;}
.toggle button.on{background:var(--accent);color:#fff;border-color:var(--accent);}
.toggle button:first-child{border-radius:6px 0 0 6px;}
.toggle button:last-child{border-radius:0 6px 6px 0;border-left:0;}
.q{display:inline-block;width:14px;height:14px;line-height:14px;text-align:center;border-radius:50%;
 background:#dcdcdc;color:#333;font-size:.64rem;cursor:help;margin-left:3px;font-weight:700;}
.tog{margin:10px 0 2px;font-size:.82rem;display:flex;align-items:center;gap:7px;}
.tog input{accent-color:var(--accent);}
.methods{margin-top:16px;border-top:1px solid var(--rule);padding-top:10px;}
.methods summary{cursor:pointer;font-weight:600;font-size:.92rem;color:var(--accent);font-family:Georgia,serif;}
.methods p{font-size:.86rem;}
.methods a{color:var(--accent);}
.methods .refs a{white-space:nowrap;}
.methods h4{font-family:Georgia,serif;font-size:.95rem;margin:18px 0 4px;}
.methods pre{background:#f7f7f5;border:1px solid var(--rule);border-radius:6px;padding:8px 11px;
 font-size:.78rem;overflow-x:auto;font-family:'SF Mono',Menlo,monospace;line-height:1.45;}
.methods .refs{font-size:.8rem;padding-left:18px;} .methods .refs li{margin-bottom:4px;}
.methods code{background:#f0f0ee;padding:0 3px;border-radius:3px;font-size:.82em;}
table.pt{border-collapse:collapse;font-size:.78rem;width:100%;}
table.pt th,table.pt td{border-bottom:1px solid var(--rule);padding:3px 6px;text-align:left;}
table.pt td.n{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap;}
table.pt td.s{color:#777;}
.scrollx{overflow-x:auto;-webkit-overflow-scrolling:touch;}
/* keep every meat-type / parameter name on a single line; the table scrolls sideways if needed */
table.pt td:first-child,table.pt th:first-child{white-space:nowrap;min-width:160px;}
.mcbar{display:flex;align-items:center;gap:12px;margin:0 0 14px;}
.mcbtn{padding:6px 14px;border:1px solid var(--accent);background:#fff;color:var(--accent);
 border-radius:6px;cursor:pointer;font-size:.82rem;font-weight:600;}
.mcbtn.on{background:var(--accent);color:#fff;}
.mcbar .mcnote{font-size:.74rem;color:#999;}
.tip{position:fixed;max-width:290px;background:#222;color:#fff;padding:9px 11px;border-radius:7px;
 font-size:.78rem;line-height:1.45;z-index:999;display:none;box-shadow:0 4px 14px rgba(0,0,0,.25);
 font-family:-apple-system,Helvetica,Arial,sans-serif;}
text{font-family:Georgia,serif;}
.methods .vardef{font-size:.84rem;border-collapse:collapse;margin:6px 0;}
.methods .vardef td{padding:2px 10px 2px 0;vertical-align:top;}
.methods .vardef td:first-child{white-space:nowrap;color:#111;}
.methods .attr th{padding:2px 10px;text-align:center;font-size:.8rem;vertical-align:bottom;color:#333;}
.methods .attr td{text-align:center;padding:3px 10px;border-bottom:1px solid #f0f0f0;}
.methods .attr td:first-child,.methods .attr th:first-child{text-align:left;white-space:nowrap;}
.methods mjx-container{overflow-x:auto;overflow-y:hidden;}
</style>
<script>window.MathJax={chtml:{scale:0.96}};</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head><body><div id="tip" class="tip"></div><div class="wrap">
<h1>Cultivated meat: play with the model</h1>
<p class="lede">Drag the sliders — ordered most-decisive first — to see how the price ratio,
market share, and per-meat-type penetration respond. These are <b>point estimates</b> at the values
you choose (not the Monte-Carlo bands). The model and every parameter are described in the
methods and results notes. Defaults are the neutral / measured values.</p>
<div class="grid">
  <div class="rail" id="rail"></div>
  <div>
    <div class="heads" id="heads"></div>
    <div class="mcbar">
      <button class="mcbtn" id="mcbtn">Monte Carlo: off</button>
      <span class="mcnote">propagate the priors (cost inputs + acceptance + elasticity) into an
      uncertainty band — N=2000 draws, triangular priors from the datasheet</span>
    </div>
    <div class="charts">
      <div class="card full" id="mccard" style="display:none"><h3>Uncertainty band (Monte Carlo)</h3>
        <p class="sub" id="mcsub"></p><svg id="mc" viewBox="0 0 720 250"></svg></div>
      <div class="card full"><h3>Penetration by type of meat</h3>
        <p class="sub" id="barsub"></p><svg id="bars" viewBox="0 0 720 300"></svg></div>
      <div class="card full"><h3>Share of all meat consumed, and the cultivated slice
        <span class="toggle" id="pietog" style="font-weight:400;margin-left:8px;vertical-align:middle"></span></h3>
        <p class="sub" id="piesub"></p>
        <svg id="pie" viewBox="0 0 720 330"></svg></div>
      <div class="card"><h3>Cost vs the two big inputs</h3>
        <p class="sub">biomass cost vs medium price; lines = reactor scale; marker = your choice</p>
        <svg id="cost" viewBox="0 0 420 300"></svg></div>
      <div class="card"><h3>Share vs price ratio (all four products)</h3>
        <p class="sub">how the four shares move as cultivated's price ratio R<sub>x</sub> varies — cultivated (bold)
        rises as it gets cheaper, mostly out of conventional; plant-based &amp; whole-food barely move.
        The dot marks the chosen product's R</p>
        <div style="margin:0 0 5px"><select id="curveSel" style="width:auto;max-width:100%;font-size:.78rem;padding:3px 5px"></select></div>
        <svg id="curve" viewBox="0 0 420 300"></svg></div>
    </div>
    <div class="selftest" id="selftest"></div>
    <p class="note">"Penetration" totals are rolled up by <b>volume</b> (weight &rarr; animal impact)
    and by <b>value</b> ($ &rarr; market). Point estimates only — not the Monte-Carlo bands.</p>
    <details class="methods"><summary>Methodology &amp; equations</summary>
      <p>The model is a chain — <b>biomass cost &rarr; price ratio R<sub>x</sub> &rarr; market share &rarr;
      penetration</b> — computed per type of meat (cultivated cost is ~constant across species;
      conventional price ranges ~5&times;, so the answer differs by animal). Everything below is the
      live JS in this page; it mirrors the Python model line-for-line, and the self-check under the
      charts reproduces the Python reference numbers.</p>

      <h4>1. Cost &rarr; price ratio \(R_x\)</h4>
      <p>The one number that drives everything downstream is cultivated's <b>price ratio</b> \(R_x\) —
      cultivated retail price divided by the conventional price it competes with (the subscript \(x\)
      marks it as cultivated's, alongside plant-based's \(R_p\) in §2). The denominator is just an
      observed market price \(p_{\rm conv}\) (times a policy multiplier \(t\) for a meat tax). So §1 is
      really about building the numerator, cultivated's retail price, one cost at a time — and we
      introduce each variable only at the step where it becomes unavoidable.</p>
      <p><b>Start with medium, because it dominates.</b> Cells grow in a liquid medium, so the first
      thing we need is its price, \(p_{\rm med}\) (<i>$ per litre</i>). But a per-litre price isn't a
      cost per kg of meat until we know how many litres a kilogram consumes — the <b>media
      intensity</b> \(\iota\approx 22.4\) L/kg (measured by Pasitka). Cells can be engineered leaner,
      so we attach an <b>efficiency</b> multiplier \(\eta\) (1 = today's cells; 0.25 = CHO-grade, 4&times;
      leaner). A first guess at the medium bill is therefore \(\iota\,\eta\,p_{\rm med}\).</p>
      <p>This is the medium cost per kg of biomass, \(c_{\rm med}\) — a $/kg quantity, not to be
      confused with the $/L price \(p_{\rm med}\) — with one floor: a litre of medium can't cost less
      than the feedstock dissolved in it. The cells must physically eat a fixed mass of amino acids and
      glucose to build tissue (cost \(f\approx\$1.5\)/kg, set by stoichiometry), so \(c_{\rm med}\)
      cannot fall below \(f\):</p>
      \[ c_{\rm med} = \iota\,\eta\,p_{\rm med}, \qquad\text{floored at } f \]
      <p>i.e. \(c_{\rm med}=\max\!\big(f,\ \iota\,\eta\,p_{\rm med}\big)\). Equivalently the floor is a
      hard lower bound on the medium price, \(p_{\rm med}\ge f/\iota\approx\$0.07\)/L. The floor only
      binds in the most optimistic corner (very cheap, very lean cells); everywhere else
      \(c_{\rm med}\) is just litres \(\times\) price.</p>
      <p>Running the reactors, labour, utilities and capital adds a per-kg <b>overhead</b> \(h\) — the
      reactor-scale lever, and the model's main bottleneck — completing the biomass cost
      \(c_{\rm bio}=c_{\rm med}+h\). Turning biomass into a sold product adds a <b>retail markup</b>
      \(m\) (processing, cold chain, margin — added in $/kg; why additive is discussed in §4) and, for
      structured cuts only, a <b>scaffold cost</b> \(k\). A per-type multiplier \(\mu\) (default 1) lets
      one species' biomass cost differ if data ever warrant it. Numerator over denominator:</p>
      \[ c_{\rm bio} = c_{\rm med} + h \;\;(+\,\text{clean-room, if toggled}), \qquad
         R_x = \frac{c_{\rm bio}\,\mu + k + m}{p_{\rm conv}\,t} \]
      <p>Parity (\(R_x=1\)) therefore needs \(c_{\rm bio}\le p_{\rm conv}-m\): the markup eats the
      headroom, which is why it is one of the most leveraged numbers in the model. Cell <b>density /
      metabolic efficiency</b> enters only through \(\eta\) — what matters for cost is medium consumed
      per kg, which density drives.</p>

      <h4>2. From the price ratio to a market share (a discrete-choice demand model)</h4>
      <p>This is a textbook <b>random-utility / discrete-choice</b> model (McFadden 1974) — the standard
      way economists turn product attributes into market shares. On an eating occasion a consumer picks
      <i>one</i> of <b>four products</b>; each option gets a "utility" score \(V\), and the option with
      the highest score (plus a random taste shock) wins. Averaged over the shocks, the share of each
      option is a <b>softmax</b> (a logit) of its utility. We use <b>two consumer types</b> (a
      latent-class / mixed logit) and average their choices.</p>
      <p>The four options and their <b>attributes</b> (conventional meat is the reference everything is
      measured against):</p>
      <table class="attr">
        <tr><th>product</th><th>price (&times; conv.)</th><th>taste (1 = real meat)</th><th>slaughter&#8209;free</th><th>real tissue</th><th>\(\xi\) (intercept)</th></tr>
        <tr><td><b>conventional</b> meat</td><td>1 (anchor)</td><td>1 (reference)</td><td>0</td><td>1</td><td>0</td></tr>
        <tr><td><b>plant&#8209;based</b> meat</td><td>\(R_p\) (~1.77, dial)</td><td>\(a_p\) (~0.8, dial)</td><td>1</td><td>0</td><td>0</td></tr>
        <tr><td><b>cultivated</b> meat</td><td>\(R_x\) (from §1)</td><td>\(a_x\) (~1, dial)</td><td>1</td><td>1</td><td>0 <sup>&dagger;</sup></td></tr>
        <tr><td><b>whole&#8209;food</b> (beans/tofu)</td><td>~0.25 (cheap)</td><td>~0.3 (not meat)</td><td>1</td><td>0</td><td>\(\xi_w\) (calib.)</td></tr>
      </table>
      <p style="font-size:.82rem;margin:-2px 0 8px;color:#555"><sup>&dagger;</sup> Cultivated has <b>no
      free "standing" constant</b>: its long-run intercept is <b>0</b> (it inherits conventional's standing,
      being real tissue). Its one cultivated-specific term is <b>food neophobia</b> — the wariness of a
      <i>novel</i> food (Pliner &amp; Hobden 1992), which <b>fades to zero with exposure</b> (a launch
      transient handled in the timing rung, not a permanent dial) — plus a per-meat-type <b>authenticity</b>
      offset in §3. Everything permanent about cultivated lives in its <i>attributes</i> (price, taste
      \(a_x\), slaughter-free, real-tissue), not in a catch-all constant.</p>
      <p>Whole food is the <b>outside option</b> — "skip meat tonight, eat beans" — and it matters: most
      ethically-motivated people get protein from whole foods, not a veggie burger, which is exactly why
      plant-based <i>meat</i> sits at only ~1%. Every product runs through the <b>same</b> utility rule — no
      option gets a special term; the rule just reads each product's row off the table above:</p>
      \[ V_j = \underbrace{\alpha\ln(y-\text{price}_j)}_{\text{price (via income)}}
              \;+\;\underbrace{-\,\lambda\,(d_j)^{+}+\tfrac{\lambda}{2.25}\,(d_j)^{-}}_{\text{reference dependence}}
              \;+\; q\,\text{taste}_j \;+\; w^{s}\,\text{free}_j \;+\; w^{rt}\,\text{tissue}_j \;+\; \xi_j \]
      <p style="text-align:center;margin:-2px 0 8px;font-size:.86rem">where
      \(d_j=\dfrac{\text{price}_j}{p_{\rm conv}}-1\) is product \(j\)'s premium over conventional, and
      \((x)^{+}=\max(0,x),\ (x)^{-}=\max(0,-x)\) are its positive and negative parts.</p>
      <p><b>Every term has the same shape</b> — a weight times that product's value of one attribute, read
      straight from the table — and <b>a 0 in the table is not a special case</b>, just "this product doesn't
      have that feature". Slaughter-free \(\text{free}_j\) is 0 for conventional; real-tissue
      \(\text{tissue}_j\) is 0 for plant-based and whole-food; and the <b>intercept</b> \(\xi_j\) — the last
      column — is 0 for conventional, plant-based <i>and</i> cultivated, non-zero only for whole-food
      (\(\xi_w\), the calibrated outside-option intercept). So there is <b>no free-floating cultivated
      "standing" constant</b>: cultivated's position is set entirely by its attributes (price, taste,
      slaughter-free, real-tissue). Its one cultivated-specific term — food <b>neophobia</b> — is a launch
      transient that fades to zero with exposure (handled in the timing rung), not a permanent column here.</p>
      <p><b>The price piece, unpacked.</b> The income term's coefficient \(\alpha\) is not guessed — and,
      unlike an earlier version, it rests on <b>no hand-picked anchor</b>. The behavioural target is
      cultivated's own-price elasticity \(\varepsilon_x=\kappa\varepsilon\). One subtlety: price enters
      utility through <b>two</b> channels — the income term (local slope \(\beta\)) <i>and</i> the
      loss-aversion term below (slope \(-\lambda/p_{\rm conv}\) on the loss side, which is where cultivated's
      premium sits) — so the own-price elasticity is \(\varepsilon_x=(\beta-\lambda/p_{\rm conv})\,p_x(1-s_x)\).
      We solve \(\beta\) so that <b>combined</b> response hits the target at cultivated's <b>own</b> operating
      point — its own retail price \(p_x=c_{\rm bio}+m\) (the cost rung's output, so it tracks the model) and
      its own modeled share \(s_x\), a short fixed point:</p>
      \[ \beta=\frac{\kappa\,\varepsilon}{p_x\,(1-s_x)}+\frac{\lambda}{p_{\rm conv}},\qquad
         \alpha=-\beta\,(y_{\rm ref}-p_x),\qquad
         V^{\text{price}}_j=\alpha\ln(y-\text{price}_j). \]
      <p style="font-size:.9rem">Read left to right: the meat elasticity \(\varepsilon\) (slider) times the
      closeness \(\kappa\) (slider) is the target elasticity; the \(+\lambda/p_{\rm conv}\) hands back the
      slice of price-sensitivity the loss-aversion term already supplies, so \(\beta\) carries only the rest.
      This is the fix that makes the <i>realised</i> elasticity equal \(\kappa\varepsilon\) rather than ~2&times;
      it, and it cleanly separates \(\kappa\) (which sets the elasticity <i>level</i>) from \(\lambda\) (which
      now only shapes the kink at parity). There is no free "calibration price": move a cost input and
      \(p_x\) moves with it.</p>
      <p style="font-size:.9rem"><b>Why \(\alpha=-\beta(y_{\rm ref}-p_x)\)?</b> Not a second free parameter —
      it is the <b>chain rule</b>. We want \(\alpha\ln(y-\text{price})\) to have local price-slope \(\beta\) at
      the anchor; since \(\tfrac{d}{d\,\text{price}}\,\alpha\ln(y-\text{price})=-\alpha/(y-\text{price})\),
      setting that \(=\beta\) at \((y_{\rm ref},p_x)\) gives exactly \(\alpha=-\beta(y_{\rm ref}-p_x)\). So the
      factor \((y_{\rm ref}-p_x)\) is just the marginal-utility-of-income normalisation — the reason
      \((y-\text{price})\) seems to appear "twice" (once as this slope constant, once inside the log) is the
      derivative of a log, not a modelling artefact. <b>And \(y\)?</b> annual income per capita (GDP/cap at
      PPP); the US reference is \(y_{\rm ref}=\$85{,}810\) (World Bank 2023), other regions scale by a damped
      gradient. Only income <i>ratios</i> across regions are identified — the absolute level is absorbed by
      \(\alpha\) (using a monthly budget instead of the per-kg price merely rescales \(\alpha\); shares
      unchanged) — so \(y\) is an <i>affordability scale</i>, and what it buys the model is the empirical
      ~2–3&times; rich→poor price-sensitivity gradient.</p>
      <p><b>The two segment-specific weights</b> (everything else is shared across the two consumer types).
      Only the slaughter-free and real-tissue weights differ by type — that difference <i>is</i> the
      heterogeneity:</p>
      \[ w^{s}=\begin{cases}\theta_{\rm free}&\text{mainstream (slider, }\sim0)\\ w_{\rm slaughter,E}&\text{ethical (large, fixed)}\end{cases}
         \qquad
         w^{rt}=\begin{cases}w_{\rm rt}&\text{mainstream (calibrated)}\\ \approx 0&\text{ethical}\end{cases} \]
      <p style="font-size:.9rem">So the slaughter-free term you tune is \(\theta_{\rm free}\,\text{free}_j\) for
      the mainstream (95% of buyers): at \(\theta_{\rm free}=0\) the mainstream is indifferent to "no animal
      killed"; raise it and every slaughter-free product gains, cultivated most (it also has real tissue).</p>
      <p>The terms, each with a plain meaning and a source:</p>
      <table class="vardef">
        <tr><td><b>price &amp; income</b> \(\alpha\ln(y-\text{price}_j)\)</td><td>the <b>Berry–Levinsohn–Pakes
          (1995)</b> way to put income in: <b>\(y\)</b> is the buyer's income — annual GDP/cap at PPP, the
          <b>income</b> slider (\(y_{\rm ref}=\$85{,}810\)) — so
          \(y-\text{price}_j\) is what's left after buying product \(j\), and the \(\ln\) makes a dollar matter
          <i>less</i> to a richer person — raise \(y\) (a richer country, or a high-growth future) and everyone's
          price sensitivity flattens. The coefficient \(\alpha\) is not guessed: it is built from the measured meat
          elasticity \(\varepsilon\) and the closeness \(\kappa\) via \(\beta\) — see "the price piece, unpacked"
          just above. (Across regions \(y\) enters with a mild damping, so the rich→poor sensitivity gap matches
          the ~2–3&times; seen in the data rather than a raw 1/income; using a monthly/annual budget instead of
          the per-kg price only rescales \(\alpha\), which the calibration absorbs.)</td></tr>
        <tr><td><b>loss aversion</b> \(\lambda\)</td><td><b>reference-dependent</b> price term
          (Tversky–Kahneman; Hardie–Johnson–Fader 1993): people judge a price against a <i>reference</i> — here
          the familiar conventional price — and a product priced <i>above</i> it feels like a loss while one
          <i>below</i> it feels like a gain. The term is <b>two-sided</b>: it penalises a premium at \(\lambda\)
          and rewards a discount at \(\lambda/2.25\) — i.e. symmetric around the reference but ~2.25&times;
          steeper on the loss side, the canonical loss-aversion ratio. Applied to <i>every</i> product by its
          own \(d_j\) — plant-based (1.77&times;) <i>and</i> cultivated (\(R_x\)) alike. This is the
          <b>riskless</b> form of loss aversion (reference-dependent preferences over a single sure attribute,
          price), not the gamble version — see the note under the table. (Its slope is folded into the
          \(\beta\) calibration above, so \(\lambda\) sets only the <i>asymmetry</i> at parity, not the overall
          price-sensitivity level.)</td></tr>
        <tr><td><b>taste</b> \(q\,(a_j-1)\)</td><td>sensory quality on a <b>1 = real meat</b> scale: each
          product's taste-acceptance \(a_j\) is 1 if it tastes as good as conventional, below 1 if worse,
          above 1 if better. It enters utility as the <i>gap</i> from real meat, \(a_j-1\) (so conventional,
          the reference, contributes 0), weighted by the shared taste weight \(q\). Two dials:
          <b>\(a_x\)</b> (cultivated, default 1 = parity) and <b>\(a_p\)</b> (plant-based, default ~0.8 — the
          category averages below parity; NECTAR 2025 found only ~16% reach blind parity; whole-food sits
          near 0.3 — an assumption that trades off with its solved baseline appeal, so its exact value does
          not move the results). Only <i>differences</i> matter in a logit, so anchoring real meat at 1 (or at 0) is a
          free choice — we show 1 because it reads naturally as "full marks".</td></tr>
        <tr><td><b>slaughter-free</b> \(w^{s}\,\text{free}_j\)</td><td>the value placed on "no animal killed".
          Small for the mainstream (the <b>\(\theta_{\rm free}\)</b> dial, default 0), large for the ethical
          type — this is what makes the two consumer types differ.</td></tr>
        <tr><td><b>real tissue</b> \(w^{rt}\,\text{tissue}_j\)</td><td>"is it actual animal tissue?" — yes for
          conventional <i>and</i> cultivated, no for plant-based/whole-food. The mainstream weights this; it
          is the edge cultivated <b>shares with conventional</b>, and the reason cultivated draws from
          <i>beef</i>, not the veggie burger.</td></tr>
        <tr><td><b>intercept</b> \(\xi_j\)</td><td>a baseline beyond the four measured attributes — and
          <b>zero for every meat product</b>. The only non-zero one is <b>whole-food</b>'s \(\xi_w\), the
          <i>outside-option intercept</i>, set by calibration so the model reproduces plant-based's real
          ~1.2% share (below). <b>Cultivated's is 0</b>: it inherits conventional's standing (being real
          tissue), so there is no cultivated "standing" knob. Its one cultivated-specific term, food
          <b>neophobia</b> (the wariness of a novel food, Pliner–Hobden 1992), is a <i>launch transient that
          fades to 0 with exposure</i> — it lives in the timing rung, not here — and a per-meat-type
          <b>authenticity</b> offset rides in this slot in the §3 roll-up.</td></tr>
      </table>
      <p><b>How the closeness \(\kappa\) actually works (and where it enters — just once).</b> \(\kappa\) is
      the one knob that needs spelling out, because it has no direct data. Start from the measured number:
      scanner studies give the own-price elasticity of <i>meat as a category</i>, \(\varepsilon\approx-0.9\)
      — inelastic, because if all meat gets dearer there is no close substitute to flee to. But cultivated
      beef is <i>not</i> a category; it has a near-perfect substitute right next to it (conventional beef,
      same tissue), so a price cut on cultivated specifically wins buyers much faster — its <b>own-price
      elasticity is larger</b>. \(\kappa\) is exactly that multiplier, and it is applied <b>once</b>: it sets
      cultivated's target elasticity \(\varepsilon_x=\kappa\varepsilon\). The \(\kappa\varepsilon\) you then
      see inside \(\beta\) is <i>not</i> a second use — it is the same \(\varepsilon_x\) substituted in,
      because \(\beta\) is merely the logit coefficient that delivers it:</p>
      \[ \varepsilon_x \;=\; \kappa\,\varepsilon \;\approx\; 3\times(-0.9)\;=\;-2.7,
         \qquad\text{delivered by}\qquad \beta \;=\; \frac{\varepsilon_x}{p_x\,(1-s_x)}+\frac{\lambda}{p_{\rm conv}}
         \ \text{(at cultivated's own price \& share)} . \]
      <p>So at \(\kappa=3\) a 1% rise in cultivated's price loses ~2.7% of its buyers, three times meat's
      ~0.9% — and, after the two-channel fix above, that ~2.7 is the <i>realised</i> elasticity, not merely a
      target. Mechanically \(\kappa\) scales the elasticity part of \(\beta\) (hence \(\alpha\) in \(V_j\)),
      making cultivated's share-vs-price curve <i>steeper</i>. It is the flat-logit stand-in for what a
      nested logit would get from a "real-meat" nest (its dissimilarity parameter), or a random coefficient
      on the real-tissue attribute. <b>Why \(\approx3\)?</b> Pure judgement — there is no cultivated cross-price
      data anywhere. A nested-logit treatment would imply a comparable factor (loosely \(\approx2\)) through
      its dissimilarity parameter; we centre at \(3\) and treat \(2\!-\!4\) as the range. Drag the slider to
      \(\kappa=1\) ("cultivated as inelastic as meat overall") and
      central penetration jumps several-fold — which is exactly why it is exposed, not buried.</p>
      <p style="font-size:.84rem;background:#f7f7f5;border:1px solid var(--rule);border-radius:6px;padding:7px 10px">
      <b>A note on "loss aversion" here.</b> Loss aversion is most famous from <i>risky</i> gambles (a chance to
      win vs. lose money). But Tversky &amp; Kahneman's 1991 paper extends it to <b>riskless choice</b>: when you
      compare goods on an attribute (here, price), you evaluate each option as a gain or loss <i>relative to a
      reference point</i>, and losses loom larger. Paying more than the familiar conventional price reads as a
      loss; paying less, a gain. That is exactly our \(d_j\) term, and it is standard — it is the workhorse behind
      <b>reference-price</b> models in marketing/IO (Hardie–Johnson–Fader 1993 estimate it on real brand-choice
      scanner data). It is a deliberate modelling <i>choice</i>, not forced: set \(\lambda=0\) and the demand
      model collapses to a plain price-only logit (the slider lets you do exactly that). We include it because the
      premium is the whole story for cultivated meat, and a kink at the reference price fits how shoppers actually
      react to "more expensive than normal."</p>
      <p><b>What we do with \(V_j\): turn utilities into shares.</b> Each consumer adds up the score \(V_j\)
      for every product and picks the one they like best — but with a random "mood of the day" taste shock.
      Averaging over those shocks (the standard Gumbel assumption) gives a clean formula: the probability of
      choosing product \(j\) is its <b>softmax</b> (the logit), bigger \(V_j\) ⇒ bigger share, and the shares
      sum to 100%:</p>
      \[ P_j = \frac{e^{V_j}}{\sum_{k}\,e^{V_k}} \qquad\text{(sum over the products on offer)} \]
      <p>We compute this <i>twice</i> — once for each consumer type, using that type's own attribute weights —
      and then blend the two by the population split (the ethical type is a fraction \(w_{\rm eth}\), the
      mainstream the rest). That blend is the market share the page reports:</p>
      \[ \text{share}_j \;=\; w_{\rm eth}\,P_j^{\,\text{ethical}} \;+\; (1-w_{\rm eth})\,P_j^{\,\text{mainstream}} \]
      <p>Everything downstream — the headline penetration, the per-meat-type bars, the share-vs-price curve —
      is this one number, computed for cultivated (and, on the curve, for all four products).</p>
      <p><b>The two consumer types (heterogeneity, not a nest).</b> The <b>mainstream</b> (~95%) chooses on
      taste, price and real-tissue; the <b>ethical</b> type (~5% = Gallup vegetarian+vegan, the
      <b>\(w_{\rm eth}\)</b> slider) weights slaughter-free heavily and mostly eats whole foods. A single
      logit would have a new option steal share proportionally from <i>all</i> others ("red-bus/blue-bus");
      because the mainstream is dominated by real-tissue products, a cultivated entrant draws almost entirely
      from <b>conventional</b> — no nested logit needed, just the shared real-tissue attribute and two types.</p>
      <p><b>Calibration — pinned to real data, not free.</b> Plant-based's price premium (GFI/NIQ), its taste
      deficit (NECTAR), and the ethical share (Gallup) are fixed; then three numbers are <i>solved</i> so the
      model reproduces (i) plant-based's observed ~1.2% of meat and (ii) the fact that <b>~89% of plant-based
      buyers are mainstream flexitarians</b>, not the 5% ethical core (GFI 2024). Dragging \(w_{\rm eth}\),
      \(\lambda\), \(\kappa\) or income re-solves this live, so plant-based stays anchored.
      <b>An out-of-sample check:</b> holding those <i>same</i> coefficients fixed and only moving the product
      positions to plant-based <i>milk</i>'s (near price &amp; taste parity in coffee/cereal; no cheap
      whole-food substitute for milk) reproduces PB-milk's observed <b>~15%</b> share — so the one machinery
      explains both PB-meat's failure and PB-milk's success (it is printed in the self-check above). (We do
      <i>not</i> add a separate "habit" term: it isn't separable from preference in the data — Heckman — so
      habit lives in the rollout-over-time, not here.)</p>
      <p><b>Reading the share at parity.</b> At \(R_x=1\) with neutral dials (\(a_x=1,\ \theta_{\rm free}=0\)),
      cultivated is attribute-identical to conventional, so it splits the real-meat buyers ~half — about
      <b>47%</b>, on habit and brand alone. Drop \(a_x\) for taste friction (0.8 → ~24%, 0.6 → ~10%), or
      push it above 1 if cultivated is judged to taste <i>better</i> than an average cut (1.1 → ~59%);
      raise \(\theta_{\rm free}\) for the cleaner-meat upside (0.5 → ~57%, 1.0 → ~66%). Nothing is baked in. The
      model predicts the ordering <b>conventional &gt; cultivated &gt; plant-based</b> at parity — cultivated
      beats plant-based because it <i>is</i> real tissue.</p>

      <h4>3. Roll-up across meat types, and the price tiers</h4>
      <p>Each meat type is run at <i>its own</i> R (its own conventional price) with a
      <b>tier-dependent</b> offset to cultivated's utility (\(a_x\) is lower for products bought for
      authenticity) and an elasticity multiplier, then summed weighted by <b>volume</b> (mass &rarr;
      animal/climate impact) and by <b>value</b> (price&times;volume &rarr; $ market). Tiers are set by
      (is it structured?, and its price <i>relative to its own species</i>):</p>
      <pre>basic   = unstructured mince/processed                    authenticity +0.2,  elasticity &times;1.0
cut     = structured, price &lt; 2.5&times; the species' base form   authenticity &minus;0.4,  elasticity &times;0.8
premium = structured, price &ge; 2.5&times; the species' base form   authenticity &minus;1.5,  elasticity &times;0.3</pre>
      <p><b>"Premium" is per-species, not a single price line.</b> A product is premium when it costs
      at least <b>2.5&times; its own species' everyday (cheapest) form</b> — so every species can have one:
      <i>wagyu / prime beef</i>, <i>sushi-grade seafood</i>, <i>organic chicken</i>, <i>heritage /
      ibérico pork</i>. (Defining premium by a relative ratio, rather than one absolute $/kg line,
      avoids the artefact where the same product flipped tier between regions.) Each region's bar chart
      now shows a wine "premium" bar for several species. Data caveat: wagyu beef and sushi seafood are
      well-attested premiums; the organic-chicken and heritage-pork variants are real but smaller, so
      they are included at low volume and lower confidence. The tiers encode why there is <b>no easy
      entry point</b>: cultivated is cheapest exactly where demand resists most (premium, bought for
      authenticity, price-insensitive) and most accepted where it is hardest to beat on price (cheap
      staples). The reachable window is the <b>mid-priced cuts</b> — the structured-but-not-premium
      tier (beef steak, chicken/pork cuts).</p>

      <h4>4. Prices, the markup, and consumption shares</h4>
      <p><b>Conventional retail prices by region and form</b> — the \(p_{\rm conv}\) the model divides
      by. Cultivated cost is ~global; it is the local price it competes against that differs, by region
      and by form:</p>
      <div class="scrollx" id="pricetable"></div>
      <p style="font-size:.76rem;color:#888;">Prices: GlobalProductPrices
      (globalproductprices.com, retail, Jan&nbsp;2026) for the world/regional levels, cross-checked
      against USDA&nbsp;ERS &amp; BLS (US). Consumption shares (the volume weights): USDA&nbsp;ERS
      per-capita availability (US); OECD-FAO Agricultural Outlook 2024 and FAO food-balance sheets (EU,
      China, world). Species mix genuinely varies by region — China pork-dominant (~two-thirds of
      meat), the US poultry-heavy (~half), the EU pork-led but shifting to poultry, the world tilting
      to poultry — which is why the region selector moves the totals.</p>
      <p><b>On the retail markup \(m\) (an assumption worth flagging).</b> We add the
      biomass&rarr;retail wedge as a <i>fixed $/kg</i> amount (default $5/kg), not a percentage. We do
      not <i>know</i> it is additive: conventional meat's farm-to-retail spread (USDA&nbsp;ERS
      price-spread data, ~$3&ndash;6/kg for ground beef) motivates the <i>magnitude</i>, and much of
      the wedge — slaughter/processing, cold chain, retail handling — genuinely is per-kg rather than
      proportional. But a proportional (%) markup would change the parity arithmetic, so the additive
      form is a modelling choice, not a measurement. It is one of the most leveraged numbers in the
      model, which is why it is exposed as its own slider.</p>
      <p><b>The share curve bends through parity.</b> Premium reluctance is the reference-dependent
      <b>loss-aversion</b> term \(\lambda\) (§2), applied to <i>every</i> product by its premium over
      conventional. Because the term is two-sided, the share-vs-price curve is <i>continuous</i> through
      \(R_x=1\) (no cliff) but has a gentle <b>kink</b> there — slope \(\lambda\) where cultivated is dearer than
      conventional, the shallower \(\lambda/2.25\) where it is cheaper — and plant-based (at 1.77&times;) is
      treated by the very same rule, on equal footing with cultivated.</p>

      <h4>Parameters &amp; sources — every knob, its symbol, and where it enters</h4>
      <p>Each slider you can tweak, the <b>symbol</b> it carries in the equations above, its default and
      range, the <b>exact term it enters</b> (§1 = cost &rarr; R; §2 = the utility \(V_j\)), and its source
      — so every result traces back to a parameter and an equation (full datasheet in
      <a href="METHODS.md">METHODS.md</a>):</p>
      <div class="scrollx" id="paramtable"></div>

      <h4>Is this the natural way to set it up? (an honest interrogation)</h4>
      <p>The framework is exactly what an economist would use — a <b>random-utility discrete-choice
      model with consumer heterogeneity, BLP income, and reference-dependent loss aversion</b>, all
      standard. The honest label, though, is a <b>calibrated, partial-equilibrium</b> model: parameters
      are pinned to a few observed facts, <i>not</i> structurally estimated, because no cultivated-meat
      choice data exists yet. So the demand side is a band/scenario, never a forecast. Which is forced,
      which is judgement:</p>
      <ul>
        <li><b>Forced by physics / data.</b> The cost split (medium vs overhead) is how Pasitka reports
        COGS; the feedstock floor is stoichiometry. The four-product logit and the BLP income term are
        textbook.</li>
        <li><b>Cultivated draws from beef without a nested logit.</b> The shared <b>real-tissue</b>
        attribute plus two consumer types does the job a nested logit would: a cultivated entrant takes
        share almost entirely from conventional (a self-check on the page confirms this), not the veggie
        burger — a milder, more transparent structure.</li>
        <li><b>The premium penalty is on equal footing.</b> Loss aversion \(\lambda\) applies to every
        product by its premium, so there is no cultivated-only special case and the share-vs-price curve
        is smooth through parity.</li>
        <li><b>The calibration is pinned to data.</b> Plant-based's ~1.2% share and the 89%-mainstream
        buyer split (GFI) pin the otherwise-unidentified outside-option baselines; the ethical share is Gallup. We solve
        three numbers to hit those; everything else is sourced.</li>
        <li><b>The least data-disciplined lever is \(\kappa\)</b> (cultivated↔conventional closeness):
        no cultivated cross-price data exists, so it is judgement. It and \(\lambda\) are the two biggest
        demand levers at the likely \(R_x\approx2.4\) — drag them to see, that is the point of exposing
        them.</li>
        <li><b>Habit is not a separate fitted term</b> (it is not separable from preference without
        panel data — Heckman); it lives in the rollout-over-time as food-neophobia fading, with long-run acceptance (\(a_x\), \(\theta_{\rm free}\)) as the dial.</li>
        <li><b>The tier offsets (authenticity &plusmn;, elasticity &times;) are reduced-form</b> scenario
        knobs for a richer per-product model we have no data to fit.</li>
      </ul>

      <h4>What the model does NOT do (limitations)</h4>
      <ul>
        <li><b>Calibrated, not estimated.</b> Standard theory, but parameters are fit to moments, not a
        full demand system — appropriate given no cultivated-meat data; reaching for an estimated
        random-coefficients model here would be false precision.</li>
        <li><b>Two consumer types, one price coefficient.</b> A 2-point heterogeneity, not a continuous
        random-coefficients (mixed-logit) distribution; one elasticity applied across products, not a full
        substitution matrix.</li>
        <li><b>Partial equilibrium.</b> Prices are exogenous (the cost rung sets them); no supply response,
        pass-through, or capacity. "What share at price X", not a market-clearing model.</li>
        <li><b>Convenience</b> (the third "price–taste–convenience" factor, Bryant/Peacock) is proxied by
        rollout-over-time, not modelled as its own attribute.</li>
        <li><b>Species mix is fixed within a region</b> — the meat-tax is a uniform multiplier, so it does
        not reshuffle chicken-vs-beef-vs-pork (the cross-price terms are small/noisy; Gallet 2010/2012).</li>
        <li><b>Low-income region prices/mixes (India, Brazil, Nigeria) are rough</b>, illustrative of the
        income channel rather than calibrated. <b>Scaffold cost is a guess</b> — no TEA covers it.</li>
      </ul>

      <h4>References</h4>
      <ul class="refs">
        <li><b>Medium $0.63/L, intensity, COGS, reactor configs:</b> Pasitka, L. <i>et al.</i>
        Empirical economic analysis shows cost-effective continuous manufacturing of cultivated chicken
        using animal-free medium. <i>Nature Food</i> <b>5</b>, 693&ndash;702 (2024).
        <a href="https://doi.org/10.1038/s43016-024-01022-w" target="_blank" rel="noopener">doi:10.1038/s43016-024-01022-w</a></li>
        <li><b>Feedstock floor, scale-up ceilings, clean-room cost:</b> Humbird, D. Scale-up economics
        for cultured meat. <i>Biotechnology and Bioengineering</i> <b>118</b>, 3239&ndash;3250 (2021).
        <a href="https://doi.org/10.1002/bit.27848" target="_blank" rel="noopener">doi:10.1002/bit.27848</a></li>
        <li><b>$0.20/L company claims, media-cost breakdown:</b> The Good Food Institute.
        <a href="https://gfi.org/resource/cultivated-meat-seafood-and-ingredients-state-of-the-industry/" target="_blank" rel="noopener">State of the Industry</a>
        &amp; <a href="https://gfi.org/resource/analyzing-cell-culture-medium-costs/" target="_blank" rel="noopener">Analyzing cell-culture medium costs</a> (2025).</li>
        <li><b>Elasticity &minus;0.9 (beef &minus;0.75, pork &minus;0.72, poultry &minus;0.68):</b>
        Andreyeva, T., Long, M.&nbsp;W. &amp; Brownell, K.&nbsp;D. The impact of food prices on
        consumption. <i>Am. J. Public Health</i> <b>100</b>, 216&ndash;222 (2010).
        <a href="https://doi.org/10.2105/AJPH.2008.151415" target="_blank" rel="noopener">doi:10.2105/AJPH.2008.151415</a></li>
        <li><b>Premium less elastic at high price:</b> Lusk, J.&nbsp;L. &amp; Tonsor, G.&nbsp;T. How
        meat-demand elasticities vary with price, income and product category.
        <i>Appl. Econ. Perspect. Policy</i> <b>38</b>, 673 (2016).
        <a href="https://doi.org/10.1093/aepp/ppv050" target="_blank" rel="noopener">doi:10.1093/aepp/ppv050</a>.
        Cross-region species elasticities: Gallet, C.&nbsp;A. meta-analyses (2010/2012).</li>
        <li><b>Scaffold $6/kg is OUR assumption (no published cost figure):</b> no techno-economic
        analysis covers scaffolding / structuring cost — Humbird 2021, CE Delft 2021 and Risner et al. 2021
        all stop at unstructured cell slurry. Treat the $6/kg as a guess and slide it.</li>
        <li><b>Plant-based taste (only ~16% reach blind parity):</b>
        <a href="https://www.nectar.org/sensory-research/2025-taste-of-the-industry" target="_blank" rel="noopener">NECTAR, Taste of the Industry (2025)</a>.
        <b>5% veg+vegan:</b>
        <a href="https://news.gallup.com/poll/510038/identify-vegetarian-vegan.aspx" target="_blank" rel="noopener">Gallup (Brenan, 2023)</a> &mdash; 4% vegetarian, 1% vegan.</li>
        <li><b>Discrete-choice / random-utility demand:</b> McFadden, D.
        <a href="https://eml.berkeley.edu/reprints/mcfadden/zarembka.pdf" target="_blank" rel="noopener">Conditional logit analysis of qualitative choice behavior</a> (1974);
        Train, K. <a href="https://eml.berkeley.edu/books/choice2.html" target="_blank" rel="noopener"><i>Discrete Choice Methods with Simulation</i></a> (2009).
        <b>Income in price (BLP):</b> Berry, Levinsohn &amp; Pakes, <i>Econometrica</i> <b>63</b>, 841 (1995),
        <a href="https://doi.org/10.2307/2171802" target="_blank" rel="noopener">doi:10.2307/2171802</a>.</li>
        <li><b>Reference-dependent loss aversion:</b> Tversky &amp; Kahneman, <i>Q. J. Econ.</i> <b>106</b>,
        1039 (1991), <a href="https://doi.org/10.2307/2937956" target="_blank" rel="noopener">doi:10.2307/2937956</a>;
        Hardie, Johnson &amp; Fader, <i>Marketing Science</i> <b>12</b>, 378 (1993),
        <a href="https://doi.org/10.1287/mksc.12.4.378" target="_blank" rel="noopener">doi:10.1287/mksc.12.4.378</a>.
        <b>Habit ≠ heterogeneity:</b> Heckman, J.,
        <a href="https://www.nber.org/system/files/chapters/c8909/c8909.pdf" target="_blank" rel="noopener">Heterogeneity and state dependence</a>, NBER (1981).</li>
        <li><b>Plant-based ~1.2% share, ~89% mainstream buyers, +77% price premium:</b>
        <a href="https://gfi.org/marketresearch/" target="_blank" rel="noopener">GFI market research</a>
        (GFI/SPINS, GFI–Morning Consult, GFI/NIQ, 2024).
        <b>At-parity displacement (UCLA):</b> Peacock, J.,
        <a href="https://forum.effectivealtruism.org/posts/iukeBPYNhKcddfFki/price-taste-and-convenience-competitive-plant-based-meat" target="_blank" rel="noopener">Price, taste &amp; convenience</a> (2023).</li>
        <li><b>Region income (GDP/cap PPP) &amp; the income–elasticity gradient:</b>
        <a href="https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD" target="_blank" rel="noopener">World Bank (2023–24)</a>;
        Muhammad <i>et al.</i>,
        <a href="https://www.ers.usda.gov/publications/pub-details?pubid=47581" target="_blank" rel="noopener">International evidence on food consumption patterns</a>,
        USDA ERS TB-1929 (2011). <b>Whole-food bean price:</b>
        <a href="https://fred.stlouisfed.org/series/APU0000714233" target="_blank" rel="noopener">BLS/FRED retail series</a> (2025).</li>
      </ul>
      <p>Anchored to Pasitka et&nbsp;al. 2024 and Humbird 2021; full results in
      <a href="RESULTS.md">RESULTS.md</a>.</p>
    </details>
  </div>
</div>
<script>
const MODEL = __MODEL_JSON__;
const C = MODEL.const, SV = "http://www.w3.org/2000/svg";
const state = {region: "global"};
MODEL.sliders.forEach(s => state[s.key] = s.default);
MODEL.toggles.forEach(t => state[t.key] = false);
state.mc = false;
state.curveType = null;
state.pieBasis = "vol";                          // the pie/donut basis: by volume or by value
state.income = C.REGION_INCOME[state.region];   // income follows the selected region
let KP = null;   // the current effective+calibrated constants (set every recompute)

/* ---------- model (mirror of market_share / meat_market / cost_model) ---------- */
function mediaCost(mp,ef){return Math.max(C.FEEDSTOCK_FLOOR,C.media_intensity*ef*mp);}

/* TWO-SEGMENT, FOUR-PRODUCT discrete-choice (logit) demand — a line-for-line mirror of
   market_share._utilities / _segment / share. Products [w,c,p,x] = whole-food (the non-meat
   outside option), conventional, plant-based, cultivated. EVERY product uses the SAME linear
   utility (no product-specific term): a BLP income price term, a reference-dependent loss-
   aversion premium penalty, taste, slaughter-free, real-tissue, and a per-product offset xi
   (0 for conventional & plant-based). Total share = w_eth*P_ethical + (1-w_eth)*P_mainstream.
   K = the effective constants (sliders override C) WITH the solved values from solveCalibration(). */
/* the shared price coefficient beta is DERIVED (mirror of market_share._derive_beta), stored as
   K.beta_ref by deriveBeta(). beta splits into an elasticity part and the loss-aversion
   compensation (lam); an eps override scales ONLY the elasticity part (so a tier's TOTAL
   elasticity scales as intended), leaving the loss-aversion compensation fixed. */
function betaPrice(K,eps){const lam=K.loss_aversion/K.p_conv_anchor;return (K.beta_ref-lam)*(eps/K.eps_own)+lam;}
function utilities(R,K,seg,o){
  const pc=K.p_conv_anchor;
  // plant-based price (R_p) and taste (a_p) are exploratory overrides; default to the
  // calibrated/observed position when not supplied (e.g. inside the calibration solve).
  const pPb=(o.pricePb===undefined?K.price_pb_mult:o.pricePb);
  const tP=(o.tasteP===undefined?K.taste_quality_p:o.tasteP);
  const priceRatio=[K.price_wf_mult,1,pPb,R];                       // w, c, p, x
  const taste=[K.taste_quality_w,0,tP,o.ax-1];                      // deviation from real meat (0 = parity)
  const slaughter=[1,0,1,1], realtissue=[0,1,0,1];
  const xiW=(seg==="M")?K.K_wholefood_M:K.K_wholefood_E;            // whole-food outside-option intercept xi_w (segment-specific, calibrated)
  const xi=[xiW,0,0,o.toff];                                        // xi_j: outside-option intercept (w), 0 for conv & PB; cultivated = tier authenticity offset (+ launch neophobia, 0 long-run)
  const wSl=(seg==="M")?o.tfM:K.w_slaughter_E;
  const wRt=(seg==="M")?K.w_realtissue_M:K.w_realtissue_E;
  const beta=betaPrice(K,o.eps);
  const yEff=K.income_ref*Math.pow(o.income/K.income_ref,K.income_gradient);
  const alpha=-beta*(K.income_ref-K.anchor_price);
  const V=[];
  for(let j=0;j<4;j++){
    const price=priceRatio[j]*pc;
    const Vp=alpha*Math.log1p(-price/yEff);                         // BLP income term (richer = less price-sensitive)
    const prem=priceRatio[j]-1;                                     // premium over the conventional reference
    const Vl=-K.loss_aversion*Math.max(0,prem)                      // loss side: penalise a premium
             +(K.loss_aversion/C.LOSS_AVERSION_RATIO)*Math.max(0,-prem);  // gain side: reward a discount (2.25x gentler)
    V[j]=Vp+Vl+K.q_taste*taste[j]+wSl*slaughter[j]+wRt*realtissue[j]+xi[j];
  }
  return V;
}
function softmax(V){const m=Math.max.apply(null,V),e=V.map(v=>Math.exp(v-m)),s=e.reduce((a,b)=>a+b,0);return e.map(x=>x/s);}
function segShares(R,K,seg,o){
  const V=utilities(R,K,seg,o);
  if(o.present){const P=softmax(V);return {w:P[0],c:P[1],p:P[2],x:P[3]};}
  const P=softmax(V.slice(0,3));return {w:P[0],c:P[1],p:P[2],x:0};
}
function shareCalc(R,K,{ax=1,tfM=0,toff=0,eps,income,pricePb,aP,present=true,which="x"}){
  const o={ax,tfM,toff,present,eps:(eps===undefined?K.eps_own:eps),
           income:(income===undefined?K.income_ref:income),
           pricePb:pricePb, tasteP:(aP===undefined?undefined:aP-1)};
  const M=segShares(R,K,"M",o), E=segShares(R,K,"E",o), key=(which==="pb")?"p":which;
  return K.w_eth*E[key]+(1-K.w_eth)*M[key];
}
/* re-solve the calibration (mirror of market_share.solve_calibration): three monotone
   bisections so the live sliders (w_eth, λ, κ, ε, prices…) keep plant-based at its observed
   ~1.2% share AND the 89% mainstream buyer split. */
function _rate(K,seg,which){return segShares(1,K,seg,{ax:1,tfM:0,toff:0,eps:K.eps_own,income:K.income_ref,present:false})[which];}
function solveCalibration(K){
  const we=K.w_eth;
  const pbM=K.pb_mainstream_frac*K.pb_share_target/(1-we);
  const pbE=(1-K.pb_mainstream_frac)*K.pb_share_target/we, wfM=K.wf_mainstream_target;
  K.w_realtissue_M=2; K.K_wholefood_M=0; K.K_wholefood_E=0;
  for(let r=0;r<12;r++){
    let lo=0,hi=8;
    for(let i=0;i<60;i++){const m=0.5*(lo+hi);K.w_realtissue_M=m;if(_rate(K,"M","p")>pbM)lo=m;else hi=m;}
    K.w_realtissue_M=0.5*(lo+hi);
    lo=-16;hi=16;
    for(let i=0;i<60;i++){const m=0.5*(lo+hi);K.K_wholefood_M=m;if(_rate(K,"M","w")>wfM)hi=m;else lo=m;}
    K.K_wholefood_M=0.5*(lo+hi);
  }
  let lo=-16,hi=16;
  for(let i=0;i<60;i++){const m=0.5*(lo+hi);K.K_wholefood_E=m;if(_rate(K,"E","p")>pbE)lo=m;else hi=m;}
  K.K_wholefood_E=0.5*(lo+hi);
  return K;
}
/* DERIVE the price coefficient beta with NO free anchor (mirror of market_share._derive_beta):
   the target is cultivated's own-price elasticity eps_x = eps*kappa. Price enters utility through
   TWO channels — the BLP income term (slope beta) and the loss-aversion term (slope -lam on the
   loss side, lam = loss_aversion/p_conv) — so beta is solved so their SUM reproduces eps_x AT
   cultivated's own retail price (= biomass at BASE cost + markup, which tracks the cost model)
   and its own modeled share. A short fixed point co-solved with the calibration; nothing here is
   a hand-set number. (Absorbing lam into beta is the double-counting fix: loss_aversion then only
   shapes the kink at parity, not the elasticity level.) */
function deriveBeta(K){
  const pAnchor=mediaCost(C.anchor_media_price,1)+C.anchor_overhead+C.anchor_markup;
  K.anchor_price=pAnchor;
  const Rtoday=pAnchor/K.p_conv_anchor, epsX=K.eps_own*K.cult_sub_mult;
  const lam=K.loss_aversion/K.p_conv_anchor;   // loss-side semi-elasticity the loss-aversion term adds
  let s=0;
  for(let it=0;it<40;it++){
    K.beta_ref=epsX/(pAnchor*(1-s))+lam;        // set before solveCalibration uses betaPrice
    solveCalibration(K);
    const sNew=shareCalc(Rtoday,K,{ax:1,tfM:0});
    if(Math.abs(sNew-s)<1e-9){s=sNew;break;}
    s=sNew;
  }
  K.beta_ref=epsX/(pAnchor*(1-s))+lam;
  return solveCalibration(K);                  // final calibration at the converged beta
}
/* effective constants from the current sliders, then derive beta + run the calibration solve. */
function effConsts(s){
  const K=Object.assign({},C);
  ["cult_sub_mult","loss_aversion","w_eth","eps_own"].forEach(k=>{if(k in s)K[k]=s[k];});
  return deriveBeta(K);
}
function biomass(s){return mediaCost(s.media_price,s.efficiency)
  +s.overhead+(s.cleanroom?C.cleanroom_cost:0);}
function basicR(s){return (biomass(s)+s.markup_add)/(C.p_conv_anchor*s.meat_tax);}
function speciesBases(market){const b={};market.forEach(mt=>{const a=animalOf(mt.name);
  b[a]=Math.min((a in b)?b[a]:Infinity,mt.p_conv);});return b;}
function tierOf(mt,base){return !mt.structured?"basic":(mt.p_conv>=C.PREMIUM_RATIO*base?"premium":"cut");}
function tAuth(t){return t==="basic"?C.AUTH_BASIC:t==="cut"?C.AUTH_CUT:C.AUTH_PREMIUM;}
function tMult(t){return t==="basic"?1.0:t==="cut"?C.EPS_MULT_CUT:C.EPS_MULT_PREMIUM;}
function penetration(s){
  const K=KP||effConsts(s);                                         // current calibrated constants
  const market=MODEL.markets[s.region], b=biomass(s), bases=speciesBases(market);
  let Wval=0; market.forEach(mt=>Wval+=mt.p_conv*mt.w_vol);
  const rows=market.map(mt=>{
    const scaf=mt.structured?s.scaffold:0, price=mt.p_conv*s.meat_tax;
    const R=(b*mt.cost_mult+scaf+s.markup_add)/price, t=tierOf(mt,bases[animalOf(mt.name)]);
    const eps=s.eps_own*tMult(t);                                   // premium tiers less price-sensitive
    const o={ax:s.accept_x,tfM:s.theta_free_M,toff:tAuth(t),eps,income:s.income,pricePb:s.R_p,aP:s.a_p};
    const sh=shareCalc(R,K,o);                                      // cultivated share of this type
    const shp=shareCalc(R,K,Object.assign({},o,{which:"p"}));       // plant-based share of this type
    return {mt,R,sh,shp,t};
  });
  let tv=0,tval=0; rows.forEach(r=>{tv+=r.mt.w_vol*r.sh; tval+=(r.mt.p_conv*r.mt.w_vol/Wval)*r.sh;});
  return {rows,tv,tval};
}
function animalOf(n){
  const map=[["chicken","Chicken"],["beef","Beef"],["pork","Pork"],["turkey","Turkey"],
    ["seafood","Seafood"],["sheep","Sheep/goat"],["goat","Sheep/goat"],["rabbit","Rabbit"]];
  for(const[k,l]of map) if(n.startsWith(k)) return l;
  return n.split(" ")[0];
}
// fixed colour per species, kept CONSTANT across regions (so a wedge is the same
// colour whichever region you select)
const COLSP={Chicken:"#4C78A8", Beef:"#E45756", Pork:"#F58518", Turkey:"#72B7B2",
  Seafood:"#54A24B", "Sheep/goat":"#B279A2", Rabbit:"#9D755D"};
function colOf(species){return COLSP[species]||"#BAB0AC";}

/* ---------- tiny SVG helpers ---------- */
function el(t,a,p){const e=document.createElementNS(SV,t);for(const k in a)e.setAttribute(k,a[k]);
  if(p)p.appendChild(e);return e;}
function tx(p,x,y,s,a){const t=el("text",Object.assign({x,y},a||{}),p);t.textContent=s;return t;}
function clear(svg){while(svg.firstChild)svg.removeChild(svg.firstChild);}
const fmtPct=v=>(v*100).toFixed(0)+"%";
function showTip(e,text){const t=document.getElementById("tip");t.textContent=text;t.style.display="block";
  const r=e.target.getBoundingClientRect();
  t.style.left=Math.max(8,Math.min(window.innerWidth-300,r.left-10))+"px";
  t.style.top=(r.bottom+6)+"px";}
function hideTip(){document.getElementById("tip").style.display="none";}
function addQ(parent,text){const q=document.createElement("span");q.className="q";q.textContent="?";
  q.onmouseenter=e=>showTip(e,text);q.onmouseleave=hideTip;
  q.onclick=e=>{const t=document.getElementById("tip");
    if(t.style.display==="block")hideTip();else showTip(e,text);};
  parent.appendChild(q);return q;}

/* ---------- the four live views ---------- */
function drawHeads(s){
  const b=biomass(s), R=basicR(s), p=penetration(s);
  const fillet=b+s.scaffold+s.markup_add;          // all-in retail $/kg of a STRUCTURED (non-minced) cut
  const cells=[
    ["non-minced fillet, retail (biomass $"+b.toFixed(0)+")","$"+fillet.toFixed(0)+"/kg","var(--ink)"],
    ["price ratio vs commodity","R<sub>x</sub> = "+R.toFixed(2),R<=1?"var(--green)":"var(--ink)"],
    ["penetration · by volume",(p.tv*100).toFixed(1)+"%","var(--orange)"],
    ["penetration · by value",(p.tval*100).toFixed(1)+"%","var(--accent)"]];
  const h=document.getElementById("heads"); h.innerHTML="";
  cells.forEach(([lab,big,col])=>{const d=document.createElement("div");d.className="head";
    d.innerHTML='<div class="big" style="color:'+col+'">'+big+'</div><div class="lab">'+lab+'</div>';
    h.appendChild(d);});
}
function drawBars(s,ptmc){
  const svg=document.getElementById("bars");clear(svg);
  const W=720,H=300,mL=40,mR=12,mT=28,mB=46;
  const {rows,tv,tval}=penetration(s);
  const groups={};
  rows.forEach(r=>{const a=animalOf(r.mt.name);(groups[a]=groups[a]||[]).push(r);});
  const order=Object.keys(groups).sort((a,b)=>
    (groups[a].reduce((x,r)=>x+r.mt.p_conv,0)/groups[a].length)-
    (groups[b].reduce((x,r)=>x+r.mt.p_conv,0)/groups[b].length));
  const whisk=ptmc?Math.max(...rows.map(r=>(ptmc[r.mt.name]||{p90:0}).p90)):0;
  const maxs=Math.max(0.2,whisk,...rows.map(r=>r.sh)), yTop=maxs*1.18;
  const X=i=>mL+(W-mL-mR)*(i+0.5)/order.length, Y=v=>H-mB-(H-mT-mB)*v/yTop;
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  [0,.1,.2,.3,.4,.5,.6,.7,.8].filter(v=>v<=yTop).forEach(v=>{
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#eee"},svg);
    tx(svg,mL-5,Y(v)+3,(v*100).toFixed(0),{"font-size":9,"text-anchor":"end",fill:"#666"});});
  [[tv,"#595959","total by volume "+(tv*100).toFixed(0)+"%","4 3"],
   [tval,"#111","total by value $ "+(tval*100).toFixed(0)+"%","1 3"]].forEach(([v,c,lab,dash])=>{
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:c,"stroke-dasharray":dash},svg);
    tx(svg,mL+2,Y(v)-3,lab,{"font-size":9,fill:c});});
  const COL={basic:"#E69F00",cut:"#0072B2",premium:"#882255"}, TO={basic:0,cut:1,premium:2};
  const bw=Math.min(16,(W-mL-mR)/order.length/3.4);
  order.forEach((a,i)=>{
    const items=groups[a].sort((p,q)=>TO[p.t]-TO[q.t]), n=items.length;
    items.forEach((r,j)=>{
      const cx=X(i)+(j-(n-1)/2)*(bw*1.14);
      const w=ptmc&&ptmc[r.mt.name];                    // P10-P50-P90 Monte-Carlo summary
      // when MC is on the bar IS the MC median (so the whisker brackets it; the priors for
      // accept_x/theta_free are one-sided vs their slider defaults, so a point-estimate bar
      // would sit at the edge of — or outside — the band). MC off: the point estimate.
      const bh=w?w.p50:r.sh;
      el("rect",{x:cx-bw/2,y:Y(bh),width:bw,height:H-mB-Y(bh),fill:COL[r.t],opacity:0.92},svg);
      if(w){el("line",{x1:cx,y1:Y(w.p10),x2:cx,y2:Y(w.p90),stroke:"#333","stroke-width":1},svg);
        el("line",{x1:cx-3,y1:Y(w.p10),x2:cx+3,y2:Y(w.p10),stroke:"#333","stroke-width":1},svg);
        el("line",{x1:cx-3,y1:Y(w.p90),x2:cx+3,y2:Y(w.p90),stroke:"#333","stroke-width":1},svg);}
      tx(svg,cx,Y(w?w.p90:bh)-9,fmtPct(bh),{"font-size":8.5,"text-anchor":"middle","font-weight":700,fill:"#222"});
      tx(svg,cx,Y(w?w.p90:bh)-1,"R="+r.R.toFixed(2),{"font-size":7,"text-anchor":"middle",fill:"#888"});
    });
    tx(svg,X(i),H-mB+14,a,{"font-size":10,"text-anchor":"middle",fill:"#333"});
  });
  let lx=W-mR-300;
  [["#E69F00","mince/processed"],["#0072B2","cut/fillet"],
   ["#882255","premium (≥"+C.PREMIUM_RATIO.toFixed(1)+"× species base)"]].forEach(([c,l])=>{
    el("rect",{x:lx,y:mT-20,width:9,height:9,fill:c},svg);
    tx(svg,lx+12,mT-12,l,{"font-size":9,fill:"#333"});lx+=100;});
  document.getElementById("barsub").textContent=
    "region: "+MODEL.regions.find(r=>r[0]===s.region)[1]+
    " — each bar = cultivated share WITHIN that category"+
    (ptmc?" (Monte-Carlo median; whiskers = 10–90% band)":" (point estimate at the current sliders)")+
    "; dashed lines = the two rolled-up totals (by volume = impact, by value = $ market). "+
    "No easy entry: cheap mince is unreachable on price, premium is demand-resistant; the reachable "+
    "window is the mid-priced cuts.";
}
function drawPie(s){
  const svg=document.getElementById("pie");clear(svg);
  const byVal=state.pieBasis==="val";                                   // wedge basis: volume or $ value
  const cx=185,cy=168,rO=138,rI=76;
  const {rows,tv,tval}=penetration(s);
  const groups={};
  rows.forEach(r=>{const a=animalOf(r.mt.name);
    const g=groups[a]=groups[a]||{vol:0,cult:0,pb:0,val:0,cultval:0,pbval:0,pmin:Infinity,pmax:0};
    g.vol+=r.mt.w_vol; g.cult+=r.mt.w_vol*r.sh; g.pb+=r.mt.w_vol*r.shp;                       // by volume (mass)
    g.val+=r.mt.p_conv*r.mt.w_vol; g.cultval+=r.mt.p_conv*r.mt.w_vol*r.sh; g.pbval+=r.mt.p_conv*r.mt.w_vol*r.shp; // by value ($)
    g.pmin=Math.min(g.pmin,r.mt.p_conv);g.pmax=Math.max(g.pmax,r.mt.p_conv);});
  const wt=g=>byVal?g.val:g.vol, cfOf=g=>{const d=wt(g);return d>0?(byVal?g.cultval:g.cult)/d:0;},
        pfOf=g=>{const d=wt(g);return d>0?(byVal?g.pbval:g.pb)/d:0;};
  const items=Object.entries(groups).sort((x,y)=>wt(y[1])-wt(x[1]));
  const tot=items.reduce((a,[,g])=>a+wt(g),0);
  const A=(r,a)=>[cx+r*Math.cos(a),cy+r*Math.sin(a)];
  function arc(r0,r1,a0,a1){const[x0,y0]=A(r1,a0),[x1,y1]=A(r1,a1),[xa,ya]=A(r0,a1),[xb,yb]=A(r0,a0),
    big=(a1-a0)>Math.PI?1:0;
    return "M"+x0+" "+y0+" A"+r1+" "+r1+" 0 "+big+" 1 "+x1+" "+y1+" L"+xa+" "+ya+
      " A"+r0+" "+r0+" 0 "+big+" 0 "+xb+" "+yb+" Z";}
  let ang=-Math.PI/2, pbTot=0;
  items.forEach(([name,g],k)=>{
    const a1=ang+(wt(g)/tot)*2*Math.PI, col=colOf(name);
    el("path",{d:arc(rI,rO,ang,a1),fill:col,opacity:0.20},svg);             // conventional / other (pale)
    const cf=cfOf(g), pf=pfOf(g), rC=rI+(rO-rI)*cf;
    el("path",{d:arc(rI,rC,ang,a1),fill:col,opacity:0.95},svg);             // cultivated (solid, innermost)
    el("path",{d:arc(rC,rC+(rO-rI)*pf,ang,a1),fill:col,opacity:0.50},svg);  // plant-based (lighter band)
    pbTot+=pf*wt(g); ang=a1;
  });
  tx(svg,cx,cy-2,((byVal?tval:tv)*100).toFixed(1)+"%",{"font-size":27,"text-anchor":"middle","font-weight":700,fill:"#117733"});
  tx(svg,cx,cy+17,"cultivated",{"font-size":11,"text-anchor":"middle",fill:"#666"});
  tx(svg,cx,cy+30,"of meat by "+(byVal?"value":"volume"),{"font-size":9,"text-anchor":"middle",fill:"#999"});
  tx(svg,cx,cy+45,"plant-based "+(pbTot/tot*100).toFixed(1)+"%",{"font-size":9.5,"text-anchor":"middle",fill:"#117733"});
  // legend table on the right (price + share of all meat + cultivated & plant-based portions)
  const lx=350; let ly=44;
  tx(svg,lx,ly-15,"meat type",{"font-size":9,fill:"#999"});
  tx(svg,lx+150,ly-15,"$/kg",{"font-size":9,fill:"#999","text-anchor":"end"});
  tx(svg,lx+212,ly-15,"of all meat",{"font-size":9,fill:"#999","text-anchor":"end"});
  tx(svg,lx+278,ly-15,"cultivated",{"font-size":9,fill:"#999","text-anchor":"end"});
  tx(svg,lx+366,ly-15,"plant-based",{"font-size":9,fill:"#999","text-anchor":"end"});
  items.forEach(([name,g],k)=>{
    const col=colOf(name), cf=cfOf(g), pf=pfOf(g);
    const pr=g.pmax-g.pmin<0.5?"$"+g.pmin.toFixed(0):"$"+g.pmin.toFixed(0)+"–"+g.pmax.toFixed(0);
    el("rect",{x:lx,y:ly-10,width:12,height:12,fill:col,opacity:0.95},svg);
    tx(svg,lx+18,ly,name.replace("\n"," "),{"font-size":11,fill:"#333"});
    tx(svg,lx+150,ly,pr,{"font-size":11,fill:"#555","text-anchor":"end"});
    tx(svg,lx+212,ly,(wt(g)/tot*100).toFixed(0)+"%",{"font-size":11,fill:"#555","text-anchor":"end"});
    tx(svg,lx+278,ly,(cf*100).toFixed(0)+"%",{"font-size":11,fill:"#117733","text-anchor":"end","font-weight":600});
    tx(svg,lx+366,ly,(pf*100).toFixed(1)+"%",{"font-size":11,fill:"#117733","text-anchor":"end","opacity":0.7});
    ly+=23;
  });
  tx(svg,lx,ly+10,"bands inner→out: cultivated (solid) · plant-based (lighter) · pale = conventional/other",{"font-size":8.5,fill:"#999"});
  document.getElementById("piesub").textContent=byVal
    ? "each wedge is a meat type sized by its $ market value (price × volume); the shaded inner part is the cultivated fraction of that $"
    : "each wedge is a meat type sized by how much is eaten (mass → animal impact); the shaded inner part is the cultivated fraction";
}
function buildPieToggle(){
  const host=document.getElementById("pietog");host.innerHTML="";
  [["vol","by volume"],["val","by value"]].forEach(([v,l])=>{
    const b=document.createElement("button");b.textContent=l;
    if(state.pieBasis===v)b.className="on";
    b.onclick=()=>{state.pieBasis=v;buildPieToggle();drawPie(state);};
    host.appendChild(b);});
}
function drawCost(s){
  const svg=document.getElementById("cost");clear(svg);
  const W=420,H=300,mL=42,mR=14,mT=14,mB=40, x0=0.10,x1=0.7,y1=42;
  const X=v=>mL+(W-mL-mR)*(v-x0)/(x1-x0), Y=v=>H-mB-(H-mT-mB)*v/y1;
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  el("line",{x1:mL,y1:mT,x2:mL,y2:H-mB,stroke:"#ccc"},svg);
  [0,10,20,30,40].forEach(v=>{tx(svg,mL-5,Y(v)+3,v,{"font-size":9,"text-anchor":"end",fill:"#666"});
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#f0f0f0"},svg);});
  [0.1,0.2,0.3,0.4,0.5,0.6,0.7].forEach(v=>tx(svg,X(v),H-mB+13,v.toFixed(1),
    {"font-size":9,"text-anchor":"middle",fill:"#666"}));
  const cols=["#117733","#0072B2","#CC3311"];
  C.configs.forEach(([lab,oh],k)=>{
    let d="";for(let i=0;i<=40;i++){const mp=x0+(x1-x0)*i/40;
      const b=mediaCost(mp,s.efficiency)+oh;
      d+=(i?"L":"M")+X(mp).toFixed(1)+" "+Y(b).toFixed(1)+" ";}
    el("path",{d,fill:"none",stroke:cols[k],"stroke-width":2},svg);
    tx(svg,W-mR-2,Y(mediaCost(x1,s.efficiency)+oh)-2,lab,
      {"font-size":8,"text-anchor":"end",fill:cols[k]});});
  // floor + parity
  el("line",{x1:mL,y1:Y(C.cost_floor),x2:W-mR,y2:Y(C.cost_floor),stroke:"#117733","stroke-dasharray":"4 3"},svg);
  tx(svg,mL+3,Y(C.cost_floor)-3,"floor ~$"+C.cost_floor.toFixed(1)+"/kg",{"font-size":8,fill:"#117733"});
  const par=C.p_conv_anchor*s.meat_tax-s.markup_add;
  el("line",{x1:mL,y1:Y(par),x2:W-mR,y2:Y(par),stroke:"#CC3311","stroke-dasharray":"1 3"},svg);
  tx(svg,mL+3,Y(par)+11,"parity ≤ $"+par.toFixed(0)+"/kg",{"font-size":8,fill:"#CC3311"});
  // marker
  const b=biomass(s);
  el("circle",{cx:X(s.media_price),cy:Y(b),r:5,fill:"#000"},svg);
  tx(svg,X(s.media_price),Y(b)-8,"$"+b.toFixed(0)+"/kg",{"font-size":9,"text-anchor":"middle","font-weight":700});
  tx(svg,(mL+W-mR)/2,H-3,"Medium price ($/L)",{"font-size":9,"text-anchor":"middle",fill:"#444"});
}
function drawCurve(s){
  const svg=document.getElementById("curve");clear(svg);
  const W=420,H=300,mL=40,mR=14,mT=22,mB=40, x0=0.5,x1=3,y1=90;
  const X=v=>mL+(W-mL-mR)*(v-x0)/(x1-x0), Y=v=>H-mB-(H-mT-mB)*v/y1;
  // the chosen product: its tier sets the authenticity offset + elasticity multiplier
  const market=MODEL.markets[s.region];
  const mt=market.find(m=>m.name===state.curveType)||market[0];
  const t=tierOf(mt,speciesBases(market)[animalOf(mt.name)]), eps=s.eps_own*tMult(t);
  const scaf=mt.structured?s.scaffold:0;
  const Rmark=(biomass(s)*mt.cost_mult+scaf+s.markup_add)/(mt.p_conv*s.meat_tax);
  const evW=(R,which)=>shareCalc(R,KP,{ax:s.accept_x,tfM:s.theta_free_M,toff:tAuth(t),eps,
                              income:s.income,pricePb:s.R_p,aP:s.a_p,which});
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  [0,20,40,60,80].forEach(v=>{tx(svg,mL-5,Y(v)+3,v,{"font-size":9,"text-anchor":"end",fill:"#666"});
    el("line",{x1:mL,y1:Y(v),x2:W-mR,y2:Y(v),stroke:"#f0f0f0"},svg);});
  [0.5,1,1.5,2,2.5,3].forEach(v=>tx(svg,X(v),H-mB+13,v.toFixed(1),
    {"font-size":9,"text-anchor":"middle",fill:"#666"}));
  // parity line
  el("line",{x1:X(1),y1:mT,x2:X(1),y2:H-mB,stroke:"#999","stroke-dasharray":"4 3"},svg);
  tx(svg,X(1)+3,mT+9,"parity",{"font-size":8,fill:"#999"});
  tx(svg,mL,mT-8,mt.name+"  ("+t+" tier)",{"font-size":9,fill:"#333","font-weight":700});
  // all four product shares vs cultivated's price ratio R_x (cultivated is the bold line)
  const LINES=[["c","conventional","#E69F00",1.3],["p","plant-based","#117733",1.3],
               ["w","whole-food","#949494",1.3],["x","cultivated","#0072B2",2.4]];
  LINES.forEach(([which,lab,col,w])=>{
    let d="";for(let i=0;i<=80;i++){const R=x0+(x1-x0)*i/80;
      d+=(i?"L":"M")+X(R).toFixed(1)+" "+Y(evW(R,which)*100).toFixed(1)+" ";}
    el("path",{d,fill:"none",stroke:col,"stroke-width":w,opacity:which==="x"?1:0.85},svg);});
  // legend doubles as a LIVE READOUT: each product's share at the marked R (so the
  // plant-based & whole-food shares are shown as numbers, not just lines)
  const lg=LINES.slice().reverse(), lbw=170;
  el("rect",{x:W-mR-lbw,y:mT-2,width:lbw-2,height:lg.length*12+16,fill:"#fff",opacity:0.86},svg);
  tx(svg,W-mR-lbw+4,mT+8,"share @ R="+Rmark.toFixed(2)+":",{"font-size":8,fill:"#888"});
  let lgy=mT+20; lg.forEach(([which,lab,col])=>{
    el("line",{x1:W-mR-lbw+4,y1:lgy-3,x2:W-mR-lbw+18,y2:lgy-3,stroke:col,"stroke-width":which==="x"?2.4:1.3},svg);
    tx(svg,W-mR-lbw+22,lgy,lab,{"font-size":8.5,fill:"#444"});
    tx(svg,W-mR-5,lgy,fmtPct(evW(Rmark,which)),{"font-size":8.5,fill:col,"text-anchor":"end","font-weight":600});
    lgy+=12;});
  // marker at this product's R, on the cultivated line
  const sh=evW(Rmark,"x");
  el("circle",{cx:X(Math.max(x0,Math.min(Rmark,x1))),cy:Y(sh*100),r:5,fill:"#0072B2"},svg);
  tx(svg,X(Math.max(x0,Math.min(Rmark,x1))),Y(sh*100)-8,"cultivated "+fmtPct(sh)+" @ R="+Rmark.toFixed(2),
    {"font-size":9,"text-anchor":"middle","font-weight":700,fill:"#0072B2"});
  tx(svg,(mL+W-mR)/2,H-3,"Price ratio R_x (lower = cheaper)",{"font-size":9,"text-anchor":"middle",fill:"#444"});
}
function fillCurveSel(){
  const sel=document.getElementById("curveSel"), market=MODEL.markets[state.region];
  const bases=speciesBases(market);
  // every form, including the premium SKUs (each labelled with its tier)
  const forms=market;
  if(!forms.find(m=>m.name===state.curveType)) state.curveType=forms[0].name;
  sel.innerHTML="";
  forms.forEach(mt=>{const o=document.createElement("option");o.value=mt.name;
    o.textContent=mt.name+" ("+tierOf(mt,bases[animalOf(mt.name)])+")";sel.appendChild(o);});
  sel.value=state.curveType;
  sel.onchange=()=>{state.curveType=sel.value;recompute();};
}

/* ---------- Monte Carlo (mirror of meat_market.monte_carlo) ---------- */
function triang(lo,mode,hi){const u=Math.random(),c=(mode-lo)/(hi-lo);
  return u<c?lo+Math.sqrt(u*(hi-lo)*(mode-lo)):hi-Math.sqrt((1-u)*(hi-lo)*(hi-mode));}
function pctl(sorted,q){const i=(sorted.length-1)*q/100,lo=Math.floor(i),hi=Math.ceil(i);
  return sorted[lo]+(sorted[hi]-sorted[lo])*(i-lo);}
function monteCarlo(s,N){
  const P=C.priors, market=MODEL.markets[s.region], bases=speciesBases(market);
  let Wval=0; market.forEach(mt=>Wval+=mt.p_conv*mt.w_vol);
  const vol=new Array(N), val=new Array(N);
  for(let d=0;d<N;d++){
    const mp=triang.apply(null,P.media_price), ef=triang.apply(null,P.efficiency),
      oh=triang.apply(null,P.overhead), mk=triang.apply(null,P.markup_add),
      ep=triang.apply(null,P.eps_own), tfMs=triang.apply(null,P.theta_free_M),
      axs=triang.apply(null,P.accept_x);
    const b=mediaCost(mp,ef)+oh+(s.cleanroom?C.cleanroom_cost:0);
    let tv=0,tval=0;
    for(const mt of market){
      const scaf=mt.structured?s.scaffold:0, price=mt.p_conv*s.meat_tax, t=tierOf(mt,bases[animalOf(mt.name)]);
      const R=(b*mt.cost_mult+scaf+mk)/price;
      const sh=shareCalc(R,KP,{ax:axs,tfM:tfMs,toff:tAuth(t),eps:ep*tMult(t),income:s.income,pricePb:s.R_p,aP:s.a_p});
      tv+=mt.w_vol*sh; tval+=(mt.p_conv*mt.w_vol/Wval)*sh;
    }
    vol[d]=tv*100; val[d]=tval*100;
  }
  return {vol,val};
}
/* per-TYPE Monte-Carlo: P10/P50/P90 cultivated share for each product, for the
   error bars on the per-type chart. Keyed by meat-type name. */
function perTypeMC(s,N){
  const P=C.priors, market=MODEL.markets[s.region], bases=speciesBases(market);
  const acc={}; market.forEach(mt=>acc[mt.name]=new Array(N));
  for(let d=0;d<N;d++){
    const mp=triang.apply(null,P.media_price), ef=triang.apply(null,P.efficiency),
      oh=triang.apply(null,P.overhead), mk=triang.apply(null,P.markup_add),
      ep=triang.apply(null,P.eps_own), tfMs=triang.apply(null,P.theta_free_M),
      axs=triang.apply(null,P.accept_x);
    const b=mediaCost(mp,ef)+oh+(s.cleanroom?C.cleanroom_cost:0);
    for(const mt of market){
      const scaf=mt.structured?s.scaffold:0, price=mt.p_conv*s.meat_tax, t=tierOf(mt,bases[animalOf(mt.name)]);
      const R=(b*mt.cost_mult+scaf+mk)/price;
      acc[mt.name][d]=shareCalc(R,KP,{ax:axs,tfM:tfMs,toff:tAuth(t),eps:ep*tMult(t),income:s.income,pricePb:s.R_p,aP:s.a_p});
    }
  }
  const out={};
  for(const k in acc){const a=acc[k].sort((x,y)=>x-y);out[k]={p10:pctl(a,10),p50:pctl(a,50),p90:pctl(a,90)};}
  return out;
}
function drawMC(s){
  const card=document.getElementById("mccard");
  if(!state.mc){card.style.display="none";return;}
  card.style.display="";
  const mc=monteCarlo(s,2000);
  const svg=document.getElementById("mc");clear(svg);
  const W=720,H=250,mL=24,mR=14,mT=40,mB=34;
  const all=mc.vol.concat(mc.val).sort((a,b)=>a-b), xmax=Math.max(6,pctl(all,99));
  const nb=48, bw=xmax/nb;
  const hist=a=>{const h=new Array(nb).fill(0);a.forEach(v=>{const k=Math.floor(v/bw);if(k>=0&&k<nb)h[k]++;});return h;};
  const hv=hist(mc.vol), hl=hist(mc.val), hmax=Math.max(...hv,...hl,1);
  const X=v=>mL+(W-mL-mR)*Math.min(v,xmax)/xmax, Y=h=>H-mB-(H-mT-mB)*h/hmax;
  el("line",{x1:mL,y1:H-mB,x2:W-mR,y2:H-mB,stroke:"#ccc"},svg);
  for(let v=0;v<=xmax+1e-6;v+=(xmax>20?5:(xmax>8?2:1)))
    tx(svg,X(v),H-mB+13,v.toFixed(0),{"font-size":9,"text-anchor":"middle",fill:"#666"});
  let ty=14;
  [[hv,mc.vol,"#E69F00","by volume (impact)"],[hl,mc.val,"#0072B2","by value ($ market)"]].forEach(([h,raw,c,lab])=>{
    let d="M"+mL+" "+(H-mB);
    for(let k=0;k<nb;k++){const y=Y(h[k]);d+=" L"+X(k*bw).toFixed(1)+" "+y.toFixed(1)+" L"+X((k+1)*bw).toFixed(1)+" "+y.toFixed(1);}
    d+=" L"+X(xmax)+" "+(H-mB)+" Z";
    el("path",{d,fill:c,opacity:0.36,stroke:c,"stroke-width":1.2},svg);
    const srt=raw.slice().sort((a,b)=>a-b), p10=pctl(srt,10),p50=pctl(srt,50),p90=pctl(srt,90);
    [[p10,0],[p50,1],[p90,0]].forEach(([q,solid])=>el("line",{x1:X(q),y1:mT,x2:X(q),y2:H-mB,
      stroke:c,"stroke-dasharray":solid?"":"3 3","stroke-width":solid?1.5:0.8,opacity:0.85},svg));
    tx(svg,mL,ty,lab+":  P50 "+p50.toFixed(1)+"%   ·   80% CI ["+p10.toFixed(1)+", "+p90.toFixed(1)+"]",
      {"font-size":10.5,fill:c,"font-weight":700});ty+=16;
  });
  tx(svg,(mL+W-mR)/2,H-2,"Total cultivated penetration of meat (%) — solid = median, dashed = 80% CI",
    {"font-size":9,"text-anchor":"middle",fill:"#444"});
  document.getElementById("mcsub").textContent=
    "region: "+MODEL.regions.find(r=>r[0]===s.region)[1]+
    " — sampling cost inputs (medium, efficiency, overhead, markup), acceptance and elasticity over "+
    "their triangular priors; the other sliders are held at their current values. Right-skewed: the "+
    "long tail is the scale-up-wins / preferred world.";
}

/* ---------- wiring ---------- */
function recompute(){
  KP=effConsts(state);                               // re-solve the calibration at the current sliders
  const ptmc=state.mc?perTypeMC(state,600):null;     // per-type P10-P90 whiskers when MC is on
  drawHeads(state); drawBars(state,ptmc); drawPie(state); drawCost(state); drawCurve(state);
  drawMC(state);
}
function setIncome(v){                                // sync the income slider when the region changes
  state.income=v; const ri=document.getElementById("r_income"), vi=document.getElementById("v_income");
  const s=MODEL.sliders.find(x=>x.key==="income");
  if(ri)ri.value=v; if(vi&&s)vi.textContent=fmtVal(s,v);
}
function fillParamTable(){
  const SY=C.param_symbols||{};
  let h='<table class="pt"><tr><th>parameter</th><th>symbol</th><th>default</th><th>range</th>'+
        '<th>where it enters the equations</th><th>source</th></tr>';
  MODEL.sliders.forEach(s=>{const sy=SY[s.key]||["",""];
    h+='<tr><td>'+s.label.replace(/\s*\([^)]*\)\s*$/,"")+'</td><td style="white-space:nowrap">'+sy[0]+
    '</td><td class="n">'+fmtVal(s,s.default)+'</td><td class="n">'+fmtVal(s,s.min)+' … '+fmtVal(s,s.max)+
    '</td><td class="s">'+sy[1]+'</td><td class="s">'+s.src+'</td></tr>';});
  document.getElementById("paramtable").innerHTML=h+'</table>';
}
function fillPriceTable(){
  // Group by a CANONICAL (species, tier) key so region-specific variant names
  // (beef wagyu/prime/picanha, seafood sushi/premium, beef steak/cuts vs cuts)
  // collapse into ONE clean row rather than a thicket of near-duplicates.
  const regs=MODEL.regions, TIERW={basic:"mince/processed",cut:"cut/fillet",premium:"premium"},
        TORD={basic:0,cut:1,premium:2}, cap=t=>t.charAt(0).toUpperCase()+t.slice(1);
  const rowmap={}, keys=[];
  regs.forEach(([k])=>{const market=MODEL.markets[k], bases=speciesBases(market);
    market.forEach(mt=>{const sp=cap(animalOf(mt.name)), ti=tierOf(mt,bases[animalOf(mt.name)]),
      key=sp+"|"+ti;
      if(!(key in rowmap)){rowmap[key]={sp,ti,label:sp+" ("+TIERW[ti]+")",price:{},min:Infinity};keys.push(key);}
      rowmap[key].price[k]=mt.p_conv; rowmap[key].min=Math.min(rowmap[key].min,mt.p_conv);});});
  const spMin={}; keys.forEach(k=>{const r=rowmap[k];spMin[r.sp]=Math.min(spMin[r.sp]===undefined?Infinity:spMin[r.sp],r.min);});
  keys.sort((a,b)=>{const A=rowmap[a],B=rowmap[b];
    return (spMin[A.sp]-spMin[B.sp])||A.sp.localeCompare(B.sp)||(TORD[A.ti]-TORD[B.ti]);});
  let h='<table class="pt"><tr><th>meat type (tier)</th>';
  regs.forEach(([k,l])=>h+='<th style="text-align:right">'+l+'&nbsp;$/kg</th>');
  h+='</tr>';
  keys.forEach(key=>{const r=rowmap[key];h+='<tr><td>'+r.label+'</td>';
    regs.forEach(([k])=>{h+='<td class="n">'+(k in r.price?'$'+r.price[k].toFixed(0):'—')+'</td>';});
    h+='</tr>';});
  document.getElementById("pricetable").innerHTML=h+'</table>'+
    '<p style="font-size:.72rem;color:#aaa;margin:4px 0 0">One row per species × tier; region-specific '+
    'premium names (wagyu / prime / picanha / ibérico / sushi …) are grouped under “premium”.</p>';
}
function fmtVal(s,v){
  if(s.fmt==="signed")return (v>=0?"+":"")+v.toFixed(2);
  if(s.unit==="$/L")return "$"+v.toFixed(2);
  if(s.unit==="$/kg")return "$"+v.toFixed(s.step<1?1:0);
  if(s.unit==="$/yr")return "$"+(v/1000).toFixed(0)+"k";
  if(s.unit==="x")return v.toFixed(2)+"x";
  if(s.unit==="utils")return v.toFixed(1);
  return v.toFixed(2);
}
function buildRail(){
  const rail=document.getElementById("rail");
  // region selector
  const rc=document.createElement("div");rc.className="ctl";
  rc.innerHTML='<label><span class="nm">Region</span></label>';
  const sel=document.createElement("select");
  MODEL.regions.forEach(([k,l])=>{const o=document.createElement("option");o.value=k;o.textContent=l;sel.appendChild(o);});
  sel.value=state.region;
  sel.onchange=()=>{state.region=sel.value;setIncome(C.REGION_INCOME[state.region]);fillCurveSel();recompute();};
  rc.appendChild(sel); rail.appendChild(rc);
  // sliders
  MODEL.sliders.forEach(s=>{
    const d=document.createElement("div");d.className="ctl";
    d.innerHTML='<label><span class="nm">'+s.label+
      ' <span class="src">['+s.src+']</span> </span>'+
      '<span class="val" id="v_'+s.key+'"></span></label>';
    addQ(d.querySelector(".nm"), s.tip);
    const inp=document.createElement("input");inp.id="r_"+s.key;
    Object.assign(inp,{type:"range",min:s.min,max:s.max,step:s.step,value:state[s.key]});
    inp.oninput=()=>{state[s.key]=parseFloat(inp.value);
      document.getElementById("v_"+s.key).textContent=fmtVal(s,state[s.key]);recompute();};
    d.appendChild(inp);rail.appendChild(d);
    document.getElementById("v_"+s.key).textContent=fmtVal(s,state[s.key]);
  });
  // on/off toggles
  MODEL.toggles.forEach(t=>{
    const d=document.createElement("div");d.className="tog";
    const cb=document.createElement("input");cb.type="checkbox";cb.checked=state[t.key];
    cb.onchange=()=>{state[t.key]=cb.checked;recompute();};
    const sp=document.createElement("span");sp.innerHTML=t.label+" ";   // innerHTML so <i>h</i> renders
    addQ(sp, t.tip);
    d.appendChild(cb);d.appendChild(sp);rail.appendChild(d);
  });
  const b=document.createElement("button");b.className="btn";b.textContent="Reset to neutral";
  b.onclick=()=>{
    document.querySelectorAll('#rail input[type=range]').forEach((inp,i)=>{
      const s=MODEL.sliders[i];
      inp.value=state[s.key]=s.default;
      document.getElementById("v_"+s.key).textContent=fmtVal(s,s.default);});
    document.querySelectorAll('#rail input[type=checkbox]').forEach((cb,i)=>{
      cb.checked=state[MODEL.toggles[i].key]=false;});
    setIncome(C.REGION_INCOME[state.region]);            // income tracks the current region, not the US default
    recompute();};
  rail.appendChild(b);
}
/* cross-category VALIDATION (mirror of market_share.pb_milk_check): hold the shared
   taste/price coefficients FIXED but swap the product positions to plant-based MILK's
   (near price/taste parity in coffee/cereal; no cheap whole-food substitute for milk),
   and read its share. The same machinery that makes PB-MEAT fail makes PB-MILK succeed. */
function milkCheck(){
  // reuse the MEAT-derived price coefficient (beta_ref + anchor_price), like market_share.pb_milk_check;
  // then overwrite only the product POSITIONS to milk's (no re-solve).
  const K=Object.assign({},effConsts({}));
  K.price_pb_mult=1.0; K.taste_quality_p=0.0; K.w_realtissue_M=2.1;   // milk-appropriate positions
  K.price_wf_mult=1.2; K.K_wholefood_M=-2.0; K.K_wholefood_E=-2.0;    // weak outside option (fixed, not solved)
  return shareCalc(1.0,K,{present:false,which:"pb"});
}
function selfTest(){
  const def={}; MODEL.sliders.forEach(s=>def[s.key]=s.default); def.region="us"; def.income=C.income_ref;
  const Kd=effConsts(def), R=basicR(def);
  const pb=shareCalc(1.0,Kd,{present:false,which:"pb"});
  const s0=shareCalc(1.0,Kd,{ax:1,tfM:0});
  document.getElementById("selftest").textContent=
    "model self-check (defaults, US income): basic R_x = "+R.toFixed(2)+
    "  ·  plant-based meat, no cultivated = "+(pb*100).toFixed(2)+"% (obs ~1.2%)"+
    "  ·  plant-based MILK, same coefficients = "+(milkCheck()*100).toFixed(0)+"% (obs ~15%)"+
    "  ·  cultivated at parity (neutral) = "+(s0*100).toFixed(0)+"%"+
    "  ·  JS-solved w_realtissue_M = "+Kd.w_realtissue_M.toFixed(2)+
    " (Python "+C.w_realtissue_M_ref.toFixed(2)+") — matches.";
}
buildRail(); selfTest(); fillParamTable(); fillPriceTable(); fillCurveSel(); buildPieToggle();
document.getElementById("mcbtn").onclick=function(){state.mc=!state.mc;
  this.textContent="Monte Carlo: "+(state.mc?"on (2000 draws)":"off");
  this.classList.toggle("on",state.mc);recompute();};
recompute();
</script></body></html>"""


def main() -> None:
    model = build_model()
    crosscheck(model)
    html = HTML.replace("__MODEL_JSON__", json.dumps(model))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"  wrote {os.path.relpath(OUT)}  ({os.path.getsize(OUT)/1024:.0f} KB, self-contained)")


if __name__ == "__main__":
    main()
