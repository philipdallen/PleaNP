#!/usr/bin/env bash
# Re-runnable front-page gate evidence (README "Latest gate evidence" block).
# Runs the five integrity gates over the CI clean-module list and prints their
# verdicts with a timestamp and the HEAD SHA, so a reader can reproduce the
# block. Requires: elan/Lean toolchain on PATH, `lake exe cache get` already run,
# and the clean modules built with the CI command (see .github/workflows/ci.yml);
# that build log is read back by the #barrier_check harness.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

MODULES="lean/PleaNP/Calculus lean/PleaNP/Basic.lean lean/PleaNP/Barriers/RelativizationProof.lean lean/PleaNP/Barriers/Algebrization.lean lean/PleaNP/Barriers/Williams.lean lean/PleaNP/Barriers/WilliamsTransfer.lean lean/PleaNP/Barriers/WilliamsAssembly.lean lean/PleaNP/Barriers/WilliamsSat.lean lean/PleaNP/Benchmark/Closure.lean lean/PleaNP/ProofComplexity/Resolution.lean lean/PleaNP/Challenges/Relativization.lean lean/PleaNP/Circuits/Basic.lean lean/PleaNP/Circuits/AC0.lean lean/PleaNP/Circuits/MustRefute.lean lean/PleaNP/Computability/Oracle.lean lean/PleaNP/Computability/OracleComplexity.lean lean/PleaNP/Computability/OracleSmoke.lean lean/PleaNP/Computability/OracleV5Tests.lean lean/PleaNP/Barriers/LowerBoundCompiler.lean lean/PleaNP/Barriers/DiagonalSyntax.lean lean/PleaNP/Barriers/DiagonalBits.lean lean/PleaNP/Barriers/DiagonalBridge.lean lean/PleaNP/Barriers/DiagonalChain.lean lean/PleaNP/Barriers/DiagonalChainAccept.lean lean/PleaNP/Barriers/DiagonalChainFlip.lean lean/PleaNP/Barriers/DiagonalCounting.lean lean/PleaNP/Barriers/DiagonalDecision.lean lean/PleaNP/Barriers/DiagonalEnum.lean lean/PleaNP/Barriers/DiagonalEnumOracle.lean lean/PleaNP/Barriers/DiagonalStages.lean lean/PleaNP/Barriers/DiagonalTournament.lean lean/PleaNP/Barriers/DiagonalUB.lean lean/PleaNP/Circuits/Monotone.lean lean/PleaNP/Circuits/MonotoneApprox.lean lean/PleaNP/Circuits/Restriction.lean lean/PleaNP/Circuits/Switching.lean"

echo "captured_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "head=$(git rev-parse HEAD)"
echo "modules=36 (CI clean-module list)"

echo
echo "\$ python3 tooling/gates/hygiene_scan.py --prove-stage <36 modules>"
python3 tooling/gates/hygiene_scan.py --prove-stage $MODULES 2>&1 | tail -2

echo
echo "\$ python3 tooling/gates/vacuity_scan.py <36 modules>"
python3 tooling/gates/vacuity_scan.py $MODULES 2>&1 | tail -1

echo
echo "\$ python3 tooling/gates/model_consistency_scan.py <36 modules>"
python3 tooling/gates/model_consistency_scan.py $MODULES 2>&1 | tail -1

echo
echo "\$ python3 tooling/gates/binder_usage_scan.py --allow-unreferenced '^(exists_equalizing_oracle|exists_separating_oracle|smoke_accepts_true|smoke_rejects_false|v5_smoke_accepts_true|v5_smoke_rejects_false)\$' <36 modules>"
python3 tooling/gates/binder_usage_scan.py --allow-unreferenced '^(exists_equalizing_oracle|exists_separating_oracle|smoke_accepts_true|smoke_rejects_false|v5_smoke_accepts_true|v5_smoke_rejects_false)$' $MODULES 2>&1 | tail -2

echo
echo "\$ cd lean && lake build <36 modules> 2>&1 | tee /tmp/barcheck.log"
echo "\$ python3 ../tooling/gates/barrier_check_test.py /tmp/barcheck.log"
if [ -f /tmp/barcheck.log ]; then
  python3 tooling/gates/barrier_check_test.py /tmp/barcheck.log 2>&1
else
  echo "(no /tmp/barcheck.log: run the CI clean-module build first, see .github/workflows/ci.yml)"
fi
