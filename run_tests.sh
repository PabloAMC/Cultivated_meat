#!/usr/bin/env bash
# Rebuild the interactive page from the current Python model, then run the test suite.
# Usage:  ./run_tests.sh            (all tests, in parallel, one per CPU core)
#         JOBS=1 ./run_tests.sh     (one at a time, as before 2026-11-21)
#
# The page is built first, because several tests read interactive.html. The tests then run in
# parallel: each writes only to its own temporary directory, so they do not touch each other.
# Each test's output goes to a log; a failing test's log is printed in full. The slowest tests
# are listed at the end, with their times.
set -euo pipefail
cd "$(dirname "$0")"

TESTS=(
  "the Monte Carlo's vectorised share against share(), and the plant-item cache|tests/test_share_many.py"
  "golden-value regression|tests/test_golden.py"
  "doubling-time envelope|tests/test_growth_rate.py"
  "physics-based floor|tests/test_floor_physics.py"
  "plant by items, contamination|tests/test_plant_items.py"
  "cost scenarios|tests/test_scenarios.py"
  "vessel types against operating modes|tests/test_vessels.py"
  "cell retention for a 20 m3 perfusion tank|tests/test_retention.py"
  "downside: no perfusion at 20 m3|tests/test_downside.py"
  "cost against tank size|tests/test_tank_size.py"
  "how thick a culture can be|tests/test_thick_culture.py"
  "least medium per kg of cells that physics allows|tests/test_min_litres.py"
  "nutrient floor|tests/test_nutrient_floor.py"
  "gas-exchange side study|tests/test_gas_exchange.py"
  "growth-factor prices and the fastest doubling time|tests/test_gf_doubling_bounds.py"
  "model audit: global uncertainty and the retail translation|tests/test_audit.py"
  "the path from Humbird's design to the all-favourable case|tests/test_frontier.py"
  "one all-favourable case, and the order of the reference points|tests/test_ordering.py"
  "the filter flux limit|tests/test_filter_flux.py"
  "the model against company claims|tests/test_industry_claims.py"
  "the tank design search|tests/test_design_space.py"
  "cultivated meat anchored on premium real meats|tests/test_premium_curve.py"
  "cultivated meat competing with welfare labels for premium buyers|tests/test_premium_buyers.py"
  "cost falling with market size, solved with the share|tests/test_market_size_loop.py"
  "the model's response to price against four measurements|tests/test_demand_checks.py"
  "a spread of liking for cultivated meat across shoppers|tests/test_liking_spread.py"
  "what the answer rests on|tests/test_answer_rests_on.py"
  "cleaning and reusing the medium|tests/test_medium_reuse.py"
  "the retail markup rule against USDA's meat spreads|tests/test_retail_spreads.py"
  "the engine against Humbird's own tables|tests/test_humbird_check.py"
  "the page's short version|tests/test_easy_view.py"
  "published cost studies: Humbird's design with one study's assumptions at a time|tests/test_study_assumptions.py"
  "Python <-> JS parity|tests/run_parity.py"
)

JOBS="${JOBS:-$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)}"
LOGS="$(mktemp -d "${TMPDIR:-/tmp}/cm_tests.XXXXXX")"
trap 'rm -rf "$LOGS"' EXIT

start=$(date +%s)
echo "==> regenerating interactive.html from the Python model"
python build_interactive.py >/dev/null
echo "    built in $(( $(date +%s) - start )) s"

run_one() {  # $1 = index, $2 = "label|path"; writes <index>.log, <index>.rc, <index>.time
  local i="$1" label="${2%%|*}" path="${2#*|}" t0 rc
  t0=$(date +%s)
  set +e; python "$path" >"$LOGS/$i.log" 2>&1; rc=$?; set -e
  echo "$rc" >"$LOGS/$i.rc"; echo "$(( $(date +%s) - t0 ))" >"$LOGS/$i.time"
  if [ "$rc" -eq 0 ]; then echo "    pass  $label"; else echo "    FAIL  $label"; fi
}
export -f run_one; export LOGS

echo "==> ${#TESTS[@]} tests, $JOBS at a time"
for i in "${!TESTS[@]}"; do printf '%s\0%s\0' "$i" "${TESTS[$i]}"; done |
  xargs -0 -n 2 -P "$JOBS" bash -c 'run_one "$0" "$1"'

failed=0
for i in "${!TESTS[@]}"; do
  if [ "$(cat "$LOGS/$i.rc" 2>/dev/null || echo 1)" -ne 0 ]; then
    failed=$((failed + 1))
    echo; echo "==> FAILED: ${TESTS[$i]%%|*} (${TESTS[$i]#*|})"; cat "$LOGS/$i.log" 2>/dev/null || true
  fi
done

echo; echo "==> slowest tests (seconds)"
for i in "${!TESTS[@]}"; do echo "$(cat "$LOGS/$i.time" 2>/dev/null || echo 0) ${TESTS[$i]#*|}"; done | sort -rn | head -6 | sed 's/^/    /'
echo "    whole run: $(( $(date +%s) - start )) s"

if [ "$failed" -ne 0 ]; then echo "==> $failed test(s) failed"; exit 1; fi
echo "==> all tests passed"
