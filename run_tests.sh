#!/usr/bin/env bash
# Rebuild the interactive page from the current Python model, then run the test suite.
# Usage:  ./run_tests.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "==> regenerating interactive.html from the Python model"
python build_interactive.py >/dev/null

echo "==> golden-value regression"
python tests/test_golden.py

echo "==> doubling-time envelope"
python tests/test_growth_rate.py

echo "==> physics-based floor"
python tests/test_floor_physics.py

echo "==> plant by items, contamination"
python tests/test_plant_items.py

echo "==> cost scenarios"
python tests/test_scenarios.py

echo "==> vessel types against operating modes"
python tests/test_vessels.py

echo "==> cell retention for a 20 m3 perfusion tank"
python tests/test_retention.py

echo "==> downside: no perfusion at 20 m3"
python tests/test_downside.py

echo "==> cost against tank size"
python tests/test_tank_size.py

echo "==> how thick a culture can be: viscosity, stirrer, oxygen, cost at other density limits"
python tests/test_thick_culture.py

echo "==> least medium per kg of cells that physics allows"
python tests/test_min_litres.py

echo "==> nutrient floor"
python tests/test_nutrient_floor.py

echo "==> gas-exchange side study"
python tests/test_gas_exchange.py

echo "==> growth-factor prices and the fastest doubling time"
python tests/test_gf_doubling_bounds.py

echo "==> Python <-> JS parity"
python tests/run_parity.py

echo "==> all tests passed"
