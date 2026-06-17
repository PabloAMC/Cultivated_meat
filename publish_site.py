#!/usr/bin/env python3
"""publish_site.py — publish the interactive explorer to pabloamc.github.io.

Regenerates the standalone /cultivated-meat/ page on the personal site from the
current model artifacts and (optionally) commits + pushes it:

  index.html   = interactive.html, with the METHODS.md/RESULTS.md links repointed
                 to the rendered methods.html/results.html siblings.
  methods.html = METHODS.md rendered to standalone HTML (tables, no MathJax — the
                 "$" in these docs are dollar amounts, not LaTeX).
  results.html = RESULTS.md, likewise.

Run `python build_interactive.py` first so interactive.html is current.

Usage:
    python publish_site.py                 # render into the site's static/ dir
    python publish_site.py --push          # also git add/commit/push the site
    python publish_site.py --site PATH     # point at an existing site checkout

Locating the site repo (first hit wins):
    1. --site PATH
    2. $PABLOAMC_SITE
    3. ../pabloamc.github.io  (sibling of this project)
    4. a fresh `gh repo clone` into a temp dir (requires the gh CLI)
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
SITE_SUBDIR = os.path.join("static", "cultivated-meat")
REPO = "PabloAMC/pabloamc.github.io"

CSS = """
:root { --ink:#1a1a1a; --muted:#666; --rule:#e3e3e3; --accent:#0072B2; --bg:#fff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:Georgia,'Times New Roman',serif; line-height:1.62; }
.wrap { max-width:820px; margin:0 auto; padding:48px 24px 96px; }
.backlink { font-family:-apple-system,Helvetica,Arial,sans-serif; font-size:.9rem;
  display:inline-block; margin-bottom:1.4em; }
h1 { font-size:2.0rem; line-height:1.2; margin:0 0 .4em; letter-spacing:-.01em; }
h2 { font-size:1.4rem; margin:2.2em 0 .5em; padding-top:.6em; border-top:1px solid var(--rule); }
h3 { font-size:1.12rem; margin:1.6em 0 .4em; color:#222; }
h4 { font-size:1.0rem; margin:1.3em 0 .3em; color:#333; }
p, li { font-size:1.02rem; }
em { color:var(--muted); }
a { color:var(--accent); text-decoration:none; border-bottom:1px solid #bcdcef; }
a:hover { border-bottom-color:var(--accent); }
img { display:block; max-width:100%; height:auto; margin:1.4em auto; }
hr { border:0; border-top:1px solid var(--rule); margin:2.4em 0; }
code, pre { font-family:'SF Mono',Menlo,Consolas,monospace; font-size:.86rem; }
pre { background:#f7f7f5; border:1px solid var(--rule); border-radius:6px;
  padding:14px 16px; overflow-x:auto; line-height:1.45; }
code { background:#f1f1ef; padding:1px 5px; border-radius:4px; }
pre code { background:none; padding:0; }
table { border-collapse:collapse; width:100%; margin:1.3em 0; font-size:.92rem;
  font-family:-apple-system,Helvetica,Arial,sans-serif; }
th, td { text-align:left; padding:7px 10px; border-bottom:1px solid var(--rule); vertical-align:top; }
th { border-bottom:2px solid #ccc; font-weight:600; }
tr:hover td { background:#fafafa; }
blockquote { margin:1.2em 0; padding:.4em 1.1em; border-left:3px solid var(--accent);
  background:#f6fafd; color:#234; font-style:italic; }
strong { color:#111; }
"""


def render_md(src_name: str, title: str) -> str:
    with open(os.path.join(HERE, src_name), encoding="utf-8") as fh:
        text = fh.read()
    body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "attr_list", "sane_lists", "toc"]
    )
    back = '<a class="backlink" href="./">&larr; Back to the interactive explorer</a>'
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{title}</title><style>{CSS}</style></head>"
        f'<body><div class="wrap">{back}{body}</div></body></html>'
    )


def build(dest: str) -> None:
    os.makedirs(dest, exist_ok=True)

    for src_name, out_name, title in [
        ("METHODS.md", "methods.html", "Cultivated meat — methods"),
        ("RESULTS.md", "results.html", "Cultivated meat — results"),
    ]:
        html = render_md(src_name, title)
        with open(os.path.join(dest, out_name), "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"  wrote {out_name}  ({len(html)/1024:.0f} KB)")

    with open(os.path.join(HERE, "interactive.html"), encoding="utf-8") as fh:
        page = fh.read()
    page = page.replace('href="METHODS.md"', 'href="methods.html"')
    page = page.replace('href="RESULTS.md"', 'href="results.html"')
    assert 'href="METHODS.md"' not in page and 'href="RESULTS.md"' not in page, (
        "interactive.html link rewrite failed — its METHODS.md/RESULTS.md links "
        "may have changed; update publish_site.py to match."
    )
    with open(os.path.join(dest, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"  wrote index.html  ({len(page)/1024:.0f} KB)")


def locate_site(arg_site: str | None) -> str:
    for cand in (arg_site, os.environ.get("PABLOAMC_SITE"),
                 os.path.normpath(os.path.join(HERE, "..", "..", "pabloamc.github.io"))):
        if cand and os.path.isdir(os.path.join(cand, ".git")):
            return cand
    # Fall back to a clone in a stable cache dir (not the system temp dir, which
    # macOS periodically reaps — that corrupts the .git and breaks `git pull`).
    cache = os.environ.get("XDG_CACHE_HOME") or os.path.join(
        os.path.expanduser("~"), ".cache")
    dest = os.path.join(cache, "pabloamc.github.io")
    is_repo = subprocess.run(
        ["git", "-C", dest, "rev-parse", "--is-inside-work-tree"],
        capture_output=True).returncode == 0
    if not is_repo:
        # No checkout, or a partially-reaped one — start clean.
        if os.path.isdir(dest):
            print(f"Removing stale/broken checkout at {dest}")
            shutil.rmtree(dest)
        print(f"Cloning {REPO} -> {dest}")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        subprocess.run(["gh", "repo", "clone", REPO, dest], check=True)
    else:
        subprocess.run(["git", "-C", dest, "pull", "--ff-only"], check=True)
    return dest


def git_push(site: str) -> None:
    rel = SITE_SUBDIR
    subprocess.run(["git", "-C", site, "add", rel], check=True)
    diff = subprocess.run(["git", "-C", site, "diff", "--cached", "--quiet"]).returncode
    if diff == 0:
        print("No changes to publish — site already up to date.")
        return
    subprocess.run(
        ["git", "-C", site, "commit", "-m",
         "Update cultivated-meat interactive explorer"], check=True)
    subprocess.run(["git", "-C", site, "push"], check=True)
    print("Pushed — GitHub Pages will redeploy in ~1-2 min.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", help="path to a pabloamc.github.io checkout")
    ap.add_argument("--push", action="store_true",
                    help="git add/commit/push the site after building")
    args = ap.parse_args()

    if not os.path.exists(os.path.join(HERE, "interactive.html")):
        sys.exit("interactive.html not found — run `python build_interactive.py` first.")

    site = locate_site(args.site)
    dest = os.path.join(site, SITE_SUBDIR)
    print(f"Site: {site}")
    build(dest)

    if args.push:
        git_push(site)
    else:
        print("\nBuilt. Review, then publish with:  python publish_site.py --push")


if __name__ == "__main__":
    main()
