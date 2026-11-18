#!/usr/bin/env python3
"""test_easy_view.py — the page's short version (build_interactive.py, page_scenarios.js).

The short version shows three numbers for a chosen case and folds every long section under its heading. It must not carry numbers of
its own: every figure comes from the same functions as the full page. Checks that its cases are real scenarios, that its words hold no
typed-in numbers, that each folded section has a one-line summary, and that the built page carries the pieces. Runs as a script or
under pytest.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import build_interactive as B  # noqa: E402
import scenarios as S  # noqa: E402


def check() -> list:
    fails = []
    easy = B.build_model()["const"]["easy"]
    for c in easy["cases"]:
        if c["key"] not in S.SCENARIOS:
            fails.append(f"the short version's case '{c['key']}' is not a scenario")
        if re.search(r"\d", c["say"] + c["label"]):
            fails.append(f"the short version's words for '{c['key']}' carry a typed-in number")
    page = B.PAGE_HTML
    folded = re.findall(r'<section id="(\w+)" data-easy>\s*<h2 class="sech">[^<]*</h2>\s*(<p class="easysum">[^<]+</p>)?', page)
    if len(folded) < 5:
        fails.append("fewer than five sections fold in the short version")
    for sid, summary in folded:
        if not summary:
            fails.append(f"section #{sid} folds but has no one-line summary")
    js = open(os.path.join(ROOT, "page_scenarios.js"), encoding="utf-8").read()
    for piece in ("function setView(", "function easyInit(", "function easyRender(", "shelfPrice(cost,state)", "SC.bands[named]"):
        if piece not in js:
            fails.append(f"page_scenarios.js no longer has: {piece}")
    for piece in ('id="easy_nums"', 'id="view_easy"', 'id="view_full"', "easyInit();"):
        if piece not in page and piece not in B.JS_ENGINE:
            fails.append(f"the page no longer has: {piece}")
    return fails


def test_easy_view():
    assert not check()


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("easy view: all checks passed")
