#!/usr/bin/env python3
"""
industry_claims.py — the model against what companies and their advisers report, on the same basis.

Company cost figures are usually operating cost (COGS): medium, labour, utilities, consumables, with no charge for
the plant. The model's scenario costs include a yearly charge on the plant (17.3% of its cost, food-industry
financing). This module splits every scenario into the two, and computes the model's figure for the way the one
working 20 m3 plant runs (Vow: drained and refilled, nothing holding the cells back), so that a claim can be set
against the number it should be compared with.

The claims themselves are sourced data, not model output: each records what it is a cost of, whether capital is in
it, whether it is a run or a model, and who checked it, as far as the source says. "not stated" means the source
does not say. Sources were read on 2026-11-16 (trade press and a company page; the underlying reports were not).

    python industry_claims.py              # the tables, as text
    python industry_claims.py --markdown   # the tables RESULTS.md quotes
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

import floor_physics as fp
import plant_items as PI
import scenarios as S
import vessels as V
from inputs import value


@dataclass(frozen=True)
class Claim:
    who: str          # who produced the figure
    figure: str       # as stated, with its unit
    of_what: str      # cell mass / finished product / medium / a vessel; wet or dry if stated
    capital: str      # "excluded (COGS)", "included", "not stated"
    kind: str         # "run", "model", "vetted under NDA", "company statement"
    checked: str      # who checked it, if anyone
    date: str
    source: str       # URL


CLAIMS = (
    Claim("Lever VC (investor), across several companies", "$10–15/kg; some below $10/kg",
          "cell mass; wet or dry not stated; scale not stated", "excluded (COGS)", "vetted under NDA",
          "the investor; data not public", "April 2025",
          "https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive"),
    Claim("Lever VC (investor)", "medium at $1/L or less, several under $0.50/L",
          "medium per litre; litres per kg not stated", "not applicable", "vetted under NDA",
          "the investor; data not public", "April 2025",
          "https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive"),
    Claim("Gourmey (now PARIMA), modelled by Arthur D. Little", "€7/kg at 5,000 L scale; medium €0.20/L",
          "production cost; product basis not stated", "not stated", "model",
          "a consultancy, commissioned by whom not stated", "May 2025",
          "https://parima.bio/blog/gourmey-sets-new-cost-benchmark-in-cultivated-meat-production-with-3-4-lb-model-independently-validated"),
    Claim("Arthur D. Little (consultancy)", "low €40s/kg in 2026; about €10/kg by 2030",
          "finished product", "not stated", "model", "nobody named", "2025",
          "https://www.adlittle.com/en/insights/viewpoints/cultivated-meat-one-year"),
    Claim("SuperMeat (company white paper)", "$29.5/kg with depreciation ($26.0 without)",
          "100% chicken cells, wet; 10 L runs scaled on paper to 25,000 L", "depreciation only", "model from runs",
          "nobody; not peer reviewed", "November 2024",
          "https://supermeat.com/wp-content/uploads/2024/11/A-Deep-Dive-Into-Cost-Effective-Cultivated-Meat-Production-V.pdf"),
    Claim("Vow (company)", "a 20,000 L bioreactor built for “well under $1 million”",
          "one vessel; whether piping and installation are in it not stated", "a capital cost", "company statement",
          "nobody", "April 2025",
          "https://agfundernews.com/humbird-was-spectacularly-wrong-on-cultivated-meat-economics-says-report-as-vow-predicts-it-will-soon-be-unit-margin-positive"),
)


def _split(r: dict) -> dict:
    """Total, the yearly charge on the plant, and the rest (operating cost), with the parts worth naming."""
    return {"total": r["total"], "capital": r["capital"], "operating": r["total"] - r["capital"],
            "membranes": r["membranes"], "protectant": r["protectant"],
            "medium_gf": r["feedstock"] + r["growth_factors"], "density": r["density"], "medium_l": r["medium_l"],
            "capex_k_m3": r["capex"]}


def scenario_split() -> dict:
    """{key: split} for the reference case and each scenario, as the model runs them (each in its own mode since 2026-11-19)."""
    out = {"reference": _split(fp.explore())}
    for k in S.PAGE_ORDER:
        out[k] = _split(S.run(S.SCENARIOS[k].choice))
    return out


# the plants a cheaper route could be built as: the scenario's own, and two built item by item (plant_items.py)
PLANTS = (("the scenario's food-grade plant", {}),
          ("a food-grade plant with shared medium", {"items": PI.PLANTS["lean"]}),
          ("a yeast plant with what animal cells need", {"items": PI.PLANTS["yeastplus"]}))


def central_as_vow(cap: float | None = None) -> list:
    """the Selected cells case's cells and settings in a 20 m3 stirred tank drained and refilled (no cell retention), in each plant of
    PLANTS. `cap` caps the density (g/L), for the 27 g/L reported for meat cells at 20 m3. Returns [(plant, split)]."""
    kw = S.explore_kwargs(S.SCENARIOS["central"].choice)
    rows = []
    for name, extra in PLANTS:
        base = {k: v for k, v in kw.items() if not (extra and k in ("plant", "items"))}
        k2 = V.explore_kwargs("stirred", "filldraw", {**base, **extra})
        if cap is not None:
            k2["vm"] = {**k2["vm"], "caps": {"shown for meat cells": cap}}
        rows.append((name, _split(fp.explore(**k2))))
    return rows


def summary() -> dict:
    """The figures RESULTS.md and the page quote."""
    sp = scenario_split()
    vow = central_as_vow()
    vow27 = central_as_vow(value("vm_x_meat_shown"))
    eng = _split(S.run({**S.SCENARIOS["central"].choice, "cells": "engineered"}))
    return {"split": sp, "vow": vow, "vow27": vow27, "central_engineered": eng}


# ----------------------------------------------------------------------------
NAMES = {"reference": "Humbird's optimistic design", "today": "1. Published cells, fed-batch", "process": "2. Plus process changes",
         "selected": "3. Plus selected cells, fed-batch", "central": "4. Selected cells (perfusion)", "central_lean": "5. Plus a plant with shared medium",
         "engineered": "6. Plus engineered cells", "best": "7. Engineered cells, all favourable", "forecast": "Forecast for 2035, switches at their medians"}


def markdown() -> str:
    s = summary()
    out = ["| case | cells, $/kg | of which: charge on the plant | operating cost | of which: filter membranes | medium and growth factors |",
           "|---|---|---|---|---|---|"]
    for k in S.PAGE_ORDER + ("reference",):
        d = s["split"][k]
        out.append(f"| {NAMES[k]} | ${d['total']:.1f} | ${d['capital']:.1f} | **${d['operating']:.1f}** | ${d['membranes']:.1f} | "
                   f"${d['medium_gf']:.1f} |")
    out += ["", "| the Selected cells case's cells, 20 m³ tank drained and refilled (as Vow runs), in | cells, $/kg | charge on the plant | operating cost | "
            "at the 27 g/L reported for meat cells |", "|---|---|---|---|---|"]
    for (name, d), (_n, d27) in zip(s["vow"], s["vow27"]):
        out.append(f"| {name} (${d['capex_k_m3']:.0f}k per m³) | ${d['total']:.1f} ({d['density']:.0f} g/L) | ${d['capital']:.1f} | "
                   f"**${d['operating']:.1f}** | ${d27['total']:.1f} (operating ${d27['operating']:.1f}) |")
    out += ["", "| who | figure | a cost of | capital in it? | kind | checked by | date |", "|---|---|---|---|---|---|---|"]
    for c in CLAIMS:
        out.append(f"| [{c.who}]({c.source}) | {c.figure} | {c.of_what} | {c.capital} | {c.kind} | {c.checked} | {c.date} |")
    return "\n".join(out)


def main() -> None:
    if "--markdown" in sys.argv:
        print(markdown())
        return
    s = summary()
    for k in S.PAGE_ORDER + ("reference",):
        d = s["split"][k]
        print(f"  {k:<13} total ${d['total']:6.2f}  plant charge ${d['capital']:5.2f}  operating ${d['operating']:5.2f}"
              f"  (membranes ${d['membranes']:.2f}, medium+GF ${d['medium_gf']:.2f})")
    print("  the Selected cells case's cells, drained and refilled:")
    for (name, d), (_n, d27) in zip(s["vow"], s["vow27"]):
        print(f"    {name:<44} ${d['total']:6.2f} (plant ${d['capital']:.2f}, operating ${d['operating']:.2f}, {d['density']:.0f} g/L); "
              f"at 27 g/L ${d27['total']:.2f}")
    e = s["central_engineered"]
    print(f"  Selected cells with engineered cells: ${e['total']:.2f}, operating ${e['operating']:.2f}")


if __name__ == "__main__":
    main()
