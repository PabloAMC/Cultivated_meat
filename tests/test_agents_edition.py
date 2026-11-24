"""test_agents_edition.py — the edition for AI agents (agents_edition.py) matches the model.

Checks
  * agents_edition_scan.json (answer_rests_on's 28-minute scan, stored) still belongs to the model: the inputs' fingerprint and the
    low-lactate and all-favourable examples' costs match;
  * AGENTS.md, llms.txt and inputs.json are exactly what a fresh run of agents_edition.py writes (so no number in them can drift
    from the code; after a change, run `python agents_edition.py` and commit the three files);
  * inputs.json lists every input of inputs.py's REGISTRY with its value;
  * every file a dead end names exists;
  * the words follow the page's rules (tests/test_easy_view.py): no retired name, no judgement attributed to the owner, no cost
    in "today's dollars", no em dash, and no word naming a way to obtain a trait in the prose (code names in backticks excepted).

Runs as a script or under pytest. It reads answer_rests_on.py's scan from agents_edition_scan.json and does not run it.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import agents_edition as AE  # noqa: E402
import inputs as I  # noqa: E402
import test_easy_view as EV  # noqa: E402


def check() -> list:
    fails = []
    # the stored scan still belongs to this model: the same inputs, and the two examples cost the same
    sc = AE.load_scan()
    if sc["fingerprint"] != AE.fingerprint():
        fails.append("an input's value or range changed since agents_edition_scan.json was written: run "
                     "`python agents_edition.py --scan` and commit the four files")
    import answer_rests_on as AR
    for key in ("central", "best"):
        now, then = AR._cost(key), sc[f"{key}_cost"]
        if abs(now / then - 1.0) > 1e-9:
            fails.append(f"the {key} scenario costs ${now:.4f} now and ${then:.4f} in agents_edition_scan.json: the engine changed; "
                         "run `python agents_edition.py --scan` and commit the four files")
        share = AR.S.shares(now)["global"]
        if abs(share - sc[f"{key}_share"]) > 1e-9 * max(1.0, share):
            fails.append(f"the {key} scenario's world share is {share:.6f}% now and {sc[f'{key}_share']:.6f}% in "
                         "agents_edition_scan.json: the demand model changed; run `python agents_edition.py --scan`")
    fresh = AE.outputs()
    for path, text in fresh.items():
        name = os.path.basename(path)
        if not os.path.exists(path):
            fails.append(f"{name} is missing: run `python agents_edition.py`")
            continue
        old = open(path, encoding="utf-8").read()
        if old != text:
            a, b = old.splitlines(), text.splitlines()
            i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
            fails.append(f"{name} differs from a fresh run (first at line {i + 1}): run `python agents_edition.py` and commit it\n"
                         f"    committed: {a[i][:160] if i < len(a) else '(end)'}\n    fresh:     {b[i][:160] if i < len(b) else '(end)'}")

    doc = json.loads(fresh[AE.INPUTS_JSON])
    names = [r["name"] for r in doc["inputs"]]
    if names != list(I.REGISTRY):
        fails.append("inputs.json does not list the REGISTRY's inputs in order")
    for r in doc["inputs"]:
        if r["value"] != I.REGISTRY[r["name"]].value:
            fails.append(f"inputs.json: {r['name']} has the wrong value")

    for date, _what, _why, where in AE.DEAD_ENDS_DATA:
        if not re.fullmatch(r"\d{4}-\d\d-\d\d", date):
            fails.append(f"a dead end has no date: {date}")
        for f in re.findall(r"[\w/.-]+\.(?:md|py)", where):
            if not os.path.exists(os.path.join(ROOT, f)):
                fails.append(f"a dead end names a file that does not exist: {f}")

    for path in (AE.AGENTS_MD, AE.LLMS_TXT):
        text = fresh[path]
        name = os.path.basename(path)
        prose = re.sub(r"```.*?```", " ", text, flags=re.S)
        prose = re.sub(r"`[^`]*`", " ", prose)
        prose_no_quotes = prose.replace(", ".join(repr(x) for x in EV.RETIRED), "")
        for bad in EV.RETIRED:
            if bad in prose_no_quotes:
                fails.append(f"{name}: a retired name: {bad}")
        for rx, what in ((EV.OWNER_JUDGED, "a judgement attributed to the owner"), (EV.TODAY_COST, "a cost in today's dollars")):
            for m in rx.finditer(prose):
                fails.append(f"{name}: {what}: ...{prose[max(0, m.start() - 60):m.end() + 40]}...")
        if "—" in text:
            fails.append(f"{name}: an em dash")
        for m in EV.ROUTE_WORDS.finditer(prose_no_quotes):
            fails.append(f"{name}: a word naming a way to obtain a trait: ...{prose_no_quotes[max(0, m.start() - 60):m.end() + 40]}...")
    return fails


def test_agents_edition():
    fails = check()
    assert not fails, "\n".join(fails)


if __name__ == "__main__":
    fails = check()
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print("PASS: AGENTS.md, llms.txt and inputs.json match the model")
