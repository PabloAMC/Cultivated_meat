#!/usr/bin/env python3
"""
common.py — shared plotting style and figure-saving, used by every rung.

These are pure plumbing (no model logic). They previously lived in the price-ratio module, which
meant every rung had to import the *placeholder* rung just to save a figure;
they belong in a neutral module instead.
"""

from __future__ import annotations

import os
import shutil

import matplotlib


def _have_real_latex() -> bool:
    """True LaTeX needs a TeX engine AND a PDF->raster tool. We avoid dvipng
    (not installable without admin here) by using the PGF backend with pdflatex
    and rasterising PNGs through pdftocairo/pdftoppm — both already present."""
    return bool(shutil.which("pdflatex")
                and (shutil.which("pdftocairo") or shutil.which("pdftoppm")))


def setup_style(use_latex: bool = True) -> None:
    """Apply a LaTeX-quality style.

    When a TeX engine + pdftocairo are available (they are here), figures are
    rendered with REAL LaTeX via the PGF backend (pdflatex) — no dvipng needed.
    Otherwise we fall back to matplotlib's Computer-Modern mathtext (the LaTeX
    look, no external dependency). `use_latex=False` forces the mathtext fallback.
    """
    real_tex = use_latex and _have_real_latex()
    if real_tex:
        matplotlib.use("pgf", force=True)
    import matplotlib.pyplot as plt  # after the backend is chosen

    # base look (grid, serif, sober spines) — set manually so it composes with
    # either the PGF or the mathtext path without a style-sheet preamble clash.
    plt.rcParams.update({
        "figure.dpi": 130, "font.size": 10, "axes.grid": True, "grid.alpha": 0.28,
        "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.8, "font.family": "serif", "axes.unicode_minus": False,
    })
    if real_tex:
        plt.rcParams.update({
            "text.usetex": True,
            "pgf.texsystem": "pdflatex",
            "pgf.rcfonts": False,
            # lmodern = Computer Modern; T1 fontenc makes <, >, | render literally
            "pgf.preamble": r"\usepackage[T1]{fontenc}\usepackage{lmodern}"
                            r"\usepackage{underscore}",
        })
    else:
        plt.rcParams.update({"text.usetex": False, "mathtext.fontset": "cm"})


def _save(fig, outdir: str, name: str, fmts) -> None:
    """Write `fig` to outdir/name.<ext> for each requested format."""
    os.makedirs(outdir, exist_ok=True)
    for ext in fmts:
        fig.savefig(os.path.join(outdir, f"{name}.{ext}"), bbox_inches="tight")
    print(f"  wrote {name}.{{{','.join(fmts)}}}")
