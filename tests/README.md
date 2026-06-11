# Tests

Run everything with `./run_tests.sh` (from `model/`): it rebuilds `interactive.html`
from the Python model, then runs the golden-value and parity checks.

## Golden-value regression (`test_golden.py`)

Pins the model's headline outputs — the price ratio R, plant-based share, at-parity
cultivated share, the plant-based-milk cross-check, the derived β / calibration values,
the regional income gradient, a health-dial point, and the US penetration roll-ups — so any
accidental change to a formula, default, or the calibration solve is caught with the old vs
new value shown. If a change is intentional, update `GOLDEN` in `test_golden.py` in the same
commit so the output move is explicit in the diff.

```bash
python tests/test_golden.py     # -> "PASS — all headline model outputs match their golden values."
```

Runs as a plain script (exit 0/1) or under pytest.

## Python ↔ JS parity (`run_parity.py`)

`build_interactive.py` hand-ports the model (utilities / shareCalc / solveCalibration /
deriveBeta / penetration / bassTrajectory …) from the Python modules into JavaScript so the
interactive explorer runs offline. That means the model logic exists **twice**, and the two
can silently drift — which has happened (a regional income-term mismatch worth 5–8 percentage
points). This test is the guard against it.

It extracts the embedded JS from `interactive.html`, runs it headless under Node, recomputes the
same quantities with the Python source-of-truth modules, and asserts they agree to `1e-4` over a
grid that spans price, both acceptance dials, elasticity, income, the calibration solve, the
plant-based-milk cross-check, and the timing rung (~2,000 grid points + headline values + the
full trajectory).

### Run it

```bash
# from the model/ directory, with the venv active
python build_interactive.py      # regenerate interactive.html if you changed Python model code
python tests/run_parity.py        # -> "PASS — the JS model mirrors the Python source of truth."
```

Exit code is `0` on parity, `1` on mismatch. If [Node.js](https://nodejs.org) isn't on `PATH`
the test **skips** (exit 0 with a notice) rather than failing.

Under pytest (optional): `pytest tests/run_parity.py`.

### When it fails

A failure means the JS mirror and the Python model disagree. Either:

- you changed a **Python** model formula but didn't rebuild — run `python build_interactive.py`; or
- you changed one side's formula and not the other — reconcile them (Python is the source of
  truth; the JS in `build_interactive.py` must mirror it).

The failure output lists the worst grid points with both values and the diff, which usually
points straight at the diverging term (e.g. all-income-dependent rows ⇒ the BLP income term).

### Self-test

To confirm the test isn't vacuous: temporarily change the JS `alpha` in `build_interactive.py`
back to `-beta*(K.income_ref-K.anchor_price)`, rebuild, and run — it should report ~1,700
mismatches concentrated at non-US incomes. Revert and it returns to PASS.
