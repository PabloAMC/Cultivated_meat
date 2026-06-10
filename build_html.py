#!/usr/bin/env python3
"""
build_html.py — render POST.md to a single self-contained POST.html.

Figures referenced as `figures/<name>.png` are embedded as base64 data URIs, so
the HTML is fully portable (one file, no external assets). Run after the figures
are built (`python report_figures.py`):

    python build_html.py
"""
from __future__ import annotations

import base64
import os
import re

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "POST.md")
OUT = os.path.join(HERE, "POST.html")

CSS = """
:root { --ink:#1a1a1a; --muted:#666; --rule:#e3e3e3; --accent:#0072B2; --bg:#fff; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:Georgia,'Times New Roman',serif; line-height:1.62; }
.wrap { max-width:820px; margin:0 auto; padding:48px 24px 96px; }
h1 { font-size:2.0rem; line-height:1.2; margin:0 0 .4em; letter-spacing:-.01em; }
h2 { font-size:1.4rem; margin:2.2em 0 .5em; padding-top:.6em; border-top:1px solid var(--rule); }
h3 { font-size:1.12rem; margin:1.6em 0 .4em; color:#222; }
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
.wrap > p:first-of-type em { display:block; font-size:.95rem; }
"""


def embed_images(html: str) -> str:
    """Replace src="figures/x.png" with a base64 data URI."""
    def repl(m):
        path = os.path.join(HERE, m.group(1))
        if not os.path.exists(path):
            return m.group(0)
        with open(path, "rb") as fh:
            data = base64.b64encode(fh.read()).decode("ascii")
        return f'src="data:image/png;base64,{data}"'
    return re.sub(r'src="(figures/[^"]+\.png)"', repl, html)


def main() -> None:
    with open(SRC, encoding="utf-8") as fh:
        text = fh.read()
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list", "sane_lists"])
    body = embed_images(body)
    html = (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>How far does cultivated meat actually get?</title>"
        f"<style>{CSS}</style></head><body><div class=\"wrap\">{body}</div></body></html>"
    )
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    kb = os.path.getsize(OUT) / 1024
    print(f"wrote {os.path.relpath(OUT)}  ({kb:.0f} KB, figures embedded)")


if __name__ == "__main__":
    main()
