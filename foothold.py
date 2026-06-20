#!/usr/bin/env python3
"""
foothold.py — the strategic ENTRY layer: which concrete PRODUCTS make the best
disruptive footholds, and the price they pay in displacement impact.

This is the "spine + gate" prototype for the foothold analysis. It is DISTINCT
from meat_market.py in three ways:

  * per concrete PRODUCT, not per species (foie gras != duck breast; sushi bluefin
    != canned tuna; unagi, caviar, shark-fin, novel/no-referent items);
  * it scores BEACHHEAD-FITNESS (can it establish a foothold NOW?), not the
    equilibrium share meat_market computes;
  * its headline output is a PREDICTION about entry order + an anti-correlation,
    not a calibrated share.

The beachhead conditions (Tesla-derived + this project's demand findings)
---------------------------------------------------------------------------
A product is a good disruptive foothold when, like the Tesla Roadster, three
things align: (i) high willingness-to-pay, (ii) cultivated's differentiated
attribute is a PLUS there (not the authenticity tax it pays at the luxury tier),
and (iii) a ridable cost curve. Condition (ii) is decisive and is satisfied where
the CONVENTIONAL product carries a salient, intrinsic DEFECT that cultivated
removes -- health/safety (mercury, contaminants), environmental (overfishing),
or ethical (gavage). Foie gras is the purest case (the defect IS the product's
defining sin); wagyu is the trap (no defect -> cultivated only loses authenticity).

EPISTEMIC STATUS (read before trusting a number)
------------------------------------------------
Two kinds of input, treated differently (mirrors METHODS.md Layer-2):
  * MODEL-DERIVED, quantitative: the price ratio R per product, computed by the
    ONE cost->R equation (uncertainty.R_from_inputs) -- single-sourced, parity-safe.
  * SOURCED-ORDINAL judgements: defect advantage, authenticity penalty, tractability,
    transferability, regulatory opening. These are coarse -1..+2 scores. THE VALUES
    BELOW ARE PROVISIONAL best-knowledge estimates with rationale notes; before this
    is promoted to the published site they must be hardened with citations and the
    registry migrated into inputs.py per the single-source rule.

The GATE (why this runs before any UI)
--------------------------------------
Two checks decide whether the story is real enough to build a panel for:
  1. ANTI-CORRELATION: foothold-fitness should run OPPOSITE to displacement impact
     (the best footholds save the fewest animals). Reported as a rank correlation.
  2. RETRODICTION: the products real companies launched first (Gourmey->foie gras,
     Wildtype->salmon, Vow->novel, Forsea->eel, BlueNalu->bluefin) should rank near
     the top on foothold-fitness. If they don't, the framework is wrong.
  3. ROBUSTNESS: a ranking is only reported if it survives perturbation of the axis
     weights; rank-fragile products are flagged, not forced into an order.

    python foothold.py
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from inputs import value
from uncertainty import R_from_inputs


# ----------------------------------------------------------------------------
# The product registry. PROVISIONAL sourced ordinals (-1..+2); authenticity is a
# PENALTY (0 none .. +2 high). volume_kt = global category size, kt/yr, the
# displacement-impact proxy. structure drives the scaffold cost in R.
# ----------------------------------------------------------------------------
@dataclass(frozen=True)
class Foothold:
    label: str
    p_conv: float | None     # $/kg conventional referent (None = no referent / novel)
    volume_kt: float         # global category volume kt/yr (displacement proxy)
    structure: str           # "processed" (mince/roe/organ — no scaffold) | "structured" (whole-muscle cut — scaffold)
    defect_health: int       # cultivated advantage from a HEALTH/SAFETY defect of the conv. product
    defect_env: int          # ... from an ENVIRONMENTAL defect (overfishing, emissions)
    defect_ethics: int       # ... from an ETHICAL/WELFARE defect (gavage, finning, feedlot)
    authenticity: int        # authenticity PENALTY: whole-cut high (+2), processed/novel low (0)
    tractability: int        # ease of culturing convincingly (fatty/soft +, structured muscle -)
    transferability: int     # does the capability descend toward mass products?
    regulatory: int          # protected market space / approval momentum
    launched_by: str = ""    # real company that led with this product (for retrodiction); "" = none
    no_referent: bool = False
    note: str = ""
    # --- Option B: authenticity as an observable market PARTITION (not a latent utility coefficient) ---
    p_base: float | None = None   # accessible-tier price cultivated actually competes at (provenance rent
                                  #   stripped); None -> p_conv (commodity: a single grade, no rent tier)


# The prestige-core VOLUME share is a SINGLE GLOBAL value phi (not per-product). Only two products' splits
# are sourceable — salmon (~0.25, wild's share of supply) and iberico (~0.20, bellota's share) — and they
# cluster at ~0.2-0.25, so one global number is as defensible as 11 unsourced guesses (and far easier to
# explain). phi is the knob (slider, default below). A product HAS a prestige core iff it has a distinct,
# cheaper accessible tier (p_base < p_conv); commodity products (p_base = p_conv) have none.
PHI_DEFAULT = 0.25


def base_price(p: "Foothold") -> float | None:
    """The price cultivated competes at: the accessible tier (rent stripped), not the headline."""
    return p.p_conv if p.p_base is None else p.p_base


def has_rent(p: "Foothold") -> bool:
    """True iff a distinct prestige tier sits above the accessible grade (p_base < p_conv)."""
    b = base_price(p)
    return b is not None and p.p_conv is not None and b < p.p_conv


def addressable_kt(p: "Foothold", phi: float = PHI_DEFAULT) -> float:
    """Volume cultivated can contest = the aspirational base; the prestige core (global share phi) is
    removed, but only where a prestige tier exists (commodity has none)."""
    return (1.0 - (phi if has_rent(p) else 0.0)) * p.volume_kt


# Prices SOURCED (June 2026 retail/wholesale; per-product citations in PRICE_BASIS below): p_conv = the
# prestige/headline-grade price, p_base = the accessible-grade price cultivated competes at. A product has
# a prestige core iff p_base < p_conv; the prestige VOLUME share itself is a SINGLE GLOBAL phi (PHI_DEFAULT
# above; the §6 slider), since only salmon (~0.25) and iberico (~0.20) are sourceable. (volume_kt = global
# category volume; ordinals carry their rationale.)
PRODUCTS: list[Foothold] = [
    Foothold("cultivated foie gras", 140, 30, "processed",
             defect_health=0, defect_env=0, defect_ethics=2, authenticity=0,
             tractability=2, transferability=1, regulatory=2, launched_by="Gourmey",
             p_base=80,
             note="gavage is the defining, legally-banned defect; cruelty-free SUBSTITUTES for much of the "
                  "artisanal rent; pate->no authenticity penalty; fatty liver is easy"),
    Foothold("cultivated unagi (eel)", 60, 250, "structured",
             defect_health=1, defect_env=2, defect_ethics=1, authenticity=1,
             tractability=0, transferability=1, regulatory=1, launched_by="Forsea",
             p_base=35,
             note="eel FILLET = whole-muscle (structured cut); Japanese/European eel endangered (IUCN/CITES); "
                  "~all farmed (one grade); glazed kabayaki -> low rent"),
    Foothold("cultivated bluefin tuna (sushi)", 350, 40, "structured",
             defect_health=2, defect_env=2, defect_ethics=1, authenticity=2,
             tractability=-1, transferability=1, regulatory=1, launched_by="BlueNalu",
             p_base=150,
             note="high mercury + overfishing; OTORO is the rent tier, AKAMI the accessible one ($150/kg) -> "
                  "even the accessible bluefin tier is premium, so cultivated is price-reachable; sashimi block is hard"),
    Foothold("cultivated salmon (sushi-grade)", 40, 2900, "structured",
             defect_health=1, defect_env=2, defect_ethics=1, authenticity=1,
             tractability=0, transferability=2, regulatory=1, launched_by="Wildtype",
             p_base=26,
             note="cultivated's safety/sustainability is capturable, but the accessible farmed-fillet tier "
                  "(~$26/kg) is cheap -> cultivated sits near/just-above parity there; big addressable base"),
    Foothold("cultivated caviar", 8000, 0.4, "processed",
             defect_health=0, defect_env=2, defect_ethics=1, authenticity=1,
             tractability=0, transferability=0, regulatory=1, launched_by="",
             p_base=2500,
             note="sturgeon CITES-listed; wild beluga banned (>$20k); even 'accessible' ossetra ~$2.5k/kg is "
                  "deep rent -> price-reachable, but the category VOLUME (~0.4 kt) is so tiny that impact ~0 regardless"),
    Foothold("cultivated shark fin", 400, 8, "processed",
             defect_health=1, defect_env=2, defect_ethics=2, authenticity=0,
             tractability=1, transferability=0, regulatory=-1, launched_by="",
             p_base=150,
             note="finning + conservation defect, but the TRADE ITSELF is being banned (category eliminated) "
                  "-> regulatory HEADWIND; price ESTIMATE (illegal/declining market, not cleanly sourceable)"),
    Foothold("cultivated wagyu", 330, 100, "structured",
             defect_health=0, defect_env=0, defect_ethics=0, authenticity=2,
             tractability=-1, transferability=2, regulatory=0, launched_by="Orbillion",
             p_base=55,
             note="A5 prestige is pure rent (no defect to fix), BUT a real accessible American-'wagyu' tier "
                  "(~$55/kg) exists -> cultivated can contest that base on price, conceding the A5 core"),
    Foothold("cultivated beef steak (commodity)", 15, 72000, "structured",
             defect_health=1, defect_env=2, defect_ethics=1, authenticity=2,
             tractability=-1, transferability=2, regulatory=0, launched_by="Mosa Meat",
             note="huge climate/feedlot defect + huge volume, but cheap -> R awful + structured"),
    Foothold("cultivated chicken breast (commodity)", 8, 120000, "structured",
             defect_health=1, defect_env=1, defect_ethics=1, authenticity=0,
             tractability=0, transferability=1, regulatory=1, launched_by="UPSIDE/GOOD Meat",
             note="the impact prize, but a structured breast at near-commodity price -> R poor; APPROVED yet stalled. "
                  "$8/kg = panel 1's chicken-CUTS tier (shares reconcile)"),
    Foothold("cultivated pork loin (commodity)", 9, 115000, "structured",
             defect_health=1, defect_env=1, defect_ethics=2, authenticity=0,
             tractability=0, transferability=1, regulatory=1, launched_by="Mission Barns",
             note="the other mass-meat prize: huge volume + a strong, heavily-legislated welfare defect "
                  "(gestation crates; pigs are highly intelligent), but a structured loin at near-commodity "
                  "price -> R>1, unreachable on price. $9/kg = panel 1's pork-CUTS tier (shares reconcile)"),
    Foothold("cultivated pet food", 6, 20000, "processed",
             defect_health=1, defect_env=1, defect_ethics=1, authenticity=0,
             tractability=2, transferability=1, regulatory=2, launched_by="Bond Pet Foods",
             note="no authenticity penalty (pets), lower regulatory bar, but very low WTP/margin"),
    Foothold("cultivated uni (sea urchin)", 250, 30, "processed",
             defect_health=0, defect_env=1, defect_ethics=1, authenticity=1,
             tractability=0, transferability=0, regulatory=1, launched_by="",
             p_base=75,
             note="luxury roe; premium Japanese uni ~$300/kg vs accessible ~$75; conservation case MIXED "
                  "(wild urchin 'barrens'); gonad tissue is specialised to culture"),
    Foothold("cultivated lobster", 60, 300, "structured",
             defect_health=1, defect_env=1, defect_ethics=1, authenticity=1,
             tractability=0, transferability=1, regulatory=1, launched_by="",
             p_base=40,
             note="boiled-alive welfare + fishery pressure; little provenance rent (price is the product) -> "
                  "accessible whole/frozen tier ~$40/kg is the base"),
    Foothold("cultivated premium prawns", 30, 2000, "structured",
             defect_health=1, defect_env=2, defect_ethics=2, authenticity=0,
             tractability=1, transferability=1, regulatory=1, launched_by="Umami Bioworks (ex-Shiok), CellMEAT",
             p_base=18,
             note="whole prawn = muscle (structured cut, like lobster); mangrove loss + bycatch (env) + documented "
                  "forced labour (ethics); little provenance rent; the accessible prawn tier (~$18/kg) is cheap; large addressable base"),
    Foothold("cultivated shrimp (commodity)", 10, 4000, "structured",
             defect_health=1, defect_env=2, defect_ethics=2, authenticity=0,
             tractability=1, transferability=1, regulatory=1, launched_by="",
             note="whole shrimp = muscle (structured cut, like premium prawns); same defects as premium prawns but "
                  "at commodity price -> R>1; the high-impact prize, unreachable on price"),
    Foothold("cultivated iberico ham", 120, 30, "structured",
             defect_health=0, defect_env=0, defect_ethics=0, authenticity=2,
             tractability=-1, transferability=1, regulatory=0, launched_by="",
             p_base=35,
             note="A TRAP for a different reason than caviar: the base (cebo, ~80% of volume) is LARGE, but cultivated "
                  "has no defect to fix AND is barely cheaper than ~$35/kg cebo -> ~parity with no attribute edge"),
    Foothold("novel / no-referent (e.g. cultured quail)", None, 0.1, "processed",
             defect_health=0, defect_env=0, defect_ethics=1, authenticity=0,
             tractability=1, transferability=0, regulatory=1, launched_by="Vow",
             no_referent=True,
             note="escapes the authenticity benchmark entirely (no referent); high margin, ~0 displacement"),
]


# Per-product PRICE BASIS — surfaced in the panel so the reader sees where the competition price comes from.
# PRICES are SOURCED (June 2026 retail/wholesale, sources named). The prestige VOLUME share is a SINGLE GLOBAL
# φ (the §6 slider), anchored to the two products whose grade splits ARE published — salmon (wild ~25%) and
# iberico (bellota ~20%); applied to every product with a prestige tier (p_base < p_conv).
PRICE_BASIS: dict[str, str] = {
    "cultivated foie gras":            "duck foie gras ~$88–176/kg retail (GourmetFoodStore); France fresh €40–100/kg (Statista) → accessible ~$80, premium goose ~$140/kg",
    "cultivated unagi (eel)":          "Japan wholesale ¥5,553/kg≈$37 (Japan Times 2023), ~all farmed → base ~$35, premium/wild ~$60",
    "cultivated bluefin tuna (sushi)": "akami $69.99/lb≈$154/kg, ō-toro retail ~$364/kg (Yama Seafood; Pacific Wild Pick) → base ~$150, headline ~$350",
    "cultivated salmon (sushi-grade)": "farmed Atlantic ~$11/kg wholesale to ~$32/kg fillet (Selina Wamucii; Tridge) → base ~$26, headline ~$40. ANCHORS global φ (wild salmon ~25% of supply, IMARC)",
    "cultivated caviar":               "wild beluga banned >$20k/kg, farmed beluga $5–15k, accessible ossetra/sevruga $1.5–5k (caviar trade guides) → base ~$2500, headline ~$8000 (impact ~0 anyway: category ~0.4 kt)",
    "cultivated shark fin":            "prices ESTIMATED (illegal/declining trade, not cleanly sourceable): ~$150 accessible, ~$400 top-grade",
    "cultivated wagyu":                "A5 Japanese $100–250/lb≈$220–550/kg, American wagyu $15–40/lb≈$33–88/kg (The Meatery; Cozymeal) → base ~$55, headline ~$330",
    "cultivated beef steak (commodity)":"commodity retail steak ~$15/kg (single grade; no prestige tier)",
    "cultivated chicken breast (commodity)":"everyday chicken breast ~$8/kg (single grade; no prestige tier; = panel 1 chicken-cuts tier)",
    "cultivated pork loin (commodity)":"everyday pork loin ~$9/kg (single grade; no prestige tier; = panel 1 pork-cuts tier)",
    "cultivated pet food":             "premium pet-food meat ~$6/kg (single grade; no prestige tier)",
    "cultivated uni (sea urchin)":     "premium Japan/US uni ~$300/kg vs accessible ~$75/kg (Tridge; Selina Wamucii) → base ~$75, headline ~$250",
    "cultivated lobster":              "whole live ~$26.72/lb≈$59/kg, tail meat $55–75/lb (LobsterAnywhere) → base ~$40, headline ~$60; little provenance rent",
    "cultivated premium prawns":       "tiger prawns ~$5–25/kg vs commodity shrimp ~$2–10/kg (Tridge; IndexMundi) → base ~$18, premium ~$30",
    "cultivated shrimp (commodity)":   "commodity whole shrimp ~$10/kg retail (single grade; no prestige tier)",
    "cultivated iberico ham":          "bellota whole-leg ~$80–150/kg vs serrano/cebo ~$25–40/kg (IberGour; Ibericofoods) → base ~$35, headline ~$120. ANCHORS global φ (bellota ~20% of iberico, Nat Geo/TasteAtlas)",
}


# ----------------------------------------------------------------------------
# Per-product R — reuse THE one cost->R equation (no parallel cost math).
# ----------------------------------------------------------------------------
def product_R(p: Foothold) -> float:
    """Price ratio R = cultivated retail / the price cultivated actually competes at = base_price
    (the accessible tier, NOT the rent-laden headline). Via uncertainty.R_from_inputs at the central
    (mode) inputs; scaffold terms switch on only for STRUCTURED cuts; np.nan for no-referent products."""
    if p.no_referent or base_price(p) is None:
        return float("nan")
    structured = p.structure == "structured"
    return float(R_from_inputs(
        value("media_price"), value("efficiency"), value("overhead"),
        value("markup_add"), base_price(p),
        scaffold_frac=value("scaffold_frac") if structured else 0.0,
        material_price=value("material_price") if structured else 0.0,
        process_cost=value("process_cost") if structured else 0.0,
    ))


# ----------------------------------------------------------------------------
# Scoring. Three SEPARATED scores (foothold-fitness, displacement, descent-value).
# Axes are min-max normalised to 0..1 across the product set, then weighted.
# ----------------------------------------------------------------------------
DEFAULT_WEIGHTS = {
    "wtp": 0.22,            # willingness-to-pay / margin headroom (from p_conv)
    "attribute": 0.34,      # the DECISIVE Tesla condition (ii): defect advantage net of authenticity
    "price_comp": 0.12,     # price-competitiveness (low R) -- matters less than attribute at the foothold
    "tractability": 0.16,   # can we make it convincingly yet?
    "regulatory": 0.16,     # protected space / approval momentum
}


def _minmax(x: np.ndarray) -> np.ndarray:
    lo, hi = np.nanmin(x), np.nanmax(x)
    if hi - lo < 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


def _axes(products: list[Foothold]) -> dict[str, np.ndarray]:
    """Raw (un-normalised) axis values per product, before min-max."""
    Rs = np.array([product_R(p) for p in products])
    # no-referent products escape the price race -> treat as best-in-class price-competitiveness
    price_comp_raw = -Rs.copy()
    price_comp_raw[np.isnan(price_comp_raw)] = np.nanmax(price_comp_raw)  # novel = not price-constrained
    return {
        # WTP / margin headroom = the ACCESSIBLE-tier price cultivated can charge (rent stripped)
        "wtp": np.array([np.log10(base_price(p)) if base_price(p) else np.log10(_novel_wtp(products))
                         for p in products]),
        # Option B: authenticity is handled by the price partition, so the attribute axis is the
        # CAPTURABLE premium only (max defect cultivated genuinely delivers), no authenticity subtraction.
        "attribute": np.array([max(p.defect_health, p.defect_env, p.defect_ethics)
                               for p in products], dtype=float),
        "price_comp": price_comp_raw,
        "tractability": np.array([p.tractability for p in products], dtype=float),
        "regulatory": np.array([p.regulatory for p in products], dtype=float),
        "_R": Rs,
    }


def _novel_wtp(products: list[Foothold]) -> float:
    """No-referent novelties sell into fine dining -> assign them the top observed base price."""
    return max(base_price(p) for p in products if base_price(p))


def _market_viability(products: list[Foothold]) -> np.ndarray:
    """A ONE-SIDED floor on foothold-fitness: a beachhead needs an addressable revenue
    pool ($ = volume x price). Saturates EARLY (~$1B): every real market — including the
    luxury low-volume/high-price ones (foie gras, shark fin, caviar) — sits at 1.0, so this
    does NOT reward commodity volume and cannot reintroduce the impact axis. It only pulls
    down genuinely near-zero, unproven markets (a no-referent novelty with no category yet).
    Shark fin is demoted by its regulatory headwind (banned trade), NOT here. Uses ADDRESSABLE market
    VALUE (base price x base volume, prestige core removed) — so pure-rent categories (caviar) shrink."""
    mv = np.array([addressable_kt(p) * (base_price(p) if base_price(p) else _novel_wtp(products))
                   for p in products])   # $M (addressable kt x accessible $/kg)
    return np.clip(np.log10(mv + 1) / 3.0, 0.5, 1.0)   # saturates at ~$1B; floor 0.5


def foothold_fitness(products: list[Foothold], weights: dict | None = None) -> np.ndarray:
    w = DEFAULT_WEIGHTS if weights is None else weights
    ax = _axes(products)
    norm = {k: _minmax(ax[k]) for k in w}
    base = sum(w[k] * norm[k] for k in w)
    return base * _market_viability(products)


def displacement_impact(products: list[Foothold]) -> np.ndarray:
    """Size of the prize if the product won its ADDRESSABLE base ~ log addressable volume
    (the prestige core is unreachable, so it doesn't count toward displaceable impact)."""
    vol = np.array([max(addressable_kt(p), 1e-3) for p in products])
    return _minmax(np.log10(vol))


def descent_value(products: list[Foothold]) -> np.ndarray:
    """Does a win here help reach mass products? transferability x accessible-price margin headroom."""
    transfer = _minmax(np.array([p.transferability for p in products], dtype=float))
    wtp = _minmax(np.array([np.log10(base_price(p)) if base_price(p) else np.log10(_novel_wtp(products))
                            for p in products]))
    return transfer * wtp


# ----------------------------------------------------------------------------
# Gate checks
# ----------------------------------------------------------------------------
def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rho without scipy: Pearson on ranks."""
    ra, rb = _rank(a), _rank(b)
    ra, rb = ra - ra.mean(), rb - rb.mean()
    denom = np.sqrt((ra**2).sum() * (rb**2).sum())
    return float((ra * rb).sum() / denom) if denom else 0.0


def _rank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    r = np.empty_like(order, dtype=float)
    r[order] = np.arange(len(x))
    return r


def robustness(products: list[Foothold], n: int = 2000, seed: int = 0) -> dict:
    """Perturb the weights (Dirichlet around the defaults) and measure how stable the
    ranking is. Returns, per product, the fraction of draws it lands in the top-third."""
    rng = np.random.default_rng(seed)
    keys = list(DEFAULT_WEIGHTS)
    base = np.array([DEFAULT_WEIGHTS[k] for k in keys])
    k_top = max(1, len(products) // 3)
    top_counts = np.zeros(len(products))
    base_rank = _rank(-foothold_fitness(products))
    taus = []
    for _ in range(n):
        w = rng.dirichlet(base * 40)            # concentrated around the defaults
        wd = {k: w[i] for i, k in enumerate(keys)}
        F = foothold_fitness(products, wd)
        top_counts += (_rank(-F) < k_top)
        taus.append(_spearman(-F, -foothold_fitness(products)))
    return {
        "top_third_frac": top_counts / n,
        "mean_rank_corr_vs_default": float(np.mean(taus)),
        "base_rank": base_rank,
        "k_top": k_top,
    }


# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
def main() -> None:
    P = PRODUCTS
    F = foothold_fitness(P)
    I = displacement_impact(P)
    V = descent_value(P)
    ax = _axes(P)
    R = ax["_R"]
    rob = robustness(P)
    order = np.argsort(-F)

    print("=" * 96)
    print("FOOTHOLD ANALYSIS  —  the strategic entry layer  (PROVISIONAL sourced ordinals)")
    print("=" * 96)
    print("R is vs the ACCESSIBLE-tier price (base, rent stripped); impact uses the ADDRESSABLE base "
          "(prestige core removed).")
    hdr = (f"{'product':<34}{'head$':>6}{'base$':>6}{'rent?':>6}{'R':>6}{'foothold':>9}"
           f"{'impact':>8}{'top⅓%':>7}  launched")
    print(hdr)
    print(f"(prestige share phi = {PHI_DEFAULT} global where rent? = yes)")
    print("-" * 96)
    for i in order:
        p = P[i]
        rtxt = "  — " if np.isnan(R[i]) else f"{R[i]:4.2f}"
        head = "  — " if p.p_conv is None else f"{p.p_conv:.0f}"
        base = "  — " if base_price(p) is None else f"{base_price(p):.0f}"
        rent = "yes" if has_rent(p) else "no"
        print(f"{p.label:<34}{head:>6}{base:>6}{rent:>6}{rtxt:>6}{F[i]:9.3f}{I[i]:8.3f}"
              f"{100*rob['top_third_frac'][i]:6.0f}%  {p.launched_by}")
    print("-" * 96)

    # GATE 1 — anti-correlation between foothold-fitness and displacement impact
    rho = _spearman(F, I)
    print(f"\nGATE 1  anti-correlation (foothold vs impact):  Spearman rho = {rho:+.2f}")
    print("        expect NEGATIVE — the best footholds displace the fewest animals.")
    print(f"        -> {'PASS' if rho < -0.3 else 'WEAK/FAIL'}")

    # GATE 2 — retrodiction: do launched products rank near the top?
    launched_idx = [i for i in range(len(P)) if P[i].launched_by]
    ranks = {P[i].label: int(_rank(-F)[i]) + 1 for i in launched_idx}
    premium_launchers = {"Gourmey", "Forsea", "Wildtype", "BlueNalu", "Vow"}
    prem = [P[i].label for i in launched_idx if P[i].launched_by in premium_launchers]
    prem_ranks = [ranks[l] for l in prem]
    print(f"\nGATE 2  retrodiction — rank of each company's first product (1 = best foothold):")
    for i in launched_idx:
        print(f"        #{ranks[P[i].label]:>2}  {P[i].label:<38} ({P[i].launched_by})")
    print(f"        premium/defect launchers (Gourmey/Forsea/Wildtype/BlueNalu/Vow) "
          f"median rank = {int(np.median(prem_ranks))} of {len(P)}")
    print(f"        -> {'PASS' if np.median(prem_ranks) <= len(P)/2 else 'WEAK/FAIL'} "
          f"(commodity-chicken players chose the impact prize directly — the hardest economics)")

    # GATE 3 — robustness
    print(f"\nGATE 3  robustness: mean rank-correlation to default across 2000 weightings = "
          f"{rob['mean_rank_corr_vs_default']:.2f}")
    print(f"        -> {'PASS' if rob['mean_rank_corr_vs_default'] > 0.8 else 'WEAK/FAIL'} "
          f"(ranking stable under weight perturbation)")
    print("=" * 96)


if __name__ == "__main__":
    main()
