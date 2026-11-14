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

echo "==> gas-exchange side study"
python tests/test_gas_exchange.py

echo "==> Python <-> JS parity"
python tests/run_parity.py

echo "==> all tests passed"
