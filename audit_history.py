#!/usr/bin/env python3
"""
audit_history.py — the headline costs at every commit that touched the cost code.

Checks out each commit in a temporary git worktree and runs the model there, so the history of the headline numbers is measured, not
remembered. Needs the full git history. It takes about ten minutes.

    python audit_history.py            # prints one line each time a headline number changed
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

PROBE = r'''
import json, warnings
warnings.filterwarnings("ignore")
out = {}
def tryit(name, fn):
    try: out[name] = round(float(fn()), 2)
    except Exception: out[name] = None
def default():
    from cost_model import CostParams, biomass_cost
    return biomass_cost(CostParams())
def floor():
    import floor_physics as fp
    return fp.explore()["total"]
def central():
    import scenarios as S
    return S.run(S.SCENARIOS["central"].choice)["total"]
def best():
    import scenarios as S
    return S.run(S.SCENARIOS["best"].choice)["total"]
tryit("default", default); tryit("floor", floor); tryit("central", central); tryit("best", best)
print(json.dumps(out))
'''
FILES = ("floor_physics.py", "inputs.py", "scenarios.py", "cost_model.py")


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    git = lambda *a, cwd=here: subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    commits = [ln.split("|", 2) for ln in git("log", "--reverse", "--format=%h|%ad|%s", "--date=format:%m-%d %H:%M",
                                              "origin/main", "--", *FILES).stdout.splitlines()]
    with tempfile.TemporaryDirectory() as tmp:
        wt = os.path.join(tmp, "wt")
        git("worktree", "add", "-q", "--detach", wt, "origin/main")
        prev = None
        for sha, when, msg in commits:
            if git("checkout", "-q", "--detach", sha, cwd=wt).returncode:
                continue
            r = subprocess.run([sys.executable, "-c", PROBE], cwd=wt, capture_output=True, text=True, timeout=120,
                               env={**os.environ, "PYTHONPATH": wt})
            try:
                d = json.loads(r.stdout.strip().splitlines()[-1])
            except Exception:
                continue
            key = tuple(d.values())
            if key != prev:
                print(f"{sha} {when}  default {d['default']}  floor {d['floor']}  central {d['central']}  best {d['best']}  | {msg[:80]}")
                prev = key
        git("worktree", "remove", "--force", wt)


if __name__ == "__main__":
    main()
